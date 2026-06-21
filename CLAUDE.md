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
plugins/keystone/                     # THE installable bundle — self-contained, copied intact on install
├── .claude-plugin/plugin.json
├── SKILL.md                          # always-loaded front door (owns the capability)
├── references/                       # on-demand depth, incl. artifact-catalog.md (the artifact catalog)
├── templates/                        # blank artifact forms (single source of truth for document shape)
├── schemas/                          # JSON schemas (single source of truth for data shape)
├── scripts/                          # init_skill_repo.py (repo bootstrap) + validate_package.py (gates)
└── assets/                           # logos (used by repo-init branding)
docs/                                 # architecture, methodology, workflow, design-decisions, install
evals/                                # behavioral eval scenarios (skill-level, model-in-the-loop)
examples/  generated-samples/  tests/ # teaching material, demo package, validator self-test
.github/workflows/                    # CI (validator + golden packages) + scheduled eval-spec lint
SECURITY.md                           # trust model, untrusted-content posture, reporting
```

The bundle also carries `references/required-artifacts.json` — the machine-readable mirror of the **Always**
class in `artifact-rules.md`, read by gate **G-SET**. There is **no** top-level `skill/`, `templates/`,
`schemas/`, `scripts/`, `commands/`, or `adrs/` anymore — everything runtime moved into `plugins/keystone/`;
build-history docs were removed.

## Commands

Python 3.9+ is the only hard dependency (stdlib only — no pytest, no third-party packages).

```bash
# Validator self-test (this is the test suite)
python tests/test_validate_package.py

# Validate a generated package against the 6 mechanical quality gates
python plugins/keystone/scripts/validate_package.py <package-dir>          # human report
python plugins/keystone/scripts/validate_package.py <package-dir> --json   # machine-readable

# Preview a repo bootstrap (writes nothing); drop --dry-run to apply.
# --layout defaults to `plugin` (self-contained bundle); use `classic` for the old skill/+commands/ layout.
python plugins/keystone/scripts/init_skill_repo.py --repo-name <name> --owner <org> --dry-run
```

`validate_package.py` exits `0` (all critical gates pass), `1` (a critical gate failed → NOT READY), `2`
(usage/IO error). The init script uses exit codes `2`/`3`/`4`/`130` (see its `scripts/README.md`).

> Windows note: `init_skill_repo.py` reconfigures stdout/stderr to UTF-8 at startup (`_configure_stdio`), so
> its banner/summary glyphs (`→`, `•`, box-drawing) don't raise `UnicodeEncodeError` on legacy code pages
> such as cp1252.

## Architecture — the governing principle

> **The skill owns the capability; every entry point is a thin wrapper.**

All methodology — the 22 stages, artifact selection, quality gates, handoff logic — lives in
`plugins/keystone/SKILL.md` + its `references/`. External entry points (CLI/API/MCP/UI) only normalize input,
invoke the skill, and route output, carrying no methodology (gate **G-CMD-THIN**). In Claude Code the skill
*is* the entry point (invoked as `/keystone:keystone` when installed as a plugin, or `/keystone` when copied
standalone into a skills dir) — there is no separate command file.

The 22 stages: **Understand** (1–8 intake→scope) → **Explore** (9–15 research→decisions→risk) → **Plan &
hand off** (16–22 execution plan→artifacts→repo init→validation→handoff). Authoritative per-stage spec:
`plugins/keystone/references/workflow.md`.

## Invariants that must stay true

- **Self-contained bundle (mechanically required).** Claude Code copies only the plugin directory on install,
  so everything the skill reads/invokes at runtime must live inside `plugins/keystone/` with **zero** outward
  (`../..`, repo-root) references. `docs/` may link into the bundle; the bundle never links out.
- **Single source of truth** = the bundle: forms in `plugins/keystone/templates/`, data shapes in
  `plugins/keystone/schemas/`, the artifact catalog in `plugins/keystone/references/artifact-catalog.md`.
  Never make a second copy.
- **Identifier scheme** (`plugins/keystone/references/governance.md`): `FR-`/`NFR-`, `CON-`, `INV-`, `ASM-`,
  `DEP-`, `OQ-`, `DEC-`, `ADR-`, `RISK-`, `HYP-`, `EXP-`, `AC-`, `PH-`, `WBS-`, `MS-`. Statuses:
  `Draft → Proposed → Approved / Rejected / Superseded / Deferred → Implemented`. A *proposed* decision is
  never rendered as *approved*.
- **New identifier prefixes** must be added to `ID_PATTERNS` in `plugins/keystone/scripts/validate_package.py`
  or gate **G-IDS** won't recognize them.
- **Immutable-after-approval** artifacts (ADRs, approved acceptance criteria) are *superseded*, never edited.
- **Extend additively** via the registries in `plugins/keystone/references/extension.md` (templates, schemas,
  gates, profiles, diagram kinds, entry points). Additive = MINOR; changing a schema's required fields, the
  identifier scheme, or the handoff contract = MAJOR + migration note.

Note: paths inside `*.template.md` and the strings `init_skill_repo.py` writes describe the **generated**
package/repo structure (e.g. `skill/`, `docs/assets/`) — those are intentional output content, not stale
references to this repo's layout.

## The 6 mechanical quality gates (validator)

`plugins/keystone/scripts/validate_package.py` implements the mechanical subset of
`plugins/keystone/references/quality-gates.md`; all six are Critical:

- **G-IDS** — identifiers well-formed, defined once, every referenced id resolves (no dangling refs).
- **G-DEC-STATUS** — every decision/ADR row carries an explicit status from the allowed set.
- **G-REQ-SRC** — every `FR-`/`NFR-` row has a non-empty source/provenance.
- **G-COMPLETE** — no unfinished markers (`TODO`/`TBD`/`<placeholder>`/`{{…}}`/…) and no empty sections.
- **G-TRACE** — every MVP requirement in the traceability matrix links to ≥1 decision, ≥1 work item, ≥1 test.
- **G-SET** — every **Always** artifact (`references/required-artifacts.json`, the machine mirror of the
  `artifact-rules.md` Always class) is present on disk or recorded in `manifest.json` `omitted_artifacts[]`
  with a reason; the manifest exists; nothing it declares present is missing. Closes the gap where a hollow
  package (charter + README only) passed because every other gate SKIPped on the absent input.

When changing the validator, exercise `tests/fixtures/valid-package/` (must pass, exit 0),
`tests/fixtures/invalid-package/` (must fail, exit 1, each seeded defect caught by the right gate), and
`tests/fixtures/incomplete-package/` (internals valid but a required artifact missing → must fail on G-SET).
Adding/removing an Always artifact means editing **both** `artifact-rules.md` and `required-artifacts.json`.
