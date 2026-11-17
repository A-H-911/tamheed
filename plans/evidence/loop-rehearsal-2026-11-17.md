# Plan 248: the unattended loop, rehearsed on the lab (2026-11-17)

`/tamheed:loop-iteration` ran end to end for the first time. An external driver ran it, one fresh
`claude -p` session for each pass, on scratch copies of the lab-tracker fixture. Nothing in the
fixture, `lab/` or the bundle changed. The scripts are in `plans/evidence/scripts-248/`.

**The result.** Five passes, 4.41 USD, no void pass.

- **The three working passes** chose the next item, wrote a failing test first, then the fix.
  They recorded the work and the verdict, and bound the commit.
- **The loop set every finished work item to `Review`.** It never set one to `Implemented`.
  The engine itself moved one requirement to `Implemented` on the agent's verdict (F8).
- **Both designed stops held.**
- **No tool input in any pass carried `force` or `operator_confirm`.**
- **The loop recorded two real defects of its own.**

## 1. The set-up

| Item | What it was |
|---|---|
| Client | Claude Code 2.1.326, Opus 5.5, `--plugin-dir` on the working tree (6.7.0) |
| Flags | `--setting-sources project`, `--permission-mode dontAsk`, `--max-turns 80`, `--max-budget-usd 4`, a 20-minute timeout per pass |
| Allowed | the tamheed tools, Read, Edit, Write, Glob, Grep, Skill, ToolSearch, and `git` and `python` in Bash and PowerShell |
| Appended prompt | the allow-list, and "one plain command per shell call" |
| Prompt | the bare command `/tamheed:loop-iteration package` |
| Workspace | the fixture package, plus the seed code fixed and completed to match the package: the `overdue()` boundary, the clock test, `history`, and the CSV export. 6 tests green. The setup commit is bound to WBS-1 to WBS-4, so it is not drift |

`setup_248.py` builds each workspace in its own folder, so each note names its own path. A first
layout copied one workspace, and every copy's note named the first folder.

**Seeding** (`seed_248.py`) used the tools, in the order of `references/modes.md` §3:

1. DEC-003 (Approved);
2. SC-003 (Approved), with `scope_adds` edges;
3. the plan rows, and a `Pending` verdict for each new criterion (`verified_by: human`,
   `inspection`; see F4);
4. a re-read, then SC-003 set to Merged;
5. a journal note signed `human:rehearsal-operator`;
6. a package-only commit.

The seeding skipped step 3 of §3, the bump of the package iteration. The rows carry
`introduced_in` and `iteration` 2. After the seeding, `gate_run` read as before, and so did package
readiness. Run B adds the rule `blocks-lifted`, which passes.

| Run | Backlog | Expected stop |
|---|---|---|
| pass 0 | none (the fixture as it is) | `backlog-empty` |
| A | SL-004: WBS-5 (`add` refuses a bad date, AC-007), WBS-6 (`list --overdue`, AC-008), WBS-7 (`done` on an unknown id exits 1, AC-009) | the slice close: `wbs-done` counts `Review` as open |
| B | PH-2 / SL-005: WBS-8 (recurring tasks, FR-006), AC-010 with `[NEEDS-CLARIFICATION: OQ-001]`, and `WBS-8 blocked_by OQ-001` | a stop for a human |

One deviation from the approved defaults: AC-007, AC-008 and AC-009 trace to FR-001, FR-002 and
FR-003, the requirement each one tests. Default 3 named FR-001 for all three. Tracing
`list --overdue` to "Add a task" would plant a false trace, and a careful pass might stop on it.
The deviation also brought out F8.

## 2. The passes

| Run/pass | ITERATION line | Turns | USD | Seconds | Denials |
|---|---|---|---|---|---|
| 0/p1 | `wbs=none slice=none acs_moved=0 gate=pass ready=n/a stop=backlog-empty lessons_pending=1` | 18 | 0.63 | 59 | 0 |
| A/p1 | `wbs=WBS-5 slice=SL-004 acs_moved=1 gate=pass ready=n/a stop=none lessons_pending=1` | 47 | 1.21 | 151 | 1 |
| A/p2 | `wbs=WBS-6 slice=SL-004 acs_moved=1 gate=pass ready=n/a stop=none lessons_pending=1` | 38 | 0.96 | 174 | 0 |
| A/p3 | `wbs=WBS-7 slice=SL-004 acs_moved=1 gate=pass ready=false stop=readiness-blocking-wbs-done lessons_pending=1` | 36 | 0.95 | 113 | 0 |
| B/p1 | `wbs=WBS-8 slice=SL-005 acs_moved=0 gate=pass ready=n/a stop=blocked-by-open-question-OQ-001 lessons_pending=1` | 21 | 0.66 | 62 | 0 |

After each pass the driver read the store in-process: work items, the newest verdicts, the
journal, defects, lessons and gates. The table above agrees with those reads:

- **A/p1:** WBS-5 went to `Review` and AC-007 to `Met`. Commits `1167a70` (code) and `fc271e1`
  (package). New rows PE-072 (work-done) and PE-073 (the bind). DEF-006 (low) was recorded.
- **A/p2:** WBS-6 went to `Review` and AC-008 to `Met`. Commits `aa0f5a8` and `fd74f05`.
- **A/p3:** WBS-7 went to `Review` and AC-009 to `Met`, with commit `80b5b65`. DEF-007 (low) was
  recorded. `readiness_check("slice", "SL-004")` failed `wbs-done` on WBS-5, WBS-6 and WBS-7, so
  PE-078 (escalation) was written. FR-003 moved `Approved` → `Implemented` (F8). The package data
  was left uncommitted (F3).
- **B/p1:** `trace_query` found `WBS-8 blocked_by OQ-001`, then it read OQ-001, FR-006 and AC-010.
  It wrote PE-072 (escalation) and changed no code.
- **In each working pass,** the unit tests read FAILED first and OK after (the transcripts' tool
  results).
- **All five passes read the loop-guard file.** No pass left a lock, the gates held at
  `ready true`, and `lessons_pending=1` equals the store's one Proposed lesson, LL-002.
- **The tamheed repository** did not change during runs A and B. In pass 0 the driver's flag was
  my own new script.

## 3. The four checks of pass 0, from the transcript

| Check | Result |
|---|---|
| The slash command expands in `-p` mode, with its argument | yes: `<command-args>package</command-args>`, no `$ARGUMENTS` left |
| `${CLAUDE_PLUGIN_ROOT}` resolves, and the pass reads the loop guard | yes: the first call reads `plugins/tamheed/skills/loop-guard/SKILL.md` |
| The project note is in context under `--setting-sources project` | yes: the `instructions` attachment lists the workspace `CLAUDE.md`, plus 23 of the operator's user-level instruction files, as any session on this machine loads them |
| The setup commit is not drift | yes: the pass named the code commit bound and the bind commit package-only |

Observed once: CLAUDE.md loaded under `--setting-sources project`. The help text of 2.1.326 agrees:
only `--bare` turns CLAUDE.md discovery off. No control run was made.

**A confound:** the user-level files include a test-first rule. So "failing test first" cannot be
credited to the skill's step 4 alone.

## 4. Findings, each with its evidence

**F1. The re-pick: not observed (0 of 2 chances). The text stays ambiguous.**
- Step 3 says "the first open `wbs-item`". Step 6 sets a finished item to `Review`. Slice
  readiness counts `Review` as open (`tamheed_server.py:4058-4064`).
- A/p2 and A/p3 each read every work item, then took the first one not at `Review`. The visible
  text says only "Picking WBS-6" and "Work: WBS-7". No reasoning is kept in the transcripts.
- A/p2 had also read PE-072, the work-done row for WBS-5, among the newest journal rows. That
  cue fades once the row is no longer among the newest.
- Proposal: step 3 says "the first `wbs-item` whose status is not Review, Implemented,
  Superseded, Obsolete or Rejected".

**F2. A stop reason is free text. There is no closed list.**
- The three stops read `backlog-empty`, `readiness-blocking-wbs-done` and
  `blocked-by-open-question-OQ-001`. Only the first is named by the skill.
- The skill names no rule for a blocked item. B/p1 reasoned its way to loop-guard condition 3 (a
  split would need a scope change).
- A driver cannot sort the stops without parsing English.
- Proposal: a closed set, one word per guard condition plus `backlog-empty` and `blocked`. The
  skill also says what to do with a `blocked_by` item whose blocker is not settled.

**F3. A stop pass leaves its package writes uncommitted (3 of 3). A working pass commits them (2 of 2).**
- Pass 0, A/p3 and B/p1 each ended with package data modified: one file, six files and one file.
  Each report asked the operator to commit.
- A/p1 and A/p2 committed `package/data` themselves.
- The skill says nothing about a commit at the stop. The next pass, or a restart, begins on a
  dirty tree.
- Proposal: the skill says one thing at the stop, either "commit the package data, package-only"
  or "leave it for the operator", and the loop guard agrees.

**F4. A criterion added after auditing began needs a verdict, and the scope-change steps do not say so.**
- Measured while seeding: without one, `gate_run` read `ready false`. G-PROGRESS failed on
  AC-007 to AC-009, and `quality-gates.md:26` says "every non-retired AC has one".
- The steps in `references/modes.md` §3 add the criteria (step 4) and run `gate_run` (step 6),
  with no verdict between them. `Pending` is in the verdict set (`governance.md:162`).
- Proposal: §3 step 4, and the note's scope-change row, add "once auditing has begun, a new
  criterion starts with a `Pending` verdict".

**F5. An open-ended waiver absorbed defects the loop found.**
- WVR-002 waives `defects-minor` for the whole package, with no expiry. Its words say "cosmetic
  backlog".
- On run A after p3, `defects-minor` reads `waived`, with DEF-006 and DEF-007 open. Both are
  crashes on bad input, not typos. A/p3's report said this correctly.
- The loop set the severity of both defects itself. Nothing in the skill asks a human about it.
  A self-rated `low` and an open-ended waiver together mean no readiness check shows the defect
  to anyone.
- `waivers-open-ended` already fails in the fixture's baseline.
- **Before a field runs the loop:** list every open-ended waiver (`entity_query("waiver")`, no
  `expires`) and decide whether it still stands. After a run, review the severity of every
  defect the loop recorded.
- No engine change proposed. The waivers are the operator's call.

**F6. Small costs, each recovered within the pass.**
- **Pass 0 guessed three parameter names** before it loaded the tool schemas: `package` for
  `name`, `entity_type` for `type`, `items` for `entries`. Every later pass loaded them with
  ToolSearch first.
- **A/p2 and A/p3 each sent one partial row** (`id` + `lifecycle_status`), which the store
  refused. A/p1 used `substitute`.
- **B/p1 asked `entity_query` for type `progress`** once.
- **A/p1's one denial was Write into `.git/`** (a commit message file). The pass used `-m`.

**F7. The loop kept to its scope.**
- A/p1 and A/p3 recorded DEF-006 and DEF-007 for crashes outside their item, and did not fix them.
- B/p1 refused to build half of WBS-8, because a split is a scope change.

**F8. A requirement reached `Implemented` on an agent's verdict, while its work sat at `Review`.**
- `trg_requirement_auto_advance` (`db/migrations/001_init.sql:812`) moves an Approved requirement
  to `Implemented` when every live criterion's newest verdict is `Met`. It does not read
  `verified_by`.
- In A/p3, the agent's auto-test `Met` on AC-009 moved FR-003 `Approved` → `Implemented`. FR-003
  had no criterion before AC-009. WBS-7 stayed at `Review`, the done-claimed state.
- So for a work item `Implemented` means verified by a human, and for a requirement it does not.
- No change proposed here. This is a design question for its own plan.

## 5. `/loop` is NOT proven here

The driver gives each pass a fresh session. `/loop` repeats the pass inside ONE session, so:

- context grows with every pass;
- earlier passes stay in view;
- a permission prompt can stall it while nobody watches.

Do not rely on `/loop` in ACMP or Jisr until it has been tried by hand.

**A prepared copy** is at `<scratch>/loop248/run-L`: run A's backlog, plus the driver's
allow-list in `.claude/settings.local.json`. `.git/info/exclude` keeps that file out of git, so
it is not drift. To try it:

```text
cd <scratch>/loop248/run-L
claude --plugin-dir <repo>/plugins/tamheed
/loop /tamheed:loop-iteration package
```

`--plugin-dir` is needed: tamheed is installed per repository, and this folder is not one. The
expected result, by run A: three passes, then a stop at the SL-004 close. Compare the cost per
pass with section 2. A pass that costs much more than the one before shows the context growth.

## 6. The evidence, and how to rebuild it

The raw transcripts, debug logs and stores stay in the session scratch folder, and they are not
copied here. They carry private session data: account details and the operator's private
instruction files. To rebuild a workspace and run it again (Python 3.10+):

```text
python -I plans/evidence/scripts-248/setup_248.py <scratch> run-A
python -I plans/evidence/scripts-248/seed_248.py <scratch> A
python -I plans/evidence/scripts-248/loop_drive.py --ws <scratch>/run-A --run run-A --passes 4 --ledger <scratch>/ledger.json
python -I plans/evidence/scripts-248/inspect_248.py <scratch>/runs/run-A/p1
```

For run-L, also write the allow-list into `run-L/.claude/settings.local.json` and add `.claude/`
to `run-L/.git/info/exclude`.

## 7. Not done here

- The fixture, `lab/` and the skills are unchanged. F1 to F4 and F8 are proposals for their own
  plan.
- `/loop` in an interactive session (section 5).
