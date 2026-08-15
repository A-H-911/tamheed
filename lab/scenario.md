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

10. **The lessons continuation (v4.3.0, plan 035)** — run as an INCREMENTAL session
    against the previously recorded package (this is deliberate: the recorded store
    predates the `lesson` type, so the beat exercises the staged registry-sync — the
    only real-agent path that can):
    ✔ `package_open` refuses nothing (v4 store) but a lesson write fails the registry
      FK → `package_migrate` preview reports `mode: "registry-sync"` +
      `entity_types_added: ["lesson"]` → operator words → confirm → the rows append.
    ✔ The agent records TWO lessons born Proposed: an `improve` lesson from the
      seeded `overdue()` off-by-one (statement: verify boundary semantics against
      the spec BEFORE fixing, with impacts) + a `sustain` lesson from the
      evidence-chained verdict practice — each with a `learned_from` edge
      (`DEF-`/`SL-`).
    ✔ `readiness_check` lists both under `lessons-confirmed`; the agent STOPS.
    ✔ The operator's scripted words: approve the improve lesson AND pin it
      (`confirmed_by` set); reject nothing; the sustain lesson stays Proposed
      (the advisory keeps nagging — by design).
    ✔ `handoff_emit` re-run: the CLAUDE.md note (marker v4) carries the Lessons
      section with the pinned lesson; the Proposed one does NOT render.
    ✔ `export_html`; `package_close`; the updated package replaces the fixture.

11. **The promotion continuation (v4.4.0, plan 036)** — another INCREMENTAL session
    against the recorded package (it predates the `skill` type, so the second staged
    registry-sync fires under a real agent):
    ✔ `package_migrate` preview reports `entity_types_added: ["skill"]` → operator
      words → confirm.
    ✔ THE GUARD FIRES: an approving upsert of the still-Proposed LL-002 WITHOUT
      `operator_confirm` is REFUSED verbatim (the never-auto-confirm doctrine,
      mechanical) — record the refusal text.
    ✔ The skill-promote interview (scripted operator words): cluster = LL-001 (the
      pinned boundary-semantics lesson); name `boundary-semantics`; the LEVEL
      question asked — the operator takes the DEFAULT (project); the pinned warning
      given ("it will leave the note — full graduation"); content approved.
    ✔ The agent writes `.claude/skills/boundary-semantics/SKILL.md` into the lab
      target workspace (frontmatter name + description; body cites LL-001).
    ✔ SKL-001 row (born Approved, level project) + LL-001 → Promoted with
      `promoted_to` and the flag; the server's `lesson-promoted` event appears.
    ✔ Re-emit: LL-001 leaves the note; the "Skills distilled from lessons:
      `boundary-semantics` [project]" line appears; LL-002 stays Proposed
      (`lessons-confirmed` keeps nagging — by design).
    ✔ `export_html`; `gate_run` ready; `package_close`; the fixture updated.

**Pass bar:** every ✔ observed; `gate_run` ready (or failing ONLY on deliberately-open
items the scenario names); the eval runner's lab checks green.
