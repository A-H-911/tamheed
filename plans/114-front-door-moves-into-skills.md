# Plan 114: the front door moves into `skills/` and the skills lint exists

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: MEDIUM (the plugin's only entry point moves; §0 measured the new layout first)

## Why this matters

The docs: a plugin with a `skills/` directory does not load a root `SKILL.md`. Today the front door loads only because the bundle has no `skills/` directory (this session's loader resolved `tamheed` to the root file). Every later plan adds skills, so the front door moves first — to `skills/tamheed/SKILL.md`, keeping its `/tamheed:tamheed` invocation.

## What changes

`git mv plugins/tamheed/SKILL.md plugins/tamheed/skills/tamheed/SKILL.md` + the bundle-root sentence (`${CLAUDE_PLUGIN_ROOT}`, substituted at load — measured in §0). check.py lints 8/9/10 and the teaching dict point at the new path; lint 12 (new): every `skills/*/SKILL.md` has frontmatter `name` == folder and a `description`, is ≤ 500 lines, carries no `{package}`, every `${CLAUDE_PLUGIN_ROOT}/…` token resolves against the bundle, and no stack/product/field identifier appears (denylist with an allowlist); `skills/**` joins the teaching lint with the prompts scope. `tests/test_check_lints.py` re-aimed + two lint-12 tests. The eleven path references in CLAUDE.md, CONTRIBUTING.md, docs/install.md, docs/methodology.md, README.md, SECURITY.md.

## Done criteria

- [x] RED (two lint-12 tests fail before the lint exists) then GREEN
- [x] `python check.py`
- [x] §0 steps 2-3 re-run on a copy of the REAL bundle after the move
- [ ] CI green

## Execution note

RED: both lint-12 tests failed (`None != 1`: no lint refused the planted skills). GREEN after the lint; the only identifier the front door carries is `ADR-0001` (tamheed's own design record), allowlisted by name. §0 re-run on a copy of the real moved bundle: `Base directory … \skills\tamheed`, the placeholder substituted to the bundle root, both `tamheed:tamheed` and `tamheed:probe` listed. The stock prompt bodies carry two illustrative ids (`LL-003, LL-007` in skill-promote) and no stack words — plan 116 neutralises them.
