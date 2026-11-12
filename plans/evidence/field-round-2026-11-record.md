# Field round 2026-11: ACMP FB-030..032 + Jisr FB-001..011 -> tamheed 6.5.0 (plans 221-229)

## Context

Two field projects on tamheed 6.4.0 handed up operator-confirmed feedback rows: ACMP three
(`feedback-fb030-032.json`), Jisr eleven (`feedback.json`, two of them `local-tool` registrations).
Every claim was checked against the source at `6169f14`, and against ACMP's own store. All ten
actionable rows are true. Three are wider than reported. The operator ruled the open design calls on
2026-11-11 (R81-R89 below). Outcome: one MINOR release, 6.5.0, that answers every row, with tests,
the guide and its diagrams, and one upgrade prompt per field.

## Revision 2 - the devil's-advocate review (2026-11-11, before any execution)

Method: every load-bearing sub-agent claim was re-read in the source or re-measured by me. An
adversarial design reviewer and the advisor each challenged the plan. Research was three targeted
web searches, not a `/deep-research` run. Two findings overturned ruled designs and were put to the
operator again (R88, R89).

### 1. Weaknesses of the first plan
- **Lock (224).** It trusted a machine id. Machines built from one image share it (confirmed by
  search), so a renamed clone on shared storage could have freed a live writer's lock.
- **Migrate lock (224).** Offered as small and safe. A readable lock would let `package_unlock` pass
  a half-swapped store: nothing checks `data/*.jsonl.tmp`, and a missing table file loads as empty.
- **Registers (226).** A new JSON text column. The blocking content gate grades every text column,
  so an allowed value such as `TBD` would fail it. Eight server sites special-case the literal `custom_attributes`.
- **Interview page (227).** "The package moved" was true after any write. The slate name became a
  file name unchecked. Callers could name paths. A hash CSP does not allow inline event handlers.
- **Read (221).** Two existing answers became refusals inside a MINOR. The default payload was unmeasured.
- **Wired rule (222).** The plan said a waiver clears the list. `gate_run`'s copy has no waiver path.
- **Sections (225).** It said three scans read sections (two do), and it leaned on 226's registry-sync unsaid.
- **Process.** Sub-agent reports were used as facts in places, and the plan was handed over before
  one review had reported. No checkpoint covered a stalled Step 0.

### 2. Assumptions
**Confirmed by my own reading or measurement**
- `trace_query` reads edges only, unordered, with no total (srv:2611). `entity_query` echoes nothing (srv:2551).
- Both wired surfaces count any edge (srv:2762, 2991). The ruled predicate runs in 1 ms on ACMP and lists FR-156..159 only. On the repo's four fixtures it lists nothing.
- The migrate lock is written empty (srv:4914). `package_open` never touches `.tmp` staging (srv:1433), and the only `.tmp` glob is a rollback helper (srv:4690).
- `store.load` binds an explicit NULL for a missing column (store.py:372), so a new column must be nullable. On an in-memory schema the scanners' literal drops every live section after the `ALTER`.
- The enum parser reads 97 value sets from `sqlite_master`. The trace-edge ignore path returns a generic text (srv:2223).
- Column links derive from `PRAGMA foreign_key_list`: FR-166 returns AC-184, SL-043 returns 249 links. Payload for SL-043: 6.0 KB grouped, 17.5 KB flat, against 187 bytes today.
- `REG-` and `ENT-` occur nowhere in ACMP, the local Jisr copy or the four fixtures. `REC-` does (ACMP).
- `_PLAIN_PROSE_COLUMNS` holds no section column. The eval fixture pins `verified=True`. The pins the reviewer listed exist (`test_user_guide:194, 207, 214`, `test_export_html:567`, `content.py:1138`, `check.py:434`).
- Baseline: `check.py` twice, the selftest, the guide build and all twelve suites pass at `6169f14`.

**Rejected**
- A machine id proves the same machine. (Clones share it.)
- pid 4 gives a Windows boot marker. (Measured: `unobservable` for a standard user.)
- A second JSON column is cheap. (Eight literal sites, and the content gate grades it.)
- The package digest tells whether quoted rows changed. (Any write moves it.)
- A waiver clears FR-156..159 on both surfaces. (Only readiness applies waivers today.)

**Unresolved, each with the place it is measured**
- macOS: the boot-session sysctl, the process start time, the struct size. Step 0 probe, then the macOS CI leg.
- The Linux pid-namespace check does not tell two hosts apart (the initial namespace has one constant id). My reasoning, not measured here. A test on the Ubuntu leg records the value.
- A hash CSP in a meta tag on `file://`, stored state, and the download. Chrome at acceptance, then the field browser through the Jisr prompt. The page works without the last two.
- The guide's figure geometry and every suite on macOS. The baseline CI run, first commit.
- SQLite versions on the CI images. The same baseline run prints them.
- Jisr's real register rows and page. Step 0, then the design checkpoint.

### 3. Risks and mitigations
| Risk | Mitigation |
|---|---|
| A lock freed under a live writer | R88: only a matching boot session bridges a host-name change. Other-machine, after-restart and Windows cases stay manual. The staging guard of R89. Seam tests for every branch |
| Step 0 stalls and holds ACMP's fixes | Named checkpoint: when 221-225 are done and the folder is not here, the batch is put to the operator again (cut 6.5.0 without 226/227, or wait) |
| 225 loses its upgrade step if 226 leaves | The same checkpoint. Without a new family no sync opens, so the prompt would then name the silent one-time rewrite and run a close before any verify |
| Guessed register rules reject real rows | No build before Jisr's rows are replayed through the family on a scratch copy |
| Script in a generated page | One static script named by hash, no inline handlers, no JSON block, `base-uri` and `form-action` closed, fixed file locations, a checked name, hostile-text tests, a security review |
| An answers file taken as the operator's word | `slate_read` writes nothing. The skill requires an in-session confirmation, and a file from an earlier session is history |
| The first macOS CI run is red for other reasons | It lands alone and first. A failure outside the lock is reported, and narrowing that leg to the lock suite needs the operator's word |
| A larger default answer from `trace_query` | Grouped pairs (6 KB worst case on ACMP). `relation=` returns edges only |
| A new advisory that cannot be cleared | Both surfaces honour a waiver. `gate_run` names waived ids, never hides them |
| The field's private data on this machine | The Step 0 folder stays outside the repository. Evidence is trimmed (R72). Nothing from it is committed |
| A long branch drifts or loses its thread | Plan files 221-229 and the ledger section are written first. One commit per plan, each green on `check.py` |
| Server line cites in the guide rot (about 85) | The shift script and the byte-twin test, in every plan that edits the server |

### 4. Changes made, and why
- 221: unknown `relation` or id answers ok with a named `warning`, not a refusal (stays additive).
  `column_links` is grouped by column (measured payload). `limit` and totals unchanged.
- 222: `gate_run` subtracts waived ids and lists them under `waived` (the statement to the operator now holds).
- 226: a family the package's registry does not know yet is refused with the route (today a bare FK text).
- 224: boot session replaces machine id (R88). The staging guard joins the migrate lock (R89). No hardware id is read, so nothing is hashed or stored about the machine.
- 225: two scans, not three. `status=` selects retired sections only. The sync dependency is stated.
- 226: declared fields and entry values live in `custom_attributes` (no new JSON semantics, the content gate skips it). The guard runs on the materialised row. The filter is named `register_id`.
- 227: no caller path, the name checked by `_bad_name`, ids read from the DOM, per-row change detection, a reason on the recommendation, freshness stated.
- Step 0: the probe measures every candidate lock signal in one trip.

## Evaluation (measured, `srv` = `plugins/tamheed/server/tamheed_server.py`)

| Row | Verified | Answer | Plan |
|---|---|---|---|
| ACMP FB-030 no bulk edge read | `entity_query` refuses `trace-edge` (srv:2487). `trace_query` takes one id, has no `ORDER BY` and no `total` (srv:2611) | bulk form, ordered, with `total` | 221 |
| ACMP FB-032 `requirement_id` invisible | `trace_query` reads `trace_edges` only. The review page already merges the column (export_html.py:815). `slice-review` and `slice-kickoff` look for a slice's criteria through edges, but criteria bind by `slice_id` | foreign-key columns returned as `column_links`, never copied into edges | 221 |
| Jisr FB-009 no argument echo | envelope at srv:2551. `trace_query` echoes nothing either | `query` key on both | 221 |
| ACMP FB-031 wired rule fooled | both surfaces count ANY edge (srv:2762, srv:2991). Measured on ACMP today: the rule lists nothing | read the three legs | 222 |
| Jisr FB-002 enums untold | `_AUDIT_RECORD_DESC` names keys only (srv:5632). The refusal is raw `str(exc)` (srv:3544), and SQLite names only the first failed CHECK | one DDL-derived hint, all bad values at once | 223 |
| Jisr FB-003 gate words | CHECK `Go/Hold/Redirect/Kill` (schema.sql:534). The bundle names the four words and defines none | define them (R83) | 223 |
| Jisr FB-001 lock after rename | exact `socket.gethostname()` compare before any probe (store.py:203). On macOS a running pid is always `unobservable` (store.py:81) | the boot session bridges a rename, plus three extras (R86, R88, R89) | 224 |
| Jisr FB-011 section retire | retire is trace-edge only (srv:1832). `document_sections` has no lifecycle column | nullable status column (R85) | 225 |
| Jisr FB-004/005/006 typed registers | no package-level family mechanism exists. `custom_attributes` fields are dropped from the review page (export_html.py:789) | generic register family (R81) | 226 |
| Jisr FB-007 interview surface | `review.html` forbids script. ACMP keeps 12+ static slates, Jisr an interactive one | slate page + read-back tool (R82) | 227 |
| Jisr FB-008, FB-010 | local-tool registrations | nothing to build. FB-010 imports the plugin's `ste_lint.py` by cache path: named in the Jisr prompt | - |

## Rulings (operator, 2026-11-11; R80 was the last)

- **R81** Typed registers are built in this release. Jisr's data comes through an export prompt (Step 0).
- **R82** The interview page is built in this release, as a separate page. `review.html` stays
  script-free. Moved premise: both fields hand-build slates, and a 71-question workshop does not fit a session question.
- **R83** `Hold` carries a No-go whose blockers are recorded, worked and put again. `Redirect` = the
  plan or scope changes first. `Kill` = the guarded work stops. No schema change.
- **R84** `requirements-wired`: listed with no decision, work or test link, and an `Implemented`
  requirement when it lacks any of the three. The result names the missing leg. Still advisory.
- **R85** A section is retired through a nullable `lifecycle_status` column.
- **R86** Lock extras: the interrupted-migrate lock, the live-holder hint, and the macOS start time
  (taken against the maintainer's recommendation, so CI gains a macOS leg to test it). Its
  machine-identity part is superseded by R88.
- **R87** 6.5.0 MINOR.
- **R88** (re-put after the review) The boot session is the signal that bridges a host-name change.
  It does not survive a restart. After one, and on Windows, removal stays manual.
- **R89** (re-put after the review) The migrate lock becomes readable, and `package_unlock` refuses
  while any `data/*.jsonl.tmp` staging file exists.
- **R90** (at plan 222's commit) `requirements-wired` reads a requirement as live until its
  `retired_in` is set, as G-TRACE does. A dead status alone does not take a row out of the rule.

## Step 0

A read-only export prompt was handed to the operator for the Jisr machine (the package copy, the
project files the designs are measured against, and a macOS probe of every candidate lock signal).
It blocks plans 226, 227, the macOS half of 224 and the Jisr replay. Its folder is private and is
never committed here (R72).

## The plans (one commit each on branch `round/6.5.0`; tests red first)

Shared mechanics for every plan that edits `srv`: the guide cites server line numbers
(`docs/guide/diagrams.py` `TOOL_EFFECTS`, `GATE_HOW`, `VACUOUS`; `tests/test_user_guide.py:143,167`).
Re-aim them with a shift script derived from `plans/evidence/scripts-217/shift_217.py`, then
`python docs/guide/build.py`, then `python check.py`. New text passes lint 14 (25 words, no semicolon).

Pinned counts that move in this round, each re-aimed in the plan that moves it: schema head 8 to 10
(`test_mcp_contract:244, 3239`), tables 42 to 44 and tools 19 to 21 (`test_user_guide:205`, the
selftest line, the READMEs, diagram D2), suites 12 to 13 (`check.py` `SUITES`), package readiness
rules 30 to 31 (`extract.py:251`), relations stay 16, journal event kinds stay 12. Also pinned and
verified to exist: the conditional-rule list (`test_user_guide:194`), the tool groups
(`extract.py:45`), "Seven families" of own-status tables (`content.py:1138`, EN and AR), the id
prefix list (`check.py:434`), one fold per table (`test_export_html:567`), about 85 server line
cites in `diagrams.py`, lints 7 and 11, the lock's field list (`db/CANONICAL.md:57`).

Named checkpoint, a stalled Step 0: when 221-223, 224a and 225 are done and the Jisr folder is not
here, the batch is put to the operator again (release without 226, 227 and 224b, or wait). R81 and
R82 were ruled on the premise that the data arrives.

Order on the branch: the macOS CI leg lands FIRST, alone, and is dispatched on the branch for a
baseline. That leg has never run `check.py`, and the tag will depend on it. The baseline names what
is red on macOS today (the real-process probe test may be, until 224b). The leg is green at the tag.

## Reviews behind this plan
- The advisor reviewed the approach before the rulings and the plan after them. Its findings are in:
  the measured predicate for 222, the DDL-derived hint for 223, the split of 224, the additive
  warnings in 221, the field-browser checks in 227, the Step 0 edits.
- The adversarial design review of 225, 226, 227 and the lock reported after the first hand-over.
  I re-checked its claims in the source before using them. Nine findings are folded in (Revision 2,
  section 4). Two overturned ruled designs and were put to the operator again (R88, R89).
- Research: three targeted web searches. Confirmed: cloned images share a machine id. Confirmed:
  a CSP hash allows an inline script and not an inline event handler. Found, not yet measured: the
  macOS boot-session sysctl. No `/deep-research` run was made.

## 5. Execution order and validation points
| # | Step | Validation point | Expected output |
|---|---|---|---|
| 0 | Operator submits the Step 0 prompt on the Jisr machine | `MANIFEST.txt`, two probe files with equal hashes | the folder, outside the repository |
| 1 | Branch `round/6.5.0`. Plan files 221-229 and the ledger section. The macOS CI leg alone | CI dispatched on the branch | a baseline: what is red on macOS today |
| 2 | 221, 222, 223, each red-first, one commit on the operator's word | `check.py`, replay on a scratch copy of ACMP, code and security review, advisor | the three ACMP rows and FB-002, FB-003, FB-009 answered |
| 3 | 224a, 225 | `check.py` on three OS legs, fixtures verify clean | schema head 9, the staging guard, the Linux boot bridge |
| 4 | Checkpoint: is the Step 0 folder here? | operator interview if not | go on, or re-put the batch |
| 5 | Design checkpoint for 226 and 227 on Jisr's rows and page | replay refusal count, layout against the field page | the operator's rulings on prefixes, grammar, layout |
| 6 | 224b, 226, 227 | `check.py`, security review, browser pass with captures | schema head 10, tools 21, a slate read back |
| 7 | 228 the guide, diagrams, docs | `build.py --missing` empty, geometry lint, byte-twin | `index.html` rebuilt in EN and AR |
| 8 | 229 acceptance on the merged state | both `check.py` runs, selftest 21/21, scratch scenario, both field replays | every changed behaviour exercised once |
| 9 | Release on the operator's word | CI green on every leg, then the tag | `v6.5.0`, bundle diff 0 against the tag |
| 10 | The two field prompts, each recipe dry-run first | probes hold on the scratch copies | two prompts handed in session |

## 6. Approval checkpoint
Approving this plan approves: the nine plans as revised, R81-R89, the Step 0 prompt as printed, a
macOS CI leg, two new tools, two migrations, and work on a branch with one commit per plan, each on
the operator's word. It approves no push, no tag and no release: those are asked at step 9. Nothing
has been executed.

## Not built, and why
- An unlock for a lock held on another machine: a pid absent here proves nothing about there, and
  the shell's permission prompt is the operator's checkpoint for that removal.
- A machine identity in the lock, and a Windows boot marker: the first is shared by cloned
  machines, the second could not be read by a standard user.
- A status filter on the two wired surfaces (they read `retired_in` only, as G-TRACE does): not asked.
- Project-defined rules over register fields ("no result on a non-approved row"): a rule language is
  a second engine. The project's test stays an inspection, over typed data.
- A tool that writes decision rows from an answers file: the word stays the session's.

## Verification
0. Baseline, measured 2026-11-11 on the untouched tree at `6169f14`: `python check.py` passes, it
   passes again with `PYTHONWARNINGS=error::DeprecationWarning`, and the selftest registers 19/19
   tools (longest description 387). The five suites this round extends run 222, 20, 47, 16 and 11
   tests (`test_mcp_contract`, `test_db_roundtrip`, `test_export_html`, `test_user_guide`,
   `test_store_migrations`). A later failure is this round's.
1. Per plan: the red-first test, `python check.py`, a code review and a security review of the diff
   (lock, file reads, generated script), the advisor, then the operator's word for the commit.
2. End to end: 229's acceptance list. Field proof: each prompt's probes hold in the field, or the
   field files a row.
