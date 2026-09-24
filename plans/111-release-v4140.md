# Plan 111: release v4.14.0

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [106-111-batch-findings-30.md](106-111-batch-findings-30.md).

## Status

- **Priority**: P1 - **Effort**: XS - **Risk**: LOW (the plan-058 recipe)

## The recipe

CHANGELOG `[Unreleased]` -> `[4.14.0]`; `plugin.json`; the six stamps; F-1 by `handoff_emit(refresh_stock=True)`
(`refreshed` = the changed guides); stock-history re-set; `python check.py`; annotated tag; push the tag
separately; CI; memory + index close-out.

## Done criteria

- [x] lints green; tag `v4.14.0` on `83cfb12` pushed; CI green
- [x] the ACMP brief printed in the transcript
