# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Tamheed is **not an application** — it is a reusable, vendor/stack-neutral agent **skill**, packaged
as a **Claude Code plugin**, that turns a project description into an execution-ready planning &
handoff package for *another* agent to implement. The "product" is a methodology spec plus a small
stdlib-only relational package store and MCP server. There is no build step.

This repo is the home of the *capability*, not of any project Tamheed plans. Generated output only
ever lives under `examples/`, `generated-samples/`, and `evals/sample-results/` (curated) — never
elsewhere.

## Layout (v4)

The repository is its own **plugin marketplace**, and the skill is one **self-contained bundle**:

```
.claude-plugin/marketplace.json      # repo = marketplace (one plugin: tamheed)
plugins/tamheed/                     # THE installable bundle — self-contained, copied intact on install
├── .claude-plugin/plugin.json
├── SKILL.md                          # always-loaded front door (owns the capability)
├── references/                       # on-demand depth: artifact-catalog, governance, workflow, entity-guide
├── templates/                        # section templates for narrative prose + prompt patterns
├── db/                               # the store: schema.sql (v4 DDL), migrations/, store.py, CANONICAL.md
├── server/                           # Tamheed MCP server + migrate_v3to4 + adopt + export_html + viewer.css
├── prompts/                          # scenario prompt library, emitted into <package>/prompts/
└── assets/                           # logos
docs/                                 # architecture, methodology, workflow, entities (the v4 study), install
evals/                                # behavioral eval scenarios (skill-level, model-in-the-loop)
lab/                                  # the permanent mock lab project (v4 acceptance harness)
examples/  generated-samples/  tests/ # teaching material, demo package, test suites
.github/workflows/                    # CI (runs exactly `python check.py`) + scheduled eval-spec lint
SECURITY.md                           # trust model, untrusted-content posture, reporting
```

**v1 machinery is gone (plan 031):** no `schemas/`, no `scripts/validate_package.py`, no
`required-artifacts.json`, no markdown-tree importer. A v1 Keystone package migrates under
tamheed 3.2.1 first, then v3→v4 (`docs/migrate-from-keystone.md`).

## Commands

Python 3.9+ for the store/tests (stdlib only); the MCP server needs 3.10+ (ASM-D).

```bash
# THE gate — suites + lints + canonical round-trip + evals (CI runs exactly this)
python check.py                       # subset: python check.py lint

# Individual suites
python tests/test_db_roundtrip.py
python tests/test_mcp_contract.py
python tests/test_migrate_v3to4.py

# MCP server selftest (PEP 723: uv fetches the mcp SDK)
uv run plugins/tamheed/server/tamheed_server.py --selftest
```

> Windows note: `tamheed_server.py` reconfigures stdout/stderr to UTF-8 at startup, so its output
> doesn't raise `UnicodeEncodeError` on legacy code pages such as cp1252.

## Architecture — the governing principle

> **The skill owns the capability; every entry point is a thin wrapper.**

All methodology — the 22 stages, artifact selection, quality gates, readiness, handoff — lives in
`plugins/tamheed/SKILL.md` + its `references/`. External entry points only normalize input, invoke
the skill, and route output. In Claude Code the skill *is* the entry point.

The 22 stages: **Understand** (1–8 intake→scope) → **Explore** (9–15 research→decisions→risk) →
**Plan & hand off** (16–22 execution plan→artifacts→storage→validation→handoff). Authoritative
per-stage spec: `plugins/tamheed/references/workflow.md`.

## Invariants that must stay true

- **Self-contained bundle (mechanically required).** Claude Code copies only the plugin directory on
  install, so everything the skill reads/invokes at runtime must live inside `plugins/tamheed/`
  with **zero** outward (`../..`, repo-root) references. `docs/` may link into the bundle; the
  bundle never links out.
- **Single source of truth** = the bundle: the DDL (`db/schema.sql`) is the single source of data
  shape; the artifact catalog is `references/artifact-catalog.md`; the registry
  (`BASELINE_ENTITY_TYPES`) is the machine mirror of the Always class — `check.py` lints the
  registry ↔ catalog ↔ table-map ↔ DDL sync and the `schema.sql` == `migrations/001_init.sql`
  byte-twin.
- **Identifier scheme** (`plugins/tamheed/references/governance.md`): `FR-`/`NFR-`, `CON-`, `INV-`,
  `ASM-`, `DEP-`, `OQ-`, `DEC-`, `ADR-`, `RISK-`, `HYP-`, `EXP-`, `POC-`, `TEST-`, `KPI-`, `STK-`,
  `PH-`, `MS-`, `SL-`, `WBS-`, `AC-`, `AV-`, `PE-`, `DEF-`, `DW-`, `GATE-`, `EP-`, `CONV-`, `SC-`,
  `WVR-`, `DOC-`/`SEC-`, `DIA-`, `GT-`. Statuses: `Draft → Proposed → Approved / Rejected /
  Superseded / Deferred → Implemented` (+ `Review` = done-claimed, wbs/slices only; `Obsolete`).
  A *proposed* decision is never rendered as *approved*; `Review` never counts as done.
- **A new entity family** = DDL table + `ENTITY_TABLES` + `BASELINE_ENTITY_TYPES` + catalog row +
  governance row (the check.py sync lints catch a partial add).
- **Immutable-after-approval** artifacts (ADRs incl. `confirmation`, approved acceptance criteria)
  are *superseded*, never edited — trigger-enforced.
- **Byte-canonical JSONL** (`db/CANONICAL.md`): an idle open→close produces zero git diff; goldens
  are regenerated by scripts, never hand-edited.
- **Migration is explicit.** `package_open` refuses pre-v4 stores; `package_migrate` is staged
  (preview → operator backs up → confirm; old files kept in `data-v3-backup/`).
- **Extend additively** via `plugins/tamheed/references/extension.md`. Additive = MINOR; changing
  the store shape, the identifier scheme, or the handoff contract = MAJOR + explicit migration.

Note: paths inside `*.template.md` describe the **generated** package structure — intentional
output content, not stale references to this repo's layout.

## The quality gates (gate_run, all mechanical)

`gate_run` on an open package (all blocking except where noted):

- **G-IDS** — foreign_key_check + entity_index⇄tables consistency, verified at gate time.
- **G-DEC-STATUS** — decision statuses in the allowed set (also CHECK-enforced at write).
- **G-REQ-SRC** — every requirement has non-empty provenance (whitespace-only caught).
- **G-COMPLETE** — no unfinished markers; `[NEEDS-CLARIFICATION: OQ-NNN]` legal only while the
  cited OQ is live.
- **G-TRACE** — every MVP requirement links to ≥1 decision, ≥1 work item, ≥1 test (vacuous-pass
  warning at zero MVP rows).
- **G-SET** — every Always family present or omission-recorded (vacuous-pass warning for
  G-PROGRESS at zero verdicts).
- **G-PROGRESS** — active ACs all carry verdicts once auditing has begun.
- **G-REL** — stored trace edges satisfy the endpoint-type rules (v4: blocking; migrate cleans at
  conversion, adopt reports, writes reject).

Above the gates sits `readiness_check(scope)` — the semantic layer: blocking rules (pre-approval
decisions/ADRs, ACs not latest-Met, open critical/high defects, undischarged risks, open
slices/work incl. `Review`) + advisory liveness rules + operator-approved `WVR-` waivers
(reported `waived`, never silent) + `human_required` execution gates. The phase/slice →
`Implemented` transition is guarded by the same blocking rules; `force` is operator-words-only
and self-audited.

When changing the engine, run `python check.py` — suites, lints, the canonical round-trip, and
the eval fixtures are the merge bar.
