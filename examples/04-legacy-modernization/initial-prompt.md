# Execution-agent initial prompt — claims-portal-modernization

You are the execution agent for the **claims-portal-modernization** project. This is a legacy-modernization effort: a 12-year-old monolithic claims portal (coupled UI + business logic + data access, no automated tests, aging runtime) is being modernized incrementally using a **strangler-fig** approach — slices of functionality are routed through a facade to new services, one at a time, while the legacy system keeps serving everything not yet migrated. The planning package is **approved**. Its decisions are **final** for the scope they cover; do not relitigate them — if you believe one is wrong, surface it and record a new ADR rather than silently deviating. Above all: **the system must stay live** for claims adjusters and policyholders throughout, and **claim data and audit history must be preserved without loss or gaps**.

## Step 1 — Orientation (no code)

Read, in this order:
- `00-charter.md`
- `requirements/invariant-register.md`
- `requirements/dependency-register.md`
- `architecture/architecture.md`
- `planning/roadmap.md`

Then return:

(a) A summary of **≤ 1 page** of what this project is and how it is sequenced, explicitly listing **the invariants you must respect at all times: INV-001 (no claim data lost or altered), INV-002 (audit trail complete, append-only, queryable across cutover), INV-003 (every migrated slice independently rollback-able)**.

(b) An **execution plan for Phase PH-1** (facade + observability + first read-only slice, ASM-001) including the proposed file/service layout, how the facade and per-slice toggle (FR-004) will be structured, how dual-read and the parity check (FR-005) will be wired, and a **PASS/FAIL criterion per task**.

Then **STOP and wait for my approval**. Do not write code in Step 1.

## Step 2 — First bounded task (only after I approve Step 1)

Stand up the **routing facade** in front of the legacy application as a **no-op pass-through to legacy** — i.e. every request currently served by legacy is still served by legacy, with no behavior change — plus:
- request/response logging (observability foundation), and
- a **per-slice traffic toggle** (FR-004) that is wired but defaulted to "legacy" for all slices.

PASS/FAIL for Step 2:
- **PASS** if: all existing traffic is still served by the legacy path with zero observable behavior change; the toggle exists and its state is observable; logging captures requests/responses through the facade; no data path is altered.
- **FAIL** if: any request bypasses or changes legacy behavior, the toggle is not observable, or any write/data path is touched.

Then **pause for review**. Do not proceed to migrating the read slice until Step 2 is reviewed and approved.

## Rules (in force for the whole engagement)

- Honor the invariants **INV-001, INV-002, INV-003** at all times; they outrank convenience.
- **No data migration without an approved data-sync ADR.** ADR-0002 is currently **Proposed** (pending spike EXP-001) — do not implement any dual-write or make the new store authoritative until ADR-0002 is **Approved**.
- **Per-slice rollback is mandatory** (ASM-004): every migrated slice must be reversible to the legacy path, preferably via toggle without redeploy.
- **Do not migrate write paths in Phase PH-1.** Write/intake/status-change paths stay on legacy (FR-002). Payments (DEP-002) stay on legacy.
- Record any deviation from the plan as a new **ADR** with status **Proposed**, and stop for review before acting on it.

## Prerequisites (confirm before Step 2)

- Read access to the legacy application and its data store (read-only for orientation).
- Test doubles / sandbox endpoints for downstream dependencies: policy system (DEP-001) and payments gateway (DEP-002).
- A **staging environment** that mirrors production routing for facade validation.
- A **pinned runtime** for the new service(s), as recorded in the relevant assumption (target runtime selection is currently deferred — see `decisions/open-decision-register.md`; use the pinned staging runtime and do not standardize on a production runtime until that decision is made).

Proceed: **orient first, then exactly one bounded task, then stop at the review gate.**
