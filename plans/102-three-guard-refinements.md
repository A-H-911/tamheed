# Plan 102: three guard refinements (findings_29 §1, §3, §4)

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: MEDIUM (three guards; security reviewer)

## What changes

1. `go_no_go` is PRESENCE-checked: naming it without the operator's word is refused whatever the
   value (the 4.12.0 brief's probe could not fail); the audit row is still written only when the
   verdict moves.
2. `substitute` refuses the re-run shape: when `new` contains `old` AND `new` already occurs in the
   stored column — a second run would compound (`scripts/X` → `src/Acmp.Web/src/Acmp.Web/scripts/X`).
   Order: zero-occurrence → digit-glue → re-run → `custom_attributes` JSON. The remedy is in the
   message: send old/new with the characters that bound them.
3. `expect_unchanged`: an omitted column is preserved by the UPDATE (`:1657`; the retire path's
   precedent at `:1500`) and never counts as drift; a SENT column must still match. The
   `entity_upsert` docstring stops saying "Send FULL rows" unconditionally.
4. Wording: the JSON refusal guards `custom_attributes`, not "a JSON column".

## Done criteria

- [ ] RED then GREEN; `python check.py`; security reviewer's findings closed or recorded
- [ ] dry-run on a fixture copy
- [ ] CI green
