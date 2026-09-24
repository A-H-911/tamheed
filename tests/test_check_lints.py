"""check.py's own lints under test (plan 056): the release gate is verified, not trusted."""
import io, json, shutil, sys, tempfile, unittest, contextlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import check  # noqa: E402

IGNORE = shutil.ignore_patterns(".git", ".claude", "__pycache__", "evidence", "sample-results")


class CheckLintsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.copy = Path(cls._tmp.name) / "repo"
        shutil.copytree(REPO_ROOT, cls.copy, ignore=IGNORE)

    @classmethod
    def tearDownClass(cls):
        check.REPO = REPO_ROOT
        cls._tmp.cleanup()

    def _lint(self) -> tuple[int | None, str]:
        check.REPO = self.copy
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                check.gate_lint()
            return None, out.getvalue()
        except SystemExit as exc:
            return exc.code, out.getvalue()
        finally:
            check.REPO = REPO_ROOT

    def _restore(self, rel: str):
        shutil.copy2(REPO_ROOT / rel, self.copy / rel)

    def test_lints_pass_on_the_repo_copy(self):
        code, out = self._lint()
        self.assertIsNone(code, out)
        self.assertGreaterEqual(out.count("lint:"), 11)

    def test_version_mismatch_is_caught(self):
        rel = "plugins/tamheed/.claude-plugin/plugin.json"
        p = self.copy / rel
        data = json.loads(p.read_text(encoding="utf-8")); data["version"] = "0.0.1"
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("CHECK FAILED", out)
        finally:
            self._restore(rel)

    def test_dead_path_reference_is_caught(self):
        rel = "plugins/tamheed/skills/tamheed/SKILL.md"
        p = self.copy / rel
        p.write_text(p.read_text(encoding="utf-8") + "\nSee `references/does-not-exist.md`.\n",
                     encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("dead path references", out)
        finally:
            self._restore(rel)

    def test_skill_frontmatter_drift_is_caught(self):
        """Plan 114 (lint 12): a skill folder whose frontmatter name differs from the folder
        is invoked under a name the docs never show - the lint refuses it."""
        rel = "plugins/tamheed/skills/probe-drift/SKILL.md"
        p = self.copy / rel
        p.parent.mkdir(parents=True)
        p.write_text("---\nname: something-else\ndescription: A probe.\n---\nBody.\n",
                     encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("skills lint", out)
        finally:
            p.unlink(); p.parent.rmdir()

    def test_stack_coupled_skill_is_caught(self):
        """Plan 114 (lint 12): the bundle's teaching surface is stack-neutral (front-door
        principle 9) and never carries a field package's identifiers."""
        rel = "plugins/tamheed/skills/probe-stack/SKILL.md"
        p = self.copy / rel
        p.parent.mkdir(parents=True)
        p.write_text("---\nname: probe-stack\ndescription: A probe.\n---\n"
                     "Run it on Kestrel; see WBS-40.3.\n", encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("skills lint", out)
            self.assertIn("Kestrel", out); self.assertIn("WBS-", out)
        finally:
            p.unlink(); p.parent.rmdir()

    def test_widened_mcp_pin_is_caught(self):
        rel = "plugins/tamheed/server/tamheed_server.py"
        p = self.copy / rel
        p.write_text(p.read_text(encoding="utf-8").replace('"mcp>=1.2,<2"', '"mcp>=1.2"', 1),
                     encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("PEP 723", out)
        finally:
            self._restore(rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
