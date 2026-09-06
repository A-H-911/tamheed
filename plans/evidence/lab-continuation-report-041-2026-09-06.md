# Lab continuation report — beat 14, v4.7.0 RC (plan 041, 2026-09-06)

> The execution agent's report from `lab/scenario.md` beat 14 (the export continuation:
> `entity_export` as the sanctioned read path for a committed script, the calibrated slate
> generator, the partial/whole export pair, the two export refusals, the `expect_unchanged`
> paste guard), archived **verbatim** below the header. Context: an INCREMENTAL real-agent
> session (`actor: agent:lab-continuation-041`) against the recorded `lab-tracker` fixture,
> driven in-process through the working-tree server (`plugins/tamheed/server/`, the
> uncommitted plan-041 tree), three scripts plus two read-only lookups, every script ending
> in `package_close()` (in a `finally`). Files touched = the fixture (`data/progress_entries.jsonl`,
> `csv/progress_entries.csv`, `review.html`, five refreshed `prompts/` files via
> `refresh_stock=True`, and — new this beat — three files under `package/exports/`) + the
> workspace generator `workspace/scripts/gen-slate.py` + its output `workspace/slate.html`.
> No file under `tests/`, `evals/evals.json`, `evals/pkg_check.py`, `lab/`, or `plugins/`
> was edited (the untracked `plans/041-findings24-entity-export-paste-guard.md` appeared in
> `git status` during the session — the plan file, not this agent's); no `data/*.jsonl` was read or edited by hand (every read went through the
> tools; the only file read directly was the agent's own export). All three eval commands
> green (`pkg_check gates` ready=True, `run_evals` lab-tracker **26/26**, `check.py` ALL
> CHECKS PASSED). A `data/` backup (26 files) was taken to
> `<scratch>/lab041-backup/data` before the first write and was never restored from.

---

## Tamheed v4.7.0 lab continuation — beat 14 — execution report

### Numbered tool-call log (in-process handler calls + key outcomes)

Script 1 (package CLOSED):

1. `package_migrate("package")` — **refused as expected**, verbatim: `{"ok": false, "error": "package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate"}`. `data/.lock` absent afterwards; `git status --porcelain evals/sample-results/lab-tracker` empty (fixture untouched).

Backup: `cp -r package/data → <scratch>/lab041-backup/data` (26 files) — before script 2.

Script 2:

2. `package_open("package")` — ok.
3. `package_verify()` — verbatim: `{"ok": true, "package": "package", "files": 26, "foreign": [], "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "recorded": null, "verified": true, "loadable": true, "dirty": [], "memory_matches_disk": true}` → **D1** = `48e5d2e3…a29b3` (full text below).
4. **THE EXPORT** — `entity_export("slate-rows.json", args={"type": "acceptance-criterion", "ids": ["AC-003", "AC-005"]})` (nothing between the verify and the export) — verbatim: `{"ok": true, "path": "C:\\Users\\ahammo\\Repos\\tamheed\\evals\\sample-results\\lab-tracker\\package\\exports\\slate-rows.json", "bytes": 1512, "tool": "entity_query", "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "memory_matches_disk": true, "count": 2, "total": 2, "partial": false}`. Checked in code: `digest == D1` → True; `"result" in r` → False; `"rows" in r` → False.
5. Read the export file (the agent's own file, not `data/`): top-level keys `['tamheed_export', 'result']`; `tamheed_export` keys `['version', 'package', 'tool', 'args', 'digest', 'memory_matches_disk']`, verbatim: `{"version": "4.7.0", "package": "package", "tool": "entity_query", "args": {"type": "acceptance-criterion", "ids": ["AC-003", "AC-005"]}, "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "memory_matches_disk": true}`; `result` keys `['ok', 'rows', 'count', 'total', 'next_after']`; `result.rows` holds the two whole rows (every column of `acceptance_criteria`):
   - `{"id": "AC-003", "title": "Help text is polished", "statement": "Given tick --help, then the text is typo-free and lists every command.", "requirement_id": "FR-002", "slice_id": "SL-002", "lifecycle_status": "Approved", "disposition": null, "disposition_reason_ref": null, "superseded_by": null, "introduced_in": 1, "retired_in": null, "source_kind": null, "source_span": null, "custom_attributes": null, "last_referenced": null}`
   - `{"id": "AC-005", "title": "CSV export writes one row per task", "statement": "Given tasks exist in tasks.json, when `export` is run, then a CSV file with one row per task (id, title, due, done) is written beside tasks.json and the command exits 0.", "requirement_id": "FR-007", "slice_id": "SL-002", "lifecycle_status": "Approved", "disposition": null, "disposition_reason_ref": null, "superseded_by": null, "introduced_in": 1, "retired_in": null, "source_kind": null, "source_span": null, "custom_attributes": null, "last_referenced": null}`
   The eval's pinned substring `Given tick --help` is present (AC-003's statement).
6. `package_close()` — ok.

The generator (committed at `evals/sample-results/lab-tracker/workspace/scripts/gen-slate.py`, 86 lines, stdlib: `html`, `json`, `sys`, `pathlib`):

7. `python evals/sample-results/lab-tracker/workspace/scripts/gen-slate.py evals/sample-results/lab-tracker/package/exports/slate-rows.json evals/sample-results/lab-tracker/workspace/slate.html` — exit 0, output verbatim:
   ```
   wrote evals\sample-results\lab-tracker\workspace\slate.html (2 rows, digest 48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3)
   verify AC-003: PASS (statement byte-exact in HTML)
   verify AC-005: PASS (statement byte-exact in HTML)
   calibrate AC-003: corrupted 1 char -> mismatch DETECTED
   all checks pass; verifier calibrated
   ```
   The page: `<h1>Review slate — package package</h1>`, `<p>export digest <code>48e5d2e3…a29b3</code> (tool entity_query, tamheed 4.7.0)</p>`, then one `<section id='AC-003'>` / `<section id='AC-005'>` each with `<h2>{id} — {title}</h2><pre>{html.escape(statement)}</pre>`. The verifier re-reads the export and the HTML **as bytes** and checks `html.escape(statement).encode("utf-8") in page_bytes`; the calibration replaces the first character of `rows[0].statement` in memory and re-runs the same check (exit 3 if it still passes). Exit codes: 0 pass · 1 verify failure · 2 not a tamheed export · 3 uncalibrated.
8. Refusal paths exercised: a JSON file without the envelope → `REFUSED: <path> is not a tamheed export (no 'tamheed_export' envelope) — export it with entity_export() first`, exit 2; a non-JSON file (`review.html`) → the same refusal, exit 2 (after one fix — see Findings 6). Determinism checked: the md5 of `slate.html` before and after a further run over the same export is `34b7fb2a873df15266941554d8c90a23` both times (the generator embeds no timestamp).

Read-only lookup (idle open → `entity_query` → close, `git status` count unchanged): `DEF-001` = `severity: "high"`, `lifecycle_status: "Fixed"`, `found_in: "SL-002"`; all defect severities `[('DEF-001', 'high'), ('DEF-002', 'low'), ('DEF-003', 'low')]`; `audit-verdict` `total: 5`. Taken so the scripted flip to `medium` would be a real change (Findings 2).

Script 3:

9. `package_open` — ok; `package_verify()` again → the same D1 (`dirty: []`, `memory_matches_disk: true`) — script 2 wrote nothing into `data/`.
10. `entity_export("verdicts.json", args={"type": "audit-verdict", "limit": 1})` — verbatim: `{"ok": true, "path": "C:\\Users\\ahammo\\Repos\\tamheed\\evals\\sample-results\\lab-tracker\\package\\exports\\verdicts.json", "bytes": 770, "tool": "entity_query", "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "memory_matches_disk": true, "count": 1, "total": 5, "partial": true, "note": "PARTIAL: 1 of 5 rows — the file has no payload cap; pass a limit above total (or page with after_id) to export the whole family"}`
11. Same path, `"limit": 1000` — verbatim: `{"ok": true, "path": "C:\\Users\\ahammo\\Repos\\tamheed\\evals\\sample-results\\lab-tracker\\package\\exports\\verdicts.json", "bytes": 2234, "tool": "entity_query", "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "memory_matches_disk": true, "count": 5, "total": 5, "partial": false}` — the existing export was overwritten (770 → 2234 bytes); the file's envelope `args` reads `{"type": "audit-verdict", "limit": 1000}` and `result.count == result.total == 5`.
12. `entity_export("gates.json", tool="gate_run")` — verbatim: `{"ok": true, "path": "C:\\Users\\ahammo\\Repos\\tamheed\\evals\\sample-results\\lab-tracker\\package\\exports\\gates.json", "bytes": 1933, "tool": "gate_run", "digest": "48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3", "memory_matches_disk": true}` — no `count`/`total`/`partial` keys (gate_run is not a paged tool; expected). The file's `result.ready` is `true`.
13. Refusal (a) — `entity_export("../data/x.json")` — verbatim: `{"ok": false, "error": "refusing to write inside the canonical data/ directory (C:\\Users\\ahammo\\Repos\\tamheed\\evals\\sample-results\\lab-tracker\\package\\data\\x.json) — an export is a derived file; data/ holds only the store"}`. `package/data/x.json` exists afterwards → **False**.
14. Refusal (b) — `entity_export("w.json", tool="entity_upsert", args={"entities": []})` — verbatim: `{"ok": false, "error": "entity_export runs read-only tools only — one of: entity_query, trace_query, gate_run, readiness_check, package_verify, server_info (got 'entity_upsert')"}`. `exports/` listing afterwards: `['gates.json', 'slate-rows.json', 'verdicts.json']` — no `w.json`.
15. **THE PASTE GUARD** — `entity_query("defect", id="DEF-001")` (first read) — the full row, verbatim: `{"id": "DEF-001", "title": "overdue() off-by-one: a task due TODAY is flagged OVERDUE (uses <= instead of <)", "severity": "high", "lifecycle_status": "Fixed", "found_in": "SL-002", "fixed_by": null, "custom_attributes": null, "last_referenced": null}` (`count: 1, total: 1`).
16. `entity_upsert([{"type": "defect", **row, "title": <title with ONE word replaced: "flagged" → "marked">, "expect_unchanged": ["title"]}])` (severity unchanged, every other column as returned) — **REFUSED**, verbatim: `{"ok": false, "applied": 0, "error": "batch rolled back — one or more items violated constraints", "items": [{"index": 0, "ok": false, "id": "DEF-001", "error": "DEF-001: expect_unchanged — title differ(s) from the stored row (an omitted column counts as changed): the transport altered the value; re-fetch the row through entity_query and paste that"}]}`. Re-read `DEF-001` → row `==` the first read: **True**.
17. The SAME item with the exact stored title and `"severity": "medium"` — **accepted**: `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "DEF-001"}]}`. Re-read: `severity: "medium"`, title `==` first read: True.
18. The same item with `"severity": "high"` (the original) and `expect_unchanged: ["title"]` — **accepted**: `{"ok": true, "applied": 1, "items": [{"index": 0, "ok": true, "id": "DEF-001"}]}`. Re-read: title byte-identical to the first read → **True**; severity back → **True**; whole row `==` the first read → **True**.
19. `progress_update([{"entry": <closing note>, "event_type": "note", "actor": "agent:lab-continuation-041"}])` — `{"ok": true, "ids": ["PE-019"]}`. The stored row (re-read via `entity_query("progress-entry", id="PE-019")`, verbatim `entry`): `Beat 14 (plan 041, v4.7.0 RC): entity_export wrote exports/slate-rows.json (AC-003, AC-005) stamped with digest 48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3 == package_verify(); workspace/scripts/gen-slate.py rendered workspace/slate.html from that file and calibrated its verifier (one corrupted character detected). The paste guard: a full-row DEF-001 upsert with expect_unchanged [title] and ONE word of the title altered (flagged -> marked) was REFUSED naming title; the same row with the exact stored title and severity high -> medium was ACCEPTED, then severity restored to high under expect_unchanged [title] (accepted); the title re-read byte-identical. Also observed: the PARTIAL export note (verdicts.json, limit 1 of 5), the data/ path refusal and the read-only-tools refusal.` (`actor: "agent:lab-continuation-041"`, `event_type: "note"`, `subject_id: null`, `occurred_at: "2026-09-06T20:56:31Z"`).
20. `handoff_emit("<scratch>/lab14-handoff-i61d531a", refresh_stock=True)` (fresh empty dir) — ok. `written: [".mcp.json", "CLAUDE.md"]`, `stale_references: []`, `restated_content: []`, `project_prompts: ["project-kickoff.md"]`, `warnings: ["5 stale-stock prompt(s) refreshed to the current template (refresh_stock)"]`. `prompt_library`: **`refreshed` (stale-stock): `["prompts/package-onboarding.md", "prompts/progress-sync.md", "prompts/README.md", "prompts/register-liveness.md", "prompts/slice-review.md"]`** (5); `unchanged`: `[defect-triage, drift-register, generate-report, integrity-check, loop-guard, loop-iteration, orient-resume, phase-close, release-close-out, replan-deferred, skill-promote, slice-kickoff]` (12); **`diverged_customized: []`**, `diverged_stale_stock: []` (after refresh), `diverged: []`, `emitted: []`.
21. The emitted `CLAUDE.md` contains all three substrings — `reads an \`entity_export\` file the tool wrote` → True; `- \`entity_export(path, tool?, args?)\`` → True; `expect_unchanged: [cols]` → True (the lines quoted verbatim below).
22. `export_html()` — ok: `review.html` 102,081 bytes; csv `emitted: ["csv/progress_entries.csv"]` (the one touched table — `defects.csv` is `unchanged`: the flip + restore was net zero), 23 unchanged, `diverged: []`.
23. `gate_run()["ready"]` — **`true`**; `audit_evidence` unchanged from beat 13: `{"evidenced": 3, "narrated": 0, "ungraded": 1, "narrated_ids": [], "ungraded_ids": ["AV-005"], …}`.
24. `package_verify()` — verbatim: `{"ok": true, "package": "package", "files": 26, "foreign": [], "digest": "8e2881280bb8f8f6de2a379faf5f9f16f6491fc00c22648ce4ee8e935b3bd604", "recorded": null, "verified": true, "loadable": true, "dirty": [], "memory_matches_disk": true}` → **D2 ≠ D1** (by construction: the PE-019 row rewrote `progress_entries.jsonl`; `exports/` is outside the `foreign` scan, which is `data/`-only).
25. `package_close()` — ok; `data/.lock` absent after every script.

Step 10 (repo root, nothing edited):

26. `python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`, all eight `G-*=pass`, `audit_evidence=evidenced:3/narrated:0/ungraded:1`, exit 0.
27. `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → `PASS lab-tracker`, **26 `pass` lines, 0 fail, 0 skip** (incl. the four plan-041 ones: `exports/slate-rows.json` exists; it carries `"tamheed_export"`; it holds `Given tick --help`; `expect_unchanged` in `progress_entries`), `1 case(s) checked, 0 failed, 0 skipped`, exit 0. The full runner (`--results-dir evals/sample-results`): `3 case(s) checked, 0 failed, 6 skipped`, exit 0.
28. `python check.py` → tail: `3 case(s) checked, 0 failed, 6 skipped` / **`ALL CHECKS PASSED`**, exit 0.

Fixture files changed by the session (`git status --porcelain -uall evals/sample-results/lab-tracker`, 13 entries): modified `package/data/progress_entries.jsonl` (+1 line — the only `data/` change), `package/csv/progress_entries.csv`, `package/review.html`, and the five refreshed `package/prompts/` files (`README.md`, `package-onboarding.md`, `progress-sync.md`, `register-liveness.md`, `slice-review.md`); new `package/exports/gates.json`, `package/exports/slate-rows.json`, `package/exports/verdicts.json`, `workspace/scripts/gen-slate.py`, `workspace/slate.html`. `data/defects.jsonl` is byte-identical to the recorded fixture.

### Emitted CLAUDE.md — the quoted lines (verbatim)

The note's export sentence (inside the opening paragraph):

```
All package reads/writes go through the `tamheed` MCP tools — a committed script that must QUOTE the store (a review slate, a docket) reads an `entity_export` file the tool wrote under `exports/`, never `data/*.jsonl` and never a pasted display; ready-made task prompts live in `package/prompts/` — start with `package/prompts/README.md`, the operator guide (which prompt for which situation, semi-auto vs fully-auto); the human review surface is `package/review.html`.
```

The two cheat-sheet lines:

```
- `entity_upsert(entities=[{type, id, ...}])` — FULL rows, even for updates; `expect_unchanged: [cols]` on an item refuses the write if those columns differ from the stored row (a long-row status flip is self-verifying); `{type: trace-edge, from_id, to_id, relation, retire: true}` removes that edge (journaled — retype in ONE batch: retire + the corrected edge)
```
```
- `entity_export(path, tool?, args?)` — write a read tool's WHOLE result to `<package>/exports/<path>` (digest-stamped, deterministic) for a committed script to quote from; pass a limit above total for a whole family
```

### Scenario ✔ ticks — observed vs missed

| Beat-14 tick | Result |
|---|---|
| `package_migrate` preview REFUSED verbatim as before | observed (step 1) |
| THE EXPORT: file at `<package>/exports/slate-rows.json`; `digest` EQUALS `package_verify()["digest"]`; `partial: false`; `memory_matches_disk: true`; the result carries no rows | observed (steps 3–5) |
| A COMMITTED generator `workspace/scripts/gen-slate.py` (stdlib, ~60 lines): reads the export by path, writes `workspace/slate.html` quoting each `statement` byte-exact (escaped), headed by the digest; verifies byte-for-byte; CALIBRATES (one corrupted character MUST be reported); never opens `data/` | observed (steps 7–8; 86 lines incl. docstring) |
| Whole-family export: `limit: 1` → `partial: true` + the PARTIAL note; `limit: 1000` → `partial: false`, `count == total` | observed (steps 10–11) |
| `entity_export("gates.json", tool="gate_run")` works; two refusals verbatim (`../data/x.json`; `tool: "entity_upsert"`) | observed (steps 12–14) |
| THE PASTE GUARD on `DEF-001`: one-word-altered title + `expect_unchanged: ["title"]` → REFUSED naming `title`; exact title with only `severity` changed → accepted; severity restored the same way | observed (steps 15–18) |
| `handoff_emit` re-run: the note's export sentence + the two cheat-sheet lines | observed (steps 20–21) |
| `export_html`; `gate_run` ready; `package_close`; the fixture updated — `exports/` files and the workspace script are part of it | observed (steps 22–25, 28) |

Missed: none. Every mechanism fired exactly as the scenario and the docstrings describe.

### Findings

1. **The refusal is two-layered again** (the beat-12/13 shape): the top-level `error` is the generic `batch rolled back — one or more items violated constraints`; the sentence that names `title` is `items[0].error`: `DEF-001: expect_unchanged — title differ(s) from the stored row (an omitted column counts as changed): the transport altered the value; re-fetch the row through entity_query and paste that`. The scenario's "REFUSED naming `title`" holds on the item error, not the top-level one — fine if "verbatim" means the recorded item text (as the earlier beats assumed).
2. **The scripted `severity → "medium"` was a real change only because the fixture's DEF-001 is `high`.** `lab/scenario.md` beat 6 says the `overdue()` defect was recorded at "severity honest: medium", but the recorded fixture (beats 1–9, untouched since) carries `severity: "high"` on DEF-001. Had the fixture matched beat 6's wording, the accepted write in the beat-14 script would have been a no-op and would have proved nothing about the accept path. Checked before writing (the read-only lookup), so the flip here is `high → medium → high`. A doc/fixture wording mismatch in `lab/` — reported, not edited.
3. **Export digests are stamped with D1 while the committed fixture verifies at D2 — by construction, and worth stating in the docs.** All three `exports/*.json` files carry `digest: 48e5d2e3…a29b3` (the state when they were written); the closing `progress_update` then rewrote `progress_entries.jsonl`, so a fresh `package_verify()` on the committed fixture reports `8e288128…bd604`. This is exactly the docstring's currency check working ("export immediately before generating; never reuse across sessions"): the recorded fixture's exports are, by the tool's own definition, stale relative to the committed store, and any future beat that re-generates the slate must re-export first. The eval only pins the envelope + the quoted text, not digest currency — correct, since the note row always follows the export.
4. **`gates.json` carries no `count`/`total`/`partial` keys** in the return (step 12) — `gate_run`'s result has no `count`/`total`, so the partial logic is skipped. Matches the code (`if "count" in result and "total" in result`); the scenario only says it "works". Fine.
5. **The refresh classified 5 stale-stock files, where beat 13 reported 6 and beat 12 reported 9** — again exactly the stock files the uncommitted plan-041 tree edits (`git status` shows `plugins/tamheed/prompts/README.md`, `package-onboarding.md`, `progress-sync.md`, `register-liveness.md`, `slice-review.md`, `stock-history.json`). `diverged_customized: []` — the fixture has never carried a customized stock prompt; `project-kickoff.md` is the one project prompt. The mechanism is a function of the stock you run against, as beat 13 concluded.
6. **One generator fix during the beat:** the first draft let a non-JSON input (e.g. `review.html` passed by mistake) escape as a `json.JSONDecodeError` traceback (exit 1) instead of the exit-2 refusal; `load_export` now treats unparsable JSON and non-object JSON as "not a tamheed export" (same message, exit 2). The spec case — valid JSON without the envelope — refused with exit 2 from the first draft. The committed script is the fixed one; the fix touches only `load_export`, and the md5 of `slate.html` is unchanged across the runs before and after it (step 8).
7. **`html.escape` is the byte-for-byte contract, not the raw statement.** AC-005's statement carries backticks and parentheses (no `<`, `>`, `&`, quotes), so escaped == raw for both rows here; the verifier still compares the escaped bytes, which is the only form that can be in the page. A future row with `<` or `&` would exercise the escape path; the calibration would still detect a one-character corruption because the check is on the escaped form on both sides.
8. **The flip + restore left `defects.jsonl` byte-identical and journaled nothing.** `entity_upsert` on a `defect` row appends no `progress-entry` (only edge retires and forced transitions do), so the only trace of the guard exercise in the store is the agent's own PE-019 note — which is why the eval pins `expect_unchanged` in `progress_entries` (the note) rather than a server row. Worth knowing: the paste guard's *refusal* leaves no journal row either (`applied: 0`, nothing written).
9. Everything else behaved exactly as documented: `memory_matches_disk: true` on every export; `../data/x.json` resolved to the real `data/` path and nothing was created; the rejected `tool` wrote no file; the overwrite of `verdicts.json` (an export replacing an export) was silent and correct; `package_verify` ignored `exports/` (`foreign: []`, `files: 26`); the lock was released after every script including the closed-package refusal; the closing flush left the fixture byte-canonical (steps 24 and 27, `verify` assertion pass).

### Verbatim refusal texts and digests

Step 1 — `package_migrate("package")`, package closed (`ok: false`, `error`):

```
package is already v4.0.0, its entity-type registry is current, and data/ holds no foreign audit-trail file — nothing to migrate
```

Step 13 — `entity_export("../data/x.json")` (`error`):

```
refusing to write inside the canonical data/ directory (C:\Users\ahammo\Repos\tamheed\evals\sample-results\lab-tracker\package\data\x.json) — an export is a derived file; data/ holds only the store
```

Step 14 — `entity_export("w.json", tool="entity_upsert", args={"entities": []})` (`error`):

```
entity_export runs read-only tools only — one of: entity_query, trace_query, gate_run, readiness_check, package_verify, server_info (got 'entity_upsert')
```

Step 16 — the paste guard (top-level `error`, then `items[0].error`):

```
batch rolled back — one or more items violated constraints
```
```
DEF-001: expect_unchanged — title differ(s) from the stored row (an omitted column counts as changed): the transport altered the value; re-fetch the row through entity_query and paste that
```

Step 10 — the PARTIAL `note`:

```
PARTIAL: 1 of 5 rows — the file has no payload cap; pass a limit above total (or page with after_id) to export the whole family
```

Digest D1 (step 3, before any write this beat; stamped on all three exports):

```
48e5d2e35cf1ff9a43340f629d07fa21ea5823eab9f3b5f547c6c4cda65a29b3
```

Digest D2 (step 24, after `progress_entries` was rewritten by PE-019):

```
8e2881280bb8f8f6de2a379faf5f9f16f6491fc00c22648ce4ee8e935b3bd604
```
