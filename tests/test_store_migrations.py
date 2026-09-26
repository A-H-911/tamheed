"""Schema-migration mechanics for the v2 store (plan 027/B23).

Stdlib unittest only. Pins the contract migration 003+ lands on: PRAGMA user_version
tracks the applied head (stamped from Python, never inside the SQL files — schema.sql
stays 001's frozen byte-twin), re-application is a no-op, migrations apply BEFORE the
JSONL load, and a data/ directory carrying a JSONL for a table absent from the schema
loads without error (the dropped-table orphan case).
"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))

import store  # noqa: E402  (plugins/tamheed/db/store.py)

GOLDEN_DATA = REPO_ROOT / "generated-samples" / "support-triage-agent-v2" / "data"


class StoreMigrationTest(unittest.TestCase):
    def test_user_version_tracks_migration_head(self):
        """connect() leaves user_version at the newest migrations/NNN number.
        v4 (plan 031) re-baselined the chain: schema.sql IS the new 001, so a fresh
        repo checkout sits at head 1 until a future 002 ships."""
        conn = store.connect()
        head = conn.execute("PRAGMA user_version").fetchone()[0]
        self.assertEqual(head, store.schema_version())
        self.assertGreaterEqual(head, 1)
        conn.close()

    def test_apply_migrations_idempotent(self):
        """A second _apply_migrations pass applies nothing (002's CREATE TABLE would
        raise if re-run) and leaves user_version unchanged."""
        conn = store.connect()
        before = conn.execute("PRAGMA user_version").fetchone()[0]
        store._apply_migrations(conn)  # must skip everything already applied
        self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], before)
        conn.close()

    def test_migrations_apply_before_populated_load(self):
        """load() over a real populated package succeeds with post-001 tables present
        (ordering contract: schema -> migrations -> data)."""
        conn = store.load(GOLDEN_DATA)
        tables = {name for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertIn("glossary_terms", tables)  # 002's table exists alongside the data
        self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0],
                         store.schema_version())
        conn.close()

    def test_migration_002_lessons_lands(self):
        """Plan 035: the v4 chain's first real migration. Head is 2, the lessons
        table exists, and the recreated trace_edges CHECK accepts learned_from
        (and still rejects an unknown relation)."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)
        tables = {name for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertIn("lessons", tables)
        conn.executemany(  # registry rows are seeded at package_create, not in DDL
            "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
            " VALUES (?, ?, ?, ?)",
            [("lesson", "Lesson learned (LL-)", "LL-", "Continuous"),
             ("defect", "Defect (DEF-)", "DEF-", "Conditional")])
        conn.execute("INSERT INTO lessons (id, title, statement, kind)"
                     " VALUES ('LL-1', 't', 's', 'improve')")
        conn.execute("INSERT INTO defects (id, title, severity)"
                     " VALUES ('DEF-1', 'd', 'low')")
        conn.execute("INSERT INTO trace_edges VALUES ('LL-1', 'DEF-1', 'learned_from')")
        with self.assertRaises(Exception):
            conn.execute("INSERT INTO trace_edges VALUES ('LL-1', 'DEF-1', 'bogus_rel')")
        # the index survived the recreation
        idx = {name for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
            " AND tbl_name='trace_edges'")}
        self.assertIn("idx_trace_edges_to", idx)
        conn.close()

    def test_migration_003_skills_lands(self):
        """Plan 036: head is 3; skills exists; a lesson can be Promoted with
        promoted_to; the recreated journal CHECK accepts the lesson-guard event
        types; Promoted content is frozen (the extended trigger)."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 3)
        conn.executemany(
            "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
            " VALUES (?, ?, ?, ?)",
            [("lesson", "Lesson learned (LL-)", "LL-", "Continuous"),
             ("skill", "Skill (SKL-)", "SKL-", "On-request"),
             ("progress-entry", "Progress entry (PE-)", "PE-", "Continuous")])
        conn.execute("INSERT INTO skills (id, name, title, level)"
                     " VALUES ('SKL-1', 'boundary-checks', 'Boundary checks',"
                     " 'project')")
        conn.execute("INSERT INTO lessons (id, title, statement, kind,"
                     " lifecycle_status, promoted_to) VALUES ('LL-1', 't', 's',"
                     " 'improve', 'Promoted', 'SKL-1')")
        conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                     " VALUES ('PE-1', 'lesson-confirmed', 'e')")
        conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                     " VALUES ('PE-2', 'lesson-promoted', 'e')")
        with self.assertRaises(Exception):   # Promoted content frozen
            conn.execute("UPDATE lessons SET statement = 'x' WHERE id = 'LL-1'")
        with self.assertRaises(Exception):   # promoted_to re-pointing frozen
            conn.execute("UPDATE lessons SET promoted_to = NULL WHERE id = 'LL-1'")
        conn.close()

    def test_migration_004_amends_and_verify_land(self):
        """Plan 039 (findings_22 §2/§5): head is 4; the recreated trace_edges CHECK
        accepts `amends` (and still rejects an unknown relation); the recreated
        journal CHECK accepts `integrity-verified`; both indexes/triggers survive."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 4)
        conn.executemany(
            "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
            " VALUES (?, ?, ?, ?)",
            [("scope-change", "Scope change (SC-)", "SC-", "Continuous"),
             ("decision", "Decision (DEC-)", "DEC-", "Always"),
             ("progress-entry", "Progress entry (PE-)", "PE-", "Continuous")])
        conn.execute("INSERT INTO decisions (id, title, lifecycle_status)"
                     " VALUES ('DEC-1', 'd', 'Approved')")
        conn.execute("INSERT INTO scope_changes (id, decision_ref, description,"
                     " iteration) VALUES ('SC-1', 'DEC-1', 'x', 1)")
        conn.execute("INSERT INTO trace_edges VALUES ('SC-1', 'DEC-1', 'amends')")
        with self.assertRaises(Exception):
            conn.execute("INSERT INTO trace_edges VALUES ('SC-1', 'DEC-1', 'bogus')")
        conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                     " VALUES ('PE-1', 'integrity-verified', 'e')")
        with self.assertRaises(Exception):
            conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                         " VALUES ('PE-2', 'bogus-event', 'e')")
        idx = {name for (name,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
            " AND tbl_name='trace_edges'")}
        self.assertIn("idx_trace_edges_to", idx)
        self.assertEqual(conn.execute(
            "SELECT entity_type FROM entity_index WHERE id='PE-1'").fetchone()[0],
            "progress-entry")  # the trigger pair was recreated
        conn.close()

    def test_migration_005_feedback_lands(self):
        """Plan 087: head is 5; feedback exists with its kind and status vocabularies;
        a local-tool row must name its file; the index trigger fires."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 5)
        conn.execute("INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
                     " VALUES ('feedback', 'Upstream feedback (FB-)', 'FB-', 'Continuous')")
        conn.execute("INSERT INTO feedback (id, kind, title, workaround) VALUES"
                     " ('FB-1', 'missing-capability', 'no patch mode', 'a scratch script')")
        self.assertEqual(conn.execute("SELECT entity_type FROM entity_index WHERE id = 'FB-1'")
                         .fetchone()[0], "feedback")
        self.assertEqual(conn.execute("SELECT lifecycle_status FROM feedback").fetchone()[0],
                         "Proposed")
        with self.assertRaises(Exception):   # a tool row names its file
            conn.execute("INSERT INTO feedback (id, kind, title) VALUES ('FB-2', 'local-tool', 't')")
        with self.assertRaises(Exception):   # closed vocabulary
            conn.execute("INSERT INTO feedback (id, kind, title) VALUES ('FB-3', 'praise', 't')")
        conn.execute("INSERT INTO feedback (id, kind, title, tool_path) VALUES"
                     " ('FB-2', 'local-tool', 't', 'scripts/gen-record-slate.mjs')")
        conn.close()

    def test_migration_006_carries_lands(self):
        """Plan 113: head is 6; `carries` is a legal relation and the vocabulary stays closed."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 6)
        for tid, prefix in (("phase", "PH-"), ("slice", "SL-"), ("wbs-item", "WBS-"),
                            ("deferred-work", "DW-")):
            conn.execute("INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
                         " VALUES (?, ?, ?, 'Continuous')", (tid, tid, prefix))
        conn.execute("INSERT INTO phases (id, title) VALUES ('PH-1', 'p')")
        conn.execute("INSERT INTO slices (id, title, phase_id) VALUES ('SL-1', 's', 'PH-1')")
        conn.execute("INSERT INTO wbs_items (id, title, slice_id) VALUES ('WBS-1', 'w', 'SL-1')")
        conn.execute("INSERT INTO deferred_work (id, title, severity, activation_trigger)"
                     " VALUES ('DW-1', 'd', 'low', 't')")
        conn.execute("INSERT INTO trace_edges (from_id, to_id, relation) VALUES"
                     " ('WBS-1', 'DW-1', 'carries')")
        with self.assertRaises(Exception):   # closed vocabulary
            conn.execute("INSERT INTO trace_edges (from_id, to_id, relation) VALUES"
                         " ('WBS-1', 'DW-1', 'frobs')")
        conn.close()

    def test_migration_007_handoff_lands(self):
        """Plan 121 (v5.1): head is 7; `handoff` is a legal journal kind, the vocabulary stays
        closed, the trigger pair survives the recreation, and skills carry `upstreamed_to`."""
        conn = store.connect()
        self.assertGreaterEqual(conn.execute("PRAGMA user_version").fetchone()[0], 7)
        conn.execute("INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
                     " VALUES ('progress-entry', 'Progress entry (PE-)', 'PE-', 'Continuous')")
        conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                     " VALUES ('PE-1', 'handoff', 'Resume at: the next slice')")
        with self.assertRaises(Exception):   # closed vocabulary
            conn.execute("INSERT INTO progress_entries (id, event_type, entry)"
                         " VALUES ('PE-2', 'hand-off', 'e')")
        self.assertEqual(conn.execute(
            "SELECT entity_type FROM entity_index WHERE id='PE-1'").fetchone()[0],
            "progress-entry")  # the trigger pair was recreated
        cols = [r[1] for r in conn.execute("PRAGMA table_info(skills)")]
        self.assertIn("upstreamed_to", cols)
        self.assertEqual(cols[-1], "upstreamed_to")  # appended: the JSONL key lands last
        conn.execute("INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
                     " VALUES ('skill', 'Skill (SKL-)', 'SKL-', 'Continuous')")
        conn.execute("INSERT INTO skills (id, name, title, lifecycle_status, upstreamed_to)"
                     " VALUES ('SKL-1', 'writing-rows', 't', 'Obsolete', 'tamheed:package-writes')")
        conn.close()

    def test_load_ignores_orphan_jsonl_of_dropped_table(self):
        """A data/ dir with a JSONL for a table the schema no longer declares loads
        without error — the contract a DROP TABLE migration (003) lands on. The orphan
        file is skipped, not deleted; converters/callers own any loud reporting."""
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data / "no_such_table.jsonl").write_text(
                '{"id": "X-001"}\n', encoding="utf-8")
            conn = store.load(data)  # must not raise
            self.assertTrue((data / "no_such_table.jsonl").exists())
            conn.close()


if __name__ == "__main__":
    unittest.main()
