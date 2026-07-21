"""Migration goldens (plan 010/B5): v1 -> v2 fidelity + refusal routing.

Fidelity criterion (references/migration-v1.md): (a) identifier sets match,
(b) family counts match the manifest's identifier_counts where present — disk wins
over a stale manifest, deltas reported; (c) a v1-passing package passes v2 gates.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))

import migrate  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "fixtures"
DEMO_V1 = REPO_ROOT / "generated-samples" / "support-triage-agent"
GOLDEN_V2 = REPO_ROOT / "generated-samples" / "support-triage-agent-v2"


def tree_digest(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


class MigrationGoldenTest(unittest.TestCase):
    def test_valid_package_migrates_with_full_fidelity(self):
        before = tree_digest(FIXTURES / "valid-package")
        with tempfile.TemporaryDirectory() as dest:
            out = migrate.run_migration(str(FIXTURES / "valid-package"), dest, confirm=True)
            self.assertTrue(out["ok"], out)
            fid = out["fidelity"]
            self.assertEqual(fid["identifier_gaps"], [])       # (a)
            self.assertEqual(fid["count_deltas"], {})          # (b)
            self.assertEqual(fid["gate_failures"], {})         # (c)
        # v1 input is a read-only migration source: byte-identical after the run.
        self.assertEqual(before, tree_digest(FIXTURES / "valid-package"))

    def test_demo_migrates_and_matches_committed_golden(self):
        with tempfile.TemporaryDirectory() as dest:
            out = migrate.run_migration(str(DEMO_V1), dest,
                                        name="support-triage-agent-v2", confirm=True)
            self.assertTrue(out["ok"], out)
            fid = out["fidelity"]
            self.assertEqual(fid["identifier_gaps"], [])       # (a)
            # (b) the ONE known stale-manifest divergence: the v1 manifest counts 12
            # WBS leaves; disk defines 18 (6 group headings + 12 leaves). Disk wins;
            # the delta is reported, never auto-resolved.
            self.assertEqual(fid["count_deltas"],
                             {"WBS": {"manifest": 12, "migrated": 18}})
            self.assertEqual(fid["gate_failures"], {})         # (c)
            # Regression: fresh migration output is byte-identical to the committed golden.
            fresh = tree_digest(Path(dest) / "support-triage-agent-v2" / "data")
            self.assertEqual(fresh, tree_digest(GOLDEN_V2 / "data"))

    def test_golden_loads_and_passes_gates(self):
        sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))
        import store
        conn = store.load(GOLDEN_V2 / "data")
        for view in ("g_trace_failures", "g_set_failures", "g_progress_failures"):
            self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0], 0,
                             msg=f"{view} not clean on the committed golden")
        conn.close()

    def test_preview_writes_nothing(self):
        with tempfile.TemporaryDirectory() as dest:
            out = migrate.run_migration(str(FIXTURES / "valid-package"), dest)
            self.assertTrue(out["ok"])
            self.assertEqual(out["stage"], "preview")
            self.assertEqual(list(Path(dest).iterdir()), [])

    def test_invalid_and_incomplete_refused_at_preflight(self):
        # invalid-package's seeded defects include a MISSING manifest -> the routing
        # refusal fires; incomplete-package has one -> the v1 validator refusal fires.
        expected = {"invalid-package": "not a conformant v1 package",
                    "incomplete-package": "v1 validator failed"}
        for fixture, message in expected.items():
            with tempfile.TemporaryDirectory() as dest:
                out = migrate.run_migration(str(FIXTURES / fixture), dest, confirm=True)
                self.assertFalse(out["ok"], f"{fixture} must be refused")
                self.assertEqual(out["stage"], "preflight")
                self.assertIn(message, out["error"])
                self.assertEqual(list(Path(dest).iterdir()), [])  # nothing written

    def test_nonconformant_lineage_routed_to_adopt(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dest:
            (Path(src) / "notes.md").write_text("# TD-01 hand-coined ids, no manifest\n",
                                                encoding="utf-8")
            out = migrate.run_migration(src, dest, confirm=True)
            self.assertFalse(out["ok"])
            self.assertEqual(out["stage"], "preflight")
            self.assertIn("package_adopt", out["error"])


def _package_row(name: str) -> dict:
    return {"name": name, "title": "T", "profile": "unknown", "mode": "full",
            "package_version": "1.0.0", "mvp_definition": None, "entry_point": None,
            "go_no_go": None, "created_at": "v1-migration", "custom_attributes": "{}"}


class FieldReportHardeningTest(unittest.TestCase):
    """Plan 017 Phase 1 (field-evidence C11/C12): in-process preflight with crash
    isolation, promoted_to ADR-filter, populate row context, no poison directory."""

    def test_preflight_spawns_no_subprocess(self):
        import subprocess as sp
        real = sp.run
        sp.run = lambda *a, **k: (_ for _ in ()).throw(
            AssertionError("preflight spawned a subprocess (C11 regression)"))
        try:
            self.assertTrue(migrate.preflight(FIXTURES / "valid-package")["ok"])
        finally:
            sp.run = real

    def test_preflight_crash_is_isolated_not_raised(self):
        real = migrate.vp.run_gates
        migrate.vp.run_gates = lambda p: (_ for _ in ()).throw(RuntimeError("kaboom"))
        try:
            out = migrate.preflight(FIXTURES / "valid-package")
        finally:
            migrate.vp.run_gates = real
        self.assertFalse(out["ok"])
        self.assertIn("crashed", out["error"])
        self.assertIn("kaboom", out["traceback"])

    def test_preflight_failure_names_critical_gates(self):
        out = migrate.preflight(FIXTURES / "incomplete-package")
        self.assertFalse(out["ok"])
        self.assertIn("G-SET", out["error"])
        self.assertIn("critical_failed", out["report"])

    def test_promoted_to_accepts_only_adr_tokens(self):
        md = ("| ID | Decision | Status | Promoted to |\n"
              "|----|----------|--------|-------------|\n"
              "| DEC-001 | Use X | Approved | amends **DEC-019**, see **ADR-0006** |\n"
              "| DEC-002 | Use Y | Approved | n/a (amends **DEC-019**'s phase) |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        for row in table.rows:
            migrate._map_register_row(plan, "DEC", row[0].strip(), table, row)
        rows = {r["id"]: r for r in plan.rows["decisions"]}
        self.assertEqual(rows["DEC-001"]["promoted_to"], "ADR-0006")
        self.assertIsNone(rows["DEC-002"]["promoted_to"])  # ACMP DEC-028 shape: no FK crash
        self.assertTrue(any("DEC-002" in note for note in plan.unmapped))

    def test_populate_failure_names_row_and_leaves_no_poison_dir(self):
        bad = migrate.Plan()
        bad.package = _package_row("pkg")
        bad.add("decisions", {"id": "DEC-001", "decision": "no title",
                              "lifecycle_status": "Approved"})  # NOT NULL violation
        with tempfile.TemporaryDirectory() as dest:
            out = migrate.populate(bad, Path(dest), "pkg")
            self.assertFalse(out["ok"])
            self.assertIn("decisions row DEC-001", out["error"])
            # no poison dir: the created data/ dir is removed, so a retry is not blocked
            self.assertFalse((Path(dest) / "pkg" / "data").exists())
            good = migrate.Plan()
            good.package = _package_row("pkg")
            good.add("decisions", {"id": "DEC-001", "title": "t", "decision": "t",
                                   "lifecycle_status": "Approved"})
            self.assertTrue(migrate.populate(good, Path(dest), "pkg")["ok"])


class DialectToleranceTest(unittest.TestCase):
    """Plan 017 Phase 2 (C12/C13/C14): the ACMP dialect quirks, unit-level. The
    integration-level lock is the Phase-4 dialect fixture."""

    def _mini_package(self, tmp: Path) -> None:
        (tmp / "adrs").mkdir()
        (tmp / "execution").mkdir()
        (tmp / "manifest.json").write_text(json.dumps({
            "package": "mini", "generated": "2026-01-01",
            "profile": "software-platform (on-prem, <=20 users)",
            "identifier_counts": {"FR": 1}}), encoding="utf-8")
        (tmp / "functional.md").write_text(
            "# Functional\n\n"
            "| ID | Requirement | Priority | Status | Source |\n"
            "|----|-------------|----------|--------|--------|\n"
            "| FR-001 | Do the thing | M | Approved | brief L1 |\n", encoding="utf-8")
        (tmp / "execution" / "deferred-work-register.md").write_text(
            "# Deferred\n\n"
            "| ID | Deferred item | Severity | Trigger |\n"
            "|----|---------------|----------|---------|\n"
            "| D-01 | Harden the retry loop | High | before GA |\n"
            "| D-02 | Odd severity word | sometime | — |\n", encoding="utf-8")
        (tmp / "notes.md").write_text("# Stray prose\n\n## Context\nWorth keeping.\n",
                                      encoding="utf-8")
        (tmp / "adrs" / "adr-0001.md").write_text(
            "# ADR-0001: Use queues\n\n- Status: Accepted\n\n"
            "## Context\nWhy.\n\n## Decision Drivers\n- speed\n\n"
            "## Decision Outcome\nUse the queue.\n\n## Consequences\nFine.\n",
            encoding="utf-8")

    def test_parse_v1_absorbs_the_acmp_dialect(self):
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            self._mini_package(tmp)
            plan = migrate.parse_v1(tmp)
        req = plan.rows["requirements"][0]
        self.assertEqual(req["mvp"], 1)                        # MoSCoW M -> mvp (C14)
        self.assertEqual(plan.package["created_at"], "2026-01-01")   # `generated` spelling
        self.assertIn("software-platform",
                      plan.package["custom_attributes"])       # raw profile preserved
        dw = {r["id"]: r for r in plan.rows["deferred_work"]}
        self.assertEqual(dw["DW-001"]["severity"], "high")     # D-nn -> DW- (C13)
        self.assertEqual(dw["DW-002"]["severity"], "medium")   # off-enum -> normalized
        adr = plan.rows["adrs"][0]
        self.assertEqual(adr["id"], "ADR-0001")                # MADR fallback (C12)
        self.assertEqual(adr["lifecycle_status"], "Approved")  # Accepted -> Approved
        self.assertEqual(adr["decision"], "Use the queue.")    # outcome, never drivers (D4)
        others = [d for d in plan.rows["narrative_documents"] if d["doc_kind"] == "other"]
        self.assertTrue(any("Stray prose" in d["title"] for d in others))  # catch-all

    def test_ac_statement_never_inherits_title_cap(self):
        long_stmt = ("**Given** a very long precondition " + "x" * 200
                     + " **when** acted **then** verified")
        md = ("| ID | Given / When / Then | Status | Verifies |\n"
              "|----|--------------------|--------|----------|\n"
              f"| AC-001 | {long_stmt} | Approved | FR-001 |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "AC", "AC-001", table, table.rows[0])
        ac = plan.rows["acceptance_criteria"][0]
        self.assertEqual(ac["statement"], long_stmt)           # raw cell, uncapped (C12)
        self.assertLessEqual(len(ac["title"]), 120)

    def test_zero_family_tripwire_blocks_until_acknowledged(self):
        real_pre, real_parse = migrate.preflight, migrate.parse_v1
        plan = migrate.Plan()
        plan.package = _package_row("t")
        plan.manifest_counts = {"ADR": 33}                     # ACMP shape: 33 ADRs -> 0
        migrate.preflight = lambda s: {"ok": True, "stage": "preflight"}
        migrate.parse_v1 = lambda s: plan
        try:
            with tempfile.TemporaryDirectory() as dest:
                out = migrate.run_migration(".", dest, name="t", confirm=True)
                self.assertFalse(out["ok"])
                self.assertEqual(out["stage"], "populate-refused")
                self.assertIn("ADR", out["error"])
                acked = migrate.run_migration(".", dest, name="t", confirm=True,
                                              allow_zero=["ADR"])
                self.assertEqual(acked["stage"], "post-flight")  # populate proceeded
        finally:
            migrate.preflight, migrate.parse_v1 = real_pre, real_parse

    def test_patch_applied_by_id_before_populate(self):
        plan = migrate.Plan()
        plan.add("acceptance_criteria", {"id": "AC-001", "title": "truncated",
                                         "statement": "truncated"})
        plan.audits.append({"ac_id": "AC-001", "verdict": "Met", "evidence": None})
        with tempfile.TemporaryDirectory() as tmp:
            patch = Path(tmp) / "patch.json"
            patch.write_text(json.dumps({
                "acceptance_criteria": [{"id": "AC-001", "statement": "full text"}],
                "audits": [{"ac_id": "AC-001", "evidence": "tests/test_x.py"}]}),
                encoding="utf-8")
            report = migrate._apply_patch(plan, str(patch))
        self.assertEqual(report["updated"], 2)
        self.assertEqual(plan.rows["acceptance_criteria"][0]["statement"], "full text")
        self.assertEqual(plan.audits[0]["evidence"], "tests/test_x.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
