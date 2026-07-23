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
        migrate.parse_v1 = lambda s, **kw: plan
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

    def test_status_coercions_recorded_in_preview(self):
        """Plan 018 (C17): unknown v1 statuses map semantically, always ledgered."""
        md = ("| ID | Risk | Status |\n|----|------|--------|\n"
              "| RISK-001 | a | Open |\n| RISK-002 | b | Monitoring |\n"
              "| RISK-003 | c | Closed |\n| RISK-004 | d | Active |\n"
              "| RISK-005 | e | Bizarre-word |\n| RISK-006 | f | |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        for row in table.rows:
            migrate._map_register_row(plan, "RISK", row[0].strip(), table, row)
        rows = {r["id"]: r["lifecycle_status"] for r in plan.rows["risks"]}
        self.assertEqual(rows["RISK-001"], "Approved")     # Open
        self.assertEqual(rows["RISK-002"], "Approved")     # Monitoring
        self.assertEqual(rows["RISK-003"], "Obsolete")     # Closed
        self.assertEqual(rows["RISK-004"], "Approved")     # Active
        self.assertEqual(rows["RISK-005"], "Draft")        # unknown -> default
        ledger = {e["id"]: e for e in plan.status_coerced}
        self.assertEqual(len(ledger), 5)                   # empty cell NOT recorded
        self.assertNotIn("RISK-006", ledger)
        self.assertEqual(ledger["RISK-001"],
                         {"id": "RISK-001", "original": "Open", "coerced": "Approved"})
        # operator override wins over the semantic default (status_map, normalized keys)
        plan2 = migrate.Plan()
        plan2.status_map = {"Open": "Deferred"}
        migrate._map_register_row(plan2, "RISK", "RISK-001", table, table.rows[0])
        self.assertEqual(plan2.rows["risks"][0]["lifecycle_status"], "Deferred")

    def test_status_map_values_validated(self):
        out = migrate.run_migration(str(FIXTURES / "valid-package"), ".",
                                    status_map={"Open": "NotAStatus"})
        self.assertFalse(out["ok"])
        self.assertIn("lifecycle vocabulary", out["error"])

    def test_id_column_never_becomes_title(self):
        """Plan 018 (C17/F2): a title alias must never resolve to the id column."""
        md = ("| Phase | Goal | Status |\n|-------|------|--------|\n"
              "| PH-0 | Build the foundations | Active |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "PH", "PH-0", table, table.rows[0])
        row = plan.rows["phases"][0]
        self.assertNotEqual(row["title"], "PH-0")
        self.assertTrue(any(f["id"] == "PH-0" for f in plan.title_fallbacks))
        # `name` alias resolves for stakeholder-style tables
        md2 = ("| ID | Name | Interest |\n|----|------|----------|\n"
               "| STK-001 | Ops lead | uptime |\n")
        [t2] = migrate.vp.parse_markdown_tables(md2)
        plan2 = migrate.Plan()
        migrate._map_register_row(plan2, "STK", "STK-001", t2, t2.rows[0])
        self.assertEqual(plan2.rows["stakeholders"][0]["name"], "Ops lead")

    def test_failed_adr_falls_through_to_other_narrative(self):
        """Plan 018 (C17/F3): parse failures are preserved, not just listed."""
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "adrs").mkdir()
            (tmp / "architecture" / "diagrams").mkdir(parents=True)
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "adrs" / "README.md").write_text(
                "# ADR index\n\n## Purpose\nWhy these records exist.\n", encoding="utf-8")
            (tmp / "adrs" / "notes.md").write_text(
                "# Drafting notes\n\n## Style\nMADR, outcome-first.\n", encoding="utf-8")
            (tmp / "adrs" / "adr-0001.md").write_text(
                "# ADR-0001: Real one\n\n- Status: Accepted\n\n## Context\nc\n\n"
                "## Decision Outcome\nd\n\n## Consequences\nq\n", encoding="utf-8")
            (tmp / "architecture" / "diagrams" / "README.md").write_text(
                "# Diagram index\n\n## Kinds\nWhat lives here.\n", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        by_path = {json.loads(d["custom_attributes"])["v1"]["path"]: d["doc_kind"]
                   for d in plan.rows["narrative_documents"]}
        # READMEs match the 'readme' narrative kind on fall-through; other prose -> 'other'.
        self.assertIn("adrs/README.md", by_path)                     # preserved, not lost
        self.assertIn("architecture/diagrams/README.md", by_path)    # unknown stem too
        self.assertEqual(by_path["adrs/notes.md"], "other")          # non-README prose
        self.assertEqual(len(plan.rows["adrs"]), 1)                  # real ADR: rows-only
        adr_twin = [d for d in plan.rows["narrative_documents"]
                    if "adr-0001" in d["custom_attributes"]]
        self.assertEqual(adr_twin, [])                               # no double-processing
        self.assertTrue(any("adrs/README.md" in u for u in plan.unmapped))

    def test_no_status_column_defaults_approved_with_note(self):
        """Plan 019 (C21/B1): no-status-column registers get Approved, not Draft."""
        md = ("| ID | Risk | Impact |\n|----|------|--------|\n"
              "| RISK-001 | leak | high |\n| RISK-002 | drift | low |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        for row in table.rows:
            migrate._map_register_row(plan, "RISK", row[0].strip(), table, row,
                                      src="risks/register.md")
        self.assertTrue(all(r["lifecycle_status"] == "Approved"
                            for r in plan.rows["risks"]))
        self.assertEqual(plan.status_defaulted[("risks/register.md", "RISK")], 2)
        self.assertEqual(plan.status_coerced, [])      # defaulting is not coercion
        # governance exclusion: decisions never auto-approve
        md2 = ("| ID | Decision | Rationale |\n|----|----------|----------|\n"
               "| DEC-001 | use X | speed |\n")
        [t2] = migrate.vp.parse_markdown_tables(md2)
        plan2 = migrate.Plan()
        migrate._map_register_row(plan2, "DEC", "DEC-001", t2, t2.rows[0])
        self.assertEqual(plan2.rows["decisions"][0]["lifecycle_status"], "Proposed")

    def test_grouped_ledger_shapes(self):
        """Plan 019 (C21/B4-B5): groups are the operator decision unit."""
        entries = ([{"id": f"FR-{i:03d}", "family": "FR"} for i in range(1, 78)]
                   + [{"id": "PH-1", "family": "PH"}, {"id": "PH-2", "family": "PH"}])
        grouped = migrate._group(entries, lambda e: (e["family"],), ("family",))
        self.assertEqual(grouped[0], {"family": "FR", "count": 77})   # no ids: >10
        self.assertEqual(grouped[1],
                         {"family": "PH", "count": 2, "ids": ["PH-1", "PH-2"]})

    def test_clean_line_preserves_hyphens_and_ids(self):
        """Plan 020 (C24/D-2): positional stripping — governed ids survive."""
        out = migrate._clean_line(
            "- **WBS-1.1** Realizes FR-001, FR-003–FR-015. (BL-005 / EPIC-01)")
        self.assertIn("WBS-1.1", out)
        self.assertIn("FR-001", out)
        self.assertIn("BL-005", out)
        long = migrate._clean_line("x" * 300)
        self.assertEqual(len(long), 200)                   # one cap, 200 — not 120

    def test_fallback_statement_keeps_raw_cell(self):
        """Plan 020 (C24/D-0): a fallback title never becomes the statement."""
        raw = ("As a **committee-member**, I want FR-linked agenda-items "
               + "x" * 150 + " so that decisions trace end-to-end.")
        md = (f"| ID | User story | Priority |\n|----|-----------|----------|\n"
              f"| FR-001 | {raw} | M |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "FR", "FR-001", table, table.rows[0],
                                  src="domain/user-stories.md")
        row = plan.rows["requirements"][0]
        self.assertEqual(row["statement"], raw)            # raw, uncleaned, uncapped
        self.assertNotIn("**", row["title"])               # title cleaned + capped
        self.assertLessEqual(len(row["title"]), 200)
        self.assertIn("committee-member", row["title"])    # hyphens intact
        self.assertTrue(any(f["id"] == "FR-001" for f in plan.title_fallbacks))

    def test_dw_keyed_on_parsed_number_never_position(self):
        """Plan 020 (C24/D-4): unsorted registers must not renumber ids."""
        md = ("| ID | Deferred item | Severity |\n|----|--------------|----------|\n"
              "| D-15 | out-of-order first | High |\n"
              "| D-03 | second | Low |\n| D-15 | duplicate number | Low |\n")
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "execution").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "execution" / "deferred-work-register.md").write_text(
                f"# Deferred\n\n{md}", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        self.assertEqual(plan.dw_crosswalk["D-15"], "DW-015")
        self.assertEqual(plan.dw_crosswalk["D-03"], "DW-003")
        self.assertTrue(any("duplicate number" in u for u in plan.unmapped))

    def test_ac_lands_proposed_when_no_status_column(self):
        """Plan 020 (C24/D-12, caught by the golden delta review): the Approved default
        must never freeze slice_id before slices can exist."""
        md = ("| ID | Given / When / Then | Verifies |\n|----|----|----|\n"
              "| AC-001 | Given X when Y then Z happens for the committee. | FR-001 |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "AC", "AC-001", table, table.rows[0], src="a.md")
        self.assertEqual(plan.rows["acceptance_criteria"][0]["lifecycle_status"],
                         "Proposed")
        self.assertEqual(plan.status_defaulted[("a.md", "AC")], 1)

    def test_weak_def_rows_carry_raw_line(self):
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "planning").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "planning" / "work-breakdown.md").write_text(
                "# WBS\n\n- **WBS-1.1** Vendor-neutral model-ports + bounded-loop "
                "skeleton. Realizes ADR-0003.\n", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        row = next(r for r in plan.rows["wbs_items"] if r["id"] == "WBS-1.1")
        self.assertIn("model-ports", row["title"])         # hyphens survive
        attrs = json.loads(row["custom_attributes"])
        self.assertIn("model-ports", attrs["v1"]["raw_line"])  # raw line preserved

    def test_phase_prose_status_resolves(self):
        """Plan 020 (C24/D-9, narrow): heading-contains-PH-id + Status line only."""
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "planning").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "planning" / "roadmap.md").write_text(
                "# Roadmap\n\n| ID | Phase | Goal |\n|----|-------|------|\n"
                "| PH-1 | Alpha | ship |\n| PH-2 | Beta | polish |\n\n"
                "## PH-1 — Alpha\n\n**Status: complete.**\n\n"
                "## Later work\n\nStatus: irrelevant here.\n", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        rows = {r["id"]: r["lifecycle_status"] for r in plan.rows["phases"]}
        self.assertEqual(rows["PH-1"], "Implemented")      # Complete -> Implemented
        self.assertEqual(rows["PH-2"], "Approved")         # untouched default
        self.assertEqual(plan.status_defaulted.get(("planning/roadmap.md", "PH")), 1)

    def test_sections_split_on_shallowest_level(self):
        """Plan 020 (C24/D-7): a ###-only body must not collapse into one Preamble."""
        parts = migrate._sections("# T\n\n### 2026-01-01 — a\nbody a\n\n"
                                  "### 2026-01-02 — b\nbody b\n")
        headings = [h for h, _ in parts]
        self.assertIn("2026-01-01 — a", headings)
        self.assertIn("2026-01-02 — b", headings)

    def test_fidelity_ledgers_fire(self):
        """Plan 020 (C23): truncation histogram + column starvation, end to end."""
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dest:
            tmp = Path(src)
            (tmp / "planning").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "planning" / "work-breakdown.md").write_text(
                "# WBS\n\n- **WBS-1.1** " + "y" * 300 + "\n", encoding="utf-8")
            inv_rows = "\n".join(f"| INV-00{i} | inv {i} rule | note {i} |"
                                 for i in range(1, 7))
            (tmp / "invariants.md").write_text(
                "# Invariants\n\n| ID | Invariant | Enforcement notes |\n"
                f"|----|-----------|-------------------|\n{inv_rows}\n",
                encoding="utf-8")
            real_pre = migrate.preflight  # mini fixture is not G-SET-conformant
            migrate.preflight = lambda s: {"ok": True, "stage": "preflight"}
            try:
                out = migrate.run_migration(str(tmp), dest, name="t", confirm=True)
            finally:
                migrate.preflight = real_pre
            ledgers = out["fidelity"]["fidelity_ledgers"]
        self.assertIn({"family": "wbs_items", "field": "title",
                       "count_at_cap": 1, "cap": 200}, ledgers["truncations"])
        starved = {(s["family"], s["column"]) for s in ledgers["column_starvation"]}
        self.assertIn(("invariants", "enforcement"), starved)

    def test_title_column_beats_alias_columns(self):
        """Plan 021 (C26/B1): an exact Title column wins over earlier alias columns —
        the EPIC crosswalk cell must never become the title again."""
        md = ("| EPIC | Title | Realizes |\n|------|-------|----------|\n"
              "| EPIC-18 | Tarseem Diagram Management | WBS-18 |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "WBS", "WBS-18", table, table.rows[0], id_col=2)
        self.assertEqual(plan.rows["wbs_items"][0]["title"],
                         "Tarseem Diagram Management")

    def test_title_never_displaces_statement(self):
        """Plan 021 round-5 review guard: a Title column must not replace a Statement
        column in the long-form text (the D-0 class reborn)."""
        md = ("| ID | Title | Statement | Status |\n|----|-------|-----------|--------|\n"
              "| FR-001 | Short name | The full long statement of the requirement with "
              "detail. | Approved |\n")
        [table] = migrate.vp.parse_markdown_tables(md)
        plan = migrate.Plan()
        migrate._map_register_row(plan, "FR", "FR-001", table, table.rows[0])
        row = plan.rows["requirements"][0]
        self.assertEqual(row["title"], "Short name")
        self.assertIn("full long statement", row["statement"])

    def test_escaped_pipes_do_not_shear_rows(self):
        """Plan 021 (C26/B3): `\\|` is a literal pipe inside ONE cell."""
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "functional.md").write_text(
                "# FR\n\n| ID | Statement | Priority | Status |\n"
                "|----|-----------|----------|--------|\n"
                "| FR-100 | Lifecycle states (Superseded \\| Deprecated). No backward "
                "transitions. | M | Approved |\n", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        row = plan.rows["requirements"][0]
        self.assertIn("(Superseded | Deprecated)", row["statement"])   # one cell, unescaped
        self.assertEqual(row["priority"], "M")                          # columns intact
        self.assertNotIn("\\", row["statement"])

    def test_deferred_work_status_carried(self):
        """Plan 021 (C26 §A residual): the v1 Status maps onto the DW enum."""
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "execution").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "execution" / "deferred-work-register.md").write_text(
                "# Deferred\n\n| ID | Deferred item | Severity | Status |\n"
                "|----|---------------|----------|--------|\n"
                "| D-01 | a thing | High | Done |\n"
                "| D-02 | b thing | Low | Activated |\n"
                "| D-03 | c thing | Low | Someday-maybe |\n", encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        rows = {r["id"]: r.get("status") for r in plan.rows["deferred_work"]}
        self.assertEqual(rows["DW-001"], "Done")
        self.assertEqual(rows["DW-002"], "Activated")
        self.assertIsNone(rows["DW-003"])                    # off-enum -> schema default
        self.assertTrue(any("Someday-maybe" in u for u in plan.unmapped))

    def test_phase_prose_status_matches_by_title(self):
        """Plan 021 (C26): headings carry titles, not ids — both now match."""
        with tempfile.TemporaryDirectory() as src:
            tmp = Path(src)
            (tmp / "planning").mkdir()
            (tmp / "manifest.json").write_text('{"package": "t"}', encoding="utf-8")
            (tmp / "planning" / "roadmap.md").write_text(
                "# Roadmap\n\n| ID | Title | Goal |\n|----|-------|------|\n"
                "| PH-0 | Discovery & Validation | learn |\n\n"
                "## Phase 0 — Discovery & Validation\n\n**Status: complete.**\n",
                encoding="utf-8")
            plan = migrate.parse_v1(tmp)
        self.assertEqual(plan.rows["phases"][0]["lifecycle_status"], "Implemented")

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
