---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# R&D Backlog — <project-name>

<!-- A prioritized queue of investigation items (spikes, prototypes, benchmarks, evaluations) derived
     from the research plan's uncertainties. Each item is bounded and produces a decision or evidence.
     Generation class: Conditional (genuine technical uncertainty). Lives at: research/rnd-backlog.md. -->

## Conventions

- **Item** — a bounded investigation with a clear question.
- **Priority** — High | Med | Low (drive ordering by what unblocks the most / earliest phase).
- **Unblocks** — the decision, requirement, phase, or risk it serves.
- **Output** — what it produces (a `DEC-`, a benchmark number, a `HYP-` confirmed/refuted).
- **Status** — Draft | Proposed | Approved | Deferred | Implemented (done) | Obsolete.

## Backlog

| ID | Item | Priority | Unblocks | Linked HYP/EXP/POC | Output | Status |
|---|---|---|---|---|---|---|
| RND-001 | <investigation question> | High | DEC-002, PH-1 | HYP-001 / EXP-001 | <decision / number> | Proposed |
| RND-002 | <investigation question> | Med | RISK-003 | POC-001 | <go/no-go> | Draft |
| RND-003 | <investigation question> | Low | NFR-001 | EXP-002 | <benchmark> | Deferred |

<!-- RND- is a local backlog id for ordering research work; it is not a governed cross-package
     identifier. Promote outcomes into governed registers (DEC-/ADR-/RISK-/HYP-) as they resolve. -->
