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
        """connect() leaves user_version at the newest migrations/NNN number."""
        conn = store.connect()
        head = conn.execute("PRAGMA user_version").fetchone()[0]
        self.assertEqual(head, store.schema_version())
        self.assertGreaterEqual(head, 2)  # 002_example_glossary.sql ships with the repo
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
