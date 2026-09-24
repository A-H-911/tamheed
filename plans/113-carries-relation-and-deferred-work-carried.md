# Plan 113: the `carries` relation + the `deferred-work-carried` advisory (FB-018)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a schema migration; a new advisory the field reads on day one)

## Why this matters

ACMP's `FB-018`: `RELATION_RULES` lets no typed relation link a WBS item to the deferred row it carries; plan 107's note said "its WBS rows carry it", which is prose — two finished Activated rows were invisible to every rule. Interview ruling: a NEW relation `carries` (wbs-item -> deferred-work), advisor-confirmed; the edge is the ONLY carrier.

## What changes

Migration `006_carries.sql` (the 002/004 recreation of `trace_edges` with `carries` in the CHECK; applies at connect(), no operator step; `schema_version` 6). `RELATION_RULES["carries"]`. Advisory `deferred-work-carried`: Activated rows with no `carries` edge from a WBS item whose status is not Implemented/Superseded/Obsolete/Rejected. The `replan-deferred` skill writes the edge in the activating batch. Docs across the whole relation roster (every file the repo-wide `amends` grep names).

## Done criteria

- [ ] RED then GREEN: edge accepted, reverse refused, advisory lists / drops / re-lists; `test_store_migrations` 006 twin
- [ ] a v4.14 fixture copy opens with `schema_version 6`, edges intact, `package_verify` unchanged
- [ ] the `amends` grep re-run: every surviving file also names `carries`
- [ ] `python check.py`
- [ ] CI green
