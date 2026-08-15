---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Review Prompts — <project-name>

<!-- Prompts that make Claude Code (or a human) CHECK work against the approved plan; reference
     entities by real ids; replace every <placeholder> (G-HANDOFF). Generation class: Conditional (handoff
     to Claude Code). PROJECT prompt files in `<package>/prompts/` (purpose-named).
     Shape: references/prompt-templates.md. -->

## Invariant audit

Verify the current implementation honors the invariants `INV-001..INV-00n` listed in
`entity_query("invariant")`. For each: state whether it holds, and for any
violation give `file:line` and a proposed minimal fix. Do not make functional changes during the audit —
produce a report only.

## Readiness re-check

Re-run the quality gates against the current repository (the DoR/DoD gates:
`entity_query("execution-gate")`). Run `gate_run()` — the full mechanical set (`G-IDS`,
`G-DEC-STATUS`, `G-REQ-SRC`, `G-TRACE`, `G-SET`, `G-PROGRESS`, `G-COMPLETE`, `G-REL`) — plus
`readiness_check`; report each gate as pass/fail with offending IDs, then give an overall
**go / no-go**. Never report "ready" while a Critical gate fails.

## PR review against acceptance criteria

Review the changes in <PR / branch> against the acceptance criteria in
`entity_query("acceptance-criterion")` — running a code review (e.g. `/code-review`)
where available is a good way to do this. For each `AC-` the PR claims to satisfy:
confirm it is met — record via `audit_record` with the full evidence chain (evidence,
`verified_by`, `verification_method`, `against_commit`) — or record **Not-met honestly,
never softened** (a Not-met that blocks is resolved, waived by the OPERATOR's `WVR-`, or
carried loudly — not narrated away). Also check:
- Invariants (`INV-`) not regressed.
- NFR thresholds (`NFR-`) it touches still met.
- No scope beyond the current phase (`PH-`); deviations captured as ADRs.
- Traceability links updated.

Output: a pass/fail per `AC-`, a list of issues, and an approve / request-changes recommendation.

## Traceability audit

Walk the coverage matrix in `review.html#traceability` (or `trace_query` per
requirement). Confirm every **MVP** `FR-/NFR-`
reaches >=1 decision, >=1 work item, and >=1 test, and that behavior-bearing ones reach an `AC-`. Report
any requirement `gate_run` lists under G-TRACE and whether it is a real gap or a missing link. Backward check: list any `WBS-` or
`TEST-` that traces to no requirement (possible gold-plating).
