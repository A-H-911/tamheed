"""Round-trip + integrity tests for the v2 package store (plan 007/B2, ADR-0001).

Stdlib unittest only. Covers: JSONL -> SQLite -> JSONL byte identity, FK enforcement,
CHECK enforcement, ADR supersession immutability, the requirement auto-advance trigger,
and the single-writer lockfile.
"""
import sqlite3
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
