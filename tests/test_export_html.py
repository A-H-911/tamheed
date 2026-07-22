"""Viewer tests for the Tamheed HTML review surface (plan 012/B6).

The plan's three groups: (a) the migrated demo package (plan 010's golden) renders
all five sections; (b) hostile content — a <script> body, an onerror= attribute
payload, and a javascript: link — never appears unescaped in the raw HTML; (c)
determinism — two exports of the same DB state are byte-identical.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))

import export_html as viewer  # noqa: E402
import tamheed_server as srv  # noqa: E402

DEMO_DATA = REPO_ROOT / "generated-samples" / "support-triage-agent-v2" / "data"

XSS_SCRIPT = "<script>alert(1)</script>"
XSS_ATTR = '"><img src=x onerror=alert(1)>'
XSS_LINK = "javascript:alert(document.cookie)"


class ExportHtmlTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    def _open_demo_copy(self, name: str = "demo") -> None:
        shutil.copytree(DEMO_DATA, srv.PACKAGE_ROOT / name / "data")
        self.assertTrue(srv.package_open(name)["ok"])

    def _export(self, output: str | None = None) -> str:
        result = srv.export_html(output)
        self.assertTrue(result["ok"], result)
        return Path(result["path"]).read_text(encoding="utf-8")

    # -------------------------------------------- plan 018 phase 2 (C18): navigation & scale

    def test_toc_links_all_sections(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn('<nav class="toc">', out)
        for anchor, _title, _fn in viewer.SECTIONS:
            self.assertIn(f'href="#{anchor}"', out)
        self.assertIn("position: sticky", out)          # CSS is embedded in the page

    def test_wide_table_css_scrolls(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn("width: max-content", out)        # tables overflow the wrap...
        self.assertIn("min-width: 100%", out)           # ...instead of squeezing columns
        self.assertIn("overflow-x: auto", out)

    def test_all_edges_table_always_collapsed(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn("<details><summary>All trace edges (", out)

    def test_large_register_collapses_small_stays_flat(self):
        srv.package_create("big", "Big", "rnd")
        srv.entity_upsert([{"type": "risk", "id": f"RISK-{i:03d}", "title": f"risk {i}"}
                           for i in range(1, 61)])
        srv.entity_upsert([{"type": "requirement", "id": "FR-001", "kind": "functional",
                            "title": "t", "lifecycle_status": "Approved",
                            "source_kind": "brief", "source_span": "x"}])
        out_a = self._export("a.html")
        self.assertIn("<details><summary>Risks (60 rows)</summary>", out_a)
        self.assertIn("<h3>Requirements (1)</h3>", out_a)      # small family stays flat
        self.assertNotIn("<summary>Requirements", out_a)
        # determinism at scale: byte-identical re-export
        self.assertEqual(out_a, self._export("b.html"))

    def test_freshness_reports_no_v2_activity(self):
        self._open_demo_copy()                     # migrated golden: no v2 timestamps
        out = self._export()
        self.assertIn("package record dated", out)
        self.assertIn("no v2 activity recorded yet", out)
        srv.progress_update([{"entry": "first real v2 work"}])
        out2 = self._export()
        self.assertNotIn("no v2 activity recorded yet", out2)
        self.assertIn("latest recorded activity:", out2)

    def test_migrated_package_metadata_labeled(self):
        self._open_demo_copy()
        self.assertIn("(v1-manifest-derived)", self._export())
        srv.package_close()
        srv.package_create("fresh", "Fresh", "rnd")
        self.assertNotIn("(v1-manifest-derived)", self._export())

    # ------------------------------------------------------------ (a) sections

    def test_demo_package_renders_five_sections(self):
        self._open_demo_copy()
        out = self._export()
        for anchor in ('id="overview"', 'id="registers"', 'id="traceability"',
                       'id="execution"', 'id="gaps"'):
            self.assertIn(anchor, out)
        self.assertIn("FR-001", out)                       # registers carry demo content
        self.assertIn("Gate verdict:", out)                # per-gate chips summary
        self.assertIn("Design-ahead lead", out)            # C9 roadmap render
        self.assertIn("last_referenced", out)              # C3 per-entity column
        self.assertGreaterEqual(out.count('class="freshness"'), 5)  # C1 per-view stamp

    def test_default_export_lands_in_package_dir(self):
        self._open_demo_copy()
        result = srv.export_html()
        self.assertEqual(Path(result["path"]),
                         srv.PACKAGE_ROOT / "demo" / "review.html")

    def test_export_requires_open_package(self):
        result = srv.export_html()
        self.assertFalse(result["ok"])
        self.assertIn("no package open", result["error"])

    # ------------------------------------------------------ (b) hostile content

    def test_hostile_content_is_neutralized(self):
        self.assertTrue(srv.package_create("hostile", "Hostile", "rnd")["ok"])
        payload = f"{XSS_SCRIPT} {XSS_ATTR} {XSS_LINK}"
        self.assertTrue(srv.entity_upsert([
            {"type": "requirement", "id": "FR-001", "kind": "functional",
             "title": payload, "statement": payload, "mvp": 1,
             "lifecycle_status": "Approved", "source_kind": "brief",
             "source_span": payload},
            {"type": "risk", "id": "RISK-001", "title": "Risky",
             "description": XSS_SCRIPT},
        ])["ok"])
        out = self._export()
        # the raw payloads never appear...
        self.assertNotIn(XSS_SCRIPT, out)
        self.assertNotIn(XSS_ATTR, out)
        # ...only their escaped forms do
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", out)
        self.assertIn("&quot;&gt;&lt;img src=x onerror=alert(1)&gt;", out)
        # the viewer ships zero JS and zero DATA-derived links (javascript: is inert
        # text). The only anchors allowed are the TOC's code-derived fragment links —
        # a stronger pin than the old blanket <a> ban: exactly one per section, every
        # href a #fragment.
        self.assertNotIn("<script", out)
        self.assertEqual(out.count("<a "), len(viewer.SECTIONS))
        self.assertEqual(out.count('href="'), out.count('href="#'))
        self.assertNotIn('href="javascript:', out)
        self.assertIn('http-equiv="Content-Security-Policy"', out)
        self.assertIn("default-src 'none'", out)

    # -------------------------------------------------------- (c) determinism

    def test_exports_are_byte_identical(self):
        self._open_demo_copy()
        first = srv.export_html(str(srv.PACKAGE_ROOT / "a.html"))
        self.assertTrue(srv.package_close()["ok"])         # round-trip through canonical text
        self.assertTrue(srv.package_open("demo")["ok"])
        second = srv.export_html(str(srv.PACKAGE_ROOT / "b.html"))
        self.assertTrue(first["ok"] and second["ok"])
        self.assertEqual(Path(first["path"]).read_bytes(),
                         Path(second["path"]).read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
