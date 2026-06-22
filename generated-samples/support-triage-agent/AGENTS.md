---
status: Draft
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
generation: derived
---

# AGENTS.md — standing operating context for support-triage-agent

The ambient control surface Claude Code auto-loads via `CLAUDE.md`, which imports this file. Keep it loaded
for the whole engagement.

## Project state

- **What this is:** an email support-triage + draft-reply agent, human-in-the-loop.
- **The contract** — read in order: [charter](00-charter.md),
  [architecture](architecture/architecture.md), [roadmap](planning/roadmap.md),
  [acceptance criteria](validation/acceptance-criteria.md). The ADRs and approved registers are FINAL.
- **Where you are now:** the live [status report](progress/status-report.md) and
  [acceptance audit](validation/acceptance-audit.md). Do not re-litigate settled decisions.

## Invariants — never violate (a violation requires a new ADR)

- `INV-001` — no external reply is sent without human approval.
- `INV-002` — every drafted factual claim cites retrieved context, or the agent defers to a human.
- `INV-003` — no PII leaves the system to an unapproved tool, model, or log.
- `INV-004` — every processed email carries a full decision trace.
- Full list + rationale + enforcement: [invariant register](requirements/invariant-register.md).
- **Rule:** breaking an invariant is not a silent option — record a new ADR (`adrs/adr-NNNN-*.md`,
  status Proposed) and STOP for approval.

## Hard constraints (refuse work that crosses these)

- See the [constraint register](requirements/constraint-register.md) and the NFR thresholds in
  [non-functional requirements](requirements/non-functional.md) — e.g. the `NFR-001` accuracy bar,
  `NFR-003` PII handling, and `NFR-005` auditability.

## Operating conventions

- Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement, repeat.
- **Track at each phase gate:** keep [acceptance criteria](validation/acceptance-criteria.md) current
  (status + evidence); update the [acceptance audit](validation/acceptance-audit.md) (verdict + evidence
  per `AC-`); append the [progress log](progress/progress-log.md); regenerate the
  [status report](progress/status-report.md). Then STOP for review.
- No phase starts with red CI; keep changes small and reviewable; record deviations as ADRs.

## Kickoff

Start from [handoff/initial-prompt.md](handoff/initial-prompt.md); subsequent phases use
[handoff/follow-up-prompts.md](handoff/follow-up-prompts.md).
