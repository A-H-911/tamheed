# Plan 060: Readiness cites the specific waiver before a whole-rule one

> Executed directly by the reviewer (maintainer-delegated, 2026-09-12) after a
> devil's-advocate review of the post-v4.8.0 loose ends; recorded here so the index row
> has a self-contained record like every other advisor plan.

## Status

- **Priority**: P3
- **Effort**: XS
- **Risk**: LOW (two branches swapped; verdict logic unchanged)
- **Depends on**: 056 (whole-rule waivers), 059 (the observation)
- **Category**: correctness (audit-trail specificity)
- **Planned at**: commit `c8e3920` (v4.8.0), 2026-09-12

## Why this matters

Lab beat 15 (plan 059) observed that when a whole-rule `WVR-` row (no `applies_to`) and a
per-entity `WVR-` row both cover the same rule, `_readiness_report.rule()` cited the
whole-rule waiver for **every** entity — the per-entity waiver, the operator's words about
that named entity, never appeared in the `waived` list. The verdict was right (the entity is
waived either way); the audit trail was less specific than the operator's own record.

Judgment recorded here, not inherited doctrine: **the most specific operator words are
cited; a whole-rule waiver is the fallback, never the shadow.**

## Current state (before)

`plugins/tamheed/server/tamheed_server.py`, inside `rule()` (~:1526): the loop tested
`whole_rule` first, then `ent in per_entity`.

## Scope

**In scope**: the two branches in `rule()`; one test in `tests/test_mcp_contract.py`
(`V4EngineTest.test_waiver_citation_prefers_the_specific_waiver`); CHANGELOG `[Unreleased]`
`### Fixed`; this record; the index row.

**Out of scope**: the viewer (`export_html` never receives `readiness_check` output — it
renders the waivers table and `v_phase_exit`, so no golden changes; verified by re-exporting
the lab fixture in a scratch copy and byte-comparing: identical), the lab fixture, the
evidence report (the observation stays as history).

## Steps (as executed)

1. Test first: seed `DEF-012` (open, low) next to `setUp`'s `DEF-001`; `WVR-020` on
   `defects-minor` with `applies_to: DEF-012`; `WVR-021` on `defects-minor` with no
   `applies_to`. Assert status `waived`, `entities == []`, `DEF-012 → WVR-020`,
   `DEF-001 → WVR-021`. **RED** on the old order: one failure, `'WVR-021' != 'WVR-020'`.
2. Swap: test `ent in per_entity` first, `whole_rule` second; one comment line.
   **GREEN**: `python tests/test_mcp_contract.py` → 138 tests OK (+1).
3. `python check.py` → `ALL CHECKS PASSED`; scratch re-export of
   `evals/sample-results/lab-tracker/package` → `review.html` and `csv/` identical.

## Done criteria

- [x] `grep -n "if ent in per_entity" plugins/tamheed/server/tamheed_server.py` → one hit,
      before the `elif whole_rule` line
- [x] `python tests/test_mcp_contract.py` → OK, 138 tests
- [x] `python check.py` → `ALL CHECKS PASSED`
- [x] `git status` shows no change under `evals/sample-results/` or `lab/`

### Release discipline (this repo's `check.py` will fail you otherwise)

- No `plugin.json` bump (lint 4). CHANGELOG under `## [Unreleased]` → `### Fixed`.
- The five version-stamped files untouched; no stock prompt or template touched; no golden
  hand-edited (none changed).
