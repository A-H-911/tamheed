---
id: ADR-0004
status: Proposed
version: 0.1.0
updated: 2026-06-17
supersedes: none
superseded_by: none
---

# ADR-0004 — Confidence-based routing and gated auto-send

## Status
**Proposed** — pending calibration (`EXP-001`) and Support-Ops + Security sign-off on the whitelist
(`DEC-004`). This ADR is *not* Approved and must not be treated as such. While it is Proposed, `FR-008`
(auto-send) is gated and `INV-001` holds for **all** categories. (A Proposed ADR is mutable; it becomes
immutable only when approved.)

## Context
The team's efficiency goal is to stop hand-drafting routine, low-risk replies. That requires trusting the
agent's classification confidence — but confidence is meaningless until it is calibrated against real
outcomes (`HYP-001`). Deciding thresholds now would be premature architecture and would put a
customer-facing safety control on an unmeasured signal.

## Decision (proposed)
Route and escalate by **classification confidence** and **category sensitivity**:
- Low confidence, or any sensitive category (`ASM-002`), always escalates to a human (`FR-005`).
- A **calibrated high-confidence band** on the explicitly whitelisted low-risk categories becomes
  eligible for auto-send (`FR-008`), with a kill-switch and per-category error monitoring.
The numeric thresholds and the eligible whitelist are set **from `EXP-001` results**, not assumed.

## Alternatives considered
- **Fixed confidence threshold chosen up front** — *Rejected (premature).* No basis before calibration.
- **No auto-send ever** — *Held as the fallback.* If `EXP-001` fails, this ADR is rejected and the system
  stays fully supervised (`INV-001` everywhere).

## Consequences
- When approved, narrows `INV-001` *only* for the named whitelist; everything else still requires approval.
- The narrowing and every auto-send are audited (`INV-004`).
- Verified, on approval, by the PH-2 entry criteria (measured per-category error under bar; kill-switch
  tested).

## References
`FR-005`, `FR-008`, `HYP-001`, `EXP-001`, `DEC-004`, `INV-001`, `INV-004`.
