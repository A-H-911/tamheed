"""Plan 230: the tests, written before the fix. Run once from the repository root.

    python plans/evidence/scripts-230/tests_230.py

Each replacement must find its text exactly once. On the code of 6.5.0 seven tests then fail.
"""
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TIME = r'r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$"'


def patch(rel: str, pairs: list) -> None:
    path = ROOT / rel
    text = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, (rel, text.count(old), old[:70])
        text = text.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


patch("tests/test_migrate_v3to4.py", [
    ("import unittest\nfrom pathlib import Path\n",
     "import unittest\nfrom pathlib import Path\nfrom unittest import mock\n"),
    ('        self.assertEqual(audit[0]["actor"], "system:migrate")\n',
     '        self.assertEqual(audit[0]["actor"], "system:migrate")\n'
     "        # plan 230: the row says when the migration ran. It had no time from 4.0.0 to 6.5.0\n"
     f'        self.assertRegex(str(audit[0].get("occurred_at")), {TIME})\n'),
    ('''class MigrateDeterminismTest(unittest.TestCase):
    def test_same_input_same_bytes(self):
        outs = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as td:
                srv.PACKAGE_ROOT = Path(td)
                srv._CURRENT = srv._CURRENT_NAME = None
                pkg = build_v3_fixture(srv.PACKAGE_ROOT)
                res = srv.package_migrate("legacy", confirm=True)
                self.assertTrue(res.get("ok"), res)
                outs.append({p.name: p.read_bytes()
                             for p in sorted((pkg / "data").glob("*.jsonl"))})
        self.assertEqual(set(outs[0]), set(outs[1]))
        for name in outs[0]:
            self.assertEqual(outs[0][name], outs[1][name],
                             f"{name} differs between identical migrations")
''',
     '''class MigrateDeterminismTest(unittest.TestCase):
    def _migrate(self, clock: str) -> dict:
        """The files of one migration of the fixture, with the server's clock held at `clock`."""
        with tempfile.TemporaryDirectory() as td, \\
                mock.patch.object(srv, "_now", return_value=clock):
            srv.PACKAGE_ROOT = Path(td)
            srv._CURRENT = srv._CURRENT_NAME = None
            pkg = build_v3_fixture(srv.PACKAGE_ROOT)
            res = srv.package_migrate("legacy", confirm=True)
            self.assertTrue(res.get("ok"), res)
            return {p.name: p.read_bytes() for p in sorted((pkg / "data").glob("*.jsonl"))}

    def test_same_input_same_bytes(self):
        """Under one clock. The migration's journal row carries the time of the run (plan
        230), so two runs a second apart differ in that one value."""
        first = self._migrate("2026-01-01T00:00:00Z")
        second = self._migrate("2026-01-01T00:00:00Z")
        self.assertEqual(set(first), set(second))
        for name in first:
            self.assertEqual(first[name], second[name],
                             f"{name} differs between identical migrations")

    def test_the_clock_is_the_only_difference_between_two_runs(self):
        """Plan 230: two runs under two clocks differ in one column of one row, and nowhere
        else. So the bytes of a migration depend on its input and on the clock alone."""
        first = self._migrate("2026-01-01T00:00:00Z")
        second = self._migrate("2026-01-02T00:00:00Z")
        self.assertEqual(sorted(n for n in first if first[n] != second[n]),
                         ["progress_entries.jsonl"])
        one, two = ([json.loads(line) for line in files["progress_entries.jsonl"]
                     .decode("utf-8").splitlines()] for files in (first, second))
        self.assertEqual(len(one), len(two))
        differ = [(a["id"], sorted(k for k in a if a[k] != b[k]))
                  for a, b in zip(one, two) if a != b]
        self.assertEqual([cols for _, cols in differ], [["occurred_at"]], differ)
'''),
])

patch("tests/test_mcp_contract.py", [
    # 1) a registry sync for a missing type
    ('''        pes = srv.entity_query("progress-entry")["rows"]
        self.assertTrue(any("REGISTRY-SYNC" in (p.get("entry") or "")
                            for p in pes))
        srv.package_close()
        again = srv.package_migrate("demo")      # registry now current -> refuses
''',
     f'''        pes = srv.entity_query("progress-entry")["rows"]
        self.assertTrue(any("REGISTRY-SYNC" in (p.get("entry") or "")
                            for p in pes))
        sync = [p for p in pes if "REGISTRY-SYNC" in (p.get("entry") or "")]
        self.assertRegex(str(sync[-1].get("occurred_at")), {TIME})   # plan 230
        srv.package_close()
        again = srv.package_migrate("demo")      # registry now current -> refuses
'''),
    # 2) a sync for a column alone, and the resume block that shows the row
    ('''            self.assertTrue(srv.package_migrate("demo", confirm=True)["ok"])
            self.assertTrue(srv.package_open("demo")["ok"])
            entry = srv.entity_query("progress-entry", limit=100000)["rows"][-1]["entry"]
            self.assertEqual(entry, "REGISTRY-SYNC: columns added (lessons: promoted_to)")
''',
     f'''            self.assertTrue(srv.package_migrate("demo", confirm=True)["ok"])
            opened = srv.package_open("demo")
            self.assertTrue(opened["ok"])
            row = srv.entity_query("progress-entry", limit=100000)["rows"][-1]
            self.assertEqual(row["entry"], "REGISTRY-SYNC: columns added (lessons: promoted_to)")
            self.assertRegex(str(row.get("occurred_at")), {TIME})    # plan 230
            latest = opened["resume"]["last_entries"][0]             # the resume block shows it
            self.assertEqual((latest["id"], latest["occurred_at"]), (row["id"], row["occurred_at"]))
'''),
    # 3) a sync that relocates a foreign file
    ('''        journal = srv.entity_query("progress-entry", search="REGISTRY-SYNC")["rows"]
        self.assertEqual(len(journal), 1)
''',
     f'''        journal = srv.entity_query("progress-entry", search="REGISTRY-SYNC")["rows"]
        self.assertEqual(len(journal), 1)
        self.assertRegex(str(journal[0].get("occurred_at")), {TIME})   # plan 230
'''),
    # 4) R119: the stopped swap now holds the journal's row too, and the retry adds a second
    ('''        moved = sorted(n for n in before if before[n] != after[n])
        self.assertEqual(moved, ["constraints.jsonl"])
        self.assertNotIn("UNCHANGED", out["error"])
        for needle in ("No table was removed", "constraints.jsonl", "package_migrate again",
                       "restore data/ from git"):
            self.assertIn(needle, out["error"], needle)
        self.assertTrue(srv.package_migrate("demo", confirm=True)["ok"])
        self.assertTrue(srv.package_open("demo")["ok"])
        self.assertTrue(srv.package_verify()["verified"])
        srv.package_close()
''',
     f'''        moved = sorted(n for n in before if before[n] != after[n])
        # R119 (plan 230): the journal file goes first, so it holds the sync's row already.
        # (As built, this assertion reads the new file apart: the fixture had no journal file.)
        self.assertEqual(moved, ["constraints.jsonl", "progress_entries.jsonl"])
        self.assertNotIn("UNCHANGED", out["error"])
        for needle in ("No table was removed", "constraints.jsonl", "package_migrate again",
                       "restore data/ from git"):
            self.assertIn(needle, out["error"], needle)
        self.assertTrue(srv.package_migrate("demo", confirm=True)["ok"])
        self.assertTrue(srv.package_open("demo")["ok"])
        self.assertTrue(srv.package_verify()["verified"])
        sync = srv.entity_query("progress-entry", search="REGISTRY-SYNC")["rows"]
        self.assertEqual(len(sync), 2)                    # the stopped run, and the run that finished
        for row in sync:
            self.assertRegex(str(row.get("occurred_at")), {TIME})
        srv.package_close()

    def test_a_sync_whose_journal_file_is_held_moves_no_file_and_runs_again(self):
        """R119 (plan 230). The swap ran in sorted order, so `progress_entries.jsonl` came
        after `entity_types.jsonl`. With the journal file held, every other file was written.
        A second run then answered "Nothing to migrate", and the sync had no journal row. The
        journal file now goes first: this failure moves no file, and the second run does it all."""
        data = self._behind_in_one_type()
        before = {{p.name: p.read_bytes() for p in data.iterdir()}}
        real = srv.os.replace

        def held(src, dst, *args, **kwargs):
            if Path(dst).name == "progress_entries.jsonl":
                raise PermissionError(13, "the file is held by another program")
            return real(src, dst, *args, **kwargs)

        srv.os.replace = held
        try:
            out = srv.package_migrate("demo", confirm=True)
        finally:
            srv.os.replace = real
        self.assertFalse(out["ok"], out)
        after = {{p.name: p.read_bytes() for p in data.iterdir()}}
        self.assertEqual(sorted(n for n in before if before[n] != after.get(n)), [])
        self.assertEqual(set(after), set(before))                       # no .tmp is left
        self.assertIn("UNCHANGED", out["error"])
        again = srv.package_migrate("demo", confirm=True)
        self.assertTrue(again["ok"], again)
        self.assertTrue(srv.package_open("demo")["ok"])
        sync = srv.entity_query("progress-entry", search="REGISTRY-SYNC")["rows"]
        self.assertEqual(len(sync), 1)
        srv.package_close()

    def test_every_journal_row_that_the_server_builds_names_its_time(self):
        """FB-033 of the first field (plan 230): `package_migrate` built its journal row as a
        dict with no `occurred_at`, from 4.0.0 to 6.5.0. Every other writer is an INSERT that
        names the column. This reads the writers in the server's source. So a row that an
        earlier release wrote never fails it."""
        import ast
        source = (REPO_ROOT / "plugins" / "tamheed" / "server" / "tamheed_server.py"
                  ).read_text(encoding="utf-8")
        nodes = list(ast.walk(ast.parse(source)))

        def keys(node) -> set:
            return {{k.value for k in node.keys if isinstance(k, ast.Constant)}}

        built = [n for n in nodes if isinstance(n, ast.Dict) and {{"actor", "event_type"}} <= keys(n)]
        self.assertGreaterEqual(len(built), 1)            # the guard reads at least one row
        for node in built:
            self.assertIn("occurred_at", keys(node), f"tamheed_server.py line {{node.lineno}}")
        inserts = [n.value for n in nodes if isinstance(n, ast.Constant)
                   and isinstance(n.value, str) and "INSERT INTO progress_entries" in n.value]
        self.assertEqual(len(inserts), source.count("INSERT INTO progress_entries"))  # each is read
        for text in inserts:
            columns = re.search(r"INSERT INTO progress_entries \\(([^)]*)\\)", text)
            self.assertIsNotNone(columns, text[:80])
            self.assertIn("occurred_at", columns.group(1), text[:80])
'''),
])

patch("tests/test_resume_hook.py", [
    ('''    def test_a_v6_note_still_resumes(self):
''',
     '''    def test_a_package_that_is_behind_names_the_file_and_the_migration(self):
        """R118 (plan 230). The header's schema number is the engine's. For a package with a
        data file behind the engine, the hook said "unlocked", and `package_open` then refused
        it. The hook now names the file, the column and `package_migrate`. It reads the same
        check as the open, so the two never disagree."""
        self._package()
        current, _ = run_hook(self.project, source="startup")
        self.assertNotIn("package_migrate", current)       # a current package gets no such line
        path = self.project / "pkg" / "data" / "requirements.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        key = sorted(k for k in rows[0] if rows[0][k] is None)[0]
        path.write_text("".join(json.dumps({k: v for k, v in r.items() if k != key},
                                           ensure_ascii=False, separators=(",", ":")) + "\\n"
                                for r in rows), encoding="utf-8")
        before = path.read_bytes()
        out, code = run_hook(self.project, source="startup")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("tamheed resume — package `pkg` (schema 10)"), lines[0])
        fact = f"requirements.jsonl lacks `{key}`"
        self.assertIn(fact, lines[1])
        for needle in ("BEHIND THIS ENGINE", "package_open refuses", "package_migrate"):
            self.assertIn(needle, lines[1], needle)
        self.assertIn(fact, srv.package_open("pkg").get("error", ""))   # the open says the same
        self.assertEqual(path.read_bytes(), before)                     # the hook writes nothing
        self.assertLessEqual(len(lines), hook.MAX_LINES)

    def test_a_v6_note_still_resumes(self):
'''),
])
print("tests of plan 230 written")
