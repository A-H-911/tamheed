---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Constraint Register — support-triage-agent

Boundaries the solution must operate within (distinct from requirements, which are things it must do, and
invariants, which are properties that must always hold).

| ID | Constraint | Source | Type | Status |
|---|---|---|---|---|
| CON-001 | The launch configuration must be supervised: no autonomous send before the calibration gate (`EXP-001`) and an approved decision (`ADR-0004`). | `STK-001`, `STK-002` | Operational / safety | Approved |
| CON-002 | All processing must comply with the company PII and data-retention policy; PII handling is dictated by security, not by this project (`ASM-003`). | `STK-002` | Compliance / privacy | Approved |
| CON-003 | The agent must reach the model provider only through a vendor-neutral abstraction; no provider-specific SDK calls in application code (`ASM-004`). | `STK-003` | Architectural / portability | Approved |
| CON-004 | Per-email cost must stay within the operating budget; a run that would exceed the cap is aborted, not completed (`NFR-004`, `INV-005`). | `STK-001`, `STK-003` | Cost | Approved |
| CON-005 | The category/urgency taxonomy and the auto-send whitelist are owned by Support Ops (`STK-004`); the agent must use them as given and not invent categories. | `STK-004` | Organizational | Approved |
