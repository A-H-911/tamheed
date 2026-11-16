# Brief to ACMP: tamheed 6.6.0 (the standup report, one registry sync, a way back)

> **How to use this file.** The ACMP prompt is one line: *read this brief and execute it. Write
> no report unless a class fails.* Every result below is the maintainer's own measurement of
> 2026-11-16, on a scratch export of your commit `208c7f2e`. The measurements are ids, file names
> and counts. No text of your rows is quoted.
>
> **This brief prescribes writes to your record.** One registry sync and one standup report.
> Each is the operator's word.

## 1. What 6.6.0 is

A minor release. It adds the standup report: `/tamheed:standup` writes a page for the window
since the last report. The page says what we did, the challenges and decisions, and what we
expect to do next. A team and a manager read it in 5 to 10 minutes. The release also fixes one
fault: a journal id such as `PE-1x` made `package_open` raise and leave the lock behind.

## 2. The upgrade

### 2.1 Before anything: four checks, and a STOP if one fails

1. `git status --short -- tamheed-package` prints nothing. If it prints a line, STOP: commit or
   discard that work first.
2. Record the commit to go back to: `git rev-parse HEAD`. It is called PRE below.
3. No file `tamheed-package/data/.lock` exists. Ask the operator whether another client has this
   repository open: the agent cannot see that.
4. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at
   scope `project`. If it also shows a record at scope `user`, STOP and ask the operator.

### 2.2 The plugin

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then **quit the client and start it again**. `server_info` in the new process reads `6.6.0`,
`011_standup_reports.sql`, schema `11`.

### 2.3 The registry sync, on the operator's word

The package opens before the sync. Measured on your commit: the open moves no file, and
`gate_run` and `readiness_check("package")` read `ready true` before and after the sync.

1. `package_close()`, then `package_migrate("tamheed-package")`, the preview. It reads mode
   `registry-sync` and adds `standup-report`. No other family and no column.
2. On the operator's word: `package_migrate("tamheed-package", confirm=true)`. It is a pure
   append, with no backup. It moved `data/entity_types.jsonl` and `data/progress_entries.jsonl`.
3. If the preview names anything else, STOP and file a feedback row.

### 2.4 The stock guide and the review page

`package_open("tamheed-package")`, then `handoff_emit("<repository root>", refresh_stock=true)`.
It moved `tamheed-package/README.md` (the stock guide, now of 6.6.0) and
`tamheed-package/CLAUDE.md`. Then `export_html()`. `package_verify` then reads
`review_current true` and `review_exported_by "6.6.0"`. Commit what moved.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A
marketplace install does not write it. If it appears, remove it and commit nothing of it.

## 3. The first standup report

Run `/tamheed:standup` and follow it. Measured on your commit:

- The first report covers the package from its start. The tool asks for the operator's UTC
  offset once (for example `+03:00`). Later reports reuse it.
- The facts call returns 58 KB on `208c7f2e` and 84 KB on a later commit, `d7ce1e04`. The page
  is about 462 KB. Its visible words depend on the agent's words: 2,270 and 2,510 in two runs.
  The tool warns when a page passes 2,000 words. The first report may run long, by design.
- The rule colour read green: no open critical or high defect, no open high risk, no question
  past its date.
- The record moved `data/standup_reports.jsonl`, `data/progress_entries.jsonl`,
  `reports/RPT-001.html`, `review.html` and the `csv/` file of each table it wrote. It also writes
  a new `reports/.gitignore`, which keeps the draft page out of git. Commit it.
- The narrative check refuses an id that names no row. In a rehearsal it refused two ids that the
  agent had made up, and the agent wrote the sentence again.

Three facts for the operator:

- **The words.** Recording needs the operator's words. They stay in the report's row, and the
  journal note and every page leave them out. The row is in `data/`, so a commit puts them in
  git history.
- **The colour.** Red is an open critical or high defect. Amber is an open high risk or a
  question past its date. The release rules show under "Not ready to close yet" and do not move
  the colour.
- **What the report sees.** New rows, status moves and edits that the store holds. It never sees
  work that nobody recorded. Run `/tamheed:progress-sync` first when the store is behind: the
  skill offers it.

## 4. Going back to 6.5.1

The plugin goes back alone. Measured on your commit, after the sync and a recorded report: 6.5.1
opens the store, reads the same gates and moves no file. Its `package_verify` names
`standup_reports.jsonl` as dirty, because 6.5.1 does not know that table. Remove that file for a
clean verify: git keeps it.

```text
claude plugin marketplace add A-H-911/tamheed#v6.5.1 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then quit the client and start it again. `server_info` reads `6.5.1`. The first command writes
the pin into `.claude/settings.json`, and one machine keeps one marketplace record named
`tamheed`. To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope
project`, then the two update commands.

## 5. If a class fails

File one feedback row for each class that fails, with the step, the expected result above and
what you saw. Then stop.
