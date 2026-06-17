# Representative artifacts — support-triage-agent

Filled excerpts from the generated package. These are representative, not exhaustive; full content lives in the files listed in `structure.md`. All cross-references are by ID.

## Functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| FR-001 | The agent SHALL ingest incoming support emails from the mailbox/queue and create a triage record for each. | input (ingest pipeline); DEP-002 | MVP | Approved |
| FR-002 | The agent SHALL classify each email into a category and an urgency level per the Support-Ops taxonomy. | input (classify); ASM-002 | MVP | Approved |
| FR-003 | The agent SHALL retrieve relevant knowledge-base/context for the email before drafting. | input (retrieve); DEP-003 | MVP | Approved |
| FR-004 | The agent SHALL draft a proposed reply grounded in retrieved context, citing its sources. | input (draft, grounded); INV-002 | MVP | Approved |
| FR-005 | The agent SHALL route/escalate to the correct human queue when confidence is low or the category is sensitive. | input (route/escalate); ASM-002; OQ-002 | MVP | Approved |
| FR-006 | The agent SHALL require explicit human approval before any reply is sent (human-in-the-loop). | input (human approval before send); INV-001 | MVP | Approved |
| FR-007 | The agent SHALL log every action, tool call, and decision with rationale to an append-only audit trail. | input (full audit log); INV-004 | MVP | Approved |
| FR-008 | The agent SHALL auto-send replies for a whitelisted set of low-risk categories after sustained measured accuracy. | input (later auto-send); ASM-005; OQ-001; gated by EXP-001/ADR-0004 | Full (PH-2) | Proposed |

Note: FR-008 (auto-send) is **Proposed** and **gated** — it does not begin until EXP-001 = PASS and ADR-0004 = Approved. Until then INV-001 holds absolutely.

## Non-functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| NFR-001 | Classification SHALL meet the accuracy bar: ≥ 85% top-1 category accuracy on the labeled eval set (urgency measured separately). | input (accuracy); ASM-005; Clarification 1 | MVP | Approved |
| NFR-002 | End-to-end triage latency SHALL be ≤ 30 s per email (p95) from ingest to draft-ready-for-review. | input (latency); Clarification 3 | MVP | Approved |
| NFR-003 | No PII SHALL leak to unauthorized tools, models, or logs; PII stays within the trust boundary. | input (protect PII); ASM-003; INV-003 | MVP | Approved |
| NFR-004 | Cost per triaged email SHALL stay within budget: ≤ $0.05 (model + retrieval), enforced by a per-run cap. | input (bounded cost); ASM-005; Clarification 4; INV-005 | MVP | Approved |
| NFR-005 | Every email SHALL have a full, reconstructable decision trace (auditability). | input (full audit); INV-004 | MVP | Approved |

## Invariants

These are the crown jewels of the package — always-true safety properties that constrain every change.

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | The agent never sends an external reply without human approval (until FR-008 is explicitly enabled per category via an approved decision). | A wrong reply to a customer does real harm; the approval gate is the primary safety control (FR-006, ADR-0001, AC-003). |
| INV-002 | The agent never fabricates facts in a reply — every claim is grounded in retrieved context, or the agent defers to a human. | Hallucinated answers mislead customers and destroy trust; grounding-or-defer makes fabrication structurally impossible (FR-004, ADR-0002, AC-002). |
| INV-003 | No PII leaves the trust boundary — PII is never sent to unapproved tools, models, or logs. | Personal data exposure is a security and regulatory failure (NFR-003, ASM-003, AC-004). |
| INV-004 | Every action and tool call is logged with inputs, outputs, and rationale, to an append-only audit trail. | Auditability is required to defend decisions and meet review obligations (FR-007, NFR-005, AC-005). |
| INV-005 | The agent operates within an explicit tool allow-list and a per-run cost/iteration budget — no unbounded loops. | Prevents runaway cost and uncontrolled actions; bounds the blast radius of any failure (ADR-0003, RISK-004, NFR-004). |

## Dependencies

| ID | Dependency | Type | Criticality | Notes |
|----|------------|------|-------------|-------|
| DEP-001 | LLM / model provider (abstracted) | External service (abstracted) | Critical | Accessed only through a vendor-neutral model port (ADR-0003 boundary; ASM-004). No vendor named in the plan. Supports FR-002/FR-004. |
| DEP-002 | Email system / mailbox / queue | External service | Critical | Source of inbound email (FR-001) and the send channel (gated by FR-006/INV-001). Test double required for non-prod. |
| DEP-003 | Knowledge base / retrieval source | External service / data source | Critical | Supplies grounding context (FR-003); grounding-or-defer (INV-002) depends on it. Test corpus required for eval. |
| DEP-004 | Human-review queue / ticketing system | External service | Critical | Receives drafts for approval and escalations (FR-005, FR-006). The HITL gate (ADR-0001) writes here. |

## ADRs (two full + two summarized)

### ADR-0001 — Human-in-the-loop approval gate before send
**Status: Approved**

- **Context.** This is a customer-facing system and a wrong or unsafe reply harms a customer and the brand (RISK-001). The brief makes human approval before send non-negotiable at launch (INV-001).
- **Decision.** No external reply is sent until a human explicitly approves it. The agent produces a draft and routes it to the human-review queue (DEP-004); send is a separate, human-gated action (FR-006). The gate is unconditional in PH-1 and may be relaxed only per explicitly whitelisted categories via a future approved decision (see ADR-0004 / FR-008).
- **Alternatives considered (rejected).** *Auto-send from day one* — rejected: removes the only human safety control on a customer-facing channel before accuracy is measured; unacceptable risk (RISK-001).
- **Consequences.** Strong safety and trust; humans remain the bottleneck on send (the very thing PH-2 aims to relax, but only with evidence). Enables the audited approval action (FR-007).
- **References:** INV-001, FR-006, RISK-001, AC-003.

### ADR-0002 — Retrieval-grounded drafting (RAG) with citation-or-defer
**Status: Approved**

- **Context.** The agent must never fabricate facts (INV-002). A free-generating model can produce plausible but wrong answers (RISK-001). Drafts must be defensible against the knowledge base.
- **Decision.** Drafts are generated from retrieved knowledge-base context (FR-003) and **must cite the retrieved sources** for their claims. If the agent cannot ground an answer in retrieved context, it **defers to a human** rather than guessing (FR-004). Email content is treated as data to answer, never as instructions to follow (see RISK-003).
- **Alternatives considered (rejected).** *Free-form generation without retrieval grounding* — rejected: cannot guarantee INV-002 and invites hallucinated, unsupported claims.
- **Consequences.** Every draft is traceable to sources; coverage gaps surface as deferrals rather than fabrications. Retrieval quality (DEP-003) becomes a first-class concern and is measured in EXP-001 alongside classification.
- **References:** INV-002, FR-004, RISK-001, AC-002.

### ADR-0003 — Bounded agent loop with tool allow-list + cost/iteration cap (summary)
**Status: Approved.** The agent runs inside a bounded loop constrained to an explicit tool allow-list with a hard per-run cost and iteration cap; no unbounded loops or off-list tool calls. Directly enforces INV-005 and mitigates runaway cost (RISK-004); supports FR-001..FR-005 and the cost budget NFR-004. Validated early by POC-001.

### ADR-0004 — Confidence-based routing & escalation policy (summary)
**Status: Proposed — pending calibration (EXP-001).** Route/escalate by classification confidence and category sensitivity: low confidence or sensitive categories escalate to humans (FR-005); a calibrated high-confidence band on whitelisted low-risk categories becomes auto-send eligible (FR-008). The confidence thresholds depend on HYP-001/EXP-001 results and are **not** final — this ADR stays Proposed and FR-008 stays gated until EXP-001 = PASS and this ADR is approved. **References:** FR-005, FR-008, HYP-001, EXP-001.

## Risk register (excerpt)

| ID | Risk | Impact | Likelihood | Mitigation | Owner | MVP/Full |
|----|------|--------|-----------|------------|-------|----------|
| RISK-001 | A wrong or hallucinated reply harms a customer. | High | Medium | Human approval before send (INV-001, ADR-0001, AC-003); retrieval grounding with citation-or-defer (INV-002, ADR-0002, AC-002). | Eng lead (STK-003) | MVP |
| RISK-002 | PII leaks to an unapproved tool, model, or log. | High | Medium | PII stays within the trust boundary (INV-003, NFR-003); Security PII policy (ASM-003); negative tests asserting no PII egress (AC-004). | Security lead (STK-002) | MVP |
| RISK-003 | Prompt-injection via malicious email content drives unintended actions. | High | Medium | Treat email content as data, never as instructions; bounded tool allow-list (INV-005, ADR-0003); the agent never acts on instructions embedded in an email; outputs grounded and human-gated (ADR-0001/0002). | Eng lead (STK-003) | MVP |
| RISK-004 | Runaway agent loop or unbounded cost. | Medium | Medium | Hard per-run cost/iteration cap and tool allow-list (INV-005, ADR-0003, NFR-004); validated by POC-001. | Eng lead (STK-003) | MVP |

## Hypothesis + experiment

**HYP-001** — Classification accuracy meets the NFR-001 bar (≥ 85% top-1 category) on a labeled email sample, and a confidence threshold exists that isolates a low-risk subset safe enough to auto-send.

**EXP-001 — Confidence calibration + accuracy measurement on a labeled corpus.**
- **Setup.** Run classification over the labeled corpus (ASM-001); measure top-1 category accuracy and urgency accuracy; calibrate confidence and analyze error rate per category and per confidence band.
- **PASS condition.** Accuracy ≥ NFR-001 bar **AND** a confidence threshold exists that yields a whitelisted low-risk auto-send subset at ≤ X% measured error (X agreed with Support Ops + Security before the run).
- **FAIL condition.** Accuracy below bar, or no confidence threshold produces a sufficiently low-error low-risk subset → auto-send stays disabled.
- **Timebox.** Bounded spike; results recorded in `experiments/exp-001-confidence-calibration.md`.
- **Unblocks.** ADR-0004 (Proposed → Approved on PASS) and FR-008 (auto-send enablement for the named whitelist). On FAIL, FR-008 remains deferred and INV-001 holds for all categories.

## Roadmap (phases)

### PH-1 — Assisted triage with human approval (NO auto-send)
- **Goal.** Stand up the full triage pipeline that drafts grounded replies and routes them for human approval, with every safety invariant enforced.
- **Deliverables.** Ingest (FR-001); classify category + urgency (FR-002); retrieve context (FR-003); grounded draft with citation-or-defer (FR-004, ADR-0002); route/escalate to human queue (FR-005); human-in-the-loop approval gate before send (FR-006, ADR-0001); append-only audit trail (FR-007); bounded tool-allow-list loop with cost/iteration cap (ADR-0003); PII containment (NFR-003).
- **Exit criteria.** No reply sent without approval (AC-003); every draft cites context or defers (AC-002); no PII leaves the boundary (AC-004); full audit trace per email (AC-005); classify+route correct on the labeled sample (AC-001). Auto-send remains **off**.

### PH-2 — Calibration + confidence routing + auto-send for whitelisted low-risk categories
- **Goal.** Once accuracy is measured and calibrated, enable confidence-based routing and guarded auto-send for a named low-risk whitelist.
- **Deliverables.** Confidence-based routing/escalation (ADR-0004); auto-send (FR-008) for the explicitly whitelisted low-risk categories only, with a kill-switch and per-category error monitoring; expanded audit/monitoring dashboards.
- **Gate (unmistakable).** PH-2 auto-send does **not** start until **EXP-001 = PASS** *and* **ADR-0004 = Approved**, and even then auto-send is limited to the categories explicitly named in that approved decision. Everything else still requires human approval (INV-001).
- **Exit criteria.** Measured per-category error stays under the agreed bar; kill-switch tested; INV-002/INV-003/INV-004/INV-005 continue to hold.

### PH-3 — Broaden categories + ongoing quality monitoring
- **Goal.** Operational maturity: widen the handled-category set and sustain quality.
- **Deliverables.** Broader category coverage; continuous accuracy/quality monitoring against KPI-001 (deflection/auto-handle rate), KPI-002 (human handling time saved), KPI-003 (reply quality/accuracy); periodic recalibration.
- **Exit criteria.** KPIs trend to target with monitoring in place; quality does not regress as categories expand.

## Acceptance criteria (excerpt)

| ID | Given / When / Then | Verifies |
|----|---------------------|----------|
| AC-001 | **Given** an email from the labeled sample, **when** the agent classifies and routes it, **then** the predicted category/urgency and routing match the labeled expectation within the NFR-001 bar. | FR-002, FR-005, NFR-001 |
| AC-002 | **Given** an email to draft a reply for, **when** the agent produces a draft, **then** every factual claim cites retrieved context, or the agent defers to a human. | FR-004, INV-002 |
| AC-003 | **Given** a completed draft, **when** no human has approved it, **then** no external reply is sent. | FR-006, INV-001 |
| AC-004 | **Given** an email containing PII, **when** the agent processes it, **then** no PII is sent to any unapproved tool, model, or log. | INV-003, NFR-003 |
| AC-005 | **Given** any processed email, **when** the audit trail is inspected, **then** a full decision trace (actions, tool calls, inputs, outputs, rationale) exists for it. | FR-007, INV-004, NFR-005 |

---

**Cross-reference integrity:** ADR-0001 ↔ INV-001 / FR-006 / AC-003; ADR-0002 ↔ INV-002 / FR-004 / AC-002; ADR-0003 ↔ INV-005 / RISK-004 / NFR-004; INV-003 ↔ NFR-003 ↔ AC-004; FR-007 / INV-004 ↔ NFR-005 ↔ AC-005; ADR-0004 (Proposed) ↔ FR-008 (gated) ↔ HYP-001 / EXP-001; PH-2 auto-send conditional on EXP-001 PASS + ADR-0004 approval; model/email/KB/queue remain vendor-neutral throughout (DEP-001..DEP-004, ASM-004).
