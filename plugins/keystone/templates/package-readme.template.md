---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# <project-name> — Planning & Handoff Package

<!-- The README for a GENERATED package (not for Keystone itself). It tells a reader — human or
     execution agent — what this package is, the order to read it in, and how an execution agent should
     consume it. Generation class: Always. Lives at: README.md (package root). -->

## What this is

This is a validated, execution-ready **planning and handoff package** for **<project-name>**, produced by
Keystone. It contains the approved problem framing, requirements, decisions, architecture, plan, validation
criteria, and the handoff prompts an execution agent uses to start building. The decisions recorded in the
ADRs and Approved registers are **final** unless superseded through a recorded decision.

## Status (snapshot)

Regenerated from the live [status report](progress/status-report.md). Phase status: ✅ done · ◑ in
progress · ⬜ not started.

| Phase | Scope | Status |
|---|---|---|
| PH-1 | <headline / MVP slice> | ⬜ not started |
| PH-2 | <headline> | ⬜ not started |

Deferred / out of current scope: <list, or "none">.

## How to read it (suggested order)

1. [Executive summary](01-executive-summary.md) — the one-page overview and recommendation.
2. [Charter](00-charter.md) — problem, objectives, scope, success metrics (`KPI-`).
3. [Requirements](requirements/) — functional (`FR-`), non-functional (`NFR-`), constraints (`CON-`),
   invariants (`INV-`), dependencies (`DEP-`).
4. [Architecture](architecture/architecture.md) and [decisions](decisions/) / [ADRs](adrs/).
5. [Roadmap](planning/roadmap.md) and [work breakdown](planning/work-breakdown.md).
6. [Acceptance criteria](validation/acceptance-criteria.md) and [traceability matrix](validation/traceability-matrix.md).
7. [Risks](risks/risk-register.md).

## How an execution agent should consume this package

- **Start here:** paste [handoff/initial-prompt.md](handoff/initial-prompt.md) into the execution agent.
- **Respect the invariants** in [requirements/invariant-register.md](requirements/invariant-register.md)
  (`INV-`) from the first commit.
- **Proceed phase by phase** using [handoff/follow-up-prompts.md](handoff/follow-up-prompts.md) — one prompt
  per phase gate; stop at each exit gate for approval.
- **Do not expand scope** beyond the current phase; record any deviation as a new ADR.
- **Check readiness** in [handoff/execution-readiness-report.md](handoff/execution-readiness-report.md);
  the structured contract is [handoff/handoff-manifest.(yaml|json)](handoff/).

## Conventions

Identifiers, statuses, and cross-references follow [governance/governance.md](governance/governance.md) and
[governance/naming-conventions.md](governance/naming-conventions.md). Derived artifacts (traceability,
readiness, status report) are regenerated, not hand-edited.

## Package metadata

- Package version: <semver> — see [manifest.json](manifest.json).
- Generated: <YYYY-MM-DD> by Keystone.
- MVP definition: see the [executive summary](01-executive-summary.md) and handoff manifest.
