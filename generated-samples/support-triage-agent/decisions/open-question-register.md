---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Open Question Register — support-triage-agent

Questions whose answer could change the plan. Blocking questions are answered or consciously deferred
with an `ASM-`/risk before scope lock (gate G-OQ); non-blocking ones are listed as accepted-open.

| ID | Question | Blocking? | Resolution | Status |
|---|---|---|---|---|
| OQ-001 | Which categories, if any, may ever be auto-sent, and at what measured error bar? | Yes (for PH-2; not PH-1) | Deferred to the calibration gate: the eligible whitelist is decided from `EXP-001` results with Support-Ops + Security sign-off (`DEC-004`). PH-1 proceeds with auto-send off (`CON-001`). | Accepted-open (PH-2) |
| OQ-002 | What confidence threshold and which "sensitive" categories must always escalate to a human? | Yes (for routing) | Sensitive categories from the taxonomy (`ASM-002`) always escalate; the numeric confidence threshold is calibrated in `EXP-001` (`ADR-0004`, `FR-005`). | Resolved (rule) / threshold pending `EXP-001` |
| OQ-003 | What are the exact accuracy and latency targets? | Yes | Answered: `NFR-001` ≥ 85% top-1; `NFR-002` ≤ 30 s p95 (`ASM-005`, clarification batch). | Resolved |
| OQ-004 | How long is processed email + draft data retained, and where? | No (governed by policy) | Governed by the security/retention policy (`ASM-003`, `CON-002`); the agent complies, it does not set the policy. | Accepted-open (policy-owned) |
