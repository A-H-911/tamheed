# Traceability

The traceability matrix is what lets an implementing agent navigate from any need to its evidence and back.
It is a **derived** artifact — generated from the registers, never hand-maintained — and is re-derived on
every update cycle.

## The chain

```
Requirement (FR-/NFR-)
   → Decision (DEC-/ADR-)        why it's built this way
   → Work item (WBS-)            where it gets built
   → Test (TEST-)               how we know it works
   → Risk (RISK-)               what could go wrong
   → Acceptance criterion (AC-) when it's done / accepted
```

Not every requirement touches every column, but the gate (`G-TRACE`) requires: every MVP `FR-/NFR-` links
to ≥1 decision, ≥1 work item, and ≥1 test; every requirement asserting user-visible behavior links to ≥1
acceptance criterion.

## Representation

Markdown table for humans, mirrored by structured rows conforming to `../schemas/traceability.schema.json`
for tooling. One row per requirement, with comma-separated linked IDs per column, plus a `coverage` flag
(`full` / `partial` / `gap`).

| Req | Decisions | Work items | Tests | Risks | Acceptance | Coverage |
|---|---|---|---|---|---|---|
| FR-001 | DEC-002, ADR-0001 | WBS-1.2 | TEST-004 | RISK-003 | AC-001 | full |

## Building & checking

1. After Stage 16, walk each requirement and collect links from the registers (decisions cite requirements;
   WBS items cite requirements; tests cite requirements/AC; risks cite what they threaten).
2. Compute `coverage`; flag any `gap`.
3. `G-TRACE` fails on any MVP requirement with a gap in a required column — fix by adding the missing
   decision/task/test or by explicitly de-scoping the requirement (recorded).
4. On updates (Stage 21), re-derive; a superseded item's links move to its successor.

## Bidirectional

The matrix reads forward (need → evidence) and backward (a test/risk → the needs it serves). Backward links
catch orphans: a work item or test that traces to no requirement is either gold-plating or a missing
requirement — investigate, don't ignore.
