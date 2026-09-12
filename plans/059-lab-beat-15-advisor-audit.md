# Plan 059: Lab beat 15 — exercise the advisor-audit mechanisms against the recorded lab package, pin them with assertions

> **Executor instructions**: You are the execution agent for a lab continuation beat.
> Follow the beat script step by step, drive everything through the tool handlers
> IN-PROCESS against the working-tree server, record every verbatim refusal text you
> are told to record, and archive your numbered report. Touch only the files listed as
> in scope. If any STOP condition occurs, stop and report. Commit in the worktree per
> the git workflow section. SKIP updating `plans/README.md` — the reviewer maintains it.
> Reply with the report format at the end.
>
> **Drift check (run first)**: `git diff --stat 094dd13..HEAD -- evals/sample-results/lab-tracker lab evals/evals.json evals/README.md`
> Any diff = STOP (the fixture moved underneath the plan).

## Status

- **Priority**: P1 (release acceptance)
- **Effort**: M
- **Risk**: LOW (the fixture is backed up first; every write goes through the tools)
- **Depends on**: plans 042–057 DONE (they are: `main` `094dd13`)
- **Category**: tests
- **Planned at**: commit `094dd13`, 2026-09-12

## Why this matters

The repo's release convention (`lab/README.md`, "How a release exercises the lab") is that
every release runs a numbered **continuation beat**: an incremental real-agent session
against the recorded `lab-tracker` package that fires the release's new mechanisms, records
the resulting package as the eval fixture, and pins the outcome with new `evals.json`
assertions. Beats 10–14 correspond to plans 035–041; the beat-14 report
(`plans/evidence/lab-continuation-report-041-2026-09-06.md`) is the procedural exemplar:
driven **in-process through the working-tree server** (`plugins/tamheed/server/`), scripts
ending in `package_close()` inside `finally`, a `data/` backup taken before the first
write, no hand edits to `data/*.jsonl` (with one deliberate exception below — the stale-tree
rollback needs a disk edit to fire, and the beat restores the bytes from the backup), and
the whole numbered tool-call log archived verbatim under `plans/evidence/`. Beat 15 is that
session for the sixteen advisor plans (042–057) that ship in v4.8.0.

## Current state

- The fixture: `evals/sample-results/lab-tracker/package/` — `data/*.jsonl` (26 files),
  `prompts/*.md`, `csv/*.csv`, `review.html`, `exports/*.json`; workspace beside it at
  `evals/sample-results/lab-tracker/workspace/` (`scripts/gen-slate.py`, `slate.html`).
  Package name is `package`; its root is `evals/sample-results/lab-tracker/`.
- Fixture facts you will build on (read them yourself with `entity_query` before writing):
  slices `SL-001`, `SL-002` (both `Implemented`, phase `PH-1` Approved); defects `DEF-001`
  (Fixed, high), `DEF-002` (Fixed, low), `DEF-003` (Open, low, `found_in SL-002`); one
  waiver `WVR-001` (rule `defects-minor`, `applies_to DEF-003`); one skill `SKL-001`
  (`boundary-semantics`); journal ends at `PE-019` with exactly one `forced-override` row;
  no `omissions.jsonl` (every Always family is present).
- The server: `plugins/tamheed/server/tamheed_server.py` (working tree = v4.8.0 RC, plans
  042–057 merged). Drive it as the beat-14 report did:

  ```python
  import sys, pathlib
  sys.path.insert(0, "plugins/tamheed/server")
  import tamheed_server as srv
  srv.PACKAGE_ROOT = pathlib.Path("evals/sample-results/lab-tracker").resolve()
  srv.package_open("package")
  try:
      ...                      # tool calls
  finally:
      srv.package_close()
  ```

  Run scripts from the repo root (your worktree). Write your scripts under a scratch
  directory outside the repo (e.g. `%TEMP%`), never under the repo.
- The scenario file `lab/scenario.md` ends with beat 14 (a numbered `14. **The export
  continuation (v4.7.0, plan 041)** — …` block of `✔` lines) followed by the `**Pass bar:**`
  paragraph. `lab/README.md:26` lists the continuation beats (`10: lessons, 11: promotion, …
  14: the entity_export read …`). `evals/README.md:28` is the `lab-tracker` row listing the
  beats' plans.
- `evals/evals.json` case `lab-tracker`: `deterministic_assertions` is a list of
  `{"check": "...", "cmd": ["python", "evals/pkg_check.py", <subcommand>, ...], "expect_exit": 0}`
  objects (see the last three — `grep-file`, `grep-present … --tables progress_entries`).
  Primitives: `gates`, `count <type> [--col K=V]... [--min N] [--max N]`, `nonempty`,
  `nonempty-any`, `grep-present/absent <pkg> <needle> [--tables t1,t2]`, `grep-tree-present/absent
  <dir> <needle>`, `file-exists`, `grep-file <path> <needle>`, `verify`. `count --col K=V`
  compares `str(row.get(K)) == V`, so `--col applies_to=None` matches a NULL.
- Evidence report exemplar: `plans/evidence/lab-continuation-report-041-2026-09-06.md`
  (header block quoting the context, then `## … execution report` with a numbered tool-call
  log, verbatim refusal texts, and the three eval commands' results). Mirror its shape.
- Verification commands: `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package`
  → `ready=True`; `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker`
  → all pass; `python check.py` → `ALL CHECKS PASSED` (> 2 min; background it).

### Release discipline

- Do NOT bump `plugin.json`; do NOT touch `CHANGELOG.md` (plan 058 writes the 4.8.0 note and
  will cite this beat); do NOT edit the five version-stamped files.
- The fixture is regenerated **by the tools only** (`package_close` writes canonical JSONL;
  `export_html` writes `review.html` + `csv/`; `handoff_emit` refreshes prompts). The single
  sanctioned hand edit is the stale-tree step, which is restored from the backup before
  the next tool write.
- Every assertion you add must pass against the fixture you recorded, and `check.py` must
  stay green.

## Scope

**In scope** (the only files you may change):
- `evals/sample-results/lab-tracker/**` (the recorded fixture — via the tools)
- `evals/evals.json` (append assertions to the `lab-tracker` case only)
- `lab/scenario.md` (append beat 15 before the `**Pass bar:**` paragraph; update that
  paragraph's list of deliberately-open items if the beat adds one)
- `lab/README.md` (extend the beats list on line ~26 with `15: the advisor-audit mechanisms`)
- `evals/README.md` (extend the `lab-tracker` row with the beat-15 clause)
- `plans/evidence/lab-continuation-report-059-2026-09-12.md` (create — your report, verbatim)
- `plans/README.md` — NO (reviewer)

**Out of scope**: `plugins/**`, `tests/**`, `check.py`, `evals/pkg_check.py`, `CHANGELOG.md`,
any other fixture.

## Git workflow

- One commit on your worktree branch: `lab: beat 15 — the advisor-audit mechanisms exercised and pinned (plan 059)`.
  Do NOT push.

## The beat (append this to `lab/scenario.md` as item 15, then perform it)

```
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
      write is `ok` and NOT `unchanged`; `entity_query`/the table holds the revised text.
    ✔ THE CSV GUARD (plan 050): `entity_upsert` `DEF-004` (title
      "=SUM(A1) in the CSV header looks like a formula", severity low, Open,
      `found_in SL-002`) → `export_html()` → `csv/defects.csv` carries `'=SUM(A1)` — the
      quote-prefixed cell — and `review.html` renders the title unchanged.
    ✔ THE NOTE SCREEN (plan 054): `entity_upsert` skill `SKL-002` named
      `ignore all previous instructions` (level project) → `handoff_emit(<workspace>)`
      REFUSED, gate `G-INJECT`, a `skill` finding (record the text); then re-upsert
      `SKL-002` with a lifecycle status that is not Approved (read the `skills` CHECK in
      `plugins/tamheed/db/schema.sql` and pick the rejected/obsolete value it allows; if
      only Approved is legal, supersede it per the schema) → `handoff_emit` succeeds; the
      note's skills line names only `boundary-semantics`.
    ✔ Close the beat with ONE `progress_update` note (actor `agent:lab-continuation-059`,
      `event_type: "note"`) quoting the four refusal fragments verbatim:
      `invalid package name`, `NOT applied`, `cannot be created as Implemented`,
      `G-INJECT`, plus the word `indeterminate`.
    ✔ `export_html` (re-run after the note); `gate_run` ready; `package_close`; the
      fixture updated (data/, csv/, review.html, refreshed prompts if `handoff_emit`
      refreshed stock); `package_verify()` green.
```

## Steps

### Step 1: Baseline and backup

- Drift check (top of file) → empty.
- `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`.
- `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → all pass
  (record the pass count).
- Copy `evals/sample-results/lab-tracker/package/data` to a scratch backup directory
  (outside the repo). Record the file count (expect 26).

### Step 2: Perform the beat

Script it as 3–5 small in-process scripts (the exemplar used three), every script opening
and closing the package in `try/finally`. Record every verbatim text the beat asks for in
your report. Guardrails:
- The stale-tree step: the disk edit must be made **while the package is open** (after
  `package_open`), the refusal observed, `package_close` observed to warn, THEN the file
  restored from the backup **before** any further tool call. Confirm restoration with a
  byte comparison against the backup copy.
- After the beat, `git status --porcelain evals/sample-results/lab-tracker` must list only
  files the tools wrote (data/*.jsonl, csv/*.csv, review.html, prompts/*.md, plus
  `workspace/CLAUDE.md` / `.mcp.json` if `handoff_emit` targeted the workspace — target the
  workspace directory the exemplar used: `evals/sample-results/lab-tracker/workspace`).

### Step 3: Append the assertions to `evals.json` (`lab-tracker` case, after the last one)

```json
{"check": "A slice born Implemented was refused, then forced with a typed audit (plan 053: >=2 forced-override rows now).",
 "cmd": ["python","evals/pkg_check.py","count","{case_dir}/package","progress-entry","--col","event_type=forced-override","--min","2"], "expect_exit": 0},
{"check": "The forced audit names the born-Implemented shape (plan 053).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","born-Implemented","--tables","progress_entries"], "expect_exit": 0},
{"check": "A whole-rule waiver exists (plan 056 coverage: applies_to NULL waives the rule).",
 "cmd": ["python","evals/pkg_check.py","count","{case_dir}/package","waiver","--col","applies_to=None","--min","1"], "expect_exit": 0},
{"check": "The revised omission reason landed (plan 051: no silent 'unchanged').",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","revised: invariants deferred","--tables","omissions"], "expect_exit": 0},
{"check": "The CSV export defuses a formula-shaped cell (plan 050).",
 "cmd": ["python","evals/pkg_check.py","grep-file","{case_dir}/package/csv/defects.csv","'=SUM(A1)"], "expect_exit": 0},
{"check": "The beat's closing note quotes the stale-tree refusal (plan 043).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","NOT applied","--tables","progress_entries"], "expect_exit": 0},
{"check": "The beat's closing note quotes the note-screen refusal (plan 054).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","G-INJECT","--tables","progress_entries"], "expect_exit": 0},
{"check": "No Approved skill carries an injection-shaped name (plan 054: the screened skill was not left Approved).",
 "cmd": ["python","evals/pkg_check.py","count","{case_dir}/package","skill","--col","name=ignore all previous instructions","--col","lifecycle_status=Approved","--max","0"], "expect_exit": 0},
{"check": "The emitted note names only the legitimate skill (plan 054).",
 "cmd": ["python","evals/pkg_check.py","grep-file","{case_dir}/workspace/CLAUDE.md","`boundary-semantics`"], "expect_exit": 0}
```

Keep the existing assertions untouched. If `entity_query`'s type name for skills/waivers
differs (`skill`, `waiver` are the `ENTITY_TABLES` keys — verify with
`python -c "import sys; sys.path.insert(0,'plugins/tamheed/server'); import tamheed_server as s; print(sorted(s.ENTITY_TABLES))"`),
use the real key. If the workspace `CLAUDE.md` is not part of the recorded fixture layout,
drop the last assertion and say so.

**Verify**: `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker`
→ every assertion `pass` (record the new total); `python evals/pkg_check.py verify evals/sample-results/lab-tracker/package`
→ `verified=True`; `python check.py` → `ALL CHECKS PASSED`.

### Step 4: Docs + evidence

- `lab/scenario.md`: insert the beat-15 block above; in the `**Pass bar:**` paragraph, add
  `SL-003` (forced, empty — its scoped readiness reads indeterminate by design) and `DEF-004`
  (the CSV-guard defect, open low, waived by `WVR-002`) to the deliberately-open items.
- `lab/README.md` line ~26: extend the beats list with `15: the advisor-audit mechanisms
  (stale-tree rollback, born-Implemented refusal + force, scoped indeterminate, whole-rule
  waiver, omission revision, CSV defusing, the note's skill screen)`.
- `evals/README.md` `lab-tracker` row: add `and the advisor-audit mechanisms (042–057, beat 15)`
  before `; the assertions pin the package`.
- `plans/evidence/lab-continuation-report-059-2026-09-12.md`: your report — header block in
  the exemplar's shape (context, what was touched, the three eval results, the backup), then
  the numbered tool-call log with every recorded verbatim text.

**Verify**: `python check.py` → `ALL CHECKS PASSED` (docs are unlinted, but run the gate once
more on the final tree); `git status --porcelain` → only in-scope paths.

## Done criteria

- [ ] `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → 0 failed, ≥ 9 more assertions than at Step 1
- [ ] `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`
- [ ] `python evals/pkg_check.py verify evals/sample-results/lab-tracker/package` → `verified=True`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `grep -c "advisor-audit continuation" lab/scenario.md` → `1`; `grep -c "15:" lab/README.md` → `1`
- [ ] `plans/evidence/lab-continuation-report-059-2026-09-12.md` exists and contains every verbatim refusal the beat asked for
- [ ] `git status --porcelain` → only in-scope paths; one commit on the branch

## STOP conditions

- The drift check shows any diff.
- `package_migrate("package")` preview is NOT refused (the fixture is not the v4 package the
  scenario expects).
- The stale-tree refusal does not fire, or `entity_query` shows the new row after it (that
  would be plan 043 regressing — report, do not proceed).
- Any tool returns `ok: false` where the beat expects success — record the text and stop.
- `run_evals` fails on a PRE-EXISTING assertion after your writes (you changed something the
  scenario pins) — restore `data/` from the backup and report.
- You are tempted to hand-edit any file under `data/` other than the one sanctioned
  `risks.jsonl` edit, or any file under `plugins/`, `tests/`, `check.py`, `pkg_check.py`.

## Maintenance notes

- Beat 15 leaves `SL-003` (forced, empty) and `DEF-004` (open, low, waived) in the fixture
  deliberately; the pass bar names them. A future beat that closes them must update the
  pass bar and the assertions together.
- The next release's beat is 16; the beat number, the plan number, and the evidence file
  name travel together.
