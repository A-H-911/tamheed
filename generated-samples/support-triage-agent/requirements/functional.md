---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Functional Requirements — support-triage-agent

What the system must DO. One row per requirement (`FR-NNN`). Every `FR` carries a `source` (gate
G-REQ-SRC) and a `status`. Priority is `MVP` or `Full`. Each `FR` is reachable in the
[traceability matrix](../validation/traceability-matrix.md) to ≥1 decision, ≥1 task, ≥1 test, and (for
user-visible behavior) an acceptance criterion.

## Conventions

- **Statement** — testable "the system shall …" phrasing; what, not how.
- **Source** — input span, `STK-`, `OQ-` resolution, `ASM-`, or derived-from.
- **Priority** — `MVP` (ships in PH-1) or `Full` (PH-2/PH-3).
- **Status** — Draft | Proposed | Approved | Implemented | Rejected | Deferred | Superseded | Obsolete.

## Requirements

| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| FR-001 | The agent shall ingest incoming support emails from the mailbox/queue and create one triage record per email. | input (ingest pipeline); `DEP-002` | MVP | Approved |
| FR-002 | The agent shall classify each email into a category and an urgency level per the Support-Ops taxonomy. | input (classify); `ASM-002` | MVP | Approved |
| FR-003 | The agent shall retrieve relevant knowledge-base context for an email before drafting a reply. | input (retrieve); `DEP-003` | MVP | Approved |
| FR-004 | The agent shall draft a proposed reply grounded in retrieved context, citing the sources for its claims, or defer to a human when it cannot ground an answer. | input (draft, grounded); `INV-002` | MVP | Approved |
| FR-005 | The agent shall route or escalate an email to the correct human queue when classification confidence is low or the category is sensitive. | input (route/escalate); `ASM-002`; `OQ-002` | MVP | Approved |
| FR-006 | The agent shall require explicit human approval before any reply is sent to a customer (human-in-the-loop). | input (human approval before send); `INV-001` | MVP | Approved |
| FR-007 | The agent shall log every action, tool call, and decision — with inputs, outputs, and rationale — to an append-only audit trail. | input (full audit log); `INV-004` | MVP | Approved |
| FR-008 | The agent shall auto-send replies for an explicitly whitelisted set of low-risk categories, after sustained measured accuracy and an approved decision. | input (later auto-send); `ASM-005`; `OQ-001`; gated by `EXP-001` / `ADR-0004` | Full | Proposed |

> **`FR-008` is `Proposed` and gated.** Auto-send does not begin until `EXP-001` = PASS **and**
> `ADR-0004` = Approved, and even then only for the categories named in that approved decision. Until
> then `INV-001` holds for every category. Rendering `FR-008` as Approved before the gate would violate
> the decision-status safeguard.

## Detail (selected)

### FR-004 — Grounded drafting with citation-or-defer
- **Rationale:** a free-generating model can produce plausible but wrong answers; grounding makes
  fabrication structurally hard (`INV-002`, `RISK-001`).
- **Behavior:** the draft must cite the retrieved `DEP-003` sources backing its claims; if no retrieved
  context supports an answer, the agent defers to a human instead of guessing. Email content is treated
  as data to answer, never as instructions to follow (`RISK-003`).
- **Acceptance:** `AC-002`. **Decision:** `ADR-0002`.

### FR-006 — Human-in-the-loop approval gate
- **Rationale:** the only unconditional safety control on a customer-facing channel before accuracy is
  measured (`INV-001`, `RISK-001`).
- **Behavior:** the agent produces a draft and routes it to the human-review queue (`DEP-004`); *send* is
  a separate, human-gated action. The gate is unconditional in PH-1.
- **Acceptance:** `AC-003`. **Decision:** `ADR-0001`.

### FR-008 — Gated auto-send (Full)
- **Rationale:** the team's eventual efficiency goal, but only once trust is earned by measurement.
- **Behavior:** for the approved low-risk whitelist only, a calibrated high-confidence reply may be sent
  without human approval, with a kill-switch and per-category error monitoring; everything else still
  routes for approval (`INV-001`).
- **Gate:** `EXP-001` PASS + `ADR-0004` Approved. **Acceptance:** covered under PH-2 entry criteria.
