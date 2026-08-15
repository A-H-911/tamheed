> Project prompt of the demo package (rewritten for v4 — the original was the
> v1-migrated copy; its history is in git).

# Kickoff — support triage agent

Open the package and orient by QUERIES, never by files:
`package_open("support-triage-agent-v2")`, then `entity_query("requirement", status="Approved")`,
`entity_query("invariant")`, `entity_query("phase")` / `("slice")` /
`("acceptance-criterion")`, and the human surface `review.html`.

Give me (a) a one-page summary of what you will build and the invariants you must
respect, and (b) your plan for the first slice with a pass/fail observable per task.
**STOP and wait for my approval — no code yet.**

Rules: the recording obligations in this repo's CLAUDE.md are mandatory. Work
acceptance-criteria-first; claim finished work as `Review` (Implemented = verified,
guarded); `audit_record` with the full evidence chain; ambiguity = an `OQ-` +
`[NEEDS-CLARIFICATION: OQ-NNN]` in place, never a guess.
