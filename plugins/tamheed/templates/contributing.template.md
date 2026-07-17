---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Contributing — <project-name>

<!-- How contributors (human or agent) change this package and the project it plans, without breaking
     governance. Generation class: Conditional (handoff to Claude Code / repo requested).
     Lives at: governance/contributing.md. Keep tech-neutral. -->

## Principles

- **Respect the invariants** (`INV-`) — they are non-negotiable; a change that violates one is rejected.
- **Decisions are decisions.** Treat Approved `DEC-/ADR-` as settled; to change one, supersede it with a
  new recorded decision — do not silently re-decide.
- **Trace everything.** New work items (`WBS-`) and tests (`TEST-`) must trace to a requirement; new
  requirements must reach the traceability matrix.
- **No silent scope creep.** Scope changes after lock require a recorded decision.

## Workflow for a change

1. **Identify the owning artifact** (a register, ADR, plan doc) and read it.
2. **Make the change in the source artifact**, not in a derived one. Update the front-matter `version`,
   `updated`, and `status` as appropriate (see governance).
3. **If it is a decision**, record it as a `DEC-` (or `ADR-` if architecturally significant) with status
   and rationale; keep rejected alternatives.
4. **If it supersedes** an existing item, create the successor and set `supersedes`/`superseded_by` on both;
   leave the old item at status Superseded.
5. **Regenerate derived artifacts** (traceability matrix, readiness report, status report) — never hand-edit
   them.
6. **Re-run the gates** affected by the change (at minimum `G-IDS`, `G-DEC-STATUS`, `G-TRACE`).
7. **Record the change** in the progress log with who/what/when.

## Reviews

- Use the [review prompts](../handoff/review-prompts.md) for invariant audits, readiness re-checks, and PR
  reviews against acceptance criteria.
- A change is mergeable only when the Definition of Done is met and criticals are green.

## What NOT to do

- Do not edit immutable artifacts in place (ADRs, Approved acceptance criteria) except to fix typos.
- Do not hand-maintain derived artifacts.
- Do not couple the project needlessly to a single provider/agent/stack (`G-COUPLING`).
