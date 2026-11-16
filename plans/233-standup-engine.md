# Plan 233 -- the standup engine: state, deltas, replay, window, facts (SR10, SR13, SR40, SR44)

> Status: PLANNED. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

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
