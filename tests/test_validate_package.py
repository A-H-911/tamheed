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
# The validator now lives inside the self-contained plugin bundle.
SCRIPTS = HERE.parent / "plugins" / "keystone" / "scripts"
VALIDATOR = SCRIPTS / "validate_package.py"
VALID_PKG = HERE / "fixtures" / "valid-package"
INVALID_PKG = HERE / "fixtures" / "invalid-package"
INCOMPLETE_PKG = HERE / "fixtures" / "incomplete-package"

# Make the validator importable regardless of cwd.
sys.path.insert(0, str(SCRIPTS))
import validate_package as vp  # noqa: E402
import init_skill_repo as isr  # noqa: E402


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
        # The seven mechanical gates should all have found inputs to check (the
        # valid fixture now ships an acceptance audit, so G-PROGRESS runs too), so
        # a silently-empty fixture can't masquerade as 'passing'.
        for gate in ("G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-COMPLETE", "G-TRACE", "G-SET", "G-PROGRESS"):
            g = next(x for x in self.summary["gates"] if x["gate"] == gate)
            self.assertTrue(g["checked"], msg=f"{gate} had no inputs in the valid fixture")

    def test_progress_passes(self):
        g = next(x for x in self.summary["gates"] if x["gate"] == "G-PROGRESS")
        self.assertTrue(g["checked"], msg="G-PROGRESS should run (valid fixture has an acceptance audit)")
        self.assertTrue(g["passed"], msg=f"G-PROGRESS should pass on the valid fixture; findings: {g['findings']}")

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

    def test_all_gates_failed(self):
        # invalid-package seeds a defect for every critical gate, carries no
        # manifest (so G-SET fails), and ships an acceptance audit missing AC-003
        # (so G-PROGRESS fails on the coverage gap).
        failed = set(self.summary["critical_failed"])
        for gate in ("G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-COMPLETE", "G-TRACE", "G-SET", "G-PROGRESS"):
            self.assertIn(gate, failed, msg=f"{gate} should have failed; failed={failed}")

    def test_progress_defect_detected(self):
        msgs = all_messages(self.summary, "G-PROGRESS")
        self.assertIn("AC-003", msgs, msg=f"G-PROGRESS findings:\n{msgs}")

    def test_cli_exit_one(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(INVALID_PKG)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout + proc.stderr)
        self.assertIn("NOT READY", proc.stdout)


class IncompletePackage(unittest.TestCase):
    """Regression for audit finding F-01: a package whose internals are each
    individually valid but that is missing a required 'Always' artifact (here the
    traceability matrix) must NOT be reported ready. Before G-SET this passed with
    exit 0 because the absent matrix made G-TRACE SKIP rather than FAIL."""

    @classmethod
    def setUpClass(cls):
        cls.results = vp.run_gates(INCOMPLETE_PKG)
        cls.summary = vp.build_summary(INCOMPLETE_PKG, cls.results)

    def test_overall_not_ok(self):
        self.assertFalse(
            self.summary["ok"],
            msg="a package missing a required artifact must not be reported ready",
        )

    def test_only_set_gate_failed(self):
        # The internals are valid; the sole critical failure must be G-SET.
        self.assertEqual(
            set(self.summary["critical_failed"]),
            {"G-SET"},
            msg=f"expected only G-SET to fail; got {self.summary['critical_failed']}",
        )

    def test_progress_skipped(self):
        # incomplete-package has acceptance criteria but no acceptance audit, so
        # the SKIP-safe G-PROGRESS must not run (checked == False) and must not
        # appear among the critical failures.
        g = next(x for x in self.summary["gates"] if x["gate"] == "G-PROGRESS")
        self.assertFalse(g["checked"], msg="G-PROGRESS should SKIP when no audit is present")
        self.assertNotIn("G-PROGRESS", self.summary["critical_failed"])

    def test_set_finding_names_the_missing_matrix(self):
        msgs = all_messages(self.summary, "G-SET")
        self.assertIn("traceability-matrix", msgs.lower(), msg=f"G-SET findings:\n{msgs}")

    def test_cli_exit_one(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(INCOMPLETE_PKG)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout + proc.stderr)
        self.assertIn("NOT READY", proc.stdout)


class ScriptSafety(unittest.TestCase):
    """Audit P2 (F-04 / F-09): the bundled scripts must not be exploitable."""

    def test_no_shell_true_in_scripts(self):
        for script in (VALIDATOR, SCRIPTS / "init_skill_repo.py"):
            src = script.read_text(encoding="utf-8")
            self.assertNotIn(
                "shell=True", src, msg=f"{script.name} must not use shell=True (CWE-78)"
            )

    def test_repo_name_rejects_traversal(self):
        for bad in ("../../evil", "..", ".", "a/b", "a\\b", "", "with space"):
            self.assertIsNotNone(
                isr.validate_repo_name(bad), msg=f"{bad!r} should be rejected"
            )

    def test_repo_name_accepts_simple(self):
        for good in ("keystone", "my-skill", "my_skill", "Repo.2", "a"):
            self.assertIsNone(
                isr.validate_repo_name(good), msg=f"{good!r} should be accepted"
            )

    def test_resolve_target_stays_inside_parent(self):
        import argparse
        import tempfile

        parent = tempfile.mkdtemp()
        ns = argparse.Namespace(target_dir=parent, repo_name="safe-name")
        target = isr.resolve_target(ns)
        self.assertEqual(Path(target).parent, Path(parent).resolve())


class ScaffoldLayout(unittest.TestCase):
    """Audit P5 (F-08): the bootstrapper emits an installable plugin bundle by default,
    and the classic layout still works."""

    def _plan_paths(self, layout):
        import argparse

        target = Path("/__plan__")  # plan_actions is pure; nothing is written
        ns = argparse.Namespace(repo_name="demo", owner="acme", license="MIT", layout=layout)
        actions = isr.plan_actions(target, ns)
        return {
            str(a.path.relative_to(target)).replace("\\", "/")
            for a in actions
            if a.path != target
        }

    def test_plugin_layout_is_installable(self):
        paths = self._plan_paths("plugin")
        for needed in (
            ".claude-plugin/marketplace.json",
            "plugins/demo/.claude-plugin/plugin.json",
            "plugins/demo/SKILL.md",
        ):
            self.assertIn(needed, paths, msg=f"plugin layout missing {needed}")
        tops = {p.split("/")[0] for p in paths}
        self.assertNotIn("commands", tops, msg="plugin layout should not scaffold commands/")

    def test_classic_layout_has_skill_and_commands(self):
        paths = self._plan_paths("classic")
        tops = {p.split("/")[0] for p in paths}
        self.assertIn("skill", tops)
        self.assertIn("commands", tops)
        self.assertNotIn(".claude-plugin/marketplace.json", paths)

    def test_emits_agent_control_surface(self):
        # The ambient control surface — CLAUDE.md (the loaded entry) importing AGENTS.md —
        # is emitted at the repo root in BOTH layouts.
        for layout in ("plugin", "classic"):
            paths = self._plan_paths(layout)
            self.assertIn("AGENTS.md", paths, msg=f"{layout}: AGENTS.md (control surface) missing")
            self.assertIn("CLAUDE.md", paths, msg=f"{layout}: CLAUDE.md shim missing")

    def test_agent_control_surface_content(self):
        agents = isr.agents_md_content("demo")
        self.assertIn("AGENTS.md", agents)
        self.assertIn("ADR", agents)                       # invariants -> ADR rule present
        self.assertIn("acceptance-criteria-first", agents)  # track-as-you-go convention
        # Executor is Claude Code: CLAUDE.md is the loaded entry that IMPORTS AGENTS.md
        # (Anthropic's documented idiom), not an "agent-neutral" canonical/shim pair.
        self.assertIn("Claude Code", agents)
        claude = isr.claude_md_content()
        self.assertIn("@AGENTS.md", claude)                 # CLAUDE.md imports AGENTS.md
        self.assertIn("Claude Code auto-loads", claude)     # CLAUDE.md is the loaded entry
        for content in (agents, claude):
            self.assertNotIn("agent-neutral", content)      # no regression to the neutral framing


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


import os as _os  # noqa: E402
import shutil as _shutil  # noqa: E402
import tempfile as _tempfile  # noqa: E402
from unittest import mock as _mock  # noqa: E402


def _make_pkg(test, files):
    """Create a throwaway package dir with the given {relpath: content} files."""
    d = Path(_tempfile.mkdtemp())
    test.addCleanup(_shutil.rmtree, d, ignore_errors=True)
    for rel, content in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d


def _msgs(result):
    return " | ".join(f.message for f in result.findings)


class ValidatePackageBranches(unittest.TestCase):
    """Direct-API coverage of validator error/finding branches not exercised by the
    valid/invalid fixtures."""

    def test_invalid_json_flagged_by_ids(self):
        pkg = _make_pkg(self, {"keystone-state.json": "{ not valid json "})
        res = vp.gate_ids(vp.load_package(pkg))
        self.assertIn("invalid JSON", _msgs(res))

    def test_duplicate_definition_in_family(self):
        pkg = _make_pkg(self, {
            "requirements/functional.md":
            "| ID | Requirement | Source |\n|---|---|---|\n"
            "| FR-001 | first | brief |\n| FR-001 | dup | brief |\n"
        })
        res = vp.gate_ids(vp.load_package(pkg))
        self.assertIn("duplicate definition", _msgs(res))
        self.assertIn("FR-001", _msgs(res))

    def test_standalone_adr_without_status(self):
        pkg = _make_pkg(self, {
            "adrs/adr-0001-thing.md":
            "# ADR-0001: Thing\n\n## Context\n\nbody\n\n## Decision\n\nbody\n"
        })
        res = vp.gate_dec_status(vp.load_package(pkg))
        self.assertIn("Status", _msgs(res))

    def test_requirements_table_without_source_column(self):
        pkg = _make_pkg(self, {
            "requirements/non-functional.md":
            "| ID | Requirement |\n|---|---|\n| NFR-001 | fast |\n"
        })
        res = vp.gate_req_src(vp.load_package(pkg))
        self.assertIn("Source", _msgs(res))

    def test_empty_artifact_flagged(self):
        pkg = _make_pkg(self, {"00-charter.md": "   \n\n"})
        res = vp.gate_complete(vp.load_package(pkg))
        self.assertIn("empty", _msgs(res).lower())

    def test_json_traceability_gap(self):
        pkg = _make_pkg(self, {
            "validation/traceability-matrix.json":
            json.dumps([{"req": "FR-001", "decisions": "DEC-001",
                         "work_items": "WBS-1", "tests": ""}])
        })
        res = vp.gate_trace(vp.load_package(pkg))
        self.assertIn("FR-001", _msgs(res))
        self.assertIn("test", _msgs(res).lower())

    def test_gate_set_rejects_unreadable_manifest(self):
        pkg = _make_pkg(self, {"manifest.json": "{ broken"})
        res = vp.gate_set(pkg)
        low = _msgs(res).lower()
        self.assertTrue("invalid json" in low or "unreadable" in low, msg=_msgs(res))

    def test_progress_invalid_verdict(self):
        # An out-of-set verdict in the acceptance audit is flagged by G-PROGRESS.
        pkg = _make_pkg(self, {
            "validation/acceptance-criteria.md":
            "| ID | Criterion | Status |\n|---|---|---|\n| AC-001 | x | Approved |\n",
            "validation/acceptance-audit.md":
            "| AC | Criterion | Verdict | Evidence |\n|---|---|---|---|\n| AC-001 | x | Maybe | - |\n",
        })
        res = vp.gate_progress(vp.load_package(pkg))
        self.assertIn("invalid verdict", _msgs(res).lower())
        self.assertIn("AC-001", _msgs(res))

    def test_progress_blank_verdict(self):
        # An empty verdict cell is flagged ("has no verdict").
        pkg = _make_pkg(self, {
            "validation/acceptance-criteria.md":
            "| ID | Criterion | Status |\n|---|---|---|\n| AC-001 | x | Approved |\n",
            "validation/acceptance-audit.md":
            "| AC | Criterion | Verdict | Evidence |\n|---|---|---|---|\n| AC-001 | x |  | - |\n",
        })
        res = vp.gate_progress(vp.load_package(pkg))
        self.assertIn("no verdict", _msgs(res).lower())

    def test_progress_missing_verdict_column(self):
        # An audit table with no Verdict column at all is flagged.
        pkg = _make_pkg(self, {
            "validation/acceptance-criteria.md":
            "| ID | Criterion | Status |\n|---|---|---|\n| AC-001 | x | Approved |\n",
            "validation/acceptance-audit.md":
            "| AC | Criterion | Evidence |\n|---|---|---|\n| AC-001 | x | - |\n",
        })
        res = vp.gate_progress(vp.load_package(pkg))
        self.assertIn("no Verdict column", _msgs(res))


class InitSkillRepoUnits(unittest.TestCase):
    """Pure-function and filesystem-guard coverage for the bootstrapper."""

    def test_license_mit_vs_placeholder(self):
        self.assertIn("MIT License", isr.license_content("MIT", "Acme", 2026))
        placeholder = isr.license_content("Apache-2.0", "Acme", 2026)
        self.assertIn("Apache-2.0", placeholder)
        self.assertIn("SPDX", placeholder)

    def test_plugin_manifest_generators_are_valid_json(self):
        m = json.loads(isr.marketplace_json_content("demo", "acme"))
        p = json.loads(isr.plugin_json_content("demo", "acme", "MIT"))
        self.assertEqual(m["plugins"][0]["source"], "./plugins/demo")
        self.assertEqual(p["name"], "demo")
        self.assertEqual(p["license"], "MIT")

    def test_readme_is_layout_aware(self):
        plug = isr.readme_content("demo", "acme", "plugin")
        classic = isr.readme_content("demo", "acme", "classic")
        self.assertIn("marketplace", plug.lower())
        self.assertIn("plugins/demo/SKILL.md", plug)
        self.assertIn("skill/", classic)

    def test_starter_skill_md_has_name_and_no_outward_refs(self):
        s = isr.starter_skill_md_content("demo")
        self.assertIn("name: demo", s)
        self.assertNotIn("../..", s)

    def test_misc_content_generators_nonempty(self):
        for text in (
            isr.contributing_content("demo"),
            isr.code_of_conduct_content(),
            isr.changelog_content("0.1.0"),
            isr.seed_adr_content(),
            isr.bug_report_template(),
            isr.feature_request_template(),
            isr.pull_request_template(),
        ):
            self.assertTrue(text.strip())

    def test_check_prereqs_reports_missing_git(self):
        with _mock.patch("init_skill_repo.shutil.which", return_value=None):
            problems = isr.check_prereqs(create_remote=False)
        self.assertTrue(any("git" in p for p in problems))

    def test_check_prereqs_reports_missing_gh_when_remote(self):
        def fake_which(name):
            return "/usr/bin/git" if name == "git" else None
        with _mock.patch("init_skill_repo.shutil.which", side_effect=fake_which):
            problems = isr.check_prereqs(create_remote=True)
        self.assertTrue(any("gh" in p for p in problems))

    def test_directory_is_nonempty(self):
        d = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, d, ignore_errors=True)
        self.assertFalse(isr.directory_is_nonempty(d / "missing"))
        self.assertFalse(isr.directory_is_nonempty(d))
        (d / "f.txt").write_text("x", encoding="utf-8")
        self.assertTrue(isr.directory_is_nonempty(d))

    def test_validate_target_blocks_nonempty_non_repo(self):
        d = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, d, ignore_errors=True)
        (d / "stuff.txt").write_text("x", encoding="utf-8")
        problems = isr.validate_target(d, force=False)
        self.assertTrue(problems)
        self.assertEqual(isr.validate_target(d, force=True), [])

    def test_validate_target_rejects_file_in_place_of_dir(self):
        d = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, d, ignore_errors=True)
        f = d / "afile"
        f.write_text("x", encoding="utf-8")
        self.assertTrue(isr.validate_target(f, force=False))

    def test_working_tree_is_dirty_false_on_non_repo(self):
        d = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, d, ignore_errors=True)
        self.assertFalse(isr.working_tree_is_dirty(d))


class InitSkillRepoBootstrap(unittest.TestCase):
    """End-to-end coverage of main(): dry-run writes nothing; a real run scaffolds
    the installable bundle (git identity not required — commit failures are handled).
    main() narrates to stdout/stderr, so calls are wrapped to keep test output clean."""

    @staticmethod
    def _main(argv):
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            return isr.main(argv)

    def test_dry_run_writes_nothing(self):
        parent = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, parent, ignore_errors=True)
        rc = self._main(["--repo-name", "demo", "--owner", "acme",
                         "--target-dir", str(parent), "--dry-run"])
        self.assertEqual(rc, 0)
        # Dry-run must not create the repo directory or any files.
        self.assertFalse((parent / "demo").exists())

    def test_real_bootstrap_creates_plugin_bundle(self):
        parent = Path(_tempfile.mkdtemp())
        self.addCleanup(_shutil.rmtree, parent, ignore_errors=True)
        rc = self._main(["--repo-name", "demo", "--owner", "acme",
                         "--target-dir", str(parent)])
        self.assertEqual(rc, 0)
        repo = parent / "demo"
        for rel in (".claude-plugin/marketplace.json",
                    "plugins/demo/.claude-plugin/plugin.json",
                    "plugins/demo/SKILL.md", "README.md", "LICENSE"):
            self.assertTrue((repo / rel).is_file(), msg=f"missing {rel}")

    def test_bad_repo_name_exits_two(self):
        rc = self._main(["--repo-name", "../escape", "--dry-run"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
