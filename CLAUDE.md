# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Keystone is **not an application** — it is a reusable, vendor/stack-neutral agent **skill**, packaged as a
**Claude Code plugin**, that turns a project description into an execution-ready planning & handoff package
for *another* agent to implement. The "product" is mostly Markdown (a methodology spec, blank artifact
templates, JSON schemas) plus two small stdlib-only Python tools. There is no build step; the only executable
code is the repo bootstrapper and the package validator.

This repo is the home of the *capability*, not of any project Keystone plans. Generated output only ever
lives under `examples/` and `generated-samples/` (curated) — never elsewhere.

## Layout (post-restructure)

The repository is its own **plugin marketplace**, and the skill is one **self-contained bundle**:

```
.claude-plugin/marketplace.json      # repo = marketplace (one plugin: keystone)
plugins/tamheed/                     # THE installable bundle — self-contained, copied intact on install
├── .claude-plugin/plugin.json
├── SKILL.md                          # always-loaded front door (owns the capability)
├── references/                       # on-demand depth, incl. artifact-catalog.md (the artifact catalog)
├── templates/                        # blank artifact forms (single source of truth for document shape)
├── schemas/                          # JSON schemas (single source of truth for data shape)
├── scripts/                          # validate_package.py (frozen v1 gate engine)
├── db/                               # v2 relational store: schema.sql, migrations/, store.py, CANONICAL.md
├── server/                           # Tamheed MCP server + .mcp.json launch config (plugin root)
├── prompts/                          # scenario prompt library, emitted into <package>/prompts/ (plan 018)
└── assets/                           # logos
docs/                                 # architecture, methodology, workflow, design-decisions, install
evals/                                # behavioral eval scenarios (skill-level, model-in-the-loop)
examples/  generated-samples/  tests/ # teaching material, demo package, validator self-test
.github/workflows/                    # CI (validator + golden packages) + scheduled eval-spec lint
SECURITY.md                           # trust model, untrusted-content posture, reporting
```

The bundle also carries `references/required-artifacts.json` — the machine-readable mirror of the **Always**
class in `artifact-rules.md`, read by gate **G-SET**. There is **no** top-level `skill/`, `templates/`,
`schemas/`, `scripts/`, `commands/`, or `adrs/` anymore — everything runtime moved into `plugins/tamheed/`;
build-history docs were removed.

## Commands

Python 3.9+ is the only hard dependency (stdlib only — no pytest, no third-party packages).

```bash
# Validator self-test (this is the test suite)
python tests/test_validate_package.py

# Validate a generated package against the 7 mechanical quality gates
python plugins/tamheed/scripts/validate_package.py <package-dir>          # human report
python plugins/tamheed/scripts/validate_package.py <package-dir> --json   # machine-readable

# v2 store + MCP server suites
python tests/test_db_roundtrip.py
python tests/test_mcp_contract.py

# MCP server selftest (PEP 723: uv fetches the mcp SDK; Python >=3.10 per ASM-D)
uv run plugins/tamheed/server/tamheed_server.py --selftest
```

`validate_package.py` exits `0` (all critical gates pass), `1` (a critical gate failed → NOT READY), `2`
(usage/IO error). It is the **frozen v1 gate engine** — the migration source contract (plan 010); v2
gates run through the MCP server's `gate_run`. The v1 repository bootstrapper was removed in v2 (ASM-B).

> Windows note: `tamheed_server.py` reconfigures stdout/stderr to UTF-8 at startup, so its output doesn't
> raise `UnicodeEncodeError` on legacy code pages such as cp1252.

## Architecture — the governing principle

> **The skill owns the capability; every entry point is a thin wrapper.**

All methodology — the 22 stages, artifact selection, quality gates, handoff logic — lives in
`plugins/tamheed/SKILL.md` + its `references/`. External entry points (CLI/API/MCP/UI) only normalize input,
invoke the skill, and route output, carrying no methodology (gate **G-CMD-THIN**). In Claude Code the skill
*is* the entry point (invoked as `/keystone:keystone` when installed as a plugin, or `/keystone` when copied
standalone into a skills dir) — there is no separate command file.

The 22 stages: **Understand** (1–8 intake→scope) → **Explore** (9–15 research→decisions→risk) → **Plan &
hand off** (16–22 execution plan→artifacts→repo init→validation→handoff). Authoritative per-stage spec:
`plugins/tamheed/references/workflow.md`.

## Invariants that must stay true

- **Self-contained bundle (mechanically required).** Claude Code copies only the plugin directory on install,
  so everything the skill reads/invokes at runtime must live inside `plugins/tamheed/` with **zero** outward
  (`../..`, repo-root) references. `docs/` may link into the bundle; the bundle never links out.
- **Single source of truth** = the bundle: forms in `plugins/tamheed/templates/`, data shapes in
  `plugins/tamheed/schemas/`, the artifact catalog in `plugins/tamheed/references/artifact-catalog.md`.
  Never make a second copy.
- **Identifier scheme** (`plugins/tamheed/references/governance.md`): `FR-`/`NFR-`, `CON-`, `INV-`, `ASM-`,
  `DEP-`, `OQ-`, `DEC-`, `ADR-`, `RISK-`, `HYP-`, `EXP-`, `AC-`, `PH-`, `WBS-`, `MS-`. Statuses:
  `Draft → Proposed → Approved / Rejected / Superseded / Deferred → Implemented`. A *proposed* decision is
  never rendered as *approved*.
- **New identifier prefixes** must be added to `ID_PATTERNS` in `plugins/tamheed/scripts/validate_package.py`
  or gate **G-IDS** won't recognize them.
- **Immutable-after-approval** artifacts (ADRs, approved acceptance criteria) are *superseded*, never edited.
- **Extend additively** via the registries in `plugins/tamheed/references/extension.md` (templates, schemas,
  gates, profiles, diagram kinds, entry points). Additive = MINOR; changing a schema's required fields, the
  identifier scheme, or the handoff contract = MAJOR + migration note.

Note: paths inside `*.template.md` describe the **generated** package structure — intentional output
content, not stale references to this repo's layout.

## The 7 mechanical quality gates (validator)

`plugins/tamheed/scripts/validate_package.py` implements the mechanical subset of
`plugins/tamheed/references/quality-gates.md`; all seven are Critical:

- **G-IDS** — identifiers well-formed, defined once, every referenced id resolves (no dangling refs).
- **G-DEC-STATUS** — every decision/ADR row carries an explicit status from the allowed set.
- **G-REQ-SRC** — every `FR-`/`NFR-` row has a non-empty source/provenance.
- **G-COMPLETE** — no unfinished markers (`TODO`/`TBD`/`<placeholder>`/`{{…}}`/…) and no empty sections.
- **G-TRACE** — every MVP requirement in the traceability matrix links to ≥1 decision, ≥1 work item, ≥1 test.
- **G-SET** — every **Always** artifact (`references/required-artifacts.json`, the machine mirror of the
  `artifact-rules.md` Always class) is present on disk or recorded in `manifest.json` `omitted_artifacts[]`
  with a reason; the manifest exists; nothing it declares present is missing. Closes the gap where a hollow
  package (charter + README only) passed because every other gate SKIPped on the absent input.
- **G-PROGRESS** — when an acceptance audit (`validation/acceptance-audit.md`) is present, every `AC-` in
  the acceptance criteria appears in it with a verdict from {Met, Partial, Not-met, Pending}; **SKIPs** when
  no audit exists (the audit is Conditional — handoff / long execution horizon), so a planning-only package
  is never penalised. Closes the execution-tracking loop (the downstream agent's during/after-exec close-out
  of the acceptance criteria).

When changing the validator, exercise `tests/fixtures/valid-package/` (must pass, exit 0),
`tests/fixtures/invalid-package/` (must fail, exit 1, each seeded defect caught by the right gate), and
`tests/fixtures/incomplete-package/` (internals valid but a required artifact missing → must fail on G-SET).
Adding/removing an Always artifact means editing **both** `artifact-rules.md` and `required-artifacts.json`.
