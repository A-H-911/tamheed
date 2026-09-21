# Lab continuation report — beat 16, v4.9.0 RC (plan 073, 2026-09-21)

> The execution agent's report from `lab/scenario.md` beat 16 (the findings_25 continuation:
> the dead holder's lock, the read-while-locked migrate preview, `package_unlock`'s report and
> its operator-worded removal, the live holder's refusal, the legible reads —
> `server_info(detail)`, `omitted_columns`/`matched`, rule `population` — the phantom id caught
> by `prose-ids-resolve`, the partial export and its digest, the retired CSV removed while an
> operator's file survived, and the stock prompts refreshed), archived **verbatim** below the
> header. Context: an INCREMENTAL real-agent session (`actor: agent:lab-beat-16`) against the
> recorded `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plans-063–071 tree at `main` `f2569f0`), eight scripts plus
> one child process, every script that opens the package ending in `package_close()` (in a
> `finally`) and asserting `data/.lock` absent before it starts. Files touched =
> the fixture (`data/` — `defects.jsonl` + `progress_entries.jsonl`; `csv/` — `defects.csv` +
> `progress_entries.csv`; `prompts/` — the five refreshed stock bodies; `review.html`; the new
> `exports/beat16-defects.json`) + `evals/evals.json` (nine appended assertions on the
> `lab-tracker` case) + `lab/scenario.md`, `lab/README.md` + this report. No file under
> `plugins/`, `tests/`, `check.py`, `evals/pkg_check.py`, `CHANGELOG.md`, `evals/README.md` or
> any other fixture was edited. **Zero** hand edits of a `data/` file were made. Three files
> were written or removed BY HAND, each because the beat's text says so and each named where it
> happens below: `data/.lock` (written twice — once by the CHILD process of step 2.1, which the
> beat's text prescribes, and once by the driver itself as the LIVE holder of step 2.6; the
> live one was then removed by hand, the tool's own refusal naming manual removal as the
> deliberate path, and the dead one was removed by `package_unlock`), `csv/prompts.csv` and
> `csv/operator-notes.csv` (planted in step 6; the first was removed by `export_html`, the
> second by hand). Everything else went through the tools. All three eval commands green
> (`pkg_check gates` ready=True, `run_evals` lab-tracker **44/44** — 35 before the beat, +9 —
> `check.py` ALL CHECKS PASSED). A full `package/` backup (27 `data/` files) was taken to
> `<scratch>/beat16/backup-package` before script 1; nothing was restored from it.
>
> **No deviation from the plan's steps.** Every needle in the plan's proposed assertion block
> matched the verbatim text observed and was used unchanged; the plan's `exports/` fallback was
> not needed (`evals/sample-results/lab-tracker/package/exports/` is tracked, and the emitted
> envelope carries no machine-specific path). `evals/README.md` states no assertion count for
> `lab-tracker`, so it was left untouched, as the scope line allows.

---

## Tamheed v4.9.0 lab continuation — beat 16 — execution report

### Numbered tool-call log (in-process handler calls + key outcomes)

Drift check (repo root, nothing written):

0. `git log --oneline -1` → `f2569f0 docs: plan 073 recorded (lab beat 16); the acceptance pass
   noted in the index` (the commit the reviewer named when dispatching).
   `python plugins/tamheed/server/tamheed_server.py --selftest` →
   `mcp sdk: ok (1.27.2) — 19/19 tools registered`.
   Backup: `cp -r evals/sample-results/lab-tracker/package → <scratch>/beat16/backup-package`
   (**27 `data/` files**) — before script 1.

Script 1 — baseline (`data/.lock` absent at start and at end):

1. `package_open("package")` → `{"ok": true, "package": "package", "package_root": "<worktree>/evals/sample-results/lab-tracker"}`.
2. `gate_run()` → **`ready: true`**, all eight `G-*` `pass`,
   `audit_evidence = {"evidenced": 3, "narrated": 0, "ungraded": 1, "ungraded_ids": ["AV-005"]}`,
   `requirements_unwired` advisory with an empty list.
3. `package_verify()` → verbatim:
   ```json
   {"ok": true, "package": "package", "files": 27, "foreign": [], "foreign_csv": [],
    "digest": "5f4c1731c83cca30a6e3518cf68298f07270b1359443902c630205c95e9b6570",
    "recorded": null, "verified": true, "loadable": true, "dirty": [],
    "memory_matches_disk": true}
   ```
4. `entity_query("progress-entry", limit=1)` → `total: 21`.
   `entity_query("defect", limit=50)` → `total: 4` (DEF-001…DEF-004; every
   `custom_attributes` is `null`, every `found_in` is `SL-002` — which is what chose the
   step-3 search needle). `package_close()` → `{"ok": true, "package": "package"}`.

Script 2 — **THE DEAD HOLDER** (plans 063–064; package CLOSED):

5. A CHILD process (`subprocess.run([sys.executable, child_lock.py])`, rc 0) wrote
   `package/data/.lock` naming ITSELF and exited. The bytes it left, verbatim:
   ```json
   {"pid": 366344, "host": "Anas-PC", "taken_at": "2026-09-21T04:48:00+00:00",
    "started": 1789966080.4973545, "identity": "win:17899660804973546"}
   ```
   (the store's own key set, minus `pidns`, which is `None` on win32.)
6. `package_open("package")` — **REFUSED**, verbatim:
   `{"ok": false, "error": "C:\\Users\\ahammo\\Repos\\tamheed\\.claude\\worktrees\\agent-aea3acc13f73168bf\\evals\\sample-results\\lab-tracker\\package\\data\\.lock exists — another writer owns this package (held by pid 366344 on Anas-PC since 2026-09-21T04:48:00+00:00; observed: not-running - no process with pid 366344 is running on this host). If the writer is gone, the server's package_unlock(name) reports the holder and removes the lock only on the operator's word"}`
   → the outcome was **`not-running`** (not `reused`); `_CURRENT is None` → `True`.
7. `package_migrate("package")` — the read-only preview **ANSWERED**, verbatim:
   `{"ok": false, "error": "package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate (the expected answer on a current store) (read while locked: held by pid 366344 on Anas-PC since 2026-09-21T04:48:00+00:00; observed: not-running - no process with pid 366344 is running on this host)"}`
8. `package_unlock("package")` → **report only**, verbatim:
   ```json
   {"ok": true, "stage": "report", "package": "package", "locked": true,
    "lock": {"pid": 366344, "host": "Anas-PC", "taken_at": "2026-09-21T04:48:00+00:00"},
    "observed": "not-running",
    "evidence": "no process with pid 366344 is running on this host",
    "would_unlock": true,
    "note": "nothing written. confirm=true removes the lock and journals it - on the OPERATOR's word only."}
   ```
   The lock file was **byte-unchanged** after the report (`read_bytes() == snapshot` → `True`).
9. `package_unlock("package", confirm=True)` — **the operator's word given by plan 073** →
   verbatim:
   ```json
   {"ok": true, "stage": "unlocked", "package": "package", "observed": "not-running",
    "evidence": "no process with pid 366344 is running on this host",
    "journaled": true, "journal_id": "PE-022"}
   ```
   `data/.lock` gone → `True`.
10. `package_open("package")` → `entity_query("progress-entry", id="PE-022")` → the journal row,
    verbatim:
    ```json
    {"id": "PE-022", "event_type": "forced-override",
     "entry": "FORCED lock removal: data/.lock held by pid 366344 on Anas-PC since 2026-09-21T04:48:00+00:00 was observed `not-running` - no process with pid 366344 is running on this host - and removed on the operator's word (package_unlock confirm=true)",
     "subject_id": null, "actor": "system:package-unlock", "corrects": null,
     "phase_id": null, "slice_id": null, "occurred_at": "2026-09-21T04:48:00Z",
     "custom_attributes": null, "last_referenced": null}
    ```
    `package_close()` → ok.
11. **THE LIVE HOLDER** — a lock naming THIS driver process was planted **by hand**:
    `{"pid": 370136, "host": "Anas-PC", "taken_at": "2026-09-21T04:48:00+00:00", "started": 1789966080.415348, "identity": "win:17899660804153480"}`.
    `package_unlock("package", confirm=True)` — **REFUSED**, verbatim:
    `{"ok": false, "error": "package 'package': the lock's holder was observed `alive` (pid 370136 is the very process that wrote the lock (exact start identity)) - not removed. Only a holder observed not-running or reused is unlocked by this tool; a manual removal of data/.lock stays the deliberate path when YOU know what this host cannot see"}`
    That planted lock was then **removed by hand** (`LOCK.unlink()`) — I wrote it, I removed it,
    and that is the very path the refusal names.

Script 3 — **THE LEGIBLE READS** (plans 066, 068, 069):

12. `server_info()` `package` block, verbatim:
    ```json
    {"name": "lab-tracker", "title": "tick — tiny CLI task tracker", "profile": "rnd",
     "mode": "full", "iteration": 1, "package_version": "4.0.0", "go_no_go": null,
     "entry_point": null}
    ```
    (top-level keys: `ok`, `version`, `package_root`, `open_package`, `package`,
    `migrations_head`, `schema_version`.)
13. `server_info(detail=True)` → `entity_types` is a **list of 37** entries; the `defect` one,
    verbatim: `{"type": "defect", "table": "defects", "id_prefix": "DEF-"}`.
    `relation_rules["mitigates"]`, verbatim:
    ```json
    {"from": ["acceptance-criterion", "adr", "assumption", "constraint", "convention",
              "decision", "defect", "deferred-work", "execution-plan", "experiment",
              "invariant", "phase", "poc", "requirement", "slice", "test", "wbs-item"],
     "to": ["risk"]}
    ```
14. `entity_query("defect", columns=["id","title"], search="SL-002")` → 4 rows, and the two
    plan-068 siblings of `rows`, verbatim:
    `"omitted_columns": ["severity", "lifecycle_status", "found_in", "fixed_by", "custom_attributes", "last_referenced"]`
    `"matched": {"DEF-001": ["found_in"], "DEF-002": ["found_in"], "DEF-003": ["found_in"], "DEF-004": ["found_in"]}`
    — the search says WHERE it matched, and it matched in a column the projection did not
    return. (No defect carries `custom_attributes`, so `found_in` was the needle that proves
    the point.)
15. `readiness_check("package")` → `ready: false` (the scenario's deliberately-open items).
    `defects-closed`, verbatim: `{"rule": "defects-closed", "severity": "blocking",
    "status": "pass", "entities": [], "note": "open critical/high defects: fix, disposition,
    or convert to deferred-work (scope-change first if it changes scope)",
    "population": {"table": "defects", "rows": 4, "scoped": false}}`.
    `lessons-confirmed`: `"status": "fail"`, `"entities": ["LL-002"]`,
    `"population": {"table": "lessons", "rows": 2, "scoped": false}`.
    `package_close()` → ok.

Script 4 — **THE PHANTOM ID** (plan 070):

16. Failing readiness rules BEFORE the write (the baseline to compare against):
    `["acs-met", "clarifications-open", "defects-minor", "lessons-confirmed",
    "open-questions-overdue", "open-questions-resolved"]`.
17. `entity_upsert([{type: defect, id: DEF-005, title: "export header drifts after RISK-909
    (see DEF-001)", severity: low, lifecycle_status: Open, found_in: SL-002, …}])` — the full
    row, mirroring DEF-004's column set → `{"ok": true, "applied": 1,
    "items": [{"index": 0, "ok": true, "id": "DEF-005"}]}`.
18. `readiness_check("package")` → `prose-ids-resolve` **caught it**, verbatim:
    ```json
    {"rule": "prose-ids-resolve", "severity": "advisory", "status": "fail",
     "entities": ["DEF-005.title -> RISK-909"],
     "note": "identifiers written in prose that resolve to NO entity (G-IDS checks foreign keys and the index, never a sentence): correct the id, or record the missing row; an immutable row is repaired by supersession. Code spans, the append-only journal and Superseded/Obsolete rows are not scanned"}
    ```
    It named `RISK-909` and **not** `DEF-001` — the real row cited in the same sentence was
    left alone. The failing set grew by exactly this one rule.
19. `entity_upsert` the SAME id, full row, title `export header drifts (see DEF-001)` →
    `{"ok": true, "applied": 1, …}`; `readiness_check("package")` → `prose-ids-resolve`
    `"status": "pass", "entities": []`, and the failing set is back to the step-16 baseline.
    `entity_query("defect", id="DEF-005")` confirms the stored title. `package_close()` → ok.

Script 5 — **THE PARTIAL EXPORT AND THE DIGEST** (plan 067):

20. `entity_export("beat16-defects.json", args={"type": "defect", "limit": 1})` → verbatim:
    ```json
    {"ok": true, "path": "<worktree>/evals/sample-results/lab-tracker/package/exports/beat16-defects.json",
     "bytes": 703, "tool": "entity_query",
     "digest": "5544ab8f846498557c4fb75cc0d006aa4bcd5b83555b4781fa8f5b19f6a1879c",
     "memory_matches_disk": true, "count": 1, "total": 5, "partial": true,
     "note": "PARTIAL: 1 of 5 rows — the file has no payload cap; pass a limit above total (or page with after_id) to export the whole family"}
    ```
21. The FILE's `tamheed_export` envelope, read back off disk, verbatim:
    ```json
    {"version": "4.8.1", "package": "package", "tool": "entity_query",
     "args": {"type": "defect", "limit": 1},
     "digest": "5544ab8f846498557c4fb75cc0d006aa4bcd5b83555b4781fa8f5b19f6a1879c",
     "memory_matches_disk": true, "count": 1, "total": 5, "partial": true}
    ```
    It carries `count`, `total` and `"partial": true`, and — unlike an emitted handoff — **no
    machine-specific absolute path**, which is why this one file is fixture material.
22. `package_verify()` → `digest: 5544ab8f846498557c4fb75cc0d006aa4bcd5b83555b4781fa8f5b19f6a1879c`
    (the package digest now equals the digest the export cites).
    `package_verify(expect="5544ab8f846498557c4fb75cc0d006aa4bcd5b83555b4781fa8f5b19f6a1879c")`
    — the digest the export itself cites — → `"matches_expected": true`,
    `"verified": true`, `"foreign": []`, `"foreign_csv": []`. `package_close()` → ok.

Script 6 — **`csv/`** (plan 065):

23. Written **BY HAND** into `package/csv/`: `prompts.csv` with the retired table's exact header
    `id,prompt_kind,title,body,phase_id,custom_attributes,last_referenced` plus one data line
    (`PR-001,kickoff,Kick off the executor,Read the CLAUDE.md note first.,PH-001,,`), and
    `operator-notes.csv` with `my,own` / `1,2`.
24. `package_verify()` → `"foreign_csv": ["operator-notes.csv", "prompts.csv"]` — both named
    (`"foreign": []`, `"verified": true` — a foreign CSV is reported, not a corruption).
25. `export_html()` → its `csv` block, verbatim:
    `"removed": ["csv/prompts.csv"]`, `"unowned": ["csv/operator-notes.csv"]`,
    `"emitted": ["csv/defects.csv", "csv/progress_entries.csv"]`, `"diverged": []`.
    The retired table's derived CSV was deleted by the tool; the operator's own file was left
    exactly where it was.
26. `operator-notes.csv` was then deleted **by hand** (I wrote it in step 23, I removed it), and
    `export_html()` run once more → `"removed": []`, `"unowned": []`, `"emitted": []`,
    everything `unchanged`. `package_close()` → ok.

Script 7 — **THE STOCK PROMPTS** (plan 071):

27. `handoff_emit(target_dir="<scratch>/beat16/beat16-emit", refresh_stock=True)` (no `force`) →
    `prompt_library`, verbatim:
    ```json
    {"emitted": [],
     "unchanged": ["prompts/defect-triage.md", "prompts/drift-register.md",
                   "prompts/generate-report.md", "prompts/loop-guard.md",
                   "prompts/loop-iteration.md", "prompts/package-onboarding.md",
                   "prompts/phase-close.md", "prompts/progress-sync.md",
                   "prompts/release-close-out.md", "prompts/skill-promote.md",
                   "prompts/slice-kickoff.md", "prompts/slice-review.md"],
     "diverged": [], "diverged_stale_stock": [], "diverged_customized": [],
     "refreshed": ["prompts/integrity-check.md", "prompts/orient-resume.md",
                   "prompts/README.md", "prompts/register-liveness.md",
                   "prompts/replan-deferred.md"]}
    ```
    Exactly the five bodies plan 071 changed, and nothing customized to preserve. The emit's
    own `warnings`: `["5 stale-stock prompt(s) refreshed to the current template (refresh_stock)"]`;
    `written: [".mcp.json", "CLAUDE.md"]` — into the SCRATCH target, never `workspace/`, since
    both carry the absolute package path of the machine that ran the beat. `package_close()` → ok.

Script 8 — **CLOSING THE BEAT**:

28. `progress_update([{event_type: "note", actor: "agent:lab-beat-16", entry: <the beat's
    narration>}])` → `{"ok": true, "ids": ["PE-023"]}`. The note quotes verbatim the
    `observed: not-running - no process with pid 366344 is running on this host` clause, the
    `` the lock's holder was observed `alive` (pid 370136 is the very process that wrote the
    lock (exact start identity)) - not removed `` refusal, and the `DEF-005.title -> RISK-909`
    entity string, plus `read while locked`, `omitted_columns`, `matched`, `population`,
    `partial: true`, `foreign_csv`, `unowned` and the five refreshed bodies.
29. `package_verify(expect="5544ab8f…6a1879c")` — the step-22 digest, after ONE append —
    verbatim:
    ```json
    {"ok": true, "package": "package", "files": 27, "foreign": [], "foreign_csv": [],
     "digest": "7ab7df8bccc25a81060a4b88cdf6f5a806be73a7fbf83fc1520f88a74e609256",
     "recorded": null, "matches_expected": false, "verified": true, "loadable": true,
     "dirty": [], "memory_matches_disk": true}
    ```
    **`matches_expected: false`** — any write moves the package digest, and `verified` stays
    `true`: the instrument distinguishes "changed" from "corrupt", which is the lesson the
    field learned the hard way.
30. `export_html()` → `"emitted": ["csv/progress_entries.csv"]`, `"removed": []`,
    `"unowned": []`, `"diverged": []`; `bytes: 114369`.
31. `gate_run()` → **`ready: true`**; every gate `pass`
    (`G-IDS`, `G-DEC-STATUS`, `G-REQ-SRC`, `G-TRACE`, `G-SET`, `G-PROGRESS`, `G-COMPLETE`,
    `G-REL`; `requirements_unwired` advisory).
32. `package_verify()` → `"verified": true`, `"foreign": []`, `"foreign_csv": []`,
    `"files": 27`, `"dirty": []`,
    `digest 7ab7df8bccc25a81060a4b88cdf6f5a806be73a7fbf83fc1520f88a74e609256`.
33. `readiness_check("package")` → `ready: false` on the scenario's deliberately-open items and
    **nothing else**: `acs-met` `["AC-003", "AC-005"]`, `open-questions-resolved` `["OQ-001"]`,
    `open-questions-overdue` `["OQ-001"]`, `clarifications-open`
    `["FR-006.statement -> OQ-001"]`, `lessons-confirmed` `["LL-002"]`, `defects-minor`
    **`waived`**, `prose-ids-resolve` `pass`.
    `entity_query("progress-entry")` → `total: 23` (21 at baseline, +PE-022 the unlock journal,
    +PE-023 the beat's note). `package_close()` → ok; `data/.lock` absent.

### Mechanism → observed

| Mechanism (plan) | Verdict |
|---|---|
| Lock observation: `observed: not-running` in `package_open`'s refusal (063) | **observed** (step 6) |
| Lock-free `package_migrate` preview: `read while locked` (063) | **observed** (step 7) |
| `package_unlock` report stage, `would_unlock`, nothing written (064) | **observed** (step 8) |
| `package_unlock(confirm=True)` → removal + `forced-override` journal row (064) | **observed** (steps 9–10) |
| Live holder REFUSED, naming `alive` (064) | **observed** (step 11) |
| `csv/` retired-table cleanup + operator's file left `unowned` (065) | **observed** (steps 24–26) |
| `package_verify.foreign_csv` names foreign CSV files (065) | **observed** (step 24) |
| `server_info` `package` row (066) | **observed** (step 12) |
| `server_info(detail=True)` entity types + relation rules (066) | **observed** (step 13) |
| Export envelope `partial` (067) | **observed** (steps 20–21) |
| `package_verify(expect=)` → `matches_expected` true, then false (067) | **observed** (steps 22, 29) |
| `omitted_columns` (068) | **observed** (step 14) |
| `matched` — WHERE the search hit (068) | **observed** (step 14) |
| The plan-068 lesson `next` hint | **not observed** — it is a `lesson`-path hint, and this beat wrote no lesson; beat 10 owns the lessons path. No lab-reachable call on this fixture surfaces it without inventing a lesson the scenario does not need. |
| Readiness rule `population` (069) | **observed** (step 15: `defects-closed`, `lessons-confirmed`) |
| `prose-ids-resolve` catches a phantom id, clears on correction (070) | **observed** (steps 18–19) |
| Stock prompts refreshed to the 4.9.0 bodies (071) | **observed** (step 27) |

### Findings

1. **`WVR-002` swallowed DEF-005 without being asked to.** Beat 15's whole-rule waiver on
   `defects-minor` has no `applies_to`, so the new open-low DEF-005 written by THIS beat was
   already `waived` the moment it existed: `readiness_check` step 33 reports
   `"waived": [{"entity": "DEF-003", "waiver": "WVR-001"}, {"entity": "DEF-004", "waiver": "WVR-002"}, {"entity": "DEF-005", "waiver": "WVR-002"}]`.
   That is the documented meaning of a whole-rule waiver, and the engine did report it rather
   than pass silently — but it is worth saying out loud that a rule-scoped waiver keeps
   absorbing rows written long after the operator approved it. `lab/scenario.md`'s pass-bar
   paragraph was updated to name DEF-005 for exactly this reason, so the fixture's own text
   does not call it a finding later.
2. **`entity_types` is a list, not a map.** `server_info(detail=True)["entity_types"]` returns
   37 list entries of `{"type", "table", "id_prefix"}`; the plan's phrasing ("the `defect`
   entry") reads as if it were keyed. Nothing is wrong — recorded so the next beat's driver
   does not index it as a dict.
3. **The export envelope stamps `"version": "4.8.1"`.** The fixture's committed
   `exports/beat16-defects.json` therefore carries the pre-release version string, exactly as
   `prompts/README.md`'s version line will read stale by one line after the reviewer cuts
   v4.9.0 (the plan's own maintenance note). Expected, not a defect.
4. **No `reused` outcome.** The OS did not recycle pid 366344 in the instant between the child
   exiting and `package_open` probing, so the observation was `not-running` throughout — the
   plan's primary expectation, not its acceptable alternative.

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
  …
  pass     A dead holder's lock was removed through the sanctioned tool and journaled (plan 064).
  pass     The unlock journal row is a typed forced-override naming the observation (plans 063-064).
  pass     The beat's note quotes what the store OBSERVED about the dead holder (plan 063).
  pass     A live holder's lock was refused, and the note says so (plan 064).
  pass     The phantom id was caught and then corrected out of the defect's prose (plan 070).
  pass     The beat's note names the prose-ids-resolve finding (plan 070).
  pass     The export FILE says it is partial (plan 067).
  pass     The fixture's prompt guide carries the 4.9.0 stock body (plans 064, 071).
  pass     No orphan CSV survives in the fixture (plan 065).
PASS  lab-tracker

1 case(s) checked, 0 failed, 0 skipped
```

(**44 `pass` lines, 0 fail, 0 skip** — 35 before the beat, +9. The nine assertions were
appended to the `lab-tracker` case exactly as plan 073 proposed them; **no needle was adapted**,
because every one matched the verbatim text above.)

```
$ python check.py
  …
PASS  lab-tracker

3 case(s) checked, 0 failed, 6 skipped

ALL CHECKS PASSED
```

### Verbatim refusal texts (the three the beat's note quotes)

1. `package_open` on a dead holder's lock:
   `…\package\data\.lock exists — another writer owns this package (held by pid 366344 on Anas-PC since 2026-09-21T04:48:00+00:00; observed: not-running - no process with pid 366344 is running on this host). If the writer is gone, the server's package_unlock(name) reports the holder and removes the lock only on the operator's word`
2. `package_unlock(confirm=True)` on a LIVE holder's lock:
   ``package 'package': the lock's holder was observed `alive` (pid 370136 is the very process that wrote the lock (exact start identity)) - not removed. Only a holder observed not-running or reused is unlocked by this tool; a manual removal of data/.lock stays the deliberate path when YOU know what this host cannot see``
3. `readiness_check`'s advisory, on the phantom id:
   `prose-ids-resolve` → `entities: ["DEF-005.title -> RISK-909"]`
