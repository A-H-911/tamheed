---
id: DOC-DECISIONS
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Open decision register

Lightweight decisions (`DEC-`). Architecturally significant ones are promoted
to an ADR; `DEC-002 -> ADR-0001` records such a promotion. Every row carries a
status from the allowed set (Proposed / Approved / Rejected / Superseded /
Deferred).

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DEC-001 | Generate short codes with a base-62 counter. | Approved | Simple, collision-free, sortable. |
| DEC-002 | Store links and counts in a single relational table. | Approved | Promoted to ADR-0001 for blast radius. |
| DEC-003 | Use a thicker cache layer for hot links. | Deferred | Revisit if NFR-001 is missed under load. |
