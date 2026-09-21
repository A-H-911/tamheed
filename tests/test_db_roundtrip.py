"""Round-trip + integrity tests for the v2 package store (plan 007/B2, ADR-0001).

Stdlib unittest only. Covers: JSONL -> SQLite -> JSONL byte identity, FK enforcement,
CHECK enforcement, ADR supersession immutability, the requirement auto-advance trigger,
and the single-writer lockfile.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))

import store  # noqa: E402  (plugins/tamheed/db/store.py)

ENTITY_TYPES = [
    ("requirement", "Requirement", "FR-", "Always"),
    ("decision", "Decision", "DEC-", "Always"),
    ("adr", "ADR", "ADR-", "Conditional"),
    ("acceptance-criterion", "Acceptance criterion", "AC-", "Always"),
    ("audit-verdict", "Audit verdict", "AV-", "Continuous"),
    ("test", "Test", "TEST-", "Conditional"),
    ("phase", "Phase", "PH-", "Always"),
    ("slice", "Slice", "SL-", "Always"),
    ("invariant", "Invariant", "INV-", "Conditional"),
    ("deferred-work", "Deferred work", "DW-", "Conditional"),
]


def seed(conn: sqlite3.Connection) -> None:
    """A minimal but relation-rich package: FR -> DEC/ADR/AC/TEST links, phase -> slice."""
    conn.executemany(
        "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
        " VALUES (?, ?, ?, ?)",
        ENTITY_TYPES,
    )
    conn.execute(
        "INSERT INTO packages (name, title, profile, mode, package_version, created_at)"
        " VALUES ('demo', 'Demo package', 'ai-agentic', 'full', '2.0.0', '2026-07-17')"
    )
    conn.execute(
        "INSERT INTO requirements (id, kind, title, mvp, lifecycle_status,"
        " source_kind, source_span)"
        " VALUES ('FR-001', 'functional', 'Triage inbound email', 1, 'Approved',"
        " 'brief', 'brief L10-L14')"
    )
    conn.execute(
        "INSERT INTO decisions (id, title, lifecycle_status)"
        " VALUES ('DEC-001', 'Human approval gate', 'Approved')"
    )
    conn.execute(
        "INSERT INTO adrs (id, title, context, decision, consequences, lifecycle_status)"
        " VALUES ('ADR-0001', 'Bounded loop', 'ctx', 'dec', 'cons', 'Approved')"
    )
    conn.execute(
        "INSERT INTO phases (id, title, lifecycle_status) VALUES ('PH-1', 'MVP', 'Approved')"
    )
    conn.execute(
        "INSERT INTO slices (id, title, phase_id) VALUES ('SL-001', 'Ingest', 'PH-1')"
    )
    conn.execute(
        "INSERT INTO acceptance_criteria (id, title, statement, requirement_id, slice_id,"
        " lifecycle_status) VALUES ('AC-001', 'Email triaged', 'given/when/then',"
        " 'FR-001', 'SL-001', 'Approved')"
    )
    conn.execute(
        "INSERT INTO tests (id, title) VALUES ('TEST-001', 'triage e2e')"
    )
    conn.executemany(
        "INSERT INTO trace_edges (from_id, to_id, relation) VALUES (?, ?, ?)",
        [
            ("FR-001", "DEC-001", "derives_from"),
            ("AC-001", "FR-001", "verifies"),
            ("TEST-001", "FR-001", "tests"),
            ("SL-001", "FR-001", "implements"),
        ],
    )
    conn.commit()


class RoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self._tmp.name)
        self.data = self.pkg / "data"

    def tearDown(self):
        self._tmp.cleanup()

    def _read_all(self):
        return {p.name: p.read_bytes() for p in sorted(self.data.glob("*.jsonl"))}

    def test_roundtrip_byte_identity(self):
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
        first = self._read_all()
        self.assertTrue(first, "seed produced no JSONL files")
        # Reload from text and write back untouched: bytes must be identical.
        with store.PackageStore(self.pkg) as s:
            s.commit()
        self.assertEqual(first, self._read_all())

    def test_canonical_shape(self):
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
        raw = (self.data / "requirements.jsonl").read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        # entity_index is derived and must never be serialized.
        self.assertFalse((self.data / "entity_index.jsonl").exists())

    def test_fk_violation_raises(self):
        conn = store.connect()
        seed(conn)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO trace_edges (from_id, to_id, relation)"
                " VALUES ('FR-001', 'FR-999', 'relates_to')"
            )

    def test_check_violation_raises(self):
        conn = store.connect()
        seed(conn)
        # D-U1: 'Draft' is not a legal decision status (G-DEC-STATUS as schema).
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO decisions (id, title, lifecycle_status)"
                " VALUES ('DEC-002', 'x', 'Draft')"
            )

    def test_provenance_not_null(self):
        conn = store.connect()
        seed(conn)
        # G-REQ-SRC as schema: requirements demand source_kind + source_span.
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO requirements (id, kind, title) VALUES ('FR-002', 'functional', 'x')"
            )

    def test_approved_adr_immutable(self):
        conn = store.connect()
        seed(conn)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("UPDATE adrs SET decision = 'rewritten' WHERE id = 'ADR-0001'")
        # Supersession path stays open: successor first, then point the old row at it.
        conn.execute(
            "INSERT INTO adrs (id, title, lifecycle_status)"
            " VALUES ('ADR-0002', 'Bounded loop v2', 'Proposed')"
        )
        conn.execute(
            "UPDATE adrs SET superseded_by = 'ADR-0002', lifecycle_status = 'Superseded'"
            " WHERE id = 'ADR-0001'"
        )

    def test_requirement_auto_advance(self):
        conn = store.connect()
        seed(conn)
        conn.execute(
            "INSERT INTO audit_verdicts (id, ac_id, verdict) VALUES ('AV-001', 'AC-001', 'Met')"
        )
        status = conn.execute(
            "SELECT lifecycle_status FROM requirements WHERE id = 'FR-001'"
        ).fetchone()[0]
        self.assertEqual(status, "Implemented")

    def test_gate_views(self):
        conn = store.connect()
        seed(conn)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM g_trace_failures").fetchone()[0], 0)
        conn.execute("DELETE FROM trace_edges WHERE from_id = 'TEST-001'")
        self.assertEqual(
            conn.execute("SELECT id FROM g_trace_failures").fetchall(), [("FR-001",)]
        )

    def test_lockfile_single_writer(self):
        with store.PackageStore(self.pkg):
            with self.assertRaises(store.StoreLockedError):
                store.PackageStore(self.pkg).__enter__()
        # Lock released on exit: reopening succeeds.
        with store.PackageStore(self.pkg):
            pass

    def _lock(self, **holder):
        lock = Path(self.pkg) / "data" / ".lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps(holder), encoding="utf-8")
        return lock

    def test_observe_lock_four_outcomes(self):
        """Plan 063 (findings_25 §1): the store OBSERVES a lock's holder and reports it —
        not-running / reused / alive / unobservable — and never guesses. Fakes drive
        the branches (a real pid would make this flaky); the discriminator for reuse
        is recorded-start != observed-start, both from the process API."""
        here = store.socket.gethostname()
        lock = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                          started=1000.0)
        obs = lambda probe: store.observe_lock(lock, probe=probe)["outcome"]
        # exact identity wins over the epoch tolerance when the lock recorded a token
        tok = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                         started=1000.0, identity="win:1")
        run = lambda pid: ("running", 1000.0)
        self.assertEqual(store.observe_lock(tok, probe=run, identity=lambda p: "win:1")
                         ["outcome"], "alive")
        self.assertEqual(store.observe_lock(tok, probe=run, identity=lambda p: "win:2")
                         ["outcome"], "reused")        # same second, different process
        ns = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                        pidns="pid:[1]")
        self.assertEqual(store.observe_lock(ns, probe=lambda pid: ("not-running", None))
                         ["outcome"], "unobservable")  # another container, never probed
        lock = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                          started=1000.0)
        self.assertEqual(obs(lambda pid: ("not-running", None)), "not-running")
        self.assertEqual(obs(lambda pid: ("running", 1000.5)), "alive")       # same process
        self.assertEqual(obs(lambda pid: ("running", 5000.0)), "reused")      # pid recycled
        self.assertEqual(obs(lambda pid: ("running", None)), "unobservable")  # no start time
        self.assertEqual(obs(lambda pid: ("unobservable", None)), "unobservable")
        other = self._lock(pid=4242, host="some-other-host", taken_at="2026-09-19T20:13:02+00:00")
        out = store.observe_lock(other, probe=lambda pid: ("not-running", None))
        self.assertEqual(out["outcome"], "unobservable")                      # never probed
        self.assertIn("another host", out["evidence"])

    def test_observe_lock_legacy_lock_falls_back_to_ordering(self):
        """A lock without a recorded start (pre-4.9.0, or a legacy bare pid) can only be
        judged by ordering: a process that started AFTER the lock was taken is not the
        writer (the field's VS Code case). Weaker than identity, and labelled so."""
        here = store.socket.gethostname()
        lock = self._lock(pid=71948, host=here, taken_at="2026-08-04T01:51:50+00:00")
        taken = datetime(2026, 8, 4, 1, 51, 50, tzinfo=timezone.utc).timestamp()
        late = store.observe_lock(lock, probe=lambda pid: ("running", taken + 8.5 * 3600))
        self.assertEqual(late["outcome"], "reused")
        self.assertIn("ordering", late["evidence"])
        early = store.observe_lock(lock, probe=lambda pid: ("running", taken - 60))
        self.assertEqual(early["outcome"], "alive")
        lock.write_text("71948", encoding="utf-8")                            # bare-int lock
        self.assertEqual(store.observe_lock(
            lock, probe=lambda pid: ("not-running", None))["outcome"], "unobservable")

    def test_a_garbled_pid_is_unobservable_and_the_refusal_never_raises(self):
        """Security review of plan 063: JSON accepts Infinity (int() overflows), bool is
        an int, and a huge pid truncates modulo 2**32 on Windows onto an unrelated live
        process. None may be probed, and none may mask the StoreLockedError."""
        for bad in (float("inf"), True, -1, 0, 2 ** 40, "4242", 4242.0, None):
            self.assertEqual(store.process_start_time(bad), ("unobservable", None), bad)
        lock = Path(self.pkg) / "data" / ".lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text('{"pid": Infinity, "host": "%s"}' % store.socket.gethostname(),
                        encoding="utf-8")
        with self.assertRaises(store.StoreLockedError) as ctx:
            store.PackageStore(self.pkg).__enter__()
        self.assertIn("observed: unobservable", str(ctx.exception))

    def test_process_probe_on_real_processes(self):
        """The real probe, on the two cases that cannot flake: this process is running
        with an observable-or-absent start, and a finished child whose handle is
        released is never reported as the same running process."""
        state, _ = store.process_start_time(os.getpid())
        self.assertEqual(state, "running")
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        try:
            pid = child.pid
            self.assertEqual(store.process_start_time(pid)[0], "running")
            alive_token = store.process_identity(pid)
        finally:
            child.kill()
            child.wait()
        # the handle is still held here: on Windows the dead process still OPENS, and
        # only its exit code says it is gone - the case the probe was written for
        self.assertEqual(store.process_start_time(pid)[0], "not-running")
        del child
        # whatever owns that pid now (nothing, or a recycled process) is NOT the child
        if alive_token is not None:
            self.assertNotEqual(store.process_identity(pid), alive_token)

    def test_lock_records_the_writers_start_and_refusal_reports_the_observation(self):
        with store.PackageStore(self.pkg):
            held = json.loads((Path(self.pkg) / "data" / ".lock").read_text(encoding="utf-8"))
            self.assertIn("started", held)
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
        self.assertIn("observed:", str(ctx.exception))
        # it is us: `alive` wherever the platform reports a start time, and an honest
        # `unobservable` where it cannot - never `not-running` or `reused`
        expected = ("alive" if store.process_start_time(os.getpid())[1] is not None
                    else "unobservable")
        self.assertIn(f"observed: {expected}", str(ctx.exception))

    def test_lock_error_names_holder(self):
        """Plan 025 (C31/D): the lock says WHO and SINCE WHEN — a bare PID invited an
        unsound liveness check (PID reuse); legacy bare-int locks still describe."""
        import os as _os
        with store.PackageStore(self.pkg):
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
            self.assertIn(f"pid {_os.getpid()}", str(ctx.exception))
            self.assertIn("since", str(ctx.exception))
        legacy = Path(self.pkg) / "data" / ".lock"
        legacy.write_text("71948", encoding="utf-8")     # pre-2.7.0 bare-PID lock
        try:
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
            self.assertIn("pid 71948", str(ctx.exception))
        finally:
            legacy.unlink()

    def test_commit_refuses_stale_tree(self):
        """Plan 025 (C31/C1): data/ moved underneath the session (git checkout, a
        second writer) -> StoreStaleError naming the file; disk state preserved."""
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()                                    # baseline fingerprints
            path = Path(self.pkg) / "data" / "requirements.jsonl"
            external = path.read_text(encoding="utf-8") + "\n"
            path.write_text(external, encoding="utf-8")   # the tree moves underneath
            s.conn.execute("UPDATE requirements SET title = 'clobber?' WHERE id = 'FR-001'")
            with self.assertRaises(store.StoreStaleError) as ctx:
                s.commit()
            self.assertIn("requirements.jsonl", str(ctx.exception))
            self.assertEqual(path.read_text(encoding="utf-8"), external)  # not clobbered
        # a fresh session reconciles: reopening reads the disk truth and can commit
        norm = external.rstrip("\n") + "\n"               # canonical load ignores blanks
        with store.PackageStore(self.pkg) as s2:
            s2.commit()
        self.assertEqual((Path(self.pkg) / "data" / "requirements.jsonl")
                         .read_text(encoding="utf-8"), norm)


if __name__ == "__main__":
    unittest.main(verbosity=2)
