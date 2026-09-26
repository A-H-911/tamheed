# Plan 129: `stock_merged` verifies the whole declared release (the field's FB-023)

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (report-only; the 5.1 test survives unchanged)

## Why this matters

FB-023 (ACMP, 5.1.0): `prompts/integrity-check.md` carried `<!-- tamheed:stock-merged 4.9.0 -->`
over a 4.2.1-era body. Plan 125's check compared only the lines 4.9.0 ADDED over 4.6.0 — the nine
closing-section lines, all present — and read `verified: true, delta_missing 0/9`, while 38 of
4.9.0's 62 lines were absent. Plan 125's docstring claimed this case reads false. A marker declared
for a release whose newest increment alone was merged passed the check built to catch it.

## What changes

- `_stock_merged_check` (`tamheed_server.py`): `required` = every non-blank line of the DECLARED
  release's body (after `{package}` substitution); `missing` = those absent on disk; `verified`
  iff none missing; `missing_by_release` = each absent line counted under the first release
  (ascending) whose body carries it; `delta_missing` (the declared release's own increment) kept;
  `reason` = "n of the m lines of X.Y.Z are absent (4.5.0: 18, 4.6.0: 18, …)". The docstring says
  why the check is report-only: a customisation that rewrites stock lines reads as absent.
- Docs: `references/handoff.md`, `server/README.md` (the result shape), `prompts/README.md` (the
  5.0 text "never verified" was stale since 5.1 — the history key for the new body lands with the
  stamp in plan 134), CHANGELOG.

## Evidence

Replayed over ACMP's deleted file at `c85e68d8` with the tag's history: required 62, missing 38,
`missing_by_release {4.5.0: 18, 4.6.0: 18, 4.2.1: 2}` — the field's 38/62 reproduced; the 4.2.1
count is two lines the customisation rewrote (why the reason says "absent", never "never merged").

## Tests

- `test_stock_merged_marker_is_verified_against_the_history` — unchanged, green (its partial file
  is the previous body + one added line, so the missing set is the rest of the increment under
  either semantics).
- `test_stock_merged_attributes_missing_lines_to_their_release` — a retired file's history
  (`orient-resume.md`, five releases): the FIRST release's body + the LATEST increment + the
  marker → `verified False`, `delta_missing 0/n`, `missing_by_release` keyed by the middle
  releases in ascending order, the reason's count equal to their sum.

## Skipped on purpose

An in-order containment check (FB-019 q3's wording): presence answers its substance; order adds
code for no field case.
