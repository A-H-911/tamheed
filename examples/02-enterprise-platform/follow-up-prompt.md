# Follow-up prompt — Phase PH-2 gate (unify-billing)

## Resume context

Phase **PH-1 is complete and approved**. Confirmed at the gate: the **double-entry ledger reconciles to zero**, **tenant isolation is enforced** (cross-tenant access denied), **flat and per-seat pricing** plus **asynchronous invoice generation at period close** are live, and a **single payment provider is integrated through the provider port** (no direct SDK coupling). The **EXP-001 metering spike has PASSED**, and **ADR-0002** (async invoice generation) has been **Approved** by finance. Phase PH-2 scope is therefore unblocked.

## PH-2 goal

Add metered revenue and customer-facing surfaces: **usage-based/metered pricing**, **dunning/retry on failed payments**, the **tenant billing portal**, and **multi-currency hardening** — all while the financial invariants remain in force.

## Bounded tasks (execute in order, pause for review after each)

**Task 1 — Metered pricing + accurate aggregation (FR-009).** Implement usage-based pricing using the aggregation approach validated by EXP-001.
- PASS: metered charges match the EXP-001-validated aggregation for a known event stream.
- PASS: **idempotent ingestion holds for metered events** — replaying an event id never double-counts or double-charges (INV-003).
- FAIL: any aggregation path that loses or double-counts events, or that bypasses idempotency.

**Task 2 — Dunning / retry state machine (FR-006).** Implement the failed-payment retry policy via the provider port.
- PASS: a failed payment advances through the defined retry/dunning states and terminates correctly (paid, or exhausted → flagged).
- PASS: all provider interactions go **through the provider port** (ADR-0003); no vendor SDK leakage.
- FAIL: a retry path that charges twice, or that couples to a vendor directly.

**Task 3 — Tenant billing portal (FR-007).** Expose the tenant-facing portal (invoices, plan, payment status).
- PASS: a tenant sees **only their own** invoices, plan, and payment status (INV-002, NFR-001).
- PASS: portal reads derive from ledger projections (ADR-0001), not mutable balances.
- FAIL: any cross-tenant data exposure.

## Invariants still in force

INV-001 (ledger reconciles), INV-002 (tenant isolation), INV-003 (idempotency — **especially for metered ingestion**), INV-004 (integer minor units, no float). These continue to take precedence over convenience.

## PH-2 exit gate

All three tasks PASS; metered aggregation meets the EXP-001-validated accuracy and the NFR-004 scale/latency targets (500 tenants; 5,000,000 events/day; ≤ 5 min aggregation latency); dunning state machine verified; portal live with isolation confirmed. On pass, proceed to PH-3 planning (reporting, webhooks, additional provider adapters, SOC2 evidence completion).
