# Artifact-selection rules

Generate artifacts by **need, not ceremony** (safeguard 11). Each artifact has a generation class; the
project profile (Stage 2) and the answered questions decide which optional ones apply. The authoritative
catalog with one row per artifact is `artifact-catalog.md`; this file is the decision logic.

## Generation classes

- **Always** — every package gets it. Skipping requires an explicit recorded reason.
- **Conditional** — generated when a trigger holds (profile, size, risk, regulatory, etc.).
- **On-request** — only when the user asks.
- **Continuous** — created early, updated every cycle (Stage 21).
- **Derived** — generated from other artifacts; never hand-authored (regenerate instead).

## Always

Charter, executive summary, functional + non-functional requirements, constraint register, assumption
register, open-question register, open-decision register, risk register, phased roadmap, acceptance
criteria, traceability matrix (derived), handoff initial prompt, execution-readiness report, package
manifest, README for the package.

## Conditional (trigger → artifact)

| Trigger | Add |
|---|---|
| Genuine technical uncertainty | research plan, R&D backlog, hypotheses, experiment/POC plans |
| Architecturally significant decisions | ADRs, architecture doc, diagrams |
| ≥2 viable technology options | technology-comparison matrix |
| Cross-team / multi-actor delivery | stakeholder register, work-breakdown, milestones |
| Non-trivial NFRs (perf/security/scale) | NFR thresholds + test strategy section |
| Regulatory/compliance input | compliance constraints, validation evidence plan |
| Invariants present | invariant register |
| External dependencies | dependency register |
| Long execution horizon | progress log, status report cadence, checkpoints, acceptance audit, deferred-work / tech-debt register |
| Repo requested / handoff to Claude Code | repository bootstrap, follow-up + review prompts, DoR/DoD, agent-control surface (`CLAUDE.md` importing `AGENTS.md`), acceptance audit |

## On-request

Deep stakeholder analysis, cost/budget models, detailed data-flow/deployment diagrams beyond MVP, code-of-
conduct, governance charter beyond the baseline, marketing/positioning material.

## Selection algorithm

1. Start with the **Always** set.
2. Add **Conditional** artifacts whose triggers are satisfied by the profile + answered questions.
3. Add **On-request** artifacts the user named.
4. Remove anything that would be empty (no content to put in it) — record the omission reason in the manifest.
5. Confirm the resulting set with the user before Stage 17 if it is large or if you dropped anything they
   might expect.

## Anti-bloat checks

- If an artifact would only restate another, **derive or link** instead of duplicating.
- If a section has no project-specific content, omit it rather than emit a placeholder.
- Prefer one well-populated register over several thin ones.
- A diagram must add understanding a paragraph cannot; otherwise skip it.
