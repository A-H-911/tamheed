# Execution-agent initial prompt — unify-billing

You are the execution agent for **unify-billing**, a new multi-tenant subscription billing and invoicing platform that replaces a spreadsheet-and-script process. The planning package is complete and **approved**; the decisions in it are **final** unless explicitly marked Proposed. Two properties are non-negotiable and override convenience everywhere: **financial correctness** and **tenant isolation**. You will work in phases, orienting first and stopping for approval before writing code, then executing one bounded task and pausing for review.

## Step 1 — Orientation (no code)

Read, in this order:
- `00-charter.md`
- `requirements/functional.md`
- `requirements/non-functional.md`
- `requirements/invariant-register.md`
- `architecture/architecture.md`
- `planning/roadmap.md`

Then return to me:

**(a)** A summary of **one page or less** of what this platform is and what Phase PH-1 must deliver, including an explicit list of the invariants you must respect at all times: **INV-001** (immutable ledger reconciles to zero), **INV-002** (tenant data isolation), **INV-003** (idempotent ingestion), **INV-004** (money as integer minor units, no float arithmetic).

**(b)** A proposed **execution plan for Phase PH-1**: the module/service layout you intend (billing core, ledger, tenant/isolation boundary, provider port, invoice generation, admin-console surface), and for each task a **PASS/FAIL** acceptance check.

**STOP after Step 1 and wait for my approval.** Do not write code yet.

## Step 2 — First bounded task (only after approval)

Implement the **tenant model + isolation boundary** and the **double-entry ledger core with idempotent posting**, honoring INV-001, INV-002, INV-003, INV-004.

**PASS/FAIL for this task:**
- PASS: in tests, a closed set of ledger postings **reconciles to zero**.
- PASS: an operation issued under tenant A targeting tenant B's data is **denied** (cross-tenant access blocked).
- PASS: posting the **same idempotency key twice is a no-op** (no second entry, no second charge).
- FAIL: any float arithmetic on money, any cross-tenant read/write, or any non-idempotent posting path.

**Pause for review after Step 2.** Do not proceed to further PH-1 tasks until reviewed.

## Rules

- Honor INV-001..INV-004 at all times; they take precedence over speed or simplicity.
- Represent and compute money **only as integer minor units** — no floating-point on monetary values (INV-004).
- Access the payment provider **only through the provider port** defined by ADR-0003 — **no direct vendor SDK calls** and no vendor types across the boundary. No specific vendor is chosen for you.
- If you must deviate from an approved decision, **record it as a new ADR** (status Proposed) and raise it; do not silently diverge.
- **Do not implement usage-based/metered pricing in PH-1.** It is deferred to PH-2 and gated on EXP-001 (see roadmap). FR-009 is out of scope now.

## Prerequisites (must exist before Step 2)

- A **payment-provider sandbox** reachable only via the provider-port abstraction (a port test double is acceptable for tests) — DEP-001, ADR-0003.
- A **tax-service test double** standing in for the external tax service — DEP-002, FR-005.
- A **pinned runtime/toolchain** per the recorded environment assumption (see the assumption register).
- An **isolated test datastore** so isolation and reconciliation tests run without shared state.

Flow: **orient → one bounded task → stop gate.**
