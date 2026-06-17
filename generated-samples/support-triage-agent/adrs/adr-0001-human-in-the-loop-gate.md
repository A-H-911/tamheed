---
id: ADR-0001
status: Approved
version: 1.0.0
updated: 2026-06-17
supersedes: none
superseded_by: none
---

# ADR-0001 — Human-in-the-loop approval gate before send

## Status
Approved (promoted from `DEC-001`). Immutable after approval; change only by a superseding ADR.

## Context
This is a customer-facing system. A wrong, fabricated, or unsafe reply harms a customer and the brand
(`RISK-001`), and at launch there is no measured evidence of accuracy. The brief makes human approval
before send non-negotiable for the supervised launch (`INV-001`, `CON-001`).

## Decision
No external reply is sent until a human explicitly approves it. The agent produces a draft and routes it
to the human-review queue (`DEP-004`); **send is a separate, human-gated action** (`FR-006`). The gate is
unconditional in PH-1. It may be *narrowed* later only for explicitly whitelisted low-risk categories via
an approved decision (`ADR-0004` / `DEC-004`), and even then every other category still requires approval.

## Alternatives considered
- **Auto-send from day one** — *Rejected.* Removes the only human safety control on a customer-facing
  channel before accuracy is measured; unacceptable risk (`RISK-001`).
- **Approval only for low-confidence drafts** — *Rejected for PH-1.* Confidence is uncalibrated until
  `EXP-001`; trusting it before measurement is premature. This becomes viable, scoped, under `ADR-0004`.

## Consequences
- Strong safety and trust; humans remain the bottleneck on send — which is exactly what PH-2 aims to
  relax, but only with evidence.
- The approval action itself is audited (`FR-007`, `INV-004`).
- Verified by `AC-003` and `TEST-003`.

## References
`INV-001`, `FR-006`, `RISK-001`, `AC-003`, `DEC-001`.
