"""Tests for the bundled runbook-§8 scratch-diff tool (plan 024/B20, C29).

The tool's contract: correct per-table keying (the two mis-keyings findings_8 §E1
hit — trace_edges and entity_types — are regression cases here), union-of-columns
comparison including JSON blobs, report-never-clobber duplicates, and exit codes
0/1/2 with exit 1 being the normal mid-life outcome.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "scripts"))

import scratch_diff  # noqa: E402


def write_pkg(root: Path, tables: dict[str, list[dict]]) -> str:
    root.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        (root / f"{name}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8")
    return str(root)


def run_tool(*argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = scratch_diff.main(list(argv))
    return code, buf.getvalue()


class ScratchDiffTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_identical_dirs_exit_zero(self):
        rows = {"requirements": [{"id": "FR-001", "title": "t",
                                  "custom_attributes": '{"v1": {"a": 1}}'}]}
        a = write_pkg(self.base / "a", rows)
        b = write_pkg(self.base / "b", rows)
        code, out = run_tool(a, b)
        self.assertEqual(code, 0)
        self.assertIn("no differences", out)

    def test_json_blob_only_diff_detected(self):
        """The findings_7 §C class: identical visible columns, stale blob."""
        live = {"requirements": [{"id": "FR-100", "title": "t", "priority": "S",
                                  "custom_attributes": '{"v1": {"Priority": "Deprecated)"}}'}]}
        scratch = {"requirements": [{"id": "FR-100", "title": "t", "priority": "S",
                                     "custom_attributes": '{"v1": {"Priority": "S"}}'}]}
        a = write_pkg(self.base / "a", live)
        b = write_pkg(self.base / "b", scratch)
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        [diff] = report["tables"]["requirements"]["changed"]["FR-100"]
        self.assertEqual(diff["field"], "custom_attributes")
        self.assertEqual(report["problems"], [])

    def test_trace_edges_composite_key_no_dup_noise(self):
        """findings_8 §E1: edges sharing from_id are distinct rows, never DUP-KEY."""
        rows = {"trace_edges": [
            {"from_id": "AC-001", "to_id": "FR-002", "relation": "verifies"},
            {"from_id": "AC-001", "to_id": "FR-005", "relation": "verifies"}]}
        extra = {"trace_edges": rows["trace_edges"] + [
            {"from_id": "SL-001", "to_id": "FR-002", "relation": "implements"}]}
        a = write_pkg(self.base / "a", rows)
        b = write_pkg(self.base / "b", extra)
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["problems"], [])          # no dup-key noise
        self.assertEqual(report["tables"]["trace_edges"]["only_scratch"],
                         ["SL-001/FR-002/implements"])
        self.assertEqual(report["tables"]["trace_edges"]["changed"], {})

    def test_entity_types_keyed_on_type_id(self):
        rows_a = {"entity_types": [{"type_id": "requirement", "label": "Req"}]}
        rows_b = {"entity_types": [{"type_id": "requirement", "label": "Requirement"}]}
        a = write_pkg(self.base / "a", rows_a)
        b = write_pkg(self.base / "b", rows_b)
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertIn("requirement", report["tables"]["entity_types"]["changed"])

    def test_only_live_and_only_scratch_rows(self):
        a = write_pkg(self.base / "a", {"decisions": [{"id": "DEC-001", "title": "x"},
                                                      {"id": "DEC-029", "title": "post"}]})
        b = write_pkg(self.base / "b", {"decisions": [{"id": "DEC-001", "title": "x"}]})
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["tables"]["decisions"]["only_live"], ["DEC-029"])
        self.assertEqual(report["tables"]["decisions"]["only_scratch"], [])

    def test_duplicate_keys_reported_not_clobbered(self):
        a = write_pkg(self.base / "a", {"risks": [{"id": "RISK-001", "title": "a"},
                                                  {"id": "RISK-001", "title": "b"}]})
        b = write_pkg(self.base / "b", {"risks": [{"id": "RISK-001", "title": "a"}]})
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertTrue(any("duplicate key" in p for p in report["problems"]))

    def test_packages_singleton_compares_fields(self):
        """A live/scratch pair differs on name structurally — field diff, not
        an add/remove pair."""
        a = write_pkg(self.base / "a", {"packages": [{"name": "acmp", "title": "T"}]})
        b = write_pkg(self.base / "b", {"packages": [{"name": "acmp-scratch",
                                                      "title": "T"}]})
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        [diff] = report["tables"]["packages"]["changed"]["(package)"]
        self.assertEqual(diff["field"], "name")

    def test_table_only_on_one_side(self):
        a = write_pkg(self.base / "a", {"defects": [{"id": "DEF-001", "title": "x"}]})
        b = write_pkg(self.base / "b", {})
        code, out = run_tool(a, b, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["tables"]["defects"]["table_only_in"], "live")

    def test_missing_dir_exits_two(self):
        a = write_pkg(self.base / "a", {})
        code, _ = run_tool(a, str(self.base / "nope"))
        self.assertEqual(code, 2)

    def test_demo_package_self_diff_clean(self):
        demo = REPO_ROOT / "generated-samples" / "support-triage-agent-v2" / "data"
        code, out = run_tool(str(demo), str(demo))
        self.assertEqual(code, 0)
        self.assertIn("no differences", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
