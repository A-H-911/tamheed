> Project prompt of the demo package (rewritten for v4 — the original was the
> v1-migrated copy; its history is in git).

# Phase-gate follow-up — support triage agent

Resume against the record: `package_open("support-triage-agent-v2")`, `gate_run()`,
`readiness_check("phase", "<PH-x>")`, and the latest `entity_query("progress-entry")`
rows cross-checked against `git log` (flag unbound commits).

Work the next slice per its `execution-plan` row. Before the exit gate: `audit_record`
each bound AC with evidence + `verified_by` + `verification_method` + `against_commit`;
`progress_update` typed events (`work-done`, `subject_id`, your actor string);
`work_bind` every commit. Any deviation: an `SC-` row FIRST with its delta edges —
apply and set `Merged` only after my approval. A stubborn readiness failure: ask me
for a `WVR-` waiver — never author one.
