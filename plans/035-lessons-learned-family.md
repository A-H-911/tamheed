# Plan 035 (B31): the lessons-learned entity family — v4.3.0

## Status

**DONE (2026-08-15)** — all six phases executed, `python check.py` fully green (8
suites incl. 8 new tests — 6 contract, 1 store-migration, 1 viewer; all 11 lints;
canonical unchanged — a zero-row table emits no file; 3 eval cases incl. the
14-assertion lab battery against the REGENERATED fixture; the scheduled eval-spec
lint replicated locally, green), `--selftest` green. Version stamped **v4.3.0** (MINOR — additive family via
migration 002; no break). *Release (push + GitHub release) happens only on the
maintainer's explicit words — this line records execution, not publication.*

## What this was

The maintainer's feature ask (no field report — the 4.2.1 cycle closed clean, no
findings_19): execution agents make mistakes and learn; the lessons must be recorded
IN the package as a sophisticated first-class entity, interviewed and CONFIRMED by
the operator, and remembered by the executing agent ALL THE TIME.

Method: internet research (PMI lessons-register practice; NASA LLIS's
approval-before-entry workflow; Reflexion/agent-memory research — persisting a WRONG
lesson is the documented failure mode, which is the research case for the operator
gate; the CLAUDE.md curation ceiling ~150-200 instructions; US Army AAR's two
polarities) + two parallel explorers (the additive-extension mechanics; every
delivery surface) + **eight interview forks locked across two rounds** (both
polarities; capped note section; strict Approved-only gate; the learned_from
relation; staged registry-sync via package_migrate; fold into existing prompts;
pinned-first cap 10; the full LLIS column set) + advisor + the devil's-advocate
round (which corrected two explorer-derived claims by direct read: the ADR
immutability trigger is ALREADY column-selective, and trace_edges carries zero
triggers — so migration 002 is simpler than drafted) + the maintainer's mid-review
addition: the full review.html treatment (the dedicated Lessons section, not just
the automatic register fold).

## What shipped

1. **Migration `002_lessons.sql`** — the v4 chain's first real migration, validating
   the extension recipe in-tree. The LLIS-shaped `lessons` table (statement /
   context / recommendation / rationale / kind improve|sustain / category / both
   impacts / recorded_at / confirmed_by+confirmed_at / pinned / superseded_by);
   lifecycle Proposed→Approved/Rejected/Superseded→Obsolete (no Draft, no Deferred
   — an undecided lesson nags by design); the entity_index trigger pair; the
   column-selective immutability trigger (content freezes at approval; pinned,
   lifecycle, superseded_by stay mutable); trace_edges recreated with
   `learned_from` (empty at migration time — migrations apply before the JSONL
   load, test-pinned).
2. **The always-loaded surface**: the `tamheed:note v4` span renders Approved
   lessons — pinned always, cap 10 unpinned, numeric CAST ordering, one-line
   flattened statements, the count line; zero approved = no section (byte-stable
   for lesson-less packages). G-INJECT screens each RAW statement and blocks the
   emit naming the LL- row (two screens: the operator interview + the pattern
   scan). The obligations table gained the capture row in the note AND
   agent-control.template.md — with the sync test-enforced for the first time
   (it caught the template missing the row on its first run).
3. **`lessons-confirmed`** — the 14th package advisory (fires on existence; no
   hollow-pass class; waiver support inherited).
4. **Registry-sync in `package_migrate`**: staged (preview `mode: "registry-sync"`
   + `entity_types_added`; confirm appends + a typed PE- note; pure append, no
   backup taken; an existing data-v3-backup never blocks it; an up-to-date v4
   store still refuses). This shipped extension.md's promised "registry-row write
   path".
5. **The viewer**: the dedicated Lessons section (confirmation queue → Approved
   with pinned/impacts/attribution → closed rows folded), placed between
   Execution progress and Registers; the flow lane; registers/graph/CSV automatic.
6. **Teaching**: catalog row + entity-map/lifecycle diagrams; governance (LL- row,
   the lesson status set, learned_from — lint-11 needle added); 7 stock prompts
   (capture in drift-register/progress-sync/slice-review/defect-triage; reading in
   package-onboarding/orient-resume; the operator interview in register-liveness
   step 14 incl. the pin decision and the re-read-then-resend rule); 4 templates;
   docs/entities.md full family study with sources; 13 docs/references files swept.
7. **The lab continuation (the real-agent proof, run in-session):** an agent drove
   scenario beat 10 against the RECORDED package — the FK refusal fired verbatim;
   the staged registry-sync previewed and confirmed on scripted operator words;
   the agent AUTHORED two lessons grounded in the recorded defects (its own
   judgment, per the rubric); the advisory listed both; the operator words
   approved + pinned LL-001 only; the re-emitted note carried the pinned lesson
   and NOT the Proposed one; gates stayed green end-to-end. **The lab also did
   its job on the plan itself**: the original eval assertion (`nonempty lesson
   confirmed_by`) could NEVER pass against a scenario-conformant fixture (the
   deliberately-Proposed remainder has an empty confirmed_by) — caught on first
   run, replaced with the count-on-Approved form, recorded in the assertion text.

## Verification

`python check.py` green end-to-end; `uv run … --selftest`; the lab agent's
step-by-step report (every scenario ✔ observed; one agent stumble — a wrong edge
type name — was rejected loudly by the server with the valid-type list, exactly the
fail-closed contract).

## Left open (operator-side, in the delivery prompt)

ACMP's path: upgrade → staged registry-sync → record their first lesson (findings_18
§1, paste-don't-retype, is the natural LL-001) → confirm + pin. Their three
customized prompts will not receive the new capture steps via refresh (the 4.2.1
lag warning names them; hand-merge). The plan-033 GitHub diagram-render
confirmation remains open.
