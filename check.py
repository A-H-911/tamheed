#!/usr/bin/env python3
"""The one-command deterministic gate (plan 013/B10) — stdlib only.

CI job 1 runs exactly `python check.py`, so local and CI cannot drift. Gates run
in order and stop at the first failure with the failing command echoed:

  suites    — every unit/contract suite under tests/
  goldens   — the frozen v1 validator against its four golden packages (0/0/1/1)
  lint      — every tracked *.json parses; the v2 entity_types registry, the
              entity-type->table map, and the DDL agree; the frozen v1 Always
              mirror (required-artifacts.json) stays in sync with the artifact
              catalog while v1 artifacts remain
  canonical — load+dump of the committed v2 demo package is byte-identical
              (the guard against W-V2-5 git churn)
  evals     — the deterministic eval runner passes on the shipped sample fixture

`python check.py <gate> [<gate> ...]` runs a subset. New suites register in
SUITES here, nowhere else.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent

SUITES = [
    "tests/test_validate_package.py",
    "tests/test_db_roundtrip.py",
    "tests/test_mcp_contract.py",
    "tests/test_migration_golden.py",
    "tests/test_adopt_sample.py",
    "tests/test_export_html.py",
    "tests/test_eval_runner.py",
]

V1_VALIDATOR = "plugins/tamheed/scripts/validate_package.py"
V1_GOLDENS = [  # (package, expected exit) — the frozen migration contract
    ("tests/fixtures/valid-package", 0),
    ("generated-samples/support-triage-agent", 0),
    ("tests/fixtures/invalid-package", 1),
    ("tests/fixtures/incomplete-package", 1),
]

V2_DEMO_DATA = REPO / "generated-samples" / "support-triage-agent-v2" / "data"


def fail(reason: str, cmd: list[str] | None = None) -> None:
    print(f"\nCHECK FAILED: {reason}")
    if cmd:
        print(f"reproduce: {' '.join(cmd)}")
    sys.exit(1)


def run(args: list[str], expected: int = 0) -> None:
    cmd = [sys.executable, *args]
    print(f"$ python {' '.join(args)}", flush=True)
    code = subprocess.run(cmd, cwd=REPO).returncode
    if code != expected:
        fail(f"exit {code}, expected {expected}", cmd)


# ------------------------------------------------------------------ gates

def gate_suites() -> None:
    for suite in SUITES:
        run([suite])


def gate_goldens() -> None:
    for package, expected in V1_GOLDENS:
        run([V1_VALIDATOR, package], expected=expected)


def gate_lint() -> None:
    # 1) every tracked *.json parses
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--", "*.json"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
        tracked = [p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        tracked = [str(p.relative_to(REPO)) for p in REPO.rglob("*.json")
                   if ".git" not in p.parts]
    for rel in tracked:
        try:
            json.loads((REPO / rel).read_text(encoding="utf-8"))
        except ValueError as exc:
            fail(f"unparseable JSON: {rel}: {exc}")
    print(f"lint: {len(tracked)} tracked JSON file(s) parse")

    # 2) v2 sync: entity_types registry rows <-> entity-type->table map <-> DDL
    sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
    sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
    import store  # noqa: PLC0415
    import tamheed_server as srv  # noqa: PLC0415
    registry = {row[0] for row in srv.BASELINE_ENTITY_TYPES}
    mapped = set(srv.ENTITY_TABLES) - {"trace-edge", "omission"}  # write-only surfaces
    if registry != mapped:
        fail("entity_types registry <-> ENTITY_TABLES drift: "
             f"registry-only={sorted(registry - mapped)}, map-only={sorted(mapped - registry)}")
    conn = store.connect()
    ddl_tables = {name for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    conn.close()
    missing = set(srv.ENTITY_TABLES.values()) - ddl_tables
    if missing:
        fail(f"ENTITY_TABLES names tables absent from schema.sql: {sorted(missing)}")
    print(f"lint: v2 registry ({len(registry)} types) <-> table map <-> DDL in sync")

    # 3) v1 sync (while v1 artifacts remain): every Always mirror entry's match
    #    paths appear in the artifact catalog — the two files must move together.
    refs = REPO / "plugins" / "tamheed" / "references"
    mirror = json.loads((refs / "required-artifacts.json").read_text(encoding="utf-8"))
    catalog = (refs / "artifact-catalog.md").read_text(encoding="utf-8")
    stale = [entry["id"] for entry in mirror["always"]
             if not any(path in catalog for path in entry["match"])]
    if stale:
        fail(f"required-artifacts.json entries missing from artifact-catalog.md: {stale}")
    print(f"lint: v1 Always mirror ({len(mirror['always'])} entries) <-> artifact catalog in sync")


def gate_canonical() -> None:
    sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
    import store  # noqa: PLC0415
    conn = store.load(V2_DEMO_DATA)
    with tempfile.TemporaryDirectory() as tmp:
        store.dump(conn, tmp)
        dumped = {p.name: p.read_bytes() for p in Path(tmp).glob("*.jsonl")}
    conn.close()
    committed = {p.name: p.read_bytes() for p in V2_DEMO_DATA.glob("*.jsonl")}
    if set(dumped) != set(committed):
        fail("canonical round-trip changed the demo's file set: "
             f"only-dumped={sorted(set(dumped) - set(committed))}, "
             f"only-committed={sorted(set(committed) - set(dumped))}")
    dirty = sorted(name for name in committed if dumped[name] != committed[name])
    if dirty:
        fail(f"demo package is not in canonical form (load+dump differs): {dirty}")
    print(f"canonical: {len(committed)} demo JSONL file(s) byte-identical after round-trip")


def gate_evals() -> None:
    run(["evals/run_evals.py", "--results-dir", "evals/sample-results"])


GATES = [
    ("suites", gate_suites),
    ("goldens", gate_goldens),
    ("lint", gate_lint),
    ("canonical", gate_canonical),
    ("evals", gate_evals),
]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # UTF-8 output on legacy Windows code pages
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    wanted = list(argv if argv is not None else sys.argv[1:])
    names = [name for name, _ in GATES]
    if unknown := set(wanted) - set(names):
        print(f"unknown gate(s) {sorted(unknown)} — choose from: {', '.join(names)}")
        return 2
    for name, gate in GATES:
        if wanted and name not in wanted:
            continue
        print(f"\n=== gate: {name} ===")
        gate()
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
