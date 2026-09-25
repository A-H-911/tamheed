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

14. **The export continuation (v4.7.0, plan 041)** — another INCREMENTAL session against
    the recorded package (findings_24: a committed script had no sanctioned route to whole
    canonical rows under an MCP-exclusive read rule):
    ✔ `package_migrate` preview REFUSED verbatim as before (record the text).
    ✔ THE EXPORT: `entity_export("slate-rows.json", args={"type": "acceptance-criterion",
      "ids": ["AC-003", "AC-005"]})` → the file at `<package>/exports/slate-rows.json`;
      the result's `digest` EQUALS `package_verify()["digest"]`, `partial: false`,
      `memory_matches_disk: true`, and the result carries no rows.
    ✔ A COMMITTED generator in the lab workspace, `workspace/scripts/gen-slate.py`
      (stdlib Python, ~60 lines): reads the export (path as its argument), writes
      `workspace/slate.html` quoting each row's `statement` byte-exact (escaped for
      HTML), headed by the export's digest; then CALIBRATES its verifier — re-reads the
      export and compares every quoted statement to the file byte-for-byte, then
      deliberately corrupts one character and the comparison MUST report it (the
      ACMP pattern). The script never opens `data/`.
    ✔ A whole-family export: `entity_export("verdicts.json", args={"type":
      "audit-verdict", "limit": 1})` → `partial: true` with the PARTIAL note; then
      `limit: 1000` → `partial: false`, `count == total`.
    ✔ `entity_export("gates.json", tool="gate_run")` works; two refusals verbatim: a path
      under `data/` (`../data/x.json`) and `tool: "entity_upsert"`.
    ✔ THE PASTE GUARD on the unguarded-register class the field named: re-upsert `DEF-001`
      (full row from `entity_query`) with `expect_unchanged: ["title"]` and ONE word of
      the title altered → REFUSED naming `title` (record the text); the exact stored
      title with only `severity` changed → accepted; restore the severity the same way.
    ✔ `handoff_emit` re-run: the note's export sentence + the two cheat-sheet lines.
    ✔ `export_html`; `gate_run` ready; `package_close`; the fixture updated — the export
      files under `exports/` and the workspace script are part of it. *Recorded fixture
      note:* the exports carry the digest of the state they quoted; the committed store
      verifies at a LATER digest because the beat's closing journal row followed — an
      export names the state it came from, never the head, which is exactly why a slate
      cites its digest and the operator compares it with a fresh `package_verify()`.

15. **The advisor-audit continuation (v4.8.0, plans 042–057)** — another INCREMENTAL
    session against the recorded package (the 2026-09-10 advisor audit: sixteen plans,
    every one executed and accepted; this beat fires the mechanisms a lab can reach):
    ✔ `package_migrate("package")` preview REFUSED verbatim as before (record the text).
    ✔ NAMES: `package_open("../package")` → REFUSED `invalid package name` (plan 044;
      record the text); nothing is opened.
    ✔ THE STALE-TREE ROLLBACK (plan 043): with the package OPEN, hand-edit
      `data/risks.jsonl` (one character inside an existing title — the one sanctioned
      hand edit of this beat, restored below), then `entity_upsert` a new `RISK-` row →
      REFUSED naming `risks.jsonl` and `NOT applied` (record the text); `entity_query("risk")`
      shows NO new row (the batch rolled back); `package_close()` warns `WITHOUT the final
      flush`; restore `risks.jsonl` from the backup byte-for-byte; `package_open` → clean;
      `package_verify()` → `verified: true`.
    ✔ BORN-IMPLEMENTED (plan 053): `entity_upsert` a new slice `SL-003` ("Export polish",
      `phase_id PH-1`) with `lifecycle_status: "Implemented"` → REFUSED
      `cannot be created as Implemented` (record the text); the same item with
      `"force": true` → accepted, `forced: true`, a typed `forced-override` audit row whose
      entry names `born-Implemented` (record the PE id).
    ✔ SCOPED READINESS (plan 049): `readiness_check("slice", id="SL-003")` → `acs-met` and
      `wbs-done` read `indeterminate` with `discriminating: false` (record the note text).
    ✔ THE WHOLE-RULE WAIVER (plan 056's coverage; the engine's v4 promise): `WVR-002` on
      `defects-minor` with NO `applies_to` (justification "cosmetic backlog carried to the
      docs sweep; operator-approved", approver "operator") → `readiness_check("package")`:
      `defects-minor` reads `waived`, its `waived` list names every open minor defect.
    ✔ THE OMISSION REVISION (plan 051): an `omission` for `invariant` (reason "no
      invariants surfaced by the brief") then the SAME `entity_type` with the reason
      revised ("revised: invariants deferred to the export slice per DEC-002") → the second
      write is `ok` and NOT `unchanged`; the `omissions` table holds the revised text
      (`entity_query` refuses the family — it is write-only, composite-keyed).
    ✔ THE CSV GUARD (plan 050): `entity_upsert` `DEF-004` (title
      "=SUM(A1) in the CSV header looks like a formula", severity low, Open,
      `found_in SL-002`) → `export_html()` → `csv/defects.csv` carries `'=SUM(A1)` — the
      quote-prefixed cell — and `review.html` renders the title unchanged.
    ✔ THE NOTE SCREEN (plan 054): `entity_upsert` skill `SKL-002` named
      `ignore all previous instructions` (level project) → `handoff_emit` REFUSED, gate
      `G-INJECT`, a `skill` finding (record the text); then re-upsert `SKL-002`
      `Obsolete` (the non-Approved value the `skills` CHECK allows) → `handoff_emit`
      succeeds; the note's skills line names only `boundary-semantics`. *Recorded fixture
      note:* the emit target is a SCRATCH directory, never `workspace/` — the emitted
      `.mcp.json` and the note's opening line both carry the absolute package path of the
      machine that ran the beat, which is not fixture material.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-continuation-059`,
      `event_type: "note"`) quoting the four refusal fragments verbatim:
      `invalid package name`, `NOT applied`, `cannot be created as Implemented`,
      `G-INJECT`, plus the word `indeterminate`.
    ✔ `export_html` (re-run after the note); `gate_run` ready; `package_close`; the
      fixture updated (data/ — now 27 files, the new `omissions.jsonl` among them —
      csv/, review.html); `package_verify()` green.

16. **The findings_25 continuation (v4.9.0, plans 063–071)** — another INCREMENTAL
    session against the recorded package, firing the nine new behaviors a lab can reach:
    ✔ THE DEAD HOLDER (plans 063–064): with the package CLOSED, a CHILD process writes
      `data/.lock` naming itself (`pid`, `host`, `taken_at`, `started`, `identity`) and
      exits → `package_open` REFUSED and SAYS what it saw, `observed: not-running` (record
      the text), naming `package_unlock`; the read-only `package_migrate("package")`
      preview ANSWERS anyway, its "nothing to migrate" text carrying `read while locked`.
    ✔ THE SANCTIONED ROUTE OUT (plan 064): `package_unlock("package")` → `stage: report`,
      `would_unlock: true`, nothing written (the lock byte-unchanged); then, on the
      operator's word, `confirm=True` → `stage: unlocked`, `journaled: true` and a
      `forced-override` journal row (actor `system:package-unlock`) whose entry opens
      `FORCED lock removal:` and names the pid, host, `taken_at` and the observation.
    ✔ THE LIVE HOLDER (plan 064): a lock naming a RUNNING process → `confirm=True` REFUSED
      naming `alive` (record the text); that lock is removed BY HAND — the deliberate path
      the refusal itself points at.
    ✔ THE LEGIBLE READS (plans 066, 068, 069): `server_info()` carries a `package` block;
      `server_info(detail=True)` names every entity type and each relation's endpoints; a
      `defect` query projected to `id`+`title` reports `omitted_columns`, and a `search`
      reports `matched` — WHICH column each row matched in, `found_in` here, a column the
      projection never returned; `readiness_check("package")` rules carry their
      `population` (table, rows, scoped), so a pass over nothing is visible as such.
    ✔ THE PHANTOM ID (plan 070): a new `DEF-` row whose title cites a `RISK-` that does not
      exist → `readiness_check` advisory `prose-ids-resolve` names `<id>.title -> RISK-909`
      and NOT the real `DEF-001` beside it; correcting the title clears the rule.
    ✔ THE PARTIAL EXPORT (plan 067): `entity_export` of one row of a five-row family → the
      FILE's `tamheed_export` envelope carries `count`, `total` and `"partial": true`; the
      digest it cites, fed back as `package_verify(expect=…)`, reads `matches_expected: true`.
    ✔ `csv/` (plan 065): a retired table's `csv/prompts.csv` and an operator's
      `csv/operator-notes.csv`, both planted BY HAND → `package_verify()` names both under
      `foreign_csv`; `export_html()` REMOVES the retired one and leaves the operator's file
      alone as `unowned`.
    ✔ THE STOCK PROMPTS (plan 071): `handoff_emit(refresh_stock=True)` into a SCRATCH
      directory → `prompt_library.refreshed` names the five changed bodies
      (`README.md`, `integrity-check.md`, `orient-resume.md`, `register-liveness.md`,
      `replan-deferred.md`), with nothing `diverged`/customized to preserve.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-16`,
      `event_type: "note"`) quoting verbatim the `observed: …` clause, the `alive` refusal
      and the `prose-ids-resolve` entity string; then `package_verify(expect=<the export's
      digest>)` → `matches_expected: false` — ANY write moves the package digest;
      `export_html`; `gate_run` ready; `package_verify()` green (`foreign_csv: []`);
      `package_close`; no `data/.lock` remains.
17. **The findings_26 continuation (v4.10.0, plans 075–081)** — another INCREMENTAL
    session against the recorded package. A lesson turns out false. Its correction is
    recorded and the false lesson is pointed at it — and the engine SAYS the pointer
    retires nothing: the false lesson still binds. The agent tries to retire it unattended
    and is refused: what binds on the operator's word stops binding on it too. The
    operator approves the correction, and the engine retires the false lesson in that same
    write, journaled. Along the way a re-sent statement that lost its second paragraph
    shows up as a number; a backticked phantom id is reported as inert rather than hidden;
    the open-ended blanket waiver is named; a rule over an empty family reads
    `indeterminate` until the omission is recorded, then `pass`; the review page says
    whether it is current; and on a scratch copy a hand-merged prompt declares its merge
    and stops lagging.
    ✔ THE LOST PARAGRAPH (plan 080): a new `LL-` correction re-sent with its last
      paragraph dropped → the item's `changed_columns` names `statement` with
      `old_len` > `new_len`; re-sent in full it reverses, re-sent unchanged it is `[]`.
    ✔ THE HALF-FINISHED SUPERSESSION (plan 075): the false lesson is Approved on the
      operator's word; pointing it at its successor UNATTENDED is REFUSED for `pointing a
      BINDING lesson at a successor`; with `operator_confirm` the pointer lands and the
      `next` hint says the row `is still Approved, so it KEEPS BINDING`; the emitted
      always-loaded note reads `superseded by <LL-NNN> - pending its approval`.
    ✔ THE OPERATOR'S WORD, BOTH WAYS (plan 075): retiring the binding lesson UNATTENDED —
      to `Superseded`, then to `Proposed` — is REFUSED both times for `retiring a lesson
      that BINDS future sessions` (record the text); approving the successor on the
      operator's word retires it in that same write (`superseded: [<LL-NNN>]`), journaled
      as a `transition` by actor `system:lesson-supersession`.
    ✔ THE BACKTICKED PHANTOM (plan 076): the beat-16 defect's title re-sent citing a
      phantom id inside a code span → `prose-ids-resolve` lists it under `in_code_spans`
      as `<id>.title -> RISK-808` while `entities` stays empty, the note saying the entity
      list is a FLOOR. The title is LEFT as it is: the inert report is the point.
    ✔ THE OPEN-ENDED WAIVER (plan 079): `waivers-open-ended` fails, advisory, naming
      `WVR-002` — the whole-rule waiver with no expiry. It stays open-ended on purpose: a
      dated expiry would become a time bomb in a fixture replayed for years.
    ✔ NO RULE PASSES OVER NOTHING (plan 077): `deferred-work-reviewed` reads
      `indeterminate`, `discriminating: false`, `population.rows: 0`, `measured nothing`;
      recording the family's omission turns it `pass` carrying `omitted` with the reason,
      and neither `gate_run`'s nor `readiness_check`'s `ready` moves. `hypotheses-measurable`
      is LEFT `indeterminate` — one explained zero beside one amber zero is the contrast.
    ✔ THE STALE REVIEW PAGE (plan 081): `package_verify()["review_current"]` is `null` on
      the recorded page (it predates the stamp) and `true` after `export_html()`, whose
      `review.html` carries `<meta name="tamheed-digest" …>`.
    ✔ THE COMPLETED HAND-MERGE (plan 078) — on a SCRATCH COPY, never the fixture: two
      prompts rewritten by hand, one declaring `<!-- tamheed:stock-merged <current> -->`
      and one declaring `3.0.0` → both are `diverged_customized` with
      `contains_current_stock: false`, and the `CUSTOMISED` warning's lag list names the
      stale declaration only. The fixture's own prompts stay stock.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-17`,
      `event_type: "note"`) quoting verbatim the `retiring a lesson that BINDS future
      sessions` refusal, the `KEEPS BINDING` hint, the `changed_columns` length drop, the
      `in_code_spans` entity string, `waivers-open-ended` naming `WVR-002`, `measured
      nothing` and `omitted`, and the `review_current` values; then `export_html`;
      `gate_run` ready; `package_verify()` green (`review_current: true`,
      `foreign_csv: []`); `package_close`; no `data/.lock` remains.
18. **The findings_27 continuation (v4.11.0, plans 085–087)** — another INCREMENTAL
    session against the recorded package. The agent needs a function the tools lack and
    records it as feedback instead of writing a script; the operator confirms it and it
    leaves the package as an export. The agent registers the lab's one local tool on the
    operator's word after an unattended attempt is refused, and an attempt to rewrite the
    confirmed row underneath the operator's name is refused. A lesson is retired by hand
    on the operator's word and the engine writes the row; a forged engine row is refused.
    A formula's variable names stop tripping the prose-id scan, and the two stock prompts
    refresh.
    ✔ THE REGISTRY SYNC (plan 087): the recorded store's `entity_types` predates the
      `feedback` family, so `package_migrate` runs FIRST in `registry-sync` mode (preview,
      then confirm) — `entity_types_added: ["feedback"]`, `backup: "none (registry-sync is
      a pure append)"` — journaled as `REGISTRY-SYNC: entity types added (feedback)` by
      actor `system:migrate`, exactly as beats 10 and 12 did for `lesson` and `skill`.
    ✔ THE UNDERSCORE (plan 085): `DEF-005`'s title is re-sent in full carrying a formula
      whose variables are `KPI-17_score` and `KPI-10_score` → `changed_columns` names
      `title` alone, and `prose-ids-resolve` still reads `pass` with `entities` [],
      `in_code_spans` exactly `["DEF-005.title -> RISK-808"]` and `not_well_formed` [] —
      the variable names appear NOWHERE, because `_` is a word character and, as the
      rule's own note says, `width is tested first`. `hypotheses-measurable` is the
      `indeterminate` rule whose note carries `scoped: false`.
    ✔ THE MISSING FUNCTION AS FEEDBACK (plan 087): `FB-001` is born `Proposed` for a patch
      mode the tools lack, in place of the script that would otherwise have done the
      substitution; the UNATTENDED confirmation is REFUSED for `feedback leaves the
      package only on the OPERATOR's word`, and `handoff_emit` names it while it waits —
      `1 feedback row(s) await the operator's word (FB-001)`. On the operator's word it is
      `Confirmed` carrying a `feedback_audit`, journaled by actor `system:feedback-guard`.
    ✔ THE REWRITE UNDER THE NAME (plan 087): the same row re-sent `Confirmed` with a
      changed `detail` and NO word is REFUSED for `content drifted on ['detail']`, and the
      stored `detail` does not move.
    ✔ THE ROW THAT LEAVES (plan 087): the next emission asks for the export instead —
      `entity_export("feedback.json", args={"type": "feedback"})` writes an envelope with
      `total: 1`, `partial: false` — and `FB-001` then goes `Reported` with NO operator
      word needed, because it has left.
    ✔ THE LOCAL TOOL (plan 087): `FB-002` (`kind: local-tool`, `tool_path:
      evals/pkg_check.py`) is REFUSED at INSERT for `a local tool over the package exists
      only on the OPERATOR's word` — the family total stays 1 — then lands `Confirmed`
      with a `feedback_audit` on the word. `FB-001`'s `detail` names `DEF-005` and the
      phantom `RISK-808` and neither appears in any `prose-ids-resolve` list: the family
      is exempt, like the journal.
    ✔ THE BY-HAND RETIREMENT (plan 086): `LL-005` is recorded, approved on the operator's
      word (`lesson_audit`), then retired BY HAND to `Superseded` with no successor — a
      lesson withdrawn — and the ENGINE writes the row: `lesson_audit`, actor
      `system:lesson-guard`, `LESSON LL-005 -> Superseded (was Approved) on the operator's
      word, by hand`.
    ✔ THE RESERVED NAMESPACE (plan 086): that same row forged by hand is REFUSED on BOTH
      caller paths — `progress_update` and the `progress-entry` upsert — in the same
      words, `actor 'system:lesson-guard' is the engine's own namespace`; no forged row
      reaches the journal.
    ✔ THE PROMPTS (plan 087): `handoff_emit(refresh_stock=true)` reports `refreshed`
      exactly `prompts/orient-resume.md` and `prompts/README.md` with
      `diverged_customized` empty, and the refreshed guide teaches the `FB-` row and the
      `local-tool` row (the stock scenarios are the plugin's skills since beat 22 / v5.0.0;
      the guide is the one stock file).
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-18`,
      `event_type: "note"`) quoting verbatim the `leaves the package only on the
      OPERATOR's word`, `content drifted on ['detail']`, `a local tool over the package
      exists only on the OPERATOR's word` and `engine's own namespace` clauses, the words
      `feedback_audit` and `lesson_audit`, and `width is tested first`; then `export_html`;
      `gate_run` ready; `package_verify()` green (`verified: true`, `foreign: []`,
      `foreign_csv: []`, `review_current: true`); `package_close`; no `data/.lock` remains.
19. **The findings_28 continuation (v4.12.0).** The project's kickoff prompt narrates a
    phantom id and the new prompt rule reads amber; quoting it in backticks makes it inert
    and visible. A token census with context counts every occurrence of a known id. The
    package's go/no-go verdict is changed on the operator's word after an unattended
    attempt is refused, and a string `"false"` does not attest. One token in a long defect
    title is corrected by a `substitute` write that touches nothing else, a match glued to
    a digit is refused, and a substitute on an Approved lesson is refused. The review page
    gains its Readiness and Feedback sections.
    ✔ THE PROMPT RULE (plan 093): one history line naming two ids that resolve to nothing
      is appended BY HAND to `prompts/project-kickoff.md` — a prompt is a file — and
      `readiness_check("package")` reads `prompt-ids-resolve` `status: fail` over
      `population` `{table: "prompts/*.md", rows: 1, scoped: false, unit: "files"}`, its
      `entities` naming `prompts/project-kickoff.md:4 -> DEF-090` and
      `prompts/project-kickoff.md:4 -> SL-007`, under the note's own `THE ENTITY LIST IS A
      FLOOR`. Quoting both ids in backticks makes them inert: the rule reads `pass`,
      `entities` empties and both move to `in_code_spans`. `gate_run` never moves — the
      rule is advisory.
    ✔ THE CENSUS (plan 092): `entity_query("defect", search="RISK-808", context=12)`
      reports `matched` `{"DEF-005": ["title"]}` and `occurrences` `DEF-005.title`
      `count: 1` with one snippet carrying `` `RISK-808` ``;
      `entity_query("defect", search="KPI-1", context=8)` counts TWO `occurrences` in that
      same title — `KPI-17_score` and `KPI-10_score`. A census counts SUBSTRINGS; the
      prose-id rule does not, and those two tokens still trip no id list.
    ✔ THE HEADER (plan 094): `entity_upsert(type="package")` writes `entry_point` =
      `prompts/project-kickoff.md` — `changed_columns` names it alone and
      `server_info().package` reads it back. The UNATTENDED verdict is REFUSED for
      `go_no_go is the package's governance verdict and changes only on the OPERATOR's
      word`, and a STRING `"true"` is refused in exactly the same words — only the JSON
      boolean attests. On the operator's word the verdict lands and the ENGINE witnesses it
      in the same savepoint: `package_audit` `PE-034`, `event_type: "transition"`, actor
      `system:package-guard`. `profile` stays frozen: `header column(s) ['profile'] are the
      package's identity and are frozen`.
    ✔ THE SUBSTITUTE (plan 095): one token in `DEF-005`'s long title is corrected by a
      `substitute` write — `substituted` `{"title": 1}`, `changed_columns` exactly one
      entry with `old_len` and `new_len` both 108 — and every other column of the row stays
      byte-identical to the pre-beat backup. A match glued to a digit is REFUSED:
      `'KPI-1' in 'title' also matches inside a longer token ('KPI-17_score')`. A
      substitute on the Approved lesson `LL-004` is REFUSED by the immutability trigger —
      `approved/promoted lessons are immutable: supersede, never edit` — and a mixed item
      is REFUSED because `a substitute item carries only type, id, substitute,
      operator_confirm and expect_unchanged`.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-19`,
      `event_type: "note"`) quoting verbatim the pre-backtick entity string, the `changes
      only on the OPERATOR's word` clause, the glued-match refusal naming the
      `longer token ('KPI-17_score')`, the words `substituted`, `occurrences` and
      `package_audit`, and `in_code_spans` — written BEFORE the export, so the page is
      re-rendered after it; then `export_html`, whose page carries
      `<section id="readiness">`, `<section id="feedback">` and `Evaluated as of` (plan
      096); `gate_run` ready; `package_verify()` green (`verified: true`, `foreign: []`,
      `foreign_csv: []`, `review_current: true`); `package_close`; no `data/.lock` remains.
20. **The findings_29 continuation (v4.13.0).** The request the project reported in beat
    18 has been answered upstream; the readiness rule and the handoff warning had named it
    every day until now. It is resolved by a partial row — id, kind, title and the three
    bookkeeping columns — and the engine journals the move as bookkeeping, claiming no
    word. The MVP definition is written and read back through the tool. Re-sending the
    current verdict without the operator's word is refused; with it, nothing is journaled
    because nothing moved. A prefix repair by `substitute` passes once and is refused the
    second time. A partial defect row names an omitted column in `expect_unchanged` and
    passes.
    ✔ THE CHANNEL'S MIDDLE (plan 100): `FB-001` — the patch-mode request beat 18 filed,
      answered upstream by plan 095 in 4.12.0 — is closed by the disposition recipe the
      readiness note itself teaches: a PARTIAL row of `id`, `kind`, `title`,
      `lifecycle_status: "Resolved"`, `resolved_in: "4.12.0"` and
      `upstream_ref: "tamheed plan 095"`. `changed_columns` names exactly those three
      bookkeeping columns, and `detail` and `workaround` read back byte-identical to the
      pre-beat backup — the absence of a column from `changed_columns` is the proof that
      the UPDATE preserved it. The engine journals the move itself: `feedback_audit`
      `PE-036`, `event_type: "transition"`, actor `system:feedback-guard`, entry
      `FEEDBACK FB-001 -> Resolved (was Reported; kind missing-capability) — bookkeeping,
      no word required; resolved_in 4.12.0; upstream_ref tamheed plan 095` — and it never
      says `attested`, because no word was asked for or given. The advisory
      `feedback-unanswered` moves from `fail` (`entities: ["FB-001"]`) to `pass` with an
      empty list, and `handoff_emit`'s third feedback warning — the one naming `FB-001` as
      `reported upstream and not yet answered` — is gone.
    ✔ THE HEADER READ (plan 101): `entity_upsert(type="package")` writes `mvp_definition`
      and `server_info().package` reads it straight back, together with all ten header
      columns — `created_at` (`2026-08-14T14:33:11Z`) among them, which no caller may
      write. `v1_manifest_derived` is ABSENT: this package was born v4 and was never
      migrated from a v1 manifest, so there is nothing for that key to annotate.
    ✔ THE VERDICT, PRESENCE-CHECKED (plan 102): the CURRENT verdict, re-sent unchanged and
      unattended — the shape the change-checked guard let through, so the 4.12.0 brief's
      refusal probe could not fail — is REFUSED: `go_no_go is the package's governance
      verdict and changes only on the OPERATOR's word`. On the operator's word the same
      item is accepted with `changed_columns: []` and NO `package_audit` key, and the
      progress-entry total holds at 36 across the step: the audit row is written only when
      the verdict MOVES.
    ✔ THE SUBSTITUTE RE-RUN (plan 102): a prefix repair on `DEF-005`'s long title —
      `DEF-001` to `DEF-001 (fixed in SL-002)` — lands once (`substituted` `{"title": 1}`,
      `old_len` 108, `new_len` 126). Sent a SECOND time, byte-identical, it is REFUSED:
      `'DEF-001 (fixed in SL-002)' already occurs 1 time(s) in 'title' and contains
      'DEF-001' — a re-run would compound it`. The title still carries exactly one
      `DEF-001 (fixed in SL-002)`.
    ✔ EXPECT_UNCHANGED HONOURS OMISSION (plan 102): a PARTIAL `DEF-005` row naming
      `custom_attributes` in `expect_unchanged` while OMITTING it is ACCEPTED with
      `changed_columns: []` — an omitted column is preserved by the UPDATE, so naming it is
      a true assertion, never drift. The same item with a drifted value actually SENT is
      REFUSED: `custom_attributes differ(s) from the stored row (a sent column must match;
      an omitted column is preserved by the UPDATE and never counts as drift)`.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-20`,
      `event_type: "note"`) quoting verbatim `bookkeeping, no word required`, the `changes
      only on the OPERATOR's word` clause, `already occurs 1 time(s)`, `omitted column is
      preserved`, and the words `feedback-unanswered` and `mvp_definition` — written BEFORE
      the export; then `export_html`, whose page carries `id="feedback-closed"` and
      `Resolved or rejected (kept as evidence)` and no longer files live reports under the
      closing heading `Reported, resolved or rejected` (plan 100); `gate_run` ready;
      `package_verify()` green (`verified: true`, `foreign: []`, `foreign_csv: []`,
      `review_current: true`); `package_close`; no `data/.lock` remains.
21. **The findings_30 continuation (v4.14.0).** The third slice closed a year ago with no
    criteria and no work items, and the tool had called it ready while its own page called
    it not ready. Now the tool says `ready: false` and names the two rules that could not
    discriminate; one work item and one criterion with a Met verdict make it ready. The
    pointer warning says what it did; the page says when nothing awaits an answer; a guard
    that could only pass is refused; the deferred-work advisory reads its recorded omission
    as a deliberate zero.
    ✔ READY FOLLOWS ITS OWN DOCTRINE (plan 106): untouched, `readiness_check("slice",
      id="SL-003")` reads `ready: false` with `indeterminate: ["acs-met", "wbs-done"]` —
      both rules `status: "indeterminate"`, `discriminating: false`, scoped `population`
      `rows: 0`. A rule that cannot discriminate is not a pass, and the page has always
      said so. Populating the slice through the tools — `WBS-4` (`slice_id: "SL-003"`,
      `Implemented`) and `AC-006` (`requirement_id: "FR-001"`, `slice_id: "SL-003"`,
      `Approved`) with an `audit_record` `Met` verdict (`verified_by: "agent"`,
      `verification_method: "inspection"`, `against_commit`) — flips it to `ready: true`,
      `indeterminate: []`, both populations `rows: 1`. `SL-001` reads `ready: true`,
      `indeterminate: []` before and after: the fix discriminates, it does not blanket.
    ✔ THE OMISSION AS A DELIBERATE ZERO (plan 107): `deferred-work-reviewed` passes over an
      empty family and SAYS why — `no deferred_work rows, and the family's omission is
      recorded: a deliberate zero` — carrying the recorded reason back in `omitted`
      (`The lab tracker defers no work: every slice is in scope for its phase.`). The note
      also names Open and Scheduled as the rows a human still judges. **No `DW-` row is
      written here**: the recorded omission IS the answer.
    ✔ THE POINTER WARNING TELLS THE TRUTH (plan 107): with a root `CLAUDE.md` in a scratch
      target that imports `@package/CLAUDE.md`, the first `handoff_emit` warns that the
      managed span `was rebuilt there; the root file was left untouched`; an idle
      re-emission warns that it `is current there; nothing written; the root file was left
      untouched` and returns `written: []`. The warning reports what the call did, not what
      the call might have done.
    ✔ THE EMPTY FOLD SAYS SO (plan 107): `export_html`'s page renders
      `<p class="empty" id="feedback-reported">No reported feedback awaits an answer.</p>`
      instead of an empty fold — the channel's two rows being `FB-001` `Resolved` and
      `FB-002` a `local-tool` register, which never reports.
    ✔ THE VACUOUS ASSERTION REFUSED (plan 108): a `DEF-005` item naming `custom_attributes`
      in `expect_unchanged` while OMITTING that column is REFUSED — `expect_unchanged names
      column(s) this item does not carry (custom_attributes) — an omitted column is
      preserved by the UPDATE, so naming it asserts nothing: drop it from expect_unchanged,
      or send it`. The same item naming `title`, a column it DOES carry, is accepted with
      `changed_columns: []`. Beat 20 proved the omitted-column write passes; a guard that
      could only ever pass now says so instead of pretending to check.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-21`,
      `event_type: "note"`) quoting verbatim `SL-003 read ready: false`,
      `indeterminate: ["acs-met", "wbs-done"]`, `is current there; nothing written`,
      `No reported feedback awaits an answer`, `asserts nothing` and `a deliberate zero` —
      written BEFORE the export; then `export_html`; `gate_run` ready; `package_verify()`
      green (`verified: true`, `foreign: []`, `foreign_csv: []`, `review_current: true`);
      `package_close`; no `data/.lock` remains.
22. **The v5.0.0 continuation.** The sixteen scenario prompts the package had carried since v3
    are the plugin's slash skills now; the tool named the sixteen leftovers, refused to delete them
    on a plain emit, and deleted them on `refresh_stock` because each was byte-equal to shipped
    stock. The note it wrote is v5: the obligations table stays, the cheat-sheet is gone, the
    plugin's skills are named, and the flush sentence finally says which tool flushes what. On a
    scratch package a work item `carries` an activated deferred row and the advisory watches the
    carrier close; the lab's own deferred-work omission still reads as a deliberate zero. The
    note-budget step says what the field measured: an unpinned retirement removes nothing.
    ✔ THE RETIRED LIBRARY (plan 116): opened at `schema_version: 6` (migration 006 applies at
      connect; `package_migrate` is NOT run). A plain `handoff_emit` into a SCRATCH target with
      no `CLAUDE.md` reports `project_prompts: ["project-kickoff.md"]`, sixteen
      `leftover_stale_stock` entries (`{"file": "prompts/<name>.md", "matches": "<release>"}`),
      `leftover_customized: []`, `retired: []`, and warns `16 retired stock prompt(s) remain`
      with `re-run with refresh_stock=true to delete them safely` — and deletes nothing: all
      18 files are still on disk. `handoff_emit(refresh_stock=true)` reports `retired` (the
      sixteen paths), `refreshed: ["prompts/README.md"]` and warns `16 retired stock
      prompt(s) deleted (refresh_stock)`; `prompts/` holds exactly `README.md` and the
      untouched project-authored `project-kickoff.md`, and the guide carries
      `## Which skill, when`. `prompt-ids-resolve` still reads `pass` over `rows: 1`.
    ✔ THE NOTE v5 (plan 116): the scratch `CLAUDE.md` opens `<!-- tamheed:note v5 -->`,
      names the plugin's `tamheed:package-writes` skill, says `work_bind` records a commit
      and `dirties the tree AFTER it`, keeps `### Recording obligations`, and carries no
      `Tool cheat-sheet` and no `tamheed:note v4`. A re-emission returns `written: []` with
      `CLAUDE.md` `unchanged` — the note is byte-stable.
    ✔ CARRIES (plan 113), on a SCRATCH package (`carry`, outside the repository — **no `DW-`
      row is ever written to the fixture**): `DW-001` `Activated` with no carrier →
      `deferred-work-carried` `fail`, `entities: ["DW-001"]` (`deferred-work-reviewed` passes:
      Activated is work, not a judgment). The reverse edge `DW-001 carries WBS-1` is REFUSED —
      `does not allow deferred-work -> wbs-item`; `WBS-1 carries DW-001` lands, the list
      empties and `trace_query("DW-001", direction="in")` shows the one `carries` edge. `WBS-1`
      set `Implemented` → `DW-001` is listed again: the finished activation is visible.
      `G-REL` passes the edge.
    ✔ THE ARITHMETIC (plan 112): `register-liveness`'s step 15 says retiring or rejecting an
      UNPINNED lesson `removes NOTHING` — the fill simply refills; on the fixture
      `lessons-note-budget` passes at 1 rendered lesson line against the ceiling of 20.
    ✔ THE OMISSION FOR BOTH RULES (plans 107, 113): `deferred-work-reviewed` and
      `deferred-work-carried` both `pass` over the recorded `deferred-work` omission, both
      carrying it in `omitted` — `a deliberate zero`.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-beat-22`,
      `event_type: "note"`) quoting verbatim `16 retired stock prompt(s) deleted
      (refresh_stock)`, `Which skill, when`, `tamheed:note v5`, `dirties the tree AFTER it`,
      `deferred-work-carried listed DW-001`, `does not allow deferred-work -> wbs-item`,
      `removes NOTHING`, `schema_version 6` and `a deliberate zero`; then `export_html`;
      `gate_run` ready; `package_verify()` green (`verified: true`, `foreign: []`,
      `foreign_csv: []`, `review_current: true`); `package_close`; no `data/.lock` remains.

**Pass bar:** every ✔ observed; `gate_run` ready (or failing ONLY on deliberately-open
items the scenario names); the eval runner's lab checks green. `readiness_check` is
expectedly NOT ready on the scenario's deliberately-open items (AC-003 and, since beat
13, the ungraded export AC — AC-005 in the recorded fixture; LL-002; OQ-001 — whose
`due_by` also trips `open-questions-overdue` by calendar and the `open-questions-resolved`
/ `clarifications-open` pair; the waived DEF-003 and, since beat 15, DEF-004 — the CSV-guard
defect, open low, waived by `WVR-002`, which, being a WHOLE-rule waiver, also sweeps up beat
16's DEF-005 — the phantom-id defect, open low; `SL-003` is Implemented-by-force and was
deliberately empty until beat 21, so its scoped `acs-met`/`wbs-done` read `indeterminate` by
design up to that point — since beat 21 they discriminate and `SL-003` reads ready) — anything
else failing there is a finding.
