---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Non-Functional Requirements — support-triage-agent

How well the system must behave. One row per requirement (`NFR-NNN`). Every `NFR` carries a `source` and
a `status`; thresholds are explicit and testable.

## Requirements

| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| NFR-001 | Classification shall meet the accuracy bar: ≥ 85% top-1 category accuracy on the labeled eval set; urgency accuracy measured and reported separately. | input (accuracy); `ASM-005`; `OQ-003` | MVP | Approved |
| NFR-002 | End-to-end triage latency shall be ≤ 30 s per email at p95, from ingest to draft-ready-for-review. | input (latency); `OQ-003` | MVP | Approved |
| NFR-003 | No PII shall leave the trust boundary — PII is never sent to unauthorized tools, models, or logs. | input (protect PII); `ASM-003`; `INV-003` | MVP | Approved |
| NFR-004 | Cost per triaged email shall stay within budget: ≤ $0.05 (model + retrieval combined), enforced by a per-run cap. | input (bounded cost); `ASM-005`; `INV-005` | MVP | Approved |
| NFR-005 | Every email shall have a full, reconstructable decision trace (auditability). | input (full audit); `INV-004` | MVP | Approved |

## Detail (selected)

### NFR-001 — Accuracy bar
- **Threshold:** ≥ 85% top-1 category accuracy on the labeled corpus (`ASM-001`). Urgency accuracy is
  reported but not gated at this bar in PH-1.
- **Measurement:** `EXP-001` over the labeled corpus; re-measured each model/prompt change.
- **Consequence if unmet:** auto-send (`FR-008`) cannot be enabled; the assistive flow still ships.
- **Acceptance:** `AC-001`. **Test:** `TEST-001`.

### NFR-003 — PII containment
- **Threshold:** zero PII egress to unapproved destinations. "PII" is defined by the security policy
  (`ASM-003`, owned by `STK-002`).
- **Measurement:** negative tests asserting no PII in outbound tool calls or logs; boundary review.
- **Acceptance:** `AC-004`. **Test:** `TEST-004`. **Invariant:** `INV-003`.

### NFR-004 — Cost ceiling
- **Threshold:** ≤ $0.05/email; a hard per-run cost/iteration cap aborts a run that would exceed budget.
- **Measurement:** cost accounting in the audit trail (`FR-007`); alerting on breach.
- **Invariant:** `INV-005`. **Test:** `TEST-006`.
