# Lab continuation report — beat 13, v4.6.0 RC (plan 040, 2026-09-06)

> The execution agent's report from `lab/scenario.md` beat 13 (the retire continuation:
> the `relates_to` residue, the typed edge retire + the server's `correction` row, the two
> retire refusals, the three-bucket audit split), archived **verbatim** below the header.
> Context: an INCREMENTAL real-agent session (`actor: agent:lab-continuation-040`) against
> the recorded `lab-tracker` fixture, driven in-process through the working-tree server
> (`plugins/tamheed/server/`, the uncommitted plan-040 tree), three scripts plus one
> read-only lookup, every script ending in `package_close()` (in a `finally`). The
> session's writes replaced the fixture (`data/`, `csv/`, `review.html`, and — new this
> beat, via `refresh_stock=True` — six files under `prompts/`); no file under `tests/`,
> `evals/evals.json`, `evals/pkg_check.py`, `lab/`, or `plugins/` was edited. All three eval
> commands green (`pkg_check gates`, `run_evals` 22/22, `check.py` ALL CHECKS PASSED). A
> `data/` backup (26 files) was taken to the scratch dir before the first write and was
> never restored from.

---

## Tamheed v4.6.0 lab continuation — beat 13 — execution report

### Numbered tool-call log (in-process handler calls + key outcomes)

Script 1 (package CLOSED):

1. `package_migrate("package")` — **refused as expected** (verbatim below). `data/.lock` absent afterwards; `git status` showed the fixture untouched.

Backup: `cp -r package/data → <scratch>/lab040-backup/data` (26 files) — before script 2.

Script 2:

2. `package_open("package")` — ok
3. `package_verify()` — ok: `verified: true`, `files: 26`, `dirty: []`, `foreign: []`, `memory_matches_disk: true`, `recorded: null`, digest **D1** (below)
4. `trace_query("SC-002")` — ok: exactly one edge `{"from": "SC-002", "to": "DEC-001", "relation": "amends"}`, `count: 1`
5. `entity_upsert([{"type":"trace-edge","from_id":"SC-002","to_id":"DEC-001","relation":"relates_to"}])` — **accepted**: `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": null}]}` (the escape hatch is always legal)
6. `trace_query("SC-002")` — ok, BOTH edges, verbatim: `{"ok": true, "edges": [{"from": "SC-002", "to": "DEC-001", "relation": "amends"}, {"from": "SC-002", "to": "DEC-001", "relation": "relates_to"}], "count": 2}`
7. **THE RETIRE** — `entity_upsert([{"type":"trace-edge","from_id":"SC-002","to_id":"DEC-001","relation":"relates_to","retire":True}])` — verbatim: `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": null, "retired": true, "retire_audit": "PE-016"}]}`
8. `trace_query("SC-002")` — ok: only `amends` left — `{"ok": true, "edges": [{"from": "SC-002", "to": "DEC-001", "relation": "amends"}], "count": 1}`
9. `entity_query("progress-entry", id="PE-016")` — the server's own row, verbatim: `{"id": "PE-016", "event_type": "correction", "entry": "EDGE RETIRED: SC-002 -relates_to-> DEC-001 (retire: true on the caller's write) — the corrected edge, if any, is written in the same batch", "subject_id": "SC-002", "actor": "system:edge-retire", "corrects": null, "phase_id": null, "slice_id": null, "occurred_at": "2026-09-06T12:18:36Z", "custom_attributes": null, "last_referenced": null}`
10. Refusal (a) — retire the same (now absent) triple again — **refused** (both layers verbatim below), `applied: 0`
11. Refusal (b) — `{"type":"trace-edge","from_id":"SC-002","to_id":"DEC-001","relation":"amends","retire":True,"note":"x"}` — **refused** (both layers verbatim below), `applied: 0`
12. `trace_query("SC-002")` after (b) — the `amends` edge still stands: `{"ok": true, "edges": [{"from": "SC-002", "to": "DEC-001", "relation": "amends"}], "count": 1}`
13. `gate_run()` (before the placeholder) — `ready: true`; `gates["G-REL"]` verbatim: `{"status": "pass", "mistyped": [], "note": "stored edges must satisfy RELATION_RULES; retype a wrong edge in ONE entity_upsert batch: {retire: true} on the old triple + the correct relation (relates_to only when no typed relation fits and the link itself is real)"}`; `gates["audit_evidence"]` verbatim: `{"evidenced": 3, "narrated": 0, "ungraded": 0, "narrated_ids": [], "ungraded_ids": [], "note": "over each active AC's LATEST verdict (superseded verdicts are history, as acs-met reads them): narrated = a graded verdict with no evidence — the graded party grading itself (C7); ungraded = a Pending placeholder nobody has graded"}` — **evidenced is 3, not the 2 the beat text predicted** (see Findings 1)
14. Pre-write reads: ACs `AC-001` (FR-001/SL-001), `AC-002` (FR-002/SL-002), `AC-003` (FR-002/SL-002), all Approved, `retired_in: null`, `total: 3`. AVs: `AV-001` AC-002 Met evidenced, `AV-002` AC-001 Met evidenced, `AV-003` AC-003 **Not-met with evidence** `"trakcer typo intentionally left under WVR-001"` (`verified_by: agent`, `inspection`), `total: 3`. `FR-004` = `{"id": "FR-004", "title": "Show task history", "lifecycle_status": "Approved", "mvp": 1}`. `SL-002` = `{"id": "SL-002", "title": "Date logic & team quality bar", "lifecycle_status": "Implemented"}`.
15. `entity_upsert` AC-004 full row, born Approved (`id: AC-004`, `title: "CSV export writes one row per task"`, `statement: "Given tasks exist in tasks.json, when `export` is run, then a CSV file with one row per task (id, title, due, done) is written beside tasks.json and the command exits 0."`, `requirement_id: FR-004`, `slice_id: SL-002`, `lifecycle_status: Approved`, `introduced_in: 1`) — **accepted first time**: `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "AC-004"}]}` (no birth-as-Approved refusal; the Proposed→Approved fallback was not needed)
16. `audit_record([{"ac_id":"AC-004","verdict":"Pending","verified_by":"agent","verification_method":"inspection"}])` — no evidence, deliberately — `{"ok": true, "ids": ["AV-004"]}`
17. `gate_run()` — `ready: true`; `G-PROGRESS` `{"status": "pass", "failures": []}`; `audit_evidence` verbatim: `{"evidenced": 3, "narrated": 0, "ungraded": 1, "narrated_ids": [], "ungraded_ids": ["AV-004"], "note": …same…}`. AC-003's verdicts untouched.
18. `readiness_check("package")` — `ready: false`. Every non-pass rule (verbatim, nothing else failed):
    - `acs-met` blocking **fail** `["AC-003", "AC-004"]` — note: `every active AC's LATEST verdict must be Met (verdicts append — an old Met does not survive a newer Not-met)`
    - `defects-minor` advisory **waived** `entities: []`, `waived: [{"entity": "DEF-003", "waiver": "WVR-001"}]`
    - `open-questions-resolved` advisory fail `["OQ-001"]`, `discriminating: false` (pre-existing)
    - `open-questions-overdue` advisory fail `["OQ-001"]` (pre-existing, by calendar)
    - `clarifications-open` advisory fail `["FR-006.statement -> OQ-001"]` (pre-existing)
    - `lessons-confirmed` advisory fail `["LL-002"]` (by design)
    - `lessons-note-budget` advisory **pass**, `entities: []`, note: `the always-loaded CLAUDE.md note renders 0 lesson line(s) against a curation ceiling of 20` (the beat-12 wording finding is fixed in this tree)
19. `progress_update([{entry: "Beat 13 (plan 040, v4.6.0 RC): wrote the relates_to residue beside SC-002 -amends-> DEC-001, retired it through {retire: true} (server correction row appended), confirmed both retire refusals, added AC-004 (FR-004/SL-002, Approved) with one Pending placeholder verdict so audit_evidence reads the three buckets.", event_type: "note", actor: "agent:lab-continuation-040", subject_id: "SC-002"}])` (`subject_id` added beyond the scripted three keys) — `{"ok": true, "ids": ["PE-017"]}`
20. `package_close()` — ok; `data/.lock` absent.

Script 3:

21. `package_open` — ok; `readiness_check` re-read: `acs-met` fail `[AC-003, AC-004]`, `lessons-confirmed` fail `[LL-002]`, `lessons-note-budget` pass (as in 18).
22. `handoff_emit("<scratch>/lab13/handoff-target", refresh_stock=True)` (fresh empty dir) — ok. Result keys: `ok, written, unchanged, diverged, prompt_library, project_prompts, converted_prompts, stale_references, restated_content, warnings`. `written: [".mcp.json", "CLAUDE.md"]`, `stale_references: []`, `restated_content: []`, `project_prompts: ["project-kickoff.md"]`, `warnings: ["6 stale-stock prompt(s) refreshed to the current template (refresh_stock)"]`. `prompt_library` (the keys relied on): `refreshed: ["prompts/drift-register.md", "prompts/integrity-check.md", "prompts/progress-sync.md", "prompts/README.md", "prompts/register-liveness.md", "prompts/replan-deferred.md"]` (6 — these were the stale-stock set), `unchanged: [defect-triage, generate-report, loop-guard, loop-iteration, orient-resume, package-onboarding, phase-close, release-close-out, skill-promote, slice-kickoff, slice-review]` (11, current), `diverged_customized: []`, `diverged_stale_stock: []` (after refresh), `diverged: []`, `emitted: []`.
23. Read the emitted `CLAUDE.md` — the cheat-sheet `entity_upsert` line carries `retire: true` (verbatim below).
24. `export_html()` — ok: `review.html` 98,356 bytes; csv emitted: `acceptance_criteria`, `audit_verdicts`, `progress_entries` (the three touched tables; `trace_edges.csv` unchanged — the residue was written and retired, net zero); 21 unchanged; diverged [].
25. `gate_run()["ready"]` — **`true`**; `audit_evidence` still `evidenced: 3, narrated: 0, ungraded: 1, ungraded_ids: ["AV-004"]`.
26. `package_verify()` — ok: `verified: true`, `files: 26`, `dirty: []`, `foreign: []`, `memory_matches_disk: true`, digest **D2 ≠ D1** (below — by construction: three `data/` files were rewritten this beat).
27. `package_close()` — ok; `data/.lock` absent after every script.
28. `review.html` (Grep, not a jsonl read) — line 179, inside the execution table's `<tbody>`, verbatim: `<tr><td>AC-004</td><td>CSV export writes one row per task</td><td>Approved</td><td>Pending</td><td>ungraded</td><td></td></tr>`; line 175 summary: `Audit evidence: 3 evidenced / 0 narrated / 1 ungraded`.

Read-only lookup (idle open → `entity_query` → close; `git status` count unchanged at 13 before and after): requirements = FR-001 Add a task, FR-002 List open tasks, FR-003 Mark done, **FR-004 Show task history**, FR-005 Persist, FR-006 Recurring (Proposed, the OQ-001 marker), **FR-007 CSV export** (Approved, mvp 0), NFR-001 Stdlib only. `trace_query("AC-004")` → `edges: [], count: 0` (ACs bind through their columns; no edge was scripted).

Step 12 (repo root):

29. `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`, all eight `G-*=pass`, `audit_evidence=evidenced:3/narrated:0/ungraded:1`, exit 0
30. `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → `PASS lab-tracker`, **22 assertions pass** (incl. the three plan-040 ones: the `EDGE RETIRED: SC-002 -relates_to-> DEC-001` row present, no `relates_to` residue in `trace_edges`, `narrated:0/ungraded:1`), `1 case(s) checked, 0 failed, 0 skipped`, exit 0
31. `python check.py` → tail: `3 case(s) checked, 0 failed, 6 skipped` / **`ALL CHECKS PASSED`**, exit 0

Fixture files changed by the session (`git status --porcelain evals/sample-results/lab-tracker`, 13 files): `data/acceptance_criteria.jsonl`, `data/audit_verdicts.jsonl`, `data/progress_entries.jsonl`, `csv/acceptance_criteria.csv`, `csv/audit_verdicts.csv`, `csv/progress_entries.csv`, `review.html`, and the six refreshed `prompts/` files (`README.md`, `drift-register.md`, `integrity-check.md`, `progress-sync.md`, `register-liveness.md`, `replan-deferred.md`). Nothing else. `data/trace_edges.jsonl` is byte-identical to the recorded fixture.

### Emitted CLAUDE.md — the quoted line (verbatim)

The only line containing `retire`, the cheat-sheet's `entity_upsert` bullet:

```
- `entity_upsert(entities=[{type, id, ...}])` — FULL rows, even for updates; `{type: trace-edge, from_id, to_id, relation, retire: true}` removes that edge (journaled — retype in ONE batch: retire + the corrected edge)
```

### Scenario ✔ ticks — observed vs missed

| Beat-13 tick | Result |
|---|---|
| `package_migrate` preview refused verbatim as in beat 12 | observed (step 1) |
| The residue: `SC-002 relates_to DEC-001` accepted beside `amends`; `trace_query` shows BOTH | observed (steps 5–6) |
| THE RETIRE: `retired: true`, `retire_audit: PE-nnn`; `trace_query` shows only `amends`; the server's `correction` row (actor `system:edge-retire`, entry `EDGE RETIRED: SC-002 -relates_to-> DEC-001 …`) quoted | observed (steps 7–9, PE-016) |
| Two refusals verbatim: absent triple ("nothing to retire (an attempt is not a write)"); extra key ("exactly from_id, to_id, relation") | observed (steps 10–11; both are substrings of the full texts — see below) |
| `gate_run`'s G-REL note names `{retire: true} on the old triple` | observed (step 13) |
| The audit split: AC-004 (SL-002 AND FR-004; Approved) + ONE Pending placeholder with `verified_by: agent`, `verification_method: inspection` → `narrated: 0, ungraded: 1, ungraded_ids: [AV-004]`; AC-003's Not-met untouched | observed (steps 15–17) — **except the `evidenced: 2` figure: the counter reads 3** (Findings 1) |
| `readiness_check`: `acs-met` now also names AC-004; `lessons-note-budget` passes; `lessons-confirmed` nags LL-002 | observed (step 18) |
| `handoff_emit` re-run: the cheat-sheet's `entity_upsert` line teaches `retire` | observed (steps 22–23) |
| `export_html` labels AC-004 `ungraded` in the execution table; `gate_run` ready; `package_close`; fixture updated | observed (steps 24–28) |

Missed: none. Every mechanism fired; one expected NUMBER in the scenario/beat text is wrong (below).

### Findings

1. **`evidenced: 2` in the scenario and the beat text is wrong — the counter reads 3, and 3 is correct.** `lab/scenario.md` beat 13 says `audit_evidence` reads `evidenced: 2, narrated: 0, ungraded: 1`, and the beat instructions predicted `evidenced 2 / narrated 0 / ungraded 0` before the placeholder "— AC-003's latest is an evidenced Not-met". That parenthetical is exactly why the number is 3: AC-003's latest verdict `AV-003` (Not-met) carries evidence (`trakcer typo intentionally left under WVR-001`), so all three pre-existing ACs are in the evidenced bucket; the beat-12 report already recorded `audit_evidence 3 evidenced / 0 narrated`. Nothing in the eval pins the evidenced count (the assertion substring is `narrated:0/ungraded:1`, which holds). Recommend correcting the scenario line to `evidenced: 3` — a doc fix, not an engine one; not edited here (`lab/` is off-limits to this agent).
2. **AC-004 is bound to FR-004 as scripted, but FR-004 is "Show task history" — the export requirement is FR-007 ("CSV export", Approved, mvp 0).** Both the scenario ("bound to `SL-002` AND `FR-004`") and the beat text name FR-004, so the fixture now carries an AC whose Given/When/Then is about the export path bound to the history requirement. Mechanically harmless (the column is a plain FK; FR-004 is MVP so G-TRACE was already satisfied by other edges and does not read ACs; the requirement auto-advance trigger sees a Pending, not a Met, so FR-004 did not move). Semantically it is a mis-binding in the eval fixture that a future beat or a scenario fix should retarget to FR-007 (supersede AC-004 — approved ACs are immutable). Reported, not fixed.
3. **AC-004 was born Approved on an already-`Implemented` slice (SL-002) with no objection from any guard.** The immutability trigger only fires on UPDATE, there is no birth guard, and no package-scope readiness rule flags an open AC under an Implemented slice (`acs-met` names the AC, not the slice). By design as far as the DDL goes; worth knowing that "slice Implemented" is not a lock on adding acceptance criteria to it.
4. **Both retire refusals are two-layered** (the beat-12 finding 2 shape): top-level `error` is the generic `batch rolled back — one or more items violated constraints`; the actionable sentence is in `items[0].error`. The scenario's quoted fragments are substrings of the full `items[0].error` texts (`no such edge SC-002 -relates_to-> DEC-001 — nothing to retire (an attempt is not a write)` and `a retire item carries exactly from_id, to_id, relation — got ['from_id', 'note', 'relation', 'to_id']`), same as beat 12's finding 3 on the migrate text. Fine if "verbatim" means the recorded text.
5. **The refresh classified 6 stale-stock files, where beat 12 reported 9.** Beat 12's `diverged_stale_stock` named defect-triage, integrity-check, loop-guard, loop-iteration, orient-resume, package-onboarding, README, register-liveness, slice-kickoff (9). This session refreshed drift-register, integrity-check, progress-sync, README, register-liveness, replan-deferred (6) and reported the other eleven as `unchanged` (byte-equal to the current stock). Checked, not inferred: `git log -- evals/sample-results/lab-tracker/package/prompts/` shows the fixture's prompts were last touched by the v4.5.0 release commit `a3bd91f` (after beat 12 ran), which is where the nine were refreshed; the six stale now are exactly the stock files the uncommitted plan-040 tree edits (`git diff --stat -- plugins/tamheed/prompts/` names README, integrity-check, progress-sync, register-liveness, stock-history.json) plus two whose stock moved with them. The mechanism behaved as designed each time; the "stale" set is a function of the stock you run against. `diverged_stale_stock: []` after refresh.
6. **`lessons-note-budget` note wording is fixed** in this tree: it now reads `the always-loaded CLAUDE.md note renders 0 lesson line(s) against a curation ceiling of 20` on the pass (beat-12 finding 1 closed).
7. **`open-questions-resolved` and `clarifications-open` also fail on OQ-001** — not in the beat's expected list by name, but both are the same OQ-001 the pass bar names, pre-existing since beats 1/8, untouched. Not chased.
8. Everything else behaved exactly as documented: the retire deleted exactly the triple (the `amends` edge survived both the retire and the extra-key refusal), the `correction` row landed in the same transaction with the retire (PE-016 precedes the closing note PE-017), the relation rule was not consulted on retire, G-PROGRESS did not trip between the AC write and the verdict (both landed before the next `gate_run`), `review.html` renders the third bucket by name, the lock was released after every script including the closed-package refusal, and the closing flush left the fixture byte-canonical (steps 26 and 30).

### Verbatim refusal texts and digests

Step 1 — `package_migrate("package")`, package closed (`ok: false`, `error`):

```
package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate
```

Step 10 — retire of the absent triple (top-level `error`, then `items[0].error`):

```
batch rolled back — one or more items violated constraints
```
```
no such edge SC-002 -relates_to-> DEC-001 — nothing to retire (an attempt is not a write)
```

Step 11 — retire item with the extra key `note` (top-level `error`, then `items[0].error`):

```
batch rolled back — one or more items violated constraints
```
```
a retire item carries exactly from_id, to_id, relation — got ['from_id', 'note', 'relation', 'to_id']
```

Digest D1 (step 3, before any write this beat):

```
68897addb465eea8dca33af561c056972b5a675dfff10b6f646f3d416df958c6
```

Digest D2 (step 26, after `acceptance_criteria`, `audit_verdicts`, `progress_entries` were rewritten):

```
fc96eb99aa26344c8c36b9792a1a1ecdf9972eb22d32a824f65fc40896ea4c65
```

PE-016 `entry` (verbatim) / `actor` / `event_type` / `subject_id`:

```
EDGE RETIRED: SC-002 -relates_to-> DEC-001 (retire: true on the caller's write) — the corrected edge, if any, is written in the same batch
```
```
system:edge-retire
```
```
correction
```
```
SC-002
```
