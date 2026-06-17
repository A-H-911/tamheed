# Follow-up prompt — Phase PH-2 gate (claims-portal-modernization)

## Resume context

Phase **PH-1 is complete and approved**. State as of this prompt:
- The routing facade is **live** and serving all traffic; non-migrated paths are unchanged on legacy.
- The first **read-only slice** (claim-status read views, ASM-001) is serving from the new claim-status service **behind its toggle**, with **dual-read** and legacy as source of truth (ASM-002).
- The **parity dashboard is green** for that slice (FR-005, AC-002): 0 unexplained discrepancies sustained.
- Spike **EXP-001 PASSED** — the dual-read + slice-scoped reconciliation model (HYP-001) detected and resolved induced divergence within the acceptable window with zero unexplained discrepancies.
- Consequently **ADR-0002 is now Approved** (was Proposed). The PH-2 entry gate is therefore satisfied.

You may now begin **Phase PH-2**.

## PH-2 goal

Migrate the **first write-path slice** behind a toggle, with dual-read + reconciliation per ADR-0002, and **prove per-slice rollback** under realistic conditions — without violating any invariant.

## Bounded tasks (do these in order; stop for review between any that I flag)

**Task 1 — Write-path slice behind toggle with dual-read + reconciliation (ADR-0002).**
Implement the first write-path slice (e.g. a claim status-change action) routed through the new service behind its per-slice toggle, with legacy still authoritative until cutover and slice-scoped reconciliation running.
- **PASS** if: the slice operates behind its toggle; reconciliation reports 0 unexplained discrepancies over the validation window; legacy remains source of truth until explicit cutover; FR-002 paths not yet migrated are untouched.
- **FAIL** if: any discrepancy is unexplained, the new store is made authoritative without cutover sign-off, or another slice/path is affected.

**Task 2 — Prove per-slice rollback drill (INV-003).**
Execute a rollback drill: with the write slice serving from the new service, flip its toggle back to legacy under load and confirm clean reversion.
- **PASS** if (AC-004): the slice reverts to the legacy path within the rollback target, with no impact on other slices and no data loss; in-flight requests are handled without corruption.
- **FAIL** if: rollback requires a redeploy, other slices are disturbed, or any data is lost/duplicated on reversion.

**Task 3 — Parity and audit-continuity gates green (INV-001, INV-002).**
Run the parity check and the audit-continuity verification across a simulated cutover of the write slice.
- **PASS** if (AC-002, AC-003): parity shows 0 unexplained discrepancies (INV-001) and the audit trail is verified complete, append-only, and queryable across the cutover (INV-002), with Compliance sign-off obtained per DEP-003.
- **FAIL** if: any discrepancy is unexplained, or any audit record is missing/mutated across the cutover, or Compliance sign-off is not obtained.

## Invariants in force

**INV-001** (no claim data lost or altered), **INV-002** (audit trail complete, append-only, queryable across cutover), **INV-003** (every migrated slice independently rollback-able). These remain non-negotiable throughout PH-2.

## PH-2 exit gate

PH-2 is complete only when **all three tasks PASS**: the write slice meets parity with zero unexplained discrepancies, the per-slice rollback drill passes (INV-003 / AC-004), the audit trail is verified across cutover (INV-002 / AC-003), and Compliance has signed off (DEP-003). On completion, stop and request approval before any PH-3 work (progressive migration of remaining slices + legacy decommission planning).
