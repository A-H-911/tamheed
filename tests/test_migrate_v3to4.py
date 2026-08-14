"""v3 -> v4 migration contract (plan 031/B27). Stdlib unittest only.

Covers: the package_open refusal, the preview report (every documented transform),
the confirmed conversion (backup, legacy-prompt conversion, store-validated
write-back), per-transform row outcomes, double-migration refusal, the migrated
package opening clean with G-REL passing, and byte-determinism (same input ->
byte-identical output).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))

import tamheed_server as srv  # noqa: E402


def build_v3_fixture(root: Path, name: str = "legacy") -> Path:
    """A synthetic v3.2.1 package exercising every v3->v4 transform."""
    data = root / name / "data"
    data.mkdir(parents=True)

    def w(fname, rows):
        (data / fname).write_bytes(("\n".join(
            json.dumps(r, ensure_ascii=False, separators=(",", ":"))
            for r in rows) + "\n").encode("utf-8"))

    w("packages.jsonl", [{"name": name, "title": "Legacy", "profile": "rnd",
                          "mode": "weird-mode", "iteration": 2,
                          "package_version": "3.2.1", "mvp_definition": None,
                          "entry_point": None, "go_no_go": None,
                          "created_at": "2026-01-01", "custom_attributes": None}])
    w("entity_types.jsonl", [
        {"type_id": t, "label": t, "id_prefix": p, "generation_class": g,
         "template_ref": None, "custom_attributes": None}
        for t, p, g in [("requirement", "FR-", "Always"), ("constraint", "CON-", "Always"),
                        ("risk", "RISK-", "Always"), ("phase", "PH-", "Always"),
                        ("milestone", "MS-", "Conditional"), ("slice", "SL-", "Conditional"),
                        ("stakeholder", "STK-", "Conditional"), ("defect", "DEF-", "Conditional"),
                        ("experiment", "EXP-", "Conditional"), ("scope-change", "SC-", "Continuous"),
                        ("progress-entry", "PE-", "Continuous"), ("decision", "DEC-", "Always"),
                        ("prompt", "PRM-", "Always"), ("test", "TEST-", "Conditional"),
                        ("wbs-item", "WBS-", "Conditional")]])
    w("requirements.jsonl", [{"id": "FR-001", "kind": "functional", "title": "req",
                              "statement": "s", "priority": None, "mvp": 1,
                              "lifecycle_status": "Approved", "disposition": None,
                              "disposition_reason_ref": None, "source_kind": "brief",
                              "source_span": "brief:1", "introduced_in": 1,
                              "retired_in": None, "custom_attributes": None,
                              "last_referenced": None}])
    w("constraints.jsonl", [{"id": "CON-001", "title": "c", "statement": None,
                             "lifecycle_status": "Approved", "disposition": None,
                             "disposition_reason_ref": None, "source_kind": None,
                             "source_span": "somewhere:3", "custom_attributes": None,
                             "last_referenced": None}])
    w("risks.jsonl", [{"id": "RISK-001", "title": "r", "description": None,
                       "probability": "High", "impact": "3 (moderate)",
                       "mitigation": None, "risk_state": "open", "discharged_by": None,
                       "lifecycle_status": "Approved", "disposition": None,
                       "disposition_reason_ref": None, "source_kind": None,
                       "source_span": None, "custom_attributes": None,
                       "last_referenced": None}])
    w("phases.jsonl", [{"id": "PH-1", "title": "one", "objective": None,
                        "exit_criteria": None, "sort_order": 0,
                        "lifecycle_status": "Approved", "disposition": None,
                        "disposition_reason_ref": None, "introduced_in": 1,
                        "retired_in": None, "source_kind": None, "source_span": None,
                        "custom_attributes": None, "last_referenced": None}])
    w("milestones.jsonl", [{"id": "MS-001", "title": "m", "phase_id": "PH-1",
                            "due": None, "lifecycle_status": "Implemented",
                            "disposition": None, "disposition_reason_ref": None,
                            "custom_attributes": None, "last_referenced": None}])
    w("slices.jsonl", [{"id": "SL-001", "title": "sl", "phase_id": "PH-1",
                        "objective": None, "sort_order": 0,
                        "lifecycle_status": "Draft", "disposition": None,
                        "disposition_reason_ref": None, "introduced_in": 1,
                        "retired_in": None, "custom_attributes": None,
                        "last_referenced": None}])
    w("stakeholders.jsonl", [{"id": "STK-001", "name": "Ops team", "role": None,
                              "interest": None, "lifecycle_status": "Draft",
                              "disposition": None, "disposition_reason_ref": None,
                              "source_kind": None, "source_span": None,
                              "custom_attributes": None, "last_referenced": None}])
    w("defects.jsonl", [{"id": "DEF-001", "title": "bug", "severity": "high",
                         "status": "Open", "found_in": "SL-001", "fixed_by": None,
                         "custom_attributes": None, "last_referenced": None}])
    w("experiments.jsonl", [{"id": "EXP-001", "title": "e", "method": None,
                             "timebox": None, "verdict": "PASS", "results": None,
                             "lifecycle_status": "Implemented", "disposition": None,
                             "disposition_reason_ref": None, "source_kind": None,
                             "source_span": None, "custom_attributes": None,
                             "last_referenced": None}])
    w("decisions.jsonl", [{"id": "DEC-001", "title": "d", "decision": None,
                           "rationale": None, "lifecycle_status": "Approved",
                           "disposition": None, "disposition_reason_ref": None,
                           "promoted_to": None, "source_kind": None,
                           "source_span": None, "custom_attributes": None,
                           "last_referenced": None}])
    w("scope_changes.jsonl", [{"id": "SC-001", "decision_ref": "DEC-001",
                               "description": "x", "iteration": 2,
                               "custom_attributes": None, "last_referenced": None}])
    w("progress_entries.jsonl", [{"id": "PE-001", "entry": "did things",
                                  "phase_id": "PH-1", "slice_id": None,
                                  "occurred_at": "2026-01-02",
                                  "custom_attributes": None, "last_referenced": None}])
    w("tests.jsonl", [{"id": "TEST-001", "title": "t", "kind": None,
                       "verdict": "Pass", "lifecycle_status": "Draft",
                       "disposition": None, "disposition_reason_ref": None,
                       "source_kind": None, "source_span": None,
                       "custom_attributes": None, "last_referenced": None}])
    w("wbs_items.jsonl", [{"id": "WBS-1", "title": "w", "parent_id": None,
                           "phase_id": "PH-1", "slice_id": "SL-001", "effort": None,
                           "lifecycle_status": "Draft", "disposition": None,
                           "disposition_reason_ref": None, "source_kind": None,
                           "source_span": None, "custom_attributes": None,
                           "last_referenced": None}])
    w("trace_edges.jsonl", [
        {"from_id": "SL-001", "to_id": "FR-001", "relation": "implements"},
        {"from_id": "WBS-1", "to_id": "FR-001", "relation": "binds_to"},
        {"from_id": "TEST-001", "to_id": "FR-001", "relation": "mitigates"},
        {"from_id": "PRM-001", "to_id": "PH-1", "relation": "relates_to"},
    ])
    w("prompts.jsonl", [{"id": "PRM-001", "prompt_kind": "initial",
                         "title": "Kickoff", "body": "Do the thing.",
                         "phase_id": "PH-1", "custom_attributes": None,
                         "last_referenced": None}])
    return root / name


def rows(pkg: Path, fname: str) -> list[dict]:
    return [json.loads(line) for line in
            (pkg / "data" / fname).read_text(encoding="utf-8").splitlines()
            if line.strip()]


class MigrateV3ToV4Test(unittest.TestCase):
    """One fixture, migrated once in setUpClass; assertions read the outcome."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(cls._tmp.name)
        srv._CURRENT = srv._CURRENT_NAME = None
        cls.pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        cls.refusal = srv.package_open("legacy")
        cls.preview = srv.package_migrate("legacy")
        cls.migrated = srv.package_migrate("legacy", confirm=True)

    @classmethod
    def tearDownClass(cls):
        if srv._CURRENT is not None:
            srv.package_close()
        cls._tmp.cleanup()

    def test_open_refuses_pre_v4(self):
        self.assertFalse(self.refusal.get("ok"))
        self.assertIn("package_migrate", self.refusal["error"])
        self.assertIn("3.2.1", self.refusal["error"])

    def test_preview_reports_every_transform_and_writes_nothing(self):
        self.assertEqual(self.preview["stage"], "preview")
        rep = self.preview["report"]
        self.assertEqual(rep["version_from"], "3.2.1")
        self.assertEqual(rep["mode_coerced"], {"from": "weird-mode", "to": "full"})
        self.assertEqual(rep["milestone_status_dropped"],
                         [{"id": "MS-001", "was": "Implemented"}])
        self.assertEqual(rep["stakeholders_renamed"], "name -> title")
        self.assertEqual(rep["status_column_renamed"], ["defects"])
        self.assertEqual(rep["verdicts_mapped"],
                         [{"id": "EXP-001", "from": "PASS", "to": "Validated"}])
        self.assertEqual(rep["scope_changes_marked_merged"], ["SC-001"])
        self.assertEqual(rep["risk_scale_normalized"],
                         [{"id": "RISK-001", "column": "probability",
                           "from": "High", "to": "high"}])
        self.assertEqual(rep["risk_scale_stashed"][0]["column"], "impact")
        self.assertEqual({e["was"] for e in rep["edges_retyped"]},
                         {"binds_to", "mitigates"})
        self.assertTrue(any(x["table"] == "constraints"
                            for x in rep["provenance_repaired"]))
        self.assertIn("waiver", rep["entity_types_added"])
        self.assertIn("prompt", rep["entity_types_scrubbed"])
        self.assertIn("legacy_prompts", rep)

    def test_confirm_backs_up_converts_prompts_and_rewrites(self):
        self.assertEqual(self.migrated["stage"], "migrated")
        self.assertTrue((self.pkg / "data-v3-backup" / "prompts.jsonl").exists(),
                        "backup must hold the ORIGINAL files")
        self.assertFalse((self.pkg / "data" / "prompts.jsonl").exists())
        self.assertEqual(self.migrated["legacy_prompts"]["prompts_converted"],
                         ["prompts/prm-001-initial.md"])
        pkg_row = rows(self.pkg, "packages.jsonl")[0]
        self.assertEqual(pkg_row["package_version"], "4.0.0")
        self.assertEqual(pkg_row["mode"], "full")

    def test_row_transforms_landed(self):
        self.assertEqual(rows(self.pkg, "stakeholders.jsonl")[0]["title"], "Ops team")
        self.assertEqual(rows(self.pkg, "defects.jsonl")[0]["lifecycle_status"], "Open")
        self.assertEqual(rows(self.pkg, "experiments.jsonl")[0]["verdict"], "Validated")
        self.assertEqual(rows(self.pkg, "scope_changes.jsonl")[0]["lifecycle_status"],
                         "Merged")
        ms = rows(self.pkg, "milestones.jsonl")[0]
        self.assertNotIn("lifecycle_status", ms)
        self.assertNotIn("disposition", ms)
        risk = rows(self.pkg, "risks.jsonl")[0]
        self.assertEqual(risk["probability"], "high")
        self.assertIsNone(risk["impact"])
        self.assertEqual(json.loads(risk["custom_attributes"])["v3_impact"],
                         "3 (moderate)")
        self.assertEqual(rows(self.pkg, "constraints.jsonl")[0]["source_kind"],
                         "inferred")

    def test_edges_cleaned(self):
        edges = {(e["from_id"], e["to_id"], e["relation"])
                 for e in rows(self.pkg, "trace_edges.jsonl")}
        self.assertIn(("WBS-1", "FR-001", "relates_to"), edges)
        self.assertIn(("TEST-001", "FR-001", "relates_to"), edges)
        self.assertNotIn(("WBS-1", "FR-001", "binds_to"), edges)
        self.assertNotIn(("TEST-001", "FR-001", "mitigates"), edges)
        self.assertFalse(any(f.startswith("PRM-") or t.startswith("PRM-")
                             for f, t, _ in edges))

    def test_migration_audit_event(self):
        pes = rows(self.pkg, "progress_entries.jsonl")
        self.assertEqual(pes[0]["event_type"], "note")  # legacy row backfilled
        audit = [p for p in pes if "MIGRATED store v3.2.1 -> v4.0.0" in p["entry"]]
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["actor"], "system:migrate")

    def test_registry_scrubbed_and_completed(self):
        ets = rows(self.pkg, "entity_types.jsonl")
        ids = {r["type_id"] for r in ets}
        self.assertIn("waiver", ids)
        self.assertNotIn("prompt", ids)
        self.assertFalse(any("template_ref" in r for r in ets))

    def test_double_migration_refused(self):
        again = srv.package_migrate("legacy")
        self.assertFalse(again.get("ok"))
        self.assertIn("already", again["error"])

    def test_migrated_package_opens_clean_with_grel_pass(self):
        opened = srv.package_open("legacy")
        self.assertTrue(opened.get("ok"), opened)
        try:
            gates = srv.gate_run()["gates"]
            self.assertEqual(gates["G-REL"]["status"], "pass", gates["G-REL"])
        finally:
            srv.package_close()

    def test_backup_refusal_on_rerun_after_manual_downgrade(self):
        """A second confirm on a package with a leftover backup dir is refused."""
        # Fake a pre-v4 version back into packages.jsonl (operator error scenario).
        path = self.pkg / "data" / "packages.jsonl"
        row = rows(self.pkg, "packages.jsonl")[0]
        row["package_version"] = "3.0.0"
        path.write_bytes((json.dumps(row, ensure_ascii=False,
                                     separators=(",", ":")) + "\n").encode())
        try:
            res = srv.package_migrate("legacy", confirm=True)
            self.assertFalse(res.get("ok"))
            self.assertIn("data-v3-backup", res["error"])
        finally:
            row["package_version"] = "4.0.0"
            path.write_bytes((json.dumps(row, ensure_ascii=False,
                                         separators=(",", ":")) + "\n").encode())


class MigrateDeterminismTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
