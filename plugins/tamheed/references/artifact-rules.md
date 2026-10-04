# Artifact-selection rules

Populate artifact families by **need, not ceremony** (safeguard 11). Each family has a generation
class. The project profile (Stage 2) and the answered questions decide which optional ones apply. The
machine mirror of these classes is **`BASELINE_ENTITY_TYPES`**, seeded into each package's
`entity_types` registry at `package_create`. Gate G-SET enforces from the registry, and `check.py`
lints registry ↔ catalog sync. The catalog with per-artifact history is `artifact-catalog.md`. The
set itself was decided at the plan-006 deliverables review.

## Generation classes

- **Always**: every package has rows (or a recorded `omission` with a reason, which G-SET enforces).
- **Conditional**: populated when a trigger holds (profile, size, risk, regulatory, and so on).
- **On-request**: only when the user asks.
- **Continuous**: created early, appended every cycle (Stage 21).
- **Derived**: views over other entities. Never authored, never stored (they are queries).

## Always (v2 set, per the approved deliverables review)

Charter + executive summary (narrative documents), requirements (FR/NFR), constraint register,
assumption register, open-question register, open-decision register, risk register, phased roadmap
(`phases`), acceptance criteria. Two Always deliverables are not entity families. The initial handoff
prompt is a `prompt` **row** (`PRT-`), and the package README is a narrative-document row.
Derived-by-construction: traceability, readiness, status, backlog views.

## Conditional (trigger → families)

| Trigger | Populate |
|---|---|
| Genuine technical uncertainty | research plan (absorbs the R&D-backlog role), hypotheses, experiments, POCs |
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
is first-class), and the milestones file (`milestones` rows live under phases). Also the execution
backlog (a view over `wbs_items`) and DoR/DoD/checkpoints as documents (merged into `execution_gates`
rows). And the separate handoff manifest (absorbed into the package manifest data).

## Continuous

Audit verdicts, progress entries, and scope changes accrue during Stage 21 by their own rules.
**Lessons** (`LL-`) join them. Create one whenever execution teaches something durable (kind
`improve` or `sustain`), born Proposed. Operator confirmation gates binding: only an Approved
lesson binds. The target repository's always-loaded note renders a roster of them (every pinned row
and the 10 highest-numbered unpinned ones). **Open the statement with the rule.** The note
prints the statement flattened to one line, whole at 180 characters or fewer and cut to its
first 177 above that. Nothing else of the row is printed, so a statement that opens with its
story renders the story. Edit it while it is Proposed. An approved lesson is immutable.

## On-request

Deep stakeholder analysis, cost/budget models, deployment/data-flow diagrams beyond MVP,
code-of-conduct, governance charter beyond the baseline, marketing/positioning material.
**Skills** (`SKL-`) are On-request in the strictest sense. They are created only by the operator's
promotion interview (the `skill-promote` prompt) distilling Approved lessons, never by a loop
or on the agent's initiative.

## Right-sizing (field evidence, 2026-07-17)

Bias register size by what execution actually references. That means **fewer, sharper FR/AC rows**
(field data showed near-zero commit references to FR/AC in three real deployments) and **rich
DEC/OQ/ADR rows** (load-bearing everywhere). WBS depth goes per profile (heavily used in one
deployment, unused in another). `last_referenced` (stamped by `work_bind`) tells you afterwards
which registers earned their keep.

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
- A diagram must add understanding a paragraph cannot. Otherwise skip it.
