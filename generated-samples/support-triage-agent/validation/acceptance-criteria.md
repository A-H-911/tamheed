---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Acceptance Criteria — support-triage-agent

Testable acceptance criteria (`AC-NNN`), each in Given/When/Then form, each naming the requirement(s) and
invariant(s) it verifies. Approved acceptance criteria are immutable; change only by superseding.

| ID | Given / When / Then | Verifies | Phase |
|---|---|---|---|
| AC-001 | **Given** an email from the labeled sample, **when** the agent classifies and routes it, **then** the predicted category/urgency and routing match the labeled expectation within the `NFR-001` bar. | `FR-002`, `FR-005`, `NFR-001` | PH-1 |
| AC-002 | **Given** an email to draft a reply for, **when** the agent produces a draft, **then** every factual claim cites retrieved context, or the agent defers to a human. | `FR-004`, `INV-002` | PH-1 |
| AC-003 | **Given** a completed draft, **when** no human has approved it, **then** no external reply is sent. | `FR-006`, `INV-001` | PH-1 |
| AC-004 | **Given** an email containing PII, **when** the agent processes it, **then** no PII is sent to any unapproved tool, model, or log. | `INV-003`, `NFR-003` | PH-1 |
| AC-005 | **Given** any processed email, **when** the audit trail is inspected, **then** a full decision trace (actions, tool calls, inputs, outputs, rationale) exists for it. | `FR-007`, `INV-004`, `NFR-005` | PH-1 |

## Notes
- `FR-008` (auto-send) has **no MVP acceptance criterion** by design — it is gated to PH-2 and its
  acceptance lives in the PH-2 entry/exit criteria (measured per-category error under bar; kill-switch
  tested). Writing an "Approved" auto-send AC now would imply a capability that is not yet decided.
- `AC-001` is also the in-harness accuracy check feeding `EXP-001`.
