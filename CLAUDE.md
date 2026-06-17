# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Keystone is **not an application** — it is a reusable, vendor/stack-neutral agent **skill** (plus a thin
`/keystone` slash command) that turns a project description into an execution-ready planning & handoff
package for *another* agent to implement. The "product" is mostly Markdown: a methodology spec, blank
artifact templates, JSON schemas, and two small stdlib-only Python tools. There is no build for the skill
itself; the only executable code is the repo bootstrapper and the package validator.

This repo is the home of the *capability*, not of any project Keystone happens to plan. Generated output
only ever lives under `examples/` and `generated-samples/` (curated) — never elsewhere in the tree.

This directory is **not currently a git repository** (`scripts/init_skill_repo.py` is the tool that turns a
directory like this into one).

## Commands

Python 3.9+ is the only hard dependency. No pytest, no third-party packages — everything is stdlib.

```bash
# Validate a generated package against the 5 mechanical quality gates (human-readable)
python tests/validate_package.py <package-dir>
python tests/validate_package.py <package-dir> --json     # machine-readable, for CI/wrappers

# Run the validator's self-test (asserts both fixtures behave; this is the test suite)
python tests/test_validate_package.py

# Bootstrap a skill-hosting repo. ALWAYS --dry-run first (writes nothing), then re-run to apply.
python scripts/init_skill_repo.py --repo-name <name> --owner <org> --dry-run
python scripts/init_skill_repo.py --repo-name <name> --owner <org>                 # local git init + commit
python scripts/init_skill_repo.py --repo-name <name> --owner <org> --create-remote # opt-in GitHub push (needs gh)
```

There is no single test runner against fixtures other than `test_validate_package.py`; run that file directly.
`validate_package.py` exits `0` (all critical gates pass), `1` (a critical gate failed → NOT READY), or
`2` (usage/IO error). The init script uses exit codes `2`/`3`/`4`/`130` (see `scripts/README.md`).

## Architecture — the one principle that governs everything

> **The skill owns the capability; every entry point is a thin wrapper.**

`/keystone` (and any future CLI/API/MCP/UI) only: gathers input, validates *invocation syntax* (flag values),
normalizes to the input contract + a mode, invokes the skill, and routes output. It contains **no
methodology and makes no planning decisions**. All 22 workflow stages, artifact selection, quality gates, and
handoff logic live in the `keystone` skill. This is enforced by gate **G-CMD-THIN**. If you feel the urge to
add logic to `commands/keystone.md`, it belongs in the skill instead.

The dependency arrow points one way: **entry points → skill → shared assets (`templates/`, `schemas/`)**.
Nothing depends on a particular entry point; adding a wrapper leaves the skill untouched.

### Where things live (and the single-source-of-truth rules)

- **`skill/SKILL.md`** — always-loaded front door: principles, modes, the 22-stage map, reference index.
- **`skill/references/*.md`** — progressive-disclosure depth, loaded only when work reaches the matching
  part. `workflow.md` is the authoritative per-stage spec; `governance.md` owns identifiers/statuses/
  versioning; `quality-gates.md` defines all gates; `extension.md` is the enforceable entry-point contract;
  `safeguards.md` lists the anti-patterns being prevented.
- **`templates/`** — blank artifact forms. **Single source of truth for document shape.**
- **`schemas/`** — JSON schemas (input, state, handoff, registers). **Single source of truth for data shape.**
  When the skill is packaged to run standalone, `templates/` and `schemas/` are *vendored* (copied) into the
  bundle by a build step — so **edit them once at the repo root; never create a second copy** during dev.
- **`scripts/init_skill_repo.py`** is the single source of truth for repo bootstrap; `.sh`/`.ps1` siblings
  are thin interpreter-locating wrappers with **no logic** — keep it that way.
- **`commands/keystone.md`** — the thin wrapper (see above).
- Repo-root `*.md` (`METHODOLOGY`, `WORKFLOW`, `ARTIFACT-CATALOG`, `ARCHITECTURE`, `ROADMAP`, etc.) are
  human-facing spec/rationale and are *not* vendored into the runtime bundle.

### The 22 stages (grouped into 3 movements)

Understand (1–8: intake → classify → extract → normalize → ambiguity → contradiction → clarify → scope) →
Explore (9–15: research → architecture → option comparison → hypotheses → POC/experiment → decision capture →
risk) → Plan & hand off (16–22: execution planning → artifact generation → repo init → quality validation →
handoff → update cycles → final readiness). The authoritative per-stage spec is `skill/references/workflow.md`.

## Conventions that must stay consistent

- **Identifier scheme** (governed by `skill/references/governance.md`): `FR-`/`NFR-` (requirements), `CON-`
  (constraints), `INV-` (invariants), `ASM-` (assumptions), `DEP-` (dependencies), `OQ-` (open questions),
  `DEC-` (decisions), `ADR-` (decision records), `RISK-`, `HYP-`, `EXP-`, `AC-`, `PH-`, `WBS-`, `MS-`.
  Lifecycle statuses: `Draft → Proposed → Approved / Rejected / Superseded / Deferred → Implemented`. A
  *proposed* decision is never rendered as *approved* — that separation is a core safeguard.
- **The validator's `ID_PATTERNS`** (`tests/validate_package.py`) keys off these prefixes. If you introduce a
  new identifier prefix anywhere, add it to `ID_PATTERNS` or G-IDS will not recognize it.
- **Immutable-after-approval artifacts** (ADRs, approved acceptance criteria) are *superseded*, never edited.
- **Extend additively, never fork the workflow.** New artifact types, templates, schemas, gates, project-type
  profiles, diagram kinds, and entry points are added via the registries in `skill/references/extension.md` —
  register an entry and drop in a file. Additive changes are MINOR; changing an existing schema's required
  fields, the identifier scheme, or the handoff contract is MAJOR and ships a migration note.

## The 5 mechanical quality gates (what the validator enforces)

`tests/validate_package.py` implements the mechanical subset of `skill/references/quality-gates.md`; all five
are **Critical**:

- **G-IDS** — identifiers are well-formed, defined once, and every referenced id resolves (no dangling refs).
- **G-DEC-STATUS** — every decision/ADR row carries an explicit status from the allowed set.
- **G-REQ-SRC** — every `FR-`/`NFR-` row has a non-empty source/provenance (a dash or `n/a` counts as empty).
- **G-COMPLETE** — no unfinished markers (`TODO`/`TBD`/`<placeholder>`/`{{…}}`/…) and no empty sections.
- **G-TRACE** — every MVP requirement in the traceability matrix links to ≥1 decision, ≥1 work item, ≥1 test.

Remaining gates (Warn gates, and the judgment parts of G-CONFLICT/G-EXEC/G-HANDOFF/G-OQ) are recorded by a
human/agent in the validation report and are intentionally out of scope for the script. A gate reported as
`SKIP` means no applicable input was found — neither pass nor fail.

When changing the validator, exercise both `tests/fixtures/valid-package/` (must pass, exit 0) and
`tests/fixtures/invalid-package/` (must fail, exit 1, each seeded defect caught by the right gate).
