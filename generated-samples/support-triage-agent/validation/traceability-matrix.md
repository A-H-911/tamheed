---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
generated: derived
---

# Traceability Matrix — support-triage-agent

**Derived artifact** — generated from the registers, not hand-maintained; re-derived on every update.
Reads forward (need → evidence) and backward (a test/risk → the needs it serves).

Gate `G-TRACE`: every MVP `FR-/NFR-` links to ≥1 decision, ≥1 work item, and ≥1 test; every
behavior-bearing requirement links to ≥1 acceptance criterion. `coverage` is `full` / `partial` / `gap`.

| Req | Decisions | Work items | Tests | Risks | Acceptance | Coverage |
|---|---|---|---|---|---|---|
| FR-001 | ADR-0003 | WBS-2.1 | TEST-005 | RISK-004 | AC-005 | full |
| FR-002 | ADR-0004 (Proposed), DEC-005 | WBS-2.2 | TEST-001 | RISK-001 | AC-001 | full |
| FR-003 | ADR-0002 | WBS-3.1 | TEST-002 | RISK-006 | AC-002 | full |
| FR-004 | ADR-0002 | WBS-3.2 | TEST-002 | RISK-001 | AC-002 | full |
| FR-005 | ADR-0004 (Proposed) | WBS-4.1, WBS-6.1 | TEST-001 | RISK-001, RISK-005 | AC-001 | full |
| FR-006 | ADR-0001 | WBS-4.2 | TEST-003 | RISK-001 | AC-003 | full |
| FR-007 | DEC-001, ADR-0001 | WBS-1.2 | TEST-005 | RISK-002 | AC-005 | full |
| FR-008 | ADR-0004 (Proposed) | WBS-6.2 | (PH-2 entry) | RISK-005 | (PH-2 entry/exit) | partial — gated to PH-2 |
| NFR-001 | ADR-0004 (Proposed) | WBS-5.1 | TEST-001 | RISK-005 | AC-001 | full |
| NFR-002 | ADR-0003 | WBS-3.2 | TEST-001 | RISK-006 | AC-001 | full |
| NFR-003 | DEC-001 | WBS-4.3 | TEST-004 | RISK-002 | AC-004 | full |
| NFR-004 | ADR-0003 | WBS-1.1 | TEST-006 | RISK-004 | — (covered by INV-005 tests) | full |
| NFR-005 | ADR-0001 | WBS-1.2 | TEST-005 | RISK-002 | AC-005 | full |

## Invariant coverage (backward view)

Every invariant is enforced by a decision, realized in a work item, and demonstrated by a (usually
negative) test and an acceptance criterion.

| Invariant | Decision/ADR | Work item | Test | Acceptance |
|---|---|---|---|---|
| INV-001 | ADR-0001 | WBS-4.2 | TEST-003 | AC-003 |
| INV-002 | ADR-0002 | WBS-3.2 | TEST-002 | AC-002 |
| INV-003 | DEC-001 / CON-002 | WBS-4.3 | TEST-004 | AC-004 |
| INV-004 | ADR-0001 | WBS-1.2 | TEST-005 | AC-005 |
| INV-005 | ADR-0003 | WBS-1.1 | TEST-006 | (negative test; no behavior AC) |

## Notes on coverage

- **`FR-008` is intentionally `partial`.** It is `Proposed` and gated to PH-2; it has a work item
  (`WBS-6.2`) but no Approved MVP test/AC, because its acceptance lives in the PH-2 entry/exit criteria
  (`EXP-001` PASS + `ADR-0004` Approved). This is a *recorded, deliberate* partial, not a `gap` — `G-TRACE`
  evaluates MVP requirements, and `FR-008` is `Full`. Flagging it here keeps the backward view honest.
- **`NFR-004`** has no behavior-bearing acceptance criterion (it is a budget property); it is covered by
  the negative cost-cap test (`TEST-006`) and `INV-005`. Not a gap.
- All decision links point to real rows in [open-decision-register](../decisions/open-decision-register.md);
  `ADR-0004` is shown `(Proposed)` everywhere it appears so the matrix never implies a capability is
  approved before its gate.
- Backward check: every `WBS-` leaf and every `TEST-` traces to at least one requirement or invariant
  above — no orphan work items or tests.
