---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Risk Register — support-triage-agent

Risks across technical, dependency, safety, and delivery dimensions. Impact and likelihood are scored
H/M/L; each top risk has an owner, a mitigation, and (where relevant) a trigger. High-impact items have a
view in the [traceability matrix](../validation/traceability-matrix.md) (gate G-RISK).

| ID | Risk | Impact | Likelihood | Mitigation | Owner | MVP/Full |
|---|---|---|---|---|---|---|
| RISK-001 | A wrong or hallucinated reply reaches and harms a customer. | High | Medium | Human approval before send (`INV-001`, `ADR-0001`, `AC-003`); retrieval grounding with citation-or-defer (`INV-002`, `ADR-0002`, `AC-002`). | STK-003 | MVP |
| RISK-002 | PII leaks to an unapproved tool, model, or log. | High | Medium | PII stays inside the trust boundary (`INV-003`, `NFR-003`); security PII policy (`ASM-003`, `STK-002`); negative egress tests (`AC-004`, `TEST-004`). | STK-002 | MVP |
| RISK-003 | Prompt-injection via malicious email content steers the agent into unintended actions. | High | Medium | Treat email content as data, never instructions; explicit tool allow-list and bounded loop (`INV-005`, `ADR-0003`); outputs grounded and human-gated (`ADR-0001`/`ADR-0002`). | STK-003 | MVP |
| RISK-004 | Runaway agent loop or unbounded cost. | Medium | Medium | Hard per-run cost/iteration cap + allow-list (`INV-005`, `ADR-0003`, `NFR-004`); validated by `POC-001`; cost alerting from the audit trail. | STK-003 | MVP |
| RISK-005 | Auto-send enabled on an over-optimistic accuracy read (mis-calibration). | High | Medium | Auto-send gated on `EXP-001` PASS + approved whitelist (`DEC-004`/`ADR-0004`); per-category error monitoring and kill-switch in PH-2; `INV-001` holds until then. | STK-001 | Full |
| RISK-006 | Knowledge base is stale or thin, so grounding coverage is low and deferral rate is high (low deflection). | Medium | Medium | Measure retrieval coverage in `EXP-001`; deferral is safe (`INV-002`); feed gaps back to KB owners; track against `KPI-001`. | STK-004 | MVP |
