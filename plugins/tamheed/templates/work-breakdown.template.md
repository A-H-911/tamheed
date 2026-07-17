---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Work Breakdown — <project-name>

<!-- Decompose each phase into work items. LEAF items must be ACTIONABLE and TESTABLE (gate G-EXEC):
     a leaf says what to do and how its completion is verified. Identified WBS-N.N[.N] aligned to the
     owning phase (governance.md). Generation class: Conditional (multi-actor / non-trivial delivery).
     Lives at: planning/work-breakdown.md. Every WBS leaf should trace to >=1 requirement. -->

## Conventions

- **ID** — `WBS-<phase>.<group>[.<leaf>]`, e.g. `WBS-1.2`, `WBS-1.2.1`. Top digit = phase number.
- **Item** — the work; leaves are imperative ("Implement <X>").
- **Traces to** — the `FR-/NFR-` (and `AC-`) it serves. A leaf tracing to nothing is gold-plating or a
  missing requirement — investigate (see traceability.md, backward links).
- **Verification** — how done is confirmed (the testable part of the leaf).
- **Depends on** — predecessor `WBS-`/`DEP-`. **Status** — Draft | Proposed | Approved | Implemented.
- **Evidence** — what proves completion once done: `TEST-` ids, commit/PR refs, CI run, or golden
  sample. Stays `—` until the item is done; the execution agent fills it as work lands (see the
  tracking protocol in `../handoff/initial-prompt.md`).

## Work items

| ID | Item | Traces to | Verification | Depends on | Status | Evidence |
|---|---|---|---|---|---|---|
| WBS-1.1 | <work group for PH-1> | — | (group; see leaves) | — | Proposed | — |
| WBS-1.1.1 | <imperative leaf task> | FR-001, AC-001 | <test / check that confirms done> | — | Proposed | <TEST-001 / commit / CI> |
| WBS-1.1.2 | <imperative leaf task> | FR-002 | <verification> | WBS-1.1.1 | Proposed | — |
| WBS-1.2 | <work group> | — | (group) | — | Proposed | — |
| WBS-1.2.1 | <imperative leaf task> | NFR-001 | <benchmark TEST-00x> | WBS-1.1.2 | Draft | — |
| WBS-2.1 | <work group for PH-2> | — | (group) | PH-1 exit | Proposed | — |

<!-- Keep the tree shallow where possible. Each leaf should be small enough to complete and verify in
     one focused unit of work. Group nodes carry no verification of their own. -->
