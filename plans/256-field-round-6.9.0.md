# Tamheed 6.9.0: the field round after 6.8.0 (ACMP FB-034..037, Jisr FB-025/029/032/033/034/043/044)

> **Plan 256, the round record (2026-11-27).** The approved plan, recorded as approved: rulings R145-R170
> (operator, six interview rounds) and defaults D1-D15. Field data appears as ids and counts only.
> The plan was approved after a strict devil's-advocate revision: a Plan agent's code review (15 findings,
> each re-checked) and two advisor passes moved it to revision 3.

> NOT the parked plan, `plans/PARKED-2026-11-17-loop-findings-and-requirement-cascade.md`. It moves to
> **6.10.0** and keeps migration 013 and ADR-0006 (R145, R163). A dated note in its file says so.

> **R52 is superseded by R147** (plans 160-164 keep their text, as a dated record). The premise of R52 moved:
> plan 250 made the write refusal name the item's columns, and a field hit the query refusal on 2026-11-26.

## Context

Both fields run tamheed 6.8.0.

- **ACMP** sent four Confirmed rows: FB-034 (a new row under an existing id updated it in silence), FB-035
  (the query refusal names no columns), FB-036 (the briefs' 2.2 when the operator updated first) and FB-037
  (package-writes section 2's hash step has no tool route). FB-038 is a `local-tool` row, context only.
- **Jisr** owes seven Confirmed rows: FB-043 (a slate text cap of 8000), FB-032 (intros lose their line
  breaks), FB-034 (a long word overflows a card at phone width), FB-033 (recommendations hidden at open),
  FB-025 (no one-key write of `custom_attributes`; no closed set on built-in families), FB-029 (edge or
  column for a discharge?) and FB-044 (orient-resume step 7 for a started slice). Nineteen `local-tool` rows
  are context only. FB-043 and FB-032 come first: Jisr's next slate waits on them.
- The ids of the two fields overlap, so every mention names the field.

## The approved plan (section 5, verbatim)

### The rulings (operator, 2026-11-27)

| # | Row | Ruling |
|---|---|---|
| R145 | release | 6.9.0, MINOR, no migration. The parked plan moves to 6.10.0 and keeps migration 013 and ADR-0006, with a dated note in its file |
| R146 | ACMP FB-034 | `create: true` refuses a write whose key exists. The refusal names the row's title (cut to 120 characters, when the family has one), and the next free id only for flat-numbered families (no dotted ids). Refused beside `substitute`, `merge_attributes`, `retire` and `expect_unchanged`. On a trace edge it refuses an existing triple. On an omission it refuses an existing `entity_type`, and a null one. On the journal it is accepted (already insert-only). `create: false` is the plain upsert. Every ok id-keyed result carries `write`: `"inserted"`, `"updated"` or `"unchanged"` (a merge no-op, R164). The flag is OPT-IN, and the teaching surfaces are in §3 |
| R147 | ACMP FB-035 | **R52 is superseded** (premise moved: plan 250, and the field refusal of 2026-11-26). One helper `_columns_told(etype, allowed)` names the allowed columns in four refusals, each with its own list. `entity_query`/`entity_export`: every column, including `last_referenced` and the standup payload. `expect_unchanged`: the family's columns. `substitute`: the TEXT columns except `id`. The write path keeps its pinned text |
| R148 | ACMP FB-037 | §2 names `expect_unchanged` and its limit (an update only, and two sends agree). Opt-in `sha256: true` returns `sha256: {column: hex}`, over the UTF-8 bytes of the stored text, read back after the write. The columns: a full row hashes the TEXT columns sent; a substitute, the columns it names; a merge, `custom_attributes`. A null reads `null`, and a JSON column is hashed as its stored text. Inserts are covered. Allowed beside `substitute` and `merge_attributes` |
| R149 | ACMP FB-036 | The 6.9.0 briefs carry a THIRD PATH in 2.1 and 2.2. When `server_info` already reads 6.9.0 and no PRE file exists, the operator updated first. PRE is the last commit before the update, from `git log` (the newest commit not made under 6.9.0), and is written to the PRE file with that note. 2.3 compares with the table's inline values and with the latest handoff's verified facts. The dated briefs keep their text |
| R150 | Jisr FB-043 | `detail` (question, option) and `intro` (slate, round) caps rise to 32,000. `references/slate.md` gains a table of every cap: `CAPS`, `MAX_*`, `MAX_NAMED`, `MAX_DROPPED`. Lint 15 keeps the table equal to the code. The `maxlength` literal is derived from `MAX_ANSWER_TEXT` |
| R151 | Jisr FB-032 / FB-034 | Slate text keeps its line breaks and wraps a long word. One inherited `overflow-wrap` rule on the reading column, plus `white-space: pre-wrap` on the multi-line fields (the intros, details, reason, basis, gap, and the decided answer). The value is the one the 257 measurement justifies |
| R152 | Jisr FB-033 | `show_recommendations: true` (slate key) shows them in every view, at every open. The button hides them until the page closes. The stored `recs` choice is ignored while the key is set. Without the key, the page acts as today |
| R153 | slate compatibility | A new slate key is written only when set. `VERSION` stays 2. A record and an answers file written by 6.8.0 (built by script, the answers with 6.8.0's `question_digests`) are read by 6.9.0 with no `question_changed` |
| R154 | slate proof | A `slate-browser` CI job on two pages (keyed and unkeyed), with the CI checks of §3. Three dispatched runs before main |
| R155 | Jisr FB-025 (a) | `merge_attributes` on `custom_attributes` (R169). The server merges into the stored object and sends the full row down the normal guarded path. §1's "JSON inside `custom_attributes`" is corrected |
| R156 | Jisr FB-025 (b) | A family's registry row declares fields in the full register grammar, through `entity_upsert({type: "entity-type", type_id, custom_attributes: {fields: [...]}, operator_confirm: true})`. Only `custom_attributes` is writable, and stray keys are refused by name. `values` and `refs` are checked when the write SETS `custom_attributes` (the caller sent it, a substitute named it, or a merge changed it). Undeclared keys stay free. `required` is advisory only. The conditional advisory `declared-attributes` lists the rows that break the declaration |
| R157 | Jisr FB-029 | `discharged_by` records the discharge, on the operator's word. A `discharges` edge records the plan. The `risks-discharged` `extra` names each listed risk with a `discharges` edge from a latest-Met AC or a Pass test as a candidate. In Jisr: RISK-013 only. The ids are unchanged, and readiness moves in neither field. The docs say so in five places |
| R158 | Jisr FB-044 | orient-resume step 7, with the test of R168. A project rule goes in a prompt row bound to `orient-resume`. slice-kickoff step 2 agrees |
| R159 | measurement | Archives in scratch only. The originals are never opened, and nothing is fetched into `Repos\Jisr`. The commits are per R167 |
| R160 | cadence | Branch `round/6.9.0`. One operator word per beat, naming the commit and the push. CI is dispatched. At the release, main is fast-forwarded, main's OWN run is read, then the tag |
| R161 | budget | 10 USD for agent runs. Stop and ask before passing it. Three paths per brief, plus the 262 lab run |
| R162 | brief offers | **Jisr:** `discharged_by` on RISK-013; drop the slate workarounds (FB-031, FB-040 and FB-042 are Jisr's scripts); declare DEC-214's layer set and read the census. **ACMP:** a rule line for `create: true` and `sha256: true`. Each needs that field operator's word |
| R163 | ADR | ADR-0007 for the declared sets |
| R164 | merge no-op | Ok with `changed_columns: []` and `write: "unchanged"`. The UPDATE is skipped, and a removed key that was absent is listed in `merged.absent` |
| R165 | declared grammar | `refs` is included. A declared family refuses a non-object `custom_attributes` |
| R166 | slate byte cap | `slate_export` compares the record's UTF-8 bytes with `MAX_RECORD_BYTES` (`:7178`) |
| R167 | Jisr base | Jisr's branch tip read with `gh api` at 263.1, archived, its sha recorded. `aafc7dd` stays the source of the rows only |
| R168 | started | **Signal 1:** journal entries whose `slice_id` is the slice. They are counted with `entity_query("progress-entry", search="<SL-id>", context=1)` (`occurrences.slice_id`). **Signal 2:** the latest handoff (the resume block's handoff entry) has that `slice_id` or names the slice. Both signals: resume at the handoff and offer no kickoff. Neither: offer the kickoff. One: state both and ask |
| R169 | merge semantics | RFC 7386 §2 for an object patch on an object target: `null` removes, objects recurse, others replace (arrays whole). Departures, named in the docs: (1) a non-object patch is REFUSED (the RFC would replace the whole value); (2) a stored non-object `custom_attributes` is REFUSED (the RFC would discard it), while a stored NULL counts as `{}`; (3) a `null` value cannot be stored |
| R170 | diagrams | No new diagram. The tool-effects map (`entity_upsert` writes `entity_types`) and the line pins only |

### The defaults (mine; approval accepts them)

- **D1. The names:** `create`, `sha256`, `merge_attributes`, `write`, `entity-type` and
  `declared-attributes`. Each is grepped before use. `written` is avoided, because it already names
  flush and handoff outputs.
- **D4.** Strict JSON booleans for `create`, `sha256` and `show_recommendations`.
- **D5. Where a declaration may live:** families with a `custom_attributes` column, except register,
  register-entry, the header, the journal and standup-report. A declared field never takes the name
  of one of the family's columns.
- **D6.** The declaration write is journaled like the other `operator_confirm` writes.
  `server_info(detail)` lists `declared` only while a package is open.
- **D7.** The 6.8.0 brief recipe (`plans/evidence/scripts-253/`).
- **D11.** `prompts/README.md:214` is corrected AT THE STAMP, with its stock-history key. The three
  eval samples and `generated-samples/support-triage-agent-v2` are regenerated by their scripts after
  it.
- **D12.** The registered description of `entity_upsert` names `create: true`.
- **D13.** `declared-attributes` is conditional, like `register-entries-conform`. Package rules go
  from 32 to 33, and the conditional pin gains it.
- **D14.** The note's obligations table gains the `create: true` row.
- **D15.** The refusal cuts an echoed title to 120 characters. "Next free id" is named only for
  flat-numbered families.

### The loop for each beat

1. A red test first.
2. Build.
3. `ecc:code-reviewer`, plus `ecc:security-reviewer` on 258-261. These are not blocked by the
   review-council guard.
4. **The guide pins.**
   1. Restore `diagrams.py` and `test_user_guide.py` from HEAD.
   2. Run `shift_221.py` once ("unmapped citations: []").
   3. Re-apply the beat's hand edits.
   4. Run `build.py`. `--missing` must be empty.
5. A new control key enters the `extract.py` assert, with its `meta.<key>` prose in EN and AR, in its
   own beat.
6. Lint 14 on every new text. No field ids in skill text.
7. `python check.py` on 3.13 and 3.10.
8. The surprises list, then ONE question naming the commit and the push.
9. CI dispatched on the branch, and green.

Every Python helper is written with the Write tool.

### The beats

| Beat | Content | Expected output, and the check that proves it |
|---|---|---|
| **256** record | `plans/256-field-round-6.9.0.md`, holding R145-R170, D1-D15, the field ids and counts only, and R52 superseded by R147. The README ledger rows 256-263. A dated note in the parked plan | One docs commit. `check.py` green |
| **257** slate: Jisr FB-043/032/034/033 (R150-R154, R166) | **The engine.** `slate.py`: caps of 32,000; `show_recommendations` written only when true. `slate_export`: the byte cap. `slate_page`: `data-recs`. `slate.js`: the start state; the storage skips `recs`. `slate.css`: the wrap rule and `pre-wrap`. `slate_round`: `maxlength` from the constant. **The fixture** script `scripts-257/fixture_680.py` writes `tests/slate_compat_680/`. **The browser proof.** `tests/slate_browser_page.py` (two pages); the check file's new checks (the "no click" check before line 86); the runner's `send()` and waits; the `slate-browser` job. Local evidence of the 1280 px widths against a 6.8.0 build. **Lint 15** with its `lint.15` prose and a red case. **The docs:** `slate.md` (caps, key, line breaks, views), operator-interview §7, `tests/README.md:24`, `CLAUDE.md:38`, ADR-0005:53, `ci.yaml:8` | 17,114 characters export, and 32,001 are refused. The fixture reads with no `question_changed`. A record of 10M Arabic characters is refused at export. The CI checks pass on three dispatched runs. The width evidence is recorded |
| **258** ACMP FB-035, FB-034 (R146, R147, D12, D14, D15) | **The helper** at four sites. **`create`**, in the filter and the assert. It is tested right after the unknown-columns check (`:2322`). Refused in the retire branch (an explicit check), beside substitute, merge and `expect_unchanged`, and as a non-boolean. **The `write` marker.** **The registered description.** **The note's obligations row.** **The skills,** each read to confirm: `package-writes` §1, `defect-triage`, `register-liveness`, `slice-review`, `ste-rewrite`, `tamheed/SKILL.md`, `skill-promote:67`, `orient-resume:60`, `ci-evidence:93`; and re-read `progress-sync`, `drift-register`, `replan-deferred` and `integrity-check`. **A sweep for exact result pins** over `tests/`, `evals/`, `lab/`, `generated-samples/` and `docs/`. **The guide:** `meta.create`, `tool.entity_upsert`, `section.tools.upsert.2`, the note prose | One test per refusal site and per `create` combination. The SC-162 replay on a lab copy is refused with the title and the next id. The note's growth, in characters, is recorded |
| **259** ACMP FB-037 (R148) | `sha256`, in the filter, the assert and the substitute and merge sets, and refused on retire. §2 rewritten: the route, the calibration, the assert, `expect_unchanged` on the next write, and the limits. `meta.sha256` | Equals `hashlib.sha256(stored.encode())` on an insert and on an update. A one-character corruption differs. CR is kept. Works beside a substitute |
| **260** Jisr FB-025a (R155, R164, R169) | `_materialize_merge` beside `_materialize_substitute`. **The refusals:** the journal, edges, omissions, the header, standup reports, a missing row, a non-object patch or target, a non-text key, depth, a mixed item. **The result:** `merged: {set, removed, absent}`. **The checks:** registers are judged on the materialized row. **The texts:** the §1 correction; `meta.merge_attributes` | The object-to-object cases of RFC 7386 Appendix A, COPIED FROM THE RFC TEXT at build time (fetched from rfc-editor.org, never from memory), each pass. The RFC rows with a non-object patch or target are refused, as departures. A no-op leaves the JSONL byte-equal. The other keys are equal when parsed. A register entry outside its set is refused |
| **261** Jisr FB-025b (R156, R163, R165, D5, D6, D13) | **`_write_entity_type`.** `entity-type` stays out of `ENTITY_TABLES`, and the unknown-type message names it. **The helpers** gain `allow_undeclared`, `skip_required` and reserved names, with register defaults kept. **The check:** the declaration is read per item, and the write is judged only when it sets `custom_attributes` (the `_same_json` model). **The advisory** `declared-attributes`. **The docs:** ADR-0007, governance, extension, entities, SECURITY, §7c, `quality-gates.md:103`, the server README. **The guide:** `meta.type`, `block.TAIL.custom_attributes`, `table.entity_types`, `param.server_info.detail`, the rule, `TOOL_EFFECTS` | No word: refused. A bad value or ref: refused. An undeclared key: free. A non-object: refused. A same-batch declaration counts. An old bad row is listed, and a title substitute on it passes. The migrate sync keeps a declaration. The canonical round trip holds. Unchanged: register entries' own checks |
| **262** Jisr FB-029, FB-044 (R157, R158, R168) | **FB-029:** the candidates through `extra`; the docs (governance §risks and cross-references, the catalog, traceability, entities, `release-close-out` step 33); the guide (`rel.discharges`, `col.risks.discharged_by`, `rule.risks-discharged`). **FB-044:** step 7 and slice-kickoff step 2 per R168. **The headless lab run:** (a) orient-resume on a lab copy with one started slice and one one-entry slice; (b) a cold agent asked to file a new defect and a new scope change | (a) The started slice resumes at its handoff, and the one-entry slice is put to the operator. (b) Whether `create: true` was sent unprompted is recorded as measured, either way. Readiness `ready` is unchanged on the FB-029 fixture |
| **263** release + briefs (R149, R159-R162, R167) | **(1) Baselines.** ACMP: `git archive` of the local HEAD (no `.lock`), sha recorded. Jisr: the branch tip from `gh api`, as a tarball into its own scratch folder (fallback: a scratch clone at that sha). `core.autocrlf=false`. Python with `-I`. **(2) Replays** under the 6.8.0 bundle and the 6.9.0 tree. **(3) The way back:** 6.8.0 reads a 6.9.0 slate (17K detail, the key), a declaration, and a merged row. **(4) The stamp** (`stamp_690`, `refresh_lab_690`): `plugin.json`, three READMEs, CHANGELOG, `index.html`, D11 with its history key, the samples regenerated; both gates; the selftest. **(5) On your word:** fast-forward main, read main's own run, annotated tag `v6.9.0`. **(6) The briefs,** in the 6.8.0 shape: the third path (R149); "`create` is opt-in"; the note's new row; the way back as measured; the R162 offers; the roster. **(7) Rehearse** on three paths per field. **(8) Publish:** docs only; the sha256 smoke; print the prompts. **(9) Answers to the fields,** including ACMP's count (the exact sentence is in four briefs, because the 6.6.0 briefs say "the list") | **Replays:** equal blocking rules in both fields; the advisory vacuous; Jisr's candidates = [RISK-013]; verify clean; the open moves no file; Jisr's old slate answers read. **The way back** recorded as measured. **Main's** run green, with the tag on it. **Rehearsals:** every class holds, inside the cap. **The hashes:** git blob = gh raw = curl |

### The acceptance checks, as the fields wrote them

| Field row | Check | Beat |
|---|---|---|
| ACMP FB-034 | A `create` on an existing id is refused, and the result says inserted or updated | 258 |
| ACMP FB-035 | The query refusal names the columns | 258 |
| ACMP FB-036 | The brief states where PRE comes from, and what 2.3 compares against, when 2.1 never ran (rehearsed on the updated-first path) | 263 |
| ACMP FB-037 | §2 names the route and its limit, and the sha256 equals the source file's | 259 |
| Jisr FB-043 | A 17,114-character detail exports and shows its line breaks, and `slate.md` lists every cap | 257 |
| Jisr FB-032 | A two-line round intro renders on two lines | 257 |
| Jisr FB-034 | A 58-character path does not overflow at 390x844 | 257 |
| Jisr FB-033 | `.recreason` shows in the room view with no click | 257 |
| Jisr FB-025 | A one-key write leaves every other key unchanged, and a value outside the declared set is refused | 260, 261 |
| Jisr FB-029 | The docs and the rule name one form | 262 |
| Jisr FB-044 | Step 7 says what an agent proposes for a slice that has already started | 262 |

### The final verification

1. `check.py` green on 3.13 and 3.10, and with deprecations as errors.
2. The selftest.
3. `build.py --missing` empty, and `--check` equal.
4. `slate-browser` and the full matrix green on main's own run.
5. Every row of the acceptance table passes.

### Not built

- A folded `source` key.
- An edge-based discharge.
- `required` enforced at write.
- A hash on every write, or a hash on read.
- `create` as the default.
- A new diagram.
- Coverage tooling: the repo is stdlib-only, and its gate is `check.py`, so no 80% figure is claimed.
