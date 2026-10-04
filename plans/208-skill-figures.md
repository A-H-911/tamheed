# Plan 208: the skill figures (the lifecycle map, the discipline citation matrix, one strip per skill)

> Maintainer-executed, 2026-10-05. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G9, G13, G17, G21, G3. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (27 strips and a 27 x 9 matrix derived from the
  skills' own text; the lifecycle map draws only the moves a line states) - **DONE 2026-10-05**

## What this beat changes

- **The discipline citation matrix** (`skills-matrix`): rows the 27 skills by group, columns the
  discipline skills, a mark where the row's SKILL.md cites the column as `tamheed:<name>`. Derived
  by `extract.skill_text()`; a cited name that is no skill fails the build.
- **The lifecycle map** (`skills-lifecycle`): the lesson statuses as pills in CHECK order and the
  skill statuses likewise (G21: no arrow the engine does not state); between them the moves a line
  states: the `lesson-confirmed` and `lesson-promoted` journal events the server writes on the
  status change, `skill-promote`'s interview that writes the `SKL-` row on the operator's word, the
  two retirement columns (`superseded_by`, `upstreamed_to`), and the readiness rules that watch
  lessons (from the rule roster).
- **One strip per skill** (`skill-<name>`): the tools the skill's text names, in the order of first
  mention, with `STOP` where the text marks a ceremony stop in bold (`**STOP`), as a chained row of
  pills; a discipline skill that names no tool says so. In a fold under the skill's group table,
  like the gates.
- Captures: the matrix and the map EN light and dark and AR light, the matrix at 390 px, one
  scenario strip and one discipline strip EN light.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-208.md` (23 pinned phrases in the guide files). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-208.md` (4 files with new tokens: the geometry
  numbers, the two event lines, `STOP`, `SKL`, `CHECK`, the citation form in `extract.py`; no modal drop).

## What landed, beyond the plan

- **The skills' text, read once** (`extract.skill_text()`): per skill the other skills it cites as
  `tamheed:<name>` and the tools and STOPs its text names in order. `tamheed:note` is the CLAUDE.md
  note span's marker (server L3933), not a skill, and is the one token the reader skips by name; any
  other cited name that is no skill fails the build. The table, printed from the facts:

| skill | group | cites | tools named, in order (STOP = a bold ceremony stop) |
|---|---|---|---|
| `ci-evidence` | discipline | `measurement-evidence`, `package-writes`, `reading-the-record`, `test-evidence` | (none) |
| `defect-triage` | scenario | - | `package_open` → `entity_query` → `entity_upsert` → `trace_query` → `audit_record` → `work_bind` → `progress_update` → `gate_run` |
| `drift-register` | scenario | `package-writes` | `package_open` → `entity_query` → `work_bind` → `progress_update` → `audit_record` → `gate_run` → `readiness_check` → `package_close` |
| `generate-report` | scenario | `progress-sync` | `package_open` → `export_html` → `entity_query` → `package_close` |
| `integrity-check` | scenario | `drift-register`, `package-writes` | `package_open` → `package_verify` → `gate_run` → `entity_upsert` → `entity_query` → `trace_query` → `export_html` → `work_bind` → `readiness_check` → `entity_export` → `handoff_emit` → `package_close` |
| `loop-guard` | scenario | `loop-iteration` | `gate_run` → `readiness_check` → `progress_update` → `package_close` |
| `loop-iteration` | scenario | `package-writes` | `server_info` → `package_open` → `gate_run` → `entity_query` → `progress_update` → `package_close` → `audit_record` → `work_bind` → `readiness_check` |
| `measurement-evidence` | discipline | `ci-evidence`, `operator-interview`, `package-writes`, `reading-the-record`, `test-evidence`, `written-claims` | (none) |
| `operator-interview` | discipline | `reading-the-record`, `session-handoff` | `package_unlock` → `package_migrate` → `package_adopt` → `entity_export` |
| `orient-resume` | scenario | `package-onboarding`, `package-writes`, `session-handoff`, `slice-kickoff` | `package_open` → `server_info` → `package_close` → `entity_query` → `package_unlock` → `gate_run` → `entity_export` → `readiness_check` → `work_bind` |
| `package-onboarding` | scenario | - | `server_info` → `package_open` → `entity_query` → `trace_query` → `entity_export` → `gate_run` → `readiness_check` → `export_html` |
| `package-writes` | discipline | `ci-evidence`, `measurement-evidence`, `operator-interview`, `reading-the-record`, `session-handoff`, `test-evidence` | `entity_query` → `readiness_check` → `gate_run` → `progress_update` → `audit_record` → `trace_query` → `server_info` → `package_verify` → `entity_export` → `entity_upsert` → `work_bind` → `package_close` → `export_html` → `handoff_emit` → `package_open` → `package_unlock` |
| `phase-close` | scenario | `slice-review` | `package_open` → `entity_query` → `readiness_check` → `progress_update` → `gate_run` → `export_html` → `package_close` |
| `plain-english` | discipline | `package-writes`, `reading-the-record`, `ste-rewrite`, `written-claims` | (none) |
| `progress-sync` | scenario | `package-writes` | `package_open` → `entity_query` → `progress_update` → `work_bind` → `audit_record` → `gate_run` → `package_close` |
| `reading-the-record` | discipline | `measurement-evidence`, `operator-interview`, `package-writes` | `entity_query` |
| `register-liveness` | scenario | `package-writes`, `plain-english`, `replan-deferred`, `session-handoff`, `skill-promote`, `ste-rewrite` | `package_open` → `readiness_check` → `entity_query` → `STOP` → `entity_upsert` → `trace_query` → `audit_record` → `work_bind` → `STOP` → `server_info` → `progress_update` |
| `release-close-out` | scenario | `register-liveness` | `package_open` → `entity_query` → `readiness_check` → `audit_record` → `progress_update` → `gate_run` → `work_bind` → `export_html` → `package_verify` → `package_close` |
| `replan-deferred` | scenario | - | `package_open` → `entity_query` → `STOP` → `gate_run` |
| `session-handoff` | discipline | `measurement-evidence`, `operator-interview`, `orient-resume`, `package-writes`, `progress-sync`, `release-close-out`, `slice-review` | `package_open` → `server_info` → `progress_update` → `gate_run` → `readiness_check` → `package_verify` → `work_bind` → `export_html` |
| `skill-promote` | scenario | `package-writes`, `written-claims` | `package_open` → `entity_query` → `STOP` → `handoff_emit` → `readiness_check` → `progress_update` → `export_html` → `package_close` |
| `slice-kickoff` | scenario | `slice-review` | `package_open` → `gate_run` → `entity_query` → `trace_query` → `STOP` → `progress_update` → `audit_record` → `work_bind` → `readiness_check` |
| `slice-review` | scenario | `phase-close` | `package_open` → `entity_query` → `trace_query` → `entity_export` → `package_verify` → `audit_record` → `work_bind` → `progress_update` → `entity_upsert` → `readiness_check` → `gate_run` → `export_html` |
| `ste-rewrite` | scenario | `operator-interview`, `package-writes`, `plain-english`, `reading-the-record` | `package_open` → `readiness_check` → `entity_query` → `STOP` → `entity_upsert` → `progress_update` |
| `tamheed` | front | `plain-english`, `reading-the-record`, `session-handoff`, `written-claims` | `package_open` → `package_migrate` → `handoff_emit` → `package_adopt` → `entity_upsert` → `entity_export` → `readiness_check` → `package_create` → `package_close` → `gate_run` → `progress_update` → `audit_record` → `work_bind` → `entity_query` → `package_unlock` → `package_verify` → `trace_query` → `server_info` |
| `test-evidence` | discipline | `ci-evidence`, `measurement-evidence`, `package-writes`, `reading-the-record` | `audit_record` |
| `written-claims` | discipline | `measurement-evidence`, `package-writes`, `plain-english`, `reading-the-record` | `progress_update` |

- **The matrix** holds 54 marks over 9 discipline columns and 27 rows, grouped by the
  three skill groups as frames. Nothing authored: an edit to a skill moves its marks.
- **The lifecycle map draws only stated moves, and all of them the evidence sheet returned.** The
  lesson and skill statuses are pills in CHECK order with no arrow between them (G21). The arrows: a
  lesson set Approved writes a `lesson-confirmed` journal event and one set Promoted a
  `lesson-promoted` event (L1852-1853); a successor lesson approved on the operator's word retires
  the old Approved and Promoted lessons to Superseded with a `transition` row (L2120-2135, the move
  `lessons-superseded-binding` watches; the first map omitted it and the advisor read it back from
  this ledger's own grep);
  `skill-promote`'s interview sets the lessons Promoted and writes the `SKL-` row on the operator's
  word (its steps 3 and 5). The two retirement columns and the lesson rules of the roster
  (`lessons-confirmed`, `lessons-note-budget`, `lessons-stranded`, `lessons-superseded-binding`)
  are drawn as frames, no arrow.
- **3 skills name no tool** (`ci-evidence`, `measurement-evidence`, `plain-english`) and their strip is the one sentence.
- **The fold per skill** reuses the gate fold (207). The matrix and the map stand open under two new
  sub-headings before the writing styles.
- **Three rounds on the matrix and one on the map.** The header pills ate their own width (a pill's
  round ends), so the headers are boxes and the columns 90 px wide by the rule's arithmetic; the
  skill names were first read from the file name instead of the folder; the first capture showed
  each group's first row under the frame's title, so every group frame now has a title band. The
  map's promote label overflowed its box and was shortened. The third move took two routing rounds:
  the right-hand channel was taken by the event and promote edges (five crossings and a label on an
  edge), so the two retirement edges run the lessons frame's left channel, the farther source on the
  outer track arriving lower (the 204 ranking), and the move's words sit as a line under the pills.
- **STOP is the bold ceremony form.** The skills' text holds 15 words `STOP` and 8 of them are the
  bold `**STOP` a ceremony stops at; the other 7 are prose about stops (`drift-register`,
  `operator-interview`, `orient-resume`, `package-onboarding`, `slice-review`, one each in
  `replan-deferred` and `ste-rewrite`). The first strips drew every word; the reader now takes the
  bold form only, and the caption says so.
- **The folder, measured:** 724 files (181 figure ids), 4.5 MB on disk (`du`, as the earlier ledgers
  measured) and 3.1 MB of bytes; the page 1,318,300 bytes,
  1,545 content ids. From the browser: the matrix 976 x 756, the map 900 x 518; at 390 px the page's
  scroll width is 375.
- **Captures** under `plans/evidence/captures-208/`: `skills-matrix` EN light, EN dark, AR light, 390 px;
  `skills-lifecycle` EN light, EN dark, AR light; `skill-slice-review` and `skill-ci-evidence` EN light.

## Rulings taken at the review (2026-10-05)

- Approved and committed as staged.
- **G26, a ceremony STOP is the bold form:** a strip marks `STOP` only where a skill's text writes
  `**STOP`; prose about stops is not a step. 8 of 15 words today.
- **G27, the citation matrix has discipline columns only:** the nine discipline skills; a citation
  of a scenario skill lives in the ledger's table, not in the figure.

## Validation

- `python docs/guide/build.py`: 1,545 ids, 0 strings missing, 0 orphans, the geometry lint and the
  label-width rule green on both copies of the 181 file models; 724 figure files. `test_user_guide`:
  `Ran 16 tests`, OK (the skills test new).
- `python check.py`: ALL CHECKS PASSED.
