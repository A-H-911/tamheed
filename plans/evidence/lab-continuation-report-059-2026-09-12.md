# Lab continuation report — beat 15, v4.8.0 RC (plan 059, 2026-09-12)

> The execution agent's report from `lab/scenario.md` beat 15 (the advisor-audit continuation:
> the name guard, the stale-tree rollback, the born-Implemented refusal + force, the scoped
> `indeterminate` verdict, the whole-rule waiver, the omission revision, the CSV formula
> defusing, the note's skill screen), archived **verbatim** below the header. Context: an
> INCREMENTAL real-agent session (`actor: agent:lab-continuation-059`) against the recorded
> `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the plan-042–057 tree at `main` `094dd13`), seven scripts (plus
> one read-only orientation pass taken before the backup), every script that opens the package
> ending in `package_close()` (in a `finally`). Files touched =
> the fixture (`data/` — five modified `*.jsonl` plus the NEW `omissions.jsonl`, `csv/` — six
> files incl. the new `csv/omissions.csv`, `review.html`) + `evals/evals.json` (nine appended
> assertions on the `lab-tracker` case) + `lab/scenario.md`, `lab/README.md`, `evals/README.md`
> + this report. No file under `plugins/`, `tests/`, `check.py`, `evals/pkg_check.py`,
> `CHANGELOG.md` or any other fixture was edited. Exactly ONE hand edit of a `data/` file was
> made — the sanctioned stale-tree trigger on `risks.jsonl`, restored byte-for-byte from the
> backup before the next tool call and confirmed with `filecmp.cmp(shallow=False)`. Two `data/`
> files were READ by hand during orientation, against the exemplar's "no hand reads" discipline:
> `risks.jsonl` (inherent to the sanctioned edit — the exact stored bytes of the title had to be
> known before one character could be changed) and `waivers.jsonl` (convenience, to mirror
> WVR-001's full column set; `entity_query("waiver")` had already returned the same row). Every
> other read went through the tools. All three
> eval commands green (`pkg_check gates` ready=True, `run_evals` lab-tracker **35/35** — 26
> before the beat, +9 — `check.py` ALL CHECKS PASSED). A `data/` backup (26 files) was taken to
> `<scratch>/lab059-backup/data` before the first write; only `risks.jsonl` was restored from it.
>
> **Deviation (reported, not hidden):** `handoff_emit` was NOT pointed at
> `evals/sample-results/lab-tracker/workspace/`. The first successful emit did target it (step
> 31) and both emitted files — `.mcp.json` and `CLAUDE.md` — carry the **absolute path of the
> worktree that ran the beat**; they were deleted un-committed and the emit was re-run against a
> scratch directory (step 34), as beat 14 did. The plan's last proposed assertion
> (`grep-file {case_dir}/workspace/CLAUDE.md`) was therefore dropped per the plan's own
> instruction and replaced with an equivalent ninth assertion pinning plan 049's
> `indeterminate` verdict through the beat's closing note.

---

## Tamheed v4.8.0 lab continuation — beat 15 — execution report

### Numbered tool-call log (in-process handler calls + key outcomes)

Baseline (repo root, nothing written):

0. `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`,
   all eight `G-*=pass`, `audit_evidence=evidenced:3/narrated:0/ungraded:1`, exit 0.
   `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` →
   `PASS lab-tracker`, **26 `pass` lines, 0 fail, 0 skip**, exit 0.
   Drift check `git diff --stat 094dd13..HEAD -- evals/sample-results/lab-tracker lab
   evals/evals.json evals/README.md` → **empty**.
   Backup: `cp -r package/data → <scratch>/lab059-backup/data` (**26 files**) — before script 1.

Script 1 (package CLOSED):

1. `package_migrate("package")` — **refused as expected**, verbatim:
   `{"ok": false, "error": "package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate"}`.
   `_CURRENT is None` → True; `data/.lock` absent.
2. **THE NAME GUARD (plan 044)** — `package_open("../package")` — **REFUSED**, verbatim:
   `{"ok": false, "error": "invalid package name '../package' (kebab-case, [a-z0-9-], one segment)"}`.
   `_CURRENT is None` → True; `_CURRENT_NAME` → `None` (nothing was opened).

Script 2 — **THE STALE-TREE ROLLBACK (plan 043)**:

3. `package_open("package")` — ok.
4. The one sanctioned hand edit, made **with the package open**: `data/risks.jsonl`,
   `"title":"Date-boundary regressions"` → `"title":"Datx-boundary regressions"` (one character
   inside RISK-001's existing title). Bytes differ from the backup → True.
5. `entity_upsert([{type: "risk", id: "RISK-002", …full row mirroring RISK-001's columns…}])` —
   **REFUSED**, verbatim:
   `{"ok": false, "error": "data/ changed on disk since this session loaded it (risks.jsonl) — refusing to overwrite — the batch was NOT applied; close the package, reconcile data/ via git, then reopen and retry"}`.
   (Top-level `error`, not an item error — `_commit()`'s failure short-circuits the whole batch.)
6. `entity_query("risk")` — `count 1`, ids `['RISK-001']`; **`RISK-002` present: False** — the
   batch rolled back in memory too.
7. `package_close()` — verbatim:
   `{"ok": true, "package": "package", "flushed": false, "warning": "closed WITHOUT the final flush — data/ changed on disk since this session loaded it (risks.jsonl) — refusing to overwrite — the batch was NOT applied; close the package, reconcile data/ via git, then reopen and retry"}`.
   `data/.lock` absent after the warned close.
8. `shutil.copyfile(<backup>/risks.jsonl, data/risks.jsonl)` — restored;
   `filecmp.cmp(shallow=False)` → **True** (byte-for-byte).
9. `package_open("package")` — ok (clean).
10. `package_verify()` — verbatim:
    `{"ok": true, "package": "package", "files": 26, "foreign": [], "digest": "8e2881280bb8f8f6de2a379faf5f9f16f6491fc00c22648ce4ee8e935b3bd604", "recorded": null, "verified": true, "loadable": true, "dirty": [], "memory_matches_disk": true}`
    → **D1** = `8e288128…bd604` (the digest beat 14 closed at — nothing had changed).
11. `package_close()` — ok. `git status --porcelain -uall evals/sample-results/lab-tracker` →
    **empty** (the hand edit left no residue).

Script 3 — the writes:

12. `package_open("package")` — ok.
13. **BORN-IMPLEMENTED (plan 053)** — `entity_upsert([{type: "slice", id: "SL-003", title: "Export polish", phase_id: "PH-1", objective: "Polish the CSV/HTML export surface", sort_order: 3, lifecycle_status: "Implemented", …}])` — **REFUSED**, verbatim (two-layered as in beats 12–14):
    top-level `{"ok": false, "applied": 0, "error": "batch rolled back — one or more items violated constraints", …}`;
    `items[0].error`: `readiness: SL-003 cannot be created as Implemented — create it (Proposed/Approved), bind its work, then transition; or re-run this item with "force": true after EXPLICIT operator confirmation`.
    `entity_query("slice")` right after → `['SL-001', 'SL-002']` (no SL-003).
14. The SAME item with `"force": true` — **accepted**:
    `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "SL-003", "forced": true, "forced_audit": "PE-020"}]}`.
    The server's own typed row (`entity_query("progress-entry", id="PE-020")`), verbatim:
    `{"id": "PE-020", "event_type": "forced-override", "entry": "FORCED transition: SL-003 -> Implemented past blocking readiness failures (born-Implemented (no readiness measured)) — operator-confirmed override", "subject_id": "SL-003", "actor": "system:transition-guard", "corrects": null, "phase_id": null, "slice_id": null, "occurred_at": "2026-09-12T12:15:20Z", "custom_attributes": null, "last_referenced": null}`.
15. **SCOPED READINESS (plan 049)** — `readiness_check("slice", id="SL-003")` → `ready: true`,
    five rules; the two that measured nothing, verbatim:
    `{"rule": "acs-met", "severity": "blocking", "status": "indeterminate", "entities": [], "note": "ACs bound to this slice whose latest verdict is not Met — no active acceptance criteria in this scope; this rule cannot discriminate (bind ACs to this slice via slice_id)", "discriminating": false}`
    `{"rule": "wbs-done", "severity": "blocking", "status": "indeterminate", "entities": [], "note": "open work items in this slice — no work items in this scope; this rule cannot discriminate (create WBS- rows with slice_id)", "discriminating": false}`
    The other three (`defects-closed`, `defects-minor`, `execution-plan-approved`) read `pass`
    with no `discriminating` key — they measured real rows (DEF-* carry `found_in: SL-002`).
16. **THE WHOLE-RULE WAIVER** — `entity_upsert([{type: "waiver", id: "WVR-002", rule: "defects-minor", applies_to: null, justification: "cosmetic backlog carried to the docs sweep; operator-approved", approver: "operator", expires: null, …}])` — `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "WVR-002"}]}`.
17. `readiness_check("package")` → `defects-minor`, verbatim:
    `{"rule": "defects-minor", "severity": "advisory", "status": "waived", "entities": [], "note": "open medium/low defects — carrying them is legal, silence is not (plan 031: severity-thresholded blocking)", "waived": [{"entity": "DEF-003", "waiver": "WVR-002"}]}`
    — note the citation: the whole-rule waiver now covers DEF-003 too (see Findings 1).
18. **THE OMISSION REVISION (plan 051)** — `entity_upsert([{type: "omission", entity_type: "invariant", reason: "no invariants surfaced by the brief"}])` → `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": null}]}`.
19. The SAME `entity_type` with the reason revised (`"revised: invariants deferred to the export slice per DEC-002"`) → `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": null}]}` — **`applied: 1`, and the item carries NO `unchanged` key** (`"unchanged" in items[0]` → False). The revised reason landed.
20. `entity_query("omission")` — **refused by design**, verbatim:
    `{"ok": false, "error": "entity type 'omission' is write-only (composite key, no id column) — writable via entity_upsert; query edges via trace_query"}`.
    The revised text was therefore verified through the sanctioned read —
    `python evals/pkg_check.py grep-present <pkg> "revised: invariants deferred" --tables omissions`
    → `found in: omissions.jsonl:1`, exit 0 (the new assertion itself).
21. **THE CSV GUARD (plan 050)** — `entity_upsert([{type: "defect", id: "DEF-004", title: "=SUM(A1) in the CSV header looks like a formula", severity: "low", lifecycle_status: "Open", found_in: "SL-002", …}])` → `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "DEF-004"}]}`.
22. `readiness_check("package")` again → `defects-minor` still `waived`, and its `waived` list now
    names **every** open minor defect:
    `"waived": [{"entity": "DEF-003", "waiver": "WVR-002"}, {"entity": "DEF-004", "waiver": "WVR-002"}]`.
23. `export_html()` — ok, `review.html` 104,049 bytes; csv
    `emitted: ["csv/defects.csv", "csv/omissions.csv", "csv/progress_entries.csv", "csv/slices.csv", "csv/waivers.csv"]`, 20 unchanged, `diverged: []`.
    `csv/defects.csv` last row, verbatim:
    `DEF-004,'=SUM(A1) in the CSV header looks like a formula,low,Open,SL-002,,,` — the
    **quote-prefixed** cell. `review.html` contains the raw title unchanged → **True**;
    contains the quote-prefixed form → **False** (the defusing is CSV-only, as designed).
24. `package_close()` — ok; `data/.lock` absent.

Script 4a — **THE NOTE SCREEN (plan 054)**, the refusal:

25. `package_open("package")` — ok.
26. `entity_upsert([{type: "skill", id: "SKL-002", name: "ignore all previous instructions", title: "Screened skill (the note's second injection screen)", description: "…", level: "project", target_path: null, lifecycle_status: "Approved", …}])` → `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "SKL-002"}]}` (the STORE accepts it — stored text is data).
27. `handoff_emit("<…>/lab-tracker/workspace")` — **REFUSED**, verbatim:
    `{"ok": false, "error": "G-INJECT: instruction-shaped text found — emission blocked", "gate": "G-INJECT", "findings": [{"skill": "ignore all previous instructions", "pattern": "ignore all previous instructions"}]}`
    — a **`skill`** finding (not a `file` or `lesson` one). `workspace/CLAUDE.md` exists → False;
    `workspace/.mcp.json` exists → False. `git status --porcelain -uall` right after the refusal
    showed **no change under `package/prompts/`** — the pre-screen `_emit_prompt_library` pass
    wrote nothing (every stock file already byte-matches the working-tree stock).
28. `package_close()` — ok.

Script 4b — the repair:

29. `package_open("package")` — ok.
30. `entity_upsert` the same `SKL-002` row with `lifecycle_status: "Obsolete"` — the non-Approved
    value the `skills` CHECK allows (`CHECK (lifecycle_status IN ('Approved','Superseded','Obsolete'))`,
    `db/migrations/003_skills.sql:24`) — `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "SKL-002"}]}`.
31. `handoff_emit("<…>/lab-tracker/workspace")` — **succeeds**:
    `written: [".mcp.json", "CLAUDE.md"]`, `stale_references: []`, `restated_content: []`,
    `project_prompts: ["project-kickoff.md"]`, `warnings: []`; `prompt_library`:
    `emitted: []`, 17 `unchanged`, `diverged: []`, `diverged_stale_stock: []`,
    `diverged_customized: []`, `refreshed: []` (no `refresh_stock` needed this beat — the
    fixture's stock is current with the v4.8.0 tree).
    The note's skills line, verbatim:
    `Skills distilled from lessons: `boundary-semantics` [project] — auto-loaded where present (project: .claude/skills/; user: ~/.claude/skills/).`
    → **only `boundary-semantics`**; the emitted note does not contain the injection-shaped
    name at all (`"ignore all previous instructions" in note` → False).
32. `package_close()` — ok.
    **Then**: both emitted files were inspected and found to carry the absolute path of THIS
    worktree (`.mcp.json`'s `args`, and `CLAUDE.md` line 5's "under `…\lab-tracker`"); they were
    **deleted un-committed** and the emit re-run against a scratch target (step 34). See the
    header deviation and Findings 4.

Script 5 — the close:

33. `package_open("package")` — ok.
34. `handoff_emit("<scratch>/lab059-handoff")` (fresh directory, as beat 14 did) — same result as
    step 31: `written: [".mcp.json", "CLAUDE.md"]`, `warnings: []`, same 17-file `unchanged`
    prompt library, and the same skills line naming only `boundary-semantics`.
35. **The closing note** — `progress_update([{entry: <below>, event_type: "note", actor: "agent:lab-continuation-059"}])` → `{"ok": true, "ids": ["PE-021"]}`. The stored row
    (`entity_query("progress-entry", id="PE-021")`): `event_type: "note"`,
    `actor: "agent:lab-continuation-059"`, `subject_id: null`, `corrects: null`,
    `occurred_at: "2026-09-12T12:20:19Z"`; `entry` verbatim:

    `Beat 15 (plan 059, v4.8.0 RC): the advisor-audit mechanisms fired against the recorded package. NAMES (plan 044): package_open("../package") was REFUSED — invalid package name '../package' (kebab-case, [a-z0-9-], one segment) — and nothing was opened. THE STALE-TREE ROLLBACK (plan 043): one character was hand-edited inside RISK-001's title while the package was open; entity_upsert(RISK-002) was REFUSED — data/ changed on disk since this session loaded it (risks.jsonl) — refusing to overwrite — the batch was NOT applied; entity_query("risk") showed no RISK-002, package_close warned it closed WITHOUT the final flush, and risks.jsonl was restored byte-for-byte from the pre-beat backup (package_verify: verified true). BORN-IMPLEMENTED (plan 053): slice SL-003 "Export polish" was REFUSED — readiness: SL-003 cannot be created as Implemented — then accepted under force, and the server appended its own typed forced-override row PE-020 naming born-Implemented. SCOPED READINESS (plan 049): readiness_check("slice", SL-003) read acs-met and wbs-done as indeterminate with discriminating false — no ACs and no work items in that scope, so neither rule could discriminate. THE WHOLE-RULE WAIVER: WVR-002 on defects-minor with no applies_to made the rule read waived and its waived list name every open minor defect (DEF-003, DEF-004). THE OMISSION REVISION (plan 051): the invariant omission's reason was rewritten and the second write landed ok, never unchanged. THE CSV GUARD (plan 050): DEF-004's formula-shaped title exports to csv/defects.csv quote-prefixed while review.html renders it unchanged. THE NOTE SCREEN (plan 054): skill SKL-002, named after the classic prompt-injection phrase, blocked handoff_emit at gate G-INJECT with a skill finding; re-upserting SKL-002 as Obsolete let the emit through and the note's skills line names only boundary-semantics.`

    Fragment check on the STORED row: `invalid package name` → True; `NOT applied` → True;
    `cannot be created as Implemented` → True; `G-INJECT` → True; `indeterminate` → True.
36. `export_html()` (re-run after the note) — ok, `review.html` **108,692 bytes**; csv
    `emitted: ["csv/progress_entries.csv", "csv/skills.csv"]`, 23 unchanged, `diverged: []`.
37. `gate_run()["ready"]` — **`true`**.
38. *(script bug — a print on `gate_run`'s return shape raised `TypeError` after step 37, so the
    `finally` closed the package before `package_verify` ran; the close itself was clean and the
    verify was taken in the next script. Reported rather than hidden.)*
39. `package_close()` — `{"ok": true, "package": "package"}`; `data/.lock` absent.

Script 6 — the final read (idle open → read → close):

40. `package_open("package")` — ok.
41. `gate_run()` — `ready: true`; every gate `pass`: `G-IDS` (*"verified now: foreign_key_check
    clean, entity_index consistent (**74 ids**)"*), `G-DEC-STATUS`, `G-REQ-SRC`, `G-TRACE`,
    `G-SET`, `G-PROGRESS`, `G-COMPLETE`, `G-REL` (`mistyped: []`);
    `audit_evidence: {"evidenced": 3, "narrated": 0, "ungraded": 1, "ungraded_ids": ["AV-005"]}`
    (unchanged from beat 14); `requirements_unwired: []`.
42. `package_verify()` — verbatim:
    `{"ok": true, "package": "package", "files": 27, "foreign": [], "digest": "5f4c1731c83cca30a6e3518cf68298f07270b1359443902c630205c95e9b6570", "recorded": null, "verified": true, "loadable": true, "dirty": [], "memory_matches_disk": true}`
    → **D2** = `5f4c1731…b6570`, **27 files** (the new `omissions.jsonl`).
43. `package_close()` — ok; `data/.lock` absent; `data/*.jsonl` count = **27**.

Step 3 — the assertions (repo root):

44. Each of the nine new assertion commands was run standalone against the recorded fixture
    before being written into `evals/evals.json`; all nine exited 0
    (`count … forced-override --min 2` → `count=2`; `grep-present born-Implemented` →
    `progress_entries.jsonl:20, :21`; `count waiver --col applies_to=None --min 1` → `count=1`;
    `grep-present "revised: invariants deferred" --tables omissions` → `omissions.jsonl:1`;
    `grep-file csv/defects.csv "'=SUM(A1)"`; `grep-present "NOT applied"` →
    `progress_entries.jsonl:21`; `grep-present "G-INJECT"` → `progress_entries.jsonl:21`;
    `count skill --col name=… --col lifecycle_status=Approved --max 0` → `count=0`;
    `grep-present indeterminate --tables progress_entries` → `progress_entries.jsonl:21`).
    `evals/evals.json`: +123 lines, −0 (CRLF preserved, re-parsed as valid JSON;
    `lab-tracker.deterministic_assertions` = **35**).
45. `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` →
    `PASS lab-tracker`, **35 `pass` lines, 0 fail, 0 skip**, `1 case(s) checked, 0 failed,
    0 skipped`, exit 0 — every pre-existing assertion still passes.
46. `python evals/pkg_check.py verify evals/sample-results/lab-tracker/package` →
    `verified=True files=27 dirty=[] foreign=[] loadable=True`, exit 0.
47. `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`,
    all eight `G-*=pass`, exit 0.
48. `python check.py` → **`ALL CHECKS PASSED`**, exit 0.

### Scenario ✔ ticks — observed vs missed

| Beat-15 tick | Result |
|---|---|
| `package_migrate` preview REFUSED verbatim as before | observed (step 1) |
| NAMES: `package_open("../package")` → `invalid package name`; nothing opened | observed (step 2) |
| THE STALE-TREE ROLLBACK: refusal naming `risks.jsonl` + `NOT applied`; no new row; `WITHOUT the final flush`; restored byte-for-byte; reopen clean; `verified: true` | observed (steps 3–11) |
| BORN-IMPLEMENTED: `cannot be created as Implemented`, then `force` → `forced: true` + typed `forced-override` naming `born-Implemented` | observed (steps 13–14; `PE-020`) |
| SCOPED READINESS: `acs-met` / `wbs-done` → `indeterminate`, `discriminating: false` | observed (step 15) |
| THE WHOLE-RULE WAIVER: `WVR-002`, no `applies_to` → `defects-minor` `waived`, list names every open minor defect | observed (steps 16–17, 22) |
| THE OMISSION REVISION: second write `ok`, NOT `unchanged`; the table holds the revised text | observed (steps 18–20) |
| THE CSV GUARD: `csv/defects.csv` carries `'=SUM(A1)`; `review.html` unchanged | observed (steps 21, 23) |
| THE NOTE SCREEN: `handoff_emit` refused, gate `G-INJECT`, a `skill` finding; re-upsert non-Approved → emit succeeds; the skills line names only `boundary-semantics` | observed (steps 26–31, 34) |
| ONE closing `progress_update` note quoting the four fragments + `indeterminate` | observed (step 35; `PE-021`) |
| `export_html` re-run; `gate_run` ready; `package_close`; fixture updated; `package_verify()` green | observed (steps 36–43) |

Missed: none. Every mechanism fired exactly as the plans and the docstrings describe.

### Findings

1. **The whole-rule waiver SHADOWS the targeted one in the `waived` citation.** After `WVR-002`
   (rule `defects-minor`, `applies_to: null`) was written, `readiness_check("package")` reported
   `{"entity": "DEF-003", "waiver": "WVR-002"}` — not `WVR-001`, the waiver written for exactly
   that defect in beat 5. The selection rule is explicit in the code (`_readiness_report`'s
   `rule()` helper): `if whole_rule: waived.append({… whole_rule[0]}) elif ent in per_entity: …`
   — a whole-rule waiver is tested FIRST and wins for every entity, and only its first id is
   cited. Both waivers are live and the outcome (`waived`) is identical, so the verdict is not
   wrong; but the citation is the operator's audit trail, and an operator reading it cannot tell
   that DEF-003 also carries its own, narrower approval. Reported, not changed (out of scope for
   this beat).
2. **`entity_query` cannot read back an omission** (step 20): `omission` is write-only
   (composite key, no `id` column), so the beat's "the table holds the revised text" tick has to
   be checked through `pkg_check grep-present … --tables omissions` or the committed JSONL. The
   plan anticipated this by pinning the revision with a `grep-present` assertion; worth stating
   because the scenario text's "`entity_query`/the table" reads as if either route works. The
   scenario block committed with this beat says so explicitly.
3. **The omission added a 27th `data/` file and a 21st CSV.** `omissions.jsonl` did not exist in
   the recorded fixture (every Always family was present), so `package_verify()` now reports
   `files: 27` where beats 12–14 reported 26, and `export_html` emitted a new `csv/omissions.csv`.
   Any future beat quoting "26 files" is quoting a pre-beat-15 fixture. The `omission` row for
   `invariant` is *deliberately contradictory* with the store (the package DOES carry invariants):
   G-SET treats an omission purely as a suppressor for a MISSING family, so recording one for a
   present family changes no gate verdict — `G-SET=pass` before and after. That is the mechanism
   working as specified, but it means an omission row is never cross-checked against reality.
4. **`handoff_emit`'s output is machine-specific and therefore not fixture material.** The emitted
   `.mcp.json` embeds `PACKAGE_ROOT.resolve()` and the resolved server path; `CLAUDE.md`'s opening
   line embeds the package root too. Emitted into
   `evals/sample-results/lab-tracker/workspace/` they would have committed this worktree's
   throwaway path (`…/.claude/worktrees/agent-a35f0967d6a0171a8/…`) into the repo — and the
   plugin-install branch (`plugin_hosted = "/.claude/plugins/" in resolved`) does not fire for a
   worktree path, so `.mcp.json` is written, not skipped. Beat 14 had already chosen a scratch
   target for exactly this reason; beat 15 does the same, and the scenario block now records the
   rule. The plan's ninth assertion (`grep-file {case_dir}/workspace/CLAUDE.md`) was dropped and
   replaced with `grep-present {case_dir}/package indeterminate --tables progress_entries`, which
   pins plan 049's mechanism through the beat's own note.
5. **The born-Implemented refusal is two-layered** (the beat-12/13/14 shape): the top-level
   `error` is the generic `batch rolled back — one or more items violated constraints`; the
   sentence naming the guard is `items[0].error`. Recorded both.
6. **The stale-tree refusal is NOT two-layered** — it is a top-level `error` with no `items` key
   at all, because `_commit()` fails after every per-item savepoint has already been released.
   The practical consequence for an agent: a stale-tree failure gives you no per-item detail, and
   the whole batch (however large) is gone. `package_close()` then repeats the same sentence
   inside its `warning`, which is the operator's only signal that the session ended without a
   flush.
7. **`force` on a born-Implemented row measures nothing and says so.** `forced_note` is the
   literal string `born-Implemented (no readiness measured)` — distinct from the forced-past-
   blockers path, which lists the failing rules. Both land in the same `forced-override`
   `event_type`, so the two shapes are only distinguishable by the entry text; the new assertion
   `grep-present born-Implemented --tables progress_entries` pins that distinction.
8. **`readiness_check("slice", "SL-003")` reports `ready: true`** while two blocking rules read
   `indeterminate` — by the maintainer decision recorded at plan 049 (`ready` and the transition
   guard trip only on real `fail`). An operator skimming `ready` alone would read an empty,
   forced slice as clean; the `indeterminate` + `discriminating: false` pair is the whole signal.
   Worth keeping in front of the reader — the beat's pass bar now names it.
9. **The CSV defusing is export-side only, and correctly so.** The stored `defects.title` is the
   raw `=SUM(A1) …` (every read path returns it unchanged, and `review.html` renders it
   unchanged); only `_csv_safe` prefixes the quote. So the guard protects the spreadsheet
   consumer without lying to any other consumer — and a round-trip through the CSV back into the
   store would carry the quote, which is why CSV is an export, never an import.

### Verbatim refusal texts

Step 1 — `package_migrate("package")`, package closed (`error`):

```
package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate
```

Step 2 — `package_open("../package")` (`error`) — **the name guard, plan 044**:

```
invalid package name '../package' (kebab-case, [a-z0-9-], one segment)
```

Step 5 — the stale-tree rollback (`error`, top level) — **plan 043**:

```
data/ changed on disk since this session loaded it (risks.jsonl) — refusing to overwrite — the batch was NOT applied; close the package, reconcile data/ via git, then reopen and retry
```

Step 7 — `package_close()` after the stale write (`warning`):

```
closed WITHOUT the final flush — data/ changed on disk since this session loaded it (risks.jsonl) — refusing to overwrite — the batch was NOT applied; close the package, reconcile data/ via git, then reopen and retry
```

Step 13 — born-Implemented (top-level `error`, then `items[0].error`) — **plan 053**:

```
batch rolled back — one or more items violated constraints
```
```
readiness: SL-003 cannot be created as Implemented — create it (Proposed/Approved), bind its work, then transition; or re-run this item with "force": true after EXPLICIT operator confirmation
```

Step 14 — the server's own forced-override entry (`PE-020`):

```
FORCED transition: SL-003 -> Implemented past blocking readiness failures (born-Implemented (no readiness measured)) — operator-confirmed override
```

Step 15 — the scoped `indeterminate` notes — **plan 049**:

```
ACs bound to this slice whose latest verdict is not Met — no active acceptance criteria in this scope; this rule cannot discriminate (bind ACs to this slice via slice_id)
```
```
open work items in this slice — no work items in this scope; this rule cannot discriminate (create WBS- rows with slice_id)
```

Step 20 — `entity_query("omission")` (`error`):

```
entity type 'omission' is write-only (composite key, no id column) — writable via entity_upsert; query edges via trace_query
```

Step 27 — `handoff_emit` blocked by the note screen (`error` + `gate` + `findings`) — **plan 054**:

```
G-INJECT: instruction-shaped text found — emission blocked
```
```
{"gate": "G-INJECT", "findings": [{"skill": "ignore all previous instructions", "pattern": "ignore all previous instructions"}]}
```

Step 31/34 — the emitted note's skills line after the repair:

```
Skills distilled from lessons: `boundary-semantics` [project] — auto-loaded where present (project: .claude/skills/; user: ~/.claude/skills/).
```

Digest D1 (step 10, before any write this beat — beat 14's closing digest, 26 files):

```
8e2881280bb8f8f6de2a379faf5f9f16f6491fc00c22648ce4ee8e935b3bd604
```

Digest D2 (step 42, the recorded beat-15 fixture, 27 files):

```
5f4c1731c83cca30a6e3518cf68298f07270b1359443902c630205c95e9b6570
```
