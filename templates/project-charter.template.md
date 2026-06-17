---
status: Draft            # Draft | Proposed | Approved | Implemented | Rejected | Deferred | Superseded | Obsolete
version: 0.1.0           # semver or vN; bump on material change
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Project Charter — <project-name>

<!-- The charter is the anchor for the whole package. Keep it tight: it states WHY the project
     exists, WHAT done looks like, and the boundaries everything downstream must respect.
     Generation class: Always. Lives at: 00-charter.md -->

## Problem statement

<!-- The problem in the user's terms, before any solution. 2-4 sentences. What hurts, for whom,
     and why now. Do NOT name a technology or design here. -->
<problem-statement>

## Objectives

<!-- The outcomes that solving the problem produces. Outcome-oriented, not feature lists. -->
- <objective-1>
- <objective-2>

## Goals and non-goals

### Goals
<!-- What this project WILL achieve. Each should be observable. -->
- <goal-1>

### Non-goals
<!-- Explicitly what this project will NOT do. Non-goals prevent scope creep as much as scope does. -->
- <non-goal-1>

## Scope

### In scope
- <in-scope-item>

### Out of scope
<!-- Things a reader might reasonably assume are included but are not. State them so no one assumes. -->
- <out-of-scope-item>

## Success metrics (KPI-)

<!-- Each KPI must be measurable, with a baseline (if known) and a target. These feed acceptance
     criteria and the traceability matrix. Use KPI-NNN identifiers (governance.md). -->

| ID | Metric | Baseline | Target | Measurement method | Status |
|---|---|---|---|---|---|
| KPI-001 | <e.g. median render time for a 50-node diagram> | <unknown / current> | <e.g. < 500 ms> | <how it is measured> | Proposed |
| KPI-002 | <metric statement> | <baseline> | <target> | <method> | Proposed |

## Stakeholders (STK-)

<!-- Summary view; the full register lives in stakeholder-register. Reference STK- ids. -->

| ID | Stakeholder / role | Interest in the project | Influence (H/M/L) |
|---|---|---|---|
| STK-001 | <role, not person where possible> | <what they need from this> | <H/M/L> |

## Constraints and assumptions (summary)

<!-- Pointers, not the full registers. Link the constraint, invariant, and assumption registers. -->
- Key constraints: see [constraint register](requirements/constraint-register.md) (`CON-`).
- Non-negotiables: see [invariant register](requirements/invariant-register.md) (`INV-`).
- Key assumptions: see [assumption register](decisions/assumption-register.md) (`ASM-`).

## Approval

<!-- A charter constrains execution only once Approved. Record who approved and when. -->
- Approved by: <name-or-role>
- Date: <YYYY-MM-DD>
