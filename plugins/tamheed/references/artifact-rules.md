# Artifact-selection rules

Populate artifact families by **need, not ceremony** (safeguard 11). Each family has a generation
class; the project profile (Stage 2) and the answered questions decide which optional ones apply. In v2
the machine mirror of these classes is the **`entity_types` registry** seeded at `package_create`
(gate G-SET reads it); the catalog with per-artifact history is `artifact-catalog.md`, and the decided
v2 set is `plans/deliverables-review.md` in the program repo. (`required-artifacts.json` alongside this
file is the frozen **v1** mirror, kept for migration — the v1 validator reads it; v2 does not.)

## Generation classes

- **Always** — every package gets rows (or a recorded `omission` with a reason — G-SET enforces).
- **Conditional** — populated when a trigger holds (profile, size, risk, regulatory, etc.).
- **On-request** — only when the user asks.
- **Continuous** — created early, appended every cycle (Stage 21).
- **Derived** — views over other entities; never authored, never stored (they are queries).

## Always (v2 set, per the approved deliverables review)

Charter + executive summary (narrative documents), requirements (FR/NFR), constraint register,
assumption register, open-question register, open-decision register, risk register, phased roadmap
(`phases`), acceptance criteria, initial handoff prompt, package README. Derived-by-construction:
traceability, readiness, status, backlog views.

## Conditional (trigger → families)

| Trigger | Populate |
|---|---|
| Genuine technical uncertainty | research plan (absorbs the v1 R&D backlog), hypotheses, experiments, POCs |
| Architecturally significant decisions | ADRs, architecture narrative, diagrams |
| ≥2 viable technology options | technology-comparison narrative |
| Cross-team / multi-actor delivery | work breakdown, milestones |
| Non-trivial NFRs (perf/security/scale) | NFR thresholds + tests (`TEST-` rows) |
| Regulatory/compliance input | compliance constraints, validation evidence plan |
| Invariants present | invariant register |
| External dependencies | dependency register |
| Long execution horizon | progress entries, audit verdicts, execution gates, deferred-work register, defect log |
| Handoff to Claude Code | follow-up + review prompts, agent-control surface, per-slice execution plans, conventions |
| Consciously postponed work exists | deferred-work rows (severity, activation trigger, invariant-at-stake) |

Dropped in v2 (decided 2026-07-17): the standalone stakeholder document (the `stakeholders` **table**
is first-class), the milestones file (`milestones` rows live under phases), the execution backlog
(a view over `wbs_items`), DoR/DoD/checkpoints as documents (merged into `execution_gates` rows), and
the separate handoff manifest (absorbed into the package manifest data).

## On-request

Deep stakeholder analysis, cost/budget models, deployment/data-flow diagrams beyond MVP,
code-of-conduct, governance charter beyond the baseline, marketing/positioning material.

## Right-sizing (field evidence, 2026-07-17)

Bias register size by what execution actually references: **fewer, sharper FR/AC rows** (field data
showed near-zero commit references to FR/AC in three real deployments) and **rich DEC/OQ/ADR rows**
(load-bearing everywhere); WBS depth per profile (heavily used in one deployment, unused in another).
`last_referenced` (stamped by `work_bind`) tells you afterwards which registers earned their keep.

## Selection algorithm

1. Start with the **Always** set.
2. Add **Conditional** families whose triggers hold (profile + answered questions).
3. Add **On-request** families the user named.
4. Any Always family with nothing real to hold → `omission` row with the reason (never an empty stub).
5. Confirm the resulting set with the user before Stage 17 if it is large or you dropped anything they
   might expect.

## Anti-bloat checks

- If a family would only restate another, **link** (trace edge) instead of duplicating.
- If a narrative section has no project-specific content, omit it rather than emit a placeholder.
- Prefer one well-populated register over several thin ones.
- A diagram must add understanding a paragraph cannot; otherwise skip it.
