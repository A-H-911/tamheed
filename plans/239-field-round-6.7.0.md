# Tamheed 6.7.0: Jisr's feedback round + standup withdraw/regenerate (REVISED after a strict review)

## Context

**Jisr's feedback.** Jisr exported its feedback register on 6.6.0
(the field's export: 21 rows, digest 8e824cb8…). Of the new rows FB-012..021,
six need work:

| Row | Kind | What it reports |
|---|---|---|
| FB-015 | doc-error | a refused `supersedes` edge |
| FB-017 | missing capability | `slate_read` is not exportable |
| FB-018 | doc-error | the browser check refuses a one-round page, and clears it first |
| FB-019 | missing capability | a closed set cannot hold booleans |
| FB-020 | question | the standup blocked list ignores the blocker's state |
| FB-021 | question | the restated scan flags phase conditions |

FB-008/010/012/014/016 register Jisr's local tools. FB-013 was rejected by Jisr. ACMP
(`8235a2f9`) filed nothing new.

**The operator's own request.** Two standup capabilities: withdraw a recorded report, and
regenerate a report.

**The operator's standing requirements:** full tests; docs, diagrams and every affected artifact
updated; an interview on every decision; the advisor's check.

**The review behind this revision.** It was asked for by the operator ("strict devil's
advocate"). Every claim was re-checked against the code by me directly, with sub-agent reports
treated as untrusted. One web check was made. Findings and corrections follow.

## 1. Weaknesses of the previous plan

1. **`blocks-lifted` could never pass.** It listed kept edges, so it failed forever. Fixed: it
   now lists open rows that are free to start.
2. **`_settled` had no legal home.** The server imports `standup_facts`, and the reverse import
   is impossible. And extracting the predicates as Python lists would silently drop the
   `population` and `indeterminate` of **`risks-discharged`, a BLOCKING rule**, and of
   `open-questions-resolved`.
3. **Withdraw as first drafted was unsafe.** The id is reused (`_next_id` takes MAX over the
   live table). A plain DELETE fails on a foreign key when anything names the report. Fourteen
   texts and three tests still say "immutable".
4. **R131 ("no migration") went stale** when withdraw added migration 012 and ADR-0004.
5. **Jisr's acceptance numbers rested on a stale copy.** Jisr has since retired both DEP-002
   edges, so its live record would show nothing of FB-020's fix.
6. **Unmeasured claims were stated as facts.** "1 of 3 id-dense becomes labeled" used a
   same-line heuristic. "48 checks" counted `check(` lines. "Same page bytes" holds only with
   the same engine and `standup.css`.
7. **Tests and docs that would break or drift were missed:**
   - JSON spelling for EVERY set would break four pinned tests;
   - the browser runner counts SKIP as a pass;
   - the runner's fresh Chrome profile cannot prove that a refused page was left alone;
   - release mechanics: the stock-history key is ALWAYS required; the evals pins; no
     `[Unreleased]` block; the lab refresh;
   - the guide's rule-count pin (31) and the conditional-rule list;
   - the migration-head pins (`tmc:4446`, `7102`);
   - the trigger prose in the guide;
   - lint 14 vocabulary (`retire` already names "a row leaves the record").

## 2. Assumptions

**Confirmed, by my own reading.**

FB-017 and FB-019:
- `_READ_TOOLS` is the six-tool tuple at srv:1817.
- `slate_read` (srv:6879) writes nothing, and its result has no `rows`/`count`.
- `values` must be all `str` (srv:1989-1992).
- Membership uses `in` (srv:2018-2021). `1 in [True]` and `{"a": True} == {"a": 1}` are both
  True.
- The retire door uses dict `==` (srv:2083).
- A register row's write re-judges the full declaration (srv:2053-2069), so 6.6.0 refuses writes
  to a boolean-set register.

FB-020 and readiness:
- `rule()` fails on a non-empty list, and `ids()` takes the table from the first `FROM`
  (srv:3451-3529).
- `risks-discharged` is blocking (3582-3586). `open-questions-resolved` is advisory and excludes
  Deferred/Rejected/Superseded/Obsolete (3618-3632).
- Jisr has 12 `blocked_by` edges, and all 15 of its dependencies are `Approved`. ACMP has 0
  edges.
- The guide pins 31 package rules (`extract.py:251`) and five conditional rules
  (`test_user_guide.py:194-195`).

FB-021:
- The prompt loop already unpacks `_kind` (srv:5136). The file scan is a separate call (4676).
- `labeled(start, end)` scans from start-3 through end, so a label inside the paragraph is seen
  when it is given the paragraph's span.
- The real detector gives Jisr 27 (24 status-claims + 3 id-dense) and ACMP 0. The pinned AGENTS.md
  case fires.

FB-018:
- The guard sits inside `try` after `clearAll()` (js:56-62), and the `finally` clears again.
- `second` is used at 61-62, 162, 163 and 199.
- The runner slices at `async () =>`, uses a fresh `--user-data-dir`, and prints only passed and
  failed.

Standup:
- RPT ids come from `_next_id` (srv:6469).
- The record note carries `custom_attributes.report` and is signed `system:standup-report`
  (6640-6645), and the window list filters that actor.
- The offset comes from the newest row of any kind (6398-6410).
- The migration head is runtime only (store.py:425-452), and `load` INSERTs every row under the
  DDL (store.py:491).
- The guide reads triggers from the live `sqlite_master` (extract.py:139-143). No migration has
  dropped a trigger before.

Tooling:
- `shift_221.py` re-aims `tamheed_server.py` only, mapping HEAD to the working copy.
- No guide pin names another file this round edits.
- The stamp scripts exist (`scripts-237/stamp_660.py`, `refresh_lab_660.py`).
- The CHANGELOG has no `[Unreleased]` block.

**Also confirmed, by direct reads made after the second advisor pass.**
- `slate_read`'s whole body (srv:6879-6978) holds no commit, write, insert, update or unlink. Its
  only guard is `_need_open`.
- The `blocked_by` rule (srv:163-165):
  - from-families: phase, slice, wbs-item, execution-plan, defect, deferred-work, open-question,
    decision, requirement;
  - far ends: the work families, open-question, dependency, decision, risk, assumption,
    execution-gate.
- The Implemented guard covers phases and slices only (srv:2313).
- No readiness rule reads a dependency's status.
- `execution-plans-approved` (3633) and `execution-plan-approved` (4034) accept `Implemented`.
- `assumptions-current` (3700) still flags an `Implemented` assumption past its date. It is
  unchanged; see the checkpoint.

**Researched (web), kept separate from my reasoning.**
- Azure's Event Sourcing guidance and Fowler's Event Sourcing never delete a recorded event. It
  is undone by a compensating record, and the original stays.
- R133/R139 depart from this on purpose (the operator's word). Keeping the row as `Withdrawn`
  would add a status that 6.6.0's CHECK refuses on load (store.py:491). The whole store could
  then not be opened on the way back.
- The journal note is our compensating record, and git keeps the removed row.

**Rejected.**
- "No migration": 012 is needed.
- "Ids are never reused": they are, today.
- "P1-P19 COMPLETE is caught": a one-letter prefix is not.
- "JSON spelling everywhere is harmless".
- "The runner can prove a refusal untouched".
- "`_settled` can live in the server".
- "Jisr's live record holds the DEP-002 edges".

**Unresolved. Each is measured in its beat, never assumed.**
- 6.6.0 opens a store after a withdrawal. This is reasoned from the load path; it is measured in
  246.
- The browser check's real counts, measured in 244.
- The real labeled count, measured in 242.
- Jisr's current state: a fresh export before 247.
- Whether DEC-172 changes anything. The field answers this in the brief.
- Which of Jisr's other 14 dependencies are met. That is the field's own judgement.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Extracting predicates changes a BLOCKING rule's verdict | SQL WHERE-fragment constants passed through `ids()`; a test pins status + population of both rules on an empty and a populated family BEFORE the change (red if the extraction drifts) |
| Withdraw loses data or breaks the chain | Refuse a correction, a report anything depends on (named rows), a live Draft and a same-seq twin. One transaction for row + note. The page is unlinked after commit, and a failed unlink is named. Tests for each refusal and a raw-DELETE trigger test |
| Withdraw mistaken for erasure | The docs say: the row leaves the store, git history keeps it, words included (R139) |
| Id reuse confuses audits | The allocator takes MAX over the table and the recorded/withdrawn notes; tested; 6.6.0's reuse is named in the brief |
| 6.6.0 way back | Measured on scratch copies after a withdrawal and with a boolean set; the brief names both notes |
| FB-021 hides a real stale copy in a situational prompt | Accepted by the operator (R122); kickoff and agent-control files keep the scan; tallies and runs still scan every prompt |
| The browser check still damages a page | Shape judged before ANY change; a refusal proven BY HAND in DevTools on an answered page (localStorage before/after) |
| Guide drift (line pins, rule counts, trigger prose) | `shift_221.py` before every server-editing commit ("unmapped citations: []"); pins updated in the same beat; `build.py --check` in the gate |
| The lint 14 vocabulary refuses new words | New engine strings written to the roster; `withdraw` gets its own vocabulary row (R140) |
| Field acceptance on stale data | The operator's read-only fresh Jisr export (Step 0, as in plan 238) before 247's replays and briefs |
| A large round runs long or half-lands | One commit per beat on `round/6.7.0`; CI per push; surprises listed before every commit question; main untouched until release |

## 4. Changes from the previous plan, and why

- **`blocks-lifted` is redefined** to "free to start": open from-rows, emitted only when edges
  exist, with a hand-set population. This makes it satisfiable and avoids a permanent
  indeterminate.
- **`_settled` moves into `standup_facts.py`** with SQL fragments, because of the import
  direction and the population rules.
- **Withdraw is fully specified:** the reference checks, the order, the actor, no id reuse,
  migration 012 keeping the trigger's name, ADR-0004, the 14 texts, re-aimed tests, and the
  vocabulary row.
- **Spelling:** JSON spelling only for boolean sets, which keeps the four pins.
- **Browser check:** a SKIP count, and the refusal proven in DevTools.
- **Fresh Jisr export:** added before 247; the brief restores the edges (R138).
- **Implemented widened** in governance.md:92, with a dry-run on a copy that compares gates and
  readiness.
- **Release mechanics corrected:** stock-history key, evals pins, `[Unreleased]`, lab refresh.

## Rulings (operator, 2026-11-16)

| # | Ruling |
|---|---|
| R121 | FB-020: the standup list reads the far end through ONE shared settled rule; a met dependency takes `Implemented` |
| R122 | FB-021: status-claims in prompt rows only in **kickoff** prompts; CLAUDE.md, AGENTS.md and the package CLAUDE.md keep the full scan; id-dense honours a label |
| R123 | FB-019: `values` all text OR all booleans, type-strict; boolean sets print in JSON spelling; the retire door's `==` fixed |
| R124 | FB-015: fix the texts; `supersedes` stays within a family; the 6.5.x briefs stay as history |
| R125 | FB-017: `slate_read` joins `_READ_TOOLS`, with its time stamps, digest scope and read-back rule stated |
| R126 | FB-018: shape guard before any change; one-round mode with SKIP; the shape named everywhere |
| R127 | the settled rule also feeds a readiness advisory |
| R128 | proceed without DEC-172; the Jisr brief asks about it |
| R129 + R135 | the settled table below; edge cases accepted and documented |
| R130 | `blocks-lifted` = open rows whose every `blocked_by` far end is settled; edges kept as history |
| R131 + R137 | 6.7.0 MINOR on `round/6.7.0`, still MINOR with migration 012 + ADR-0004 |
| R132 | two briefs to the 6.6.0 standard |
| R133 | withdraw = the newest daily report or any override; a correction is refused |
| R134 | withdrawal confirm with words; a journal note without the words; ids never reused |
| R136 | regenerate = rebuild recorded pages from stored rows + a "redo a report" skill step (existing `supersede`) |
| R138 | Jisr brief: re-write the two retired DEP-002 edges as history, DEP-002 → `Implemented`, on its operator's word |
| R139 | withdrawal removes the row (not a status); the docs say it is not erasure |
| R140 | the action is `withdraw`; vocabulary.md gains its row |

**The settled table.** It is defined in `standup_facts.py` and imported by the server:

| Far end | Settled when |
|---|---|
| dependency, assumption, phase, slice, wbs-item, execution-plan | Implemented, Superseded, Obsolete or Rejected |
| defect | Fixed, Won't-fix or Duplicate |
| deferred-work | Done or Won't-do |
| open-question | NOT `_OQ_UNRESOLVED` (the open-questions-resolved predicate) |
| decision | Approved, Rejected, Superseded or Implemented |
| risk | NOT `_RISK_UNDISCHARGED` (the risks-discharged predicate) |
| execution-gate | `outcome` = Go |
| a missing row | not settled |

## 5. Refined execution plan

**Every beat follows the same loop:**
1. A red test, then the code.
2. `ecc:code-reviewer`; each finding is re-run before it is folded.
3. For a beat that edits the server: `shift_221.py` before the commit ("unmapped citations:
   []"), then `docs/guide/build.py`.
4. Lint 14 clean.
5. `python check.py` on 3.13 and on 3.10.
6. The surprises list to the operator, then ONE question that names the commit AND the push.
7. Dispatch CI (`gh workflow run ci.yaml --ref round/6.7.0`; a push to a branch runs none), and
   wait for green.
8. For 243 and 246 (file operations, untrusted input): `ecc:security-reviewer` beside the code
   reviewer.

Each beat adds to `## [Unreleased]` in the CHANGELOG.

**239: the record.**
- Rulings R121-R140 and the triage go into the round record; rows 239-247 go into
  `plans/README.md`; cut `round/6.7.0`.
- *Validation:* `check.py lint`.
- *Output:* one docs commit.

**240: FB-019, boolean sets.**
- The declaration takes all-str or all-bool, and a mixed set is refused, naming both forms.
- Membership is type-strict.
- The retire door compares `json.dumps(sort_keys=True)`.
- A boolean set prints `true / false` in the refusal and on the page; text sets are unchanged.
- Docs: governance.md:216, artifact-catalog.md:119, srv:2001 docstring, guide `table.registers`
  EN + AR.
- *Validation:*
  - new tests: bool set accepted; mixed refused; `1`/`0`/`"true"` refused against
    `[true, false]`; page spelling; a retire of `{"a": 1}` against a stored `{"a": true}` judged
    as changed;
  - pins tmc:1635/1673/1766 and test_export_html:620 unchanged.
- *Output:* the suites green; one commit.

**241: FB-020, settled + blocked list + `blocks-lifted`.**
- `_OQ_UNRESOLVED` and `_RISK_UNDISCHARGED` become fragments; `_settled` and the open-row
  definition live in `standup_facts.py`.
- `blocked()` reads the far end (its near end stays WBS and slices).
- **Step 0, before any code:** a dry-run on a Jisr copy moves one dependency, assumption and
  plan to `Implemented`, and compares `gate_run`/`readiness_check` before and after. STOP and
  ask if a write is refused or a blocking rule moves.
- `oq_na`, `na_note` and `open-questions-overdue` are left exactly as they are.
- The advisory `blocks-lifted`:
  - **Entities:** the ids of OPEN from-rows whose every `blocked_by` far end is settled.
  - **Open rows:** "open" = not settled. A requirement is open unless it is Implemented,
    Superseded, Obsolete or Rejected. The from-families are phase, slice, wbs-item,
    execution-plan, defect, deferred-work, open-question, decision and requirement.
  - **Extra key:** `lifted: {id: [far ends]}`.
  - **Population:** set by hand, `{"table": "trace_edges", "rows": n, "unit": "blocked_by
    edges"}`.
  - **Emitted** only when a `blocked_by` edge exists.
  - **Remedy text:** "Rows whose every blocker is settled. The edge stays as history; nothing is
    retired. Start the work. The row leaves this list when it closes. If it waits on something
    else, record that as a new `blocked_by` edge. A `WVR-` row carries a deliberate wait, on
    the operator's word."
- The docs also state:
  - the R135 converse: a retired risk still `open` keeps blocking;
  - a gate lifts its block only by its `outcome` column being Go; a journal entry alone lifts
    nothing; a later Hold, Redirect or Kill re-blocks.
- Pins: `extract.py` 31 → 32; the conditional list.
- Docs: quality-gates.md:62-63 (stale count fixed) and :102; server README:113;
  register-liveness item + renumber; governance.md:92 (Implemented = met for a
  dependency/assumption/plan) and :313-325; traceability.md; entities.md; standup SKILL (new
  sentence); guide EN + AR (`rule.blocks-lifted`, `rel.blocked_by`, `type.dependency`).
- *Validation:*
  - a PRE-change test pins both extracted rules' status and population, and stays green after;
  - `blocked()` gets one test per far-end family plus a missing row;
  - the advisory: pass, fail, waived, and not emitted;
  - a dry-run on a Jisr copy moves one dependency, assumption and plan to `Implemented`, and
    compares `gate_run`/`readiness_check` before and after (expected: only `blocks-lifted` and
    the moved rows' own rules change).
- *Output:* green; one commit.

**242: FB-021, the restated scan.**
- `_restated_findings(..., claims=True)`; the prompt loop passes `claims=(kind == "kickoff")`.
- id-dense calls `labeled(para_start, i)`, keeps `kind: "id-dense"`, and adds `labeled: true`.
- Docs: handoff.md:178-183, prompt-templates.md, agent-control.template.md.
- *Validation:*
  - tests: phase and situational bodies give 0 claims; a kickoff fires; the AGENTS.md pin
    unchanged; a labelled paragraph is labeled;
  - the real detector on the Jisr copy is MEASURED (expected 3 id-dense, 1 labeled).
- *Output:* green; one commit.

**243: FB-017, export of `slate_read`.**
- The tuple gains it. The docstring states the `exported_at` time stamps, the outside-store
  inputs and the store-only digest.
- Docs: architecture.md:105, server README:118, SECURITY.md:164-167, guide `tool.entity_export`
  EN + AR, operator-interview (the read-back stays required).
- *Validation:* tests in `test_slate.py`: an export written with no `partial`, the screened and
  provenance keys kept, a missing answers file returns the error and writes no file.
- *Output:* green; one commit.

**244: FB-018, the browser check.**
- The shape is judged before the `link.click` override and before the `try`, so a refusal
  returns untouched.
- **Refused (untouched)** only when no ready round holds a question of the room.
- **The condition → check map:**

  | Condition | Checks it gates |
  |---|---|
  | a second ready round after the first | 120, 121, 161-164, 167, 199-201 |
  | a not-ready round | 126 |
  | participants | 128-134, 151-158 |
  | an operator question | 78, 141 |
  | a recommendation | 83 |

  Each gated check prints `SKIP <name> (needs …)`. No statement uses `second` (open, `$$`) when
  it is absent.
- The header comments must not contain `async () =>` (the runner slices at it).
- `skipped` is counted; the runner prints passed/skipped/failed and exits 0 on no failure; the
  headers name the shape; `tests/README.md:24`.
- *Validation:*
  - Chrome: the two-round demo's count MEASURED; a one-round demo (from `demo_227c.py`) shows the
    one-round checks pass and the rest SKIP;
  - the refusal BY HAND in DevTools on an answered page, localStorage before = after.
- *Output:* the measured counts recorded; one commit.

**245: FB-015, the texts.**
- package-writes 7b, governance.md (344-347, 236-238), governance.template.md:77-78,
  entities.md (1075-1076, 1317-1318), artifact-catalog.md:120, guide prose if it states the
  rule.
- *Validation:* lint, gate.
- *Output:* one docs commit.

**246: standup withdraw and regenerate.**
- Migration `012_standup_withdraw.sql` drops and recreates `trg_standup_reports_keep`, keeping
  its NAME. A DELETE is allowed only for a Draft, or for an Approved row that nothing names, that
  has no `supersedes` and no same-seq twin.
- `action='withdraw'` (`report`, confirm `{operator_confirm, by, words}`):
  - the reference pre-check names the rows (edges; `subject_id`; every
    `REFERENCES entity_index(id)` column; `base_report`/`supersedes`; a live Draft; a same-seq
    twin);
  - one transaction: delete + a note signed `system:standup-report` with `{"report", "withdrawn":
    true}`, no `subject_id`, no words;
  - commit, then unlink the page; a failed unlink is named.
- The allocator takes MAX over the table and the notes.
- `action='regenerate'` (`report` or all recorded): rebuilds pages from stored rows; no row
  change; `draft.html` untouched.
- `_STANDUP_DESC` under 2,048 (today 1,251).
- ADR-0004; vocabulary.md row; SKILL steps "withdraw a report" and "redo a report".
- The 14 texts swept: desc, srv:471, SKILL:71/83, entities.md:1101-1109, artifact-catalog:121,
  governance:249-253, guide content.py:801/1104/1107/1282 EN + AR, SECURITY:208-209, server
  README:126, CHANGELOG, an SR23/SR24 superseding ruling row.
- Pins: migration head `tmc:4446`, `7102` → 012; `tmc:7139-7140` (a raw DELETE of a recorded
  MIDDLE report still raises), `7110-7117` and `7484-7488` re-aimed.
- *Validation:*
  - tests: withdraw the newest daily (the window reopens); withdraw an override; refusals (a
    correction, a middle report, a live draft, a referenced report, a same-seq twin, no words);
    no id reuse; a raw middle DELETE raises; regenerate gives the same bytes on the same engine
    and moves no data file;
  - the way back MEASURED: the real 6.6.0 (from the tag) opens a store after a withdrawal.
- *Output:* green; one commit.

**Step 0, now, the operator, in parallel with 239: a fresh Jisr export.**
- The read-only prompt of plan 238, printed at approval: git reads, `server_info`, a git archive
  of the tracked paths, copies of untracked files, a MANIFEST, and status before = after.
- It is used to:
  - read DEC-171 onward, so DEC-172 is no longer unresolved;
  - run 241's dry-run;
  - run 247's replays.

**247: release 6.7.0.**
1. Re-read Jisr's export if the field moved since Step 0.
2. **Acceptance:**
   - `check.py` on 3.13, 3.10 and under `PYTHONWARNINGS=error::DeprecationWarning`;
   - `--selftest`;
   - a scratch scenario through every behaviour.
3. **Field replays on scratch copies** (`python -I`):
   - Jisr (fresh): with the two edges re-written and DEP-002 `Implemented`, SL-008 leaves the
     list and `blocks-lifted` lists it; the restated count is as measured in 242; withdraw and
     regenerate on the copy;
   - ACMP: measured unchanged.
4. **Stamp:**
   - the six surfaces;
   - CHANGELOG 6.7.0;
   - the stock guide body + the REQUIRED 6.7.0 `stock-history.json` key;
   - the `evals/evals.json` pins;
   - the lab refresh through the engine;
   - the three READMEs;
   - `index.html`.
5. **On the operator's word:** fast-forward main, push, CI, tag `v6.7.0`, ledger.
6. **Briefs (R132, R138):**
   - **Way back:** the plugin pin, plus three notes: rewrite boolean sets before going back;
     6.6.0 reuses withdrawn ids; a withdrawal stays withdrawn.
   - **Jisr's brief also names:** the edges and DEP-002, the FB rows to resolve, the 6.5.x
     correction, and the DEC-172 question.
   - **Publishing:** rehearsed headless under the real 6.6.0 and the new 6.7.0 bundles, then
     published pinned (sha + sha256), then the smoke, then the two one-line prompts.

**Expected outputs of the round:**
- eight commits on `round/6.7.0` (239-246), CI green on each, plus the release commit;
- tag `v6.7.0`;
- two pinned briefs with their prompts;
- the round record R121-R140 with the measured numbers.

## 6. Approval checkpoint

Approving this plan approves the rulings R121-R140 above, AND the defaults below, which I chose
without a separate question. Name any you want changed.

1. **Regenerate's scope.** It rebuilds every recorded page, Superseded ones included. No
   "superseded" marker is added to a page, and the draft page is left alone.
2. **Withdraw refuses rather than cascades.** It refuses while a Draft exists, and when any row
   references the report. It names the references and changes nothing.
3. **The page is unlinked AFTER the commit.** A failed unlink leaves a stray page, named in the
   result; the row is already gone, and the record is the truth.
4. **Two scopes.** The standup "Blocked work" list stays on WBS items and slices, as today. The
   `blocks-lifted` advisory covers all nine families that can be blocked.
5. **No `slates/` refusal.** An export path under `slates/` is not refused (low risk, said in the
   record).
6. **A discarded draft's id stays reusable.** A draft is not a record, so only recorded and
   withdrawn ids are never reused.
7. **`assumptions-current` is unchanged.** It still flags an `Implemented` assumption past its
   validation date. Teaching "a met assumption takes `Implemented`" therefore leaves such a row
   flagged until its date moves. Widening that rule is not built.
8. **Step 0 is your action.** The fresh Jisr export runs now, in parallel with 239. The
   read-only prompt is printed when you approve.
