# Tamheed v4.12.0 — the findings_28 batch: the four capabilities the feedback channel asked for, and the channel's return half

Status: **EXECUTED 2026-09-23 — released as v4.12.0** (approved 2026-09-22; per-plan status lives in the index rows). Revision 2, after the devil's-advocate review.
Read-only work only: `findings_28.md` read in full; the thirteen `FB-` rows read through ACMP's
tool-written `exports/feedback.json` (never `data/`); the rewrite commit (`85d0fb4d`) and PR #431
spot-checked; findings_28's tamheed-side claims verified in source; **two design assumptions of
revision 1 measured and both found wrong** (§1.8–1.9). Two advisor passes. No web research: every
open question was internal and settled by source or measurement. Neither repo is modified.

Interview rulings (2026-09-22), all four on the recommended option: **FB-004** a `substitute` item on
`entity_upsert`; **FB-001** `entity_upsert` accepts `type: "package"`; **FB-002** a separate advisory
`prompt-ids-resolve`; **FB-003** `entity_query(search=…, context=N)` with `occurrences`. No new tool
(19 stays); no migration; MINOR, v4.12.0.

Deliverable boundary: changes land in **tamheed only**; ACMP is instructed by a transcript-only brief
after the tag, which carries the **disposition of all thirteen `FB-` rows** — the channel's return half.

---

## 1. Weaknesses found (revision 1 and my last brief), each verified

1. **Two of the memory audit's "stale" verdicts were wrong, not one**: "seven gates" (no engine tally has
   ever existed; ACMP invented `7/7`) and `lessons-confirmed` (`:2174` filters a populated table; its
   green is real). ACMP kept the sentence, correctly. The second reached my brief.
2. **The brief described a `local-tool` draft stage that does not exist** (`tool_arrives` fires on the
   first insert). The guard is right; the prose (brief, `005_feedback.sql` header) was wrong.
3. **The brief's `kind` prose ("a wrong doc") does not name the enum** (`doc-error`), and the same prose
   sits in the always-loaded note row and its template mirror.
4. **The local-tool rule's wording assumes a store reader** (`FB-013`): three registered ACMP tools read
   or write project-owned files under `tamheed-package/docs/` and never touch `exports/`.
5. **"Put the export file in your findings" cannot be done**: `exports/` is gitignored at ACMP
   (DEC-139 d4). The envelope and rows must be quoted.
6. **The brief expected 9 rows; the operator ruled 13** and deleted a tool when asked what it computed.
7. **The channel has no return half**: thirteen rows sit `Reported` with nowhere to go.
8. **Revision 1's plan 094 would have changed every field package's review page.** Registering
   `"package"` in `ENTITY_TABLES` makes `export_html._registers` (`export_html.py:540`) render it and
   the CSV loop emit `packages.csv`. Measured in source. It must be special-cased, like nothing else is.
9. **Revision 1's plan 093 would have been amber on every package by construction.** Measured against
   the lab fixture's 92 ids: the seventeen stock prompts hold exactly one bare example id (`LL-007` in
   `skill-promote.md`); the lab's project prompt holds none. A rule over all of `prompts/*.md` would
   fail on the maintainer's example, not the project's prose — the hollow amber plan 077 retired.
10. **The disposition table mislabelled registers as resolvable.** A `local-tool` row is a register, not
    a request; `Resolved` is the wrong terminal state for `FB-005`–`012`.
11. **The review-page generator was never checked against the last three batches** (the maintainer's
    question). Inspected: `export_html.py` (763 lines) renders `gate_run` and every table as a generic
    register; it has no Feedback working surface (ACMP's 13 rows are a raw dump), the Approved-lessons
    fold omits `superseded_by` (so the plan-075 tag cannot show), the waivers fold cannot mark an
    open-ended whole-rule waiver (079), and `readiness_check` is never rendered — the human surface has
    none of `population`, `indeterminate`, `omitted`, `waived` or the advisories since plan 069.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by source or measurement**
- `gate_run()["gates"]` carries eight `G-` keys plus `audit_evidence` and `requirements_unwired`
  (`tamheed_server.py:1700-1729`); nothing upstream changes for `7/7`.
- The rewrite happened (13 files in `85d0fb4d`, dated corrections citing docs); both scripts deleted via
  PR #431; the remaining `count-prompt-ids` mentions in `prm-next.md` are past-tense narrative.
- The channel worked end to end on 4.11.0 (13 Confirmed with audits; export `total: 13`; warnings
  appeared and cleared; `changed_columns` proved omitted nullables preserved; `FB-008`'s guard fired).
- `omission` is the composite-key write precedent (`:1390`, `:1615`; check.py:93). `packages` columns:
  `name, title, profile, mode (CHECK), iteration, package_version, mvp_definition, entry_point,
  go_no_go, created_at` (`schema.sql:44`). `packages.jsonl` is already persisted and rewritten by the
  registry-sync path. `matched` is built at `:1687` from per-column `LIKE`. `_strip_code` (`:42`) and
  `_prose_id_pattern` are reusable over files; the package's prompts live at `pkg_dir / "prompts"`; a
  file byte-equal to current stock is classifiable with `_load_stock_history()` and the `{package}`
  substitution (the `_emit_prompt_library` classifier).
- SQLite's `LIKE` is case-insensitive for ASCII only; Python `re.I | re.A` reproduces exactly that.
- The `.scratch` probes did not exist to delete (trap 27).
- Header columns reach `server_info().package` (`:3802`) and the review page's overview
  (`export_html.py:119`, HTML-escaped), never the note or an emitted prompt — a header write is not
  an injection surface. `changed_columns` keys on `id`/`entity_type` today; the header's key is `name`.
- `rule()`'s zero-population branch keys off `measured["table"]` and looks up omissions by entity
  type; a files-based population has no table, so 093 sets `indeterminate` explicitly.

**Rejected**
- "Nine rows"; "seven gates is stale"; "`lessons-confirmed` green can be vacuous"; "a `local-tool` row
  is born Proposed"; "the export file can be committed"; "register `package` in `ENTITY_TABLES`"; "scan
  every prompt file"; "registers get Resolved".

**Unresolved — settled in execution, never by guessing**
- How amber `prompt-ids-resolve` reads on ACMP's kickoff prompt (it narrates `DEF-082` and `7/7`); the
  id index lives in `data/`, unmeasurable from here. The brief states this and the remedy.
- Whether `trg_lessons_immutable` or the guard refuses a `substitute` on an Approved lesson first (both
  are refusals; the test pins whichever fires).
- Whether ACMP's four registered generators keep working after the `substitute` write lands (they read
  `exports/`; nothing changes for them — stated, not assumed, and checked by the beat's export).

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The substitute write's first guard has holes (087's lesson) | Built LAST, security + Python reviewers. Semantics closed: the server MATERIALIZES the stored row by a raw `SELECT` of every column (stored TEXT, not the parsed JSON `entity_query` returns, so `custom_attributes` round-trips byte-stable except the replace), applies an exact substring replace to the named TEXT column(s), then sends the result down the ordinary full-row path — every guard, trigger, `expect_unchanged`, `operator_confirm` and `changed_columns` run unchanged. Refused by name: `id`; a non-TEXT column; zero occurrences (names the column); empty `old`; `old == new`; `custom_attributes` that no longer parses after the replace; **the journal families** (`progress-entry`, `audit-verdict`: corrected by compensating rows, never substituted); **composite-key surfaces** (`omission`, `trace-edge`, `package`); **a mixed item** — an item carrying `substitute` may carry only `type`, `id`, `substitute`, `operator_confirm`, `expect_unchanged`, anything else refused (half a row plus a substitute is the ambiguity class 087 paid for). Reports `substituted: {column: count}`. No regex, no multi-row |
| A header write rewrites governance under nobody's name | `go_no_go` needs `operator_confirm` and journals `transition` by `system:package-guard`; `name`, `profile`, `package_version`, `created_at` refused by name; the item may name only the open package |
| The header write leaks into the review page / CSV / registry | Special-cased BEFORE the `ENTITY_TABLES` lookup; not in the map, not in `BASELINE_ENTITY_TYPES`, not in the sync lint; `entity_query(type="package")` stays refused with a message naming `server_info().package` |
| `prompt-ids-resolve` is amber by construction | Scans only files that are NOT byte-equal to ANY stock body in `_load_stock_history()` after `{package}` substitution (the classifier `_emit_prompt_library` already applies — a stale-stock file is the maintainer's prose too); customised files ARE scanned; the one stock example (`LL-007`) is backticked in `skill-promote.md` anyway (history key); zero scanned files → `indeterminate` set explicitly with `population.files: 0`; `_PROSE_ID_CAP` and the "showing N of M" clause on all three lists (findings_27 §3 must not recur) |
| `prompt-ids-resolve` turns ACMP amber on day one | Advisory; the brief warns, names the doctrine (backticks make a quotation inert) and the remedy |
| `occurrences` leaks long text | Only with `context`; counts exact on the RAW needle (never the `%`/`_`-escaped `LIKE` needle); snippets capped at 5 per column and 50 per response; `custom_attributes` counted on its raw text, stated |
| The brief makes ACMP interview for thirteen bookkeeping writes | `resolved_in` and `upstream_ref` are outside `_FEEDBACK_CONTENT_COLS`, so `Reported → Resolved` needs no `operator_confirm`; the brief says so |
| Note row and template drift | The identity test catches a one-sided edit |
| The disposition misstates a row's fate | Requests (`FB-001`–`004`, `013`) → `Resolved` with `resolved_in`/`upstream_ref`; registers (`005`–`012`) stay `Reported` — a register has no resolution; ACMP writes the statuses |
| A shipped migration's header is edited | Not edited; the CHANGELOG says the 005 header overstates the draft stage |

## 4. Changes made and why

1. **094 special-cases `type: "package"`** instead of registering it (§1.8).
2. **093 scans non-stock prompt files only**, and `skill-promote.md`'s bare `LL-007` is backticked
   (§1.9). `population` reports `files` scanned.
3. **The disposition table separates requests from registers** (§1.10).
4. **095's semantics are stated as "materialize, then the ordinary path"**, so the guard surface is the
   existing one, not a second one (the reviewer-found holes in 087 were all in a second guard).
5. 091 folds FB-013, §3a, §3b, the export wording and the `work_bind` sentence into one docs plan first.
6. `7/7` closed as "nothing upstream, no total added"; `priority` column and remote-ref checks rejected.

## 5. Refined execution plan

Constraints: stdlib only; no migration; no new tool; bundle never links out; CHANGELOG under
`[Unreleased]` until 099; stock prompt edits carry a `4.12.0` history key in the same commit
(`README.md`, `skill-promote.md`); released CHANGELOG blocks and shipped migrations stay frozen. Per plan:
record → RED → GREEN → `python check.py` → reviewers where listed → commit from a message file → push →
CI. Status updates at least every three minutes.

| # | Plan | Validation → expected |
|---|---|---|
| 091 | **The feedback teaching says what the code does.** Two-clause local-tool rule (*writes nothing tool-owned; if it reads the STORE, it reads `exports/` only*) in the note row + `agent-control.template.md`, SKILL.md, `prompts/README.md`, governance, catalog; a `local-tool` row cannot be a draft; the five `kind` values named where the rule is taught; `handoff_emit`'s warning and the README say *quote the envelope and the rows in your findings*; `work_bind`'s README row: bind a sha that is on origin; CHANGELOG notes the 005 header overstates the draft stage | identity test green; per-behavior grep; `check.py` |
| 092 | **FB-003: `entity_query(search=…, context=N)`** → `occurrences: {id: {column: {"count", "snippets"}}}`, N chars either side, `re.I \| re.A` (the `LIKE` semantics), snippets capped 5/column and 50/response, only when `context` is passed | three hits in one column → `count: 3`, three snippets; absent without `context`; `matched` unchanged; a non-ASCII case difference not counted (matches `LIKE`) |
| 093 | **FB-002: advisory `prompt-ids-resolve`** over `<package>/prompts/*.md` files that are NOT byte-equal to any stock body in the history (`{package}` substituted): entities `prompts/<file>:<line> -> <id>`, the same three lists each capped with the "showing N of M" clause, `population: {files, scoped: false}`; fails only on a bare well-formed phantom; never blocks; zero scanned files → `indeterminate` set explicitly. `skill-promote.md`'s `LL-007` backticked (key `4.12.0`) | a project prompt naming `DEF-999` fails; backticked → `in_code_spans`; `KPI-17_score` in neither; a stock file with the example id is not scanned; the lab fixture reads `pass` on its project prompt |
| 094 | **FB-001: `entity_upsert` accepts `type: "package"`**, special-cased before the `ENTITY_TABLES` lookup (not a family: no register, no CSV, no registry row): writable `title`, `mode`, `iteration`, `mvp_definition`, `entry_point`, `go_no_go`; `go_no_go` refused without `operator_confirm`, journaled (`transition`, `system:package-guard`); `name`/`profile`/`package_version`/`created_at` refused by name; only the open package's name; `changed_columns` reports; `server_info().package` reads it back; `before_row`/`changed_columns` keyed on `name`. Security reviewer | unattended verdict refused; confirmed one journaled; frozen column refused naming it; `export_html` emits no `packages.csv`; `entity_query(type="package")` still refused, message points at `server_info` |
| 095 | **FB-004: the `substitute` item on `entity_upsert`** — `{"type", "id", "substitute": {"<column>": ["<old>", "<new>"]}}` (+ optional `operator_confirm`, `expect_unchanged`): the server materializes the stored row, replaces per named TEXT column, then runs the ordinary full-row path; refusals as in §3; result gains `substituted: {column: count}` beside `changed_columns`; the journal families, composite-key surfaces and mixed items refused by name. Security + Python reviewers. Future-options entry marked superseded | one token in a 5,000-char title → one `changed_columns` entry, `substituted: {"title": 1}`, every other column byte-identical (asserted); zero occurrences refused; an Approved lesson's `statement` refused (immutability); a `kind` change on a bound feedback row refused without the word; `id`, an INTEGER column, a JSON-breaking replace in `custom_attributes` each refused |
| 096 | **review.html follows plans 069–095** (maintainer ruling 2026-09-22, option 1). `export_html.py`: a **Feedback** section (awaiting the operator's word / confirmed, not yet reported / registered tools with `tool_path` / resolved with `resolved_in`); the Approved-lessons fold shows `superseded_by` and the plan-075 tag (`pending its approval` / `RETIRE THIS ROW`); the waivers fold marks open-ended whole-rule waivers; a **Readiness (package scope)** section from `readiness_check` — `rule`, `severity`, `status`, `population`, `discriminating`, `omitted`, `waived`, entities capped — with an *evaluated as of <date>* line so a re-export on a later day changes bytes only where the calendar moved (`open-questions-overdue`, expiring waivers); the renderer takes the readiness report as an argument from `tamheed_server.export_html` (no import cycle; determinism within a day asserted by the export test). `tests/test_export_html.py` extended per fold | 37 export tests + new ones green; two exports in one run byte-identical; the lab fixture's page shows FB rows, the retired lesson's tag history, and the readiness table |
| 097 | **Docs + diagrams sweep**: server README rows (`entity_query` context, `entity_upsert` package + substitute, `readiness_check` prompt rule), quality-gates, governance (the header on the operator's word), `docs/entities.md` (the header's write rule beside the family table), `docs/architecture.md` (the write-side paragraph gains the substitute; the read-side gains the prompt scan), SECURITY.md, and `docs/workflow.md` / the server README's `export_html` row for the review page's new sections | per-behavior grep ≥ 2 docs each; no stale sentence; mermaid lint |
| — | **Full test**: `python check.py` (nine suites incl. the extended export suite, lints, canonical round-trip, evals); every suite under `error::DeprecationWarning`; black-box acceptance, one section per plan 091–096, N/N on the batch tree and 0/N on an extracted `v4.11.0` tree, each check from an open package; `--selftest` 19/19; CI green on every pushed commit | N/N vs 0/N; all green |
| 098 | **Lab beat 19** (agent, opus, worktree; plan file first; **no registry-sync needed — stated**; every new assertion must fail on the pre-beat fixture): a project prompt narrating a phantom reads amber, then backticked reads pass; a census with context on a known token; the header's verdict changed on the operator's word after an unattended refusal; a one-token `substitute` on a long defect title and a refused one on an Approved lesson; the two refreshed stock prompts | new assertions; evidence report |
| 099 | **Release v4.12.0** (plan-058 recipe + the F-1 fixture step) | lints; tag; CI on the tag |
| — | **The ACMP brief**, transcript-only, after the tag: upgrade 4.11.0→4.12.0 (no migration, no registry-sync); **the disposition table** — `FB-001` Resolved (094), `FB-002` (093), `FB-003` (092), `FB-004` (095), `FB-013` (091), each with `resolved_in: "4.12.0"` and `upstream_ref` naming the plan, written by ACMP without the operator's word (both columns are bookkeeping, outside the bound-content set); `FB-005`–`012` stay `Reported` (registers) with the rewritten rule quoted; the `prompt-ids-resolve` warning and remedy; the `go_no_go` rewrite on the operator's word; a `substitute` walk-through on their own next repair; `findings_29.md` quoting the envelope and rows | ACMP's request rows leave `Reported` |

**Considered and rejected:** `gates_total`/`gates_passed` (findings_28 remedy 2); a `priority` column
on feedback; remote-reachability checks on `work_bind` refs; scanning stock prompt files.

## 6. Approval checkpoint

Nothing has been executed. Approving authorizes plans 091–099, commits, pushes and the `v4.12.0` tag on
`main` under the standing git delegation, and the ACMP brief. These change tamheed's behavior or doctrine:

1. **A new write shape on `entity_upsert`**: `substitute`, a partial write for one column — the first
   departure from whole-row replacement, implemented as materialize-then-ordinary-path so it inherits
   every existing guard.
2. **The package header becomes writable** through `entity_upsert(type="package")`, special-cased and
   never a family; `go_no_go` on the operator's word, journaled.
3. **A new advisory over the project's prompt files** (`prompt-ids-resolve`), never over stock; ACMP
   will likely read amber until its narrated ids are quoted.
4. **`entity_query` grows `occurrences`** when `context` is passed.
5. **Doctrine wording changes**: the two-clause local-tool rule; feedback leaves a repo as quoted
   envelope and rows.
6. **The channel gets its return half**: requests resolved, registers kept.
7. **The review page changes for every package**: new Feedback and Readiness sections, the lesson tag,
   the waiver mark; date-dependent rules render as of the export date.
8. **MINOR release v4.12.0** with lab beat 19; two stock prompt bodies change (`README.md`,
   `skill-promote.md`).

Approve as written, or name which of the eight to change.
