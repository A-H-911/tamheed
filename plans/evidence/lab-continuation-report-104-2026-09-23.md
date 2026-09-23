# Lab continuation report — beat 20, v4.13.0 RC (plan 104, 2026-09-23)

> The execution agent's report from `lab/scenario.md` beat 20 (the findings_29 continuation: the
> feedback channel's middle — the request beat 18 reported upstream, answered by a partial row and
> journaled as bookkeeping that claims no word, the readiness advisory and the handoff warning that
> fall silent with it, the review page's split folds; the header read that returns every column;
> and the three guard refinements — the presence-checked verdict, the substitute re-run, and
> `expect_unchanged` honouring omission), archived **verbatim** below the header. Context: an
> INCREMENTAL real-agent session (`actor: agent:lab-beat-20`) against the recorded `lab-tracker`
> fixture, driven in-process through the working-tree server (`plugins/tamheed/server/`, the
> plans-100–103 tree at `main` `6b98480`), six scripts run from the worktree root, each opening and
> closing the package, `data/.lock` absent before the first and after the last. Files touched = the
> fixture (`data/` — `defects.jsonl`, `feedback.jsonl`, `packages.jsonl`, `progress_entries.jsonl`;
> `csv/` — the three matching exports; `review.html`) + `evals/evals.json` (eight appended
> assertions on the `lab-tracker` case, plus the ONE pre-existing beat-18 entry the reviewer's
> ruling re-aimed — see **The STOP and the ruling** below) + `lab/scenario.md`, `lab/README.md` +
> this report. No file under `plugins/`, `tests/`, `check.py`, `evals/pkg_check.py`,
> `CHANGELOG.md`, `plans/README.md`, any version stamp or any other fixture was edited. **Zero**
> hand edits of a `data/`, `csv/`, `exports/` or `review.html` file were made: unlike beat 19, this
> beat edits no prompt file either — the fixture changed **only** through the tools. No
> registry-sync and no migration: `package_migrate` was NOT run. All three verification commands
> green (`pkg_check gates` `ready=True`, `run_evals` lab-tracker **81/81** — 73 before the beat, +8
> — `check.py` `ALL CHECKS PASSED`). A full `package/` backup was taken to `<scratch>/b20/backup`
> before the first open; nothing was restored from it, and it is the tree every new assertion was
> proved to FAIL against.
>
> **Deviations from the plan's steps.** None that changed a step's substance. Three notes:
>
> **N-1 — no assertion needle was narrowed.** All eight `cmd`s were run verbatim as the plan gives
> them, against the backup first; all eight exit non-zero there and 0 against the fixture. Nothing
> was hollow, so nothing was adapted.
>
> **N-2 — the run STOPPED at Step 9 and was resumed on a reviewer ruling.** The plan's Done
> criterion "81: 73 + 8, all pass" was unreachable within the plan's scope, because Step 2 (which
> the plan mandates) falsifies one of the 73. The agent stopped without committing, and the
> reviewer's ruling — recorded in the plan as **Step 8b** and quoted verbatim in its own section
> below — re-aimed the offending beat-18 predicate. That one in-place edit is the only change to
> `evals/evals.json` beyond the eight appends.
>
> **N-3 — the operator's word.** `operator_confirm: true` was sent in exactly ONE place, step 4.2,
> where plan 104 grants it; nothing else in the repository grants it and no other step used it.

## Tamheed v4.13.0 lab continuation — beat 20 — execution report

### Numbered tool-call log (in-process handler calls + verbatim outcomes)

**Drift check.** `git log --oneline -1` → `6b98480 docs: plans 100-102 in every teaching surface
and both feedback diagrams (plan 103)` — the commit the reviewer named.
`python plugins/tamheed/server/tamheed_server.py --selftest` → `mcp sdk: ok (1.27.2) — 19/19 tools
registered`.

**1. Step 1 — baseline and backup.** `package/` copied to `<scratch>/b20/backup` before any open
(no `data/.lock` in the source or the copy; 28 `data/*.jsonl` files).

`server_info()` before the first open:

```json
{"ok": true, "version": "4.12.0",
 "package_root": "<worktree>/evals/sample-results/lab-tracker",
 "open_package": null, "package": null,
 "migrations_head": "005_feedback.sql", "schema_version": 5}
```

`gate_run()` → `ready: true`; all eight gates `pass` (`G-IDS`, `G-DEC-STATUS`, `G-REQ-SRC`,
`G-TRACE`, `G-SET`, `G-PROGRESS`, `G-COMPLETE`, `G-REL`).

`package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "91c87a33ce3e18983919c378cd958194745d8dcd6d934b34aeaca94ba0970b40",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

Family totals: `progress-entry` **35**, `defect` **5**, `feedback` **2** — exactly the plan's
"current state".

`server_info()["package"]` — the whole block, ten keys:

```json
{"name": "lab-tracker", "title": "tick — tiny CLI task tracker", "profile": "rnd",
 "mode": "full", "iteration": 1, "package_version": "4.0.0",
 "mvp_definition": null, "entry_point": "prompts/project-kickoff.md",
 "go_no_go": "GO — MVP complete; PH-2 open", "created_at": "2026-08-14T14:33:11Z"}
```

It carries `mvp_definition` (null at baseline) and `created_at`, as the plan requires.

`readiness_check("package")` → `ready: false` (by design; the scenario's deliberately-open items).
Its `feedback-unanswered` entry:

```json
{"rule": "feedback-unanswered", "severity": "advisory", "status": "fail",
 "entities": ["FB-001"],
 "note": "feedback reported upstream and not yet answered. When it ships - or, for a question, when the maintainer answers - set lifecycle_status Resolved with `resolved_in` (the release or the response) and `upstream_ref` (the plan or reply), as a PARTIAL row: id, kind, title and those three (omitted columns are preserved; the engine journals the move). `Rejected` on the operator's word if upstream declined. A local-tool row is a register: it never resolves and is not listed here",
 "population": {"table": "feedback", "rows": 2, "scoped": false}}
```

`handoff_emit(<scratch>/h1)["warnings"]` — the two feedback lines, verbatim:

```
1 confirmed feedback row(s) not yet reported upstream (FB-002) — entity_export("feedback.json", args={"type": "feedback"}) and QUOTE its envelope and rows in your findings (exports are point-in-time and may be untracked in your git); set each row Reported once it has left
```

```
1 feedback row(s) reported upstream and not yet answered (FB-001) — when the maintainer ships or answers it, set the row Resolved with resolved_in and upstream_ref (a partial row: id, kind, title and those three); the feedback-unanswered readiness rule lists the same rows
```

(The first `handoff_emit` call returned `ok: false` for one reason only — the scratch target
directory did not exist yet. Re-run with it created, it returned `ok: true`. Nothing was emitted
into the package: `prompt_library.emitted: []`, `project_prompts: ["project-kickoff.md"]`.)

`package_close()` → `{"ok": true, "package": "package"}`; no lock.

**2. Step 2.1 — the row as it stood.** `entity_query("feedback", id="FB-001")`:

```json
{"kind": "missing-capability",
 "title": "a patch mode for one column of a long row",
 "lifecycle_status": "Reported", "resolved_in": null, "len(detail)": 666}
```

**3. Step 2.2 — the recipe: a PARTIAL row, and the engine's own bookkeeping row.** The item sent
was exactly the recipe the readiness note teaches — `id`, `kind`, `title` (both verbatim from the
stored row) and the three bookkeeping columns:

```json
{"type": "feedback", "id": "FB-001", "kind": "missing-capability",
 "title": "a patch mode for one column of a long row",
 "lifecycle_status": "Resolved", "resolved_in": "4.12.0",
 "upstream_ref": "tamheed plan 095"}
```

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "FB-001",
   "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 8},
                       {"column": "resolved_in", "old_len": 0, "new_len": 6},
                       {"column": "upstream_ref", "old_len": 0, "new_len": 16}],
   "feedback_audit": "PE-036"}]}
```

`changed_columns` is **exactly** the three bookkeeping columns — the absence of every other column
from that list IS the proof that the UPDATE preserved it. The journal row
(`entity_query("progress-entry", id="PE-036")`):

```json
{"id": "PE-036", "event_type": "transition",
 "entry": "FEEDBACK FB-001 -> Resolved (was Reported; kind missing-capability) — bookkeeping, no word required; resolved_in 4.12.0; upstream_ref tamheed plan 095",
 "subject_id": "FB-001", "actor": "system:feedback-guard", "corrects": null,
 "phase_id": null, "slice_id": null, "occurred_at": "2026-09-23T13:54:24Z",
 "custom_attributes": null, "last_referenced": null}
```

Mechanically checked on that string: contains `FB-001 -> Resolved (was Reported` → **True**;
contains `bookkeeping, no word required` → **True**; contains `attested` → **False**. The row says
which kind of move it was and claims no word it did not get. (STOP condition not met.)

**4. Step 2.3 — the omitted columns, byte-compared against the BACKUP.** The row was read back and
compared column by column against the **backup's** `data/feedback.jsonl` line for `FB-001` (a read
of the BACKUP, never of the fixture):

| Column | Backup vs fixture |
|---|---|
| `kind` | SAME |
| `title` | SAME |
| `detail` (666 chars) | **SAME — byte-identical** |
| `workaround` (`none - recorded here instead of a script`) | **SAME — byte-identical** |
| `tool_path` | SAME |
| `tool_or_rule` | SAME |
| `plugin_version` | SAME |
| `confirmed_by` | SAME |
| `confirmed_at` | SAME |
| `recorded_at` | SAME |
| `custom_attributes` | SAME |
| `last_referenced` | SAME |

Twelve of twelve omitted columns untouched; only the three sent ones moved. A partial row is a
patch — which is precisely the capability `FB-001` asked for, now used to close `FB-001`.

**5. Step 2.4 — the rule and the warning fall silent.** `readiness_check("package")`:

```json
{"rule": "feedback-unanswered", "severity": "advisory", "status": "pass",
 "entities": [],
 "population": {"table": "feedback", "rows": 2, "scoped": false}}
```

`handoff_emit(<scratch>/h2)["warnings"]` — the FB-001 line is **gone**; only the stale-stock line
and the FB-002 export line remain, and `any warning containing "not yet answered"` → **False**.
`gate_run()["ready"]` → `true`.

**6. Step 3 — the header read (plan 101, the field's FB-015).**
`entity_upsert([{"type": "package", "mvp_definition": "add, list and done over a persisted store — the loop a user runs ten times a day"}])`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "lab-tracker",
   "changed_columns": [{"column": "mvp_definition", "old_len": 0, "new_len": 80}]}]}
```

`server_info()["package"]`:

```json
{"name": "lab-tracker", "title": "tick — tiny CLI task tracker", "profile": "rnd",
 "mode": "full", "iteration": 1, "package_version": "4.0.0",
 "mvp_definition": "add, list and done over a persisted store — the loop a user runs ten times a day",
 "entry_point": "prompts/project-kickoff.md",
 "go_no_go": "GO — MVP complete; PH-2 open", "created_at": "2026-08-14T14:33:11Z"}
```

`mvp_definition` reads back byte-identical to what was sent; `created_at` is
`"2026-08-14T14:33:11Z"` — **non-null**, and a column no caller may write. The read is a SUPERSET
of plan 094's write.

**`v1_manifest_derived` is ABSENT** from the header, and correctly so — this is an observation of
the returned keys, not an inference: the key list is exactly
`['name', 'title', 'profile', 'mode', 'iteration', 'package_version', 'mvp_definition',
'entry_point', 'go_no_go', 'created_at']`, the ten names of `_PACKAGE_ROW`. This package was born
v4 (`package_version: "4.0.0"`, `created_at` 2026-08-14, the plan-031 re-baseline) and was **never
migrated from a v1 manifest**, so there is nothing for that annotation to annotate; `_V1_DERIVED`
is `export_html`'s annotation over `mode`/`profile`/`created_at`, carried as data, not a stored
column. `gate_run()["ready"]` → `true`.

**7. Step 4.1 — the verdict, PRESENCE-checked: the re-send is REFUSED.** The current verdict,
read from the header and re-sent **unchanged**, with no `operator_confirm`:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "lab-tracker",
   "error": "go_no_go is the package's governance verdict and changes only on the OPERATOR's word — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
```

**This is the probe the 4.12.0 release brief got wrong.** Under the old change-checked guard, an
unattended re-send of the stored verdict was accepted, so the brief's refusal probe could not fail.
Presence-checked, naming the verdict at all is the operator's act, whatever the value — a header
copied wholesale out of `server_info().package` and pasted back is refused unattended.

**8. Step 4.2 — on the operator's word: accepted, and nothing journaled.** *The operator's word for
every `operator_confirm: true` in this beat is given by plan 104; nothing else in the repository
grants it.* The same item with `"operator_confirm": true`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "lab-tracker", "changed_columns": []}]}
```

`changed_columns: []`, and **no `package_audit` key**. `entity_query("progress-entry",
limit=1)["total"]` read **36** before step 4 and **36** after it — unchanged across the whole step.
The audit row is written only when the verdict MOVES: re-affirming a verdict journals nothing, so
the store carries no old == new rows. `server_info()["package"]["go_no_go"]` still
`"GO — MVP complete; PH-2 open"`; `gate_run()["ready"]` → `true`.

**9. Step 5.1 — the substitute lands once.** `SL-002` was verified present first —
`entity_query("slice", id="SL-002")` → `{"count": 1, "total": 1, "id": "SL-002", "title": "Date
logic & team quality bar"}` — so the plan's id was used unchanged. `DEF-005`'s title before:
`export header DRIFTS (see DEF-001; mock id \`RISK-808\`; score = (KPI-17_score * 0.25) +
(KPI-10_score * 0.2))`.

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005",
   "substituted": {"title": 1},
   "changed_columns": [{"column": "title", "old_len": 108, "new_len": 126}]}]}
```

Title after: `export header DRIFTS (see DEF-001 (fixed in SL-002); mock id \`RISK-808\`; score =
(KPI-17_score * 0.25) + (KPI-10_score * 0.2))`. `gate_run()["ready"]` → `true` (the title's new
citation `SL-002` resolves, as does `DEF-001`).

**10. Step 5.2 — the RE-RUN is REFUSED.** The SAME item sent a second time, byte-identical:

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "DEF-005",
   "error": "DEF-005: 'DEF-001 (fixed in SL-002)' already occurs 1 time(s) in 'title' and contains 'DEF-001' — a re-run would compound it; send old and new with the characters that bound them (the backticks, the delimiter) so the result cannot re-match, or a full row"}]}
```

Contains `already occurs 1 time(s)` → True; contains `bound` → True. The title read back unchanged
by 5.2, and `title.count("DEF-001 (fixed in SL-002)")` = **1** — exactly one. A replacement that
contains its own needle re-matches its own output; the first run passes and the second is a re-run,
refused with the remedy rather than silently doubling the prefix. **Step 5.2 was NOT accepted** —
the guard is present. `gate_run()["ready"]` → `true`.

**11. Step 6 — `expect_unchanged` honours omission.** `entity_query("defect", id="DEF-005")` showed
`custom_attributes: null`, so — as the plan directs — the FULL row was written back once with
`{"lab": "beat 20"}` (`id`, `title`, `severity`, `lifecycle_status`, `found_in`, `fixed_by`,
`custom_attributes`; `last_referenced` is `work_bind`'s stamp and was not sent):

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005",
   "changed_columns": [{"column": "custom_attributes", "old_len": 0, "new_len": 18}]}]}
```

Exactly one `changed_columns` entry. Then the PARTIAL row — `id`, `title` (verbatim), `severity`,
`lifecycle_status`, with `custom_attributes` **named in `expect_unchanged` and OMITTED from the
row**:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005", "changed_columns": []}]}
```

**Accepted**, `changed_columns: []`. An omitted column is preserved by the UPDATE — the UPDATE
assigns only sent names — so naming it is a true assertion, never drift. This is the write that
plan 102 fixed: before it, a correct partial write was refused. The same item with a drifted value
actually **SENT** (`"custom_attributes": {"lab": "beat 20 drifted"}`):

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "DEF-005",
   "error": "DEF-005: expect_unchanged — custom_attributes differ(s) from the stored row (a sent column must match; an omitted column is preserved by the UPDATE and never counts as drift): the transport altered the value; re-fetch the row through entity_query and paste that"}]}
```

Contains `custom_attributes differ` → True; contains `omitted column is preserved` → True. The
stored value is still `{"lab": "beat 20"}`. A sent column must match; an omitted one is never
compared. `gate_run()["ready"]` → `true`.

**12. Step 7 — the closing note, then the page.** ONE `progress_update` entry, `event_type:
"note"`, actor `agent:lab-beat-20` → `{"ok": true, "ids": ["PE-037"]}`. It was written **BEFORE**
`export_html`, and its last paragraph says so, so the page that ships carries it. All seven needles
were verified present in the note text before the write: `bookkeeping, no word required`, `changes
only on the OPERATOR's word`, `already occurs 1 time(s)`, `omitted column is preserved`,
`feedback-unanswered`, `mvp_definition`, and `presence` (the note says *presence-checked*, and
*presence check* where it narrates step 4.1).

`export_html()`:

```json
{"ok": true, "path": "<worktree>/evals/sample-results/lab-tracker/package/review.html",
 "bytes": 169636,
 "csv": {"emitted": ["csv/defects.csv", "csv/feedback.csv", "csv/progress_entries.csv"],
         "unchanged": [23 others], "diverged": [], "removed": [], "unowned": []}}
```

The rendered page was then read from disk (plan 100's split folds):

```
review.html contains 'id="feedback-closed"'                     -> True  (count 1)
review.html contains 'Resolved or rejected (kept as evidence)'  -> True  (count 1)
review.html contains 'Reported, resolved or rejected'           -> False
review.html contains 'id="feedback-reported"'                   -> False
```

The third reading is a real observation, not a vacuous one: the **pre-beat** page carried exactly
the old heading `Reported, resolved or rejected` over the `feedback-closed` anchor — a closing
heading standing over a row that was still a live request. It is gone, and the resolved row now
sits under `Resolved or rejected (kept as evidence)`. The `feedback-reported` fold is absent
because it renders only when it holds rows, and resolving `FB-001` emptied it.

`gate_run()` → `ready: true`, all eight gates `pass`. `package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "a2fc169b717c03c4e59be0b3452c6b2783236de188c610c575a1400cdab59b32",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

`package_close()` → `{"ok": true, "package": "package"}`. No `data/.lock` remains.

### Mechanism → observed

| Plan | Mechanism | Verdict |
|---|---|---|
| 100 | The move WITHIN the bound set is journaled by the engine — `feedback_audit` `PE-036`, `event_type: "transition"`, actor `system:feedback-guard` — and the row SAYS which kind of move it was (`bookkeeping, no word required`), never claiming a word: `attested` appears nowhere in it | **observed** (step 2.2) |
| 100 | The disposition recipe is a PARTIAL row: `changed_columns` names exactly `lifecycle_status`, `resolved_in`, `upstream_ref`, and all twelve omitted columns read back byte-identical to the pre-beat backup | **observed** (steps 2.2, 2.3) |
| 100 | The advisory `feedback-unanswered` moves `fail` (`entities: ["FB-001"]`) → `pass` with an empty list | **observed** (step 2.4) |
| 100 | `handoff_emit`'s THIRD feedback warning — the unanswered report — disappears once the row is answered | **observed** (step 2.4) |
| 100 | The page's split folds: the resolved row files under `id="feedback-closed"` / `Resolved or rejected (kept as evidence)`, and the old closing heading `Reported, resolved or rejected` over live reports is gone | **observed** (step 7) |
| 101 | `server_info().package` carries ALL TEN header columns — a SUPERSET of the write: `mvp_definition` written through the tool reads straight back, and `created_at` is non-null although no caller may write it. `v1_manifest_derived` is absent: never migrated from v1 | **observed** (step 3) |
| 102 | `go_no_go` is PRESENCE-checked: the CURRENT verdict re-sent unchanged and unattended is REFUSED — `changes only on the OPERATOR's word` — the shape the change-checked guard let through | **observed** (step 4.1) |
| 102 | On the word the same item is accepted with `changed_columns: []` and NO `package_audit`, and the progress-entry total holds at 36: the audit row is written only when the verdict MOVES | **observed** (step 4.2) |
| 102 | A prefix repair by `substitute` lands ONCE — `substituted: {"title": 1}`, 108 → 126 | **observed** (step 5.1) |
| 102 | The RE-RUN of the same substitute is REFUSED, naming the count and the bounding remedy; the title still carries exactly one replacement | **observed** (step 5.2) |
| 102 | `expect_unchanged` honours OMISSION: a partial row naming an omitted column is ACCEPTED (`changed_columns: []`) — and a sent drifted value is still REFUSED (`omitted column is preserved`) | **observed** (step 6) |

**Every mechanism the plan names fired. No row reads `not observed`.**

**Not exercised, by design.** `package_migrate` was not run (the plan forbids it; this batch adds
no family), no registry-sync was needed, and `FB-002` was left untouched as the plan directs — a
`local-tool` row is a register: it never resolves and `feedback-unanswered` never lists it (the
rule's `population` still reads `rows: 2`, so the pass is not vacuous; it measured both rows and
excluded the register by predicate, not by absence).

### The STOP and the ruling (Step 8b)

The run **stopped at Step 9** before committing. `run_evals --case lab-tracker` reported all 81
assertions `pass` — including all eight new ones — but the case FAILED on ONE pre-existing entry,
appended in beat 18 for plan 087:

```
  FAIL     A missing function was recorded as feedback, confirmed on the operator's word, and reported (plan 087).
           $ ...python.exe evals/pkg_check.py count ...\lab-tracker/package feedback --col lifecycle_status=Reported --min 1
           got exit 1, expected exit 0
           | count=0
           | below required minimum 1
FAIL  lab-tracker

1 case(s) checked, 1 failed, 0 skipped
```

`FB-001` was the fixture's **only** `Reported` feedback row — as plan 104's own "Current state"
records — so Step 2, which the plan mandates, necessarily falsifies that assertion. The Done
criterion "81: 73 + 8, all pass" was therefore arithmetically unreachable, and the only repair was
a change to an **existing** entry, outside the plan's scope (`evals/evals.json` — *append to the
`lab-tracker` case only*). The agent invoked the STOP condition *"any tool result contradicts this
plan in a way the plan records cannot explain"*, made no commit, wrote no evidence file, did not
run `check.py`, and left the tree untouched for the reviewer.

**The reviewer's ruling, verbatim:**

> Ruling from the reviewer: your STOP was correct, and the gap was the plan's, not yours. Continue
> from Step 9 with one amendment.
>
> The plan file in your worktree is NOT updated (the amendment lives on main); apply exactly this,
> which the plan now records as "Step 8b: Amendment (the reviewer's ruling)":
>
> Edit IN PLACE the pre-existing beat-18 entry in `evals/evals.json` (`lab-tracker` case, the one
> whose cmd is `count ... feedback --col lifecycle_status=Reported --min 1`) so it reads:
>
> ```json
> {"check": "A missing function was recorded as feedback and confirmed on the operator's word - the engine's own journal row (plan 087; its reporting and resolution are beat 20's).",
>  "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","FB-001 -> Confirmed (was Proposed","--tables","progress_entries"], "expect_exit": 0}
> ```
>
> Reason: it asserted a live lifecycle state the channel is designed to leave; the fact beat 18
> established — the engine's `system:feedback-guard` confirmation row — survives disposition (that
> string exists in the fixture's journal; I checked). The "reported and answered" half is your
> assertion 2. Nothing else in the file changes; keep the file's formatting (json.dumps indent=2,
> ensure_ascii=False, trailing newline) so the diff stays minimal.

**Applied as given.** The needle was verified in the fixture's journal first —
`grep -c -F "FB-001 -> Confirmed (was Proposed" data/progress_entries.jsonl` → **1**, the row
reading `FB-001 -> Confirmed (was Proposed; kind missing-capability) on the operator's word` — so
the replacement asserts a fact that is now permanent. The entry replaced was
`deterministic_assertions[56]`, matched by its exact `cmd` list (exactly one match); the count
stayed at 81; and the file still round-trips byte-identically under
`json.dumps(indent=2, ensure_ascii=False) + "\n"`. Nothing else in the file changed.

The substantive lesson: **an eval assertion over a lifecycle column asserts a state, and a channel
with a middle is designed to leave its states.** Beat 18 proved the row went out; it pinned that
with the row's *current* status rather than with the engine's journal of the transition. The
journal is append-only and survives every later disposition — which is exactly why plan 100 gave
the bookkeeping move a journal row in the first place.

### Findings

Numbered after `F-5`, the last of beat 19's findings.

**F-6 (methodology, MEDIUM — the recipe lesson).** A dry run on a scratchpad COPY of the fixture
(the batch-28 lesson, recipe steps F-4/F-5) proves the *new* surface fires, but it **cannot** catch
an *existing* assertion that the beat falsifies, because `run_evals` is never invoked against the
copy — it is hard-wired to `{case_dir}`, the recorded fixture. This beat's STOP is the first
instance. **Recipe amendment:** when a beat changes a lifecycle column of an existing row, the dry
run must also grep the target eval case for assertions whose predicate names that column or that
state (`--col <column>=`, `--col lifecycle_status=`), and re-aim them in the same plan rather than
discovering the collision in the executor's Step 9.

**F-7 (observation, INFO).** The row that closed `FB-001` is itself the capability `FB-001` asked
for. The request was "a patch mode for one column of a long row"; the disposition recipe plan 100
teaches is a partial row — id, kind, title and three bookkeeping columns — and `changed_columns`
proves the other twelve were preserved. The channel's own answer to the request is the mechanism
used to close it.

**F-8 (observation, INFO).** Step 4.2's `changed_columns: []` with no `package_audit` is the pair
to step 4.1's refusal, and the two together are the whole of the presence-check design: the
**guard** is presence-checked (naming the verdict is the operator's act, whatever the value) while
the **audit** stays change-checked (a witness row only when the verdict moves). A reader who
conflates them would expect either an unattended no-op to pass or an attested no-op to journal;
neither happens, and the progress-entry total holding at 36 is the proof.

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
... (the eight new checks and the re-aimed beat-18 check, all `pass`)
PASS  lab-tracker
1 case(s) checked, 0 failed, 0 skipped

$ python check.py                       # backgrounded; the tree was not touched while it ran
ALL CHECKS PASSED
```

`run_evals` reports the `lab-tracker` case at **81** deterministic assertions, 81 `pass` (73 before
the beat, +8).

### No hollow assertion: the eight new checks, backup vs fixture

Every `cmd` was run twice — once with `{case_dir}/package` replaced by the Step 1 BACKUP
(`<scratch>/b20/backup`), once against the fixture. **No needle was narrowed**; all eight were run
verbatim as plan 104 gives them.

| # | Check | Backup exit | Backup output | Fixture exit | Fixture output |
|---|---|---|---|---|---|
| 1 | A reported feedback row was resolved by the recipe and the engine journaled the bookkeeping move without claiming a word (plan 100). | **1** | `'bookkeeping, no word required' not found` | 0 | `progress_entries.jsonl:36, :37` |
| 2 | The resolved row names the release and the plan that answered it (plan 100). | **1** | `count=0` / `below required minimum 1` | 0 | `count=1` |
| 3 | The MVP definition was written through the tool and is stored (plan 101). | **1** | `'ten times a day' not found` | 0 | `packages.jsonl:1` |
| 4 | Re-sending the current verdict without the operator's word was refused, and the note quotes the probe (plan 102). | **1** | `'presence' not found` | 0 | `progress_entries.jsonl:37` |
| 5 | A prefix repair landed once by substitute (plan 102). | **1** | `'DEF-001 (fixed in' not found` | 0 | `defects.jsonl:5` |
| 6 | The second run of the same substitute was refused, and the note names the count (plan 102). | **1** | `'already occurs 1 time(s)' not found` | 0 | `progress_entries.jsonl:37` |
| 7 | A partial row naming an omitted column in expect_unchanged passed, and a sent drifted one was refused (plan 102). | **1** | `'omitted column is preserved' not found` | 0 | `progress_entries.jsonl:37` |
| 8 | The recorded review page files the resolved row under the closed fold, not a closing heading over live reports (plan 100). | **1** | `'Resolved or rejected (kept as evidence)' NOT found in <backup>/review.html` | 0 | found in `.../package/review.html` |

Eight of eight fail on the backup and pass on the fixture.

The re-aimed beat-18 assertion (Step 8b) is deliberately **not** in that table: it is not a new
assertion but a repaired pre-existing one, and its needle — the engine's confirmation row from beat
18 — is present in the backup too, which is precisely the property the ruling selected it for.

### Verbatim refusal texts (the three the beat's note quotes from)

```
go_no_go is the package's governance verdict and changes only on the OPERATOR's word — re-run this item with "operator_confirm": true after their explicit confirmation; never in unattended mode
```

```
DEF-005: 'DEF-001 (fixed in SL-002)' already occurs 1 time(s) in 'title' and contains 'DEF-001' — a re-run would compound it; send old and new with the characters that bound them (the backticks, the delimiter) so the result cannot re-match, or a full row
```

```
DEF-005: expect_unchanged — custom_attributes differ(s) from the stored row (a sent column must match; an omitted column is preserved by the UPDATE and never counts as drift): the transport altered the value; re-fetch the row through entity_query and paste that
```

### Verbatim engine-witness text (the one row no caller wrote)

```
FEEDBACK FB-001 -> Resolved (was Reported; kind missing-capability) — bookkeeping, no word required; resolved_in 4.12.0; upstream_ref tamheed plan 095
```

`event_type: "transition"`, actor `system:feedback-guard`, `subject_id: "FB-001"`, id `PE-036`. No
caller may write a `system:` actor, and no caller asked for a word here — so the row says
*bookkeeping* and not *attested*. That distinction is the whole of plan 100's middle.
