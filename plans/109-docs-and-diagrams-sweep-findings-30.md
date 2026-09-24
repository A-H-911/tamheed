# Plan 109: docs + diagrams sweep (findings_30)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [106-111-batch-findings-30.md](106-111-batch-findings-30.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (transactional script)

## What changes

`substitute` as the cheapest status flip (server README, SKILL.md); the deferred-work lifecycle row and
readiness prose in docs/entities.md; docs/architecture.md's readiness paragraph (`ready` +
`indeterminate`); SECURITY.md; CHANGELOG `[Unreleased]` with the `ready` change first.

## Done criteria

- [x] every behaviour in >= 2 docs (census: indeterminate 8, pointer texts 2, empty fold 2, refusal 6, status flip 2 by meaning, Open+Scheduled 3); the readiness sequence diagram gains the `ready` note; `python check.py`
- [ ] CI green
