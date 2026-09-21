# Lab continuation report — beat 17, v4.10.0 RC (plan 083, 2026-09-21)

> The execution agent's report from `lab/scenario.md` beat 17 (the findings_26 continuation: the
> lost paragraph reported as a length drop, the half-finished supersession that keeps binding,
> the two refused unattended retirements and the engine's own retirement on the operator's word,
> the backticked phantom reported inert, the open-ended blanket waiver named, the empty family
> that measured nothing until its omission was recorded, the review page that says whether it is
> current, and the completed hand-merge that stops lagging), archived **verbatim** below the
> header. Context: an INCREMENTAL real-agent session (`actor: agent:lab-beat-17`) against the
> recorded `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plans-075–082 tree at `main` `37b6366`), nine scripts run from
> the repo root (one of them against a scratch copy, never the fixture), each opening and closing
> the package, `data/.lock` absent before the first and after the last. Files touched = the fixture (`data/` — `defects.jsonl`, `lessons.jsonl`,
> `omissions.jsonl`, `progress_entries.jsonl`; `csv/` — the four matching exports; `prompts/` —
> `register-liveness.md` refreshed and `README.md` accepted to current stock, both by tool;
> `review.html`) + `evals/evals.json` (twelve appended assertions on the `lab-tracker` case only)
> + `lab/scenario.md`, `lab/README.md` + this report. No file under `plugins/`, `tests/`,
> `check.py`, `evals/pkg_check.py`, `CHANGELOG.md`, `plans/README.md`, `evals/README.md`, any
> version stamp or any other fixture was edited. **Zero** hand edits of a `data/` file were made;
> the fixture changed only through the tools. The two prompt files rewritten BY HAND
> (`integrity-check.md`, `orient-resume.md`) were rewritten on a SCRATCH COPY outside the repo,
> as step 8 prescribes — the fixture's own copies of both are byte-unchanged stock. All three
> verification commands green (`pkg_check gates` `ready=True`, `run_evals` lab-tracker
> **56/56** — 44 before the beat, +12 — `check.py` `ALL CHECKS PASSED`). A full `package/` backup
> was taken to `<scratch>/backup-root/package` before script 1; nothing was restored from it, and
> it is the tree every new assertion was proved to FAIL against.
>
> **Deviations from the plan's steps.** One, and it was supplied by the reviewer mid-beat as an
> amendment to step 9 (finding **F-1** below): the fixture's `prompts/README.md` byte-matched no
> body in the bundled stock history, so `refresh_stock=True` refreshed only
> `prompts/register-liveness.md` and classified `README.md` `diverged_customized`. The amended
> procedure was followed exactly — both pre-conditions verified and quoted (step 9.2) before
> `handoff_emit(force=True)` was used (step 9.3). Every needle in the plan's proposed assertion
> block matched the verbatim text observed and was used **unchanged**; no needle was adapted.
> `evals/pkg_check.py`'s `grep-present --tables omissions` reads `omissions.jsonl` without
> trouble on both trees, so the plan's omissions fallback was not needed. `evals/README.md`
> states no assertion count for `lab-tracker` (its row is prose only, and it does not enumerate
> beat 16 either), so it was left untouched, as the scope line allows.

---

## Tamheed v4.10.0 lab continuation — beat 17 — execution report

### Numbered tool-call log (in-process handler calls + verbatim outcomes)

Drift check (repo root, nothing written):

0. `git log --oneline -1` → `37b6366 docs(plans): plan 083 - lab beat 17, the findings_26
   mechanisms (dispatch record)` — the commit the reviewer named when dispatching.
   `python plugins/tamheed/server/tamheed_server.py --selftest` →
   `mcp sdk: ok (1.27.2) — 19/19 tools registered`.

**Script 1 — Step 1: baseline and backup.**

1. Backup: `package/` copied to
   `<scratch>/backup-root/package` — before any tool call that writes.
2. `package_open("package")` → `ok`. `gate_run()` → **`ready: true`**, all eight gates `pass`:
   ```json
   {"G-IDS": "pass", "G-DEC-STATUS": "pass", "G-REQ-SRC": "pass", "G-TRACE": "pass",
    "G-SET": "pass", "G-PROGRESS": "pass", "G-COMPLETE": "pass", "G-REL": "pass"}
   ```
   `package_close()` → `ok`.
3. `package_verify("package")` → verbatim (projection):
   ```json
   {"verified": true,
    "digest": "7ab7df8bccc25a81060a4b88cdf6f5a806be73a7fbf83fc1520f88a74e609256",
    "review_current": null, "foreign": [], "foreign_csv": []}
   ```
   `review_current` is **`null`**, not `false`: the recorded `review.html` predates the
   plan-081 stamp, so there is no stamped digest to compare and the tool reports *unknown*
   rather than *stale*.
4. Totals: `progress-entry` **23**, `defect` **5**, `lesson` **2**, `waiver` **2**.
   `data/.lock` absent. `git status --short` empty after the idle open→close (the canonical
   round-trip is byte-stable, as `db/CANONICAL.md` requires).

**Script 2 — Step 2: a write says what it changed (plan 080).**

5. `LL-003` (OLD) and `LL-004` (NEW) are the next two free ids; both born `Proposed`.
   The shared opening of the two statements is **197 characters** — past the note's
   180-character window, so the two lines can render identically there. Lengths:
   OLD `statement` 326, NEW `statement` 677, NEW-minus-last-paragraph 467.
   `entity_upsert([OLD, NEW])` → `{"ok": true, "applied": 2, "items": [{"index": 0, "ok":
   true, "id": "LL-003"}, {"index": 1, "ok": true, "id": "LL-004"}]}`; statuses
   `{"LL-001": "Promoted", "LL-002": "Proposed", "LL-003": "Proposed", "LL-004": "Proposed"}`.
   Both are INSERTs, so neither item carries `changed_columns` — by design
   (`_changed_columns` runs only when there is a before-row).
6. NEW re-sent with its **last paragraph dropped** → verbatim:
   ```json
   {"index": 0, "ok": true, "id": "LL-004",
    "changed_columns": [{"column": "statement", "old_len": 677, "new_len": 467}]}
   ```
7. NEW re-sent **in full** → verbatim:
   ```json
   {"index": 0, "ok": true, "id": "LL-004",
    "changed_columns": [{"column": "statement", "old_len": 467, "new_len": 677}]}
   ```
8. NEW re-sent **unchanged** → verbatim:
   ```json
   {"index": 0, "ok": true, "id": "LL-004", "changed_columns": []}
   ```

**Script 3 — Step 3: the half-finished supersession, and the refusals (plan 075).**

Every write in this script re-sent the FULL row exactly as `entity_query("lesson", id=…)`
returned it (approval is not an edit: the handler refuses on any content drift). All nineteen
columns the query returned were accepted; **no key was refused as unknown**, so none was
dropped. The operator's word for every `operator_confirm` below is the one plan 083 gives;
`confirmed_by` takes LL-001's form, `operator:lab`.

9. **3.1 — approve OLD.** `entity_upsert([{…LL-003…, "lifecycle_status": "Approved",
   "operator_confirm": true, "confirmed_by": "operator:lab", "confirmed_at": "2026-09-21"}])`
   → verbatim:
   ```json
   {"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "LL-003",
     "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 8},
                         {"column": "confirmed_by", "old_len": 0, "new_len": 12},
                         {"column": "confirmed_at", "old_len": 0, "new_len": 10}],
     "next": "this lesson BINDS only once the always-loaded note is rebuilt - run handoff_emit in this same batch (the note is rebuilt by nothing else)",
     "lesson_audit": "PE-024"}]}
   ```
10. **3.2 — the UNATTENDED pointer.** OLD re-sent with `"superseded_by": "LL-004"` and **no**
    `operator_confirm` → **REFUSED**, verbatim:
    ```json
    {"ok": false, "applied": 0,
     "error": "batch rolled back — one or more items violated constraints",
     "items": [{"index": 0, "ok": false, "id": "LL-003",
       "error": "LL-003: pointing a BINDING lesson at a successor (approving that successor retires this one) is the OPERATOR's word, like approving it — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
    ```
    OLD after the refusal: `{"lifecycle_status": "Approved", "superseded_by": null}` — nothing
    was written.
11. **3.3 — the pointer, on the operator's word.** Same row with `"operator_confirm": true` →
    verbatim:
    ```json
    {"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "LL-003",
      "changed_columns": [{"column": "superseded_by", "old_len": 0, "new_len": 6}],
      "next": "LL-003 is still Approved, so it KEEPS BINDING: `superseded_by` is only a pointer. It is retired when its successor LL-004 is approved (the engine then sets it Superseded), or by setting lifecycle_status to Superseded on the operator's word (operator_confirm)"}]}
    ```
    OLD now: `{"lifecycle_status": "Approved", "superseded_by": "LL-004"}` — the status did
    **not** move.
12. **3.4 — the emitted always-loaded note.** `handoff_emit("<scratch>/emit-step34")` (no
    `force`, no `refresh_stock`) → `written: [".mcp.json", "CLAUDE.md"]`. The only emitted file
    naming `LL-003` is `CLAUDE.md`; its line, verbatim:
    ```
    - **LL-003** [improve, superseded by LL-004 - pending its approval] When the lab tracker's date logic changes, decide the boundary semantics first and encode them in a test before touching the comparison operator, because the operator itself is ...
    ```
    The successor is not approved, so the tag reads `pending its approval`, not
    `RETIRE THIS ROW (operator)`.
    `readiness_check("package")`'s `lessons-superseded-binding`, verbatim:
    ```json
    {"rule": "lessons-superseded-binding", "severity": "advisory", "status": "pass",
     "entities": [],
     "note": "Approved lessons whose `superseded_by` names an approved successor: they STILL BIND (the pointer alone retires nothing). Retire each by setting lifecycle_status to Superseded on the operator's word (operator_confirm); approving a successor retires the lessons pointing at it automatically",
     "population": {"table": "lessons", "rows": 4, "scoped": false}}
    ```
    Not failing on OLD — correct: its successor is still `Proposed`.
    The same call also reported `prompt_library.diverged_customized` naming
    `prompts/README.md` (see F-1); this is the first sighting of it in the beat.
13. **3.5 — the UNATTENDED retirements, both refused.** OLD re-sent with
    `"lifecycle_status": "Superseded"` and **no** `operator_confirm` → **REFUSED**, verbatim:
    ```json
    {"ok": false, "applied": 0,
     "error": "batch rolled back — one or more items violated constraints",
     "items": [{"index": 0, "ok": false, "id": "LL-003",
       "error": "LL-003: retiring a lesson that BINDS future sessions is the OPERATOR's word, like approving it — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
    ```
    Then the same row with `"lifecycle_status": "Proposed"` → **REFUSED** with the **identical**
    text (the guard is any move off a binding status, not a list of named targets):
    ```json
    {"ok": false, "applied": 0,
     "error": "batch rolled back — one or more items violated constraints",
     "items": [{"index": 0, "ok": false, "id": "LL-003",
       "error": "LL-003: retiring a lesson that BINDS future sessions is the OPERATOR's word, like approving it — re-run this item with \"operator_confirm\": true after their explicit confirmation; never in unattended mode"}]}
    ```
    OLD still: `{"lifecycle_status": "Approved", "superseded_by": "LL-004"}`.
14. **3.6 — approving the successor finishes it.** NEW re-sent with
    `"lifecycle_status": "Approved", "operator_confirm": true, "confirmed_by": "operator:lab"`
    → verbatim:
    ```json
    {"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "LL-004",
      "changed_columns": [{"column": "lifecycle_status", "old_len": 8, "new_len": 8},
                          {"column": "confirmed_by", "old_len": 0, "new_len": 12},
                          {"column": "confirmed_at", "old_len": 0, "new_len": 10}],
      "next": "this lesson BINDS only once the always-loaded note is rebuilt - run handoff_emit in this same batch (the note is rebuilt by nothing else)",
      "superseded": ["LL-003"], "lesson_audit": "PE-026"}]}
    ```
    `entity_query("lesson", id="LL-003")["rows"][0]["lifecycle_status"]` → `"Superseded"`.
    `entity_query("lesson", status="Approved")` ids → `["LL-004"]` — OLD is gone from the
    binding set. `entity_query("progress-entry", search="LL-003 -> Superseded")` → one row,
    verbatim:
    ```json
    {"id": "PE-025", "event_type": "transition",
     "entry": "LESSON LL-003 -> Superseded: its successor LL-004 was approved on the operator's word (operator_confirm attested on that write)",
     "subject_id": "LL-003", "actor": "system:lesson-supersession", "corrects": null,
     "phase_id": null, "slice_id": null, "occurred_at": "2026-09-21T17:04:35Z",
     "custom_attributes": null, "last_referenced": null}
    ```
    `gate_run()` → `ready: true`.

**Script 4 — Step 4: the backticked phantom (plan 076).**

15. Beat 16's defect is `DEF-005`, title `export header drifts (see DEF-001)`. The full row
    re-sent with the title ``export header drifts (see DEF-001; mock id `RISK-808`)`` →
    verbatim:
    ```json
    {"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "DEF-005",
      "changed_columns": [{"column": "title", "old_len": 34, "new_len": 54}]}]}
    ```
    Only `title` — `changed_columns` proves the re-send altered nothing else.
16. `readiness_check("package")`'s `prose-ids-resolve`, verbatim:
    ```json
    {"rule": "prose-ids-resolve", "severity": "advisory", "status": "pass", "entities": [],
     "note": "identifiers written in prose that resolve to NO entity (G-IDS checks foreign keys and the index, never a sentence): correct the id, or record the missing row; an immutable row is repaired by supersession. THE ENTITY LIST IS A FLOOR, not a census: hits inside code spans are listed under `in_code_spans` and tokens too narrow to be this family's ids under `not_well_formed` - both informational, neither fails the rule, so backticks hide nothing. The append-only journal and Superseded/Obsolete rows are not scanned",
     "in_code_spans": ["DEF-005.title -> RISK-808"], "not_well_formed": []}
    ```
    `entities` does **not** name `RISK-808`; `in_code_spans` names exactly
    `DEF-005.title -> RISK-808`; the note says the entity list is a FLOOR. The title was
    **left as it is** — the inert list is the point. The rule names nothing else.
    `gate_run()` → `ready: true`.

**Script 5 — Steps 5 and 6.**

17. **Step 5 — the open-ended blanket waiver (plan 079).** `waivers-open-ended`, verbatim:
    ```json
    {"rule": "waivers-open-ended", "severity": "advisory", "status": "fail",
     "entities": ["WVR-002"],
     "note": "whole-rule waivers with no expiry: each waives EVERY entity the rule names, including rows written long after it was approved. Put each to the operator - set `expires`, or narrow it to the entities it was approved for (`applies_to`). You never author or edit a waiver on your own judgment",
     "population": {"table": "waivers", "rows": 2, "scoped": false}}
    ```
    `WVR-002` was **not** changed. The lab keeps this amber deliberately: a dated `expires`
    would become a time bomb in a fixture that is replayed for years, and the rule's own note
    says a waiver is never authored or edited on the agent's judgment.
18. **Step 6 — no rule passes over nothing (plan 077).** `deferred-work-reviewed` BEFORE,
    verbatim:
    ```json
    {"rule": "deferred-work-reviewed", "severity": "advisory", "status": "indeterminate",
     "entities": [],
     "note": "activation triggers are prose — a human judges whether each fired — no deferred_work rows at all: this rule measured nothing (a package with nothing to report and one that recorded nothing look the same here). Record the rows, or record the family's omission if it is deliberately empty",
     "population": {"table": "deferred_work", "rows": 0, "scoped": false},
     "discriminating": false}
    ```
    `gate_run()["ready"]` = **`true`**, `readiness_check("package")["ready"]` = **`false`**
    (the scenario's deliberately-open items; `readiness` is not-ready on this fixture by design).
19. `population.table` is `"deferred_work"`; reversing `srv.ENTITY_TABLES` gives the entity
    type `"deferred-work"`. `entity_upsert([{"type": "omission", "entity_type":
    "deferred-work", "reason": "The lab tracker defers no work: every slice is in scope for its
    phase."}])` → `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": null}]}`
    (`id: null` is correct — the omissions table is keyed by `entity_type`, it has no `id`).
20. `deferred-work-reviewed` AFTER, verbatim:
    ```json
    {"rule": "deferred-work-reviewed", "severity": "advisory", "status": "pass",
     "entities": [],
     "note": "activation triggers are prose — a human judges whether each fired — no deferred_work rows, and the family's omission is recorded: a deliberate zero",
     "population": {"table": "deferred_work", "rows": 0, "scoped": false},
     "omitted": {"entity_type": "deferred-work",
                 "reason": "The lab tracker defers no work: every slice is in scope for its phase."}}
    ```
    `gate_run()["ready"]` = **`true`** (unchanged), `readiness_check["ready"]` = **`false`**
    (unchanged). `hypotheses-measurable` was left `indeterminate` over
    `{"table": "hypotheses", "rows": 0}` with the same `measured nothing` note — one explained
    zero beside one amber zero is the contrast the lab keeps.

**Script 6 — Step 7: the review page says whether it is current (plan 081).**

21. `package_verify("package")` BEFORE → `review_current: null` (quoted at step 3 above).
    **`null`, not `false`**: the recorded page predates the plan-081 stamp, so it carries no
    `tamheed-digest` meta to compare — the tool reports *unknown*, and only a page that
    carries a stamp which no longer matches reads `false`.
22. `export_html()` → `ok`, `121116` bytes, four CSV files re-emitted
    (`defects`, `lessons`, `omissions`, `progress_entries`), none diverged, none unowned.
23. `package_close()`, then `package_verify("package")` → verbatim (projection):
    ```json
    {"verified": true,
     "digest": "9434eb2d70d39ddcc893d5033805b1ad9bf71cdf275306906356d1ef18eb07aa",
     "review_current": true, "foreign": [], "foreign_csv": []}
    ```
    `review.html`'s meta line, verbatim:
    ```html
    <meta name="tamheed-digest" content="9434eb2d70d39ddcc893d5033805b1ad9bf71cdf275306906356d1ef18eb07aa">
    ```
    The digest is identical before and after `package_close()`, so closing does not stale the
    page — settling the ordering step 9 needs.

**Script 7 — Step 8: a completed hand-merge is visible (plan 078) — on a SCRATCH COPY.**

24. The fixture was closed; `package/` copied to `<scratch>/copy-root/package`;
    `srv.PACKAGE_ROOT` pointed at the copy; the copy opened. Newest `integrity-check.md` key in
    `plugins/tamheed/prompts/stock-history.json` = **`4.9.0`**.
25. `handoff_emit("<scratch>/emit-step8", refresh_stock=True)` on the copy →
    `refreshed: ["prompts/register-liveness.md"]`, `diverged_stale_stock: []`,
    `diverged_customized: [{"file": "prompts/README.md", "stock_last_changed": "4.10.0",
    "stock_merged": null, "contains_current_stock": false}]` (F-1).
26. The copy's `prompts/integrity-check.md` was overwritten BY HAND with a body that rewrites
    every stock line and carries `<!-- tamheed:stock-merged 4.9.0 -->`; its
    `prompts/orient-resume.md` likewise, carrying `<!-- tamheed:stock-merged 3.0.0 -->`.
27. `handoff_emit("<scratch>/emit-step8")` again → `diverged: ["prompts/integrity-check.md",
    "prompts/orient-resume.md", "prompts/README.md"]`; the three `diverged_customized` entries,
    verbatim:
    ```json
    {"file": "prompts/integrity-check.md", "stock_last_changed": "4.9.0",
     "stock_merged": "declared 4.9.0", "contains_current_stock": false}
    ```
    ```json
    {"file": "prompts/orient-resume.md", "stock_last_changed": "4.9.0",
     "stock_merged": "declared 3.0.0", "contains_current_stock": false}
    ```
    ```json
    {"file": "prompts/README.md", "stock_last_changed": "4.10.0",
     "stock_merged": null, "contains_current_stock": false}
    ```
    The third is F-1's carry-over from the fixture, not a hand-merge the beat authored.
    The `CUSTOMISED` warning, verbatim:
    ```
    3 stock prompt(s) are CUSTOMISED — kept; stock last changed: orient-resume.md (4.9.0), README.md (4.10.0) — if a customization predates that release it lacks the update: hand-merge (the bundled stock-history.json carries every release's body); to accept the current template for ONE file, delete it and re-emit; force=True overwrites ALL diverged stock files (customised included)
    ```
    It names **`orient-resume.md`** and **not** `integrity-check.md` — exactly the plan's
    check. `contains_current_stock` is `false` for both, so the containment test alone would
    have kept both in the lag list; it is the **declared** marker matching
    `stock_last_changed` that took `integrity-check.md` out of it.
28. The copy was closed and `srv.PACKAGE_ROOT` pointed back at the fixture. The fixture's own
    `prompts/integrity-check.md` and `prompts/orient-resume.md` carry no `tamheed:stock-merged`
    marker — both verified `False` — and are byte-unchanged (neither appears in
    `git status --short`).

**Scripts 8–9 — Step 9: close the beat (with the reviewer's amendment).**

29. **9.1** `handoff_emit("<scratch>/emit-step9", refresh_stock=True)` on the fixture →
    `prompt_library`, verbatim (projection):
    ```json
    {"emitted": [], "diverged": ["prompts/README.md"], "diverged_stale_stock": [],
     "diverged_customized": [{"file": "prompts/README.md", "stock_last_changed": "4.10.0",
                              "stock_merged": null, "contains_current_stock": false}],
     "refreshed": ["prompts/register-liveness.md"]}
    ```
    `refreshed` names **one** body, not the two the plan's step 9 expected — `README.md` is
    classified customised (F-1). The two warnings, verbatim:
    ```
    1 stock prompt(s) are CUSTOMISED — kept; stock last changed: README.md (4.10.0) — if a customization predates that release it lacks the update: hand-merge (the bundled stock-history.json carries every release's body); to accept the current template for ONE file, delete it and re-emit; force=True overwrites ALL diverged stock files (customised included)
    ```
    ```
    1 stale-stock prompt(s) refreshed to the current template (refresh_stock)
    ```
30. **9.2 — the two pre-conditions for `force`.** (a) `diverged_customized` is exactly
    `["prompts/README.md"]` → **true**. (b) the unified diff of the on-disk file against the
    `4.9.0` history body with `{package}` substituted, verbatim:
    ```
    --- history-4.9.0
    +++ fixture-on-disk
    @@ -1 +1 @@
    -# How to use this folder — the `package` prompt guide (tamheed v4.9.0)
    +# How to use this folder — the `package` prompt guide (tamheed v4.8.1)
    ```
    Exactly one line, and it is the title's version → **true**. Both hold, so `force` was
    permitted by the amendment.
31. **9.3** `handoff_emit("<scratch>/emit-step9force", force=True)` → `prompt_library`,
    verbatim (projection):
    ```json
    {"emitted": ["prompts/README.md"], "diverged": [], "diverged_stale_stock": [],
     "diverged_customized": [], "refreshed": []}
    ```
    Exactly the one file the pre-conditions accounted for. The fixture's
    `prompts/README.md` now contains `tamheed:stock-merged` (**true**) and still contains
    `Show the record with its id` (**true**, the needle beat 16's existing assertion pins).
    Its title line reads `# How to use this folder — the `package` prompt guide (tamheed
    v4.9.0)` — the bundled 4.10.0 body still carries the 4.9.0 stamp, which plan 084's release
    will re-stamp (F-1's tail; expected, as the plan's maintenance note says).
32. **9.4** `progress_update([{ "event_type": "note", "actor": "agent:lab-beat-17", "entry":
    … }])` → `{"ok": true, "ids": ["PE-027"]}`. The note narrates the beat and quotes, verbatim:
    `retiring a lesson that BINDS future sessions`; `LL-003 is still Approved, so it KEEPS
    BINDING: `superseded_by` is only a pointer.`; `changed_columns: [{"column": "statement",
    "old_len": 677, "new_len": 467}]` and the `old_len 467 -> new_len 677` reversal;
    `DEF-005.title -> RISK-808` under `in_code_spans`; `waivers-open-ended` failing on
    `["WVR-002"]`; `measured nothing` and `omitted`; `review_current` `null` before and `true`
    after `export_html`; plus one sentence recording finding **F-1**.
33. **9.5** `export_html()` → `ok`, `127954` bytes. `gate_run()` → **`ready: true`**, all eight
    gates `pass`. `package_verify()` while open, and again after `package_close()` — the same
    result both times, verbatim (projection):
    ```json
    {"verified": true,
     "digest": "0048451e12d0dc2e27c7f9289306dabb28d80c668bfb4f736ade5cab89968f2f",
     "review_current": true, "foreign": [], "foreign_csv": []}
    ```
    Neither `gate_run` nor `package_verify` staled the page, so no second export was needed.
34. **9.6** `package_close()` → `ok`; `data/.lock` absent.

### Mechanism → observed

| Mechanism (plan) | Verdict |
|---|---|
| The half-state `next` hint: `is still Approved, so it KEEPS BINDING` (075) | **observed** (step 11) |
| UNATTENDED pointer REFUSED: `pointing a BINDING lesson at a successor` (075) | **observed** (step 10) |
| UNATTENDED retirement REFUSED, twice: `retiring a lesson that BINDS future sessions` (075) | **observed** (step 13 — `Superseded` and `Proposed`, identical text) |
| Approving the successor retires the old lesson in the same write, journaled by `system:lesson-supersession` (075) | **observed** (step 14 — `superseded: ["LL-003"]`, `PE-025`) |
| `in_code_spans` names a backticked phantom while `entities` stays empty (076) | **observed** (step 16) |
| `not_well_formed` (076) | **not observed** — it was `[]`. This beat's phantom is a well-formed `RISK-` id inside a code span, which is the mechanism the plan asked for; a too-narrow token would need a second, different prose edit the beat does not call for. Beat 16 already pins the bare-prose half of the same rule. |
| A zero-row rule reads `indeterminate` with `measured nothing` (077) | **observed** (step 18) |
| A recorded omission turns the same rule `pass` with `omitted` (077) | **observed** (step 20) |
| `stock_merged: "declared <current>"` takes a file out of the lag list (078) | **observed** (step 27 — `integrity-check.md` absent from the `CUSTOMISED` warning) |
| `contains_current_stock` reported beside it (078) | **observed** (step 27 — `false` on all three entries; the declaration, not containment, is what cleared the lag) |
| `waivers-open-ended` names the open-ended blanket waiver (079) | **observed** (step 17 — `fail`, `advisory`, `["WVR-002"]`) |
| `changed_columns` reports a lost paragraph as a length drop (080) | **observed** (steps 6–8 — `677 → 467`, `467 → 677`, then `[]`) |
| The `tamheed-digest` stamp in `review.html` (081) | **observed** (step 23) |
| `package_verify.review_current` (081) | **observed** (steps 21, 23, 33 — `null` → `true`) |

### Findings

**F-1 (recorded at the reviewer's instruction; engine and history file both out of scope).**
A lab beat that refreshes stock prompts *before* the release re-stamps the prompt guide's
version line leaves the fixture holding a body no history key records, so it reads as
`diverged_customized` forever. Beat 16 refreshed `prompts/README.md` to the then-current stock;
the 4.9.0 release then re-stamped that file's title line and overwrote the `4.9.0` history key,
so the fixture's copy matched neither the new `4.9.0` body nor any older one. Measured here:
`refresh_stock=True` refreshed only `prompts/register-liveness.md`, and the one-line diff at
step 30 is the whole of the divergence. Resolved for this fixture by
`handoff_emit(force=True)` after both pre-conditions were verified. It will recur at every
release that changes the guide's version line, and plan 084's release will make the fixture's
copy read as stale stock by one line again — expected, as the plan's maintenance note says.

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
... (56/56 pass, the twelve new checks last)
PASS  lab-tracker

1 case(s) checked, 0 failed, 0 skipped

$ python check.py
ALL CHECKS PASSED
```

### No hollow assertion: the twelve new checks, backup vs fixture

Each `cmd` was run twice — once with `{case_dir}` pointing at the **Step 1 backup**
(`<scratch>/backup-root`), once at the fixture. Exit 0 = the claim holds.

| # | Assertion (plan) | Backup | Fixture | What the backup printed |
|---|---|---|---|---|
| 1 | Approving the successor retired the false lesson (075) | **1** | **0** | `below required minimum 1` |
| 2 | The engine journaled that retirement as its own transition (075) | **1** | **0** | `below required minimum 1` |
| 3 | An unattended retirement was refused, and the note quotes the refusal (075) | **1** | **0** | `'retiring a lesson that BINDS future sessions' not found` |
| 4 | The half-state hint said the pointer retires nothing (075) | **1** | **0** | `'KEEPS BINDING' not found` |
| 5 | A lost paragraph was a number on the screen (080) | **1** | **0** | `'changed_columns' not found` |
| 6 | The backticked phantom stays in the defect's prose, inert (076) | **1** | **0** | `` '`RISK-808`' not found `` |
| 7 | The note names it under `in_code_spans` (076) | **1** | **0** | `'in_code_spans' not found` |
| 8 | The open-ended blanket waiver was named (079) | **1** | **0** | `'waivers-open-ended' not found` |
| 9 | A rule over an empty family measured nothing, until the omission was recorded (077) | **1** | **0** | `'measured nothing' not found` |
| 10 | The deliberate zero is a recorded omission (077) | **1** | **0** | `'The lab tracker defers no work' not found` |
| 11 | The recorded review page carries the digest of the state it rendered (081) | **1** | **0** | `'tamheed-digest' NOT found in <backup>/package/review.html` |
| 12 | The fixture's prompt guide carries the 4.10.0 stock body (078) | **1** | **0** | `'tamheed:stock-merged' NOT found in <backup>/package/prompts/README.md` |

Twelve for twelve: every one fails on the pre-beat tree and passes on the fixture. No needle was
adapted; `grep-present --tables omissions` (#10) read `omissions.jsonl` on both trees, so the
plan's fallback was not needed.

### Verbatim refusal texts (the two the beat's note quotes from)

```
LL-003: pointing a BINDING lesson at a successor (approving that successor retires this one) is the OPERATOR's word, like approving it — re-run this item with "operator_confirm": true after their explicit confirmation; never in unattended mode
```

```
LL-003: retiring a lesson that BINDS future sessions is the OPERATOR's word, like approving it — re-run this item with "operator_confirm": true after their explicit confirmation; never in unattended mode
```

Both arrived under the batch-level `"error": "batch rolled back — one or more items violated
constraints"`, with `"applied": 0` — an attempt is not a write, and the store was unchanged
after each.
