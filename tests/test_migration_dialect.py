"""Dialect-fixture suite (plan 017 Phase 4, field-evidence C12/C13/C14).

`tests/fixtures/dialect-package` is v1-validator-GREEN (it is also a check.py
golden, expected exit 0) while written in the production dialect that silently
lost data before plan 017 — the ACMP field report's quirk profile: MADR ADRs
without front matter, Given/When/Then AC statements >120 chars, a "Test ref"
audit column, MoSCoW priorities, an ungoverned D-nn deferred register, the
`generated` manifest spelling, a parenthetical profile, mixed promoted-to
tokens, and template/TODO text inside code spans.

Each test pins one seeded quirk to its mapping. The conservation meta-test is
the class fix for RC2: it catches the NEXT unknown allowlist fall-through, not
just the known ones.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))

import migrate  # noqa: E402
import store  # noqa: E402

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "dialect-package"


def _digest(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


class DialectMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._before = _digest(FIXTURE)
        cls._dest = tempfile.TemporaryDirectory()
        cls.out = migrate.run_migration(str(FIXTURE), cls._dest.name,
                                        name="dialect", confirm=True)
        assert cls.out["ok"], cls.out
        cls.conn = store.load(Path(cls._dest.name) / "dialect" / "data")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls._dest.cleanup()

    def _one(self, sql: str):
        return self.conn.execute(sql).fetchone()

    def test_migration_clean_and_source_untouched(self):
        self.assertEqual(self.out["fidelity"]["identifier_gaps"], [])
        self.assertEqual(self.out["preview"]["zero_families"], [])
        self.assertEqual(self.out["fidelity"]["gate_failures"], {})
        self.assertEqual(self._before, _digest(FIXTURE))  # read-only source

    def test_madr_adr_without_front_matter_migrates(self):
        row = self._one("SELECT lifecycle_status, decision FROM adrs"
                        " WHERE id = 'ADR-0002'")
        self.assertIsNotNone(row, "MADR ADR lost (B1 regression)")
        self.assertEqual(row[0], "Approved")               # '- Status: Accepted' bullet
        self.assertIn("flush them hourly", row[1])         # Decision OUTCOME...
        self.assertNotIn("latency must not pay", row[1])   # ...never the Drivers (D4)

    def test_gwt_statements_survive_uncapped(self):
        for stmt, title in self.conn.execute(
                "SELECT statement, title FROM acceptance_criteria"):
            self.assertGreater(len(stmt), 120, "AC statement truncated (B4 regression)")
            self.assertLessEqual(len(title), 120)

    def test_test_ref_column_is_evidence(self):
        for evidence, attrs in self.conn.execute(
                "SELECT evidence, custom_attributes FROM audit_verdicts"):
            self.assertIn("tests/test_", evidence or "",
                          "audit verdict narrated (B5 regression)")
            self.assertIn("Notes", attrs or "")            # remaining columns preserved

    def test_moscow_priorities_set_mvp(self):
        # 3 FRs via MoSCoW (M / Must / M) + NFR-001 via the literal "MVP" scope cell —
        # both dialect paths must set the flag.
        self.assertEqual(self._one("SELECT COUNT(*) FROM requirements"
                                   " WHERE mvp = 1")[0], 4,
                         "MoSCoW M/Must not mapped — G-TRACE would pass vacuously (C1)")

    def test_deferred_register_maps_dnn_rows(self):
        rows = {r[0]: r[1] for r in self.conn.execute(
            "SELECT id, severity FROM deferred_work")}
        self.assertEqual(len(rows), 3, "D-nn register dropped (B3 regression)")
        self.assertEqual(rows["DW-001"], "high")
        self.assertEqual(rows["DW-003"], "medium")         # off-enum word normalized

    def test_promoted_to_mixed_tokens(self):
        rows = dict(self.conn.execute("SELECT id, promoted_to FROM decisions"))
        self.assertEqual(rows["DEC-004"], "ADR-0002")      # ADR wins over the DEC token
        self.assertIsNone(rows["DEC-005"])                 # DEC-only cell -> NULL, no crash

    def test_manifest_dialect_absorbed(self):
        created, attrs = self._one("SELECT created_at, custom_attributes FROM packages")
        self.assertEqual(created, "2026-06-17")            # `generated` spelling
        self.assertIn("software-platform", attrs)          # raw profile preserved

    def test_prose_only_file_caught(self):
        titles = [t for (t,) in self.conn.execute(
            "SELECT title FROM narrative_documents WHERE doc_kind = 'other'")]
        self.assertTrue(any("Context notes" in t for t in titles),
                        "prose-only file dropped (catch-all regression)")
        body = self._one("SELECT body FROM document_sections WHERE body LIKE"
                         " '%link_count%'")
        self.assertIsNotNone(body)                         # template text survives verbatim

    def test_preview_ledger_ergonomics(self):
        """Plan 019 (C21): grouped ledgers + status_defaulted + basis annotation."""
        preview = self.out["preview"]
        self.assertEqual(preview["status_coerced_basis"], "defaults")
        defaulted = {(e["file"], e["family"]): e for e in preview["status_defaulted"]}
        entry = defaulted[("planning/roadmap.md", "PH")]   # roadmap table has no Status
        self.assertEqual(entry["defaulted_to"], "Approved")
        for group in preview["status_coerced_groups"]:
            self.assertIn("original", group)
            self.assertIn("proposed", group)
            self.assertGreaterEqual(group["count"], 1)
        for group in preview["title_fallbacks"]:
            self.assertIn("family", group)

    def test_conservation_every_md_file_accounted(self):
        preview = self.out["preview"]
        covered = set(preview["partial_files"]) | set(preview["skipped_files"])
        for (attrs,) in self.conn.execute(
                "SELECT custom_attributes FROM narrative_documents"):
            path = (json.loads(attrs or "{}").get("v1") or {}).get("path")
            if path:
                covered.add(path)
        routed_prefixes = ("adrs/", "experiments/", "pocs/")  # per-file row mappers
        for pf in migrate.vp.load_package(FIXTURE):
            rel = pf.rel.replace("\\", "/")
            if not rel.endswith(".md") or pf.is_json:
                continue
            if migrate.vp.is_template_path(pf.rel, Path(pf.rel).name):
                continue
            if rel.startswith(routed_prefixes) or "/diagrams/" in rel:
                continue
            self.assertIn(rel, covered,
                          f"{rel}: not accounted anywhere — silent loss (RC2)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
