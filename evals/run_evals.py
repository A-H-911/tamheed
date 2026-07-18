"""Deterministic eval runner (plan 013/B10) — stdlib only.

Executes each case's deterministic_assertions from evals.json against a recorded
output directory the operator supplies (--results-dir): every live assertion is a
command (run from the repo root, {case_dir} substituted, a leading 'python'
resolved to the running interpreter) plus an expected-exit / expected-substring
contract. Assertions marked "retired" are echoed with their reason, never graded.
Cases with no recorded output SKIP visibly. Exit 1 on any FAIL — or when nothing
at all was checked. Model-in-the-loop rubric grading stays manual per README.md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _build_cmd(parts: list[str], case_dir: Path) -> list[str]:
    cmd = [p.replace("{case_dir}", str(case_dir)) for p in parts]
    if cmd and cmd[0] == "python":
        cmd[0] = sys.executable
    return cmd


def run_case(case: dict, case_dir: Path) -> bool:
    ok = True
    for assertion in case["deterministic_assertions"]:
        check = assertion["check"]
        if "retired" in assertion:
            print(f"  retired  {check}\n           ({assertion['retired']})")
            continue
        cmd = _build_cmd(assertion["cmd"], case_dir)
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
        output = proc.stdout + proc.stderr
        passed = proc.returncode == assertion.get("expect_exit", 0)
        substring = assertion.get("expect_substring")
        if passed and substring:
            passed = substring in output
        print(f"  {'pass' if passed else 'FAIL'}     {check}")
        if not passed:
            ok = False
            print(f"           $ {' '.join(cmd)}")
            expectation = f"exit {assertion.get('expect_exit', 0)}"
            if substring:
                expectation += f" + substring {substring!r}"
            print(f"           got exit {proc.returncode}, expected {expectation}")
            for line in output.strip().splitlines()[:5]:
                print(f"           | {line}")
    return ok


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # UTF-8 output on legacy Windows code pages
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results-dir", required=True,
                        help="directory holding <case-id>/ recorded outputs")
    parser.add_argument("--spec", default=str(Path(__file__).with_name("evals.json")))
    parser.add_argument("--case", action="append",
                        help="run only this case id (repeatable)")
    args = parser.parse_args(argv)

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    results_dir = Path(args.results_dir).resolve()
    checked, failed, skipped = 0, 0, 0
    for case in spec["cases"]:
        case_id = case["id"]
        if args.case and case_id not in args.case:
            continue
        case_dir = results_dir / case_id
        if not case_dir.is_dir():
            print(f"SKIP  {case_id} — no recorded output at {case_dir}")
            skipped += 1
            continue
        print(f"CASE  {case_id}")
        checked += 1
        if run_case(case, case_dir):
            print(f"PASS  {case_id}")
        else:
            print(f"FAIL  {case_id}")
            failed += 1
    print(f"\n{checked} case(s) checked, {failed} failed, {skipped} skipped")
    if checked == 0:
        print("nothing was checked — supply recorded outputs under --results-dir")
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
