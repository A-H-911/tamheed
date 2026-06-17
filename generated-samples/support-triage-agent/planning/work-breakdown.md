---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Work Breakdown — support-triage-agent

Leaf items are actionable and testable (gate G-EXEC). Each cites the requirement(s) it realizes so the
[traceability matrix](../validation/traceability-matrix.md) can link need → work → test.

## WBS-1 — Foundations (pre-PH-1)
- **WBS-1.1** Vendor-neutral model/tool ports + bounded-loop skeleton (allow-list, cost/iteration cap).
  Realizes `ADR-0003`, `INV-005`. Validated by `POC-001`, `TEST-006`.
- **WBS-1.2** Append-only audit logging substrate (inputs, outputs, rationale per action).
  Realizes `FR-007`, `INV-004`. Validated by `TEST-005`.

## WBS-2 — Ingest & classify (PH-1)
- **WBS-2.1** Email ingestion from the mailbox/queue; one triage record per email.
  Realizes `FR-001` (`DEP-002`).
- **WBS-2.2** Classification into category + urgency per the taxonomy.
  Realizes `FR-002` (`ASM-002`). Validated by `TEST-001`.

## WBS-3 — Retrieve & draft (PH-1)
- **WBS-3.1** Knowledge-base retrieval for an email.
  Realizes `FR-003` (`DEP-003`).
- **WBS-3.2** Grounded drafting with citation-or-defer.
  Realizes `FR-004`, `ADR-0002`, `INV-002`. Validated by `TEST-002`.

## WBS-4 — Route, approve, send (PH-1)
- **WBS-4.1** Routing/escalation to the correct human queue (sensitive → always escalate).
  Realizes `FR-005` (`DEP-004`).
- **WBS-4.2** Human-in-the-loop approval gate; send only after explicit approval.
  Realizes `FR-006`, `ADR-0001`, `INV-001`. Validated by `TEST-003`.
- **WBS-4.3** PII-containment boundary across all tool calls and logs.
  Realizes `INV-003`, `NFR-003`. Validated by `TEST-004`.

## WBS-5 — Calibration (PH-1→PH-2 gate)
- **WBS-5.1** Evaluation harness over the labeled corpus; accuracy + confidence calibration + coverage.
  Realizes `EXP-001` (`HYP-001`, `HYP-002`). Validated by `TEST-001`.

## WBS-6 — Confidence routing & gated auto-send (PH-2, conditional)
- **WBS-6.1** Confidence-threshold routing per the calibrated policy.
  Realizes `FR-005` (thresholds), `ADR-0004`. *Blocked by `EXP-001` PASS + `ADR-0004` Approved.*
- **WBS-6.2** Guarded auto-send for the approved whitelist; kill-switch; per-category error monitoring.
  Realizes `FR-008`. *Blocked by the same gate.*
