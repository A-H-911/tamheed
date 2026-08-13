"""Tamheed v2 package store — JSONL <-> SQLite, honoring CANONICAL.md (plan 007/B2).

Stdlib only. This module is the single loader/writer for a package's ``data/`` directory
and is reused by the plan-008 MCP server. See ADR-0001 for the doctrine.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
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
    return (f"held by pid {holder.get('pid', '?')} on {holder.get('host', '?')} "
            f"since {holder.get('taken_at') or fallback}")


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
                row = json.loads(line)
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
                f"({_describe_lock(lock_path)}; remove the stale lock deliberately "
                "if the writer crashed)"
            ) from None
        os.write(self._lock_fd, json.dumps({
            "pid": os.getpid(), "host": socket.gethostname(),
            "taken_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
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
