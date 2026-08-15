#!/usr/bin/env python3
"""The one-command deterministic gate (plan 013/B10; re-based for v4 by plan 031) —
stdlib only.

CI job 1 runs exactly `python check.py`, so local and CI cannot drift. Gates run
in order and stop at the first failure with the failing command echoed:

  suites    — every unit/contract suite under tests/
  lint      — every tracked *.json parses; the entity_types registry, the
              entity-type->table map, and the DDL agree; the registry's Always
              class stays in sync with the artifact catalog; version/CHANGELOG/
              README/migration/pin invariants hold
  canonical — load+dump of the committed v4 demo package is byte-identical
              (the guard against W-V2-5 git churn)
  evals     — the deterministic eval runner passes on the shipped sample fixture

The v1 validator + goldens gate was retired with v1 ingestion (plan 031): old
Keystone markdown packages migrate under tamheed 3.2.1 first, then v3→v4.

`python check.py <gate> [<gate> ...]` runs a subset. New suites register in
SUITES here, nowhere else.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent

SUITES = [
    "tests/test_db_roundtrip.py",
    "tests/test_store_migrations.py",
    "tests/test_mcp_contract.py",
    "tests/test_migrate_v3to4.py",
    "tests/test_adopt_sample.py",
    "tests/test_export_html.py",
    "tests/test_eval_runner.py",
    "tests/test_scratch_diff.py",
]

V4_DEMO_DATA = REPO / "generated-samples" / "support-triage-agent-v2" / "data"


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
        fail(f"ENTITY_TABLES names tables absent from the DDL: {sorted(missing)}")
    db_dir = REPO / "plugins" / "tamheed" / "db"
    if (db_dir / "schema.sql").read_bytes() != (db_dir / "migrations" / "001_init.sql").read_bytes():
        fail("schema.sql is no longer byte-identical to migrations/001_init.sql — "
             "new DDL goes in an append-only migrations/NNN >= 002, never in either twin")
    print(f"lint: v2 registry ({len(registry)} types) <-> table map <-> DDL in sync;"
          " schema.sql == 001_init.sql")

    # 3) Always-class sync (plan 031, replacing the retired v1 mirror lint): every
    #    Always type in the live registry (BASELINE_ENTITY_TYPES — what G-SET
    #    enforces) must be named in the artifact catalog — the enforcing surface and
    #    the teaching surface move together.
    refs = REPO / "plugins" / "tamheed" / "references"
    catalog = (refs / "artifact-catalog.md").read_text(encoding="utf-8")
    always = [tid for tid, _, _, gclass in srv.BASELINE_ENTITY_TYPES
              if gclass == "Always"]
    stale = [tid for tid in always if tid not in catalog]
    if stale:
        fail(f"Always entity types missing from artifact-catalog.md: {stale}")
    print(f"lint: registry Always class ({len(always)} types) <-> artifact catalog in sync")

    # 4) version sync (plan 017/C16): the version string that travels with the installed
    #    bundle IS the version as far as every user and field report is concerned — it must
    #    match the newest CHANGELOG release heading (the v2.0.0 release shipped with
    #    plugin.json still saying 1.0.0; this makes that skew structurally impossible).
    plugin_ver = json.loads(
        (REPO / "plugins" / "tamheed" / ".claude-plugin" / "plugin.json")
        .read_text(encoding="utf-8"))["version"]
    heading = re.search(r"^## \[(\d+\.\d+\.\d+)\]",
                        (REPO / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    newest = heading.group(1) if heading else None
    if plugin_ver != newest:
        fail(f"version skew: plugin.json={plugin_ver} vs newest CHANGELOG release={newest}"
             " — bump both together (plan 017 W8)")
    print(f"lint: plugin.json {plugin_ver} == newest CHANGELOG release")

    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")

    # 5) CHANGELOG ordering (plan 027): lint 4 trusts the FIRST heading to be the
    #    newest — that trust was never checked. Releases must be strictly descending.
    versions = [tuple(int(p) for p in m.groups()) for m in
                re.finditer(r"^## \[(\d+)\.(\d+)\.(\d+)\]", changelog, re.M)]
    for newer, older in zip(versions, versions[1:]):
        if newer <= older:
            fail("CHANGELOG releases not newest-first: "
                 f"{'.'.join(map(str, newer))} appears above {'.'.join(map(str, older))}")
    print(f"lint: CHANGELOG {len(versions)} releases strictly newest-first")

    # 6) the MCP SDK pin (plan 027, guards C33): SDK 2.0.0 removed mcp.server.fastmcp
    #    and the unbounded dep broke every fresh resolve — the bound must never widen
    #    silently (the deliberate mcpserver port is the only sanctioned path).
    server_head = "\n".join(
        (REPO / "plugins" / "tamheed" / "server" / "tamheed_server.py")
        .read_text(encoding="utf-8").splitlines()[:15])
    if not re.search(r'dependencies = \["mcp>=[0-9.]+,<2"\]', server_head):
        fail("PEP 723 mcp pin missing or widened in tamheed_server.py — this build"
             " requires mcp<2 (C33); port serve() to mcp.server.mcpserver before"
             " touching the bound")
    print("lint: PEP 723 mcp pin bounded (<2)")

    # 7) migrations are announced (plan 027): every shipped schema migration must be
    #    named somewhere in the CHANGELOG — a migration without a release note is how
    #    an operator meets a schema change unwarned.
    unannounced = sorted(
        p.name for p in
        (REPO / "plugins" / "tamheed" / "db" / "migrations").glob("[0-9]*.sql")
        if p.name != "001_init.sql" and p.name not in changelog)
    if unannounced:
        fail(f"schema migration(s) never mentioned in CHANGELOG.md: {unannounced}")
    print("lint: every migration (002+) is named in the CHANGELOG")

    # 8) README freshness (plan 030, maintainer contract): the documentation READMEs
    #    are updated with EVERY release — each must carry the current version string,
    #    so a release that skips one fails the gate (the version-sync-lint precedent).
    for rel in ("README.md", "plugins/tamheed/server/README.md",
                "plugins/tamheed/prompts/README.md", "plugins/tamheed/SKILL.md",
                "plugins/tamheed/references/artifact-catalog.md"):
        if plugin_ver not in (REPO / rel).read_text(encoding="utf-8"):
            fail(f"{rel} does not mention the current version {plugin_ver} — the"
                 " READMEs are updated with every release (plan 030)")
    print(f"lint: all 5 version-stamped surfaces carry v{plugin_ver}")

    # 9) the teaching surface (plan 032): prompts/templates may only teach vocabulary
    #    the engine has, and the stock history must be CURRENT — a release that
    #    changes a stock prompt without appending its body cannot ship.
    prompts_dir = REPO / "plugins" / "tamheed" / "prompts"
    history = json.loads((prompts_dir / "stock-history.json").read_text(encoding="utf-8"))
    stale_hist = [p.name for p in sorted(prompts_dir.glob("*.md"))
                  if p.read_text(encoding="utf-8")
                  not in history.get(p.name, {}).values()]
    if stale_hist:
        fail(f"stock-history.json is missing the CURRENT body of: {stale_hist} — "
             "append each changed stock prompt's body under the release version"
             " (plan 032: the history is what makes divergence classifiable)")
    print(f"lint: stock history current ({len(history)} files,"
          f" {sum(len(v) for v in history.values())} bodies)")

    # Plan 033: the teaching surface is the WHOLE bundle prose — every references
    # file and every template, not just prompts + 4 templates (the unlinted zone is
    # where the v4 audit found all the rot).
    teaching = {f"prompts/{p.name}": (REPO / "plugins" / "tamheed" / "prompts" / p.name)
                .read_text(encoding="utf-8")
                for p in sorted(prompts_dir.glob("*.md"))}
    for p in sorted((REPO / "plugins" / "tamheed" / "templates").glob("*.md")):
        teaching[f"templates/{p.name}"] = p.read_text(encoding="utf-8")
    for p in sorted(refs.glob("*.md")):
        teaching[f"references/{p.name}"] = p.read_text(encoding="utf-8")
    teaching["SKILL.md"] = (REPO / "plugins" / "tamheed" / "SKILL.md")\
        .read_text(encoding="utf-8")
    relations = set(srv.RELATION_RULES) | {"relates_to"}
    # The gate rosters form a CLOSED TRIANGLE with references/quality-gates.md
    # (plan 033): mechanical (engine GATE_NAMES) + judgment + warn tiers; every
    # roster name must appear in the doc, and every G-* token in the doc must be in
    # a roster tier — a gate added to either side alone fails the release.
    judgment_gates = {"G-INJECT", "G-CONFLICT", "G-EXEC", "G-HANDOFF", "G-OQ"}
    warn_gates = {"G-ASM-VISIBLE", "G-CLAIM", "G-RISK", "G-COUPLING", "G-BLOAT",
                  "G-CMD-THIN"}
    qg = (refs / "quality-gates.md").read_text(encoding="utf-8")
    if missing_qg := sorted(g for g in (judgment_gates | warn_gates) if g not in qg):
        fail(f"gate(s) {missing_qg} in the lint roster but not defined in"
             " references/quality-gates.md — the rosters and the gate doc move together")
    allowed_gates = set(srv.GATE_NAMES) | judgment_gates | warn_gates
    if undoc := sorted(t for t in set(re.findall(r"\bG-[A-Z][A-Z-]+\b", qg))
                       if t.rstrip("-") not in allowed_gates):
        fail(f"quality-gates.md defines gate(s) {undoc} that are in NO roster tier —"
             " add to GATE_NAMES / judgment / warn deliberately, never by prose alone")
    # (name, scope) — 'all' = every teaching file; 'prompts+templates' spares the
    # references, which legitimately DISCUSS retirements; any line explicitly framed
    # as retired/deleted/renamed history is exempt everywhere.
    blacklist = [("binds_to", "all"), ("milestones-reached", "all"),
                 ('"status":', "all"), ("PRM-", "prompts+templates"),
                 ("PASS/FAIL", "prompts")]
    _hist = re.compile(r"retired|deleted|renamed|blacklist|historical", re.I)
    problems = []
    for rel, text in teaching.items():
        for tok in set(re.findall(r"\bG-[A-Z][A-Z-]+\b", text)):
            if tok.rstrip("-") not in allowed_gates:
                problems.append(f"{rel}: unknown gate {tok!r}")
        for line in text.splitlines():
            if "event_type" in line:
                for tok in re.findall(r"[\"'`]([a-z][a-z-]+)[\"'`]", line):
                    if tok in {"event-type", "event_type"}:
                        continue
                    if "-" in tok and tok not in srv.PE_EVENT_TYPES:
                        problems.append(f"{rel}: unknown event_type {tok!r}")
        for tok in set(re.findall(r"`(scope_[a-z_]+)`?", text)):
            if tok not in relations:
                problems.append(f"{rel}: unknown relation {tok!r}")
        for name, scope in blacklist:
            if scope == "prompts" and not rel.startswith("prompts/"):
                continue
            if scope == "prompts+templates" and rel.startswith("references/"):
                continue
            if scope == "prompts+templates" and rel == "SKILL.md":
                continue
            for line in text.splitlines():
                if name in line and not _hist.search(line):
                    problems.append(f"{rel}: retired/wrong vocabulary {name!r}"
                                    f" ({line.strip()[:60]!r})")
                    break
    if problems:
        fail("teaching-surface vocabulary drift (plans 032-033):\n  "
             + "\n  ".join(problems))
    print(f"lint: teaching surface ({len(teaching)} files) speaks only engine vocabulary")

    # 10) dead references (plan 033): every relative markdown link and backticked
    #     path token in the NON-TEMPLATE bundle prose must resolve. templates/ and
    #     prompts/ are excluded — their paths describe the GENERATED package
    #     (intentional output content, per CLAUDE.md) — and so is
    #     references/generated-structure.md, which describes that same tree.
    link_files = {f"references/{p.name}": p for p in sorted(refs.glob("*.md"))
                  if p.name != "generated-structure.md"}
    link_files["SKILL.md"] = REPO / "plugins" / "tamheed" / "SKILL.md"
    link_files["server/README.md"] = REPO / "plugins" / "tamheed" / "server" / "README.md"
    link_files["db/CANONICAL.md"] = REPO / "plugins" / "tamheed" / "db" / "CANONICAL.md"
    path_token = re.compile(
        r"\]\(([^)#\s]+?)\)|`([A-Za-z0-9_./-]+/[A-Za-z0-9_.-]+\.(?:md|json|sql|py))`")
    dead = []
    for rel, path in link_files.items():
        base = path.parent
        for m in path_token.finditer(path.read_text(encoding="utf-8")):
            target = (m.group(1) or m.group(2) or "").split("#")[0]
            if (not target or target.startswith(("http", "mailto:"))
                    or "<" in target or "{" in target or "*" in target
                    or target.startswith("data/")):
                continue
            bundle = REPO / "plugins" / "tamheed"  # bundle-relative refs are legal in-bundle
            if not ((base / target).exists() or (REPO / target).exists()
                    or (bundle / target).exists()):
                dead.append(f"{rel}: {target}")
    if dead:
        fail("dead path references in bundle prose (plan 033):\n  " + "\n  ".join(dead))
    print(f"lint: no dead path references across {len(link_files)} bundle prose files")

    # 11) the necessary template copies stay synced (plan 033): generated packages
    #     cannot link back into the bundle, so these templates CARRY governance
    #     content — and must carry it correctly.
    gov = (refs / "governance.md").read_text(encoding="utf-8")
    gov_rows = {(m.group(1).strip(), m.group(2).strip()) for m in re.finditer(
        r"^\| ([^|]+) \| (`[^`]+`[^|]*) \| [a-z_ /()+-]+ \|$", gov, re.M)}
    naming = (REPO / "plugins" / "tamheed" / "templates" /
              "naming-conventions.template.md").read_text(encoding="utf-8")
    missing_rows = sorted(fmt for _e, fmt in gov_rows
                          if fmt.split("`")[1] not in naming)
    if missing_rows:
        fail(f"naming-conventions.template.md is missing governance identifier"
             f" format(s): {missing_rows} — the template is a necessary copy and"
             " moves with references/governance.md")
    gov_tpl = (REPO / "plugins" / "tamheed" / "templates" /
               "governance.template.md").read_text(encoding="utf-8")
    for needle in ("Implemented", "Review", "scope_adds", "relates_to"):
        if needle not in gov_tpl:
            fail(f"governance.template.md lacks {needle!r} — the template is a"
                 " necessary copy and moves with references/governance.md")
    print("lint: template governance copies in sync")


def gate_canonical() -> None:
    sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
    import store  # noqa: PLC0415
    conn = store.load(V4_DEMO_DATA)
    with tempfile.TemporaryDirectory() as tmp:
        store.dump(conn, tmp)
        dumped = {p.name: p.read_bytes() for p in Path(tmp).glob("*.jsonl")}
    conn.close()
    committed = {p.name: p.read_bytes() for p in V4_DEMO_DATA.glob("*.jsonl")}
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
