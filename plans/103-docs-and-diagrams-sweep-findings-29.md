# Plan 103: docs + diagrams sweep (findings_29)

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (transactional edit script, one match per edit)

## What changes

The feedback disposition recipe (a partial row: id + NOT NULL columns + the bookkeeping columns;
omitted columns preserved, their absence from `changed_columns` the proof); the substitute
idempotence sentence beside the digit-glue note; "an id check is not a truth check" in both id
rules' notes and quality-gates; name `go_no_go` only when changing it; the two diagrams
(`docs/entities.md` feedback state diagram: the journaled middle and the rule; `docs/architecture.md`
flowchart: the rule and the warning name a row until `resolved_in`); SECURITY.md; the three READMEs;
CHANGELOG `[Unreleased]`.

## Done criteria

- [ ] every behaviour named in ≥ 2 docs; mermaid lint; `python check.py`
- [ ] CI green
