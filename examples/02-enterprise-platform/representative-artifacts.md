# Representative artifacts — unify-billing

Filled excerpts from the generated package. These are representative, not exhaustive; full content lives in the files listed in `structure.md`. All cross-references are by ID.

## Functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| FR-001 | The public API SHALL ingest usage events idempotently: an event carrying an idempotency key already processed produces no additional billing effect. | input (public usage API; idempotent ingestion); INV-003 | MVP | Approved |
| FR-002 | The platform SHALL support flat-rate and per-seat pricing models. | input (pricing models); ASM-001 | MVP | Approved |
| FR-003 | The platform SHALL generate invoices per tenant at billing-period close. | input (invoicing); ASM-002 | MVP | Approved |
| FR-004 | The platform SHALL prorate charges when a tenant changes plan mid-cycle (upgrade or downgrade). | input (proration) | MVP | Approved |
| FR-005 | The platform SHALL compute tax for invoices by calling an external tax service. | input (tax via external service); DEP-002 | MVP | Approved |
| FR-006 | The platform SHALL run dunning and retry on failed payments via a configurable retry policy. | input (dunning/retry); DEP-001 | Full (PH-2) | Approved |
| FR-007 | The platform SHALL expose a tenant-facing billing portal (invoices, plan, payment status). | input (tenant portal) | Full (PH-2) | Approved |
| FR-008 | The platform SHALL expose an internal admin console for tenant, plan, and correction management. | input (admin console) | MVP | Approved |

Note: usage-based/metered pricing is tracked as FR-009 (Full / PH-2, Status: Proposed) and is gated on EXP-001; it is intentionally excluded from MVP per ASM-001 and is not shown in this excerpt.

## Non-functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| NFR-001 | Tenant data SHALL be isolated; no operation may read or write across tenant boundaries. | input (tenant isolation); INV-002 | MVP | Approved |
| NFR-002 | Monetary computation SHALL exhibit no rounding drift; for any closed period the ledger SHALL reconcile (entries sum to zero). | input (financial correctness); INV-001, INV-004 | MVP | Approved |
| NFR-003 | Event ingestion SHALL be idempotent: a duplicate event id yields exactly one billing effect. | input (idempotent ingestion); INV-003 | MVP | Approved |
| NFR-004 | Ingestion SHALL sustain the target scale (500 tenants; 5,000,000 usage events/day in PH-2) with aggregation latency ≤ 5 minutes at period close. | ASM-004; Clarification 3 | Full (PH-2) | Approved |
| NFR-005 | Every money movement (charge, credit, refund, adjustment) SHALL be auditable and traceable to its originating cause. | input (auditable money movement; SOC2) | MVP | Approved |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | Every financial transaction is recorded immutably and the ledger reconciles: across any consistent cut, the sum of debit and credit entries balances to zero. | Finance must reconcile and the system must never create or destroy money; underpins auditability (NFR-002, NFR-005). |
| INV-002 | Tenant data is isolated: no code path reads or writes another tenant's data. | Hard requirement; breach is a security and contractual failure (NFR-001). |
| INV-003 | Event ingestion is idempotent: replaying an event with the same idempotency key never produces a second billing effect. | Product teams retry; double-charging on retry is financially incorrect (FR-001, NFR-003). |
| INV-004 | Monetary amounts are represented as integer minor units; no floating-point arithmetic is performed on money. | Eliminates rounding drift at the representation level; enables exact reconciliation (ASM-003, NFR-002). |

## Dependencies

| ID | Dependency | Type | Criticality | Notes |
|----|------------|------|-------------|-------|
| DEP-001 | Payment provider | External service (abstracted) | Critical | Accessed only through a vendor-neutral provider port (ADR-0003); exactly one provider at MVP (ASM-005); no vendor named in the plan. Supports FR-006. |
| DEP-002 | External tax service | External service | Critical | Computes tax per FR-005; must be available at invoice close; test double required for non-prod (see prerequisites). |
| DEP-003 | Identity / SSO provider | External service | High | Authenticates admin-console and portal users; supports SOC2 access controls (NFR-005). |
| DEP-004 | Currency / FX rate source | External data feed | Medium (High in PH-2) | Supplies exchange rates for multi-currency invoicing; rate snapshot must be recorded per invoice for auditability. |

## Technology comparison (excerpt) — ledger / accounting model

**Criteria and weights** (sum = 1.0): Auditability **0.35**, Correctness guarantees **0.30**, Query/reporting ease **0.20**, Implementation cost **0.15** (higher fit = lower cost/effort).

| Option | Auditability (0.35) | Correctness guarantees (0.30) | Query/reporting ease (0.20) | Implementation cost (0.15) |
|--------|---------------------|-------------------------------|-----------------------------|----------------------------|
| Append-only event log + projections | Partial | Partial | Weak | Strong |
| Double-entry ledger (source of truth) + projections | Strong | Strong | Strong | Partial |
| Hybrid (event log feeding a derived ledger) | Strong | Partial | Partial | Weak |

Fit legend: Strong / Partial / Weak / Unknown.

**Verdict:** The double-entry ledger as source of truth scores highest on the two heaviest criteria (auditability, correctness) and remains strong for reporting via projections, at a moderate implementation cost. Selected; recorded in **ADR-0001**. Residual implementation-cost risk is retired by **POC-001** before Phase-1 build.

## ADRs

### ADR-0001 — Double-entry ledger as the money source of truth; projections for reporting
**Status: Approved**

- **Context.** Finance requires reconciliation that balances to zero and a defensible audit trail (INV-001, NFR-002, NFR-005). Money must never be created or destroyed and amounts must be exact (INV-004). Multiple models were viable (see technology comparison).
- **Decision.** Adopt an immutable, append-only **double-entry ledger** as the authoritative record of all money movement. Balances and reports are **projections** derived from ledger entries, never the source of truth. All amounts are integer minor units (INV-004).
- **Alternatives considered (rejected).** (a) *Mutable balances table* — rejected: in-place updates destroy the audit trail and admit drift, violating INV-001. (b) *Event-log-only without ledger semantics* — rejected: does not guarantee a balancing double-entry record; reconciliation would be reconstructed ad hoc.
- **Consequences.** Strong auditability and exact reconciliation; reporting requires maintained projections; corrections are expressed as compensating entries, never edits. Enables invoice generation (FR-003) on a trustworthy basis. Validated by POC-001.
- **References:** INV-001, INV-004, FR-003, NFR-002, NFR-005; technology-comparison verdict.

### ADR-0003 — Payment provider behind a provider port (hexagonal)
**Status: Approved**

- **Context.** The provider must be pluggable; the company may switch or run multiple providers (input hard requirement; ASM-005, DEP-001). Direct vendor coupling would violate this.
- **Decision.** Define a **provider port** (a domain-owned interface for authorize/capture/refund/retry and webhook normalization). Each concrete provider is an adapter behind the port. The billing core depends only on the port; no vendor SDK types leak across the boundary. Exactly one adapter ships at MVP (ASM-005).
- **Alternatives considered (rejected).** *Direct SDK coupling* — rejected: hard-wires a vendor, defeats pluggability, and contaminates the domain with vendor types.
- **Consequences.** New providers are added as adapters without touching the core; supports dunning/retry (FR-006) uniformly; testing uses a port test double. Slight upfront cost to define a sufficiently general port.
- **References:** DEP-001, FR-006; input hard requirement (pluggable provider); ASM-005.

### ADR-0002 — Asynchronous invoice generation at period close
**Status: Proposed (pending review with finance)**

- **Context.** The brief desired real-time invoicing, but reconciliation and proration correctness favor a batch close (see clarifications tension; ASM-002). Invoices depend on the ledger being consistent for the period (FR-003, NFR-002).
- **Decision (proposed).** Generate invoices **asynchronously at billing-period close** from the ledger, rather than synchronously per request. Real-time invoice *previews* may be offered later as projections without changing the source of truth.
- **Alternatives considered (rejected, provisionally).** *Synchronous per-request invoicing* — rejected for MVP: complicates correctness/reconciliation and couples request latency to financial computation.
- **Consequences.** Cleaner reconciliation and proration; invoices are not instantaneous on plan change (preview mitigates). **This decision is not final** — it awaits finance sign-off and must not be rendered as Approved until then.
- **References:** FR-003, NFR-002, ASM-002.

## Risk register (excerpt)

| ID | Risk | Impact | Likelihood | Mitigation | Owner | MVP/Full |
|----|------|--------|-----------|------------|-------|----------|
| RISK-001 | Rounding/precision drift causes reconciliation failures. | High | Medium | Integer minor units + single round-half-to-even point (INV-004, ASM-003); reconciliation test asserting balance-to-zero (AC-002). | Platform lead (STK-002) | MVP |
| RISK-002 | Cross-tenant data leakage. | High | Medium | Enforced isolation boundary (INV-002, ADR-0004); negative tests denying cross-tenant access (AC-004). | Platform lead (STK-002) | MVP |
| RISK-003 | Duplicate event ingestion double-charges a tenant. | High | Medium | Idempotency keys + dedupe at the ingestion boundary (INV-003, FR-001); replay tests (AC-001). | Platform lead (STK-002) | MVP |
| RISK-004 | Payment-provider lock-in or outage disrupts billing. | Medium | Medium | Provider port abstraction (ADR-0003, DEP-001); retry/dunning policy (FR-006); provider test double for resilience tests. | Platform lead (STK-002) | MVP/Full |

## Roadmap (phases)

### PH-1 — MVP money core and isolation
- **Goal.** Establish a trustworthy, isolated money foundation with flat/per-seat billing and audited invoices.
- **Deliverables.** Tenant model + isolation boundary (INV-002); double-entry ledger + integer-minor-unit money model (INV-001, INV-004); flat + per-seat pricing (FR-002); proration (FR-004); async invoice generation at close (FR-003, ADR-0002); tax via external service (FR-005, DEP-002); single payment provider via the provider port (ADR-0003, ASM-005); admin console basics (FR-008); end-to-end audit trail (NFR-005).
- **Exit criteria.** Ledger reconciles to zero in tests (AC-002); cross-tenant access denied (AC-004); duplicate posting is a no-op (AC-001); invoices generate correctly at close (AC-003); tax applied via the external service (AC-005). ADR-0002 finance review complete.

### PH-2 — Usage pricing, dunning, portal, multi-currency hardening
- **Goal.** Add metered revenue and customer-facing surfaces once metering is proven.
- **Deliverables.** Usage-based/metered pricing (FR-009) — **gated on EXP-001 PASS**; dunning/retry state machine (FR-006); tenant billing portal (FR-007); multi-currency hardening with recorded FX snapshots (DEP-004); ingestion at target scale (NFR-004).
- **Exit criteria.** Metered aggregation accurate per EXP-001 result with idempotency preserved (INV-003); dunning state machine verified; portal live; ingestion sustains NFR-004 targets.
- **Gate:** PH-2 metered-pricing scope does **not** start until **EXP-001 = PASS** and **ADR-0002 = Approved**.

### PH-3 — Reporting, webhooks, multi-provider, SOC2 evidence
- **Goal.** Operational maturity and audit readiness.
- **Deliverables.** Revenue reporting dashboards; webhooks for billing events; additional payment-provider adapters behind the existing port (ADR-0003); completion of SOC2 evidence collection.
- **Exit criteria.** Dashboards and webhooks in use by stakeholders; ≥1 second provider adapter validated via the port; SOC2 evidence package complete and accepted by Security/Compliance (STK-005).

## Acceptance criteria (excerpt)

| ID | Given / When / Then | Verifies |
|----|---------------------|----------|
| AC-001 | **Given** an event with idempotency key K already processed, **when** the same event is submitted again, **then** no additional ledger entry or charge is created. | FR-001, INV-003 |
| AC-002 | **Given** a closed billing period with posted transactions, **when** the ledger is reconciled, **then** debit and credit entries sum to zero and no float arithmetic was used. | INV-001, INV-004, NFR-002 |
| AC-003 | **Given** a tenant on a flat/per-seat plan at period close, **when** invoice generation runs, **then** an invoice is produced from the ledger for that period. | FR-003 |
| AC-004 | **Given** tenant A's credentials, **when** an operation targets tenant B's data, **then** the request is denied and audited. | INV-002, NFR-001 |
| AC-005 | **Given** an invoice ready to finalize, **when** tax is required, **then** tax is computed via the external tax service and recorded against the invoice. | FR-005, DEP-002 |

---

**Cross-reference integrity:** ADR-0001 ↔ INV-001 / INV-004 / FR-003 (and ↔ AC-002); ADR-0003 ↔ DEP-001 / FR-006; idempotency INV-003 ↔ FR-001 ↔ AC-001; technology-comparison verdict ↔ ADR-0001; PH-2 usage scope gated on EXP-001 (roadmap and readiness agree); payment provider remains vendor-neutral throughout.
