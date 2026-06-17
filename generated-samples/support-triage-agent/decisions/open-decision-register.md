---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Open Decision Register — support-triage-agent

Decisions and their explicit status. Architecturally significant decisions are **promoted** to ADRs (the
link is recorded here so it is never lost). Status is exactly one of: **Proposed, Approved, Rejected,
Superseded, Deferred**. A `Proposed` or `Deferred` decision is never rendered as Approved.

| ID | Decision | Status | Rationale (short) | Promoted to | Trigger to revisit |
|---|---|---|---|---|---|
| DEC-001 | Launch supervised: human approval before every send in PH-1. | Approved | Safety before speed; no accuracy evidence yet. | `ADR-0001` | — |
| DEC-002 | Ground all drafts in retrieved context with citation-or-defer. | Approved | Prevents fabrication (`INV-002`). | `ADR-0002` | — |
| DEC-003 | Run the agent in a bounded loop with a tool allow-list and a cost/iteration cap. | Approved | Bounds cost and blast radius (`INV-005`, `RISK-004`). | `ADR-0003` | — |
| DEC-004 | Adopt confidence-based routing and gated auto-send for whitelisted low-risk categories. | Proposed | Depends on calibration; thresholds not yet known. | `ADR-0004` | `EXP-001` PASS + Support-Ops/Security sign-off on the whitelist |
| DEC-005 | Defer the choice of agent-orchestration pattern (single-pass vs multi-step planner) until the bounded-loop POC reports. | Deferred | Avoid premature architecture; the seam (`ADR-0003`) is fixed, the internal pattern is not. | — | `POC-001` result |
| DEC-006 | Keep auto-send (`FR-008`) out of PH-1 scope. | Approved | Gated on `DEC-004`/`EXP-001`; including it now would violate the supervised-launch constraint (`CON-001`). | — | Re-opened by `DEC-004` approval |

## Notes

- `DEC-004` is the pivot decision for PH-2. It stays **Proposed** until `EXP-001` passes and the
  whitelist is signed off; only then does it (and `ADR-0004`) move to Approved and unlock `FR-008` for the
  named categories.
- `DEC-005` demonstrates the *no premature architecture* safeguard: the externally-visible contract is
  decided (`ADR-0003`), but the internal orchestration pattern is consciously deferred to evidence
  (`POC-001`), not guessed.
