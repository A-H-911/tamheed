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
        self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)
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
