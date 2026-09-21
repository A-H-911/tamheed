"""Tamheed v4 package store — JSONL <-> SQLite, honoring CANONICAL.md (plan 007/B2; re-baselined plan 031/B27).

Stdlib only. This module is the single loader/writer for a package's ``data/`` directory
and is reused by the plan-008 MCP server. See ADR-0001 for the doctrine.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
MIGRATIONS_DIR = Path(__file__).with_name("migrations")
LOCK_NAME = ".lock"
DERIVED_TABLES = frozenset({"entity_index"})  # trigger-maintained; never serialized


class StoreLockedError(RuntimeError):
    """Another writer holds this package's data/.lock — fail loud, never wait."""


class StoreStaleError(RuntimeError):
    """data/ changed on disk since this session loaded it — refuse to clobber (C31/C1).

    A package's data/ lives in a git working tree, so `git checkout`/`pull`/a second
    writer can move it underneath an open session; an unconditional dump would then
    silently overwrite every incoming change with the session's older in-memory copy."""


_START_TOLERANCE_S = 2.0  # clock granularity between two reads of one process's start


def process_start_time(pid: int) -> tuple[str, float | None]:
    """Plan 063: OBSERVE a pid without guessing - ("not-running" | "running" |
    "unobservable", start as epoch seconds or None). Stdlib only, spawns nothing,
    signals nothing. On Windows `os.kill(pid, 0)` would TERMINATE the process, so
    the probe is OpenProcess + GetExitCodeProcess + GetProcessTimes: a handle alone
    proves nothing (an exited process still opens while anyone holds a handle to it
    - measured), only exit code STILL_ACTIVE does; access denied means it EXISTS but
    cannot be inspected."""
    # A pid comes from a JSON file anyone with write access could garble: only a real,
    # bounded int is probed. bool is an int, Infinity overflows int(), and a huge value
    # truncates modulo 2**32 in a DWORD and would land on an UNRELATED live process.
    if (not isinstance(pid, int) or isinstance(pid, bool)
            or not 0 < pid <= (0xFFFFFFFF if sys.platform == "win32" else 4194304)):
        return ("unobservable", None)
    if sys.platform == "win32":
        return _windows_process_start(pid)
    if Path("/proc/self/stat").exists():                # Linux: start = boot time + ticks
        return _linux_process_start(pid)
    try:                                                # other POSIX: liveness only
        os.kill(pid, 0)
    except ProcessLookupError:
        return ("not-running", None)
    except OSError:                                     # PermissionError: it exists
        return ("unobservable", None)
    return ("running", None)


_K32 = None


def _kernel32():
    """kernel32 with its signatures declared ONCE (HANDLE is pointer-sized: an
    undeclared restype would truncate it to 32 bits)."""
    global _K32
    if _K32 is not None:
        return _K32
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetProcessTimes.argtypes = ([wintypes.HANDLE]
                                    + [ctypes.POINTER(wintypes.FILETIME)] * 4)
    _K32 = k32
    return k32


def _windows_process_start(pid: int) -> tuple[str, float | None]:
    import ctypes
    from ctypes import wintypes
    k32 = _kernel32()
    handle = k32.OpenProcess(0x1000, False, pid)        # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        # 87 = ERROR_INVALID_PARAMETER: no such pid. Anything else (5 = access denied):
        # it may well exist - say so rather than call it dead.
        return (("not-running", None) if ctypes.get_last_error() == 87
                else ("unobservable", None))
    try:
        code = wintypes.DWORD()
        if not k32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return ("unobservable", None)
        if code.value != 259:                           # STILL_ACTIVE
            return ("not-running", None)
        created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not k32.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                   ctypes.byref(kernel), ctypes.byref(user)):
            return ("running", None)
        ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
        return ("running", ticks / 1e7 - 11644473600)   # FILETIME epoch -> unix epoch
    finally:
        k32.CloseHandle(handle)


def _linux_process_start(pid: int) -> tuple[str, float | None]:
    proc = Path(f"/proc/{pid}")
    if not proc.exists():
        return ("not-running", None)
    try:
        fields = (proc / "stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
        btime = next(int(line.split()[1]) for line in
                     Path("/proc/stat").read_text(encoding="utf-8").splitlines()
                     if line.startswith("btime "))
        return ("running", btime + int(fields[19]) / os.sysconf("SC_CLK_TCK"))
    except (OSError, ValueError, IndexError, StopIteration):
        return ("running", None) if proc.exists() else ("not-running", None)


def process_identity(pid: int) -> str | None:
    """An EXACT token for "this very process", immune to wall-clock steps: the Windows
    creation FILETIME is fixed at creation; on Linux it is boot id + start ticks (the
    epoch form goes through `btime`, which moves when the clock is stepped). None
    where the platform offers no such token - identity then falls back to the epoch
    start with a tolerance."""
    state, started = process_start_time(pid)
    if state != "running" or started is None:
        return None
    if sys.platform == "win32":
        return f"win:{round(started * 1e7)}"
    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="utf-8").strip()
        ticks = (Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
                 .rsplit(")", 1)[1].split()[19])
        return f"linux:{boot}:{ticks}"
    except (OSError, IndexError):
        return None


def _pid_namespace() -> str | None:
    """Two containers can share a hostname and still not see each other's pids."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except (OSError, AttributeError, NotImplementedError):
        return None


def _read_lock(lock_path: Path) -> dict:
    try:
        parsed = json.loads(lock_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def observe_lock(lock_path: Path, probe=process_start_time,
                 identity=process_identity) -> dict:
    """Plan 063 (findings_25 s1): what can be OBSERVED about a lock's holder, with the
    evidence - the store declines to GUESS, and reporting an observation is not
    guessing. Outcomes: `not-running` (no such process), `reused` (the pid belongs
    to a different process - its start differs from the one the lock recorded, or,
    for a lock that recorded none, it started after the lock was taken), `alive`
    (the recorded process is running), `unobservable` (another host, an unreadable
    or legacy lock, access denied, or a platform that cannot report a start time)."""
    holder = _read_lock(lock_path)
    out = {"outcome": "unobservable", "pid": holder.get("pid"), "host": holder.get("host"),
           "taken_at": holder.get("taken_at")}
    if not holder.get("pid") or not holder.get("host"):
        return {**out, "evidence": "the lock does not name a pid and a host (legacy or"
                                   " unreadable) - nothing to observe"}
    if holder["host"] != socket.gethostname():
        return {**out, "evidence": f"held on another host ({holder['host']}) - this host"
                                   " cannot observe that process"}
    if holder.get("pidns") and holder["pidns"] != _pid_namespace():
        return {**out, "evidence": "held in another pid namespace (a container sharing"
                                   " this hostname) - its pids are not visible here"}
    pid = holder["pid"]
    state, started = probe(pid)
    if state == "not-running":
        return {**out, "outcome": "not-running",
                "evidence": f"no process with pid {pid} is running on this host"}
    if state != "running":
        return {**out, "evidence": f"pid {pid} exists but cannot be inspected (access"
                                   " denied or unsupported platform)"}
    if started is None:
        return {**out, "evidence": f"pid {pid} is running, but this platform cannot"
                                   " report when it started"}
    token = holder.get("identity")
    seen_token = identity(pid) if token else None
    if token and seen_token:
        same = token == seen_token
        return {**out, "outcome": "alive" if same else "reused",
                "evidence": (f"pid {pid} is the very process that wrote the lock (exact"
                             " start identity)" if same else
                             f"pid {pid} is running but is NOT the process that wrote"
                             " the lock - the pid was reused (exact start identity)")}
    recorded = holder.get("started")
    if isinstance(recorded, (int, float)) and not isinstance(recorded, bool):
        same = abs(started - recorded) <= _START_TOLERANCE_S
        return {**out, "outcome": "alive" if same else "reused",
                "evidence": (f"pid {pid} is running and started when the lock's writer"
                             " did - the same process" if same else
                             f"pid {pid} is running but started at a different time than"
                             " the lock's writer - the pid was reused (identity)")}
    try:
        taken = datetime.fromisoformat(str(holder.get("taken_at"))).timestamp()
    except (ValueError, OSError, OverflowError):
        return {**out, "evidence": "the lock records neither a start time nor a readable"
                                   " taken_at - nothing to compare"}
    late = started > taken + _START_TOLERANCE_S
    return {**out, "outcome": "reused" if late else "alive",
            "evidence": (f"pid {pid} started AFTER the lock was taken - a process cannot"
                         " write a file before it exists (ordering; the lock recorded no"
                         " start time)" if late else
                         f"pid {pid} is running and predates the lock (ordering only;"
                         " the lock recorded no start time)")}


def _describe_lock(lock_path: Path) -> str:
    # C31 (D): the lock names WHO and SINCE WHEN — a bare PID invited an unsound
    # liveness check (the OS reuses PIDs; field case: a dead writer's PID belonged to
    # VS Code started hours later). Tolerant of legacy bare-int locks and unreadable
    # content (Windows share modes may deny the read while the owner holds the fd).
    try:
        raw = lock_path.read_text(encoding="utf-8").strip()
    except OSError:
        raw = ""
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    holder = (parsed if isinstance(parsed, dict)
              else {"pid": parsed} if isinstance(parsed, int)  # legacy bare-PID lock
              else {})
    try:
        mtime = datetime.fromtimestamp(lock_path.stat().st_mtime, timezone.utc)
        fallback = mtime.isoformat(timespec="seconds")
    except OSError:
        fallback = "unknown"
    try:
        seen = observe_lock(lock_path)
    except Exception as exc:  # noqa: BLE001 - a refusal message must never raise
        seen = {"outcome": "unobservable", "evidence": f"the observation failed ({exc})"}
    return (f"held by pid {holder.get('pid', '?')} on {holder.get('host', '?')} "
            f"since {holder.get('taken_at') or fallback}; observed: {seen['outcome']}"
            f" - {seen['evidence']}")


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Apply pending migrations (NNN > PRAGMA user_version) in lexical order.

    Plan 027 (B23): user_version is stamped from PYTHON, never inside the SQL files —
    schema.sql stays the frozen byte-identical twin of 001_init.sql (check.py enforces
    the identity). On today's always-fresh :memory: connections the skip is a no-op;
    it is the contract a future persistent database and `server_info.schema_version`
    stand on, and it makes double-application (a re-run over an existing schema) safe.
    """
    applied = conn.execute("PRAGMA user_version").fetchone()[0]
    for migration in sorted(MIGRATIONS_DIR.glob("[0-9]*.sql")):
        number = int(migration.name[:3])
        if number <= applied:
            continue  # 001 == schema.sql (stamped by connect); older = already applied
        conn.executescript(migration.read_text(encoding="utf-8"))
        conn.execute(f"PRAGMA user_version = {number}")
        applied = number


def schema_version() -> int:
    """The migration head this build applies (the newest migrations/NNN_*.sql number)."""
    numbers = [int(p.name[:3]) for p in MIGRATIONS_DIR.glob("[0-9]*.sql")]
    return max(numbers) if numbers else 0


def connect() -> sqlite3.Connection:
    """The single connection factory: FK enforcement ON, schema + migrations applied.

    schema.sql is the frozen byte-identical twin of migrations/001_init.sql; every
    later append-only migration (002+) is applied by _apply_migrations — that is what
    makes "new artifact type = registry entries + one migration file" real (plan 015/B9).
    """
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("PRAGMA user_version = 1")  # schema.sql IS migration 001
    _apply_migrations(conn)
    return conn


def _tables(conn: sqlite3.Connection) -> list[str]:
    """Schema-declared tables in creation order (= load order: refs are declared last)."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
        " AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
    ).fetchall()
    return [name for (name,) in rows if name not in DERIVED_TABLES]


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def _pk_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    info = conn.execute(f"PRAGMA table_info({table})").fetchall()
    keyed = [(row[5], row[1]) for row in info if row[5] > 0]
    return [name for _, name in sorted(keyed)] or [info[0][1]]


def load(data_dir: str | os.PathLike) -> sqlite3.Connection:
    """Read data/<table>.jsonl into a fresh integrity-enforcing SQLite connection.

    FK enforcement is deferred during the bulk load (canonical row order is PK order,
    not dependency order — forward references like decisions.promoted_to -> adrs are
    legal) and verified wholesale afterwards: violations still fail loud.
    """
    conn = connect()
    conn.execute("PRAGMA foreign_keys = OFF")
    data_dir = Path(data_dir)
    for table in _tables(conn):
        path = data_dir / f"{table}.jsonl"
        if not path.exists():
            continue
        cols = _columns(conn, table)
        placeholders = ", ".join("?" for _ in cols)
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        with open(path, encoding="utf-8", newline="") as fh:
            for lineno, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except ValueError as exc:
                    # plan 039: a bare JSON error names neither file nor line —
                    # package_verify reports this as a finding, so it must locate.
                    raise ValueError(f"{path.name}:{lineno}: {exc}") from None
                unknown = set(row) - set(cols)
                if unknown:
                    raise ValueError(
                        f"{path.name}:{lineno}: unknown keys {sorted(unknown)}"
                    )
                conn.execute(sql, [row.get(col) for col in cols])
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        table, rowid, parent, _ = violations[0]
        raise sqlite3.IntegrityError(
            f"foreign key violation loading {table!r} (row {rowid} -> {parent!r});"
            f" {len(violations)} violation(s) total"
        )
    return conn


def dump(conn: sqlite3.Connection, data_dir: str | os.PathLike) -> None:
    """Write normalized canonical JSONL back (CANONICAL.md rules; empty table = no file)."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    for table in _tables(conn):
        cols = _columns(conn, table)
        order = ", ".join(_pk_columns(conn, table))
        rows = conn.execute(
            f"SELECT {', '.join(cols)} FROM {table} ORDER BY {order}"
        ).fetchall()
        path = data_dir / f"{table}.jsonl"
        if not rows:
            if path.exists():
                path.unlink()  # stale file for a now-empty table
            continue
        lines = [
            json.dumps(dict(zip(cols, row)), ensure_ascii=False, separators=(",", ":"))
            for row in rows
        ]
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


class PackageStore:
    """Context-managed single writer for one package's data/ directory.

    with PackageStore(pkg_dir) as store:
        store.conn.execute(...)
        store.commit()          # write-back normalized text
    """

    def __init__(self, package_dir: str | os.PathLike):
        self.data_dir = Path(package_dir) / "data"
        self.conn: sqlite3.Connection | None = None
        self._lock_fd: int | None = None
        self._fingerprints: dict[str, str] = {}

    def _fingerprint(self) -> dict[str, str]:
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(self.data_dir.glob("*.jsonl"))}

    def __enter__(self) -> "PackageStore":
        self.data_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.data_dir / LOCK_NAME
        try:
            self._lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StoreLockedError(
                f"{lock_path} exists — another writer owns this package "
                f"({_describe_lock(lock_path)}). If the writer is gone, the server's "
                "package_unlock(name) reports the holder and removes the lock only "
                "on the operator's word"
            ) from None
        os.write(self._lock_fd, json.dumps({
            "pid": os.getpid(), "host": socket.gethostname(),
            "taken_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            # plan 063: the writer's own start time is what makes pid REUSE decidable
            "started": process_start_time(os.getpid())[1],
            "identity": process_identity(os.getpid()),
            "pidns": _pid_namespace(),
        }).encode("utf-8"))
        try:
            self.conn = load(self.data_dir)
        except BaseException:
            self._release_lock()
            raise
        self._fingerprints = self._fingerprint()
        return self

    def commit(self) -> None:
        # C31 (C1): verify the tree did not move underneath the session BEFORE the
        # unconditional dump — the field cost of skipping this is silent overwrite of
        # every incoming change (measured guard cost on a real package: 29 files /
        # 3.1 MB ≈ 0.02 s per commit).
        current = self._fingerprint()
        if current != self._fingerprints:
            changed = sorted(
                (set(current) ^ set(self._fingerprints))
                | {name for name in current.keys() & self._fingerprints.keys()
                   if current[name] != self._fingerprints[name]})
            raise StoreStaleError(
                f"data/ changed on disk since this session loaded it ({', '.join(changed)})"
                " — refusing to overwrite")
        self.conn.commit()
        dump(self.conn, self.data_dir)
        self._fingerprints = self._fingerprint()

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        self._release_lock()

    def _release_lock(self) -> None:
        if self._lock_fd is not None:
            os.close(self._lock_fd)
            self._lock_fd = None
            lock_path = self.data_dir / LOCK_NAME
            if lock_path.exists():
                lock_path.unlink()
