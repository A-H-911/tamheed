# Plan 106: `ready` follows its doctrine (FB-016)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [106-111-batch-findings-30.md](106-111-batch-findings-30.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: MEDIUM (a verdict harnesses read changes for every empty scope)

## Why this matters (ACMP's `FB-016`, findings_30 §3.1)

`quality-gates.md` said "an empty slice is not a ready slice" and the review page's per-slice panel
already rendered one as "not ready"; `readiness_check` said `ready: true`, because `ready` ignored
`indeterminate`. 29 of ACMP's 44 slices read ready on a blocking rule that measured nothing.

## What changes

`ready = no blocking fail AND no blocking indeterminate`; the result gains `indeterminate: [rule
names]` (blocking only, rule order, `[]` when none). The Implemented transition guard stays fail-only
(the doc's second clause). `loop-iteration.md` gains one clause (+ `4.14.0` key); quality-gates, the
server README row, docs/architecture.md.

## Done criteria

- [x] RED then GREEN (the plan-049 test and `:658` rewritten; an empty slice false with both rules; a WBS row + a Met AC → true)
- [x] `python check.py`; dry-run on a fixture copy (`scratchpad/dryrun_v4140.py`: SL-003 false -> true after a WBS row + a Met AC) (`SL-003` false with `["acs-met", "wbs-done"]`, `SL-001` true)
- [ ] CI green

## Execution note

On a package that has recorded NO defects and no `defect` omission, `defects-closed` reads
indeterminate at every scope (plan 077's whole-table branch), so no scope is ready until the family's
omission is recorded — the doctrine applied uniformly; the test pins it and quality-gates says it.
