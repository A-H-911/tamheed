# Clarifications — support-triage-agent

## Clarification batch (asked together)

These questions were raised together because each materially changes scope, safety posture, the architecture, or the evaluation plan. Where a decision-maker answered, the answer is marked `[given]`; where no authoritative answer was available in time, a working assumption was adopted and recorded below.

1. **What classification accuracy bar should the agent meet (NFR-001)?** Needed to set the eval target and to decide whether any auto-send is ever defensible.
   Answer (assumed): Initial bar of **≥ 85% top-1 category accuracy** on the labeled evaluation set, with urgency measured separately. This is a starting bar to be confirmed by Support Ops and validated by EXP-001. See ASM-005, NFR-001, HYP-001.

2. **Is auto-send ever in scope, and for which risk class?** The brief wants it eventually; we must not let that ambition erode the launch safety posture.
   Answer (given): **Not at launch.** Auto-send is a Phase PH-2 capability (FR-008), restricted to an explicitly whitelisted set of **low-risk categories**, and is **gated** on EXP-001 PASS and approval of ADR-0004. Until then INV-001 holds absolutely. See FR-008, ADR-0004, EXP-001.

3. **What end-to-end latency budget per email is acceptable (NFR-002)?** Sets the loop/iteration budget and the retrieval/draft design.
   Answer (assumed): Target **≤ 30 seconds** end-to-end per email from ingest to draft-ready-for-review (p95), since a human reviews before send and seconds-level latency is not required. To be confirmed with Support Ops. See NFR-002.

4. **What is the per-email cost budget (NFR-004)?** Bounds the loop and model usage and protects against runaway cost.
   Answer (assumed): Target **≤ $0.05 per triaged email** (model + retrieval) as a planning baseline, enforced by a hard per-run cost/iteration cap (INV-005). To be confirmed against measured usage. See NFR-004, INV-005, ADR-0003.

5. **What is the source and size of the labeled evaluation corpus?** Without it, neither NFR-001 nor EXP-001 can be measured.
   Answer (given): Support Ops will provide a **labeled corpus of past emails** (category + urgency labels) of at least a few thousand items, drawn from real history with PII handled per Security policy. Availability is a precondition for EXP-001. See ASM-001, EXP-001.

6. **Who owns the category/urgency taxonomy and the escalation rules?** Determines classification targets and routing/escalation behavior.
   Answer (given): **Support Operations** owns and provides the category + urgency taxonomy and the escalation rules, and approves triage behavior. See ASM-002, FR-002, FR-005.

7. **Who is the authority on PII handling, and what counts as PII (NFR-003 / INV-003)?** Determines the trust boundary, what may reach which tool, and what may be logged.
   Answer (given): **Security** owns the PII handling and retention policy and the definition of sensitive data. PII must not cross the trust boundary into unapproved tools, models, or logs. See ASM-003, NFR-003, INV-003, AC-004.

8. **What model-provider constraints apply — single vendor or abstracted?** Affects the architecture boundary and portability.
   Answer (given): **No vendor lock-in.** The model/LLM provider is accessed only through a provider abstraction; the email system, knowledge base, and review queue are likewise behind clean boundaries. No vendor is named in the plan. See ASM-004, DEP-001..DEP-004.

## Assumptions recorded

| ID | Assumption | Basis | Risk if wrong | Status |
|----|------------|-------|---------------|--------|
| ASM-001 | A labeled evaluation corpus of past emails (category + urgency) is available for measuring accuracy and running EXP-001. | Clarification 5; Support Ops commitment. | No corpus means NFR-001 is unmeasurable, EXP-001 cannot run, and auto-send (FR-008) can never be unlocked. | Proposed |
| ASM-002 | The category and urgency taxonomy and the escalation rules are provided and owned by Support Operations. | Clarification 6; Support Ops owns triage behavior. | Wrong/changing taxonomy invalidates classifier targets (FR-002) and routing rules (FR-005). | Proposed |
| ASM-003 | PII handling, retention, and the definition of sensitive data follow company Security policy; PII must not leave the trust boundary. | Clarification 7; Security owns the policy. | A wrong PII model risks INV-003 breach, regulatory exposure, and loss of trust. | Proposed |
| ASM-004 | The model/LLM provider is behind a vendor-neutral abstraction; email, KB, and queue are behind clean boundaries; no vendor is selected in the plan. | Clarification 8; "no lock-in" requirement. | Direct vendor coupling defeats portability and contaminates the agent core with vendor types. | Proposed |
| ASM-005 | The initial NFR-001 accuracy bar is ≥ 85% top-1 category accuracy on the eval set (urgency measured separately), pending confirmation and EXP-001. | Clarification 1; planning baseline. | A wrong bar mis-sets the quality gate and the auto-send eligibility threshold (FR-008). | Proposed |

## Contradictions / tensions

- **Desire to auto-send (cut handling time) vs. safety (no wrong/unsafe reply to a customer).** The brief wants the agent to eventually send replies on its own, but a customer-facing send is exactly where a wrong or hallucinated reply does harm (RISK-001). **Resolution:** hold INV-001 absolutely at launch — no external reply is sent without human approval — and **defer auto-send to Phase PH-2 (FR-008)**, restricted to an explicitly whitelisted low-risk category set and **gated on EXP-001 calibration PASS and approval of ADR-0004** (currently Proposed). Auto-send is unlocked by measured evidence, not by ambition. No hard contradiction remains: PH-1 is fully assisted-with-approval, and the auto-send path is a separate, gated phase with its own exit bar.
