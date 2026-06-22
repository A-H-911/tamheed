---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
generation: derived      # regenerated from the registers each update cycle
---

# AGENTS.md — standing operating context for <project-name>

<!-- The AMBIENT control surface for the execution agent. Most coding agents auto-load an AGENTS.md (or a
     CLAUDE.md) at the repo root every session, so this file is where the plan's non-negotiables KEEP
     governing the work after the one-time kickoff prompt. Agent-neutral: AGENTS.md is the canonical file;
     a one-line CLAUDE.md (or other tool-specific pointer) just includes/points here (safeguard 13 — the
     tool-specific shim is isolated, the content stays neutral). Whether a given harness truly auto-loads
     it is the harness's property, not Keystone's; the handoff initial prompt also names this file as
     standing context so it is honoured either way.

     Generation class: Derived / Conditional (handoff / repo requested). Lives at the PACKAGE ROOT
     (AGENTS.md), co-located with the registers it links — so the relative links below resolve.
     Regenerated from the registers each update cycle (stage 21); do not hand-maintain. Keep it short:
     quote the few load-bearing invariants inline, link the rest. Volatile state (current phase) lives in
     the status report, linked below — do not duplicate it here. -->

## Project state

- **What this is:** <one line>.
- **The contract** — read in order: [charter](00-charter.md), [architecture](architecture/architecture.md),
  [roadmap](planning/roadmap.md), [acceptance criteria](validation/acceptance-criteria.md). Decisions in
  the ADRs and approved registers are FINAL.
- **Where you are now:** the live [status report](progress/status-report.md) and
  [acceptance audit](validation/acceptance-audit.md). Do not re-litigate settled decisions.

## Invariants — never violate (a violation requires a new ADR)

- `INV-001` — <one-line invariant>.
- `INV-002` — <one-line invariant>.
- Full list + rationale + enforcement: [invariant register](requirements/invariant-register.md).
- **Rule:** breaking an invariant is not a silent option — record a new ADR (`adrs/adr-NNNN-*.md`, status
  Proposed) and STOP for approval.

## Hard constraints (refuse work that crosses these)

- <e.g. license / dependency bans, performance budgets, "no network at <stage>">.
- Full list: [constraint register](requirements/constraint-register.md) + the NFR thresholds in
  [non-functional requirements](requirements/non-functional.md).

## Operating conventions

- Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement, repeat.
- **Track as you go — every phase gate:** keep [acceptance criteria](validation/acceptance-criteria.md)
  current (status + evidence); update the [acceptance audit](validation/acceptance-audit.md) (verdict +
  evidence per `AC-`); append the [progress log](progress/progress-log.md); regenerate the
  [status report](progress/status-report.md). Then STOP at the gate for review.
- No phase starts with red CI; keep changes small and reviewable; record deviations as ADRs.
- See [definition of done](execution/definition-of-done.md) and, if present,
  [checkpoints](execution/checkpoints.md).

## Kickoff

Start from [handoff/initial-prompt.md](handoff/initial-prompt.md); subsequent phases use
[handoff/follow-up-prompts.md](handoff/follow-up-prompts.md).
