"""Tests for the deterministic eval runner + assertion primitives (plan 013/B10).

Drives run_evals.py and pkg_check.py as subprocesses (their real contract is exit
codes + printed output): PASS on the shipped sample fixture, FAIL (non-zero) on a
deliberately broken copy, visible SKIP for unrecorded cases, and non-zero when
nothing at all was checked.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "evals" / "run_evals.py"
PKG_CHECK = REPO_ROOT / "evals" / "pkg_check.py"
SAMPLE = REPO_ROOT / "evals" / "sample-results"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=REPO_ROOT,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class EvalRunnerTest(unittest.TestCase):
    def test_sample_fixture_passes(self):
        proc = run(str(RUNNER), "--results-dir", str(SAMPLE))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS  minimal-brief", proc.stdout)
        self.assertIn("retired", proc.stdout)          # retired assertions stay visible
        self.assertIn("SKIP  rich-brief", proc.stdout)  # unrecorded cases skip loudly

    def test_broken_sample_fails_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "results"
            shutil.copytree(SAMPLE, broken)
            (broken / "minimal-brief" / "package" / "review.html").unlink()
            proc = run(str(RUNNER), "--results-dir", str(broken))
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("FAIL  minimal-brief", proc.stdout)
            self.assertIn("review.html", proc.stdout)   # the failing command is echoed

    def test_empty_results_dir_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(str(RUNNER), "--results-dir", tmp)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("nothing was checked", proc.stdout)

    def test_case_filter(self):
        proc = run(str(RUNNER), "--results-dir", str(SAMPLE), "--case", "minimal-brief")
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("rich-brief", proc.stdout)

    # ---------------------------------------------------------- pkg_check bounds

    def test_pkg_check_count_bounds(self):
        pkg = str(SAMPLE / "minimal-brief" / "package")
        self.assertEqual(run(str(PKG_CHECK), "count", pkg, "requirement",
                             "--min", "4").returncode, 0)
        proc = run(str(PKG_CHECK), "count", pkg, "requirement", "--min", "99")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("below required minimum", proc.stdout)
        self.assertEqual(run(str(PKG_CHECK), "count", pkg, "decision",
                             "--col", "lifecycle_status=Rejected", "--max", "0").returncode, 0)

    def test_pkg_check_grep_and_nonempty(self):
        pkg = str(SAMPLE / "minimal-brief" / "package")
        self.assertEqual(run(str(PKG_CHECK), "grep-absent", pkg,
                             "attacker@example.com").returncode, 0)
        self.assertEqual(run(str(PKG_CHECK), "grep-present", pkg, "FR-001",
                             "--tables", "requirements").returncode, 0)
        self.assertEqual(run(str(PKG_CHECK), "grep-present", pkg,
                             "no-such-string-anywhere").returncode, 1)
        self.assertEqual(run(str(PKG_CHECK), "nonempty", pkg, "assumption",
                             "risk_if_wrong").returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
