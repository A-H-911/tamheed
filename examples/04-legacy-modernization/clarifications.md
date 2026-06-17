# Clarifications — claims-portal-modernization

The brief is clear on intent (incremental strangler-fig modernization, system stays live, zero data loss, audit continuity) but leaves several execution-shaping decisions open. These were asked as one batch to avoid round-trips. Where an answer was not returned in time, an assumption is recorded and flagged for confirmation.

## Clarification batch (asked together)

1. **Which functional slice should we strangle first?**
   Answer (given): The team agreed the first slice should be the lowest-risk one. They confirmed claim-status read views (the screens where adjusters and policyholders look up a claim and see its current state and history) are read-mostly and a safe starting point. Write paths (intake, status changes) come later.

2. **Is there an acceptable maintenance-window downtime, or must it be truly zero?**
   Answer (given): A brief, pre-announced off-hours maintenance window is acceptable for cutover events. The team indicated up to roughly 30 minutes in the low-traffic overnight window is tolerable, provided it is rare and announced. Steady-state running must be zero-downtime.

3. **What is the rollback expectation per migrated slice?**
   Answer (given): Every slice must be independently reversible. If a migrated slice misbehaves, they must be able to route that slice's traffic straight back to the legacy path without affecting other slices and without a redeploy where possible.

4. **During dual-run, which system is the source of truth?**
   Answer (assumed): Not explicitly decided by the team. Assumed legacy remains the system of record until a given slice is formally cut over, with the new service serving reads and reconciling against legacy. Recorded as ASM-002, pending confirmation.

5. **For the data, are we doing a one-time migration or dual-write?**
   Answer (assumed): Not decided. The team wants a recommendation. Assumed approach for early phases is dual-read with legacy as source of truth (no premature dual-write), with a spike to validate consistency before any write-path migration. Recorded under ASM-002 and gated by spike EXP-001.

6. **Who owns the compliance / retention authority we must satisfy?**
   Answer (given): The insurer's Compliance & Records function owns the regulatory retention schedule and audit requirements. They must sign off that retention and audit-trail integrity are preserved before any slice that touches stored claim data is cut over. Captured as DEP-003.

## Assumptions recorded

| ID | Assumption | Basis | Risk if wrong | Status |
|----|------------|-------|---------------|--------|
| ASM-001 | First slice to strangle is claim-status read views (read-mostly, lowest risk). | Clarification Q1 (given); read-mostly surface minimizes data-integrity exposure. | If a write-heavy slice is actually first priority, PH-1 scope and risk profile shift materially. | Proposed |
| ASM-002 | Dual-run with legacy as source of truth until per-slice cutover; reads served by new service, no premature dual-write. | Clarification Q4/Q5 (assumed); avoids divergence risk before consistency is proven. | If dual-write is required earlier, ADR-0002 and PH-2 sequencing change; reconciliation cost rises. | Proposed |
| ASM-003 | A bounded off-hours maintenance window of up to 30 minutes is acceptable for cutover events; steady state is zero-downtime. | Clarification Q2 (given). | If truly zero-downtime is mandated, cutover technique must change (e.g. shadow + instant flip only). | Proposed |
| ASM-004 | Per-slice rollback to the legacy route is mandatory and must be achievable via traffic toggle, not redeploy. | Clarification Q3 (given). | If rollback can only be done by redeploy, recovery time objective during incidents degrades. | Proposed |

## Note on contradictions

One tension exists in the brief: the stated desire for **zero downtime** versus the practical need for a **brief cutover window** when a slice flips its source of truth. These are not fully reconcilable for write-path cutovers without significantly more engineering.

**Resolution path:** Accept a *bounded, announced, off-hours* maintenance window for cutover events only (ASM-003), while holding steady-state operation to zero-downtime. This narrows "zero downtime" to "zero unplanned downtime + rare bounded planned windows." This is logged as a candidate decision (DEC- candidate, to be ratified as DEC-001 in the open-decision register) so it is reviewed and signed off rather than assumed silently.
