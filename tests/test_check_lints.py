"""check.py's own lints under test (plan 056): the release gate is verified, not trusted."""
import io, json, re, shutil, sys, tempfile, unittest, contextlib
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
        self.assertGreaterEqual(out.count("lint:"), 13)
        self.assertIn("binding vocabulary", out)                  # lint 13 ran
        self.assertIn("plain English", out)                       # lint 14 ran

    # ---- lint 14, plain English (plan 181): the roster is red at the first hard finding
    _ROSTERED = "plugins/tamheed/references/vocabulary.md"

    def _append_rostered(self, text: str):
        p = self.copy / self._ROSTERED
        p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")

    def test_semicolon_in_a_rostered_surface_is_caught(self):
        self._append_rostered("\nA sentence; with a semicolon.\n")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("plain English", out)
            self.assertIn("semicolon", out); self.assertIn(self._ROSTERED, out)
        finally:
            self._restore(self._ROSTERED)

    def test_wrapped_long_sentence_is_caught(self):
        words = " ".join(f"word{i}" for i in range(30))
        wrapped = "\n" + words[:70] + "\n" + words[70:140] + "\n" + words[140:] + ".\n"
        self._append_rostered(wrapped)
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("long-sentence", out)
        finally:
            self._restore(self._ROSTERED)

    def test_hedges_terms_and_code_spans_pass(self):
        self._append_rostered("\nVerify before you claim. The lesson is operator-confirmed."
                              " The write may have failed. The flag `--a; --b` is one token.\n")
        try:
            code, out = self._lint()
            self.assertIsNone(code, out)
        finally:
            self._restore(self._ROSTERED)

    def test_allow_marker_without_a_reason_is_caught(self):
        self._append_rostered("\n<!-- ste:allow semicolon -->\nQuoted; as the standard wrote it.\n")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("allow-without-reason", out)
        finally:
            self._restore(self._ROSTERED)

    def test_allow_marker_with_a_reason_passes_and_is_counted(self):
        def markers(text: str) -> int:
            m = re.search(r"allow markers=(\d+)", text)
            self.assertIsNotNone(m, text)
            return int(m.group(1))
        _, before = self._lint()  # the tree carries its own markers (README's link bar, CLAUDE.md's id list)
        self._append_rostered("\n<!-- ste:allow semicolon: the standard's own sentence, quoted -->\n"
                              "Quoted; as the standard wrote it.\n")
        try:
            code, out = self._lint()
            self.assertIsNone(code, out); self.assertEqual(markers(out), markers(before) + 1, out)
        finally:
            self._restore(self._ROSTERED)

    # ---- plan 188: the last wave landed; the guide's prose is linted by import, both languages
    def test_ste_pending_is_empty(self):
        self.assertEqual(check._STE_PENDING, ())

    def test_ste_roster_covers_the_scope(self):
        import fnmatch
        scope = check._ste_scope(REPO_ROOT)
        rostered = [rel for rel in scope if any(fnmatch.fnmatchcase(rel, g) for g, *_ in check._STE_SURFACES)]
        self.assertEqual(sorted(rostered), scope)
        self.assertIn("docs/guide/content.py", scope)

    _GUIDE = "docs/guide/content.py"

    def test_arabic_semicolon_in_the_guide_prose_is_caught_by_id(self):
        p = self.copy / self._GUIDE
        src = p.read_text(encoding="utf-8")
        needle = '"ui.toc.contents": {"en": "Contents", "ar": "المحتويات"},'
        self.assertIn(needle, src)
        p.write_text(src.replace(needle, '"ui.toc.contents": {"en": "Contents", "ar": "المحتويات؛ الفهرس"},'),
                     encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("content.py:ui.toc.contents.ar", out)
            self.assertIn("semicolon", out)
        finally:
            self._restore(self._GUIDE)

    def test_long_english_sentence_in_the_guide_prose_is_caught_by_id(self):
        p = self.copy / self._GUIDE
        src = p.read_text(encoding="utf-8")
        needle = '"ui.toc.contents": {"en": "Contents", "ar": "المحتويات"},'
        long = " ".join(["word"] * 26) + "."
        p.write_text(src.replace(needle, f'"ui.toc.contents": {{"en": "{long}", "ar": "المحتويات"}},'),
                     encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("content.py:ui.toc.contents.en", out)
            self.assertIn("long-sentence", out)
        finally:
            self._restore(self._GUIDE)

    # ---- plan 190: the current field brief is rostered by its path; older briefs are not scanned
    _BRIEF = "plans/briefs/acmp-6.0.0.md"

    def test_current_brief_is_in_the_roster(self):
        self.assertIn(self._BRIEF, check._ste_scope(REPO_ROOT))
        self.assertNotIn("plans/briefs/acmp-5.9.0.md", check._ste_scope(REPO_ROOT))
        p = self.copy / self._BRIEF
        p.write_text(p.read_text(encoding="utf-8") + "\nA sentence; with a semicolon.\n", encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn(self._BRIEF, out); self.assertIn("semicolon", out)
        finally:
            self._restore(self._BRIEF)

    def test_prose_file_in_neither_roster_nor_pending_is_caught(self):
        probe = self.copy / "plugins" / "tamheed" / "probe-neither.md"  # the bundle root: no roster or pending glob covers it
        probe.write_text("A clean sentence.\n", encoding="utf-8")
        try:
            code, out = self._lint()
            self.assertEqual(code, 1); self.assertIn("probe-neither.md", out)
        finally:
            probe.unlink()

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

    def test_blurred_binding_vocabulary_is_caught(self):
        """Plan 147 (lint 13, v5.5, R34): the bundle shipped two meanings of "binds" for
        three releases and no check saw it. The status binds; the note's roster is what
        is rendered. A sentence that gates BINDING on the emit or the roster is refused -
        and one that gates it on the operator's word is not."""
        rel = "plugins/tamheed/skills/reading-the-record/SKILL.md"
        p = self.copy / rel
        original = p.read_text(encoding="utf-8")
        try:
            for blurred in ("An Approved lesson binds nothing until the emit\nthat renders it.",
                            "this lesson BINDS only once the note is rebuilt",
                            "unpin what no longer needs to bind every session",
                            "What binds a session is the tool-owned note's roster"):
                p.write_text(original + "\n" + blurred + "\n", encoding="utf-8")
                code, out = self._lint()
                self.assertEqual(code, 1, blurred)
                self.assertIn("binding vocabulary", out)
            # the controls: correct under R34, and a dated quote of the old text
            p.write_text(original + "\nA proposed lesson binds nothing until the operator says"
                         " so.\n\n> **Correction, 2026-09-27.** The hint said \"BINDS only once"
                         " the note is rebuilt\".\n", encoding="utf-8")
            code, out = self._lint()
            self.assertIsNone(code, out)
        finally:
            self._restore(rel)

    def test_negated_binding_vocabulary_is_caught(self):
        """Plan 152 (lint 13, v5.6, findings_37): the field's memory said approving a lesson
        "does NOT bind it" until the emit, and plan 147's shapes passed that sentence - they
        held no negated form. A negation of BIND gated on the emit, the note or the roster is
        refused; one gated on the operator's word is not, and the window never crosses a full
        stop, a semicolon or a colon into the next clause."""
        rel = "plugins/tamheed/skills/reading-the-record/SKILL.md"
        p = self.copy / rel
        original = p.read_text(encoding="utf-8")
        try:
            for blurred in ("approving and pinning a lesson does NOT bind it - `handoff_emit`"
                            " in the SAME round",
                            "an approved lesson does not bind until the emit has run",
                            "a lesson doesn't bind\nuntil the note lists it"):
                p.write_text(original + "\n" + blurred + "\n", encoding="utf-8")
                code, out = self._lint()
                self.assertEqual(code, 1, blurred)
                self.assertIn("binding vocabulary", out)
            # The probe keeps its semicolon on purpose (the lint-13 window must stop at
            # one), and the skill is a rostered plain-English surface (lint 14), so the
            # probe carries the allow marker a real author would.
            p.write_text(
                original + "\n<!-- ste:allow semicolon: lint-13 probe, the window must not"
                " cross a semicolon -->\n"
                "A lesson does not bind until the operator approves it.\n"
                "A Proposed lesson binds nothing and may be rejected freely.\n"
                "A lesson does not bind until the operator approves it; the note renders it at"
                " the next emit.\n"
                "A lesson does not bind until the operator approves it. The note renders it"
                " later.\n", encoding="utf-8")
            code, out = self._lint()
            self.assertIsNone(code, out)
        finally:
            self._restore(rel)

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
