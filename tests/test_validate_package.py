#!/usr/bin/env python3
"""Test runner for validate_package.py — stdlib unittest, no pytest needed.

Runs the validator against the two fixtures and asserts:

- ``fixtures/valid-package`` passes (exit 0, no critical findings);
- ``fixtures/invalid-package`` fails (exit 1) and each seeded defect is
  reported by the right gate.

Run directly:

    python tests/test_validate_package.py

It exercises both the importable API (``run_gates`` / ``build_summary``) and
the CLI entry point (subprocess, to verify ``--json`` and exit codes).
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_package.py"
VALID_PKG = HERE / "fixtures" / "valid-package"
INVALID_PKG = HERE / "fixtures" / "invalid-package"

# Make the validator importable regardless of cwd.
sys.path.insert(0, str(HERE))
import validate_package as vp  # noqa: E402


def findings_for(summary: dict, gate: str) -> list:
    for g in summary["gates"]:
        if g["gate"] == gate:
            return g["findings"]
    return []


def all_messages(summary: dict, gate: str) -> str:
    return "\n".join(f["message"] + " " + f["location"] for f in findings_for(summary, gate))


class FixturesExist(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(VALIDATOR.is_file(), f"missing validator at {VALIDATOR}")
        self.assertTrue(VALID_PKG.is_dir(), f"missing valid fixture at {VALID_PKG}")
        self.assertTrue(INVALID_PKG.is_dir(), f"missing invalid fixture at {INVALID_PKG}")


class ValidPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = vp.run_gates(VALID_PKG)
        cls.summary = vp.build_summary(VALID_PKG, cls.results)

    def test_overall_ok(self):
        self.assertTrue(
            self.summary["ok"],
            msg=f"valid package should pass; critical failures: "
            f"{self.summary['critical_failed']}\n"
            + json.dumps(self.summary, indent=2),
        )

    def test_no_critical_failures(self):
        self.assertEqual(self.summary["critical_failed"], [])

    def test_each_critical_gate_passes(self):
        for g in self.summary["gates"]:
            if g["severity"] == "Critical":
                self.assertTrue(
                    g["passed"],
                    msg=f"gate {g['gate']} should pass on the valid fixture; "
                    f"findings: {g['findings']}",
                )

    def test_gates_actually_ran(self):
        # The five mechanical gates should all have found inputs to check, so a
        # silently-empty fixture can't masquerade as 'passing'.
        for gate in ("G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-COMPLETE", "G-TRACE"):
            g = next(x for x in self.summary["gates"] if x["gate"] == gate)
            self.assertTrue(g["checked"], msg=f"{gate} had no inputs in the valid fixture")

    def test_cli_exit_zero(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(VALID_PKG)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("RESULT: OK", proc.stdout)

    def test_cli_json_exit_zero(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(VALID_PKG), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])


class InvalidPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = vp.run_gates(INVALID_PKG)
        cls.summary = vp.build_summary(INVALID_PKG, cls.results)

    def test_overall_not_ok(self):
        self.assertFalse(
            self.summary["ok"],
            msg="invalid package must report critical failures",
        )

    def test_req_src_defect_detected(self):
        msgs = all_messages(self.summary, "G-REQ-SRC")
        self.assertIn("FR-002", msgs, msg=f"G-REQ-SRC findings:\n{msgs}")
        self.assertIn("source", msgs.lower())

    def test_dec_status_defect_detected(self):
        msgs = all_messages(self.summary, "G-DEC-STATUS")
        self.assertIn("DEC-002", msgs, msg=f"G-DEC-STATUS findings:\n{msgs}")

    def test_dangling_reference_detected(self):
        msgs = all_messages(self.summary, "G-IDS")
        self.assertIn("DEC-099", msgs, msg=f"G-IDS findings:\n{msgs}")
        self.assertIn("dangling", msgs.lower())

    def test_malformed_id_detected(self):
        msgs = all_messages(self.summary, "G-IDS")
        self.assertIn("FR-7", msgs, msg=f"G-IDS findings:\n{msgs}")

    def test_complete_defect_detected(self):
        msgs = all_messages(self.summary, "G-COMPLETE")
        low = msgs.lower()
        self.assertTrue(
            "todo" in low or "placeholder" in low,
            msg=f"G-COMPLETE should flag the TODO/placeholder; findings:\n{msgs}",
        )
        self.assertIn("00-charter.md", msgs, msg=f"G-COMPLETE findings:\n{msgs}")

    def test_trace_gap_detected(self):
        msgs = all_messages(self.summary, "G-TRACE")
        self.assertIn("FR-003", msgs, msg=f"G-TRACE findings:\n{msgs}")
        self.assertIn("test", msgs.lower())

    def test_all_five_gates_failed(self):
        failed = set(self.summary["critical_failed"])
        for gate in ("G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-COMPLETE", "G-TRACE"):
            self.assertIn(gate, failed, msg=f"{gate} should have failed; failed={failed}")

    def test_cli_exit_one(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(INVALID_PKG)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout + proc.stderr)
        self.assertIn("NOT READY", proc.stdout)


class CliEdges(unittest.TestCase):
    def test_missing_dir_exit_two(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(HERE / "does-not-exist")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)

    def test_help_works(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("G-IDS", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
