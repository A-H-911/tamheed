# Plan 096: review.html follows plans 069–095

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (rendering; the page changes bytes on every
  package once) - **Planned at**: `e32416e`

## Why this matters (the maintainer's question, 2026-09-22)

Inspected before this plan: `export_html.py` rendered `gate_run` and every table as a generic
register. It had no Feedback working surface (ACMP's thirteen rows were a raw dump), the
Approved-lessons fold omitted `superseded_by` (so plan 075's tag could not show), the waivers fold
could not mark an open-ended whole-rule waiver (079), and `readiness_check` was never rendered - the
human surface had none of `population`, `indeterminate`, `omitted`, `waived` or any advisory since
plan 069.

## What changed (maintainer ruling: option 1)

- Every section function takes the readiness report explicitly (`fn(conn, gates, ready,
  readiness)`); `render()` gains `readiness={"report", "as_of"}`, computed by the server - the
  renderer never imports it.
- **Feedback section** (after Lessons): awaiting the operator's word / confirmed, not yet reported /
  registered local tools (with `tool_path`) / reported, resolved or rejected.
- **Readiness section** (after Execution): the package-scope rules - rule, severity, status,
  population (`table: rows unit`, scoped), discriminating, omitted reason, waived, entities capped at
  eight - under an *Evaluated as of <date>* line naming the two calendar-reading rules
  (`open-questions-overdue`, expiring waivers), so a re-export on a later day changes bytes only
  where the calendar moved. Determinism within a run is asserted.
- The Approved-lessons fold gains a `supersession` column with the plan-075 tag (`pending its
  approval` / `RETIRE THIS ROW (operator)`), read from the successor's status - the page and the
  note agree.
- The waivers fold marks `OPEN-ENDED (whole rule, no expiry)` in the expires cell.

## Tests

`test_review_page_follows_plans_069_to_095`: the four folds' presence and one row each; the tag on
the half-state lesson; the open-ended mark; the readiness section with `Evaluated as of`, both new
advisories, an `indeterminate` rule and its `measured nothing` note; two exports byte-identical.
RED (no `feedback` section) before, GREEN after; export suite 38, contract 170.

## Done criteria

- [x] export + contract suites OK
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
