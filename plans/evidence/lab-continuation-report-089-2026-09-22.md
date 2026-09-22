# Lab continuation report — beat 18, v4.11.0 RC (plan 089, 2026-09-22)

> The execution agent's report from `lab/scenario.md` beat 18 (the findings_27 continuation: the
> registry synced for a new family, the missing function recorded as feedback instead of scripted,
> confirmed and exported and reported on the operator's word, the refused unattended confirmation
> and the refused rewrite under the operator's own name, the local tool that exists only on that
> word, the by-hand lesson retirement the engine journals and the forged engine row refused on
> both caller paths, and the formula's variable names that trip no list), archived **verbatim**
> below the header. Context: an INCREMENTAL real-agent session (`actor: agent:lab-beat-18`)
> against the recorded `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plans-085–088 tree at `main` `f142dc5`), nine scripts run from
> the repo root, each opening and closing the package, `data/.lock` absent before the first and
> after the last. Files touched = the fixture (`data/` — `defects.jsonl`, `entity_types.jsonl`,
> `lessons.jsonl`, `progress_entries.jsonl`, new `feedback.jsonl`; `csv/` — the three matching
> exports plus the new `feedback.csv`; `exports/feedback.json` (new, written by `entity_export`);
> `prompts/` — `README.md` and `orient-resume.md` refreshed to current stock by tool;
> `review.html`) + `evals/evals.json` (nine appended assertions on the `lab-tracker` case only)
> + `lab/scenario.md`, `lab/README.md` + this report. No file under `plugins/`, `tests/`,
> `check.py`, `evals/pkg_check.py`, `CHANGELOG.md`, `plans/README.md`, any version stamp or any
> other fixture was edited. **Zero** hand edits of a `data/`, `csv/`, `exports/` or `prompts/`
> file were made; the fixture changed only through the tools. All three verification commands
> green (`pkg_check gates` `ready=True`, `run_evals` lab-tracker **65/65** — 56 before the beat,
> +9 — `check.py` `ALL CHECKS PASSED`). A full `package/` backup was taken to
> `<scratch>/b18/backup` before the first open; nothing was restored from it, and it is the tree
> every new assertion was proved to FAIL against.
>
> **Deviations from the plan's steps.** Two.
>
> **D-1 — the registry sync, an unscripted prerequisite step (between steps 2 and 3).** The
> plan's step 3 assumes an `FB-` row can be written to the recorded package. It cannot: the
> fixture's `data/entity_types.jsonl` was serialized before migration 005 existed and holds 35
> type rows, none of them `feedback`. The `trg_feedback_ai` insert trigger writes
> `entity_index(id, entity_type)`, and `entity_index.entity_type REFERENCES
> entity_types(type_id)`, so the first `FB-001` upsert was refused with a bare
> `FOREIGN KEY constraint failed`. Plan 087's own record (lines 48–49) names the designed
> remedy — "`package_migrate` reports `registry-sync` for the one new registry row (pure append,
> no backup)" — so `package_migrate("package")` was run as a preview and then with
> `confirm=True` before step 3 was retried unchanged. This is not a new practice in the lab: the
> journal already held `PE-009` `REGISTRY-SYNC: entity types added (lesson)` and `PE-011`
> `REGISTRY-SYNC: entity types added (skill)`, both by actor `system:migrate`, from beats 10 and
> 12. The `confirm=True` was taken under the dispatching reviewer's grant that the plan supplies
> the operator's word for this beat; the tool's own precondition ("back the package up (git
> commit or copy `data/`)") was satisfied twice over — the step 1 backup and the clean `f142dc5`
> HEAD. It added exactly one journal row, `PE-028`, and one registry row.
>
> **D-2 — one adapted assertion needle (step 7, assertion 6).** The plan's needle for the
> by-hand lesson retirement, `by hand`, is **hollow**: it already matches the Step 1 backup at
> `progress_entries.jsonl:23`, inside beat 16's own closing note ("that lock was removed by hand,
> as the tool says is the deliberate path"). The needle was narrowed to the engine's exact
> phrasing, `on the operator's word, by hand`, which is absent from the backup and present in
> both `PE-032` (the engine's row) and `PE-033` (the beat's note). Every other needle the plan
> gives was used verbatim.
>
> One further note for the maintainer, recorded but not acted on: the `FOREIGN KEY constraint
> failed` above came back **unnamed**. `entity_upsert`'s exception handler has an
> `elif "FOREIGN KEY constraint failed" in msg` branch written expressly to name the offending
> reference (plan 036, findings_19 §3), and it did not name this one — the failing reference is
> on the trigger's side, not on a column of the row being written. A legibility gap, not a
> correctness one. It was deliberately NOT recorded as an `FB-` row: step 3.7's export envelope
> must read `total: 1`, and the plan scripts `FB-001` and `FB-002` only.

## Tamheed v4.11.0 lab continuation — beat 18 — execution report

### Numbered tool-call log (in-process handler calls + verbatim outcomes)

**Drift check.** `git log --oneline -1` → `f142dc5 docs(plans): plan 089 - lab beat 18, the
findings_27 mechanisms and the feedback channel (dispatch record)`.
`python plugins/tamheed/server/tamheed_server.py --selftest` → `mcp sdk: ok (1.27.2) — 19/19
tools registered`.

**1. Step 1 — baseline and backup.** `package/` copied to `<scratch>/b18/backup` before any
open (no `data/.lock` in the copy; 27 `data/*.jsonl` files).

`server_info()`:

```json
{"ok": true, "version": "4.10.0", "open_package": null,
 "migrations_head": "005_feedback.sql", "schema_version": 5}
```

`gate_run()` → `ready: true`; all eight gates `pass` (`G-IDS`, `G-DEC-STATUS`, `G-REQ-SRC`,
`G-TRACE`, `G-SET`, `G-PROGRESS`, `G-COMPLETE`, `G-REL`).

Family totals: `progress-entry` **27**, `defect` **5**, `lesson` **4**, `feedback` **0**.

`package_verify()`:

```json
{"ok": true, "package": "package", "files": 27, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "0048451e12d0dc2e27c7f9289306dabb28d80c668bfb4f736ade5cab89968f2f",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": null}
```

`git status --short` after the idle open → close: **empty**. The zero-diff invariant holds.

A projection audit was run in the same script, because step 2 and step 3 both depend on
"re-send every column you got back" actually being every column: `entity_query("defect",
id="DEF-005")` with no `columns` argument returned all eight table columns and reported no
`omitted_columns`; the same held for `feedback` later (16 of 16 columns, `missing_from_read:
[]`). A read that DOES project reports what it withheld — `entity_query("feedback",
id="FB-001", columns=["id","lifecycle_status"])` carried `omitted_columns` naming the other
fourteen.

**2. Step 2 — the underscore (plan 085).** `DEF-005` re-sent as a full row with the new title
``export header drifts (see DEF-001; mock id `RISK-808`; score = (KPI-17_score * 0.25) +
(KPI-10_score * 0.2))``:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005",
            "changed_columns": [{"column": "title", "old_len": 54, "new_len": 108}]}]}
```

`changed_columns` names `title` and nothing else. `readiness_check("package")`, rule
`prose-ids-resolve`:

```json
{"rule": "prose-ids-resolve", "severity": "advisory", "status": "pass",
 "entities": [],
 "note": "identifiers written in prose that resolve to NO entity (G-IDS checks foreign keys and the index, never a sentence): correct the id, or record the missing row; an immutable row is repaired by supersession. THE ENTITY LIST IS A FLOOR, not a census: hits inside code spans are listed under `in_code_spans` and tokens too narrow to be this family's ids under `not_well_formed` - both informational, neither fails the rule, so backticks hide nothing. The three lists are disjoint and width is tested first, so a narrow token inside a code span appears only under `not_well_formed`. The append-only journal and Superseded/Obsolete rows are not scanned",
 "in_code_spans": ["DEF-005.title -> RISK-808"],
 "not_well_formed": []}
```

`entities` is empty, `in_code_spans` is still exactly `["DEF-005.title -> RISK-808"]`, and
`not_well_formed` is empty — **`KPI-17_score` and `KPI-10_score` appear in no list**, because
`_` is a word character and the note states the order: *"The three lists are disjoint and
width is tested first"*.

The one `indeterminate` rule whose note carries `scoped: false`:

```json
{"rule": "hypotheses-measurable", "severity": "advisory", "status": "indeterminate",
 "entities": [],
 "note": "hypotheses past Draft without a metric + threshold — the number is decided BEFORE the experiment runs (anti-confirmation-bias) — no hypotheses rows at all: this rule measured nothing (a package with nothing to report and one that recorded nothing look the same here). Record the rows, or record the family's omission if it is deliberately empty. (scoped: false - the whole table is empty; a scoped zero reads indeterminate by plan 049 and carries scoped: true)",
 "population": {"table": "hypotheses", "rows": 0, "scoped": false},
 "discriminating": false}
```

`gate_run()` → `ready: true`.

**3. D-1 — the registry sync (unscripted; see the header).** First attempt at `FB-001`, before
the sync:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "FB-001",
            "error": "FOREIGN KEY constraint failed"}]}
```

`package_migrate("package")` (preview):

```json
{"ok": true, "stage": "preview", "package": "package",
 "report": {"mode": "registry-sync", "version_from": "4.0.0",
            "note": "registry rows + the audit journal row appended; no data transform, no backup taken",
            "entity_types_added": ["feedback"]},
 "note": "nothing written — back the package up (git commit or copy data/), then re-run with confirm=true"}
```

`package_migrate("package", confirm=True)`:

```json
{"ok": true, "stage": "migrated", "package": "package",
 "report": {"mode": "registry-sync", "version_from": "4.0.0",
            "note": "registry rows + the audit journal row appended; no data transform, no backup taken",
            "entity_types_added": ["feedback"]},
 "backup": "none (registry-sync is a pure append)",
 "note": "review the report, commit the diff, then package_open"}
```

The journal row it appended, beside its two predecessors from beats 10 and 12
(`entity_query("progress-entry", search="REGISTRY-SYNC")` → `total: 5`):

```json
{"id": "PE-028", "event_type": "note",
 "entry": "REGISTRY-SYNC: entity types added (feedback)",
 "subject_id": null, "actor": "system:migrate", "occurred_at": null}
```

`gate_run()` → `ready: true`. `package_verify()` → `verified: true`, `files: 27`,
`review_current: **false**` (the digest moved to
`1e35dea3e1cf2397b75b7e45840a1b6e870afc49da8c2d0176283f2035f1ad55`; step 6's `export_html`
restamps it). `git status --short` showed exactly three modified tables — `defects.jsonl`
(step 2's), `entity_types.jsonl` and `progress_entries.jsonl` — and no other `data/` file,
although the migration rewrites every table through the canonicalizer.

**4. Step 3.1 — `FB-001` born `Proposed`, free.** Re-run unchanged after the sync:

```json
{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "FB-001"}]}
```

Stored row (`plugin_version` is the value `server_info()` reports on this tree, `4.10.0` — no
`plugin.json` bump is in scope for this beat):

```json
{"id": "FB-001", "kind": "missing-capability",
 "title": "a patch mode for one column of a long row",
 "detail": "Step 2 of this beat had to change ONE column of DEF-005 - the title, to carry the formula's variable names - and entity_upsert takes FULL rows only, so the change was a read-every-column-then-paste-it-back substitution across a long field rather than a patch. A patch mode (id + the one column + the stored row's digest, or expect_unchanged over the rest implied) would make that one write. Without it the safe way to do a substitution across a long field is a local script that reads data/defects.jsonl, and that is exactly the side tool this family exists to catch. The same title quotes the phantom RISK-808, so this row names two ids that no prose scan may flag.",
 "workaround": "none - recorded here instead of a script",
 "tool_path": null, "tool_or_rule": "entity_upsert", "plugin_version": "4.10.0",
 "lifecycle_status": "Proposed", "confirmed_by": null, "confirmed_at": null,
 "resolved_in": null, "upstream_ref": null, "recorded_at": "2026-09-22"}
```

No `operator_confirm` was needed, and none was given: a draft binds nothing.

**5. Step 3.2 — the UNATTENDED confirmation, REFUSED.** Same full row, `lifecycle_status`
`Confirmed`, no `operator_confirm`:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "FB-001",
            "error": "FB-001: feedback leaves the package only on the OPERATOR's word — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
```

Stored `lifecycle_status` after the refusal: `Proposed`. Nothing moved.

**6. Step 3.3 — `handoff_emit` names the waiting row.** Emitted to `<scratch>/b18/handoff-a`
(never committed — an emitted target carries machine-specific absolute paths). `warnings`:

```json
["2 stock prompt(s) are STALE-STOCK — byte-equal to an older release's stock, never customised: re-run with refresh_stock=true to update them safely (customised files are never touched by refresh)",
 "1 feedback row(s) await the operator's word (FB-001) — interview them: Confirmed with operator_confirm, or Rejected"]
```

**7. Step 3.4 — the operator's word (given by plan 089).** `lifecycle_status: "Confirmed"`,
`operator_confirm: true`, `confirmed_by: "operator:lab"`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "FB-001",
            "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 9},
                                {"column": "confirmed_by", "old_len": 0, "new_len": 12}],
            "feedback_audit": "PE-029"}]}
```

The engine's own witness row (`entity_query("progress-entry", search="FB-001 -> Confirmed")`):

```json
{"id": "PE-029", "event_type": "transition",
 "entry": "FEEDBACK FB-001 -> Confirmed (was Proposed; kind missing-capability) on the operator's word — operator_confirm attested; confirmed_by operator:lab",
 "subject_id": "FB-001", "actor": "system:feedback-guard",
 "occurred_at": "2026-09-22T04:30:28Z"}
```

**8. Step 3.5 — the rewrite under the operator's name, REFUSED.** Same row, still `Confirmed`,
`detail` with one sentence appended, no `operator_confirm`:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "FB-001",
            "error": "FB-001: the operator confirmed this row as it stood — content drifted on ['detail']; re-confirm the change with \"operator_confirm\": true, or record a new FB- row"}]}
```

The stored `detail` is unchanged — re-read, it does **not** contain the attempted sentence
(`"contains_the_attempted_sentence": false`).

**9. Step 3.6 — `handoff_emit` asks for the export.** Emitted to `<scratch>/b18/handoff-b`.
`warnings`:

```json
["2 stock prompt(s) are STALE-STOCK — byte-equal to an older release's stock, never customised: re-run with refresh_stock=true to update them safely (customised files are never touched by refresh)",
 "1 confirmed feedback row(s) not yet reported upstream (FB-001) — entity_export(\"feedback.json\", args={\"type\": \"feedback\"}) and put the file in your findings; set each row Reported once it has left"]
```

**10. Step 3.7 — the row leaves.** `entity_export("feedback.json", args={"type": "feedback"})`:

```json
{"ok": true,
 "path": "<repo>\\evals\\sample-results\\lab-tracker\\package\\exports\\feedback.json",
 "bytes": 1597, "tool": "entity_query",
 "digest": "09e68d41e5756943f649baf76e6ad9f632aefb0e5a4fde2934002770f4a75d56",
 "memory_matches_disk": true, "count": 1, "total": 1, "partial": false}
```

The written file's envelope (`exports/feedback.json`, top-level keys `tamheed_export`,
`result`):

```json
{"version": "4.10.0", "package": "package", "tool": "entity_query",
 "args": {"type": "feedback"},
 "digest": "09e68d41e5756943f649baf76e6ad9f632aefb0e5a4fde2934002770f4a75d56",
 "memory_matches_disk": true, "count": 1, "total": 1, "partial": false}
```

`FB-001` then set `Reported` — a full row, **no** `operator_confirm`, accepted, because
`lifecycle_status` is not one of the content columns the operator vetted and both states are
inside the bound set:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "FB-001",
            "changed_columns": [{"column": "lifecycle_status", "old_len": 9, "new_len": 8}]}]}
```

**11. Step 3.8 — the local tool.** `FB-002`, `kind: "local-tool"`, `title: "lab gate runner"`,
`tool_path: "evals/pkg_check.py"`, `detail: "reads the package through pkg_check's tool-backed
checks; writes nothing"`, **no** `operator_confirm`:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "FB-002",
            "error": "FB-002: a local tool over the package exists only on the OPERATOR's word — interview them with what it reads (exports/ only) and writes (nowhere tool-owned), then re-run this item with \"operator_confirm\": true; never in unattended mode"}]}
```

`entity_query("feedback")` total after the refusal: **1**. The insert did not happen.

With `operator_confirm: true, confirmed_by: "operator:lab"`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "FB-002", "feedback_audit": "PE-030"}]}
```

The row landed `Confirmed` without being asked to — the guard promotes a `local-tool` row that
arrives on the word (`confirmed_at` `2026-09-22`, set by the server). Its witness row:

```json
{"id": "PE-030", "event_type": "transition",
 "entry": "FEEDBACK FB-002 -> Confirmed (was new; kind local-tool) on the operator's word — operator_confirm attested; confirmed_by operator:lab",
 "subject_id": "FB-002", "actor": "system:feedback-guard",
 "occurred_at": "2026-09-22T04:31:31Z"}
```

**12. Step 3.9 — the family is exempt from the prose scan.** `FB-001`'s `detail` names a real
id (`DEF-005`) and a phantom one (`RISK-808`), and `readiness_check("package")` reports
`prose-ids-resolve` byte-identically to step 2 — `status: "pass"`, `entities: []`,
`in_code_spans: ["DEF-005.title -> RISK-808"]` (the defect's title, not the feedback row),
`not_well_formed: []`. Neither id from the `feedback` row appears anywhere.

**13. Step 4.1 — `LL-005`, recorded then approved.** Born `Proposed` (`kind: improve`,
`statement` 395 chars). Approved on the operator's word, full row, `confirmed_by:
"operator:lab"`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "LL-005",
            "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 8},
                                {"column": "confirmed_by", "old_len": 0, "new_len": 12}],
            "next": "this lesson BINDS only once the always-loaded note is rebuilt - run handoff_emit in this same batch (the note is rebuilt by nothing else)",
            "lesson_audit": "PE-031"}]}
```

**14. Step 4.2 — retired BY HAND, and the engine writes the row.** Full row,
`lifecycle_status: "Superseded"`, `superseded_by` left `null` (a lesson withdrawn, not
replaced), `operator_confirm: true`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "LL-005",
            "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 10}],
            "lesson_audit": "PE-032"}]}
```

`entity_query("progress-entry", search="LL-005 -> Superseded")`:

```json
{"id": "PE-032", "event_type": "transition",
 "entry": "LESSON LL-005 -> Superseded (was Approved) on the operator's word, by hand — operator_confirm attested; confirmed_by operator:lab",
 "subject_id": "LL-005", "actor": "system:lesson-guard",
 "occurred_at": "2026-09-22T04:33:15Z"}
```

The actor is `system:lesson-guard`, not the automatic path's `system:lesson-supersession` — the
two routes to `Superseded` stay distinguishable in the journal. The entry contains both
`by hand` and `confirmed_by operator:lab`.

**15. Step 4.3 — the forged engine row, REFUSED on BOTH caller paths.**
`progress_update([{"event_type": "transition", "actor": "system:lesson-guard", "subject_id":
"LL-005", "entry": "forged"}])`:

```json
{"ok": false,
 "error": "entries[0]: actor 'system:lesson-guard' is the engine's own namespace (system:<component> rows are what the server witnessed) — a caller records as human:<name> or agent:<session>. Batch NOT applied."}
```

The same row through `entity_upsert` as a `progress-entry` carrying an id (`PE-099`):

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "PE-099",
            "error": "actor 'system:lesson-guard' is the engine's own namespace (system:<component> rows are what the server witnessed) — a caller records as human:<name> or agent:<session>"}]}
```

Journal total after both attempts: **32**; rows matching `forged`: **0**. Neither forgery was
accepted — **no security regression**. `gate_run()` → `ready: true`.

**16. Step 5 — the prompts.** `handoff_emit("<scratch>/b18/handoff-c", refresh_stock=True)`,
`prompt_library`:

```json
{"emitted": [], "unchanged": ["prompts/defect-triage.md", "prompts/drift-register.md",
 "prompts/generate-report.md", "prompts/integrity-check.md", "prompts/loop-guard.md",
 "prompts/loop-iteration.md", "prompts/package-onboarding.md", "prompts/phase-close.md",
 "prompts/progress-sync.md", "prompts/register-liveness.md", "prompts/release-close-out.md",
 "prompts/replan-deferred.md", "prompts/skill-promote.md", "prompts/slice-kickoff.md",
 "prompts/slice-review.md"],
 "diverged": [], "diverged_stale_stock": [], "diverged_customized": [],
 "refreshed": ["prompts/orient-resume.md", "prompts/README.md"]}
```

`refreshed` is **exactly** the two the plan predicted; `diverged_customized` is **empty** —
nothing customised was touched. Before the refresh, the same field pair had reported
`diverged_stale_stock: [{"file": "prompts/orient-resume.md", "matches": "4.9.0"}, {"file":
"prompts/README.md", "matches": "4.10.0"}]`. The `warnings` on this emission:

```json
["2 stale-stock prompt(s) refreshed to the current template (refresh_stock)",
 "1 confirmed feedback row(s) not yet reported upstream (FB-002) — entity_export(\"feedback.json\", args={\"type\": \"feedback\"}) and put the file in your findings; set each row Reported once it has left"]
```

— the warning now names `FB-002` and no longer `FB-001`, which has left. The refreshed
`prompts/README.md` (11391 bytes) contains `feedback`, `FB-` and `local-tool`, and still
contains `tamheed:stock-merged` (beat 17's assertion is untouched). Its two new lines:

```
> the tools lack is a `feedback` row (`FB-`) first, never a script** (v4.11): what you
> project's findings. A script the project keeps over the package is a `local-tool` row
```

**17. Step 6 — close the beat.** ONE `progress_update` (`event_type: "note"`, actor
`agent:lab-beat-18`, 3454 chars) → `{"ok": true, "ids": ["PE-033"]}`. It quotes verbatim all
six required strings — the `leaves the package only on the OPERATOR's word` clause, the
`content drifted on ['detail']` clause, the `a local tool over the package exists only on the
OPERATOR's word` clause, the `engine's own namespace` clause, the words `feedback_audit` and
`lesson_audit`, and `width is tested first` (checked mechanically before the write).

`export_html()` → `review.html`, 141812 bytes; `csv.emitted` = `csv/defects.csv`,
`csv/feedback.csv`, `csv/lessons.csv`, `csv/progress_entries.csv`; `csv.diverged`,
`csv.removed`, `csv.unowned` all empty.

`gate_run()` → `ready: true`, all eight gates `pass`.

`package_verify()` after `package_close()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "cc521ea4fe08607964b98eeb753d56c1d80acc2cc7f00756f7711efd5d28cfca",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": null}
```

`data/.lock` exists: **False**.

### Mechanism → observed

| Plan | Mechanism | Verdict |
|---|---|---|
| 085 | `_` is a word character: a formula's `KPI-17_score` / `KPI-10_score` live in `DEF-005`'s prose and appear in NO `prose-ids-resolve` list (`entities` [], `in_code_spans` unchanged, `not_well_formed` []) | **observed** (step 2) |
| 085 | The classification order is stated in the rule's own note — `The three lists are disjoint and width is tested first` — and a whole-table zero carries `scoped: false` in its note plus `population.scoped: false` (`hypotheses-measurable`) | **observed** (step 2) |
| 086 | A by-hand exit from a binding lesson status is journaled by the ENGINE: `lesson_audit: PE-032`, `transition`, actor `system:lesson-guard`, entry carrying `by hand` and `confirmed_by operator:lab` | **observed** (step 4.2) |
| 086 | A `system:` actor is refused to a caller on the `progress_update` path (`Batch NOT applied.`) | **observed** (step 4.3a) |
| 086 | A `system:` actor is refused to a caller on the `progress-entry` `entity_upsert` path, in the same words | **observed** (step 4.3b) |
| 087 | `FB-` exists (migration 005) and a row is born `Proposed` freely — no operator word, binds nothing | **observed** (step 3.1) |
| 087 | Entering the bound set needs `operator_confirm` **and** `confirmed_by`, and is journaled by `system:feedback-guard` (`feedback_audit: PE-029`); the unattended attempt is refused and changes nothing | **observed** (steps 3.2, 3.4) |
| 087 | A `local-tool` row exists only on the operator's word — refused at INSERT, family total unmoved, then landed `Confirmed` with `feedback_audit: PE-030` | **observed** (step 3.8) |
| 087 | The CONTENT of a bound row changes only with the word: `content drifted on ['detail']`, stored `detail` unmoved | **observed** (step 3.5) |
| 087 | A **withdrawal** from the bound set is journaled too (the way OUT) | **not observed** — the beat never withdraws one. Plan 089 scripts `FB-001` `Proposed → Confirmed → Reported`, and `Confirmed` and `Reported` are both inside `_FEEDBACK_BOUND`, so the leaving branch never fires. Firing it would mean taking a confirmed row back to `Proposed`/`Rejected`, which no step asks for and which would cost the `lifecycle_status=Reported` assertion. A grep of `tests/` found no unit-tier case for it either, so this branch is unexercised by this beat and, as far as this report can tell, by the suites. |
| 087 | `handoff_emit` names the family until it has left — the `await` warning while `FB-001` is `Proposed`, the `entity_export` warning once it is `Confirmed`, and neither once it is `Reported` (the third emission names `FB-002` instead) | **observed** (steps 3.3, 3.6, 5) |
| 087 | The two stock prompts changed at 4.11.0 and refresh cleanly: `refreshed` exactly `prompts/orient-resume.md` + `prompts/README.md`, `diverged_customized` empty | **observed** (step 5) |

### Findings

**F-1 (D-1, methodology — for the plan template, not a defect).** A beat that fires a NEW
entity family against the recorded fixture must run `package_migrate`'s `registry-sync` first;
the plan should say so, as beats 10 and 12 evidently learned the same thing. The engine's
refusal at that point is a bare `FOREIGN KEY constraint failed`, which does not point at the
registry.

**F-2 (legibility, LOW).** That refusal should have been named. `entity_upsert`'s handler has a
branch for exactly this (`elif "FOREIGN KEY constraint failed" in msg`, plan 036 / findings_19
§3) and it produced no annotation, because the failing reference belongs to the
`trg_feedback_ai` trigger's `entity_index` insert rather than to a column of the row being
written. Not recorded as an `FB-` row (see the header).

**F-3 (legibility, LOW).** `FB-001` carries `confirmed_at: null` although it was confirmed on
the operator's word, while `FB-002` carries `2026-09-22`. The guard stamps it with
`cols.setdefault("confirmed_at", _now()[:10])`, and `setdefault` is a no-op when the key is
PRESENT-but-null — which is exactly what a re-read full row carries, and a full-row re-send is
the documented way to update. So the date lands on a fresh insert and silently does not land
on the confirmation of an existing draft, i.e. on the ordinary path. `confirmed_by` is
separately required and did land, so the attribution is never lost; only the date is. The same
shape appears on `LL-005` (`confirmed_by: "operator:lab"`, `confirmed_at: null`).

**F-4 (the plan's own assertion, fixed in place — D-2).** The needle `by hand` is hollow
against the pre-beat fixture: beat 16's closing note already contains "removed by hand".
Narrowed to `on the operator's word, by hand`.

**Not exercised, by design.** Plan 085's *cut clause on every list* did not fire: no
`prose-ids-resolve` list was long enough to be truncated in this fixture, so the clause that
announces a cut never appears. Nothing in the beat could force it without inventing dozens of
phantom ids, which would defeat step 2's point.

### Verification commands

```
$ python evals/pkg_check.py gates evals/sample-results/lab-tracker/package
ready=True
G-IDS=pass
G-DEC-STATUS=pass
G-REQ-SRC=pass
G-TRACE=pass
G-SET=pass
G-PROGRESS=pass
G-COMPLETE=pass
G-REL=pass
audit_evidence=evidenced:3/narrated:0/ungraded:1

$ python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker
... (the nine new checks, all `pass`)
PASS  lab-tracker
1 case(s) checked, 0 failed, 0 skipped

$ python check.py                       # backgrounded; the tree was not touched while it ran
... (the nine new lab-tracker checks again, all `pass`)
PASS  lab-tracker

3 case(s) checked, 0 failed, 6 skipped

ALL CHECKS PASSED
[exited with code 0]
```

`run_evals` reports the `lab-tracker` case at **65** deterministic assertions (56 before the
beat, +9).

### No hollow assertion: the nine new checks, backup vs fixture

Every `cmd` was run twice — once with `{case_dir}/package` replaced by the Step 1 BACKUP
(`<scratch>/b18/backup`), once against the fixture.

| # | Check | Backup exit | Backup output | Fixture exit |
|---|---|---|---|---|
| 1 | A missing function was recorded as feedback, confirmed on the operator's word, and reported (plan 087). | **1** | `below required minimum 1` | 0 (`count=1`) |
| 2 | The lab's local tool exists as a confirmed local-tool row (plan 087). | **1** | `below required minimum 1` | 0 (`count=1`) |
| 3 | The operator's confirmation of feedback is an engine-witnessed journal row (plan 087). | **1** | `below required minimum 2` | 0 (`count=2`) |
| 4 | An unattended confirmation was refused, and the note quotes it (plan 087). | **1** | `"leaves the package only on the OPERATOR's word" not found` | 0 (`progress_entries.jsonl:33`) |
| 5 | A confirmed row could not be rewritten under the operator's name (plan 087). | **1** | `"content drifted on ['detail']" not found` | 0 (`progress_entries.jsonl:33`) |
| 6 | The by-hand lesson retirement was journaled by the engine (plan 086). *(needle narrowed — D-2)* | **1** | `"on the operator's word, by hand" not found` | 0 (`progress_entries.jsonl:32, :33`) |
| 7 | A forged engine row was refused, and the note quotes the refusal (plan 086). | **1** | `"engine's own namespace" not found` | 0 (`progress_entries.jsonl:33`) |
| 8 | A formula's variable names live in the defect's prose and trip no list (plan 085). | **1** | `'KPI-17_score' not found` | 0 (`defects.jsonl:5`) |
| 9 | The fixture's prompt guide carries the 4.11.0 stock body (plan 087). | **1** | `'local-tool' NOT found in .../backup/prompts/README.md` | 0 |

Nine of nine fail on the backup and pass on the fixture. Note on checks 1–3: the backup has no
`data/feedback.jsonl`, but the `count` primitive still opens it cleanly and reads an **empty**
`feedback` table — migration 005 applies at `connect()` before the JSONL load, so the family is
queryable and the failure is an honest `below required minimum`, not an I/O error (exit 1, not
exit 2).

### Verbatim refusal texts (the four the beat's note quotes from)

```
FB-001: feedback leaves the package only on the OPERATOR's word — re-run this item with "operator_confirm": true after their explicit confirmation; never in unattended mode
```

```
FB-001: the operator confirmed this row as it stood — content drifted on ['detail']; re-confirm the change with "operator_confirm": true, or record a new FB- row
```

```
FB-002: a local tool over the package exists only on the OPERATOR's word — interview them with what it reads (exports/ only) and writes (nowhere tool-owned), then re-run this item with "operator_confirm": true; never in unattended mode
```

```
actor 'system:lesson-guard' is the engine's own namespace (system:<component> rows are what the server witnessed) — a caller records as human:<name> or agent:<session>
```
