# Plan 108: `expect_unchanged` refuses the vacuous case; the sweep prompt's four gaps

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [106-111-batch-findings-30.md](106-111-batch-findings-30.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: MEDIUM (a guard; the sweep prompt is stock)

## What changes

Outside a `substitute`, a column named in `expect_unchanged` that the FINAL row does not carry is
refused - naming it asserted nothing (findings_30 Q3). Engine-populated columns count as sent (the
batch-29 position is kept). `register-liveness.md`: step 7 clause, step 10 "search across families for
an existing ruling first", step 11 the new population, step 15 the render arithmetic (+ `4.14.0` key).

## Done criteria

- [ ] RED then GREEN; `python check.py`; the batch-29 security PoC still green
- [ ] CI green
