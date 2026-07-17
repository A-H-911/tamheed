---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Milestones — <project-name>

<!-- Milestones are verifiable checkpoints — points where a meaningful, demonstrable state is reached.
     A milestone is binary (met / not met) and tied to phase exits and/or key deliverables.
     Identified MS-NNN (governance.md). Generation class: Conditional (multi-actor / non-trivial
     delivery). Lives at: planning/milestones.md. -->

## Conventions

- **Milestone** — a demonstrable state ("<capability> works end-to-end").
- **Criteria** — the binary, verifiable conditions that mean it is met (link `AC-`/`TEST-`).
- **Phase** — the owning `PH-`.
- **Target** — date or sequence marker (avoid false precision; "after PH-1 exit" is valid).
- **Status** — Draft | Proposed | Approved | Implemented (met) | Deferred | Superseded.

## Milestones

| ID | Milestone | Criteria (met when…) | Phase | Target | Status |
|---|---|---|---|---|---|
| MS-001 | <MVP demonstrable> | <AC-001..AC-00x pass; demo runs> | PH-1 | <after PH-1 exit> | Proposed |
| MS-002 | <capability> hardened to NFR thresholds | <NFR-001 verified by TEST-00x> | PH-2 | <…> | Proposed |
| MS-003 | <release-ready> | <DoD met; readiness report = go> | PH-n | <…> | Draft |

<!-- Milestones should align to phase exit criteria in the roadmap; do not invent milestones that no
     phase delivers. -->
