"""Plan 230, after the independent review. Run once from the repository root.

1. `_columns_behind` quoted no table name. A data file named like an SQL keyword made the open
   and the session-start hook raise a raw SQL error. The name is quoted now.
2. "A second run always finishes" was too strong: a file that differs only in its spelling
   gives the second run no reason. The word leaves the three documents.
"""
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def patch(rel: str, pairs: list) -> None:
    path = ROOT / rel
    text = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, (rel, text.count(old), old[:70])
        text = text.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


patch("plugins/tamheed/server/tamheed_server.py", [
    ('ddl.execute(f"PRAGMA table_info({path.stem})")]',
     "ddl.execute(f'PRAGMA table_info(\"{path.stem}\")')]"),
])
patch("CHANGELOG.md", [
    ("Now a second run always finishes the sync. A\n",
     "Now a second run finishes the sync. A\n"),
    ("  the engine's. One line now names the file, the column and `package_migrate`.\n",
     "  the engine's. One line now names the file, the column and `package_migrate`.\n"
     "- A data file named like an SQL keyword, such as `select.jsonl`, made `package_open` and the\n"
     "  hook raise a raw SQL error (plan 230, found in review). Such a file is no table of the\n"
     "  engine, and it is passed over now.\n"),
])
patch("plugins/tamheed/server/README.md", [
    ("so that second run always has work to finish.", "so that second run has work to finish."),
])
patch("plans/230-migration-row-time.md", [
    ("and a retry that always finishes.", "and a retry that finishes."),
])
patch("tests/test_resume_hook.py", [
    ('''    def test_a_v6_note_still_resumes(self):
''',
     '''    def test_a_file_named_like_an_sql_keyword_is_no_table_and_costs_nothing(self):
        """Plan 230, found in review: the check for a package that is behind put the file's
        name into a statement unquoted. `select.jsonl` made the open and this hook raise a raw
        SQL error. The name is quoted, and a file that is no table of the engine is passed over."""
        self._package()
        (self.project / "pkg" / "data" / "select.jsonl").write_text('{"id":"X-1"}\\n', encoding="utf-8")
        self.assertEqual(srv._columns_behind(self.project / "pkg"), {})
        out, code = run_hook(self.project, source="startup")
        self.assertEqual(code, 0)
        self.assertTrue(out.splitlines()[0].startswith("tamheed resume — package `pkg`"), out)
        self.assertNotIn("OperationalError", out)
        self.assertNotIn("OperationalError", str(srv.package_open("pkg")))

    def test_a_v6_note_still_resumes(self):
'''),
])
print("review fixes of plan 230 applied")
