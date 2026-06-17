---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Assumption Register — support-triage-agent

Where Keystone proceeded without a confirmed answer, it recorded an explicit assumption with its
risk-if-wrong rather than quietly deciding (safeguard 3). Assumptions are `Proposed` until the human
confirms them; an assumption that is wrong typically re-opens a requirement or a decision.

| ID | Assumption | Basis | Risk if wrong | Status |
|---|---|---|---|---|
| ASM-001 | A labeled evaluation corpus of representative support emails (with category, urgency, and a reference reply) is available or can be assembled before `EXP-001`. | Clarification batch Q4 ([given]) | No corpus ⇒ `EXP-001` cannot run ⇒ auto-send (`FR-008`) cannot be justified; accuracy (`NFR-001`) unverifiable. | Proposed |
| ASM-002 | Support Ops provides and owns the category + urgency taxonomy and the escalation rules. | Clarification batch Q6 ([given]); `STK-004` | A shifting or ill-defined taxonomy invalidates classification training/eval and routing (`FR-002`, `FR-005`). | Proposed |
| ASM-003 | PII handling and retention follow the company security policy; security (`STK-002`) defines what counts as PII and where it may flow. | Clarification batch Q5 ([given]); `STK-002` | A misread policy risks a privacy breach (`INV-003`, `RISK-002`) or an over-restrictive design. | Proposed |
| ASM-004 | The model provider is reached through a vendor-neutral abstraction; no provider-specific behavior is assumed in application code. | Clarification batch Q7 (assumed) | Hidden coupling to one provider raises switching cost and lock-in (`RISK-004`, `CON-003`). | Proposed |
| ASM-005 | The initial accuracy bar for `NFR-001` is ≥ 85% top-1 category accuracy on the eval set; the cost budget is ≤ $0.05/email. | Clarification batch Q1 ([given]); Q3 (assumed) | A wrong bar mis-gates auto-send: too low ships unsafe automation, too high blocks viable automation (`FR-008`, `EXP-001`). | Proposed |
