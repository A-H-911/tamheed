---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Review Prompts — <project-name>

<!-- Prompts that make Claude Code (or a human) CHECK work against the approved plan; reference
     real artifact paths; replace every <placeholder> (G-HANDOFF). Generation class: Conditional (handoff
     to Claude Code). Lives at: handoff/review-prompts.md. Shape: references/prompt-templates.md. -->

## Invariant audit

Verify the current implementation honors the invariants `INV-001..INV-00n` listed in
[invariant register](../requirements/invariant-register.md). For each: state whether it holds, and for any
violation give `file:line` and a proposed minimal fix. Do not make functional changes during the audit —
produce a report only.

## Readiness re-check

Re-run the quality gates against the current repository (see [definition of done](../execution/definition-of-done.md)
and the gate list). Report each **Critical** gate (`G-TRACE`, `G-COMPLETE`, `G-IDS`, `G-DEC-STATUS`,
`G-EXEC`, `G-HANDOFF`, `G-OQ`, `G-CONFLICT`) as pass/fail with offending IDs/paths, then give an overall
**go / no-go**. Never report "ready" while a Critical gate fails.

## PR review against acceptance criteria

Review the changes in <PR / branch> against the acceptance criteria in
[acceptance-criteria.md](../validation/acceptance-criteria.md) — running a code review (e.g. `/code-review`)
where available is a good way to do this. For each `AC-` the PR claims to satisfy:
confirm it is met (cite the evidence/test), or flag it as not met. Also check:
- Invariants (`INV-`) not regressed.
- NFR thresholds (`NFR-`) it touches still met.
- No scope beyond the current phase (`PH-`); deviations captured as ADRs.
- Traceability links updated.

Output: a PASS/FAIL per `AC-`, a list of issues, and an approve / request-changes recommendation.

## Traceability audit

Walk [traceability-matrix.md](../validation/traceability-matrix.md). Confirm every **MVP** `FR-/NFR-`
reaches >=1 decision, >=1 work item, and >=1 test, and that behavior-bearing ones reach an `AC-`. Report
any `gap`/`partial` row and whether it is a real gap or a missing link. Backward check: list any `WBS-` or
`TEST-` that traces to no requirement (possible gold-plating).
