> Project prompt of the demo package (rewritten for v4 — the original was the
> v1-migrated copy; its history is in git).

# Review — support triage agent

Read-only first: `package_open("support-triage-agent-v2")`, `gate_run()` (all mechanical gates incl.
G-REL), `readiness_check("package")`. Then review the changes in the named PR/branch
against `entity_query("acceptance-criterion")`: for each AC, record the verdict via
`audit_record` with the evidence chain — a Not-met is recorded honestly, never
softened (resolve it, ask me for a waiver, or carry it loudly). Confirm every MVP
requirement still traces (review.html#traceability); end with the readiness delta and
everything awaiting my words.
