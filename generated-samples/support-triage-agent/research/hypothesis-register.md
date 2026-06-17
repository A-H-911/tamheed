---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Hypothesis Register — support-triage-agent

Falsifiable hypotheses behind the gated decisions. Each names the signal that would confirm or refute it
and the experiment that settles it. Status is the hypothesis's evaluation state (`Open` until its
experiment reports).

| ID | Hypothesis | Confirms-if (signal) | Refutes-if | Experiment | Status |
|---|---|---|---|---|---|
| HYP-001 | Classification reaches the `NFR-001` bar (≥ 85% top-1 category) on the labeled corpus, **and** a confidence threshold exists that isolates a low-risk subset safe enough to auto-send (≤ X% error, X agreed pre-run). | Accuracy ≥ 85% and a threshold yields a whitelisted low-risk subset at ≤ X% measured error. | Accuracy < 85%, or no threshold produces a sufficiently low-error low-risk subset. | `EXP-001` | Open |
| HYP-002 | Retrieval supplies grounding for a useful share of routine emails, so the deferral rate is low enough to deliver real deflection (`KPI-001`). | Grounding coverage on the corpus is high enough that projected deflection clears the `KPI-001` target. | Coverage so low that most emails defer, making deflection negligible. | `EXP-001` (coverage metric) | Open |

## Notes
- `HYP-001` is the gate for `FR-008` / `ADR-0004`. Until it is confirmed by `EXP-001`, auto-send stays
  off and `INV-001` holds for all categories — the *decide-after-experiment* safeguard.
- `HYP-002` refuting does not block PH-1 (assisted triage still ships); it lowers the expected deflection
  ceiling and feeds back to the KB owners (`RISK-006`).
