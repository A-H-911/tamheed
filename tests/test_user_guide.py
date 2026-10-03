"""The bilingual user guide (index.html) is generated from the engine and must stay a fresh build.

Byte-twin: a fresh render equals the committed page. Coverage: every id the page renders has
English and Arabic prose and nothing in content.py is unused. Runtime witness: the readiness
rules the build extracts from the server source are the rules a live readiness_check emits.
Structure: the counts the page states are the engine's. Tokens: every gate, tool and skill named
on the page exists. Hygiene: no inline handlers, no CR, one external host.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDE = REPO_ROOT / "docs" / "guide"
sys.path.insert(0, str(GUIDE))

_spec = importlib.util.spec_from_file_location("tamheed_guide_build", GUIDE / "build.py")
assert _spec and _spec.loader
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)  # type: ignore[union-attr]
extract, content, render = build.extract, build.content, build.render
srv = extract.srv


class UserGuideTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html, cls.required = build.build()
        cls.facts = extract.facts()

    def test_index_html_is_the_fresh_build(self):
        current = (REPO_ROOT / "index.html").read_bytes()
        fresh = self.html.encode("utf-8")
        if current != fresh:
            a, b = current.split(b"\n"), fresh.split(b"\n")
            line = next((i for i, (x, y) in enumerate(zip(a, b), 1) if x != y), min(len(a), len(b)) + 1)
            self.fail(f"index.html is stale (first difference at line {line}); run "
                      f"`python docs/guide/build.py` (a CRLF checkout needs `git add --renormalize index.html`)")

    def test_every_rendered_id_has_en_and_ar(self):
        missing = build.missing(self.required)
        self.assertEqual(missing, [], f"{len(missing)} strings missing, e.g. {missing[:5]}")
        self.assertEqual(build.orphans(self.required), [], "content ids the page never renders")

    def test_version_matches_plugin_json(self):
        ver = json.loads((REPO_ROOT / "plugins/tamheed/.claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertIn(f'<span class="ver">v{ver}</span>', self.html)
        self.assertIn(f'<meta name="generator" content="tamheed-guide {ver}">', self.html)

    def test_rule_extraction_matches_the_engine(self):
        static = self.facts["rules"]
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        srv.PACKAGE_ROOT = Path(tmp.name)
        self.assertTrue(srv.package_create("guide", "Guide witness", "rnd")["ok"])
        self.addCleanup(srv.package_close)
        live = [r["rule"] for r in srv.readiness_check("package")["rules"]]
        self.assertEqual(live, [r["rule"] for r in static["package"] if not r["conditional"]])
        self.assertEqual(sorted(r["rule"] for r in static["package"] if r["conditional"]),
                         ["feedback-unanswered", "handoff-repeated", "lessons-stranded", "waivers-open-ended"])
        up = srv.entity_upsert([
            {"type": "phase", "id": "PH-1", "title": "P", "lifecycle_status": "Approved"},
            {"type": "slice", "id": "SL-001", "title": "S", "phase_id": "PH-1", "lifecycle_status": "Approved"}])
        self.assertTrue(up["ok"], up)
        self.assertEqual([r["rule"] for r in srv.readiness_check("phase", "PH-1")["rules"]],
                         [r["rule"] for r in static["phase"]])
        self.assertEqual([r["rule"] for r in srv.readiness_check("slice", "SL-001")["rules"]],
                         [r["rule"] for r in static["slice"]])
        self.assertFalse(srv.entity_query(type="package")["ok"])

    def test_structural_counts(self):
        f = self.facts
        self.assertEqual(len(f["schema"]["tables"]), 41)
        self.assertEqual(len(f["families"]), len(srv.BASELINE_ENTITY_TYPES))
        self.assertEqual(sum(1 for x in f["families"] if x["cls"] == "Always"), 10)
        rel = next(t for t in f["schema"]["tables"] if t["table"] == "trace_edges")
        check = next(c["check_in"] for c in rel["columns"] if c["name"] == "relation")
        self.assertEqual(sorted(check), sorted(set(srv.RELATION_RULES) | {"relates_to"}))
        self.assertEqual(len(f["events"]["all"]), 12)
        self.assertEqual(len(f["tools"]), 19)
        self.assertEqual({s["group"] for s in f["skills"]}, {"front", "scenario", "discipline"})
        self.assertEqual(len(f["skills"]), 27)
        self.assertEqual(len(f["stages"]["stages"]), 22)
        self.assertEqual(f["stages"]["human"], [7, 8, 14, 18, 22])
        # plan 175: a multi-line table CHECK is carried whole; an `OR col GLOB` tail is a value form
        req = next(t for t in f["schema"]["tables"] if t["table"] == "requirements")
        self.assertTrue(any("NFR-" in c for c in req["table_checks"]), req["table_checks"])
        pkg = next(t for t in f["schema"]["tables"] if t["table"] == "packages")
        mode = next(c for c in pkg["columns"] if c["name"] == "mode")
        self.assertEqual(mode["check_glob"], ["stage:*"])

    def test_vocabulary_table_comes_from_the_file(self):
        """Plan 188 (R22): the Writing discipline section renders references/vocabulary.md's
        three tables, every English cell the file's own text, every row with an Arabic twin."""
        v = self.facts["vocabulary"]
        self.assertEqual(len(v["actions"]), 25)
        self.assertEqual(len(v["terms"]), 22)
        self.assertEqual(len(v["names"]), 7)
        section = self.html[self.html.index('<section class="sec" id="writing">'):]
        section = section[:section.index("</section>")]
        for cid, en in extract.vocabulary_cells(v):
            self.assertIn(cid, self.required, cid)
            self.assertEqual(content.TEXT[cid]["en"], en, cid)
            self.assertIn(render.md(en), section, cid)
            self.assertTrue(content.TEXT[cid]["ar"].strip(), cid)
        for a in v["actions"]:
            self.assertIn(f"<code>{a['verb']}</code>", section, a["verb"])
        self.assertIn("<code>check</code>", section)

    def test_diagrams_draw_cleanly(self):
        """Plan 175 (operator ruling): every edge meets its box on the border, crosses no box and
        no other edge, and no label lies on a line or a box — on both language copies."""
        import build
        self.assertEqual(build.diagram_problems(self.facts), [])
        # the relation matrix covers every typed relation and nothing the engine lacks
        import diagrams
        cells = diagrams.relation_matrix(self.facts)
        shown = {rel for rels in cells.values() for rel in rels}
        self.assertEqual(shown, set(srv.RELATION_RULES))

    def test_markup_renders(self):
        """Plan 175: the markdown subset renders bold (also around a code span) and italics."""
        import render
        self.assertEqual(render.md("**`force: true`** carries"), "<strong><code>force: true</code></strong> carries")
        self.assertEqual(render.md("counted *narrated* by `gate_run`"), "counted <em>narrated</em> by <code>gate_run</code>")
        self.assertEqual(render.md("`data/*.jsonl` and `csv/*.csv`"), "<code>data/*.jsonl</code> and <code>csv/*.csv</code>")
        body = self.html.split("<main>", 1)[1]
        self.assertNotRegex(body, r"\*\*", "literal ** reached the page")
        self.assertNotRegex(re.sub(r"<code>.*?</code>", "", body), r"(?<![\w*])\*[a-z][a-z -]*\*(?![\w*])", "literal *italic* reached the page")

    def test_tokens_resolve(self):
        gates = set(self.facts["gates"]["mechanical"]) | set(self.facts["gates"]["judgment"]) | set(self.facts["gates"]["warn"])
        for tok in set(re.findall(r"\bG-[A-Z][A-Z-]+\b", self.html)):
            self.assertIn(tok.rstrip("-"), gates, tok)
        skills = {s["name"] for s in self.facts["skills"]}
        for tok in set(re.findall(r"(?<!-- )/tamheed:([a-z-]+)", self.html)):
            self.assertIn(tok, skills, tok)
        tools = set(srv.TOOLS)
        heads = {t.split("_")[0] for t in tools}
        tails = {t.split("_", 1)[1] for t in tools}
        for tok in set(re.findall(r"<code>([a-z]+_[a-z]+)</code>", self.html)):
            head, tail = tok.split("_", 1)
            if head in heads and tail in tails:
                self.assertIn(tok, tools, tok)
        for name in tools:
            self.assertIn(f"<code>{name}</code>", self.html, name)

    def test_page_hygiene(self):
        self.assertNotRegex(self.html, r"\son[a-z]+=")
        self.assertEqual(self.html.count("<script"), 2)
        hosts = set(re.findall(r'href="https?://([^/"]+)', self.html))
        self.assertTrue(hosts <= {"fonts.googleapis.com", "fonts.gstatic.com", "github.com"}, hosts)
        self.assertNotIn("\r", self.html)
        self.assertEqual(self.html.count('<svg class="dia" lang="en"'), self.html.count('<svg class="dia" lang="ar"'))
        self.assertNotIn("[[", self.html, "unresolved content placeholder")
        # the language toggle must never be hidden by the per-language visibility rule
        for btn in re.findall(r"<button[^>]*data-lang-btn[^>]*>", self.html):
            self.assertNotIn(" lang=", btn, btn)
        # a primary key is caller-minted: it never wears the `optional` badge (plan 175, L34)
        self.assertNotRegex(self.html, r'badge pk">PK</span>\s*<span class="badge opt"')
        src = (GUIDE / "extract.py").read_text(encoding="utf-8") + (GUIDE / "render.py").read_text(encoding="utf-8")
        for m in re.finditer(r"\.(glob|iterdir|listdir)\(", src):
            line = src[src.rfind("\n", 0, m.start()) + 1: m.start()]
            self.assertIn("sorted(", line, f"unsorted enumeration: {line.strip()}")
        fixture = REPO_ROOT / "evals/sample-results/lab-tracker/package"
        for name in ("data", "csv", "exports", "prompts", "review.html"):
            self.assertTrue((fixture / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
