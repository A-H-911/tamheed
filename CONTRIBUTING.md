# Contributing to Keystone

Thanks for improving Keystone. The highest-value contributions are **additive**: new artifact types,
templates, schemas, quality gates, project-type profiles, diagram kinds, and worked examples. This guide
covers setup, the invariants to preserve, and how to extend the skill without forking its workflow.

## Setup

- **Python 3.9+** is the only hard dependency (standard library only — no pytest, no third-party packages).
- Optional, for the repo-bootstrap script's remote feature: `git` and the GitHub CLI (`gh`).
- The skill itself has no build step. The bundle at `plugins/tamheed/` *is* the product.

```bash
# run the validator self-test (the test suite)
python tests/test_validate_package.py

# validate a generated package against the mechanical quality gates
python plugins/tamheed/scripts/validate_package.py <package-dir>          # human report
python plugins/tamheed/scripts/validate_package.py <package-dir> --json   # machine-readable

# v2 store + MCP server test suites
python tests/test_db_roundtrip.py
python tests/test_mcp_contract.py
```

## Invariants you must preserve

These are load-bearing. A change that breaks one is a regression even if tests pass.

1. **The skill owns the capability; entry points are thin wrappers.** All methodology — the 22 stages,
   artifact selection, quality gates, handoff logic — lives in `plugins/tamheed/SKILL.md` and its
   `references/`. External entry points (a CLI, an HTTP API, an MCP server, a UI) must only normalize input
   to the skill's contract, invoke the skill, and route output — carrying **no** methodology of their own
   (gate **G-CMD-THIN**; see `plugins/tamheed/references/extension.md`). Inside Claude Code, the skill *is*
   the entry point — there is no separate command file to keep thin.
2. **The bundle is self-contained.** Claude Code copies the plugin directory to a cache on install, so
   anything the skill reads or invokes at runtime must live inside `plugins/tamheed/` with **zero** outward
   (`../..`, repo-root) references. `docs/` may link into the bundle, but the bundle never reaches out.
3. **Single source of truth.** Forms live in `plugins/tamheed/templates/`; data shapes in
   `plugins/tamheed/schemas/`; the artifact catalog in `plugins/tamheed/references/artifact-catalog.md`.
   Don't create a second copy of any of these.
4. **Separation of facts / decisions / proposals, and the identifier + status scheme** are part of the
   contract — see `plugins/tamheed/references/governance.md`.

## How to extend (additively)

Register an entry and drop in a file — don't fork the workflow. See
`plugins/tamheed/references/extension.md` for the full registry.

| Want to add… | Do this |
|---|---|
| A new artifact type | Add a `templates/*.template.md`, a row in `references/artifact-catalog.md`, a `schemas/*.schema.json` if structured, and a selection trigger in `references/artifact-rules.md`. |
| A new template | Add `templates/<name>.template.md`; reference it from the catalog. |
| A new schema | Add `schemas/<name>.schema.json`; reference it from the artifact/state. |
| A new quality gate | Add a gate row in `references/quality-gates.md`; if mechanical, add a check in `scripts/validate_package.py`. |
| A new identifier prefix | Add it to `ID_PATTERNS` in `scripts/validate_package.py`, or gate **G-IDS** won't recognize it. |
| A new entry point | Make it normalize→invoke→route with no methodology; see `references/extension.md`. |

## Compatibility

Additive changes (new template/schema/gate/profile/entry point) are **MINOR**. Changing an existing schema's
required fields, the identifier scheme, or the handoff contract is **MAJOR** and must ship a migration note
(see `plugins/tamheed/references/governance.md`). The validator should degrade gracefully on packages
authored under a prior MINOR version. Record notable changes in [`CHANGELOG.md`](CHANGELOG.md).

## Before opening a PR

- The validator self-test passes: `python tests/test_validate_package.py`.
- New runtime-read files live inside `plugins/tamheed/` and add no outward references.
- Conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`…).

## Design background

The rationale behind Keystone's structure is in [`docs/design-decisions.md`](docs/design-decisions.md);
the layering and entry-point contract are in [`docs/architecture.md`](docs/architecture.md).
