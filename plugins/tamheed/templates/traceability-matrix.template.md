---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
generation: derived          # DERIVED artifact — regenerated from registers, never hand-edited
---

# Traceability Matrix — <project-name>

<!-- DERIVED ARTIFACT. This is generated from the registers and re-derived on every update cycle; do
     NOT hand-maintain it (governance.md, traceability.md). It lets an implementing agent navigate from
     any need to its evidence and back. Generation class: Derived. Lives at:
     validation/traceability-matrix.md. Mirror structured rows to schemas/traceability.schema.json. -->

## The chain

```
Requirement (FR-/NFR-) → Decision (DEC-/ADR-) → Work item (WBS-) → Test (TEST-) → Risk (RISK-) → Acceptance (AC-)
```

## Coverage rule (gate G-TRACE)

Every **MVP** `FR-/NFR-` must link to >=1 decision, >=1 work item, and >=1 test; every requirement
asserting user-visible behavior must link to >=1 acceptance criterion. A required-column gap on an MVP
requirement fails the gate — fix it by adding the missing link or explicitly de-scoping (recorded).

- **coverage** flag per row: `full` | `partial` | `gap`.

## Matrix

| Req | Decisions | Work items | Tests | Risks | Acceptance | Coverage |
|---|---|---|---|---|---|---|
| FR-001 | DEC-002, ADR-0001 | WBS-1.1.1 | TEST-001 | RISK-003 | AC-001 | full |
| FR-002 | DEC-001 | WBS-1.1.2 | TEST-00x | — | AC-00x | partial |
| NFR-001 | ADR-0001 | WBS-1.2.1 | TEST-002 | RISK-001 | AC-002 | full |
| FR-003 | <—> | <—> | <—> | — | <—> | gap |

## Gaps (must be zero for MVP rows at readiness)

<!-- List every row flagged `gap`/`partial` on a required column and the resolution (link added or
     de-scope recorded). Backward check: any WBS-/TEST- tracing to NO requirement is gold-plating or a
     missing requirement — investigate, don't ignore. -->
- `FR-003` — <gap: no test yet> → <action: add TEST-00x / de-scope reason>.
