"""Plan 180 (the plain-English batch): the suite for `plugins/tamheed/server/ste_lint.py`.

The module is a port of danyuchn/asd-ste100-skill's `scripts/ste-lint.py` (MIT) with the
changes Tamheed needs: paragraphs are joined before sentences are split (Tamheed hard-wraps
Markdown near 100 columns), the vocabulary comes from `references/vocabulary.md`, Python runtime
string literals are read through `ast`, Arabic takes the semicolon and length rules, and an
allow marker needs a reason. These tests are the module's selftest.
"""
from __future__ import annotations

import io
import contextlib
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER = REPO_ROOT / "plugins" / "tamheed" / "server"
sys.path.insert(0, str(SERVER))

import ste_lint as sl  # noqa: E402

VOCAB_PATH = REPO_ROOT / "plugins" / "tamheed" / "references" / "vocabulary.md"


def rules(findings):
    return [f["rule"] for f in findings]


class VocabularyFileTest(unittest.TestCase):
    def test_the_bundle_vocabulary_parses_into_the_three_tables(self):
        v = sl.load_vocabulary(VOCAB_PATH)
        self.assertEqual(v["rejected"]["validate"], "check")
        self.assertEqual(v["rejected"]["delete"], "retire")  # the first row that rejects it
        self.assertIn("record", v["terms"])
        self.assertIn("Quality validation", v["names"])
        self.assertEqual(v["approved"]["run a mechanical gate, rule or script"], "check")
        for approved in v["approved"].values():
            self.assertNotIn(approved, v["rejected"], approved)

    def test_a_missing_header_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.md"
            p.write_text("# V\n\n| action | verb |\n|---|---|\n| a | b |\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                sl.load_vocabulary(p)


class MarkdownExtractionTest(unittest.TestCase):
    def test_paragraph_join_finds_the_wrapped_sentence(self):
        words = " ".join(f"word{i}" for i in range(30)) + "."
        wrapped = textwrap.fill(words, 60)
        self.assertGreaterEqual(wrapped.count("\n"), 2)
        joined = sl.lint_text(wrapped, mode="strict")
        self.assertEqual(rules(joined), ["long-sentence"])
        self.assertEqual(joined[0]["line"], 1)
        # a per-line split, which upstream does, sees three short fragments and nothing wrong
        per_line = [{"line": i + 1, "kind": "paragraph", "text": ln, "allow": set()}
                    for i, ln in enumerate(wrapped.splitlines())]
        self.assertEqual(sl.lint_blocks(per_line, mode="strict"), [])

    def test_frontmatter_description_is_linted_and_other_keys_are_not(self):
        text = ("---\nname: a;b\ndescription: >-\n  Use before writing; a reader cannot ask.\n"
                "argument-hint: \"[x; y]\"\n---\n\n# Title\n\nClean text here.\n")
        found = sl.lint_text(text, mode="strict")
        self.assertEqual(rules(found), ["semicolon"])
        self.assertEqual(found[0]["line"], 3)
        self.assertEqual(sl.extract_markdown_prose(text)[0]["kind"], "description")

    def test_fenced_code_blockquote_and_code_spans_are_exempt(self):
        text = ("Clean line.\n\n```\nx = a; y = b\n```\n\n> quoted; old text\n\n"
                "The flag `--a; --b` is one token.\n\n~~~text\n- code and\n~~~\n")
        self.assertEqual(sl.lint_text(text, mode="strict"), [])

    def test_html_comment_is_dropped_and_a_placeholder_stays_prose(self):
        text = "<!-- a; comment -->\n\nWrite the file under <package>/prompts/; then stop.\n"
        found = sl.lint_text(text, mode="strict")
        self.assertEqual(rules(found), ["semicolon"])
        self.assertEqual(found[0]["line"], 3)

    def test_heading_and_table_header_are_exempt_from_length_not_semicolon(self):
        long_words = " ".join(f"w{i}" for i in range(28))
        text = (f"# {long_words}\n\n| {long_words} | Detail |\n|---|---|\n"
                f"| short | {long_words}. |\n\n## a; b\n")
        found = sl.lint_text(text, mode="strict")
        self.assertEqual(sorted(rules(found)), ["long-sentence", "semicolon"])
        long = [f for f in found if f["rule"] == "long-sentence"][0]
        self.assertEqual(long["line"], 5)  # the body cell, not the heading or the header row

    def test_html_table_cells_are_linted(self):
        text = "<table>\n<tr><th>Head</th><td>a; b c</td></tr>\n</table>\n"
        self.assertEqual(rules(sl.lint_text(text, mode="strict")), ["semicolon"])

    def test_abbreviations_do_not_end_a_sentence(self):
        self.assertEqual(len(sl.split_sentences("Use a tool, e.g. the reader, for rows.")), 1)
        self.assertEqual(len(sl.split_sentences("Read v5.8.1 first. Then stop.")), 2)
        self.assertEqual(len(sl.split_sentences("Files in data/*.jsonl flush. Commit them.")), 2)

    def test_name_heavy_sentence_is_exempt_from_length_not_semicolon(self):
        triggers = ", ".join(f'"trigger phrase number {i}"' for i in range(12))
        text = f"Trigger on {triggers} and on nothing else.\n"
        self.assertEqual(sl.lint_text(text, mode="strict"), [])
        self.assertEqual(rules(sl.lint_text(text.replace(" and on", "; and on"), mode="strict")),
                         ["semicolon"])
        codes = " ".join(f"`PFX{i}-`" for i in range(30))
        self.assertEqual(sl.lint_text(f"The identifier scheme: {codes}.\n", mode="strict"), [])

    def test_list_items_join_their_continuation_lines(self):
        words = " ".join(f"w{i}" for i in range(27))
        text = f"- {words[:80]}\n  {words[80:]}.\n- Short item.\n"
        found = sl.lint_text(text, mode="strict")
        self.assertEqual(rules(found), ["long-sentence"])
        self.assertEqual(found[0]["line"], 1)

    def test_dangling_conjunction_in_a_list_item(self):
        found = sl.lint_text("- Set the target and\n- Record the result or\n- Close it.\n")
        self.assertEqual(rules(found), ["dangling-conjunction", "dangling-conjunction"])
        self.assertEqual([f["line"] for f in found], [1, 2])
        self.assertEqual(sl.lint_text("- Use `and` as a label\n- Combine `left` and `right`\n"), [])


class RulesTest(unittest.TestCase):
    def test_hedges_are_never_flagged(self):
        text = "The request may have failed. It could be a timeout. The disk might have filled.\n"
        self.assertEqual(sl.lint_text(text, mode="strict", vocab=sl.load_vocabulary(VOCAB_PATH)), [])

    def test_upstream_rules_fire_on_the_upstream_bad_text(self):
        bad = ("The panel is removed; spin up the job. Perform an analysis of the seamless log. "
               "We have received the report.\n")
        found = rules(sl.lint_text(bad, mode="strict"))
        for expected in ("semicolon", "phrasal-verb", "nominalization", "marketing-adjective",
                         "passive-voice", "present-perfect"):
            self.assertIn(expected, found, expected)
        levels = {f["rule"]: f["level"] for f in sl.lint_text(bad, mode="strict")}
        self.assertEqual(levels["passive-voice"], "advisory")
        self.assertEqual(levels["present-perfect"], "advisory")
        self.assertEqual(levels["semicolon"], "hard")

    def test_tamheed_terms_do_not_flag_and_a_rejected_word_does(self):
        v = sl.load_vocabulary(VOCAB_PATH)
        clean = ("Verify before you claim. The operator-confirmed lessons bind. "
                 "Stage 19 is Quality validation. Check the gate.\n")
        self.assertEqual(sl.lint_text(clean, mode="strict", vocab=v), [])
        found = sl.lint_text("Validate the row before the write.\n", mode="strict", vocab=v)
        self.assertEqual(rules(found), ["vocabulary"])
        self.assertEqual(found[0]["level"], "hard")
        self.assertIn("check", found[0]["message"])
        flavored = sl.lint_text("Validate the row before the write.\n", mode="flavored", vocab=v)
        self.assertEqual(flavored[0]["level"], "advisory")

    def test_inflections_of_a_rejected_word_are_caught(self):
        v = sl.load_vocabulary(VOCAB_PATH)
        found = sl.lint_text("The tool modifies the row. Verifying it is your job.\n",
                             mode="strict", vocab=v)
        self.assertEqual([f["match"] for f in found], ["modifies"])
        self.assertEqual(rules(sl.lint_text("We fetched and deleted rows.\n", mode="strict",
                                            vocab=v)), ["vocabulary", "vocabulary"])

    def test_a_rejected_word_inside_a_code_span_or_a_name_is_legal(self):
        v = sl.load_vocabulary(VOCAB_PATH)
        text = "Run `validate_all()` after the scope_modifies edge lands. A fast-forward merge.\n"
        self.assertEqual(sl.lint_text(text, mode="strict", vocab=v), [])

    def test_arabic_takes_semicolon_and_length_only(self):
        found = sl.lint_text("النص الأول؛ النص الثاني.\n", mode="flavored", lang="ar")
        self.assertEqual(rules(found), ["semicolon"])
        long_ar = " ".join(["كلمة"] * 30) + ".\n"
        self.assertEqual(rules(sl.lint_text(long_ar, mode="flavored", lang="ar")), ["long-sentence"])
        self.assertEqual(sl.lint_text("The panel is removed; perform an analysis.\n", lang="ar"),
                         sl.lint_text("The panel is removed; perform an analysis.\n", lang="ar"))
        self.assertEqual(rules(sl.lint_text("The panel is removed. Perform an analysis.\n",
                                            mode="strict", lang="ar")), [])


class PythonLiteralsTest(unittest.TestCase):
    SOURCE = textwrap.dedent('''\
        """Module docstring; with a semicolon that is not runtime text."""
        import re

        def f(name):
            """Docstring; also exempt."""
            msg = f"package {name} is locked; retry later or ask the operator"
            short = "a; b c"
            sql = "SELECT a, b FROM t WHERE x = 1; -- trailing"
            html = '<td class="x">a; b c d e f g</td>'
            path = "no project-authored prompts in <package>/prompts/; write the kickoff prompt first"
            svg = "M 10 20 L 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190 200 210 220 230 240 250 260 270"
            rx = re.compile(r"\\b(is|are)\\s+(\\w+ed)\\b; the regex is code")
            # ste:allow semicolon: quoting the standard's own sentence
            quoted = "You can use all standard English punctuation marks; but not the semicolon"
            return msg, short, sql, html, path, svg, rx, quoted
    ''')

    def test_runtime_literals_are_linted_and_code_shapes_are_skipped(self):
        found = sl.lint_source(self.SOURCE, mode="strict", filename="x.py")
        semis = [f for f in found if f["rule"] == "semicolon"]
        self.assertEqual([f["line"] for f in semis], [6, 10])
        self.assertEqual([f["rule"] for f in found if f["rule"] == "long-sentence"], [])

    def test_an_allow_marker_without_a_reason_is_a_finding(self):
        src = 'x = 1\n# ste:allow semicolon\ny = "the panel; removed from the aircraft"\n'
        found = sl.lint_source(src, mode="strict", filename="x.py")
        self.assertIn("allow-without-reason", rules(found))
        self.assertIn("semicolon", rules(found))
        md = "<!-- ste:allow semicolon -->\nThe panel; removed.\n"
        self.assertIn("allow-without-reason", rules(sl.lint_text(md, mode="strict")))
        ok = "<!-- ste:allow semicolon: a quoted standard sentence -->\nThe panel; removed.\n"
        self.assertEqual(sl.lint_text(ok, mode="strict"), [])
        self.assertEqual(sl.lint_text(ok + "\nAnother; one.\n", mode="strict")[0]["line"], 4)


class CliTest(unittest.TestCase):
    def test_exit_codes_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.md"
            bad.write_text("A sentence; with a semicolon.\n", encoding="utf-8")
            good = Path(d) / "good.md"
            good.write_text("A clean sentence.\n", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code_bad = sl.main(["--mode", "strict", str(bad)])
                code_good = sl.main(["--mode", "strict", "--json", str(good)])
            self.assertEqual((code_bad, code_good), (1, 0))
            self.assertIn("semicolon", out.getvalue())
            self.assertIn('"hard": 0', out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
