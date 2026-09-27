# Tamheed v5.4.0 — the findings_35 batch: one field in the trace line, two lessons, the interview's default

Status: **IN PROGRESS** — index section "Field cycle findings_35" in [README.md](README.md).
Execution order: step 0, then 141 → 142 → 143 → 144 → 145.

Read-only evidence this record rests on: ACMP `findings_35.md` (`c814fdd8` → `3071f1f4`), the rows
`LL-112` (Proposed), `DEC-233` (Approved), the journal `PE-1501`..`PE-1511`, all 25 feedback rows, the
field's `hook-trace.md`; the session transcripts under `~/.claude/projects` read by four scripts of
the maintainer's; the Claude Code hooks reference and three GitHub issues, fetched 2026-09-27; the
approved plan (`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`, revision 2
after a devil's-advocate review); the interview rulings R19–R26.

## 0. Measurements

| # | Measurement | Result |
|---|---|---|
| M1 | Plugin reloads against `SessionStart` events, every transcript on the machine since 2026-09-01 | 24 reloads, builds 2.1.261–2.1.283, three sessions of one project. `SessionStart` attachments of ANY hook within 30 s: 0 of 24. Next event: 5-s-later compaction once, a restart once, none at all once, 41 minutes to 23 hours for the other 21 |
| M2 | The same instrument over compactions and clears (the control) | `/compact` 19 of 19. `/clear` 16 of 18; the two misses are three-row transcripts that end at the clear, a file boundary |
| M3 | The "reload delivered the block on 5.1.0" observation | a restart: the reload's rows carry build 2.1.282; the `SessionStart:resume` 36.6 s later is the session's first row on 2.1.283 |
| M4 | A reload and the hook's code | one observation on 2.1.283: the first `SessionStart` after the 5.3.0 reload wrote a trace line, which only 5.3.0 code writes, with no restart between |
| M5 | Step 0: the real `SessionStart` event in a headless run on 2.1.283 | keys `cwd`, `hook_event_name`, `session_id`, `source`, `transcript_path`; `session_id` equals the run's id and the transcript's file name |
| M6 | The installed plugin's hook in that same run | no line in the operator's trace: the plugin is disabled in the user settings here and enabled per project |
| M7 | Headless sessions that received the field's block, 2026-09-26 13:48Z to 2026-09-27 02:36Z | six, each `sdk-cli` in the project's folder |
| M8 | `python check.py` with the trace variable unset (plan 141) | ALL CHECKS PASSED; no line in the operator's trace inside the run's window |

## 1. What the field returned (no defect, no feedback row)

P0, P1, P4–P7, P9 held. P8 held on the block and on its trace line. P2 (a stale lock at a restart)
and P3 (the render hint) were not exercised; nothing was manufactured. The trace line could not be
attributed (`PE-1508`, `LL-112`). Four brief errors, E1–E4. The operator's standing rule on
recommendations (`DEC-233`). A caution: the installed tree is CRLF on Windows.

## 2. Rulings (R19–R26, binding; R7–R18 stand)

| # | Ruling |
|---|---|
| R19 | v5.4.0, MINOR; no migration (`schema_version` 7). |
| R20 | The trace line ends `session=<session_id>`; `-` when absent or malformed. |
| R21 | The hook prints in every session; the docs say a headless session receives the block. |
| R22 | The docs state as measured that a plugin reload does not run `SessionStart`. |
| R23 | Q1 is retired. |
| R24 | The install tree check is a documented recipe. |
| R25 | `operator-interview` recommends by default; a standing instruction on how to ask is a decision row. |
| R26 | Two sentences absorbed: value-equality attribution; every item differing. |

## 3. Execution

| # | Plan | Status |
|---|---|---|
| 141 | [The trace carries the session](141-trace-carries-the-session.md) | DONE `0be3a56` |
| 142 | [Two absorbed lessons and the interview's default](142-two-lessons-and-the-interview-default.md) | DONE `983df9d` |
| 143 | [Docs + diagrams sweep](143-docs-and-diagrams-sweep-findings-35.md) | IN PROGRESS |
| 144 | [The version stamp, then lab beat 26 + evals](144-stamp-then-lab-beat-26.md) | PLANNED |
| 145 | [Tag v5.4.0, the brief file, close-out](145-release-v540.md) | PLANNED |

## 4. The 5.3.0 brief's errors, owned (E1–E4), and the maintainer's own

- **E1** the trim recipe (`substitute`) cannot run on Approved lessons: the immutability trigger
  refuses it. The copy the brief was written against already had the nine lessons Approved, and the
  recipe was never run on it.
- **E2** the brief named no live sentence a trim would falsify.
- **E3** Q1 cannot be measured where the note names the skills.
- **E4** a prediction named a moving row.
- **The maintainer's own, not found by the field:** `install.md` and the 5.3.0 CHANGELOG entry said a
  reload had delivered the block on 5.1.0 (M3); `install.md` told the reader to infer "fired, not
  delivered" from any trace line.

## 5. Execution notes (owned as they land)

1. The interview told the operator "five headless sessions" and "four reloads". The transcripts show
   six and 24. No ruling depended on either count.
2. Revision 1 of the plan rested the reload claim on one session and scheduled the stdin measurement
   after the code. The operator rejected it for a devil's-advocate review; revision 2 measures first.
3. The first patch script of plan 141 was sent through a shell heredoc and failed ("unexpected EOF").
   It was written with the editor and run as a file: the rule `measurement-evidence` §2 already states.
4. The docs sweep first wrote "the next one was a compaction 41 minutes later, or a resume hours
   later" for all 24 reloads. That held for the last ones only; two followed within minutes for their
   own recorded causes. Corrected before the commit.
5. The operator's trace file held five lines before the batch. Two are this machine's own sessions of
   03:22Z: one is attributed by the transcripts to a headless session in this repository's folder;
   the other cannot be attributed by its content. That is the condition R20 removes.
