# Brief to Jisr: tamheed 6.6.0 (the 6.5.1 route, one more family, the standup report)

> **How to use this file.** It is read by path, or its text is carried to the Mac. The Jisr
> prompt is one line: *read this brief and execute it. Write no report unless a class fails.*
> Every result below is the maintainer's own measurement of 2026-11-16, on a scratch copy of the
> folder that the operator exported on 2026-11-12 (the copy that `jisr-6.5.1.md` measured). The
> measurements are ids, file names and counts. No text of your rows is quoted.
>
> **This brief replaces the install step of `jisr-6.5.1.md`.** 6.5.1 was never installed at Jisr.
> Install 6.6.0 instead, and follow `jisr-6.5.1.md` with the changes below. Its STOPs, its go or
> no-go, its feedback rows and its section 1b still hold.

## 1. What changes against `jisr-6.5.1.md`

| Step of `jisr-6.5.1.md` | Under 6.6.0 |
|---|---|
| 1.2 The plugin | `server_info` reads `6.6.0`, `011_standup_reports.sql`, schema `11` |
| 1.3 The package does not open yet | The same refusal: `document_sections.jsonl` lacks `lifecycle_status` |
| 1.4 The preview | Mode `registry-sync`. It adds `register`, `register-entry` and `standup-report`, and the column `lifecycle_status` to `document_sections` |
| 1.5 The confirm | No backup: a pure append, and `document_sections.jsonl` is written once in full. It moved `data/document_sections.jsonl`, `data/entity_types.jsonl` and `data/progress_entries.jsonl` |
| 1.6 The go or no-go | The package opens. `readiness_check("package")` reads `ready false`, with the blocking rules `acs-met`, `adrs-approved` and `risks-discharged`. 6.5.1 reads the same three on the same copy, so the upgrade adds none |
| 1.7 After the commit | `handoff_emit(<repository root>, refresh_stock=true)` moved `CLAUDE.md` and `tamheed/README.md` (the stock guide, now of 6.6.0). Then `export_html()` |

If the preview names anything that the table does not, STOP and file a feedback row.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A
marketplace install does not write it. If it appears, remove it and commit nothing of it.

## 2. The first standup report

After section 4 of `jisr-6.5.1.md`, run `/tamheed:standup` and follow it. Measured on the copy:

- The first report covers the package from its start. The tool asks for the operator's UTC
  offset once (for example `+03:00`). Later reports reuse it.
- The facts call returns about 35 KB. The page is about 145 KB. Its visible words depend on the
  agent's words: 1,870 and 2,058 in two runs. The tool warns when a page passes 2,000 words. The
  first report may run long, by design.
- The rule colour read amber: 10 open high risks and 1 question past its date.
- The three failing release rules show under "Not ready to close yet". They do not move the
  colour, because they fail during normal work.
- The record moved `data/standup_reports.jsonl`, `data/progress_entries.jsonl`,
  `reports/RPT-001.html`, `review.html` and the `csv/` file of each table it wrote. It also writes
  a new `reports/.gitignore`, which keeps the draft page out of git. Commit it.

Recording needs the operator's words. They stay in the report's row, and the journal note and
every page leave them out. The row is in `data/`, so a commit puts them in git history.

## 3. Going back

- **To 6.5.1:** measured on the copy, after the migration and a recorded report. 6.5.1 opens the
  store, reads the same gates and moves no file. Its `package_verify` names
  `standup_reports.jsonl` as dirty, because 6.5.1 does not know that table. Remove that file for a
  clean verify. The commands are those of `jisr-6.5.1.md` section 1b route B, with the ref
  `v6.5.1`.
- **To 6.4.0:** route A of `jisr-6.5.1.md` (the data, from the commit PRE) holds, because it
  restores the files from git. Route B to 6.4.0 was not measured on a store that 6.6.0 wrote.

## 4. If a class fails

File one feedback row for each class that fails, with the step, the expected result above and
what you saw. Then stop.
