---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Dependency Register — support-triage-agent

External systems the project depends on. Each is accessed behind a neutral abstraction so no specific
vendor is hard-wired into the plan (`ASM-004`).

| ID | Dependency | Type | Criticality | Notes |
|---|---|---|---|---|
| DEP-001 | LLM / model provider | External service (abstracted) | Critical | Reached only through a vendor-neutral model port (`ADR-0003` boundary; `ASM-004`). Powers `FR-002` and `FR-004`. No vendor named in the plan. |
| DEP-002 | Email system / mailbox / queue | External service | Critical | Source of inbound email (`FR-001`) and the send channel (gated by `FR-006` / `INV-001`). Test double required for non-prod. |
| DEP-003 | Knowledge base / retrieval source | External service / data source | Critical | Supplies grounding context (`FR-003`); citation-or-defer (`INV-002`) depends on it. A test corpus is required for evaluation. |
| DEP-004 | Human-review queue / ticketing system | External service | Critical | Receives drafts for approval and escalations (`FR-005`, `FR-006`). The HITL gate (`ADR-0001`) writes here. |

## Risk linkage

- A `DEP-001` outage degrades drafting; the bounded loop (`INV-005`) fails closed rather than looping.
- `DEP-003` quality directly affects grounding coverage; gaps surface as deferrals (`INV-002`), not
  fabrications. Retrieval quality is measured in `EXP-001`.
- Vendor lock-in for `DEP-001` is mitigated by the port abstraction (`ADR-0003`); see `RISK-004` context.
