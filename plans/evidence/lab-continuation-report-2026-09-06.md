# Lab continuation report — beat 12, v4.5.0 RC (plan 039, 2026-09-06)

> The execution agent's report from `lab/scenario.md` beat 12 (the depth continuation:
> `package_verify`, keyset paging, `amends`, the server-only event refusal), archived
> **verbatim** below the header. Context: an INCREMENTAL real-agent session
> (`actor: agent:lab-continuation-039`) against the recorded `lab-tracker` fixture,
> driven in-process through the working-tree server (`plugins/tamheed/server/`), four
> scripts, every script ending in `package_close()`. The session's writes replaced the
> fixture (`data/`, `csv/`, `review.html`); no eval or test file was edited. Both eval
> commands green (19/19 assertions). A `data/` backup was taken to the scratch dir
> before the first write and was never restored from.

---

## Tamheed v4.5.0 lab continuation — beat 12 — execution report

### Numbered tool-call log (in-process handler calls + key outcomes)

Script 1 (package CLOSED):

1. `package_migrate("package")` — **refused as expected** (text below). `data/.lock` absent afterwards (the migrate lock released).

Script 2:

2. `package_open("package")` — ok
3. `package_verify()` — ok: `verified: true`, `files: 26`, `dirty: []`, `foreign: []`, `memory_matches_disk: true`, `recorded: null`, digest **D1** (below)
4. `package_verify(record=True)` — on the operator's scripted words — ok: `recorded: "PE-014"`, digest still D1 (the digest is of the state BEFORE the row)
5. `entity_query("progress-entry", id="PE-014")` — ok; `event_type: "integrity-verified"`, `actor: "system:package-verify"`, `subject_id: null`; `entry` quoted below — it names `sha256:<D1>` exactly
6. `package_verify()` — ok: `verified: true`, `dirty: []`, digest **D2 ≠ D1** (below)
7. `entity_query("acceptance-criterion", columns=["id","title"], limit=1, after_id=None)` — `rows: [AC-001]`, `total: 3`, `next_after: "AC-001"`
8. same, `after_id="AC-001"` — `rows: [AC-002]`, `total: 3`, `next_after: "AC-002"`
9. same, `after_id="AC-002"` — `rows: [AC-003]`, `total: 3`, `next_after: null` — walk complete: ids seen `AC-001, AC-002, AC-003`, each once; `total` constant at 3 on every page
10. `entity_query("acceptance-criterion", ids=["AC-003","AC-001"])` (deliberately reversed) — full rows returned **in id order** `AC-001, AC-003`, `total: 2`, all 14 columns present (AC-001: "add/list/done/history round-trip", FR-001/SL-001, Approved; AC-003: "Help text is polished", FR-002/SL-002, Approved)
11. `entity_query("requirement", search="overdue", columns=["id","title"])` — 1 hit: `{"id": "FR-002", "title": "List open tasks, overdue flagged"}`, `total: 1`
12. `package_close()` — ok

Script 3:

13. `package_open` — ok
14. `entity_upsert` SC-002 Proposed (`decision_ref: "DEC-001"`, `iteration: 1`, description: export path may write a second file beside tasks.json) — ok
15. `entity_upsert` trace-edge `SC-002 —amends→ DEC-001` — ok (`"id": null` in items, as edges do)
16. `trace_query("SC-002")` — ok: exactly one edge `{"from": "SC-002", "to": "DEC-001", "relation": "amends"}`
17. `entity_upsert` trace-edge `SC-002 —amends→ SL-001` — **refused as expected** (text below; the endpoint-type sentence sits in `items[0].error`, the top-level `error` is the generic batch-rollback line)
18. `entity_upsert` SC-002 → Approved (full row, on the operator's scripted approval) — ok
19. `entity_query("decision", id="DEC-001")` — ok; rationale BEFORE: `Choosing the ENGINE is a two-way door (stays a DEC); the record SHAPE is one-way and was promoted to ADR-0001.`
20. `entity_upsert` DEC-001 full row (every column echoed back incl. `promoted_to: "ADR-0001"`, `source_kind`, `source_span`), rationale + one sentence — ok (no trigger objected to editing an Approved DEC — correct: DEC- is the mutable family, ADR- the immutable one)
21. `entity_query("decision", id="DEC-001")` RE-READ — ok; rationale AFTER: `Choosing the ENGINE is a two-way door (stays a DEC); the record SHAPE is one-way and was promoted to ADR-0001. Narrowed by SC-002 (2026-09-06): the export path may write a second file beside tasks.json — the CSV report — without that counting as a second store or reopening the engine choice.` — `lifecycle_status` still Approved, `promoted_to` still ADR-0001
22. `entity_upsert` SC-002 → Merged (full row) — ok, the LAST step
23. `readiness_check("package")` — `scope-changes-merged`: `status: "pass"`, `entities: []`
24. `progress_update([{"entry": "LL-002 confirmed by the agent", "event_type": "lesson-confirmed", "actor": "agent:lab-continuation-039"}])` — **refused as expected** (text below)
25. `entity_query("lesson", id="LL-002", columns=["id","lifecycle_status"])` — `Proposed` (unchanged)
26. `readiness_check("package")` — `ready: false`; `lessons-note-budget`: `status: "pass"`, `entities: []`; `lessons-confirmed`: `status: "fail"`, `entities: ["LL-002"]` (by design). Non-pass rules, all pre-existing from beats 8/10 and untouched: `acs-met` fail [AC-003], `defects-minor` waived (DEF-003 → WVR-001), `open-questions-resolved` fail [OQ-001], `open-questions-overdue` fail [OQ-001], `clarifications-open` fail [FR-006.statement -> OQ-001], `lessons-confirmed` fail [LL-002]
27. `package_close()` — ok

Script 4:

28. `package_open` — ok
29. `handoff_emit("<scratch>/lab12/handoff-target")` (fresh empty dir) — ok: `written: [".mcp.json", "CLAUDE.md"]`, `stale_references: []`, `restated_content: []`, `project_prompts: ["project-kickoff.md"]`; `prompt_library.diverged_stale_stock` names 9 files (defect-triage 4.3.0, integrity-check 4.2.1, loop-guard 4.0.0, loop-iteration 4.0.0, orient-resume 4.3.0, package-onboarding 4.3.0, README 4.3.0, register-liveness 4.3.0, slice-kickoff 4.1.0), `diverged_customized: []`, one warning (quoted under Findings). NOT refreshed — not in the script.
30. Read the emitted CLAUDE.md — the three lines quoted below all present.
31. `progress_update` closing note (event_type `note`, actor `agent:lab-continuation-039`, subject SC-002) — ok, `PE-015`
32. `export_html()` — ok: `review.html` 95,838 bytes; csv emitted: decisions, progress_entries, scope_changes, trace_edges (the four touched tables); 20 unchanged; diverged []
33. `gate_run()` — **`ready: true`**; G-IDS pass (60 ids), G-DEC-STATUS pass, G-REQ-SRC pass, G-TRACE pass, G-SET pass, G-PROGRESS pass, G-COMPLETE pass, G-REL pass; audit_evidence 3 evidenced / 0 narrated; requirements_unwired advisory []
34. `package_close()` — ok. `data/.lock` absent after every script.

Step 9 (repo root):

35. `python evals/pkg_check.py verify evals/sample-results/lab-tracker/package` → `verified=True files=26 dirty=[] foreign=[] loadable=True`, exit 0
36. `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → `PASS lab-tracker`, 19 assertions pass, `1 case(s) checked, 0 failed, 0 skipped`, exit 0

Fixture files changed by the session (git status, read-only): `data/decisions.jsonl`, `data/progress_entries.jsonl`, `data/scope_changes.jsonl`, `data/trace_edges.jsonl`, the four matching `csv/*.csv`, `review.html`. Nothing else.

### Emitted CLAUDE.md — the three quoted lines (verbatim)

C31 flush-rule sentence (inside the opening paragraph):

> `work_bind`, the closing `progress_update`, `export_html` and `handoff_emit` all FLUSH `data/*.jsonl` AFTER the commit they record, so the tree is dirty again the moment you finish recording: run `git status --porcelain -uall` immediately before ANY branch operation — never a memory of having committed.

Cheat-sheet lines:

```
- `entity_query(type, id?, status?, columns?, limit?, after_id?, ids?, search?)` — rows + total + next_after (page with after_id; quote a known set via ids; keyword-sweep via search)
- `package_verify(name?, record?)` — canonical round-trip of the on-disk store (per-file byte-equality, foreign files, digest); `record=true` journals it
```

### Scenario ✔ ticks — observed vs missed

| Beat-12 tick | Result |
|---|---|
| `package_migrate` preview refused (registry current, no foreign file) | observed (step 1) |
| `package_verify()` verified/dirty []/foreign []/memory_matches_disk true; `record=true` → `integrity-verified` row, actor `system:package-verify`, names the digest; second verify differs | observed (steps 3–6) |
| Paging: every id once, `total` constant, `next_after` null on the last page; two rows via `ids`; keyword `search` | observed (steps 7–11) |
| `amends`: SC- Proposed, amends edge to DEC-001, guard refuses amends→SL-001 verbatim; DEC- upserted with narrowed rationale, RE-READ, then SC- Merged; `scope-changes-merged` clean | observed (steps 14–23) |
| Caller-written `lesson-confirmed` refused naming the appending tool; LL-002 stays Proposed | observed (steps 24–25) |
| `lessons-note-budget` passes; `lessons-confirmed` still nags LL-002 | observed (step 26) |
| `handoff_emit` note carries the flush rule, the widened `entity_query` line, `package_verify` | observed (steps 29–30) |
| `export_html`; `gate_run` ready; `package_close`; fixture updated | observed (steps 32–34) |

Missed: none.

### Findings about the engine

1. **`lessons-note-budget` note wording is wrong when it passes.** The rule reports `status: "pass"`, `entities: []`, yet its note reads verbatim: `the always-loaded CLAUDE.md note renders 0 lesson line(s) — past the curation ceiling of 20 (an always-loaded surface degrades as instructions pile up): distil shared themes into a skill (skill-promote.md — promoted lessons graduate out of the note) or unpin what no longer needs to bind every session`. "renders 0 … — past the curation ceiling of 20" reads as a false statement on a pass (the `entities` list is `rendered[20:]`, so the note is describing what a fail would list — but the sentence is composed once for both outcomes and a reader sees it on the pass). Suggest the note say "N rendered against a ceiling of 20" and reserve the "past the ceiling … distil" clause for the fail case.
2. **The `amends` refusal is two-layered.** The top-level `error` is the generic `batch rolled back — one or more items violated constraints`; the sentence naming the allowed endpoint types lives in `items[0].error`. Correct, but a client that reads only `error` loses the actionable part (the same shape as the v4.0.0 report's forced-transition refusal).
3. **Scenario text vs actual refusal.** `lab/scenario.md` beat 12 quotes the migrate refusal as `"registry is current, and data/ holds no foreign audit-trail file — nothing to migrate"`; the server says `package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate`. A substring match, not verbatim — a doc nit, fine as-is if "verbatim" means "the recorded text".
4. **The fixture's own `prompts/` are stale stock.** `handoff_emit` reports 9 of 17 stock prompts as `STALE-STOCK` (byte-equal to 4.0.0–4.3.0 stock), with the warning: `9 stock prompt(s) are STALE-STOCK — byte-equal to an older release's stock, never customised: re-run with refresh_stock=true to update them safely (customised files are never touched by refresh)`. The classification worked exactly as designed; the observation is that the eval fixture ships an out-of-date prompt library and nothing in the eval asserts prompt freshness. Not refreshed here (unscripted write). Worth a scripted `refresh_stock=true` in a future beat, or an eval assertion.
5. **Cosmetic:** `handoff_emit` lists `.mcp.json` under `written`, and a plain `ls` of the target shows only `CLAUDE.md` — the dotfile is there, just hidden. Noted only so the next agent does not misread it.
6. **`open-questions-overdue` now fails on OQ-001** (alongside the long-standing `open-questions-resolved`). Pre-existing lab state, not touched — OQ-001's `due_by` is `2026-09-01` and today is 2026-09-06, so the rule (present since v4.0.0, commit 7f5482c) started failing by calendar, not by anything this session did. By design, but it is not in the v4.0.0 report's expected-non-pass list; worth naming in the scenario's pass bar so the next runner does not chase it.
7. Everything else behaved exactly as documented: the record row's digest matched D1 byte-for-byte, the second verify's digest moved with `verified: true` and `dirty: []`, paging used the same order as the cut (no repeat, no gap), `ids` returned id order not request order, the DEC- full-row upsert of an Approved row was accepted (mutable family), the lock was released after every script including the closed-package migrate refusal, and the closing flush left the fixture byte-canonical (step 35).

### Verbatim refusal texts and digests

Step 1 — `package_migrate("package")`, package closed:

```
package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate
```

Step 17 — `entity_upsert` trace-edge SC-002 —amends→ SL-001 (top-level `error`, then `items[0].error`):

```
batch rolled back — one or more items violated constraints
```
```
relation 'amends' does not allow scope-change -> slice (SC-002 -> SL-001); allowed from: scope-change; allowed to: adr, decision — use 'relates_to' for an untyped association
```

Step 24 — `progress_update` with `event_type: "lesson-confirmed"`:

```
entries[0]: event_type 'lesson-confirmed' is appended by the server only — via entity_upsert (the lesson confirm guard); a caller-written one would be a narrated record of a mechanical fact. Batch NOT applied.
```

Digest D1 (steps 3 and 4, before the `integrity-verified` row):

```
e41ece4870e1416240c45c3c552273de5aecd79da1a05636ac0708f0058301a0
```

Digest D2 (step 6, after PE-014 rewrote `progress_entries.jsonl`):

```
5d84001a6187312809e9ab1e03279349426be1fbd06e7b34218a595a5b1d8118
```

PE-014 `entry` (verbatim) / `actor`:

```
INTEGRITY-VERIFIED: canonical round-trip byte-identical over 26 file(s); digest sha256:e41ece4870e1416240c45c3c552273de5aecd79da1a05636ac0708f0058301a0 — of the store state BEFORE this row (recording rewrites progress_entries.jsonl, so the next verify's digest differs by construction); foreign files in data/: none
```
```
system:package-verify
```
