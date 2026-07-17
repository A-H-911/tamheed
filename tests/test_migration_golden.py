"""Migration goldens (plan 010/B5): v1 -> v2 fidelity + refusal routing.

Fidelity criterion (references/migration-v1.md): (a) identifier sets match,
(b) family counts match the manifest's identifier_counts where present — disk wins
over a stale manifest, deltas reported; (c) a v1-passing package passes v2 gates.
"""
import hashlib
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
