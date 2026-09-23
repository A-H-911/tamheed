# Plan 099: Release v4.12.0

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (the plan-058 recipe with plan 084's F-1 step)
- **Depends on**: 091-098 DONE - **Planned at**: commit `9ac93fe`

## Preconditions, verified before this plan ran

- Every plan of the batch DONE in the index; CI green on each pushed commit through `de7055a` (the
  beat merge and close-out runs are checked at tag time).
- Full test: 12/12 on the batch tree and 0/12 on an extracted `v4.11.0` tree, each failure its own
  (the two lab findings F-4 and F-5 included); nine suites clean under `error::DeprecationWarning`;
  self-test 19/19.
- Lab beat 19 (`9a7aa34`) reviewed by re-running its done criteria: 8 new assertions each exit
  non-zero on `git archive de7055a`'s fixture and 0 on the fixture; lab-tracker 73/73; `check.py`
  green on main after the merge.

## The recipe (plan 058 + plan 084's step), as run

1. `plugin.json` 4.11.0 -> 4.12.0; the six stamp lines.
2. CHANGELOG: `[Unreleased]` becomes `## [4.12.0] - 2026-09-23` under a MINOR lead-in; a fresh
   empty `[Unreleased]` above it.
3. `stock-history.json`: `README.md` re-set under `4.12.0` after its version line moved.
4. The lab fixture follows the stamp: the F-1 script refused (plan 091 changed the guide's body, not
   only its version line), which was right — the fixture's copy was byte-equal to the 4.11.0 history
   body, i.e. STALE-STOCK, and `handoff_emit(refresh_stock=true)` refreshed it by the sanctioned
   route with no `force`; re-export; gates, verify, `review_current` all true.
5. `python check.py`; advisor review; commit from a message file; annotated tag `v4.12.0`; push, then
   push the tag; CI green on the tagged commit.

## Done criteria

- [x] lints green inside `python check.py` -> `ALL CHECKS PASSED`
- [x] the fixture's `prompts/README.md` byte-equals the released body; `diverged: []`
- [x] tag `v4.12.0` on the release commit `a472bd3`; CI green on it (2026-09-23)
- [x] master record -> EXECUTED; index row 099 DONE; memory updated; the ACMP brief printed in the transcript
