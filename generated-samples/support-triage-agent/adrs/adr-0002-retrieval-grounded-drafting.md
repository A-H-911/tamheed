---
id: ADR-0002
status: Approved
version: 1.0.0
updated: 2026-06-17
supersedes: none
superseded_by: none
---

# ADR-0002 — Retrieval-grounded drafting with citation-or-defer

## Status
Approved (promoted from `DEC-002`). Immutable after approval.

## Context
The agent must never fabricate facts (`INV-002`). A free-generating model can produce plausible but wrong
answers (`RISK-001`). Drafts must be defensible against the knowledge base, and coverage gaps must fail
safe rather than invent content.

## Decision
Drafts are generated from knowledge-base context retrieved for the email (`FR-003`) and **must cite the
retrieved sources** for their claims. If the agent cannot ground an answer in retrieved context, it
**defers to a human** (escalates) rather than guessing (`FR-004`). Email content is treated as data to be
answered, never as instructions to follow (`RISK-003`).

## Alternatives considered
- **Free-form generation without retrieval grounding** — *Rejected.* Cannot guarantee `INV-002`; invites
  hallucinated, unsupported claims.
- **Retrieve-and-summarize without a defer path** — *Rejected.* Forces an answer even when context is
  absent, converting a safe miss into an unsafe guess.

## Consequences
- Every draft is traceable to its sources; coverage gaps surface as deferrals, not fabrications.
- Retrieval quality (`DEP-003`) becomes a first-class concern and is measured in `EXP-001` alongside
  classification.
- Verified by `AC-002` and `TEST-002`.

## References
`INV-002`, `FR-004`, `FR-003`, `RISK-001`, `AC-002`, `DEC-002`.
