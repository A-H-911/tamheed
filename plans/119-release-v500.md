# Plan 119: release v5.0.0 + the ACMP brief

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (recipe)

## Why this matters

Every plan in the batch DONE; the combined acceptance pass (`accept_v500.py` N/N vs 0/N on an extracted `v4.14.0`; selftest 19/19; §0 on the real bundle; CI) passed.

## What changes

The release recipe (plugin.json == newest CHANGELOG heading; the six stamp lines; the README history key; the annotated tag; tag pushed separately; CI). Then the ACMP brief, transcript-only.

## Done criteria

- [ ] tag `v5.0.0`
- [ ] CI green on the tag commit
- [ ] the brief printed
