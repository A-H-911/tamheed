---
id: ADR-0003
status: Approved
version: 1.0.0
updated: 2026-06-17
supersedes: none
superseded_by: none
---

# ADR-0003 — Bounded agent loop with tool allow-list and cost/iteration cap

## Status
Approved (promoted from `DEC-003`). Immutable after approval.

## Context
An autonomous agent that calls tools and a model can loop, escalate cost, or be steered into unintended
actions by malicious input (`RISK-003`, `RISK-004`). The system needs a hard ceiling on what the agent
can do and how much it can spend, and a clean seam that keeps the model provider swappable (`CON-003`,
`ASM-004`).

## Decision
The agent runs inside a **bounded loop** constrained to an **explicit tool allow-list**, with a **hard
per-run cost and iteration cap** (`NFR-004`). Off-list tools are unreachable; a run that would exceed the
cap is aborted (fails closed), not completed. The model and external tools are reached only through
vendor-neutral ports, so no provider-specific SDK appears in application code. The internal orchestration
pattern *inside* this boundary (single-pass vs multi-step planner) is intentionally **not** fixed here —
that is `DEC-005`, deferred to `POC-001`.

## Alternatives considered
- **Unbounded ReAct-style loop** — *Rejected.* No ceiling on cost or actions; unacceptable blast radius.
- **Direct provider-SDK calls for speed** — *Rejected.* Couples the system to one vendor and defeats
  `CON-003`/`ASM-004`.

## Consequences
- Runaway cost and uncontrolled actions are structurally bounded (`INV-005`).
- The allow-list plus "email is data, not instructions" is a primary prompt-injection control (`RISK-003`).
- Validated early by `POC-001`; budget enforcement verified by `TEST-006`.

## References
`INV-005`, `NFR-004`, `RISK-003`, `RISK-004`, `DEC-003`, `DEC-005`, `POC-001`.
