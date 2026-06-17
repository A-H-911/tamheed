# Representative artifacts — claims-portal-modernization

Real filled excerpts from the generated package. These are illustrative slices of the full artifacts, chosen to show the cross-referencing that holds the package together (ADR-0002 ↔ INV-001/INV-002 ↔ EXP-001/HYP-001; INV-003 ↔ ADR-0001 ↔ rollback acceptance criteria; PH-2 gated on EXP-001).

## Functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| FR-001 | Route claim-status read views through the strangler facade to a new claim-status service, transparently to end users. | input.md; ASM-001 | Must | Approved |
| FR-002 | Maintain legacy claim intake and status-change (write) paths unchanged and fully operational throughout the migration. | input.md (system stays live) | Must | Approved |
| FR-003 | Preserve and expose the existing claim audit trail to users and downstream consumers without gaps across the migration. | input.md (audit retention); DEP-003 | Must | Approved |
| FR-004 | Provide a per-slice traffic toggle that routes a slice to either the legacy path or the new service, observable and changeable without redeploy. | input.md (rollback); ASM-004 | Must | Approved |
| FR-005 | Verify data parity between legacy and the new service for each migrated slice before and after cutover. | input.md (zero data loss); ASM-002 | Must | Approved |

## Non-functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| NFR-001 | No claim data is lost or corrupted during migration (verified by reconciliation; 0 unexplained discrepancies). | input.md; INV-001 | Must | Approved |
| NFR-002 | Audit trail remains complete, append-only, and immutable across the cutover (no record deleted or mutated). | input.md; INV-002; DEP-003 | Must | Approved |
| NFR-003 | Adjuster claim-status page load improves to p95 ≤ 1.5s for migrated read views (baseline to be measured in PH-1). | input.md (would-like: faster pages) | Should | Approved |
| NFR-004 | Any planned cutover maintenance window is bounded to ≤ 30 minutes, off-hours, and pre-announced; steady state is zero unplanned downtime. | ASM-003; DEC-001 (candidate) | Must | Approved |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | No claim data is lost or altered during migration. | Regulated insurer with retention obligations; data integrity is the load-bearing property of the whole effort. Any approach that risks silent loss/alteration is disqualified. |
| INV-002 | The audit trail remains complete, append-only, and queryable across the cutover. | Audit history of who-did-what-to-a-claim-when is a regulatory artifact; a gap or mutation during migration is a compliance failure, not a bug. |
| INV-003 | Every migrated slice is independently rollback-able to the legacy path. | Live system; a misbehaving slice must be recoverable without collateral impact on other slices, ideally via toggle (ASM-004). |

## Dependencies

| ID | Dependency | Type | Criticality | Notes |
|----|------------|------|-------------|-------|
| DEP-001 | Policy administration system | External system (read) | Critical | New claim-status service must read policy details consistently with how legacy reads them; contract must not break when traffic shifts. |
| DEP-002 | Payments gateway | External system (write/handoff) | Critical | Approved payout handoff must continue working; payment paths are out of scope for early slices and remain on legacy until explicitly migrated. |
| DEP-003 | Regulatory retention schedule (Compliance & Records) | Compliance / process | Critical | Owner of retention duration and audit requirements; sign-off required before any slice that touches stored claim data is cut over. Gates INV-001/INV-002 acceptance. |

## Two ADRs

### ADR-0001 — Strangler facade with per-slice routing
**Status:** Approved

**Context.** The legacy claims portal couples UI, business logic, and data access in one deployable on an aging runtime, with no automated tests. A big-bang rewrite is unacceptable (the system must stay live and data must be preserved). We need a seam that lets us move functionality slice by slice while the old system keeps serving everything not yet migrated.

**Decision.** Introduce a facade (reverse proxy / routing layer) in front of the legacy application. All client traffic enters through the facade. A per-slice routing toggle (FR-004) decides, per functional slice, whether a request is served by the legacy path or by a new service. New services are introduced behind the facade one slice at a time, starting with claim-status read views (ASM-001).

**Alternatives considered.**
- *Big-bang rewrite* — rejected: unacceptable risk to a live, regulated system; long dark period; high data-loss exposure.
- *Parallel-run only (build new system entirely, run alongside, flip once)* — rejected: still effectively big-bang at cutover; no incremental value; large reconciliation surface at a single high-risk moment.

**Consequences.** Enables incremental migration and per-slice rollback (INV-003). Adds a facade as a new critical-path component (must be highly available and observable). Requires discipline: each slice needs a parity check (FR-005) and a rollback route. Satisfies FR-001 and FR-004; underpins INV-003.

**References:** FR-001, FR-004, INV-003, ADR-0003.

### ADR-0002 — Data synchronization: dual-read with legacy as source of truth, slice-scoped reconciliation
**Status:** Proposed — pending spike EXP-001

**Context.** Migrated slices need data consistent with the legacy system of record. Writing to two stores immediately ("dual-write everywhere") risks silent divergence and violates INV-001/INV-002 if reconciliation is imperfect. We need a strategy that proves consistency before any write-path migration.

**Decision (proposed).** For read slices, the new service performs **dual-read**: it serves from its own projection but reconciles against legacy as the source of truth, with slice-scoped reconciliation jobs surfacing any discrepancy on a parity dashboard. Legacy remains the system of record (ASM-002) until a slice is formally cut over. Write-path dual-write is deferred until the consistency model is validated by spike EXP-001 (testing HYP-001: that dual-read + slice-scoped reconciliation detects and resolves divergence within an acceptable window with zero unexplained discrepancies).

**Alternatives considered.**
- *Immediate dual-write everywhere* — rejected (for now): high divergence risk before reconciliation is proven; directly threatens INV-001/INV-002.
- *One-time bulk migration then cut over* — rejected for early phases: a single high-risk flip with a large reconciliation surface; poor fit for incremental, reversible slices.

**Consequences.** Keeps INV-001/INV-002 protected during read-slice migration by never making the new store authoritative prematurely. Defers write-path complexity to PH-2, gated on EXP-001 PASS. Status stays **Proposed** until EXP-001 reports; PH-2 cannot start until this ADR is Approved.

**References:** INV-001, INV-002, HYP-001, EXP-001, FR-005, ASM-002.

## Risk register (excerpt)

| ID | Risk | Impact | Likelihood | Mitigation | Owner | MVP/Full |
|----|------|--------|------------|-----------|-------|----------|
| RISK-001 | Silent data divergence between legacy and new service for a migrated slice. | High (violates INV-001) | Medium | Dual-read with legacy as source of truth (ADR-0002); slice-scoped reconciliation + parity dashboard (FR-005); EXP-001 must PASS before any write-path migration. | Data lead | Full |
| RISK-002 | Audit-trail gap or mutation during a cutover event. | High (violates INV-002; compliance failure) | Low-Medium | Audit writes remain on legacy system of record until cutover; append-only verification in acceptance (AC-003); Compliance sign-off (DEP-003) before data-touching cutover. | Compliance + Eng | Full |
| RISK-003 | Downstream integration (policy read DEP-001 / payments DEP-002) breaks when traffic shifts to the facade or a new service. | High (live integrations) | Medium | Facade is pass-through by default (ADR-0001); integration contract tests with test doubles before toggling; payments stay on legacy in early phases. | Integration lead | MVP |

## Roadmap (phases)

### PH-1 — Facade, observability, first read-only slice
**Goal.** Establish the strangler seam and migrate the lowest-risk slice (claim-status read views, ASM-001) behind a toggle, with legacy as source of truth (ASM-002).
**Deliverables.** Routing facade (pass-through by default) with request/response logging and per-slice toggle (FR-004); first read-only slice served by new claim-status service behind the toggle; dual-read + parity dashboard (FR-005); PH-1 baseline of page-load p95 (NFR-003).
**Exit criteria.** All non-migrated traffic still served by legacy with zero behavior change; read slice serving behind toggle with parity dashboard green; rollback of the read slice demonstrated; no audit or data discrepancies. EXP-001 executed and reporting.

### PH-2 — First write-path slice with reconciliation + proven rollback
**Goal.** Migrate a write-path slice with reconciliation and prove per-slice rollback under load.
**Deliverables.** Write-path slice behind toggle with dual-read + reconciliation per ADR-0002; per-slice rollback drill evidence (INV-003); audit-continuity verification across cutover (INV-002).
**Exit criteria.** Write slice meets parity (FR-005) with zero unexplained discrepancies; rollback drill passes (AC-004); audit trail verified append-only/complete across cutover (AC-003); Compliance sign-off obtained (DEP-003).
**Gate.** **PH-2 entry is gated on EXP-001 = PASS and ADR-0002 = Approved.** If EXP-001 fails, the data-sync strategy is revised (new ADR-0002 revision) before PH-2 begins.

### PH-3 — Progressive migration + legacy decommission planning
**Goal.** Migrate remaining slices progressively and plan legacy decommission.
**Deliverables.** Remaining slices migrated behind toggles with parity + rollback per slice; legacy decommission plan (data retention handover, integration cutover for DEP-001/DEP-002, runtime sunset); final compliance evidence package.
**Exit criteria.** All in-scope slices serving from new services with parity sustained; rollback retained until decommission sign-off; legacy decommission plan approved (timing deferred — see open items).

## Acceptance criteria (excerpt)

| ID | Given / When / Then | Traces to |
|----|---------------------|-----------|
| AC-001 | **Given** a claim with known status and history, **when** the claim-status read slice is toggled to the new service, **then** the rendered status and history are identical to the legacy rendering for the same claim (byte-equivalent on compared fields). | FR-001, FR-005 |
| AC-002 | **Given** the slice is serving from the new service, **when** the reconciliation job runs against legacy (source of truth), **then** it reports 0 unexplained discrepancies; any discrepancy raises an alert and blocks cutover. | FR-005, INV-001, ADR-0002, EXP-001 |
| AC-003 | **Given** an in-flight cutover of a data-touching slice, **when** audit events are written and later queried before/during/after cutover, **then** the audit trail is complete, append-only, and queryable with no missing or mutated records. | INV-002, NFR-002, DEP-003 |
| AC-004 | **Given** a migrated slice serving from the new service, **when** the per-slice toggle is flipped back to legacy (rollback drill), **then** that slice is served by legacy within the rollback target with no impact on other slices and no data loss. | INV-003, ADR-0001, FR-004, ASM-004 |

**Cross-reference summary.** ADR-0002 (Proposed) ↔ INV-001/INV-002 ↔ HYP-001/EXP-001 ↔ AC-002 (parity) ↔ PH-2 gate. INV-003 ↔ ADR-0001/ADR-0003 ↔ FR-004 ↔ AC-004 (rollback drill). Every FR/NFR carries a source; every decision carries an explicit status (ADR-0001 Approved, ADR-0002 Proposed).
