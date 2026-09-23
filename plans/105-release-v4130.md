# Plan 105: release v4.13.0

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P1 - **Effort**: XS - **Risk**: LOW (the plan-058 recipe)

## The recipe

CHANGELOG `[Unreleased]` → `[4.13.0] - <date>`; `plugin.json` == newest heading; the six stamp lines;
the F-1 fixture step by `handoff_emit(refresh_stock=True)` (`refreshed` = `README.md`,
`register-liveness.md`); stock-history re-set after the guide's version line moves; `python check.py`;
annotated tag `v4.13.0`; push the tag separately; CI on the tag; memory + index close-out.

## Done criteria

- [x] lints green; tag `v4.13.0` on `91774b6` pushed; CI green
- [x] the ACMP brief printed in the transcript (transcript-only)
