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

- [x] RED then GREEN: edge accepted, reverse refused, advisory lists / drops / re-lists; `test_store_migrations` 006 twin
- [x] a v4.14 fixture copy opens with `schema_version 6`, edges intact, `package_verify` unchanged
- [x] the `amends` grep re-run: every surviving file also names `carries`
- [x] `python check.py`
- [ ] CI green

## Execution note (2026-09-25)

RED: the contract test failed on the missing rule; the store test on the missing relation. GREEN
after `006_carries.sql` (a `trace_edges` recreation, the 002/004 pattern) + `RELATION_RULES` +
the advisory. Measured on a COPY of the lab fixture: `schema_version` 6, `migrations_head`
`006_carries.sql`, 30 edges loaded == 30 on disk, `package_verify` true — no operator step, no
JSONL change. The `amends` grep re-run: the files still without `carries` name `amends` in the
scope-change context only (modes.md, prompt-templates.md, follow-up-prompts.template.md,
agent-control.template.md, the drift-register and progress-sync skills, lab/README.md, migration
004) — `carries` does not belong beside them. Lint 7 required the migration to be named in the
CHANGELOG, so the 5.0.0 `[Unreleased]` block starts here (plan 117 completes it).
