# Plan 254, freeze v3 and v4 (the A/B tasks)

## F6 version 3 (2026-11-23, after the STOP, before any scored A/B session; hashed in `ab_freeze_v3.sha256`)

Changes from F6, each because a frozen rule demanded it: O1's answer keys became `callers`, `flag`,
`flag_set_in`, and `package_open` became neutral (it appears in the copy's `CLAUDE.md`); O2 became
"which functions call `_scan_markers`" (`gate_run` neutral, it appears in `CLAUDE.md`); O3 became the
callers of `_edge_rule_violations` and its rules constant (`gate_run` neutral). M03, M25, M48 as F6.
Tasks: `ab_tasks.json`. One pilot session (O2, arm B) ran before the scorer's bug fix and is scored.
