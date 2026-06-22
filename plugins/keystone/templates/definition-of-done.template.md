---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Definition of Done — <project-name>

<!-- The checklist a work item must satisfy to be considered COMPLETE. Adapt to the project; keep items
     binary and verifiable. Generation class: Conditional (handoff to a coding agent / repo requested).
     Lives at: execution/definition-of-done.md. Pairs with definition-of-ready.md. -->

## A work item is DONE when…

- [ ] Acceptance criteria (`AC-`) for the item PASS.
- [ ] Tests (`TEST-`) covering it pass in CI; coverage target met.
- [ ] Applicable invariants (`INV-`) verified to still hold (no regressions).
- [ ] Non-functional thresholds (`NFR-`) it touches are met and measured.
- [ ] Code/artifacts reviewed; no open critical review comments.
- [ ] Documentation updated (README/usage/contracts as applicable).
- [ ] Any deviation from the plan recorded as an ADR (not silently absorbed).
- [ ] Dependency versions pinned; no unvetted new dependencies introduced.
- [ ] Any golden/regression baseline change is intentional and reviewed — no silent baseline churn
  (determinism/provenance: record pinned tool/engine versions where output depends on them).
- [ ] Traceability updated (the item's links are current).
- [ ] Merged to the integration branch; build green.

## Phase / release done

<!-- Additional conditions for declaring a PHASE or RELEASE done (beyond per-item DoD). -->
- [ ] Phase exit criteria (roadmap `PH-`) met.
- [ ] Milestone (`MS-`) criteria met.
- [ ] Readiness re-check passes (criticals green).

## Notes

- <project-specific completion conditions or accepted exceptions>
