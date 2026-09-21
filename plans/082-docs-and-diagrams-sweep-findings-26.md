# Plan 082: Docs and diagrams sweep for the findings_26 batch

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose and one diagram; one stock prompt body)
- **Category**: documentation - **Planned at**: commit `8cf9491`

## Why this matters

Plans 075-081 each documented themselves in their own record and the CHANGELOG, and 075/079 in
the `register-liveness.md` playbook. Measured before this plan, outside `plans/` and the
CHANGELOG: `changed_columns`, `review_current`, the `stock-merged` marker, `in_code_spans`,
`not_well_formed` and the recorded-omission rule were documented NOWHERE; the two new advisories
only in one prompt. Three live sentences were wrong: "sixteen" package-scope advisories (twice;
it is eighteen, one emitted only when waivers exist) and `search` as an "exact substring"
(plan 072's wording; the field established from the pragmas that SQLite's default `LIKE` is
case-insensitive for ASCII).

## What changed

| File | Change |
|---|---|
| `plugins/tamheed/server/README.md` | `entity_upsert` (`changed_columns`; lesson supersession + the operator-only retirement), `readiness_check` (zero-row semantics, the two informational prose-id lists, the two advisories), `package_verify` (`review_current`), `export_html` (the digest stamp), `handoff_emit` (`stock_merged`, `contains_current_stock`, the tagged lesson); `search` is a case-insensitive substring match |
| `plugins/tamheed/references/quality-gates.md` | advisory count; "no rule passes over nothing" with the recorded-omission exception; the prose-id floor |
| `plugins/tamheed/references/governance.md` | status is the single truth for what binds; the engine retires on approval of the successor; by hand needs `operator_confirm` |
| `plugins/tamheed/references/handoff.md` | the tagged half-state lesson in the note, and why (the 180-character window) |
| `plugins/tamheed/SKILL.md` | two sentences: read `changed_columns` after re-sending a long field; what makes a lesson stop binding |
| `plugins/tamheed/prompts/README.md` | teaches the `<!-- tamheed:stock-merged X.Y.Z -->` marker - a stock prompt body, so re-set under `stock-history.json` key `4.10.0` in this commit |
| `docs/entities.md` | **new diagram**: the lesson lifecycle (`stateDiagram-v2`) with the automatic supersession edge and which transitions need the operator's word |
| `docs/architecture.md` | advisory count |
| `SECURITY.md` | the operator-only lesson retirement, and the two unattended-unbind paths the plan-075 reviewers found |
| `README.md` | tool table: `changed_columns`, `review_current` |

## Validation

Per-behavior grep over tracked files outside `plans/`, `CHANGELOG.md`, tests and code: every new
name appears in at least two documents; `git grep -i "exact substring"` is empty; the only
surviving "sixteen" hits count the prompt library, not advisories.

The patch was applied transactionally (all anchors verified in memory, nothing written on a
miss), so no file could be left half-edited.

## Done criteria

- [x] per-behavior grep clean
- [x] `python check.py` -> `ALL CHECKS PASSED` (lint 9: the prompt guide's body is held under `4.10.0`)
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`. The release (plan 084) moves the prompt
guide's version line and re-sets its `4.10.0` key, as the plan-058 recipe requires.
