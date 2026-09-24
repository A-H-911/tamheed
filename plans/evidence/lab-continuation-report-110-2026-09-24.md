# Lab continuation report — beat 21, v4.14.0 RC (plan 110, 2026-09-24)

> The execution agent's report from `lab/scenario.md` beat 21 (the findings_30 continuation:
> `readiness_check` following its own doctrine — an empty slice is not ready, and the rules that
> could not discriminate are named; the three honesty fixes — the recorded omission read back as a
> deliberate zero, the pointer warning that says what it did, the empty unanswered fold that says
> it is empty; and the vacuous `expect_unchanged` refused), archived **verbatim** below the header.
> Context: an INCREMENTAL real-agent session (`actor: agent:lab-beat-21`) against the recorded
> `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plans-106–109 tree at `main` `e0661cc`), **seven** scripts run
> from the worktree root with `PYTHONIOENCODING=utf-8` (eight `package_open` calls: six scripts
> that open and close cleanly, one read-only probe, and the first Step 1 script, which crashed
> after its open — see **N-2**), `data/.lock` absent before the first and after the last. Files touched = the fixture (`data/` —
> `acceptance_criteria.jsonl`, `audit_verdicts.jsonl`, `wbs_items.jsonl`, `progress_entries.jsonl`;
> `csv/` — the four matching exports; `review.html`) + `evals/evals.json` (seven appended
> assertions on the `lab-tracker` case, 81 → 88; **no pre-existing entry was edited**) +
> `lab/scenario.md`, `lab/README.md` + this report. No file under `plugins/`, `tests/`, `check.py`,
> `evals/pkg_check.py`, `CHANGELOG.md`, `plans/README.md`, any version stamp or any other fixture
> was edited. **Zero** hand edits of a `data/`, `csv/`, `exports/` or `review.html` file: the
> fixture changed **only** through the tools. No prompt file was edited (the fixture's
> `prompts/register-liveness.md` is stale-stock and was read, never written). No registry-sync and
> no migration: `package_migrate` was NOT run. No `DW-` row was written. All three verification
> commands green (`pkg_check gates` `ready=True`, `run_evals` lab-tracker **88/88** — 81 before the
> beat, +7 — `check.py` `ALL CHECKS PASSED`). A full `package/` backup was taken to
> `<scratch>/b21/backup` before the first open; nothing was restored from it, and it is the tree
> every new assertion was proved to FAIL against.
>
> **Deviations from the plan's steps.** None that changed a step's substance. Four notes:
>
> **N-1 — no assertion needle was narrowed.** All seven `cmd`s were run verbatim as the plan gives
> them, against the backup first; all seven exit non-zero there and 0 against the fixture. Nothing
> was hollow, so nothing was adapted. One wording observation only: assertion 3's `check` text says
> "carries a Met verdict" while its `cmd` counts the slice binding (`--col slice_id=SL-003`). It is
> not hollow (the backup has zero ACs bound to `SL-003`, `count=0`), but the *verdict* itself is
> proved by the tool log (`audit_record` → `AV-006`) and by `acs-met` moving to `pass`, not by that
> command. Run verbatim as the plan gives it.
>
> **N-2 — a stale `data/.lock` was hand-deleted once, before any write.** The first Step 1 script
> crashed on a *reporting* line of the agent's own driver (indexing `gate_run`'s `gates`, which is a
> dict, as a list) after `package_open` and before any `finally`, leaving the lock held by a dead
> process. The lock file was deleted by hand rather than journaling a `FORCED lock removal` through
> `package_unlock(confirm=true)`, which would have written a progress entry the plan does not ask
> for. **No store file was touched**: the crash happened after two read-only calls, and the
> re-run's full open → read → `package_close` produced `git status --short` **empty** — an idle
> round-trip with zero diff, which is the mechanical proof the store was untouched. Every
> subsequent script wraps its body in `try/finally`.
>
> **N-3 — `handoff_emit` created an untracked `package/CLAUDE.md`; it was removed, not committed.**
> Step 3.2's root file imports `@package/CLAUDE.md`, so the first emission *built the managed span
> inside the fixture* — `written` names it. That file is **not** part of the canonical store
> (`package_verify` → `files: 28`, `foreign: []`, `foreign_csv: []` with it present), no sample
> package in the repository has ever carried a committed `CLAUDE.md` (`git ls-files` → none), and
> its body embeds this run's **absolute worktree path** twice, which would make the fixture
> machine-specific. The lab's own stated policy settles it — `lab/README.md`, "The honesty limit":
> *"`handoff_emit` writes machine-specific absolute paths (… the package root in the `CLAUDE.md`
> note) — by design … An emitted target is therefore never committed as a fixture: beats emit to a
> scratch target and **quote the note verbatim in their evidence report**"*. What beat 21 discovered
> is that the emitted target is not the only place the note can land: a root file importing
> `@package/CLAUDE.md` makes the *package itself* the emission site. It was deleted, and its body
> is described in the log below instead. See **F-9**.
>
> **N-4 — one clause of `scenario.md`'s Pass bar was amended, not only appended.** The plan scopes
> `lab/scenario.md` to "append beat 21", but the Pass bar asserted "`SL-003` is Implemented-by-force
> and deliberately empty, so its scoped `acs-met`/`wbs-done` read `indeterminate` by design" — a
> sentence the beat the plan *mandates* falsifies. The clause now reads "was deliberately empty
> until beat 21 … since beat 21 they discriminate and `SL-003` reads ready". This is the F-6 class
> of collision (a record the beat falsifies) in prose rather than in an eval predicate; the
> alternative was to ship a false line. Flagged for the reviewer rather than done silently.

## Tamheed v4.14.0 lab continuation — beat 21 — execution report

### Numbered tool-call log (in-process handler calls + verbatim results)

**Drift check.** `git log --oneline -1` → `e0661cc docs(plans): plan 110 - lab beat 21's executor
plan (dry-run and F-6 grep cited)` — the commit the reviewer named.
`python plugins/tamheed/server/tamheed_server.py --selftest` → `mcp sdk: ok (1.27.2) — 19/19 tools
registered`. `package_migrate` was NOT run.

**1. Step 1 — baseline and backup.** `package/` copied to `<scratch>/b21/backup` before any open
(no `data/.lock` in the source or the copy; 28 `data/*.jsonl` files).

`server_info()` before the first open:

```json
{"ok": true, "version": "4.13.0",
 "package_root": "<worktree>/evals/sample-results/lab-tracker",
 "open_package": null, "package": null,
 "migrations_head": "005_feedback.sql", "schema_version": 5}
```

`gate_run()` → `ready: true`; every gate `pass` (`G-IDS`, `G-DEC-STATUS`, `G-REQ-SRC`, `G-TRACE`,
`G-SET`, `G-PROGRESS`, `G-COMPLETE`, `G-REL`), with `audit_evidence`
`evidenced: 3 / narrated: 0 / ungraded: 1` (`AV-005`).

`package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "a2fc169b717c03c4e59be0b3452c6b2783236de188c610c575a1400cdab59b32",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

Family totals: `progress-entry` **37**, `acceptance-criterion` **5**, `wbs-item` **3** — and the
ids read `WBS-1..WBS-3`, `AC-001..AC-005`, `DEF-001..DEF-005`, `SL-001..SL-003`, `FB-001`/`FB-002`.
Requirements read `FR-001..FR-007` + `NFR-001` (the plan's "Current state" says `FR-001`–`FR-004`;
see **F-10** — no step depends on it).

`readiness_check("slice", id="SL-003")` — the untouched slice (STOP condition checked: it is **not**
`ready: true`):

```json
{"ok": true, "scope": "slice", "id": "SL-003", "ready": false,
 "indeterminate": ["acs-met", "wbs-done"], "human_required": []}
```

and its two blocking rules, verbatim:

```json
{"rule": "acs-met", "severity": "blocking", "status": "indeterminate", "entities": [],
 "note": "ACs bound to this slice whose latest verdict is not Met — no active acceptance criteria in this scope; this rule cannot discriminate (bind ACs to this slice via slice_id)",
 "population": {"table": "acceptance_criteria", "rows": 0, "scoped": true},
 "discriminating": false}
```

```json
{"rule": "wbs-done", "severity": "blocking", "status": "indeterminate", "entities": [],
 "note": "open work items in this slice — no work items in this scope; this rule cannot discriminate (create WBS- rows with slice_id)",
 "population": {"table": "wbs_items", "rows": 0, "scoped": true},
 "discriminating": false}
```

`readiness_check("slice", id="SL-001")` → `ready: true`, `indeterminate: []`; all five rules `pass`
with `acs-met` and `wbs-done` at scoped `rows: 1`.

`package_close()` → `{"ok": true, "package": "package"}`; no lock; `git status --short` **empty**
(the idle round-trip's zero diff — the invariant, and N-2's proof).

**2. Step 2.2 — populating the slice through the tools.** One batch:

```json
{"ok": true, "applied": 2,
 "items": [{"index": 0, "ok": true, "id": "WBS-4"},
           {"index": 1, "ok": true, "id": "AC-006"}]}
```

(`WBS-4`: `title` `export header: the drift check`, `slice_id: "SL-003"`, `lifecycle_status:
"Implemented"`. `AC-006`: `title` `the export header round-trips`, `requirement_id: "FR-001"`,
`slice_id: "SL-003"`, `lifecycle_status: "Approved"`.) Then the verdict:

```json
{"ok": true, "ids": ["AV-006"]}
```

(`ac_id: "AC-006"`, `verdict: "Met"`, `evidence: "lab beat 21: the export header round-trip test"`,
`verified_by: "agent"`, `verification_method: "inspection"`, `against_commit: "e0661cc"`.) Nothing
was refused, so the plan's hedge did not apply.

**3. Step 2.3 — the flip.** `readiness_check("slice", id="SL-003")`:

```json
{"ok": true, "scope": "slice", "id": "SL-003", "ready": true, "indeterminate": [],
 "human_required": []}
```

with the two rules now discriminating (and the `discriminating` key **absent**, as it is only
emitted on an indeterminate rule):

```json
{"rule": "acs-met", "severity": "blocking", "status": "pass", "entities": [],
 "note": "ACs bound to this slice whose latest verdict is not Met",
 "population": {"table": "acceptance_criteria", "rows": 1, "scoped": true}}
```

```json
{"rule": "wbs-done", "severity": "blocking", "status": "pass", "entities": [],
 "note": "open work items in this slice",
 "population": {"table": "wbs_items", "rows": 1, "scoped": true}}
```

`readiness_check("slice", id="SL-001")` → `ready: true`, `indeterminate: []`, rule statuses
`{"acs-met": "pass", "wbs-done": "pass", "defects-closed": "pass", "defects-minor": "pass",
"execution-plan-approved": "pass"}` — **unchanged** from Step 1. `gate_run()["ready"]` → `true`.

The whole of plan 106 is in the pair: the note the indeterminate rule already carried said *this
rule cannot discriminate*, and the verdict now agrees with it instead of reporting `ready: true`
over two rules that measured nothing.

**4. Step 3.1 — the recorded omission is a deliberate zero.** `readiness_check("package")` →
`ready: false` (by design; the scenario's deliberately-open items). Its
`deferred-work-reviewed` entry, verbatim:

```json
{"rule": "deferred-work-reviewed", "severity": "advisory", "status": "pass", "entities": [],
 "note": "activation triggers are prose — a human judges whether each fired: Open (has the trigger fired?) and Scheduled (has the date come?) rows are listed; an Activated row is work now (its WBS rows carry it) and Done / Won't-do are closed — a judged row leaves this list by moving to one of those states — no deferred_work rows, and the family's omission is recorded: a deliberate zero",
 "population": {"table": "deferred_work", "rows": 0, "scoped": false},
 "omitted": {"entity_type": "deferred-work",
             "reason": "The lab tracker defers no work: every slice is in scope for its phase."}}
```

Three things at once: the pass is over a measured `rows: 0`; the `omitted` block names the family
and reads the recorded reason back; and the note says which states are listed (`Open` and
`Scheduled` — plan 107's population fix) and that the zero is **deliberate**, not silence. **No
`DW-` row was written.** The full rule roster at package scope:

```json
{"decisions-approved": "pass", "adrs-approved": "pass", "acs-met": "fail",
 "defects-closed": "pass", "defects-minor": "waived", "risks-discharged": "pass",
 "deferred-work-reviewed": "pass", "open-questions-resolved": "fail",
 "execution-plans-approved": "pass", "requirements-wired": "pass",
 "decisions-look-architectural": "pass", "scope-changes-merged": "pass",
 "open-questions-overdue": "fail", "risk-liveness": "pass", "assumptions-current": "pass",
 "hypotheses-measurable": "indeterminate", "acs-slice-bound": "pass", "clarifications-open": "fail",
 "prose-ids-resolve": "pass", "prompt-ids-resolve": "pass", "lessons-confirmed": "fail",
 "lessons-superseded-binding": "pass", "waivers-open-ended": "fail", "feedback-unanswered": "pass",
 "lessons-note-budget": "pass"}
```

— exactly the scenario's Pass-bar set of deliberately-open items, nothing else.

**5. Step 3.2 — the pointer warning, twice.** In `<scratch>/b21/h1` (OUTSIDE the repo),
`CLAUDE.md` written with real newlines — `repr` of the file:
`'# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n'`.

`handoff_emit(<scratch>/b21/h1)` — call **#1**, `ok: true`, third warning verbatim:

```
C:\...\scratchpad\b21\h1\CLAUDE.md imports the package note (@package/CLAUDE.md) — the managed span lives at <worktree>\evals\sample-results\lab-tracker\package\CLAUDE.md and was rebuilt there; the root file was left untouched
```

`written: [".mcp.json", "<worktree>\\evals\\sample-results\\lab-tracker\\package\\CLAUDE.md"]`.

Call **#2**, the idle re-emission, `ok: true`, same position:

```
C:\...\scratchpad\b21\h1\CLAUDE.md imports the package note (@package/CLAUDE.md) — the managed span lives at <worktree>\evals\sample-results\lab-tracker\package\CLAUDE.md and is current there; nothing written; the root file was left untouched
```

`written: []`.

Mechanically checked on the joined warning lists:

```
#1 contains 'was rebuilt there'                 -> True
#1 contains 'is current there; nothing written' -> False
#2 contains 'was rebuilt there'                 -> False
#2 contains 'is current there; nothing written' -> True
```

The two texts are mutually exclusive and `written: []` on the second corroborates the claim: the
warning reports what the call **did**, not what the call might have done. (The other two warnings
are the fixture's known state and appear identically in both calls: `3 stock prompt(s) are
STALE-STOCK …` and `1 confirmed feedback row(s) not yet reported upstream (FB-002) …`.)

The managed span that call #1 built inside the package — deleted afterwards, see **N-3** and
**F-9** — opens with the `<!-- tamheed:note v4 -->` marker under `## Tamheed progress tracking`,
carries the recording-obligations table, the `LL-004` lesson line and the tool cheat-sheet, and
names the package root **by absolute path** twice.

**6. Step 3.3 — the empty fold says it is empty.** `export_html()` → `ok: true`, `bytes: 170623`.
Read back from disk:

```
review.html contains 'No reported feedback awaits an answer' -> True (count 1)
```

in context — the `empty` paragraph stands where the fold would have been, immediately before the
closed fold:

```html
</details><p class="empty" id="feedback-reported">No reported feedback awaits an answer.</p><details id="feedback-closed"><summary>Resolved or rejected (kept as evidence) (1 row)</summary>
```

This is the honest reading of beat 20's end state: `FB-001` is `Resolved` and `FB-002` is a
`local-tool` register that never reports, so the reported fold has no rows — and the page now
**says so** instead of rendering nothing and letting the reader guess whether the section was
skipped. `gate_run()["ready"]` → `true`.

**7. Step 4 — the vacuous assertion refused.** `entity_query("defect", id="DEF-005")`:

```json
{"id": "DEF-005",
 "title": "export header DRIFTS (see DEF-001 (fixed in SL-002); mock id `RISK-808`; score = (KPI-17_score * 0.25) + (KPI-10_score * 0.2))",
 "severity": "low", "lifecycle_status": "Open", "found_in": "SL-002", "fixed_by": null,
 "custom_attributes": "{\"lab\": \"beat 20\"}", "last_referenced": null}
```

(`title`, `severity` and `lifecycle_status` were copied programmatically from that row, never
retyped.) The item sent — `custom_attributes` named in `expect_unchanged` and **omitted from the
row**:

```json
{"type": "defect", "id": "DEF-005",
 "title": "export header DRIFTS (see DEF-001 (fixed in SL-002); mock id `RISK-808`; score = (KPI-17_score * 0.25) + (KPI-10_score * 0.2))",
 "severity": "low", "lifecycle_status": "Open",
 "expect_unchanged": ["custom_attributes"]}
```

```json
{"ok": false, "applied": 0,
 "error": "batch rolled back — one or more items violated constraints",
 "items": [{"index": 0, "ok": false, "id": "DEF-005",
   "error": "DEF-005: expect_unchanged names column(s) this item does not carry (custom_attributes) — an omitted column is preserved by the UPDATE, so naming it asserts nothing: drop it from expect_unchanged, or send it"}]}
```

Contains `does not carry` → **True**; contains `asserts nothing` → **True**. **REFUSED — the STOP
condition was not met.** Note the pairing with beat 20: there, the same shape was *accepted* with
`changed_columns: []`, and that acceptance was correct about the data (an omitted column really is
preserved) and wrong about the guard (the assertion could not fail). Plan 108 closes exactly that:
a guard that can only pass is refused with the remedy, so the caller either drops the name or
sends the column and gets a real check.

The same item with `"expect_unchanged": ["title"]` — a column it DOES carry:

```json
{"ok": true, "applied": 1,
 "items": [{"index": 0, "ok": true, "id": "DEF-005", "changed_columns": []}]}
```

`changed_columns: []` — accepted, nothing moved, and the assertion was real. `gate_run()["ready"]`
→ `true`.

**8. Step 5 — the refreshed sweep prompt, walked once.** Read from the **stock** body
`plugins/tamheed/prompts/register-liveness.md` (the fixture's copy is byte-different — stale-stock
— and NEITHER was edited). The new sentences, verbatim:

*Step 10 — Minor defects (`defects-minor`), the new opening:*

```
before framing ANY question for the operator, `entity_query(search="<DEF-id>")` across families — a ruling often lives in a decision, an AC or a scope change, never on the defect row (the field re-asked three questions whose answers were already recorded).
```

*Step 11 — Deferred work (`deferred-work-reviewed`), rewritten:*

```
the rule lists Open and Scheduled rows — the ones a human still judges. Read each activation trigger against current reality. Fired → say so and point the operator at the replan-deferred prompt (activation is a scope decision, not yours); once Activated the row is work — its WBS rows carry it — and leaves this list. Not fired → it is deliberately carried; nothing to write, and the row stays listed until it fires or is closed.
```

*Step 15 — Note budget (`lessons-note-budget`), the new arithmetic:*

```
EVERY pinned lesson plus an unpinned fill of the 10 highest-numbered Approved ones; past the curation ceiling (20 rendered lines) the rule names the rows that render beyond it — the promotion candidates. The arithmetic: unpinning removes a line only if the lesson's number is too low to re-enter the fill, so with N pinned lessons reaching 20 needs at least N - 10 removals, not one.
```

(Plan 108 also added step 7's `Name only columns the item CARRIES: an omitted column is preserved
by the store, so naming it asserts nothing and is refused; a one-token change is a `substitute`
item, which needs no re-fetch at all.` — the prose counterpart of Step 4's refusal. Recorded here
because the sweep's own instruction and the engine's refusal now say the same thing.)

`readiness_check("package")` for the steps the plan names — step 11 and steps 17–18:

- `deferred-work-reviewed` → `status: "pass"`, `omitted` naming `deferred-work` and its reason
  (quoted in full at **4** above): pass **and** omission-recorded.
- `prompt-ids-resolve` → `status: "pass"`, `entities: []`, `in_code_spans:
  ["prompts/project-kickoff.md:4 -> DEF-090", "prompts/project-kickoff.md:4 -> SL-007"]`,
  `not_well_formed: []`, `population: {"table": "prompts/*.md", "rows": 1, "scoped": false,
  "unit": "files"}`. Green because every id RESOLVES; the two phantoms are inert code spans
  (beat 19's fix), and the `rows: 1` population is the project's own prompt file — never a stock
  body.
- `feedback-unanswered` → `status: "pass"`, `entities: []`, `population: {"table": "feedback",
  "rows": 2, "scoped": false}`. Not vacuous: it measured both rows and excluded them by predicate
  (`FB-001` answered, `FB-002` a register), not by absence.

**9. Step 6 — the closing note, then the page.** ONE `progress_update` entry, `event_type: "note"`,
actor `agent:lab-beat-21` → `{"ok": true, "ids": ["PE-038"]}`. It was written **BEFORE**
`export_html`, and its last sentence says so, so the page that ships carries it. All six needles
were verified present in the note text **before** the write:

```
OK    'SL-003 read ready: false'
OK    'indeterminate: ["acs-met", "wbs-done"]'
OK    'is current there; nothing written'
OK    'No reported feedback awaits an answer'
OK    'asserts nothing'
OK    'a deliberate zero'
```

`export_html()` → `ok: true`, `bytes: 176339`, `csv.emitted: ["csv/progress_entries.csv"]`,
`diverged: []`, `removed: []`, `unowned: []`.

`gate_run()` → `ready: true`; `{"G-IDS": "pass", "G-DEC-STATUS": "pass", "G-REQ-SRC": "pass",
"G-TRACE": "pass", "G-SET": "pass", "G-PROGRESS": "pass", "G-COMPLETE": "pass", "G-REL": "pass"}`.

`package_verify()`:

```json
{"ok": true, "package": "package", "files": 28, "foreign": [], "foreign_csv": [],
 "review_current": true,
 "digest": "002f2702a1fcb5e7680a40efdae45ba1f61361e8d623917c99bcec7dafec4d0d",
 "recorded": null, "verified": true, "loadable": true, "dirty": [],
 "memory_matches_disk": true}
```

Closing totals: `progress-entry` **38** (37 + the one note), `acceptance-criterion` **6**,
`wbs-item` **4**, `audit-verdict` **6**. `package_close()` → `{"ok": true, "package": "package"}`.
No `data/.lock` remains.

### Mechanism → observed

| Plan | Mechanism | Verdict |
|---|---|---|
| 106 | The untouched `SL-003` reads `ready: false` with `indeterminate: ["acs-met", "wbs-done"]`, both rules `status: "indeterminate"`, `discriminating: false`, scoped `population.rows: 0` — the verdict now agrees with the note the rule already carried | **observed** (step 1, step 2.1) |
| 106 | Populating the slice — one `Implemented` `WBS-4` bound by `slice_id` and one `Approved` `AC-006` with an `audit_record` `Met` verdict — flips it to `ready: true`, `indeterminate: []`, both populations `rows: 1` | **observed** (steps 2.2, 2.3) |
| 106 | `SL-001` is untouched by the fix: `ready: true`, `indeterminate: []`, all five rules `pass`, before and after — the change discriminates rather than blanketing | **observed** (steps 1, 2.3) |
| 107 | `deferred-work-reviewed` passes over a measured `rows: 0` and SAYS the zero is deliberate, carrying the recorded omission's reason back in `omitted`; no `DW-` row was written | **observed** (step 3.1) |
| 107 | The rule's note names **Open and Scheduled** as the judged states (and Activated/Done/Won't-do as the exits) — the population fix | **observed** (step 3.1, step 5) |
| 107 | The pointer warning's two texts are mutually exclusive: `was rebuilt there` on the first emission, `is current there; nothing written` on the idle re-emission, corroborated by `written: []` | **observed** (step 3.2) |
| 107 | The review page renders `<p class="empty" id="feedback-reported">No reported feedback awaits an answer.</p>` instead of an empty fold | **observed** (step 3.3) |
| 108 | `expect_unchanged` naming a column the item does NOT carry is REFUSED — `does not carry` … `asserts nothing` — closing the guard beat 20 proved could only pass | **observed** (step 4) |
| 108 | The same item naming a column it DOES carry is accepted with `changed_columns: []` — a real assertion that happens to hold | **observed** (step 4) |
| 108 | The refreshed `register-liveness.md` steps 10, 11 and 15 carry their new sentences, and the three rules those steps read (`deferred-work-reviewed`, `prompt-ids-resolve`, `feedback-unanswered`) all read `pass` | **observed** (step 5) |

**Every mechanism the plan names fired. No row reads `not observed`.**

**Not exercised, by design.** `package_migrate` was not run (the plan forbids it; this batch adds
no family), no registry-sync was needed, `FB-001`/`FB-002` were left untouched as the plan directs,
no `DW-` row was written, and no prompt file was edited — `loop-iteration.md`, the other file plan
108 refreshed, is a stock body this beat has no step for and was left alone.

### No hollow assertion: the seven new checks, backup vs fixture

Every `cmd` was run twice — once with `{case_dir}/package` replaced by the Step 1 BACKUP
(`<scratch>/b21/backup`), once against the fixture. **No needle was narrowed**; all seven were run
verbatim as plan 110 gives them.

| # | Check | Backup exit | Backup output | Fixture exit | Fixture output |
|---|---|---|---|---|---|
| 1 | The empty slice read ready: false with both rules named, and the note quotes it (plan 106). | **1** | `'SL-003 read ready: false' not found` | 0 | `progress_entries.jsonl:38` |
| 2 | The slice was populated with a work item bound to it (plan 106). | **1** | `count=0` / `below required minimum 1` | 0 | `count=1` |
| 3 | The slice's criterion carries a Met verdict (plan 106). | **1** | `count=0` / `below required minimum 1` | 0 | `count=1` |
| 4 | The pointer warning told the truth on an idle re-emission, and the note quotes it (plan 107). | **1** | `'is current there; nothing written' not found` | 0 | `progress_entries.jsonl:38` |
| 5 | The recorded review page says when no reported feedback awaits an answer (plan 107). | **1** | `'No reported feedback awaits an answer' NOT found in <backup>/review.html` | 0 | found in `.../package/review.html` |
| 6 | A vacuous expect_unchanged was refused, and the note quotes the refusal (plan 108). | **1** | `'asserts nothing' not found` | 0 | `progress_entries.jsonl:38` |
| 7 | The deferred-work advisory read the recorded omission as a deliberate zero, and the note says so (plan 107). | **1** | `'a deliberate zero' not found` | 0 | `progress_entries.jsonl:38` |

Seven of seven fail on the backup and pass on the fixture. `evals/evals.json` round-tripped
byte-identically under `json.dumps(indent=2, ensure_ascii=False) + "\n"` before the append (checked
first), the seven entries were appended at the END of `lab-tracker`'s list, the count moved **81 →
88**, and **no pre-existing entry was touched** — unlike beat 20, no existing assertion collides
with this beat (the F-6 grep in plan 110's Status section, re-confirmed here: the only pre-existing
hit for any of this beat's words is assertion 34's `grep-present … indeterminate`, whose needle
this beat's writes can only add to, never remove).

### Findings

Numbered after `F-8`, the last of beat 20's findings.

**F-9 (methodology, MEDIUM — an emitted managed span inside the fixture).** Beat 21 is the first
beat whose `handoff_emit` root file imports `@package/CLAUDE.md`, so the emission built
`package/CLAUDE.md` **inside the recorded fixture** — a file no sample package has ever carried,
which `package_verify` correctly does not count (`files: 28`, `foreign: []`) and which embeds the
emitting machine's **absolute** package root twice. `lab/README.md`'s "honesty limit" already rules
that "an emitted target is … never committed as a fixture" — but it assumes the emitted target is
the *scratch* directory, and a root file importing `@package/CLAUDE.md` makes the package the
emission site, which the rule's wording does not reach. Committing it would make the fixture
machine-specific; leaving it untracked would leave a stray file in every future `git status`. It
was deleted and described in this report instead. **Recipe amendment:** a beat that points
`handoff_emit` at a root file importing the package note must say in the plan whether the managed
span it builds inside the package is part of the fixture (it should not be, while its body carries
absolute paths), and the executor should expect a new untracked `package/CLAUDE.md`. The deeper
observation for the engine: the managed span is the one tool-written file whose *content* is
machine-dependent, which is why it can never be an eval fixture the way `review.html` is.

**F-10 (observation, INFO — a plan-record inaccuracy).** Plan 110's "Current state" says
"Requirements `FR-001`–`FR-004`"; the fixture carries `FR-001`..`FR-007` + `NFR-001`. No step
depends on the count (`AC-006` binds to `FR-001`, which exists), so it is not a STOP — but the
plan's own instruction is "verify, do not assume", and this is what verifying found.

**F-11 (observation, INFO — the pair beat 20 and beat 21 make).** Beat 20's step 6 and beat 21's
step 4 send the *same shape* — a partial row naming an omitted column in `expect_unchanged` — and
get opposite verdicts, and both are right. Beat 20's acceptance was a true statement about the
**data** (an omitted column is preserved by the UPDATE, so it cannot drift); beat 21's refusal is a
true statement about the **assertion** (a predicate that cannot fail measures nothing). The two
beats read together are the whole of the distinction plan 108 draws, and the fixture now carries
both journal entries — the accepted one from beat 20 and the refusal from beat 21 — a few rows
apart. A guard whose only possible verdict is `pass` is the same defect class as an
`indeterminate` rule reported as `ready: true`, which is what plan 106 fixed in the same release:
**this batch fixed one bug twice, in two different surfaces.**

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
audit_evidence=evidenced:4/narrated:0/ungraded:1

$ python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker
... (the seven new checks among them, all `pass`)
PASS  lab-tracker
1 case(s) checked, 0 failed, 0 skipped

$ python check.py                       # backgrounded; the tree was not touched while it ran
ALL CHECKS PASSED
```

`run_evals` reports the `lab-tracker` case at **88** deterministic assertions, 88 `pass` (81 before
the beat, +7).

### Verbatim refusal text (the one the beat's note quotes from)

```
DEF-005: expect_unchanged names column(s) this item does not carry (custom_attributes) — an omitted column is preserved by the UPDATE, so naming it asserts nothing: drop it from expect_unchanged, or send it
```

### Verbatim engine-witness texts (the two the caller could not have written)

```
ACs bound to this slice whose latest verdict is not Met — no active acceptance criteria in this scope; this rule cannot discriminate (bind ACs to this slice via slice_id)
```

```
activation triggers are prose — a human judges whether each fired: Open (has the trigger fired?) and Scheduled (has the date come?) rows are listed; an Activated row is work now (its WBS rows carry it) and Done / Won't-do are closed — a judged row leaves this list by moving to one of those states — no deferred_work rows, and the family's omission is recorded: a deliberate zero
```

The first is the sentence the tool had been printing while returning `ready: true` — the engine
already knew it could not discriminate, and only the verdict disagreed. The second is a pass that
states its own basis: a measured zero plus a recorded omission, which is the only kind of empty
family a reader can trust.
