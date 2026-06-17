---
id: ADR-0002
title: The skill owns the capability; entry points are thin wrappers
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0002: The skill owns the capability; entry points are thin wrappers

Status: Accepted
Date: 2026-06-17

## Context

Keystone is invoked through a slash command (`/keystone`) and could in future
be invoked through other entry points (a different command name, an SDK call, a
CI step). The methodology — the staged workflow, the artifact-selection rules,
the governance and quality gates — is large and must behave identically no
matter how Keystone is triggered. We had to decide where that methodology
lives.

Putting methodology in the slash command is tempting because the command is the
thing the user types, but it couples the capability to one invocation surface,
duplicates logic if a second entry point is ever added, and makes the command
file the de facto source of truth — which then drifts from the documented
methodology.

## Decision

The **skill is authoritative**. All methodology, business logic, governance
rules, and gate definitions live in `skill/` (a lean `SKILL.md` plus
`references/` loaded on demand). Entry points are **thin wrappers** that do only
four things: normalize input, select a mode, invoke the skill, and route the
skill's output back to the user. The slash command at `commands/keystone.md`
contains no methodology and no business logic. This is enforced as safeguard 12
and surfaced by the Warn gate **G-CMD-THIN**.

## Consequences

- One source of truth. The skill defines behaviour; every entry point gets the
  same behaviour for free.
- New entry points are cheap and safe to add — they wrap the same skill rather
  than reimplementing it.
- The command file stays small and stable, so it rarely needs to change and
  cannot silently diverge from the methodology.
- A reviewer can check the command in seconds (does it contain any
  methodology? if so, that is a defect) and trust that the real logic is in one
  place.
- Slightly more indirection: a reader must open the skill, not the command, to
  understand what Keystone does. Documented in the README and the architecture
  notes so this is expected.

## Alternatives considered and rejected

- **Put the logic in the slash command.** Rejected: couples the capability to a
  single invocation surface, makes the command the source of truth (which then
  drifts from docs), and forces duplication the moment a second entry point
  exists. Directly violates safeguard 12.
- **Split logic between the command and the skill.** Rejected: "which half is
  authoritative?" has no good answer; the boundary blurs over time and both
  halves rot. A single owner is simpler and auditable.
- **A standalone library the command and skill both call.** Rejected as
  premature: Keystone's "logic" is largely methodology expressed in prose for a
  model to follow, not code to import; a library adds packaging and versioning
  overhead without a current consumer. The mechanical pieces that *are* code
  (e.g. the validator, the repo bootstrap) already live as standalone scripts
  the skill points to, which captures the benefit without the overhead.
