---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Definition of Ready — <project-name>

<!-- The checklist a work item must satisfy BEFORE it is started, so execution does not begin on
     under-specified work. Adapt the items to the project; keep them binary (yes/no).
     Generation class: Conditional (handoff to Claude Code / repo requested). Lives at:
     execution/definition-of-ready.md. Pairs with definition-of-done.md. -->

## A work item is READY when…

<!-- Check each. A NO means the item is not ready — resolve before starting. -->

- [ ] It traces to >=1 requirement (`FR-/NFR-`) — not gold-plating.
- [ ] Acceptance criteria (`AC-`) exist and are testable.
- [ ] Dependencies (`DEP-`/predecessor `WBS-`) are satisfied or scheduled.
- [ ] No **blocking** open question (`OQ-`) gates it.
- [ ] Required decisions (`DEC-/ADR-`) are **Approved** (not merely Proposed).
- [ ] Applicable invariants (`INV-`) are understood and listed.
- [ ] Verification approach is defined (which `TEST-`/check confirms done).
- [ ] Scope of the item is small enough to complete and verify in one focused unit.
- [ ] Prerequisites (runtime/versions/access) are available.

## Notes

<!-- Project-specific readiness conditions, or exceptions and who accepted them. -->
- <note>
