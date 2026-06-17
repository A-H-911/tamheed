---
id: DOC-DECISIONS
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Open decision register

DEFECT (G-DEC-STATUS): DEC-002 below has an empty Status cell.

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DEC-001 | Generate short codes with a base-62 counter. | Approved | Simple and collision-free. |
| DEC-002 | Store links and counts in a single relational table. |  | Promoted to ADR-0001. |
| DEC-003 | Use a thicker cache layer for hot links. | Deferred | Revisit under load. |
