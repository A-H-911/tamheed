# Lab acceptance report — the real-agent runs against the 5.8.1 working tree (plan 172, R60/R61)

Run 2026-09-30T21:42Z → 22:40Z by the maintainer's harness (`plans/evidence/scripts-fb028/`:
`labrun.py`, `labrun_turns.py`, `labrun_a2_setup.py`, `labrun_b_setup.py`, `labrun_check.py`,
`labrun_census.py`; the operator's words in `run-words.md`; the prompts `run-a1.md`, `run-a2.md`,
`run-b.md`; the outputs `labrun_check.{a1,a2,b}.out.txt`, `labrun_census.out.txt`). Every
session: Claude Code **2.1.286**, model **`claude-opus-5-5`** (each transcript's `model` attachment),
`--plugin-dir <working tree>/plugins/tamheed`, `--setting-sources ""`, `--permission-mode dontAsk`
with `--allowedTools`, never `bypassPermissions`, `--max-turns` and `--max-budget-usd` on every
process. The packages stay in the session's scratchpad (`lab-run-A/`, `lab-run-B/`); nothing of a
run is committed except this report, the harness and its outputs. The transcripts
(`~/.claude/projects/<ws slug>/<sid>.jsonl`, copied beside each result under `runs/`) are the
record; §4 quotes them. **Cost:** A1 $2.03, A2 $12.44 (twelve processes), B1 $0.80, B2 $0.77,
B3 $1.06, B4 $1.69, the probe $2.14 — $20.93 in all, inside the approved 20 + 15 + 4×8 plus the
probe.

**The result in one line:** every mechanism the scenario's items 1–9 name fired under a real
agent through the plugin's own path — the skills loaded by slash command, the tools through the
MCP server, the writes under `dontAsk` — and the 38 predicates of `labrun_check.py` all pass
(15 for A1, 14 for A2, 9 for B). No engine defect was found; five things are for the maintainer
(§5).

## 0. The probe (U25/U26) — six short sessions, what each measured

| # | Flags | Measured |
|---|---|---|
| 1 | `--setting-sources ""`, `--plugin-dir`, `dontAsk`, allow `mcp__plugin_tamheed_tamheed__*` + file tools + `Bash(python test_tracker.py*)` | `server_info` **5.8.1** (the working tree), one tool prefix (`mcp__plugin_tamheed_tamheed__`, 19 tools), no other plugin's tools or hooks; `package_create` and `package_close` ran under `dontAsk` with no prompt; the model chose **PowerShell** for `python test_tracker.py` and was denied (`Bash(...)` was the rule); a slash command inside a longer prompt is NOT expanded — the model called the Skill tool and was refused ("cannot be used with Skill tool due to disable-model-invocation"). The tamheed server's stderr on first connection: 31 pydantic validation errors for `server/discover` (the client's first-connection probe against the Python MCP SDK; the connection succeeded 1 ms later; later sessions "skip the server/discover probe" per the debug log) |
| 2 | as 1, the prompt = `/tamheed:orient-resume probe` | **the slash command as the whole `-p` prompt expands the operator-only skill** (transcript rows: `<command-name>/tamheed:orient-resume</command-name>` then the skill body as a user message); the agent oriented and stopped read-only at step 7, leaving the package open |
| 3 | `--resume` of 2 with words | **a `--resume` is a new client process and a new MCP server**: `package_close` answered `"no package open"`; the lock of the previous process stayed on disk |
| 4 | `--resume` of 2, the prompt = `/tamheed:register-liveness probe` | a slash command works as a resumed turn's prompt; the agent read the dead lock (`package_unlock` without `confirm`: `would_unlock: true`, pid not running), refused to remove it without the operator's word, and asked |
| 5 | **control:** no `--setting-sources` | the documented `--debug` line `Plugin "tamheed" from --plugin-dir overrides installed version` appears; one prefix, 5.8.1; the user's six SessionStart hooks, PreToolUse/PostToolUse/Stop/UserPromptSubmit hooks all ran (ECC, ponytail, remember, instincts); the trace line `version=5.8.1 source=startup` landed in the OPERATOR's file although the harness had unset `TAMHEED_HOOK_LOG` — the operator's `settings.json` `env` sets it, and user settings loaded |
| 6 | `--setting-sources project` with an empty project `settings.json` | no hook row, no trace; one prefix |

**Decisions the probe forced (plan §2 U25/U26, W152–W156, W160):** `--plugin-dir` with
`--setting-sources ""`, no fallback. An operator-only skill is one turn whose whole prompt is the
slash command; the task follows as a `--resume` turn (all sixteen operator-only skills use
`$ARGUMENTS` only as the package name, so no task text can ride on the command). The allow list
carries both `Bash(...)` and `PowerShell(...)` forms. Each turn is a new process: the harness clears
the dead lock in-process before a slash turn (`labrun.py lock --unlock`, the operator's word,
journaled by the engine as `forced-override` by `system:package-unlock`), and a words turn opens
with the standing preamble giving the same word to the agent. The trace variable is set to a
per-run file that the harness creates first (the hook traces only into an existing file — the
first A2 turns ran before that fix and left no trace line; their hook rows are in the transcripts).

**The hook under `--setting-sources ""`:** it runs and its output is delivered. Probe 1 and 6
showed no hook row because their workspaces carried no Tamheed note (a silent hook writes no
transcript row — one case each); in Run A2 and Run B, whose workspaces carry the note, every
process recorded `SessionStart:startup` (and `SessionStart:resume` on each resume) with the
resume block, and the per-run trace files hold 7 (A) and 9 (B) lines, `version=5.8.1`,
`status=printed`, 6–20 lines each. The operator's own trace file stayed at 51 lines across every
run (it gained one line from the control probe, and one from the ECC summariser process of the
R62 compaction earlier in the day).

## 1. Run A — fresh from the seed, the agent driving every phase

### A1 — planning (scenario items 1–5), one process (`22e7376d`, 37 turns, $2.03)

Prompt: `/tamheed:tamheed` + `run-a1.md` (items 1–5 verbatim, the operator's words for the
approvals given in advance, the executor path). Workspace `lab-run-A/plan/` with `brief.md` and
`seed/`; the executor `lab-run-A/exec/` a git repo holding the seed (`51021a7`).

What the agent did (its report, §4, verbatim; the store agrees): `package_create("lab-tracker",
…, "rnd")`; DOC-001..003 with sections; FR-001..FR-005 MVP Approved quoting the brief; FR-006
(recurring) held at Proposed with `[NEEDS-CLARIFICATION: OQ-001]`; OQ-001 owner `operator`, due
2026-11-01; NFR-001/002, CON-001, ASM-001, STK-001/002, DW-001 (the CSV export, not taken on);
DEC-001 (file on disk) stays a decision, DEC-002 promoted to ADR-0001 with the confirmation words
verbatim; RISK-001/002 with discharging tests; PH-001, SL-001, SL-002, AC-001..AC-008 bound to a
requirement and a slice, TEST-001..TEST-007, GATE-001 `ready` and GATE-002 `approval`, CONV-001,
EP-001/002, DEF-001..DEF-003 recorded from READING the seed (the off-by-one, the typo, the flaky
test); a recorded omission for the wbs family. `decisions-look-architectural` first named DEC-001
(SL-001 implemented it): the agent retired that edge (PE-001) and the advisory read clean.
`handoff_emit` twice: the first flagged one line of `prompts/kickoff.md` as a status claim, the
agent reworded it; the note span landed in `exec/CLAUDE.md`. PE-002 the handoff, `package_close`.
Questions it left for the operator: OQ-001..003, ASM-001 — none answered by the harness.

**All 15 A1 predicates pass** (`labrun_check.a1.out.txt`). Owned: the check script crashed twice
with the package open on its first two runs (a wrong `_conn` name, then `gate_run`'s shape), and
its dead-holder unlocks wrote PE-003 and PE-004 into the agent's journal before A2 started; the
first run's `closed-no-lock: PASS "lock present: False"` is the record of A1's own close.

### A2 — execution (items 6–9), one conversation over twelve processes (`19a15cdd`, $12.44)

Setup (`labrun_a2_setup.py`): the plugin's server resolves the package under the project directory,
so the operator moved `lab-tracker/` into the executor repo, re-emitted the note from there, removed
the standalone `.mcp.json`, and committed the handoff (`9429b4f`). Turns (`run-a2.md`; R = a stop
the script had not foreseen, answered with words recorded in the file):

| Turn | Prompt | What happened |
|---|---|---|
| T1 | `/tamheed:orient-resume lab-tracker` | oriented; read PE-003/PE-004 as the operator's unlocks; refused to start SL-001 before GATE-001/002 were decided (they were `human_required`) |
| R1 | the gates' words from the script: "outcome pass" | **the store refused** `CHECK constraint failed: outcome IN ('Go','Hold','Redirect','Kill')` — the operator's script was wrong; the agent did not translate "pass" to Go and asked |
| R2 | "Go for both" | GATE-001/002 → Go; PE-007/PE-008 `gate-decision`, GATE-001's stating that the ready outcome rests on DEF rows from reading the code, not a test run |
| T2 | `/tamheed:slice-kickoff lab-tracker` | a kickoff plan per AC with failing-test-first; three questions: id numbering (max+1 as part of ADR-0001), `done` on a done task (→ OQ-004 with the marker), and no remote to push to — "a sha goes into a row once the commit is on the remote"; the lock observed `reused` (PE-009) |
| T3 | items 6 + the answers | SL-001 coded (TEST-003..005, 14 tests fail then pass); PE-011..015 `work-done`; **SC-001 Proposed** with `scope_adds` DW-001 and `scope_modifies` PH-001, STOP; three engine refusals while writing SC-001 (unknown column `title`; NOT NULL `decision_ref`; NOT NULL `iteration`), each corrected from the error text; **git denied**: the model chained `cd … && git add … && git commit -F … && rm …` (Bash) and `git add …; if ($?) { git commit … }` (PowerShell) — the allow rules cover one plain command |
| R3 | one plain command per call | commits `55c680b` (SL-001), `80d940a` (DEF-001, the seed test `test_due_today_is_not_overdue` run for the first time and failing before the fix), `7dc0831` (DEF-003 quarantined with a reason, TEST-006 in its place); AV-001..AV-007 Met `verified_by agent`, `auto-test`, against the full sha; PE-018/020/022 binds; SL-001 → Review; DEF-001/003 → Fixed; PE-023 handoff |
| T4 | `/tamheed:drift-register lab-tracker` | DEC-003 as the deciding decision, DW-002, LL-001 (two refusals: unknown lesson columns `impacts`/`impact`, and a `learned_from` edge to a row that did not exist yet: "free text is never legal here") |
| T5 | the approval + the waiver words | SC-001 Approved → rows applied (FR-007, AC-009, TEST-008, WBS-001 carrying DW-001; PH-001/SL-002/EP-002 objectives amended; 12 edges) → every target re-read → **Merged**, `scope-changes-merged` clean; the export coded (`a8a68b8`, TEST-008 failed first), AV-008, bound; **WVR-001** on `defects-minor` after four refusals (unknown columns `approved_by`/`subject_id`/`terms`; NOT NULL `rule`, `justification`, `approver`) — then the agent NARROWED it to `applies_to: DEF-002` because the words named only the typo; `defects-minor` reads `waived`; it raised the conflict AC-008 (typo fixed) vs the waiver |
| T6 | `/tamheed:slice-review lab-tracker` | SL-001's five criteria re-verified at HEAD (AV-009..013) from an `entity_export` file; AC-008 recorded **Not-met** by inspection (AV-014); SL-001 NOT moved: `wbs-done` indeterminate (no work-item rows; see §5) — three routes offered |
| T7 | the force words + the answers | **the guard refused** SL-002 (`acs-met: AC-008; wbs-done: WBS-001 — resolve the blockers, or re-run this item with "force": true after EXPLICIT operator confirmation`); a second refusal (`a substitute item carries only … not ['force']`) → the forced move as a full row; **PE-033 `forced-override`** by `system:transition-guard`, PE-034 the operator's words verbatim; WBS-002 for SL-001's verified work bound to `55c680b` on the operator's word; SL-001 readiness `ready: true` → **Implemented without force** (PE-037) |
| T8 | `/tamheed:phase-close lab-tracker` | WBS-001 → Implemented with evidence, DW-001 → Done; PH-001 refused (`acs-met: AC-008`); left open |
| T9 | wrap | PE-043 the phase's state; PE-044 handoff; `export_html` AFTER the handoff ("the page must carry it" — the skill's order over the script's); `package_close`; `f78e256`; `review_current: true` |

**All 14 A2 predicates pass** (`labrun_check.a2.out.txt`): DEF rows honest (medium/low/medium) and
before the fix (by git order: `defects.jsonl` first in `9429b4f`, `tracker.py` first changed in
`55c680b`); 8 typed `work-done`; 14 verdicts `agent`/`auto-test`/real shas; the flaky test file
kept; SL-001 and SL-002 Implemented; SC-001 Merged and the advisory clean; WVR-001 with
`defects-minor` `waived`; the slice's `forced-override`; gate outcomes and two `gate-decision`
events; the page. **Zero permission denials after R3;** three before it.

## 2. Run B — four sessions on a copy of the fixture (W150: the planted question)

Setup (`labrun_b_setup.py`): the fixture copied, the note written, the handoff emitted in-process,
the standalone `.mcp.json` removed, closed. Each session: `/tamheed:orient-resume package`, then
the task by `--resume` (B4: `/tamheed:register-liveness package` between).

| Session | What happened (the agent's reports, §4) |
|---|---|
| B1 (`28afcc6a`, 2 processes) | orient: read PE-061, noted the guide-stock line "carried, not re-measured" and that the server is 5.8.1 while the handoff says 5.8.0; FB-003 `question` Proposed → Confirmed on the word (PE-063): *is a lock left by the server restarting between turns meant to need the operator's unlock every turn, each journaled as a `forced-override`?*; **OQ-002 the planted question**, owner operator, due 2026-11-01, after one refusal (`source_kind IN ('brief','clarification','code','inferred')`); PE-064 handoff LAST; closed |
| B2 (`b8fb8d54`, 2) | PE-066 note: every line of PE-064 re-checked and still held; plain `handoff_emit` (wrote `.mcp.json`; `prompts/README.md` stale stock 5.8.0; warnings FB-002/FB-003 not reported); PE-067 handoff re-measuring the line PE-064 had dropped; noted `go_no_go` says "PH-2 open" while no PH-2 row exists |
| B3 (`ed2f95b2`, 2) | LL-006 "Headless: every turn's lock is a new unlock, on that turn's word" from PE-062/065/068; the approval refused once (`approval/promotion is not an edit — content drifted on [...]; send the stored content byte-identical`), then approved on a fresh read (PE-069 `lesson-confirmed`, the note rebuilt); PE-070 handoff; closed — **no lock left** |
| B4 (`791e2b53`, 3) | T1: opened with NO unlock needed ("closing the package at the end of a turn avoids the leftover lock — one turn's result"); T2 `register-liveness`: **`handoff-repeated` FAILED naming PE-064** (22:29:00Z) — the line "The workspace is not a git repository (git log: fatal, not a git repository), so no commit cross-check ran." had stood word for word through PE-064, PE-067, PE-070; the agent re-measured it (a Glob for `**/.git/HEAD`, Bash denied), rewrote it with what it read and the date in PE-073, and the rule read **pass** at 22:31:01Z; every failing advisory item classified as needing the operator or left open on purpose; T3: advisories quoted, `export_html`, `package_verify` `review_current true`, `review_exported_by "5.8.1"`; PE-074 handoff LAST (so the page no longer carries it — said so); closed |

**The planted question:** carried by id (OQ-002) in all five new handoffs, word for word in the
first three only — B4's two handoffs name it as "the Excel byte-order-mark question". So the
planted line never tripped `handoff-repeated`: each session re-measured and re-dated it as the
skill teaches. The rule fired on a line the agents had NOT re-measured (the git line) — the case
the rule exists for — and cleared once one did. **All 9 B predicates pass** (`labrun_check.b.out.txt`).

**FB-003, the agent's own feedback, answered by the run itself:** B3 closed the package and B4
opened without an unlock; B4-T2 did not close and B4-T3 needed one. A `-p --resume` turn is a new
process; a session that ends with `package_close` leaves nothing to unlock. This goes into the
5.8.1 brief as a sentence and into `orient-resume`'s teaching as a maintainer item (§5).

## 3. The ✔ tables (`labrun_check.py`, by predicate — never by id)

Copied verbatim: `labrun_check.a1.out.txt` (15 PASS; the `closed-no-lock` line reads FAIL on the
re-runs after the script's own crashes — see §1), `labrun_check.a2.out.txt` (14 PASS),
`labrun_check.b.out.txt` (9 PASS).

## 4. The census (`labrun_census.out.txt`)

One block per session: the build, the model, the slash commands typed, the calls by tool, the
denials of every turn, the hook rows, every engine refusal verbatim (`"ok": false`), and the
agent's final report verbatim. Totals: A2 alone made 65 Bash calls, 49 `entity_query`, 35
`entity_upsert`, 17 `progress_update`, 13 `gate_run`, 12 `package_open`, 11 Skill loads
(`package-writes`, `session-handoff`, `reading-the-record`, `test-evidence` — the model-invocable
skills, loaded by the agent itself), 9 `readiness_check`. Engine refusals across the runs: 17 (15 `entity_upsert`, 2 `entity_query`),
every one a constraint or a guard, every one answered by the agent re-reading and re-sending
(none by dropping the write). A `"ok": false` never came from a bug: unknown columns (a title on a
scope change, `impacts` on a lesson, `terms` on a waiver, `status` on a query), NOT NULL columns,
a CHECK on a gate outcome and on `source_kind`, a foreign key to a row not yet written, the
approval-is-not-an-edit rule, the substitute-vs-force rule, the two readiness guards.

## 5. Triage (W143) — for the maintainer, nothing changed in this cycle

| # | Finding | Class | What follows |
|---|---|---|---|
| 1 | A slice with every criterion Met and a **recorded omission of the wbs family** still reads `wbs-done: indeterminate`, so it cannot reach Implemented without a work-item row, a waiver or force. The deferred-work rules read an omission as a deliberate zero (v5.0.0); the scoped `wbs-done`/`acs-met` rules (`empty_note`) do not read the omissions table. The agent's route — one honest work-item row on the operator's word — was right, and the plan 049 doctrine says a rule with no candidate rows measured nothing | engine or teaching — **put to the operator** | a ruling: honour the omission in the scoped rules (engine, a test first), or teach that a slice needs at least one work item (skill sentence) |
| 2 | `orient-resume` step 1 says "after a compaction the package is still open (the MCP process and the lock survive)". True for a compaction; a `-p --resume` (and any new client process) restarts the server: the package is closed and the lock names a dead process. The lab agents met this on every turn and handled it (observe → refuse → the word → unlock, journaled), but the sentence does not name the case | teaching | one clause in step 1 (plan 174's brief names it for ACMP; the skill edit is the operator's call) |
| 3 | The operator's script said a gate outcome is "pass"; the store's values are Go/Hold/Redirect/Kill | harness (the maintainer's words) | `run-words.md` corrected in place |
| 4 | Chained shell commands are denied under `dontAsk` with prefix rules; the model chains by default | harness | the words say one plain command per call |
| 5 | The client's `server/discover` probe makes the Python MCP SDK print 31 validation errors to the server's stderr on first connection (2.1.286); harmless, once per server | vendor / SDK, informational | one sentence in the 5.8.1 brief (ACMP is on 2.1.286) |

Not a finding: the agents' `Skill` loads of the model-invocable skills, the export after the
handoff (the skill's order), the narrowed waiver, the untranslated "pass", the refusal to bind an
unpushed sha until told the lab has no remote — each is the teaching working.

## 6. The windows, the trace count, the resumes and their words

- Windows (UTC, 2026-09-30): probe 21:42:45–21:56; A1 21:59:35–22:03:54; A2 22:07–22:40; B
  22:19–22:31. No run crossed midnight UTC.
- The operator's trace file: 50 before the probe, 51 after the control probe (its line), 51
  after every run. Per-run trace files: A 7 lines (from R3 on), B 9 lines, all `version=5.8.1`.
- Resumes beyond the script: A2 R1, R2, R3 (three; the words in `run-a2.md`, each labelled with
  its cause); T3, T5 and T7 also opened with answers to questions the previous turn had put
  (recorded in the file). Run B: none beyond the scripted turns.
- Harness writes into the agents' packages: A1's PE-003/PE-004 (the check script's unlocks),
  every `system:package-unlock` row before a slash turn, the operator's move of the package into
  the executor repo (`9429b4f`). Nothing else was written by anything but the agents.
- `git status` in this repository after every run: only the harness files and this report.
