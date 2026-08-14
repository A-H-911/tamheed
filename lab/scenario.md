# The lab scenario — the scripted acceptance run

Run against a release candidate. The planner phases (1–5) may be driven by the release
engineer through the MCP handlers guided by the skill; the execution phase (6–9) is driven
by a **real agent** given the package and the seed code. Every ✔ names the mechanism that
must fire; the resulting package replaces `evals/sample-results/lab-tracker/package`.

1. **Understand** — `package_create("lab-tracker", …, profile "rnd")`; record the brief as
   a narrative document; extract FR rows (add/list/done/history/persistence, MVP) with
   NOT-NULL provenance.
   ✔ The recurring-tasks ambiguity becomes `OQ-` (owner + due_by) and the requirement's
   statement carries `[NEEDS-CLARIFICATION: OQ-NNN]` — G-COMPLETE passes WITH the marker.
2. **Explore** — the storage fork: record `DEC-` (file vs database). Apply the one-way-door
   test: file-on-disk is reversible → stays a DEC; the *schema of the persisted record* is
   load-bearing → promote to `ADR-` with `confirmation` filled.
   ✔ `promoted_to` set; the `decisions-look-architectural` advisory is CLEAN after.
3. **Plan** — one phase, two slices (SL-001 core commands, SL-002 dates & quality), ACs
   bound to requirement + slice, tests planned for the date logic, a `ready` gate
   ("operator confirms the seed tests were triaged") and an `approval` gate.
   ✔ G-TRACE green over MVP rows; `acs-slice-bound` clean.
4. **Gates** — `gate_run` fully green (G-REL included); `readiness_check("package")` lists
   the expected blockers (unverified ACs).
5. **Handoff** — `handoff_emit` into the executor workspace; the CLAUDE.md note span carries
   the v4 obligations table.
6. **Execute SL-001** (the agent) — fix the seeded `overdue()` bug:
   ✔ `DEF-` row (severity honest: medium) BEFORE the fix; typed `work-done` progress events
   with `subject_id` + `actor`; `audit_record` Met with `verified_by: agent`,
   `verification_method: auto-test`, `against_commit`.
   ✔ The flaky clock test: a `DEF-` row (the flaky-test-is-a-defect doctrine), quarantined
   or fixed — never deleted silently.
   ✔ Finished work claimed as `Review`, not `Implemented`.
7. **The drift** — the P.S. export ask:
   ✔ `SC-` row Proposed + `scope_modifies`/`scope_adds` edges; STOP for operator approval;
   after approval the agent applies the rows and sets the SC- to `Merged`
   (`scope-changes-merged` advisory clean after).
8. **Close-outs** —
   ✔ The typo defect (low) stays open under an operator-approved `WVR-` waiver
   (`defects-closed`/`defects-minor` reported `waived`, never silent).
   ✔ One slice transition attempted early: the guard REFUSES; the operator's explicit words
   authorize `force: true`; the server's own `forced-override` audit event appears.
   ✔ The other slice closes clean: readiness green → `Implemented`.
9. **Wrap** — the `ready`/`approval` gates get `outcome` values + `gate-decision` events;
   `export_html`; `package_close`; the package is committed as the eval fixture.

**Pass bar:** every ✔ observed; `gate_run` ready (or failing ONLY on deliberately-open
items the scenario names); the eval runner's lab checks green.
