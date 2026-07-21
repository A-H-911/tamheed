---
id: DOC-DECISIONS
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Open decision register

Lightweight decisions (`DEC-`). Architecturally significant ones are promoted
to an ADR. The "Promoted to" cells deliberately reproduce the mixed-token
dialect found in production packages (field-evidence C12).

| ID | Decision | Status | Rationale | Promoted to |
|---|---|---|---|---|
| DEC-001 | Generate short codes with a base-62 counter. | Approved | Simple, collision-free, sortable. | — |
| DEC-002 | Store links and counts in a single relational table. | Approved | Promoted for blast radius. | ADR-0001 |
| DEC-003 | Use a thicker cache layer for hot links. | Deferred | Revisit if NFR-001 is missed under load. | — |
| DEC-004 | Batch click increments and flush hourly. | Approved | Contention relief without a second store. | n/a (scheduling; amends **DEC-003**'s trigger, see **ADR-0002**) |
| DEC-005 | Keep redirect handler framework-free. | Approved | Latency budget headroom. | n/a (amends **DEC-001** only; no ADR needed) |
