/tamheed:tamheed Plan the project described in `brief.md` in this directory (the seed code is in `seed/`), as a headless lab run of the Tamheed plugin. The operator is not present; the words below are the operator's, given in advance; anything they do not cover you record as an open question to the operator and continue. Write only inside this directory and the executor workspace named at the end.

Follow the skill you were just given, through the Tamheed MCP tools only. The package: `package_create("lab-tracker", "tick — a tiny CLI task tracker", "rnd")`. The scenario, verbatim from the lab's script:

1. **Understand** — record the brief as a narrative document; extract FR rows (add/list/done/history/persistence, MVP) with NOT-NULL provenance. The recurring-tasks ambiguity becomes `OQ-` (owner + due_by) and the requirement's statement carries `[NEEDS-CLARIFICATION: OQ-NNN]` — G-COMPLETE passes WITH the marker.
2. **Explore** — the storage fork: record `DEC-` (file vs database). Apply the one-way-door test: file-on-disk is reversible → stays a DEC; the *schema of the persisted record* is load-bearing → promote to `ADR-` with `confirmation` filled. `promoted_to` set; the `decisions-look-architectural` advisory is CLEAN after.
3. **Plan** — one phase, two slices (SL-001 core commands, SL-002 dates & quality), ACs bound to requirement + slice, tests planned for the date logic, a `ready` gate ("operator confirms the seed tests were triaged") and an `approval` gate. G-TRACE green over MVP rows; `acs-slice-bound` clean.
4. **Gates** — `gate_run` fully green (G-REL included); `readiness_check("package")` lists the expected blockers (unverified ACs).
5. **Handoff** — `handoff_emit` into the executor workspace; the CLAUDE.md note span carries the obligations table.

The operator's words, given in advance:
- Charter, executive summary, requirement rows, phase plan, slices, acceptance criteria and tests: approved as written.
- The recurring-tasks ambiguity: do not resolve it. Record the `OQ-` with owner `operator` and `due_by` one month from today; mark the requirement `[NEEDS-CLARIFICATION: OQ-NNN]`.
- The storage fork: file-on-disk stays a `DEC-`; the persisted record's schema is load-bearing — promote that to an `ADR-`. Confirmation words for the ADR: "The operator confirms the persisted-record schema ADR as written, 2026-10-01, lab run A1."
- The `ready` gate: "operator confirms the seed tests were triaged" — `human_required`. The `approval` gate: "operator approves the phase for execution" — `human_required`.

Then `handoff_emit` with `target_dir` = `{EXEC}` (the executor workspace; it holds a copy of the seed as a git repository), and `package_close`. Do not run the seed's tests and do not edit the seed. Final message: a numbered report, one line per scenario item, naming every id you created and every advisory or gate that was not clean, and every question you had for the operator.
