# Plan 090: Release v4.11.0

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [085-090-batch-findings-27.md](085-090-batch-findings-27.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (the plan-058 recipe with plan 084's F-1 step)
- **Depends on**: 085-089 DONE - **Planned at**: commit `be34858`

## Preconditions, verified before this plan ran

- Every plan of the batch DONE in the index; CI green on each pushed commit through `18d4666`
  (the beat and fix commits' runs are checked at tag time).
- Full test: 15/15 on the batch tree and 0/15 on an extracted `v4.10.0` tree, each failure its own;
  nine suites clean under `error::DeprecationWarning`; self-test 19/19.
- Lab beat 18 (`762b98b`) reviewed by re-running its done criteria: 9 new assertions each exit
  non-zero on `git archive f142dc5`'s fixture and 0 on the fixture; lab-tracker 65/65; `check.py`
  green after the merge and the F-3 fix (`be34858`).

## The recipe (plan 058 + plan 084's step), as run

1. `plugin.json` 4.10.0 -> 4.11.0; the six stamp lines.
2. CHANGELOG: `[Unreleased]` becomes `## [4.11.0] - 2026-09-22` under a MINOR lead-in that names
   `005_feedback.sql` (lint 7); a fresh empty `[Unreleased]` above it.
3. `stock-history.json`: `README.md` re-set under `4.11.0` after its version line moved
   (`orient-resume.md`'s key was set by plan 087 and does not change).
4. The lab fixture follows the stamp (F-1): re-emit the fixture's guide by tool, refusing unless it is
   the only diverged file and differs by the version line; re-export; gates, verify, `review_current`.
5. `python check.py`; advisor review; commit from a message file; annotated tag `v4.11.0`; push, then
   push the tag; CI green on the tagged commit.

## Done criteria

- [x] lints green inside `python check.py` -> `ALL CHECKS PASSED`
- [x] the fixture's `prompts/README.md` byte-equals the released body; `diverged: []`
- [x] tag `v4.11.0` on the release commit `b4e128d`; CI green on it (2026-09-22)
- [x] master record -> EXECUTED; index row 090 DONE; memory updated; the ACMP brief printed in the transcript
