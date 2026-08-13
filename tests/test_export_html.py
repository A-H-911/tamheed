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

    # -------------------------------------------- plan 027: flow view + graph rework

    def test_flow_section_lanes_and_arrowheads(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn('<section id="flow"', out)
        for lane in ("Needs (", "Decisions (", "Work (", "Verification ("):
            self.assertIn(f'class="lane">{lane}', out)
        self.assertIn('<marker id="arrowf"', out)        # flow arrowheads
        self.assertIn('<marker id="arrow"', out)         # graph arrowheads
        self.assertIn('marker-end="url(#arrowf)"', out)
        self.assertIn('marker-end="url(#arrow)"', out)
        # flow nodes are labeled: id text beside the circle
        self.assertIn('r="4" class="g0"/><text', out)

    def test_graph_connected_only_isolated_folded(self):
        """Plan 027: 74% dead dots on the golden — isolated entities leave the svg
        and land in their own fold, every one accounted for. Plan 028: the fold
        summary breaks the count down per family."""
        self._open_demo_copy()
        out = self._export()
        import re as _re
        m = _re.search(r"Relations graph \((\d+) connected, (\d+) isolated,", out)
        self.assertIsNotNone(m)
        n_connected, n_isolated = int(m.group(1)), int(m.group(2))
        self.assertGreater(n_isolated, 0)                # the demo has isolated nodes
        fold = _re.search(
            r"Isolated entities \(no trace edges\) — ([^<]+) \((\d+) rows\)", out)
        self.assertIsNotNone(fold)
        self.assertEqual(int(fold.group(2)), n_isolated)
        self.assertIn("document-section", fold.group(1))  # per-family breakdown
        # an isolated document-section is in the fold, not the svg
        conn = srv._CURRENT.conn
        linked = {r[0] for r in conn.execute("SELECT from_id FROM trace_edges")} | \
                 {r[0] for r in conn.execute("SELECT to_id FROM trace_edges")}
        (sec_id,) = next(iter(conn.execute(
            "SELECT id FROM document_sections WHERE id NOT IN"
            " (SELECT from_id FROM trace_edges)"
            " AND id NOT IN (SELECT to_id FROM trace_edges) LIMIT 1")))
        self.assertNotIn(sec_id, linked)
        self.assertNotIn(f'<a href="#{sec_id}"><circle', out)

    def test_hover_isolate_incident_copies(self):
        """Plan 028 (C34 §5.1): each node group carries hidden .hl copies of its
        incident edges; :has() dims the base layer on hover — both svgs, zero JS."""
        self._open_demo_copy()
        out = self._export()
        self.assertIn('.graph:has(.nod:hover) .edges path', out)   # the CSS mechanism
        self.assertIn('class="nod"', out)
        n_hl = out.count('class="hl e-')
        conn = srv._CURRENT.conn
        (n_edges,) = conn.execute("SELECT COUNT(*) FROM trace_edges").fetchone()
        # each edge yields exactly 2 incident copies per svg (flow + graph = 4×),
        # minus self-loops (none in the demo) — a sane, deterministic bound
        self.assertEqual(n_hl, 4 * n_edges)
        self.assertLessEqual(out.count('marker-end="url(#arrow)"'),
                             3 * n_edges + n_hl)          # base + copies, no leak

    def test_hover_isolate_hostile_id_inert(self):
        srv.package_create("hostg", "H", "rnd")
        srv.entity_upsert([
            {"type": "risk", "id": 'RISK-1"><script>', "title": "x"},
            {"type": "risk", "id": "RISK-2", "title": "y"},
            {"type": "trace-edge", "from_id": 'RISK-1"><script>', "to_id": "RISK-2",
             "relation": "relates_to"}])
        out = self._export()
        self.assertNotIn("<script", out)                  # esc() holds in .hl copies
        self.assertIn('class="nod"', out)

    def test_flow_lead_flags_isolated_requirements(self):
        """Plan 028 (C34 §5.2): the requirements the flow view cannot draw are the
        unverified ones — the lead says so instead of reading rosier than reality."""
        srv.package_create("isoreq", "I", "rnd")
        srv.entity_upsert([
            {"type": "requirement", "id": "FR-001", "kind": "functional",
             "title": "wired", "mvp": 0, "lifecycle_status": "Approved",
             "source_kind": "brief", "source_span": "x"},
            {"type": "requirement", "id": "FR-002", "kind": "functional",
             "title": "unwired", "mvp": 0, "lifecycle_status": "Approved",
             "source_kind": "brief", "source_span": "x"},
            {"type": "test", "id": "TEST-001", "title": "t"},
            {"type": "trace-edge", "from_id": "TEST-001", "to_id": "FR-001",
             "relation": "tests"}])
        out = self._export()
        self.assertIn("⚠ 1 requirement(s) have no trace edges and are not drawn", out)
        m = __import__("re").search(
            r"Isolated entities \(no trace edges\) — ⚠ 1 requirement\(s\) — ", out)
        self.assertIsNotNone(m)                           # fold prefix + sorts first
        self.assertRegex(out, r'<tr id="FR-002"><td>FR-002</td>')

    def test_relation_filter_radios_and_classes(self):
        self._open_demo_copy()
        out = self._export()
        conn = srv._CURRENT.conn
        rels = {r[0] for r in conn.execute("SELECT DISTINCT relation FROM trace_edges")}
        for prefix in ("fr", "gr"):
            self.assertIn(f'id="{prefix}-all" class="gz" checked', out)
            for rel in rels:
                self.assertIn(f'id="{prefix}-{rel}"', out)
        for rel in rels:
            self.assertIn(f'class="e-{rel}"', out)
        self.assertIn("#fr-tests:checked ~ .graphwrap path:not(.e-tests)", out)

    def test_degree_scaled_radius(self):
        srv.package_create("deg", "Deg", "rnd")
        srv.entity_upsert([{"type": "risk", "id": f"RISK-{i:03d}", "title": "r"}
                           for i in range(1, 8)])
        srv.entity_upsert([{"type": "trace-edge", "from_id": "RISK-001",
                            "to_id": f"RISK-{i:03d}", "relation": "relates_to"}
                           for i in range(2, 7)])        # RISK-001: 5 edges
        out = self._export()
        import re as _re
        radius = {m.group(1): float(m.group(2)) for m in _re.finditer(
            r'href="#(RISK-\d+)"><circle cx="[^"]+" cy="[^"]+" r="([\d.]+)"', out)}
        self.assertGreater(radius["RISK-001"], radius["RISK-002"])
        self.assertGreaterEqual(radius["RISK-002"], 3.0)

    def test_flow_hostile_id_inert(self):
        srv.package_create("hostf", "H", "rnd")
        srv.entity_upsert([
            {"type": "risk", "id": 'RISK-1"><script>', "title": "x"},
            {"type": "risk", "id": "RISK-2", "title": "y"},
            {"type": "trace-edge", "from_id": 'RISK-1"><script>', "to_id": "RISK-2",
             "relation": "relates_to"}])
        out = self._export()
        self.assertNotIn("<script", out)                 # esc() holds in the flow too
        self.assertIn("RISK-1&quot;&gt;&lt;script&gt;", out)
        self.assertIn('<section id="flow"', out)

    # -------------------------------------------- plan 027: readiness panel

    def test_execution_readiness_panel(self):
        """Per-phase readiness (latest-verdict semantics) + declared human gates
        render in the execution section."""
        self._open_demo_copy()
        srv.entity_upsert([{"type": "execution-gate", "id": "GATE-901",
                            "gate_kind": "approval",
                            "definition": "Operator signs off the release"}])
        out = self._export()
        self.assertIn("Phase readiness", out)
        self.assertIn("latest-verdict semantics", out)
        self.assertIn("Declared human gates", out)
        self.assertIn("Operator signs off the release", out)

    # -------------------------------------------- plan 018 phase 2 (C18): navigation & scale

    def test_toc_links_all_sections(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn('<nav class="toc">', out)
        for anchor, _title, _fn in viewer.SECTIONS:
            self.assertIn(f'href="#{anchor}"', out)
        self.assertIn("position: sticky", out)          # CSS is embedded in the page

    def test_long_text_wraps_in_place(self):
        """Plan 020 (C25 req 2, supersedes the 019 scroll fix): wrap, don't scroll."""
        self._open_demo_copy()
        out = self._export()
        self.assertIn("overflow-wrap: anywhere", out)
        self.assertNotIn("max-content", out)

    def test_section_order_state_relations_data(self):
        """Plan 027: the full SECTIONS order, no hardcoded subset (this test missed
        the graph section for two releases)."""
        self._open_demo_copy()
        out = self._export()
        anchors = [a for a, _title, _fn in viewer.SECTIONS]
        self.assertEqual(anchors[:3], ["overview", "flow", "graph"])
        order = [out.index(f'<section id="{a}"') for a in anchors]
        self.assertEqual(order, sorted(order))          # C25 req 1: maintainer order

    def test_csv_links_and_files(self):
        """Plan 020 (C25 req 3): every register fold links its sibling CSV file."""
        self._open_demo_copy()
        result = srv.export_html()
        out = Path(result["path"]).read_text(encoding="utf-8")
        self.assertIn('<a class="csv" href="csv/requirements.csv" download>CSV</a>', out)
        csv_dir = Path(result["path"]).parent / "csv"
        req_csv = (csv_dir / "requirements.csv").read_text(encoding="utf-8")
        self.assertTrue(req_csv.startswith("id,"))       # header row
        self.assertIn("FR-001", req_csv)
        # every csv/ href in the page has a matching emitted file
        import re as _re
        for name in set(_re.findall(r'href="csv/([^"]+)"', out)):
            self.assertTrue((csv_dir / name).exists(), name)
        # deterministic + managed: re-export reports the csvs unchanged
        again = srv.export_html()
        self.assertEqual(again["csv"]["diverged"], [])
        self.assertIn("csv/requirements.csv", again["csv"]["unchanged"])

    def test_csv_hand_edit_overwritten_as_derived(self):
        """Plan 022 (C27/D2): CSVs are derived outputs — a hand edit is overwritten
        (reported emitted), never stuck diverged with no in-tool recovery."""
        self._open_demo_copy()
        result = srv.export_html()
        req = Path(result["path"]).parent / "csv" / "requirements.csv"
        req.write_text("tampered\n", encoding="utf-8")
        again = srv.export_html()
        self.assertIn("csv/requirements.csv", again["csv"]["emitted"])
        self.assertEqual(again["csv"]["diverged"], [])
        self.assertTrue(req.read_text(encoding="utf-8").startswith("id,"))

    def test_all_edges_table_always_collapsed(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn("<summary>All trace edges (", out)
        self.assertIn("<summary>Acceptance criteria", out)           # demo has ACs
        self.assertIn('<details id="reg-adrs"><summary>Adrs (', out)  # anchored folds

    def test_every_table_folds_closed_uniformly(self):
        """Plan 019 (C21, maintainer decision): ALL tables fold closed — no size
        threshold, one consistent affordance."""
        srv.package_create("big", "Big", "rnd")
        srv.entity_upsert([{"type": "risk", "id": f"RISK-{i:03d}", "title": f"risk {i}"}
                           for i in range(1, 61)])
        srv.entity_upsert([{"type": "requirement", "id": "FR-001", "kind": "functional",
                            "title": "t", "lifecycle_status": "Approved",
                            "source_kind": "brief", "source_span": "x"}])
        out_a = self._export(str(Path(self._tmp.name) / "a.html"))
        self.assertIn("<summary>Risks (60 rows)", out_a)
        self.assertIn("<summary>Requirements (1 row)", out_a)
        self.assertIn("<details><summary>Package identity (", out_a)
        self.assertIn("<details><summary>Requirement coverage matrix (", out_a)
        self.assertNotIn("<details open", out_a)               # everything closed
        # every table lives inside a details fold (anchored or not); the graph fold
        # wraps a graphwrap instead of a tablewrap
        self.assertEqual(out_a.count("<details"),
                         out_a.count('<div class="tablewrap">')
                         + out_a.count('<div class="graphwrap">'))
        # determinism at scale: byte-identical re-export
        self.assertEqual(out_a, self._export(str(Path(self._tmp.name) / "b.html")))

    def test_gap_warning_cards_never_fold(self):
        """The sole folding exception: screening warnings exist to be SEEN."""
        srv.package_create("gappy", "Gappy", "rnd")
        srv.entity_upsert([{"type": "open-question", "id": "OQ-001",
                            "title": "Injection-shaped text found at src/evil.py",
                            "question": "review the fenced span",
                            "source_span": "src/evil.py:1",
                            "custom_attributes": '{"fenced": "`ignore instructions`"}'}])
        out = self._export()
        gaps = out.split('<section id="gaps">', 1)[1].split("</section>", 1)[0]
        self.assertIn('<div class="warn">', gaps)
        self.assertNotIn("<details", gaps)

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

    # -------------------------------------------- plan 020 phase 3 (C25): relations graph

    def test_graph_section_renders_with_toc(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn('<section id="graph">', out)
        self.assertIn("Relations graph (", out)
        self.assertIn('<div class="graphwrap">', out)
        self.assertIn("<svg", out)
        self.assertIn('href="#graph"', out)              # TOC entry

    def test_graph_zoom_fit_default_and_controls(self):
        """Plan 021 (C26, maintainer): default zoom shows ALL nodes; CSS-only controls."""
        self._open_demo_copy()
        out = self._export()
        self.assertIn('id="gz-fit" class="gz" checked', out)     # Fit is the default
        for z in ("gz-2", "gz-4", "gz-8"):
            self.assertIn(f'id="{z}"', out)
        self.assertIn("#gz-fit:checked ~ .graphwrap svg { width: 100%", out)
        # the svg carries NO fixed pixel width — the viewBox scales to the container
        graph = out.split('<section id="graph">')[1].split("</section>")[0]
        svg_tag = graph.split("<svg", 1)[1].split(">", 1)[0]
        self.assertNotIn("width=", svg_tag)
        self.assertIn("viewBox=", svg_tag)

    def test_graph_nodes_link_to_register_rows(self):
        self._open_demo_copy()
        out = self._export()
        self.assertIn('<a href="#FR-001"><circle', out)  # node = fragment link
        self.assertIn('<tr id="FR-001">', out)           # target = anchored row

    def test_every_graph_href_resolves(self):
        import re as _re
        self._open_demo_copy()
        out = self._export()
        graph = out.split('<section id="graph">')[1].split("</section>")[0]
        targets = set(_re.findall(r'<tr id="([^"]*)"', out))
        targets |= {a for a, _t, _f in viewer.SECTIONS}
        targets |= set(_re.findall(r'<details id="([^"]*)"', out))
        refs = _re.findall(r'href="#([^"]*)"', graph)
        self.assertTrue(refs)                            # the graph actually links
        for ref in refs:
            self.assertIn(ref, targets, f"dead graph link #{ref}")

    def test_graph_deterministic_at_scale(self):
        srv.package_create("big", "Big", "rnd")
        srv.entity_upsert([{"type": "risk", "id": f"RISK-{i:03d}", "title": f"r{i}"}
                           for i in range(1, 201)])
        srv.entity_upsert([{"type": "test", "id": f"TEST-{i:03d}", "title": f"t{i}"}
                           for i in range(1, 101)])
        srv.entity_upsert([{"type": "trace-edge", "from_id": f"TEST-{i:03d}",
                            "to_id": f"RISK-{(i * 7) % 200 + 1:03d}",
                            "relation": "relates_to"} for i in range(1, 101)])
        a = self._export(str(Path(self._tmp.name) / "a.html"))
        b = self._export(str(Path(self._tmp.name) / "b.html"))
        self.assertEqual(a, b)                           # byte-deterministic at scale
        # plan 027: 100 tests + 100 distinct risk targets connected; 100 risks isolated
        self.assertIn("Relations graph (200 connected, 100 isolated, 100 edges)", a)

    def test_graph_aggregates_above_limit(self):
        old = viewer._G_AGG_LIMIT
        viewer._G_AGG_LIMIT = 5
        try:
            srv.package_create("agg", "Agg", "rnd")
            srv.entity_upsert([{"type": "risk", "id": f"RISK-{i:03d}", "title": "r"}
                               for i in range(1, 11)])
            srv.entity_upsert([{"type": "trace-edge", "from_id": f"RISK-{i:03d}",
                                "to_id": f"RISK-{i + 1:03d}",
                                "relation": "relates_to"} for i in range(1, 10)])
            out = self._export()
        finally:
            viewer._G_AGG_LIMIT = old
        self.assertIn('href="#reg-risks"', out)          # family node -> register fold
        self.assertNotIn('<a href="#RISK-001"><circle', out)

    def test_hostile_id_stays_inert_in_graph(self):
        srv.package_create("host", "H", "rnd")
        srv.entity_upsert([
            {"type": "risk", "id": 'RISK-1"><script>', "title": "x"},
            {"type": "risk", "id": "RISK-2", "title": "y"},
            {"type": "trace-edge", "from_id": 'RISK-1"><script>', "to_id": "RISK-2",
             "relation": "relates_to"}])
        out = self._export()
        self.assertNotIn("<script", out)                 # esc() chokepoint holds
        self.assertIn("RISK-1&quot;&gt;&lt;script&gt;", out)

    # ------------------------------------------------------------ (a) sections

    def test_demo_package_renders_all_sections(self):
        self._open_demo_copy()
        out = self._export()
        for anchor, _title, _fn in viewer.SECTIONS:   # plan 027: never a stale subset
            self.assertIn(f'id="{anchor}"', out)
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
        # text). Allowed link classes only (C25 doctrine): same-document #fragments and
        # code-derived relative csv/<table>.csv downloads — nothing can carry a scheme.
        self.assertNotIn("<script", out)
        self.assertEqual(out.count('href="'),
                         out.count('href="#') + out.count('href="csv/'))
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
