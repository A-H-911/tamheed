---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Roadmap — support-triage-agent

Three phases. PH-1 ships a fully supervised assistive system. PH-2 is **gated**: it does not begin until
the calibration experiment passes and the routing decision is approved. PH-3 is operational maturity.
Each phase states goal, scope, deliverables, validation, risks, and an explicit exit gate.

## PH-1 — Assisted triage with human approval (no auto-send)

- **Goal.** Stand up the triage pipeline that drafts grounded replies and routes them for human approval,
  with every safety invariant enforced from the first commit.
- **Scope.** `FR-001`–`FR-007`; `NFR-001`–`NFR-005`; `INV-001`–`INV-005`.
- **Deliverables.** Ingest (`FR-001`); classify category + urgency (`FR-002`); retrieve context (`FR-003`);
  grounded draft with citation-or-defer (`FR-004`, `ADR-0002`); route/escalate to the human queue
  (`FR-005`); human-in-the-loop approval gate before send (`FR-006`, `ADR-0001`); append-only audit trail
  (`FR-007`); bounded tool-allow-list loop with cost/iteration cap (`ADR-0003`, validated by `POC-001`).
- **Validation.** `AC-001`–`AC-005`; `TEST-001`–`TEST-006`.
- **Top risks.** `RISK-001`, `RISK-002`, `RISK-003`, `RISK-004`.
- **Exit gate.** No reply sent without approval (`AC-003`); every draft cites context or defers (`AC-002`);
  no PII leaves the boundary (`AC-004`); full audit trace per email (`AC-005`); classify+route correct on
  the labeled sample (`AC-001`); cost cap holds (`TEST-006`). **Auto-send remains off.**

## PH-2 — Calibration, confidence routing, and gated auto-send  *(CONDITIONAL)*

- **Entry gate (unmistakable).** PH-2 does **not** start until **`EXP-001` = PASS** *and*
  **`ADR-0004` / `DEC-004` = Approved** with a Support-Ops + Security-signed-off whitelist. If `EXP-001`
  fails, `ADR-0004` is rejected, `FR-008` stays deferred, and the system remains the PH-1 supervised
  system (`INV-001` everywhere).
- **Goal.** Once accuracy is measured and calibrated, enable confidence-based routing and guarded
  auto-send for the named low-risk whitelist only.
- **Scope.** `FR-005` (confidence thresholds), `FR-008`; `KPI-001`, `KPI-002`.
- **Deliverables.** Confidence-based routing/escalation (`ADR-0004`); auto-send (`FR-008`) for the approved
  whitelist only, with a kill-switch and per-category error monitoring; expanded audit/monitoring.
- **Invariants still in force.** `INV-002`, `INV-003`, `INV-004`, `INV-005` unconditionally; `INV-001`
  narrowed only for the whitelisted categories named in the approved decision.
- **Exit gate.** Measured per-category error stays under the agreed bar; kill-switch tested;
  `KPI-001`/`KPI-002` trending to target.

## PH-3 — Broaden categories + ongoing quality monitoring

- **Goal.** Operational maturity: widen the handled-category set and sustain quality.
- **Scope.** Category expansion; continuous monitoring against `KPI-001`/`KPI-002`/`KPI-003`.
- **Deliverables.** Broader coverage; continuous accuracy/quality monitoring; periodic recalibration
  (re-run `EXP-001` on drift).
- **Exit gate.** KPIs hold at target with monitoring in place; quality does not regress as categories
  expand.

## Milestones (MS-)

| ID | Milestone | Phase | Gate |
|---|---|---|---|
| MS-001 | Bounded-loop POC green | pre-PH-1 | `POC-001` PASS |
| MS-002 | Supervised pipeline live (assisted, human-gated) | PH-1 | PH-1 exit gate |
| MS-003 | Calibration result + go/no-go | PH-1→PH-2 | `EXP-001` reported; `DEC-004` resolved |
| MS-004 | Guarded auto-send for the whitelist | PH-2 | PH-2 exit gate |
