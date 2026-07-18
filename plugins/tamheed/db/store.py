"""Tamheed v2 package store — JSONL <-> SQLite, honoring CANONICAL.md (plan 007/B2).

Stdlib only. This module is the single loader/writer for a package's ``data/`` directory
and is reused by the plan-008 MCP server. See ADR-0001 for the doctrine.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
MIGRATIONS_DIR = Path(__file__).with_name("migrations")
LOCK_NAME = ".lock"
DERIVED_TABLES = frozenset({"entity_index"})  # trigger-maintained; never serialized


class StoreLockedError(RuntimeError):
    """Another writer holds this package's data/.lock — fail loud, never wait."""


def connect() -> sqlite3.Connection:
    """The single connection factory: FK enforcement ON, schema + migrations applied.

    schema.sql is the frozen byte-identical twin of migrations/001_init.sql (check.py
    enforces the identity); every later append-only migration (002+) is applied here in
    lexical order — that is what makes "new artifact type = registry entries + one
    migration file" real (plan 015/B9).
    """
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    for migration in sorted(MIGRATIONS_DIR.glob("[0-9]*.sql")):
        if migration.name != "001_init.sql":  # 001 == schema.sql, already applied
            conn.executescript(migration.read_text(encoding="utf-8"))
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

    def __enter__(self) -> "PackageStore":
        self.data_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.data_dir / LOCK_NAME
        try:
            self._lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise StoreLockedError(
                f"{lock_path} exists — another writer owns this package "
                "(remove the stale lock deliberately if the writer crashed)"
            ) from None
        os.write(self._lock_fd, str(os.getpid()).encode("ascii"))
        try:
            self.conn = load(self.data_dir)
        except BaseException:
            self._release_lock()
            raise
        return self

    def commit(self) -> None:
        self.conn.commit()
        dump(self.conn, self.data_dir)

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
