# Plan 117: docs + diagrams sweep for v5.0.0

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW

## Why this matters

Every teaching and repo surface that names the front door, the prompt library, the note's contents, the relation roster or the install route must say what 5.0.0 does.

## What changes

README, server README, generated-structure (tree), handoff.md, governance, quality-gates, artifact-catalog, prompt-templates.md, extension.md (006 beside 005), install.md (plugin route; project enablement; restart after update; the manual route's unverified nesting; "v4 store under 5.x"), SECURITY.md, architecture.md (sequence + an "instruction surfaces" diagram), entities.md, methodology.md, CONTRIBUTING.md, CLAUDE.md layout, CHANGELOG 5.0.0 with the name mapping and `006_carries.sql`.

## Done criteria

- [ ] per-behaviour grep ≥ 2 docs
- [ ] `python check.py`
- [ ] CI green
