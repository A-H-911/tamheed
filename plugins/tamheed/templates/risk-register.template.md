---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Risk Register — <project-name>

<!-- Risks across technical, dependency, platform, and delivery dimensions. High-impact requirements
     and decisions should have a risk view (gate G-RISK).
     Identified RISK-NNN (governance.md). Generation class: Always.
     Lives at: risks/risk-register.md. -->

## Conventions

- **Impact** and **Likelihood** — rate `1` (low) to `5` (high), or Low/Med/High consistently.
- **Exposure** — Impact x Likelihood (or a Low/Med/High band); use it to rank.
- **Mitigation** — the plan to reduce likelihood or impact (preventive).
- **Trigger** — the early signal that the risk is materializing (when to act / invoke fallback).
- **MVP-or-Full** — whether the risk applies to the MVP scope, the Full target, or both.
- **Owner** — who watches it. **Status** — Draft | Proposed | Approved | Deferred | Superseded | Obsolete.

## Risks

| ID | Description | Impact | Likelihood | Exposure | Mitigation | Trigger | MVP/Full | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| RISK-001 | <what could go wrong and its effect> | 4 | 3 | 12 | <preventive plan; fallback option> | <observable early signal> | MVP | <role> | Proposed |
| RISK-002 | <dependency X unavailable / changes> | 5 | 2 | 10 | <alternative DEP-00x; abstraction layer> | <vendor deprecation notice> | Both | <role> | Proposed |
| RISK-003 | <delivery: scope larger than estimated> | 3 | 4 | 12 | <phase gating; cut Full items first> | <PH-1 slips by > N> | Full | <role> | Draft |

## Acknowledged trade-offs

<!-- Conflicts with no clean win — state the trade and the chosen side, so it is a decision, not a drift. -->
- <competing goals, e.g. determinism vs upgrade cadence> — chose <side> because <reason>; accepted cost:
  <what we give up>.

## Ambiguities & resolution paths

<!-- Under-specified inputs and how each gets closed; each becomes an OQ-, an ASM-, or a spike. -->
| Ambiguity | Resolution path |
|---|---|
| <vague term / missing quantity> | <becomes OQ-00x / ASM-00x / EXP-00x> |

## Notes

<!-- Reference what each risk threatens (FR-/NFR-/DEC-/DEP-/PH-) so the traceability matrix can link
     risks back to needs. A risk with no mitigation and high exposure is itself a readiness concern. -->
