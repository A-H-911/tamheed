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

12. **The depth continuation (v4.5.0, plan 039)** — another INCREMENTAL session against
    the recorded package (its registry is current and its `data/` holds no foreign file,
    so the staged sync has nothing to do — that refusal is itself an expectation):
    ✔ `package_migrate` preview is REFUSED verbatim: "package is already v4.0.0, its
      entity-type registry is current, and data/ holds no foreign audit-trail file —
      nothing to migrate" (record the text).
    ✔ `package_verify()` on the open package: `verified: true`, `dirty: []`, `foreign: []`,
      `memory_matches_disk: true`; then, on the operator's scripted words,
      `package_verify(record=true)` → the server's own `integrity-verified` row (actor
      `system:package-verify`) naming the digest; a second `package_verify()` reports a
      DIFFERENT digest (the row rewrote the journal file — by construction, not tampering).
    ✔ Paging: walk `entity_query("acceptance-criterion", limit=1)` with `after_id` until
      `next_after` is null — every id seen once, `total` constant; quote two rows verbatim
      via `ids=[...]`; one keyword `search` (e.g. "overdue") returns the rows that carry it.
    ✔ `amends`: the operator's scripted ruling narrows `DEC-001` (the storage decision)
      for the export path — an `SC-` row Proposed, an `amends` edge to `DEC-001`, and the
      guard REFUSING `amends` to `SL-001` verbatim (rulings only); after approval the DEC-
      row is upserted with the narrowed rationale, RE-READ, and only then the SC- set
      Merged (`scope-changes-merged` clean after).
    ✔ THE REFUSAL FIRES: a caller-written `progress_update` with `event_type:
      "lesson-confirmed"` is REFUSED naming the appending tool — record the text.
    ✔ `readiness_check("package")`: `lessons-note-budget` passes (well under the ceiling);
      `lessons-confirmed` still nags on LL-002 (by design).
    ✔ `handoff_emit` re-run: the note carries the flush rule (`git status --porcelain
      -uall`), the widened `entity_query` cheat-sheet line, and `package_verify`.
    ✔ `export_html`; `gate_run` ready; `package_close`; the fixture updated.

13. **The retire continuation (v4.6.0, plan 040)** — another INCREMENTAL session against
    the recorded package (findings_23: the `amends` relation arrived with no way to
    remove the `relates_to` it was meant to replace, and the C7 counter read the wrong
    population):
    ✔ `package_migrate` preview is REFUSED verbatim as in beat 12 (record the text).
    ✔ The residue: write `SC-002 relates_to DEC-001` beside the recorded `amends` edge
      (ACCEPTED — the escape hatch is always legal); `trace_query("SC-002")` shows BOTH.
    ✔ THE RETIRE: `entity_upsert([{type: trace-edge, from_id: SC-002, to_id: DEC-001,
      relation: relates_to, retire: true}])` → `retired: true`, `retire_audit: PE-nnn`;
      `trace_query` shows only `amends`; the server's own `correction` row (actor
      `system:edge-retire`, entry `EDGE RETIRED: SC-002 -relates_to-> DEC-001 …`) quoted.
    ✔ Two refusals verbatim: retiring a triple that does not exist ("nothing to retire
      (an attempt is not a write)"), and a retire item carrying an extra key ("exactly
      from_id, to_id, relation").
    ✔ `gate_run`'s G-REL note names the operation (`{retire: true} on the old triple`).
    ✔ The audit split: add an export AC (bound to `SL-002` AND `FR-007`, the CSV-export
      requirement; Approved) with ONE Pending placeholder verdict that CARRIES
      `verified_by: agent`, `verification_method: inspection` (the bucket keys on the
      VERDICT, not on empty columns; the fixture requires `verified_by` on every AV- row)
      → `audit_evidence` reads `evidenced: 3, narrated: 0, ungraded: 1` (AC-003's
      Not-met IS evidenced), the placeholder named in `ungraded_ids`; the Not-met on
      `AC-003` stays untouched (a Pending on a graded AC would be a regrade). *Recorded
      fixture note:* the beat-13 brief bound the new `AC-004` to `FR-004` (task history)
      by the maintainer's error; Approved ACs are immutable, so `AC-005` supersedes it
      bound to `FR-007` and carries the placeholder (`AV-005`), `AC-004` is retired —
      the supersession is the fixture's own record of the fix (`PE-018`).
    ✔ `readiness_check("package")`: `acs-met` now also names the new AC (deliberately
      open); `lessons-note-budget` still passes; `lessons-confirmed` still nags on LL-002.
    ✔ `handoff_emit` re-run: the cheat-sheet's `entity_upsert` line teaches `retire`.
    ✔ `export_html` (the execution table labels AC-004 `ungraded`); `gate_run` ready;
      `package_close`; the fixture updated.

**Pass bar:** every ✔ observed; `gate_run` ready (or failing ONLY on deliberately-open
items the scenario names); the eval runner's lab checks green. `readiness_check` is
expectedly NOT ready on the scenario's deliberately-open items (AC-003 and, since beat
13, the ungraded export AC — AC-005 in the recorded fixture; LL-002; OQ-001 — whose
`due_by` also trips `open-questions-overdue` by calendar and the `open-questions-resolved`
/ `clarifications-open` pair; the waived DEF-003) — anything else failing there is a finding.
