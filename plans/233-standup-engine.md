# Plan 233 -- the standup engine: state, deltas, replay, window, facts (SR10, SR13, SR40, SR44)

> Status: DONE 2026-11-16 on `feat/standup-report`. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

A new pure module `plugins/tamheed/server/standup.py` (the clock is passed in) and the logic
half of `tests/test_standup.py` (a new suite in `check.py` SUITES).

- **State map.** Every entity table except the journal, the verdicts, the reports, the edges
  and the omissions. One value per row: `status|fingerprint`. The status is `lifecycle_status`;
  risks use `risk_state|lifecycle_status`; gates use `outcome`; a table with no status gives an
  empty status. The fingerprint is 12 hex of sha256 over the row's non-null columns without
  `last_referenced`. Each link records each table's column list.
- **diff/apply** are inverses. Moved: the status part differs (a row new to the base comes from
  "none"). Edited: same status, another fingerprint, column list unchanged (a changed list
  pauses edits for that table, with a note). First counted: a table absent from the base.
- **Replay** from the latest checkpoint (the first report and every 30th recorded daily
  report), each link verified against its digest; the first mismatch names the report and
  forces the next draft to be a checkpoint.
- **Window.** Base = the latest recorded daily report, or a start report, or a start date
  snapped in the row's own offset (`strptime`, Python 3.10). `pe_to`/`av_to` by the SQL
  number, so `PE-1x` reads without raising. A journal that runs backwards is refused. Rows
  signed `system:standup-report` are skipped.
- **Facts** per section (the plan's table), ids and titles (at most 100 characters), at most 30
  per list; the first report fills every list from the current state, uncapped. The rule
  colour (red: an open critical/high defect or a failing blocking rule; amber: an open high
  risk or an overdue question; else green).
- **Check:** `python tests/test_standup.py` (diff then apply is the identity over random
  states; a corrupted middle link is named; a column-set change pauses edits; the `PE-1x`
  window; snapping; the first-report rule); `check.py` on 3.13 and 3.10.
  **Expected:** the suite green; the replay time on a scratch ACMP copy recorded (under 1 s).

## As built (2026-11-16)

- `standup.py` (state, fingerprints, diff/apply, chain and replay, the window, offsets, the
  handoff headings, `select_base`, `compute`, `verify`) and `standup_facts.py` (every section's
  lists, the at-a-glance counts, the rule colour, `build`). Both pure: the server passes the
  connection, the clock and the screen.
- **The chain is ordered by `seq`, not by `pe_to`.** Two reports share a window end when nothing
  was journaled between them, which is the usual case for status moves: the first tests hit
  it. Migration 011 (unreleased) gained `seq` (a CHECK ties it to `kind`), and the chain's
  unique index moved to `seq`. A correction keeps the place of the report it corrects.
- **Measured on scratch copies of five ACMP revisions with the real engine:** every link
  verifies; state and replay take about 0.05 s; the first report is 489 KB; daily rows are
  18.2-30.8 KB. The busiest day passed the 25 KB limit, and the operator raised it to 35 KB
  (SR50).
- **The colour rule's blocking input is package scope.** A side review feared the rule would be
  red every day. Measured: on all five revisions the 5 package-scope blocking rules pass
  (`ready: True`). The rules that fail during normal work are phase and slice scope, and the
  colour rule does not read them.
- **Review (a code-review agent):** an override drafted over a broken link diffed against a
  partial state that `verify` refused, so it could never be recorded. Now a draft over a broken
  link stores the full state, and `verify` applies a full delta with no base. The bind list
  read from the journal is coerced. Tests added: an override, a broken-chain override, a
  correction.
- **Tests:** `tests/test_standup.py`, 23 tests; the suite is in `check.py` SUITES and
  `tests/README.md`; guide prose for the suite and `seq`.
