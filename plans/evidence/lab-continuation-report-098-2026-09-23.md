# Lab continuation report — beat 19, v4.12.0 RC (plan 098, 2026-09-23)

> The execution agent's report from `lab/scenario.md` beat 19 (the findings_28 continuation: the
> phantom id in the project's own kickoff prompt reported amber and made inert by backticks, the
> token census that counts every occurrence, the go/no-go verdict that lands only on the operator's
> word — a string never attests — and the engine's own witness of it, the one-token substitute that
> touches nothing else and the glued, immutable and mixed substitutes refused, the review page's
> Readiness and Feedback sections), archived **verbatim** below the header. Context: an INCREMENTAL
> real-agent session (`actor: agent:lab-beat-19`) against the recorded `lab-tracker` fixture, driven
> in-process through the working-tree server (`plugins/tamheed/server/`, the plans-091–097 tree at
> `main` `de7055a`), six scripts run from the repo root, each opening and closing the package,
> `data/.lock` absent before the first and after the last. This is the **third dispatch** of the
> beat: the first stopped at Step 4.1 on the header crash (F-4, fixed in plan 094's amendment,
> `d8ed401`), the second at Step 6 on the page renderer (F-5, fixed in plan 096's amendment,
> `de7055a`). It was performed WHOLE from Step 1 against a pristine fixture; no earlier run's
> observations are reused. Files touched = the fixture (`data/` — `defects.jsonl`,
> `packages.jsonl`, `progress_entries.jsonl`; `csv/` — the two matching exports; `prompts/` —
> `project-kickoff.md`, the one file this beat edits BY HAND because a prompt is a file;
> `review.html`) + `evals/evals.json` (eight appended assertions on the `lab-tracker` case only) +
> `lab/scenario.md`, `lab/README.md` + this report. No file under `plugins/`, `tests/`, `check.py`,
> `evals/pkg_check.py`, `CHANGELOG.md`, `plans/README.md`, any version stamp or any other fixture
> was edited. **Zero** hand edits of a `data/`, `csv/`, `exports/` or `review.html` file were made;
> apart from the one prompt file the plan names, the fixture changed only through the tools.
> `package_migrate` was NOT run — this batch adds no family. All three verification commands green
> (`pkg_check gates` `ready=True`, `run_evals` lab-tracker **73/73** — 65 before the beat, +8 —
> `check.py` `ALL CHECKS PASSED`). A full `package/` backup was taken to `<scratch>/b19/backup`
> before the first open; nothing was restored from it, and it is the tree every new assertion was
> proved to FAIL against.
>
> **Deviations from the plan's steps.** None that changed a step's substance. Two notes:
>
> **N-1 — no assertion needle was narrowed.** All eight `cmd`s were run verbatim as the plan gives
> them, against the backup first; all eight exit non-zero there and 0 against the fixture. Nothing
> was hollow, so nothing was adapted. (The dispatch's ruling that assertion 4's needle
> `longer token ('KPI-17_score')` matches the engine's refusal verbatim was confirmed by the
> refusal text quoted in step 5.2 below.)
>
> **N-2 — the scenario paragraph's `"false"` versus the step's `"true"`.** Item 19's narrative
> paragraph is the plan's own blockquote, appended verbatim; it says *a string `"false"` does not
> attest*, which is the rule as `_operator_word` states it ("a truthy string like \"false\" or
> \"no\" must never attest"). The step actually fired is 4.3, the STRING `"true"` — the sharper
> case, since it is the very word the refusal asks for. The ✔ item under the paragraph records the
> value that was sent.

## Tamheed v4.12.0 lab continuation — beat 19 — execution report

### Numbered tool-call log (in-process handler calls + verbatim outcomes)

**Drift check.** `git log --oneline -1` → `de7055a fix: the review page renders a waived rule's
entries as records, not strings (plan 096, lab beat 19's F-5)` — the commit the reviewer named.
`python plugins/tamheed/server/tamheed_server.py --selftest` → `mcp sdk: ok (1.27.2) — 19/19 tools
registered`.

**1. Step 1 — baseline and backup.** `package/` copied to `<scratch>/b19/backup` before any open
(no `data/.lock` in the source or the copy; 28 `data/*.jsonl` files).

`server_info()` before the first open:

```json
{"ok": true, "version": "4.11.0",
 "package_root": "<worktree>/evals/sample-results/lab-tracker",
 "open_package": null, "package": null,
 "migrations_head": "005_feedback.sql", "schema_version": 5}
```

`gate_run()` → `ready: true`; all eight gates `pass` (`G-IDS` "verified now: foreign_key_check
clean, entity_index consistent (92 ids)", `G-DEC-STATUS`, `G-REQ-SRC`, `G-TRACE`, `G-SET`,
`G-PROGRESS`, `G-COMPLETE`, `G-REL`); `audit_evidence` `evidenced: 3, narrated: 0, ungraded: 1`
(`AV-005`); `requirements_unwired` advisory, empty.

`package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "cc521ea4fe08607964b98eeb753d56c1d80acc2cc7f00756f7711efd5d28cfca",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

Family totals: `progress-entry` **33**, `defect` **5**, `lesson` **5**, `feedback` **2** — exactly
the plan's "current state".

`server_info()["package"]`:

```json
{"name": "lab-tracker", "title": "tick — tiny CLI task tracker", "profile": "rnd",
 "mode": "full", "iteration": 1, "package_version": "4.0.0",
 "go_no_go": null, "entry_point": null}
```

Both of step 2's ids were verified ABSENT before the prompt line was written:
`entity_query("defect", id="DEF-090")` → `{"ok": true, "rows": [], "count": 0, "total": 0,
"next_after": null}`; `entity_query("slice", id="SL-007")` → the same. Neither is a phantom by
accident: neither resolves.

`git status --short` after the idle open → close: **empty**. The zero-diff invariant holds.

**2. Step 2.1 — the history line, appended BY HAND.** `prompts/project-kickoff.md` is CRLF-
terminated and already ended with `\r\n`, so the line was appended byte-wise as `line + b"\r\n"`
(`open(p, "ab")`), and the later backtick edit was a bytes `replace` on `rb` read / `wb` write.
The file went from 147 to 214 bytes and `git diff --stat` reads **1 insertion, 0 deletions** — one
line, exactly:

```diff
 Work EP-001 in order. The recording obligations in the target CLAUDE.md are mandatory — the package is the record.
+History: the export bug was DEF-090 and the fix landed in SL-007.
```

**3. Step 2.2 — the rule reads amber.** `readiness_check("package")` → `ready: false` (by design;
`acs-met` and the scenario's deliberately-open items), rule `prompt-ids-resolve`:

```json
{"rule": "prompt-ids-resolve", "severity": "advisory", "status": "fail",
 "entities": ["prompts/project-kickoff.md:4 -> DEF-090",
              "prompts/project-kickoff.md:4 -> SL-007"],
 "note": "identifiers written in the PROJECT's prompt files (`<package>/prompts/*.md` that are not a stock body) that resolve to NO entity - the prose a session reads before it runs any tool: correct the id, record the missing row, or quote history in backticks (a code span is inert). THE ENTITY LIST IS A FLOOR: `in_code_spans` and `not_well_formed` are informational, as for rows; width is tested first",
 "in_code_spans": [], "not_well_formed": [],
 "population": {"table": "prompts/*.md", "rows": 1, "scoped": false, "unit": "files"}}
```

`population` is `{table: "prompts/*.md", rows: 1, scoped: false, unit: "files"}` — files, not rows
— and the note carries `THE ENTITY LIST IS A FLOOR`, as the plan says.

**4. Step 2.3 — the backticks make it inert.** The line became ``History: the export bug was
`DEF-090` and the fix landed in `SL-007`.`` (still one inserted line). The same rule:

```json
{"rule": "prompt-ids-resolve", "severity": "advisory", "status": "pass",
 "entities": [],
 "in_code_spans": ["prompts/project-kickoff.md:4 -> DEF-090",
                   "prompts/project-kickoff.md:4 -> SL-007"],
 "not_well_formed": [],
 "population": {"table": "prompts/*.md", "rows": 1, "scoped": false, "unit": "files"}}
```

`gate_run()["ready"]` was `true` on BOTH readings — the rule is advisory and never moved a gate.

**5. Step 3 — the census (plan 092).** `entity_query("defect", search="RISK-808", context=12)`:

```json
"matched": {"DEF-005": ["title"]}
"occurrences": {"DEF-005": {"title": {"count": 1,
   "snippets": ["1; mock id `RISK-808`; score = ("]}}}
```

`entity_query("defect", search="KPI-1", context=8)`:

```json
"matched": {"DEF-005": ["title"]}
"occurrences": {"DEF-005": {"title": {"count": 2,
   "snippets": ["core = (KPI-17_score ", ".25) + (KPI-10_score "]}}}
```

Two occurrences in one column of one row. A census counts **substrings**: `KPI-1` is not an id
here, it is a prefix of `KPI-17_score` and of `KPI-10_score`, and the census reports both. The
prose-id rule does not — it tests width first, and `_` is a word character (plan 085, beat 18),
so those same two tokens appear in no `prose-ids-resolve` list. The two readings are not in
conflict; they answer different questions.

**6. Step 4.1 — the entry point.** `entity_upsert([{"type": "package", "entry_point":
"prompts/project-kickoff.md"}])`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "lab-tracker",
            "changed_columns": [{"column": "entry_point", "old_len": 0, "new_len": 26}]}]}
```

`server_info()["package"]["entry_point"]` → `"prompts/project-kickoff.md"`. (The `id` echoed is
the stored `name`, `lab-tracker`, not the directory `package` — the one header row read as
`server_info` reads it, which is plan 094's amendment, F-4 of the first dispatch.)

**7. Step 4.2 — the UNATTENDED verdict, refused.** `entity_upsert([{"type": "package",
"go_no_go": "GO — MVP complete; PH-2 open"}])`:

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "lab-tracker",
   "error": "go_no_go is the package's governance verdict and changes only on the OPERATOR's word — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
```

**8. Step 4.3 — the STRING, refused.** The same item with `"operator_confirm": "true"` (a STRING,
and the very word the refusal asks for) was refused in **exactly** the same words — same `error`
string, `applied: 0`. Only the JSON boolean attests.

**9. Step 4.4 — the operator's word.** *The operator's word for every `operator_confirm: true` in
this beat is given by plan 098; nothing else in the repository grants it.* The same item with
`"operator_confirm": true`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "lab-tracker",
   "changed_columns": [{"column": "go_no_go", "old_len": 0, "new_len": 28}],
   "package_audit": "PE-034"}]}
```

`server_info()["package"]["go_no_go"]` → `"GO — MVP complete; PH-2 open"`. The journal row, read
back with `entity_query("progress-entry", search="go_no_go")` (`total: 1`, `matched`
`{"PE-034": ["entry"]}`):

```json
{"id": "PE-034", "event_type": "transition",
 "entry": "PACKAGE lab-tracker go_no_go -> 'GO — MVP complete; PH-2 open' (was None) on the operator's word — operator_confirm attested",
 "subject_id": null, "actor": "system:package-guard", "corrects": null,
 "phase_id": null, "slice_id": null, "occurred_at": "2026-09-23T00:26:46Z",
 "custom_attributes": null, "last_referenced": null}
```

The update and its witness share the item's savepoint — they land together or not at all.

**10. Step 4.5 — the frozen column.** `entity_upsert([{"type": "package", "profile":
"enterprise"}])`:

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "lab-tracker",
   "error": "header column(s) ['profile'] are the package's identity and are frozen — writable: title, mode, iteration, mvp_definition, entry_point, go_no_go"}]}
```

`gate_run()["ready"]` → `true` after the whole of step 4.

**11. Step 5.1 — the substitute.** `entity_upsert([{"type": "defect", "id": "DEF-005",
"substitute": {"title": ["export header drifts", "export header DRIFTS"]}}])`:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005",
   "substituted": {"title": 1},
   "changed_columns": [{"column": "title", "old_len": 108, "new_len": 108}]}]}
```

Exactly one `changed_columns` entry, equal lengths. `entity_query("defect", id="DEF-005")` was
then compared column by column against the **backup's** `data/defects.jsonl` line for `DEF-005`
(a read of the BACKUP, not of the fixture):

| Column | Backup | Fixture | |
|---|---|---|---|
| `id` | `DEF-005` | `DEF-005` | SAME |
| `title` | `export header drifts (see DEF-001; mock id \`RISK-808\`; score = (KPI-17_score * 0.25) + (KPI-10_score * 0.2))` | `export header DRIFTS (…)` — the rest byte-for-byte | DIFF (the one intended token) |
| `severity` | `low` | `low` | SAME |
| `lifecycle_status` | `Open` | `Open` | SAME |
| `found_in` | `SL-002` | `SL-002` | SAME |
| `fixed_by` | `null` | `null` | SAME |
| `custom_attributes` | `null` | `null` | SAME |
| `last_referenced` | `null` | `null` | SAME |

Seven of eight columns byte-identical; the eighth differs only in the four characters the
substitute names. Nothing was stamped, nothing was touched.

**12. Step 5.2 — the glued match, refused.** `{"type": "defect", "id": "DEF-005", "substitute":
{"title": ["KPI-1", "KPI-2"]}}`:

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "DEF-005",
   "error": "DEF-005: 'KPI-1' in 'title' also matches inside a longer token ('KPI-17_score') — a substitute never rewrites part of an id; send the whole token, or a full row"}]}
```

The title read back unchanged (`export header DRIFTS (see DEF-001; mock id \`RISK-808\`; score =
(KPI-17_score * 0.25) + (KPI-10_score * 0.2))`). This is the census's two hits seen from the other
side: the engine refuses to rewrite either of them as *part* of a token.

**13. Step 5.3 — the Approved lesson, refused.** `LL-004`'s `statement` begins `When`; the item
sent was `{"type": "lesson", "id": "LL-004", "substitute": {"statement": ["When", "WHEN"]}}`:

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "LL-004",
   "error": "approved/promoted lessons are immutable: supersede, never edit"}]}
```

The immutability rule fired (not the drift rule). `LL-004`'s `statement` read back identical to
the pre-write read, and `lifecycle_status` is still `Approved`. **No `operator_confirm` was sent
here** — the plan's grant covers step 4.4 and nothing else.

**14. Step 5.4 — the mixed item, refused.** `{"type": "defect", "id": "DEF-005", "severity":
"low", "substitute": {"title": ["a", "b"]}}`:

```json
{"ok": false, "applied": 0,
 "items": [{"index": 0, "ok": false, "id": "DEF-005",
   "error": "a substitute item carries only type, id, substitute, operator_confirm and expect_unchanged — not ['severity']: half a row plus a substitute is ambiguous; send a full row, or a substitute alone"}]}
```

`gate_run()["ready"]` → `true` after the whole of step 5. **None of steps 4.2, 4.3 or 5.3 was
accepted** — no security regression.

**15. Step 6 — the closing note, then the page.** ONE `progress_update` entry, `event_type:
"note"`, actor `agent:lab-beat-19` → `{"ok": true, "ids": ["PE-035"]}`. It was written **BEFORE**
`export_html`, and its last paragraph says so: *"This note is written BEFORE `export_html`; the
review page is re-rendered after it, so the page that ships carries this row and its Readiness and
Feedback sections."* The export that follows makes that true; the page was then read back and the
verification is recorded in this report (below), not in the note. The note quotes verbatim: the
pre-backtick entity string `prompts/project-kickoff.md:4 -> DEF-090`, the clause `changes only on
the OPERATOR's word`, the glued-match refusal naming the `longer token ('KPI-17_score')`, the words
`substituted`, `occurrences` and `package_audit`, and `in_code_spans`.

`export_html()`:

```json
{"ok": true, "path": "<worktree>/evals/sample-results/lab-tracker/package/review.html",
 "bytes": 157134,
 "csv": {"emitted": ["csv/defects.csv", "csv/progress_entries.csv"],
         "unchanged": [24 others], "diverged": [], "removed": [], "unowned": []}}
```

The rendered page was then read from disk (plan 096's sections, each exactly once):

```
review.html contains '<section id="readiness">'  -> True  (count 1)
review.html contains '<section id="feedback">'   -> True  (count 1)
review.html contains 'Evaluated as of'           -> True  (count 1)
```

`gate_run()` → `ready: true`. `package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "91c87a33ce3e18983919c378cd958194745d8dcd6d934b34aeaca94ba0970b40",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

Both id rules were re-read at the close, and both read `pass`:

```json
{"rule": "prose-ids-resolve", "status": "pass", "entities": [],
 "in_code_spans": ["DEF-005.title -> RISK-808"]}
{"rule": "prompt-ids-resolve", "status": "pass", "entities": [],
 "in_code_spans": ["prompts/project-kickoff.md:4 -> DEF-090",
                   "prompts/project-kickoff.md:4 -> SL-007"],
 "population": {"table": "prompts/*.md", "rows": 1, "scoped": false, "unit": "files"}}
```

(`prose-ids-resolve` lists only `DEF-005.title -> RISK-808`, not the note's own backticked
`DEF-090` / `SL-007`, because `progress_entries` is one of `_PROSE_ID_EXEMPT_TABLES` — a journal
is a report of what happened, never a citation.)

`package_close()` → `{"ok": true, "package": "package"}`. No `data/.lock` remains.

### Mechanism → observed

| Plan | Mechanism | Verdict |
|---|---|---|
| 092 | `entity_query(search, context=N)` returns an `occurrences` census — exact per-column counts and bounded snippets — and counts SUBSTRINGS, so one `search="KPI-1"` finds two hits inside one title | **observed** (step 3) |
| 093 | The project's own prompt files are scanned: a phantom id written in `prompts/project-kickoff.md` reads `status: fail`, `entities` naming `<file>:<line> -> <id>`, `population` in `files` not rows, the note carrying `A FLOOR` | **observed** (step 2.2) |
| 093 | Backticking the id moves it to `in_code_spans` and the rule reads `pass`; `gate_run` never moves, because the rule is advisory | **observed** (step 2.3) |
| 094 | `entity_upsert(type="package")` writes a non-verdict header column freely (`entry_point`), `changed_columns` names it, `server_info().package` reads it back | **observed** (step 4.1) |
| 094 | The UNATTENDED verdict change is REFUSED — `changes only on the OPERATOR's word` | **observed** (step 4.2) |
| 094 | A truthy STRING does not attest: `"operator_confirm": "true"` is refused in the same words | **observed** (step 4.3) |
| 094 | On the word the verdict lands and the ENGINE witnesses it in the same savepoint: `package_audit: PE-034`, `transition`, actor `system:package-guard`; the identity columns stay frozen | **observed** (steps 4.4, 4.5) |
| 095 | One token, one column: `substituted: {"title": 1}`, `changed_columns` exactly one entry with equal lengths, every other column byte-identical to the backup | **observed** (step 5.1) |
| 095 | A match glued to a digit is REFUSED, naming the longer token | **observed** (step 5.2) |
| 095 | Every guard still applies through a substitute: an Approved lesson is immutable | **observed** (step 5.3) |
| 095 | A mixed item — half a row plus a substitute — is REFUSED (`carries only`) | **observed** (step 5.4) |
| 096 | The review page carries `<section id="readiness">`, `<section id="feedback">` and `Evaluated as of`, and renders a waived rule's entries as records (the `de7055a` fix) rather than crashing | **observed** (step 6) |

**Not exercised, by design.** `substitute`'s `expect_unchanged` companion key was never sent: no
step asks for it, and the four substitute items cover the accept path and the three refusals the
plan names. `package_migrate` was not run — this batch adds no family, and the plan forbids it.

### Findings

Numbered after `F-4` and `F-5`, this beat's two earlier findings — the header write's
name-vs-directory crash and the page renderer's waived-rule entries — which are named in plan
098's Status section and in the commits `d8ed401` and `de7055a` that fixed them. `F-1`–`F-3`
belong to the first two dispatches' own reports.

**F-6 (methodology, INFO — not a defect).** The two earlier dispatches' stop conditions are both
gone: step 4.1, which crashed the header write when the stored `name` (`lab-tracker`) differs from
the directory (`package`), now reads the one header row as `server_info` does; and step 6's
`export_html`, which crashed on a waived rule's entries, now renders them as records. Both fired
cleanly on the first attempt here. Nothing new was found in their place.

**F-7 (legibility, LOW).** The census and the prose-id rule disagree about `KPI-17_score` in a way
that is correct but worth stating once in the docs: `entity_query(search=…)` is a **substring**
sweep with no token model at all, while `prose-ids-resolve` tests width first and treats `_` as a
word character. A reader who uses the census to audit id usage will over-count; a reader who uses
the rule to find every occurrence will under-count. The beat's closing note says so explicitly so
the fixture itself carries the distinction.

**F-8 (observation, INFO).** The go/no-go verdict the plan dictates contains `PH-2`, which is not
an entity in this fixture. It did not trip `prose-ids-resolve`, and the reason was read, not
inferred: `_scan_prose_ids` sweeps `set(ENTITY_TABLES.values()) - _PROSE_ID_EXEMPT_TABLES`, and
`packages` is not in `ENTITY_TABLES.values()` at all — the header is not a family (which is also
why `entity_query(type="package")` refuses). Recorded here so a later reader does not mistake the
silence for a miss.

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
... (the eight new checks, all `pass`)
PASS  lab-tracker
1 case(s) checked, 0 failed, 0 skipped

$ python check.py                       # backgrounded; the tree was not touched while it ran
ALL CHECKS PASSED
```

`run_evals` reports the `lab-tracker` case at **73** deterministic assertions (65 before the beat,
+8).

### No hollow assertion: the eight new checks, backup vs fixture

Every `cmd` was run twice — once with `{case_dir}/package` replaced by the Step 1 BACKUP
(`<scratch>/b19/backup`), once against the fixture. No needle was narrowed.

| # | Check | Backup exit | Backup output | Fixture exit |
|---|---|---|---|---|
| 1 | The go/no-go verdict was changed on the operator's word and the engine journaled it (plan 094). | **1** | `count=0` / `below required minimum 1` | 0 (`count=1`) |
| 2 | An unattended verdict change was refused, and the note quotes it (plan 094). | **1** | `"changes only on the OPERATOR's word" not found` | 0 (`progress_entries.jsonl:35`) |
| 3 | One token in a long title was corrected by a substitute write (plan 095). | **1** | `'export header DRIFTS' not found` | 0 (`defects.jsonl:5`) |
| 4 | A match glued to a digit was refused, and the note names the longer token (plan 095). | **1** | `"longer token ('KPI-17_score')" not found` | 0 (`progress_entries.jsonl:35`) |
| 5 | The kickoff prompt quotes its history ids in backticks (plan 093). | **1** | `` '`DEF-090`' NOT found in <backup>/prompts/project-kickoff.md `` | 0 |
| 6 | The note names the prompt rule's finding before the fix (plan 093). | **1** | `'project-kickoff.md' not found` | 0 (`progress_entries.jsonl:35`) |
| 7 | The recorded review page carries the Readiness section (plan 096). | **1** | `'section id="readiness"' NOT found in <backup>/review.html` | 0 |
| 8 | The recorded review page carries the Feedback section (plan 096). | **1** | `'section id="feedback"' NOT found in <backup>/review.html` | 0 |

Eight of eight fail on the backup and pass on the fixture.

### Verbatim refusal texts (the five the beat's note quotes from)

```
go_no_go is the package's governance verdict and changes only on the OPERATOR's word — re-run this item with "operator_confirm": true after their explicit confirmation; never in unattended mode
```

(returned identically for the unattended item and for the STRING `"true"` item)

```
header column(s) ['profile'] are the package's identity and are frozen — writable: title, mode, iteration, mvp_definition, entry_point, go_no_go
```

```
DEF-005: 'KPI-1' in 'title' also matches inside a longer token ('KPI-17_score') — a substitute never rewrites part of an id; send the whole token, or a full row
```

```
approved/promoted lessons are immutable: supersede, never edit
```

```
a substitute item carries only type, id, substitute, operator_confirm and expect_unchanged — not ['severity']: half a row plus a substitute is ambiguous; send a full row, or a substitute alone
```
