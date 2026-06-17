# Clarifications — unify-billing

## Clarification batch (asked together)

These questions were raised together because each materially changes the plan, scope, or architecture. Where a decision-maker answered, the answer is marked `[given]`; where no authoritative answer was available in time, a working assumption was adopted and recorded below.

1. **Which pricing models are MVP versus later?** Flat and per-seat are well understood; usage-based/metered carries real uncertainty (accuracy, aggregation, latency).
   Answer (given): MVP = flat + per-seat. Usage-based/metered is deferred to Phase 2 and gated on a metering accuracy/ledger spike. See ASM-001, EXP-001.

2. **Real-time invoicing or batch at period close for MVP?** Real-time invoicing was mentioned as desirable in the brief.
   Answer (assumed): Async/batch invoice generation at period close for MVP. Real-time per-request invoicing conflicts with reconciliation and financial-correctness goals (see tension below). See ASM-002, candidate decision ADR-0002.

3. **What metering accuracy and acceptable ingestion latency are required?** Needed to size the metering design and set NFR thresholds.
   Answer (given): For usage events (Phase 2), target eventual aggregation accuracy of 100% (no lost/double-counted events under retry) with acceptable ingestion-to-aggregation latency of up to 5 minutes at period close. Exact mechanism to be validated by EXP-001. Drives NFR-003, NFR-004.

4. **What rounding / currency-precision rule do we standardize on?** Required to prevent rounding drift and reconciliation failures.
   Answer (given): Store all monetary amounts as integer minor units (e.g., cents) in the currency's smallest denomination; apply banker's rounding (round-half-to-even) at the single point where fractional results occur. No floating-point arithmetic on money. See ASM-003, INV-004.

5. **What scale should the MVP target — number of tenants and usage events per day?** Sets NFR throughput targets and informs the metering/ledger design.
   Answer (assumed): MVP scale target of 500 tenants and a Phase-2 ingestion target of 5,000,000 usage events/day. See ASM-004, NFR-004.

6. **Is a double-entry ledger required for audit, or is an append-only event log sufficient?** This is the single most architecturally significant question.
   Answer (assumed pending spike): Treat double-entry ledger semantics as the working baseline for the money source of truth because finance requires reconciliation that balances to zero; an event-log-only approach is a candidate but unproven for our audit needs. To be confirmed by POC-001 and recorded in ADR-0001. See INV-001.

7. **What is the SOC2 audit timeline and who is the controlling authority?** Determines how much compliance evidence must exist at GA versus later.
   Answer (given): SOC2 Type II observation window begins after GA; the platform must implement SOC2-relevant controls (access control, audit logging, change traceability) from MVP, but full evidence collection completes in Phase 3. Authority: company Security/Compliance lead (STK-005). Drives compliance constraints.

8. **One payment provider at MVP, or several behind the abstraction?** Affects scope and the provider boundary design.
   Answer (assumed): Integrate exactly one payment provider at MVP, behind a vendor-neutral provider-port abstraction; additional providers are Phase 3. No specific vendor is selected in the plan. See ASM-005, ADR-0003, DEP-001.

## Assumptions recorded

| ID | Assumption | Basis | Risk if wrong | Status |
|----|------------|-------|---------------|--------|
| ASM-001 | MVP pricing = flat + per-seat; usage-based/metered deferred to Phase 2 pending the metering spike (EXP-001). | Clarification 1; usage metering carries the most uncertainty. | If usage pricing is needed at MVP, Phase 1 scope and the launch dependency are wrong. | Proposed |
| ASM-002 | Invoice generation is asynchronous/batch at period close for MVP (not real-time per request). | Clarification 2; reconciliation and correctness favor batch close. | If real-time invoicing is a hard MVP need, the invoicing architecture (ADR-0002) must change. | Proposed |
| ASM-003 | Monetary amounts stored as integer minor units; round-half-to-even applied at the single rounding point. | Clarification 4; financial-correctness requirement. | Float or inconsistent rounding causes reconciliation drift and audit failure. | Proposed |
| ASM-004 | MVP scale target is 500 tenants; Phase-2 ingestion target is 5,000,000 usage events/day. | Clarification 5; planning baseline. | Under-sizing forces rework of ingestion/aggregation; over-sizing wastes effort. | Proposed |
| ASM-005 | Exactly one payment provider is integrated at MVP, behind a vendor-neutral provider-port abstraction. | Clarification 8; "pluggable provider" hard requirement. | Coupling to a vendor SDK undermines the pluggability requirement and Phase-3 multi-provider goal. | Proposed |

## Contradictions / tensions

- **"Real-time invoicing" (desired in brief) vs. financial-correctness + reconciliation.** Real-time per-request invoicing makes period-close reconciliation and proration harder to keep correct, and complicates a balancing ledger. **Resolution:** adopt asynchronous invoice generation at period close for MVP (ASM-002), captured as decision ADR-0002 (currently Proposed, pending finance review). Real-time invoice *previews* remain possible later without changing the source of truth.
- **"Append-only event log might suffice" vs. finance's reconcile-to-zero audit need (INV-001).** An event-log-only model is attractive for ingestion but does not by itself guarantee a balancing ledger. **Resolution path:** baseline on double-entry ledger semantics; validate with POC-001 and record the choice in ADR-0001 before Phase-1 build of the money core.
- **Usage-pricing desire vs. metering uncertainty.** The desire to sell usage-based plans (a launch blocker) conflicts with genuine unknowns in metering accuracy/latency. **Resolution path:** defer usage pricing to Phase 2 (ASM-001) and gate it on EXP-001 PASS so the launch commitment is based on validated capability, not hope.
