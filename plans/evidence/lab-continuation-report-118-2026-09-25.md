# Lab continuation report — beat 22, v5.0.0 (plan 118, 2026-09-25)

> The execution agent's report from `lab/scenario.md` beat 22 (the v5.0.0 continuation: the
> retired stock library deleted through the tool on its own proof, the note v5, the `carries`
> relation and its advisory on a scratch package, the corrected note-budget arithmetic, and the
> recorded deferred-work omission read as a deliberate zero by both deferred-work rules).
> Context: an INCREMENTAL real-agent session (`actor: agent:lab-beat-22`) against the recorded
> `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plans-112–117 tree at `main` `f40d68b`), small Python scripts
> run from the worktree root with `PYTHONIOENCODING=utf-8`, every one wrapping its body in
> `try/finally: package_close()`. `data/.lock` absent before the first open and after the last.
>
> Files touched = the fixture (`prompts/` — sixteen deletions and the refreshed `README.md`, both
> by `handoff_emit(refresh_stock=true)`; `data/progress_entries.jsonl`, `csv/progress_entries.csv`,
> `review.html` — by `progress_update` + `export_html`) + `evals/evals.json` (seven appended
> assertions on the `lab-tracker` case, 88 → 95; **no pre-existing entry was edited**) +
> `lab/scenario.md` (beat 22 appended; one parenthetical clause on the line-369 sentence),
> `lab/README.md` + this report. **Zero** hand edits of a fixture file and **no `rm`**: the sixteen
> deletions are the tool's. No file under `plugins/`, `tests/`, `check.py`, `CHANGELOG.md`,
> `plans/README.md` or any version stamp was edited. `package_migrate` was NOT run (migration 006
> applied at connect). No `DW-` row was written to the fixture. A full `package/` backup was taken
> to `<scratch>/b22/backup` before the first open; nothing was restored from it, and it is the tree
> every new assertion was proved to FAIL against. The scratch handoff target (`<scratch>/b22/target`)
> and the scratch `carry` package (`<scratch>/b22/carryroot/carry`) both live outside the repository.
>
> **Deviations from the plan's steps.** None that changed a step's substance. Five notes:
>
> **N-1 — the scratch `carry` package's `gate_run` read `ready: false` (plan: true).** Step 3.4
> expects `gate_run()["ready"]` true "(G-REL accepts the edge)". G-REL did accept it —
> `"G-REL": {"status": "pass", "mistyped": []}` — but the bare `package_create("carry", "Carry",
> "rnd")` package fails **G-SET alone**, on nine Always families it never had
> (`acceptance-criterion`, `assumption`, `constraint`, `decision`, `document-section`,
> `narrative-document`, `open-question`, `requirement`, `risk`); every other gate passed. The
> plan's dry-run measured the fixture, not a bare scratch package. No omission rows or stubs were
> added to force `ready` (that would be improvising); the closing note says exactly this. The
> mechanism the sentence is about — G-REL accepting a typed `carries` edge — is observed.
>
> **N-2 — the line-369 sentence is beat 18's, not beat 20's.** The plan calls
> `lab/scenario.md:369` "beat 20's Pass bar". Line 369 is inside beat 18 ("✔ THE PROMPTS (plan
> 087): `handoff_emit(refresh_stock=true)` reports `refreshed` exactly `prompts/orient-resume.md`
> and `prompts/README.md` …") — the sentence the plan describes by content and line number. The
> clause was appended there, verbatim as the plan gives it. Beat 16 (line 259) also names
> `orient-resume.md` among refreshed stock bodies; the plan scopes ONE clause, so it was left as
> history untouched — flagged for the reviewer.
>
> **N-3 — "the row count (12)".** The note's `Recording obligations` table has **12 `|`-rows
> counting its header row** (`| During execution, when… | Record BEFORE moving on |`), i.e. **11
> obligation rows** plus the header (the `|---|---|` separator excluded). Reported both ways.
>
> **N-4 — the refreshed guide and the server still read `4.14.0`.** `server_info().version` is
> `4.14.0` and the refreshed `prompts/README.md` opens `# How to use this folder — the `package`
> prompt guide (tamheed v4.14.0)` — expected under the plan's "no `plugin.json` bump". When the
> release bump lands, the recorded guide will be byte-equal to the *4.14.0-stamped* v5 body, which
> the engine may classify as stale-stock until someone re-emits with `refresh_stock=true`. The
> reviewer's call, not the beat's.
>
> **N-5 — `python check.py` is RED on one test the plan put out of scope (F-10).** The plan's
> order (green, then commit) could not be honoured: `tests/test_eval_runner.py::
> test_pkg_check_grep_tree` greps the fixture's `prompts/` for `gate_run`, a word only the sixteen
> retired files carried. `tests/**` is out of scope, so the test was NOT edited; every other gate
> stage is green. The beat was committed anyway so the reviewer holds the full result; the fix is
> one needle (F-10).

## Tamheed v5.0.0 lab continuation — beat 22 — execution report

### Numbered tool-call log (in-process handler calls + verbatim results)

**Drift check.** `git log --oneline -1` → `f40d68b docs(plans): plan 118 - lab beat 22's executor
plan (dry-run and F-6 grep cited)` — the dispatch commit.
`python plugins/tamheed/server/tamheed_server.py --selftest` → `mcp sdk: ok (1.27.2) — 19/19 tools
registered`. `package_migrate` was NOT run.

**1. Step 1 — baseline and backup.** `package/` copied to `<scratch>/b22/backup` before any open
(no `data/.lock`; 28 `data/*.jsonl` files; 18 `prompts/*.md`).
- `package_open("package")` → `{"ok": true, "package": "package", ...}`.
- `server_info()` → `"version": "4.14.0"`, `"schema_version": 6`, `"migrations_head": "006_carries.sql"`.
- `gate_run()` → `"ready": true`.
- `package_verify()` → `"verified": true`, `"digest": "002f2702a1fcb5e7680a40efdae45ba1f61361e8d623917c99bcec7dafec4d0d"`, `"review_current": true`.
- Totals: `progress-entry` `total: 38`; `wbs-item` `total: 4`; `trace-edge` — `entity_query` refuses
  it (`entity type 'trace-edge' is write-only (composite key, no id column) — writable via
  entity_upsert; query edges via trace_query`), so the line count: `trace_edges.jsonl` = **30**.
- `prompts/*.md` (sorted, 18): `README.md, defect-triage.md, drift-register.md, generate-report.md,
  integrity-check.md, loop-guard.md, loop-iteration.md, orient-resume.md, package-onboarding.md,
  phase-close.md, progress-sync.md, project-kickoff.md, register-liveness.md, release-close-out.md,
  replan-deferred.md, skill-promote.md, slice-kickoff.md, slice-review.md`.
- `readiness_check("package")` → `deferred-work-reviewed` `"status": "pass"`, `"entities": []`,
  `population {"table": "deferred_work", "rows": 0}`, `"omitted": {"entity_type": "deferred-work",
  "reason": "The lab tracker defers no work: every slice is in scope for its phase."}`;
  `deferred-work-carried` `"status": "pass"`, `"entities": []`, the same `omitted`, its note ending
  `— no deferred_work rows, and the family's omission is recorded: a deliberate zero`.
- `package_close()` → `{"ok": true, "package": "package"}`. `git status --short` empty.

**2. Step 2 — the retired library and the note v5 (plan 116).** Scratch target `<scratch>/b22/target`,
empty before the call (`[]`), no `CLAUDE.md`, no pointer file.

2.1 `handoff_emit(<target>)` (plain) →
- `"written": [".mcp.json", "CLAUDE.md"]`
- `"project_prompts": ["project-kickoff.md"]`
- `prompt_library.leftover_stale_stock` — 16 entries:
  `defect-triage.md 4.5.0`, `drift-register.md 4.5.0`, `generate-report.md 3.0.0`,
  `integrity-check.md 4.9.0`, `loop-guard.md 4.4.0`, `loop-iteration.md 4.14.0`,
  `orient-resume.md 4.11.0`, `package-onboarding.md 4.7.0`, `phase-close.md 4.1.0`,
  `progress-sync.md 4.7.0`, `register-liveness.md 4.14.0`, `release-close-out.md 4.1.0`,
  `replan-deferred.md 4.9.0`, `skill-promote.md 4.4.0`, `slice-kickoff.md 4.5.0`,
  `slice-review.md 4.7.0` — each shaped `{"file": "prompts/<name>.md", "matches": "<release>"}`.
- `"leftover_customized": []`, `"retired": []`; `diverged_stale_stock: [{"file": "prompts/README.md", "matches": "4.14.0"}]`.
- Warnings (verbatim):
  - `1 stock prompt(s) are STALE-STOCK — byte-equal to an older release's stock, never customised: re-run with refresh_stock=true to update them safely (customised files are never touched by refresh)`
  - `16 retired stock prompt(s) remain in <package>/prompts/, byte-equal to a shipped release (the scenarios are the plugin's /tamheed:<name> skills since v5.0.0): re-run with refresh_stock=true to delete them safely (defect-triage.md, drift-register.md, generate-report.md, integrity-check.md, loop-guard.md, loop-iteration.md, orient-resume.md, package-onboarding.md, phase-close.md, progress-sync.md, register-liveness.md, release-close-out.md, replan-deferred.md, skill-promote.md, slice-kickoff.md, slice-review.md)`
  - `1 confirmed feedback row(s) not yet reported upstream (FB-002) — entity_export("feedback.json", args={"type": "feedback"}) and QUOTE its envelope and rows in your findings (exports are point-in-time and may be untracked in your git); set each row Reported once it has left`
- `prompts/*.md` after the plain emit: the same 18 names — **a plain emit deleted nothing**.

2.2 `handoff_emit(<target>, refresh_stock=true)` →
- `"written": []`, `"unchanged": [".mcp.json", "CLAUDE.md"]`
- `prompt_library.retired`: the sixteen `prompts/<name>.md` paths listed above
- `"refreshed": ["prompts/README.md"]`, `"leftover_stale_stock": []`, `"leftover_customized": []`
- Warnings (verbatim): `1 stale-stock prompt(s) refreshed to the current template (refresh_stock)`;
  `16 retired stock prompt(s) deleted (refresh_stock) — the scenarios are the plugin's /tamheed:<name> skills (defect-triage.md, … slice-review.md)`; the `FB-002` warning.
- `prompts/*.md` → `["README.md", "project-kickoff.md"]`; deleted set = exactly the sixteen;
  `project-kickoff.md` sha256 unchanged (`true`). **No STOP condition.**
- Refreshed `README.md` first line: `# How to use this folder — the `package` prompt guide (tamheed v4.14.0)`;
  the line containing `Which skill, when`: `## Which skill, when`.

2.3 `<target>/CLAUDE.md` (sha256 `0a79f83f…b265`):
- Marker line: `<!-- tamheed:note v5 -->` (closing `<!-- /tamheed:note -->`).
- The sentence naming `tamheed:package-writes`: `The HOW of every write, read and git crossing is
  the plugin's `tamheed:package-writes` skill — `tamheed:reading-the-record` before citing a row,
  `tamheed:operator-interview` at every STOP, `tamheed:test-evidence` / `tamheed:measurement-evidence`
  / `tamheed:ci-evidence` behind every verdict (they load on relevance; this table stays here because
  it is mandatory).`
- The sentence containing `dirties the tree AFTER it`: `Every store write (`entity_upsert`,
  `progress_update`, `audit_record`, `work_bind`, `package_verify(record=true)`, `package_close`)
  FLUSHES `data/*.jsonl`, and `export_html` / `handoff_emit` write package files beside it —
  `work_bind` records a commit and dirties the tree AFTER it, so the tree is dirty again the moment
  you finish recording: run `git status --porcelain -uall` immediately before ANY branch operation
  — never a memory of having committed.`
- Heading `### Recording obligations (mandatory — unrecorded work is drift)`; 12 `|`-rows counting
  the header (11 obligations; see N-3).
- `grep -c 'Tool cheat-sheet'` → `0`; `grep -c 'tamheed:note v4'` → `0`.
- The note also carries the one lesson line (`LL-004`) and `Skills distilled from lessons:
  `boundary-semantics` [project] — auto-loaded where present (project: .claude/skills/; user:
  ~/.claude/skills/).`
- `handoff_emit(<target>)` once more → `"written": []`, `"unchanged": [".mcp.json", "CLAUDE.md"]`,
  `prompt_library.unchanged: ["prompts/README.md"]`, `retired: []` — **byte-stable**.

2.4 `readiness_check("package")` → `prompt-ids-resolve` `"status": "pass"`, `"entities": []`,
`"in_code_spans": ["prompts/project-kickoff.md:4 -> DEF-090", "prompts/project-kickoff.md:4 -> SL-007"]`,
`population {"table": "prompts/*.md", "rows": 1, "scoped": false, "unit": "files"}`.
`package_close()` → ok.

**3. Step 3 — `carries` on a scratch package (plan 113).** `srv.PACKAGE_ROOT` = `<scratch>/b22/carryroot`.
- `package_create("carry", "Carry", "rnd")` → ok (`prompt_library.emitted: ["prompts/README.md"]` — the
  README-only library).
- Seed upsert `PH-1` (Approved), `SL-001` (Approved, `phase_id: PH-1`), `DW-001` (`severity: low`,
  `activation_trigger: "when X"`, `lifecycle_status: Activated`), `WBS-1` (`slice_id: SL-001`) →
  `"applied": 4`, all four `ok`.

3.1 `readiness_check("package")` → `deferred-work-carried` `"status": "fail"`, `"entities": ["DW-001"]`,
note: `an Activated row is work only while an OPEN wbs-item `carries` it (the edge is written with the
WBS rows in the activating batch; Review counts as open): listed rows have no open carrier — every
carrier Implemented means the row is Done (close it); no carrier at all means bind one or judge the row`;
`deferred-work-reviewed` `"status": "pass"`, `"entities": []` (Activated is not listed).

3.2 `entity_upsert([{"type": "trace-edge", "from_id": "DW-001", "to_id": "WBS-1", "relation": "carries"}])`
→ **REFUSED**: `"ok": false, "applied": 0, "error": "batch rolled back — one or more items violated constraints"`,
item error: `relation 'carries' does not allow deferred-work -> wbs-item (DW-001 -> WBS-1); allowed from:
wbs-item; allowed to: deferred-work — use 'relates_to' for an untyped association`.

3.3 `entity_upsert([{"type": "trace-edge", "from_id": "WBS-1", "to_id": "DW-001", "relation": "carries"}])`
→ `"ok": true, "applied": 1`. `readiness_check` → `deferred-work-carried` `"status": "pass"`, `"entities": []`.
`trace_query("DW-001", direction="in")` → `{"edges": [{"from": "WBS-1", "to": "DW-001", "relation": "carries"}], "count": 1}`.

3.4 `WBS-1` (full row read back via `entity_query`, `lifecycle_status` Draft → Implemented) →
`"ok": true`, `changed_columns: [{"column": "lifecycle_status", "old_len": 5, "new_len": 11}]`.
`readiness_check` → `deferred-work-carried` `"status": "fail"`, `"entities": ["DW-001"]` again.
`gate_run()` → `"ready": false` — G-REL `pass` (`mistyped: []`), G-SET `fail` on nine absent
Always families, all other gates `pass` (see N-1). `package_close()` → ok. `PACKAGE_ROOT` switched
back to the fixture; nothing in this step touched the fixture.

**4. Step 4 — the corrected arithmetic and the fixture's advisories (plans 112, 113, 107).**
4.1 `plugins/tamheed/skills/register-liveness/SKILL.md` (read, not edited):
- Frontmatter line 5: `disable-model-invocation: true`.
- Step 11's sentence containing `deferred-work-carried`: `**Finished activations**
  (`deferred-work-carried`): an Activated row whose every carrier is Implemented, or that no
  `wbs-item` carries at all — put each to the operator: close it Done (the work landed), or bind
  the item that carries it.`
- Step 15's sentence containing `removes NOTHING`: `The arithmetic (the field measured it, v5):
  while ten or more unpinned Approved lessons exist the fill is always exactly ten, so unpinning or
  promoting a PINNED lesson removes exactly one line whatever its number (a high-numbered one
  displaces the tenth of the fill; a low-numbered one never enters) — and retiring or rejecting an
  UNPINNED lesson removes NOTHING, the fill simply refills.`

4.2 `package_open("package")`; `readiness_check("package")` →
- `lessons-note-budget` `"status": "pass"`, note `the always-loaded CLAUDE.md note renders 1 lesson line(s) against a curation ceiling of 20`.
- `deferred-work-reviewed` and `deferred-work-carried` — both `"status": "pass"`, `"entities": []`,
  `population.rows: 0`, both `"omitted": {"entity_type": "deferred-work", "reason": "The lab tracker
  defers no work: every slice is in scope for its phase."}`, both notes ending `the family's omission
  is recorded: a deliberate zero`.
- `feedback-unanswered` `"status": "pass"`, `"entities": []`, `population.rows: 2`.
- `package_close()` → ok; `git status --short` showed only the Step 2 `prompts/` changes (the idle
  round-trip wrote nothing).

**5. Step 5 — close the beat.** `package_open("package")`;
`progress_update([{"entry": <note>, "event_type": "note", "actor": "agent:lab-beat-22"}])` →
`{"ok": true, "ids": ["PE-039"]}`. The note (verbatim):

> Beat 22 (plan 118, the v5.0.0 continuation), opened at schema_version 6 (migration 006 applied at connect; package_migrate not run). THE RETIRED LIBRARY (plan 116): a plain handoff_emit into a scratch target named the sixteen stock scenarios under prompt_library.leftover_stale_stock, kept project_prompts ['project-kickoff.md'] and deleted nothing; handoff_emit(refresh_stock=true) reported retired (16 paths), refreshed ['prompts/README.md'] and warned '16 retired stock prompt(s) deleted (refresh_stock) — the scenarios are the plugin's /tamheed:<name> skills'; the folder now holds README.md and project-kickoff.md (unchanged), and the refreshed guide carries '## Which skill, when'. THE NOTE (plan 116): the scratch CLAUDE.md reads '<!-- tamheed:note v5 -->' (tamheed:note v5), names 'tamheed:package-writes', keeps the Recording obligations table, drops the tool cheat-sheet, and its flush sentence says 'work_bind records a commit and dirties the tree AFTER it'; a re-emission wrote nothing (CLAUDE.md unchanged). CARRIES (plan 113), on a scratch package outside the fixture: with DW-001 Activated and no carrier, deferred-work-carried listed DW-001 (status fail, entities ["DW-001"]); the reverse edge was refused - 'relation 'carries' does not allow deferred-work -> wbs-item (DW-001 -> WBS-1)'; WBS-1 carries DW-001 emptied the list; WBS-1 set Implemented listed DW-001 again - the finished activation is visible. G-REL passed the edge (that scratch package's gate_run read ready false on G-SET alone: a bare package lacks the Always families). THE ARITHMETIC (plan 112): register-liveness step 15 now says retiring or rejecting an UNPINNED lesson removes NOTHING, the fill simply refills; here lessons-note-budget passes at 1 lesson line against the ceiling of 20. THE OMISSION (plans 107/113): deferred-work-reviewed and deferred-work-carried both pass over the recorded deferred-work omission - a deliberate zero; no DW- row was written to this package.

- `export_html()` → `"ok": true`, `"bytes": 181078`, `csv.emitted: ["csv/progress_entries.csv"]`, `removed: []`, `unowned: []`, `diverged: []`.
- `gate_run()` → `"ready": true`.
- `package_verify()` → `"verified": true`, `"foreign": []`, `"foreign_csv": []`, `"review_current": true`,
  `"files": 28`, `"digest": "17e9aebeb78778cb5ebaaa1ed71b68fc02e2b3559220786fdb5180af026fbe24"`.
- `package_close()` → ok. `data/.lock` exists → `false`.

### Mechanism → observed

| Plan | Mechanism | Verdict |
|---|---|---|
| 116 | A plain `handoff_emit` names the sixteen retired scenarios under `leftover_stale_stock` (each with its matching release) and warns `16 retired stock prompt(s) remain … refresh_stock=true` | **observed** (step 2.1) |
| 116 | A plain emit deletes nothing: all 18 files still on disk; `retired: []` | **observed** (step 2.1) |
| 116 | `refresh_stock=true` deletes exactly the sixteen (`retired`, `16 retired stock prompt(s) deleted (refresh_stock)`), leaves `project-kickoff.md` byte-identical | **observed** (step 2.2) |
| 116 | The guide is refreshed (`refreshed: ["prompts/README.md"]`) and carries `## Which skill, when` | **observed** (step 2.2) |
| 116 | The note is v5 (`<!-- tamheed:note v5 -->`, `tamheed:package-writes` named, `dirties the tree AFTER it`, obligations kept, no cheat-sheet, no v4 marker) and byte-stable on re-emission (`written: []`) | **observed** (step 2.3) |
| 113 | An Activated `DW-001` with no carrier is listed by `deferred-work-carried` (`entities: ["DW-001"]`) | **observed** (step 3.1) |
| 113 | The reverse edge is refused: `does not allow deferred-work -> wbs-item` | **observed** (step 3.2) |
| 113 | `WBS-1 carries DW-001` drops it from the list; `trace_query` shows the one `carries` edge | **observed** (step 3.3) |
| 113 | The carrier set `Implemented` re-lists `DW-001` — the finished activation is visible; G-REL passes the edge (scratch `ready` false on G-SET alone — N-1) | **observed** (step 3.4) |
| 112 | Step 15's arithmetic is quoted: an UNPINNED retirement `removes NOTHING` | **observed** (step 4.1) |
| 107/113 | The recorded `deferred-work` omission reads as `a deliberate zero` for BOTH `deferred-work-reviewed` and `deferred-work-carried` | **observed** (steps 1, 4.2) |

**Every mechanism the plan names fired. No row reads `not observed`.**

### No hollow assertion: the seven new checks, backup vs fixture

Every `cmd` was run from a driver that loads the seven appended entries from `evals/evals.json` and
calls `subprocess.run` in list form (mirroring `run_evals`), once with `{case_dir}/package` replaced
by the Step 1 BACKUP (`<scratch>/b22/backup`) and once against the fixture. **No needle was
narrowed**; all seven are verbatim as plan 118 gives them.

| # | Check | Backup exit | Backup output | Fixture exit | Fixture output |
|---|---|---|---|---|---|
| 1 | The sixteen retired stock scenarios are gone from the fixture's prompts folder (plan 116). | **1** | `present (should be absent) in: loop-guard.md` | 0 | `absent` |
| 2 | The fixture's prompt guide is the v5 guide: it maps situations to skills (plan 116). | **1** | `'Which skill, when' NOT found in <backup>/prompts/README.md` | 0 | found in `…/prompts/README.md` |
| 3 | The tool deleted the leftovers only on refresh_stock, and the note quotes the count (plan 116). | **1** | `'deleted (refresh_stock)' not found` | 0 | `progress_entries.jsonl:39` |
| 4 | The note the tool wrote is v5 and its flush sentence names the mechanism (plan 116). | **1** | `'dirties the tree AFTER it' not found` | 0 | `progress_entries.jsonl:39` |
| 5 | A work item carried an activated deferred row and the advisory watched the carrier close (plan 113). | **1** | `'deferred-work-carried listed DW-001' not found` | 0 | `progress_entries.jsonl:39` |
| 6 | The carries relation is typed: the reverse direction was refused (plan 113). | **1** | `'does not allow deferred-work -> wbs-item' not found` | 0 | `progress_entries.jsonl:39` |
| 7 | The note-budget step states the field's arithmetic, and the note quotes it (plan 112). | **1** | `'removes NOTHING' not found` | 0 | `progress_entries.jsonl:39` |

Seven of seven fail on the backup and pass on the fixture. `evals/evals.json` does NOT round-trip
byte-identically through `json.dumps` (the working tree is CRLF), so the seven entries were inserted
as text after the last `lab-tracker` assertion in the neighbouring entries' 2-space style, line
endings preserved; `git diff --stat` → `87 insertions(+)`, no deletions. Count **88 → 95**. The F-6
grep in plan 118's Status holds **for `evals.json`**: no pre-existing assertion names a deleted
prompt, and the three `grep-file` needles on `prompts/README.md` stay green (95/95). It did not
reach `tests/` — see F-10.

### Verification commands

- `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`
  (`G-IDS … G-REL` all `pass`; `audit_evidence=evidenced:4/narrated:0/ungraded:1`).
- `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → 95 `pass`,
  `PASS  lab-tracker`, `1 case(s) checked, 0 failed, 0 skipped`.
- `python check.py` → **`CHECK FAILED: exit 1, expected 0`** at the `suites` gate:
  `tests/test_eval_runner.py` `FAIL: test_pkg_check_grep_tree` — `AssertionError: 1 != 0 :
  'gate_run' not found` (`Ran 9 tests … FAILED (failures=1)`). check.py stops at the first failure,
  so every other stage was run individually on the same tree: the six suites before it `OK`
  (16, 9, 173, 17, 9, 39 tests); `tests/test_scratch_diff.py` and `tests/test_check_lints.py` exit 0;
  `python check.py lint` → `ALL CHECKS PASSED`; `python check.py canonical` → `ALL CHECKS PASSED`;
  `python check.py evals` → `3 case(s) checked, 0 failed, 6 skipped` / `ALL CHECKS PASSED`.
  **The single red test is F-10** — a plan/test collision with no in-scope fix; not improvised.

### Findings

Numbered after `F-9`, beat 21's finding.

**F-10 (methodology, HIGH for the release gate — a unit test reads the files this beat deletes).**
`tests/test_eval_runner.py::test_pkg_check_grep_tree` (lines 92–100) points `grep-tree-present` at
`evals/sample-results/lab-tracker/package/prompts` with the needle `gate_run` and requires exit 0.
In the Step 1 backup `gate_run` occurs in 13 of the 16 retired stock scenarios (`defect-triage`,
`drift-register`, `integrity-check`, `loop-guard`, `loop-iteration`, `orient-resume`,
`package-onboarding`, `phase-close`, `progress-sync`, `release-close-out`, `replan-deferred`,
`slice-kickoff`, `slice-review`) and in neither survivor (`README.md`, `project-kickoff.md`). Plan
118's deletions — the beat's purpose — therefore turn the test red. This is the F-6 class (a
recorded check the beat falsifies) in a file the plan puts OUT of scope (`tests/**`): the plan's
F-6 grep covered `evals.json` and `lab/scenario.md` but never reached `tests/`. `grep -rn
lab-tracker tests/ evals/pkg_check.py evals/run_evals.py check.py | grep -i prompt` → this test is
the **only** reader of the fixture's `prompts/` folder. Nothing was edited to hide it: the tests were
not touched, the deletions were not reverted, and the surviving guide was not hand-edited (that would
make it "customized" and break the byte-equal proof).
**Reviewer's one-line fix:** re-aim the needle at a string the 5.0.0 guide carries — e.g.
`tamheed:stock-merged` or `Which skill, when` (both present only in `prompts/README.md`); the
test's `grep-tree-absent` half keeps discriminating with the same needle.
**Recipe amendment:** a beat that deletes or rewrites fixture files greps `tests/` (not only
`evals.json` and `lab/scenario.md`) for readers of those paths before dispatch.
