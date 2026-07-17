---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Dependency Register — <project-name>

<!-- External things the project relies on: libraries/runtimes, services/APIs, data sources, teams,
     upstream decisions, infrastructure. Each is a place the project can be blocked or surprised.
     Identified DEP-NNN (governance.md). Generation class: Conditional (external dependencies present).
     Lives at: requirements/dependency-register.md.
     Stay vendor/provider-neutral in naming where a category suffices (e.g. "object store" not a brand)
     unless a specific dependency is genuinely required. -->

## Conventions

- **Type** — Library | Runtime | Service/API | Data | Team | Decision | Infrastructure.
- **Dependency** — what is depended on (and version/pin if relevant).
- **Why needed** — the capability it provides.
- **Criticality** — Blocking (MVP cannot ship without it) | Important | Optional.
- **Risk if unavailable** — what happens; link `RISK-NNN` if it warrants a tracked risk.
- **Status** — Draft | Proposed | Approved | Deferred | Superseded | Obsolete.

## Dependencies

| ID | Type | Dependency | Why needed | Criticality | Risk if unavailable | Status |
|---|---|---|---|---|---|---|
| DEP-001 | Runtime | <runtime + pinned version> | <execution platform> | Blocking | <see RISK-00x> | Approved |
| DEP-002 | Library | <library / category, version policy> | <capability> | Important | <fallback: alternative library> | Proposed |
| DEP-003 | Service/API | <external service or category> | <capability> | Optional | <degrade gracefully> | Draft |
| DEP-004 | Decision | Awaiting <DEC-00x / OQ-00x> | <unblocks design choice> | Blocking | <blocks PH-x> | Proposed |

<!-- Pinned versions also belong in the handoff manifest prerequisites. Blocking dependencies that are
     not yet satisfied should surface as risks and/or open questions. -->
