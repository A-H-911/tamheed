# Project Brief — unify-billing (input as provided)

We're a B2B SaaS company and our billing situation has become a genuine liability. Today, billing runs on a tangle of spreadsheets plus one brittle Python script that a single engineer maintains. Every month-end is a fire drill: someone exports usage from three systems, hand-reconciles it in a workbook, runs the script to produce invoices, and then finance spends days chasing discrepancies. We've shipped wrong invoices to customers more than once. We cannot support usage-based pricing at all today, which is now blocking two product launches. And finance has told us plainly: they cannot audit any of this. There is no reliable trail from "money moved" back to "why."

I want us to build a new, multi-tenant subscription billing and invoicing platform — a proper internal product — that replaces the spreadsheets and the script entirely. The platform team will own and build it. Product teams across the company will integrate with it (they need to report usage and read billing state). Finance is a primary stakeholder and must sign off before we go live; they care about correctness and auditability above all.

Capabilities I expect the platform to support:

- Multiple pricing models: flat-rate subscriptions, per-seat pricing, and usage-based/metered pricing (e.g., charge per API call, per GB processed).
- Invoice generation for each tenant per billing period.
- Proration when a tenant changes plans mid-cycle (upgrade/downgrade should be fair to both sides).
- Multi-currency support — we already have customers billed in several currencies.
- Tax calculation via an external tax service (we will not build tax logic ourselves).
- Dunning and retry handling when a payment fails, so we stop leaking revenue to soft failures.
- Three surfaces: a tenant-facing billing portal (customers see invoices, plans, payment status), an internal admin console (our finance/ops staff manage tenants, plans, and corrections), and a public API that product teams call to report usage events and query billing state.

Hard requirements — these are non-negotiable:

- Tenant data isolation. One tenant must never see or affect another tenant's data.
- Auditable money movement. Every charge, credit, refund, and adjustment must be traceable to its cause, and finance must be able to reconcile.
- Idempotent event ingestion. Product teams will retry; reporting the same usage event twice must not double-charge.
- Financial-grade correctness. No rounding drift, no money created or destroyed.
- SOC2-relevant controls. We're pursuing SOC2 and this system will be in scope, so access controls, audit logging, and change traceability matter.
- Pluggable payment provider. Do NOT hard-wire us to one payment vendor. We may switch or run more than one. Abstract the provider behind a clean boundary.

Things we'd like but can live without at first: revenue reporting dashboards for finance and leadership, and webhooks so product teams can subscribe to billing events instead of polling.

There are open questions I don't have crisp answers to, and I'd rather you surface them than guess silently. How accurate does metering need to be, and what ingestion latency is acceptable — seconds, minutes? Should invoices be generated in real time or as a batch at period close? What's the right internal model for the money ledger — an event store, a double-entry ledger, something else? What currency rounding rules do we standardize on? What scale should the MVP target — how many tenants, how many usage events per day? And which pricing models are truly MVP versus a later phase? I have opinions but not decisions on these; treat them as things to pin down.

The outcome I want: a billing platform finance trusts, that product teams can build on, that we can defend in an audit, and that lets us finally sell usage-based plans. Get me a plan I can hand to the platform team to execute.
