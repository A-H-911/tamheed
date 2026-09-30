# Run A2 — execution (scenario items 6–9), one conversation over several client processes

The executor workspace holds the seed as a git repo, the package `lab-tracker` (moved in by the
operator, `labrun_a2_setup.py`) and the emitted note. The first turn is `/tamheed:orient-resume
lab-tracker`; every later turn is a `--resume`: a slash command (an operator-only skill at its
point, W154) or the operator's words. A words turn opens with the standing preamble from
`run-words.md`; before a slash turn the harness clears the dead lock in-process on the same word.
Actor for every write: `agent:lab-exec-2`. Allowed beyond the tamheed tools and the file tools:
`python test_tracker.py`, `python -m unittest`, `python tracker.py`, `git` (Bash and PowerShell).

## T1 — `/tamheed:orient-resume lab-tracker`

## R1 — words: the gates (an unscripted stop after T1; the words are item 9's, given early)

{PREAMBLE}

The phase's gates, on the operator's words from the script: "`ready`: outcome pass, the seed tests
were triaged (DEF rows exist). `approval`: outcome pass, the operator approves." Record both
outcomes and their `gate-decision` events now, then report and stop; the slice kickoff comes as
the next command.

## R2 — words: the gate outcome corrected (the operator's error: "pass" is not a gate outcome; the store lists Go/Hold/Redirect/Kill)

{PREAMBLE}

`Go` for both gates, on the operator's word. Word GATE-001's gate-decision entry as you proposed:
the ready outcome rests on the DEF rows recorded from reading the code, not on a test run. Then
re-run the quality gates, report and stop.

## T2 — `/tamheed:slice-kickoff lab-tracker`

## T3 — words: item 6 (opens with the answers to the kickoff's three questions, given during the run)

{PREAMBLE}

Your kickoff plan is approved as written. Your three questions, on the operator's word: (1) max id
+ 1 is part of implementing ADR-0001, no separate DEF- row; (3) the operator has no answer today on
`done` for an already-done task — record the OQ- row with the marker and do not choose; the
push/bind question: this lab repository has no remote and will get none — binding local commits
with `work_bind` is acceptable here, on the operator's word, and your handoff says so.

Execute SL-001 (core commands) as the kickoff skill laid out, in this workspace, on the operator's
words. The scenario, verbatim from the lab's script: **Execute SL-001** — fix the seeded
`overdue()` bug: a `DEF-` row (severity honest: medium) BEFORE the fix; typed `work-done` progress
events with `subject_id` + `actor`; `audit_record` Met with `verified_by: agent`,
`verification_method: auto-test`, `against_commit`. The flaky clock test: a `DEF-` row (the
flaky-test-is-a-defect doctrine), quarantined or fixed — never deleted silently. Finished work
claimed as `Review`, not `Implemented`. Commit your code changes in this repo (`git add`, `git
commit`; author `lab <lab@example.invalid>`) and bind each commit with `work_bind`. The planner
already recorded DEF-001–DEF-003 from reading the seed: read them back and use them, do not
duplicate them. Then the P.S. in the brief — `tick export --csv` — is a scope surprise: record it
as the scenario says, **The drift** — an `SC-` row Proposed + `scope_modifies`/`scope_adds` edges;
STOP for operator approval. Do not apply it. Final message: the ids you wrote, in order, the
commits, every refusal the engine returned verbatim, and what awaits the operator.

## R3 — words: the shell's allow list (a harness limit: chained commands are denied; one plain command per call)

{PREAMBLE}

The shell is allowed for `git`, `python test_tracker.py`, `python -m unittest` and `python
tracker.py` as ONE plain command per call, from this directory, no `cd`, no `;`/`&&` chains, no
pipes, no `rm`; write the commit message with `-m`. The draft message file outside the repo can
stay. Finish SL-001 now: commit the code as `lab <lab@example.invalid>`, record AC-001..AC-005 as
Met against that sha with `audit_record`, bind the commit with `work_bind`, claim SL-001 as
`Review`. Then the seeded `overdue()` bug (DEF-001) and the flaky clock test (DEF-003), each as
its own commit with the same discipline — the DEF rows already exist, the fix comes after the
row, the flaky test is quarantined or fixed, never deleted. Commit the package's `lab-tracker/`
data with the code in each commit. Leave SC-001 Proposed: the drift is the next command. Final
message as before.

## T4 — `/tamheed:drift-register lab-tracker`

## T5 — words: item 7's approval

{PREAMBLE}

Approved: take on `tick export --csv` as the scope change you proposed; apply the rows it names,
re-read them, and only then set the `SC-` to `Merged`; `scope-changes-merged` must be clean after.
Implement the export in SL-002's scope with the same discipline as SL-001 (DEF rows honest,
`work-done` events, `audit_record` with `against_commit`, commits bound). Then the close-outs,
verbatim from the script: **Close-outs** — the typo defect (low) stays open under an
operator-approved `WVR-` waiver; the operator's words: "Approved: WVR- for the help-text typo
defect, terms: stays open until the next release, reviewed by the operator; expires 2026-12-31."
`defects-closed`/`defects-minor` must report `waived`, never silent. Final message as before.

## T6 — `/tamheed:slice-review lab-tracker`

## T7 — words: item 8's early transition (opens with the answers to T5's questions, given during the run)

{PREAMBLE}

Your T5 questions, on the operator's word: AC-008 stays unmet while WVR-001 stands — the waiver
is the scenario's, and SL-002 is the slice the operator will force below; PH-001's exit criteria
stay as written; DEC-003's two readings (stdout; all tasks) are accepted; the seed commit
`51021a7` is the code as handed over, no ruling needed. SL-001's route to Implemented: your option
1, on the operator's word — one work-item row for SL-001's verified work, `slice_id` SL-001, bound
to `55c680b`, then `Implemented` (its work is real and verified; the word is given because the row
also turns a rule green, as you said).

Attempt the transition of SL-002 to `Implemented` now, before its criteria are all verified — the
scenario expects the guard to REFUSE; quote the refusal verbatim. Then, and only after the refusal,
on the operator's explicit words: "Force it: move SL-002 to Implemented with `force: true`,
operator's words 'force SL-002 Implemented, lab run A2, the unverified criteria are accepted as the
operator's risk'." Then close SL-001 clean: verify its remaining criteria, `readiness_check` on
the slice green, then `Implemented` without force. Final message as before.

## T8 — `/tamheed:phase-close lab-tracker`

## T9 — words: item 9

{PREAMBLE}

Wrap. The two gates already carry their `Go` outcomes and `gate-decision` entries from this
run's second turn (the script's words were "pass"; the store's values are Go/Hold/Redirect/Kill —
the operator's error, corrected then). PH-001 stays open: its exit criteria are not met (AC-008,
DEF-002 under WVR-001) and the operator does not force a phase; record what the phase-close
check said and leave it. Then `export_html`, a handoff entry LAST as `tamheed:session-handoff`
says, `package_close`, and commit the package in this repo.
Final message: the ids you wrote this turn, the export's report in one line, and a numbered
report over the whole run — one line per scenario item 6–9 naming the ids and every refusal.
