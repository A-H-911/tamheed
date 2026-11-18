# Brief to Jisr: tamheed 6.8.0 (your two rows answered, a new report page, a way back)

> **How to use this file.** The Jisr prompt is one line. It names this file at one commit of
> `A-H-911/tamheed`, its sha256, and the commands that read and check it. Run them in a terminal:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/jisr-6.8.0.md?ref=<commit>" | shasum -a 256`.
> Without `gh`: `curl -fsSL https://raw.githubusercontent.com/A-H-911/tamheed/<commit>/plans/briefs/jisr-6.8.0.md | shasum -a 256`.
> If the sum differs from the prompt's, STOP. Then execute the brief. Write no report unless a
> class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-18, on the export that the
> operator made of your commit `63896cf2` (branch `feature/sl-008-workshops`). Your repository
> was only read. Every measurement ran on Windows. Nothing here ran on your Mac.
>
> **This brief prescribes one write to your record:** one commit of the stock guide and the
> review page, on the operator's word. Section 3 offers more writes. Each is optional, and each
> is the operator's word.

## 1. What 6.8.0 is

A minor release. It answers your two rows of 2026-11-18, and it redraws the standup report as a
delivery report.

| Row | What 6.8.0 does |
|---|---|
| FB-023 | The skill `session-handoff` puts the rulings given in a session under "Do not carry". The report page cuts a "Rulings given" sentence from a line under "Awaiting the operator", so older handoffs read right too. |
| FB-024 | Eight texts now name `from_id`, `to_id` and `relation` for a trace-edge write. They say that `trace_query` reads them back as `from` and `to`. The refusal "unknown columns" names the columns that the item takes. |

**The standup report is a delivery report** (ADR-0005). Its page answers four questions, in this
window and overall. What did we do? What are we working on now? What do we expect next? What
were the challenges and decisions? The plan is one tree of phases, slices, tasks and checks. It has
filters, a search, one glossary, and light and dark colours that follow the system. The agent
states the current slice and the next one, and the operator confirms both at record.

**The page runs one script.** The page's content policy names the script by its SHA-256. It loads
nothing, sends nothing and writes no markup. Without it the page shows every row. The
maintainer checked the page in Chrome only, on Windows. Open your first page in Safari too.

**A report row is larger.** It freezes the plan tree and the full registers. Measured on
`63896cf2`, a first report's row is 314 KB under 6.8.0 and 127 KB under 6.7.0. Its page is
566 KB, and 180 KB under 6.7.0.

There is no migration of your store. No table or column changed, and the schema stays at `12`.
Measured on `63896cf2` under 6.8.0, the open moves no file. The gates and the release rules read
as under 6.7.0: `ready false`, with `acs-met`, `adrs-approved` and `risks-discharged` failing.
The restated scan reports 3 lines, as under 6.7.0. Your latest handoff holds one line under
"Awaiting the operator", with a "Rulings given" sentence. 6.8.0 shows the part before it.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed` prints nothing. If it prints a line, STOP: commit or discard
   that work first.
2. Record the commit to go back to. It is called PRE below. If `../tamheed-680-pre.txt` exists,
   this is a re-entry after the restart. Read PRE and the reading of step 3 from it, and do not
   write it again. Otherwise write `git rev-parse HEAD` into that file. It is outside the
   repository, because the restart in 2.2 ends this session.
3. On a first entry, take the reading under the old plugin, and add it to the same file. Call
   `package_open("tamheed")` and `gate_run()` (`ready`). Then call `readiness_check("package")`
   (`ready` and the blocking rules that fail), and `package_close()`.
4. **Untracked files.** `git status --short --untracked-files=all -- tamheed` lists the files that
   git does not track. On a first entry, write the list into the same file. Ask the operator which
   of them to keep. They copy those outside the repository before any `git clean` of section 4,
   because `git clean` removes such files for good.
5. No file `tamheed/data/.lock` exists. Ask the operator to quit every other client that has this
   repository open: the agent cannot see them.
6. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at scope
   `project`. If it also shows a record at scope `user`, STOP and ask the operator.
7. `.claude/settings.json` holds no `ref` under `extraKnownMarketplaces.tamheed.source`. On
   `63896cf2` it holds none. If it holds one, the repository is pinned, and the update commands
   keep the old release. Ask the operator. On their word, run
   `claude plugin marketplace add A-H-911/tamheed --scope project` first.

### 2.2 The plugin, and the restart

Run `server_info` first.

- **If it reads `6.8.0`, skip to 2.3.** PRE and the reading are in the file of 2.1.
- **If it reads `6.7.0`,** run the two commands below. Then ask the operator to quit the client,
  start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

In the new session, `server_info` reads `6.8.0`, `012_standup_withdraw.sql`, schema `12`.

### 2.3 The reading after the plugin, BEFORE any write

`package_open("tamheed")`. Then `git status --short -- tamheed` prints nothing: the open moved
no file. Then read:

| Probe | Expected |
|---|---|
| `gate_run` `ready` | equal to the reading of 2.1 (on `63896cf2`: `false`) |
| `readiness_check("package")` `ready` and the blocking rules that fail | equal to the reading of 2.1 (on `63896cf2`: `false`, with `acs-met`, `adrs-approved`, `risks-discharged`) |
| `package_verify` | `verified true`, `dirty []` |

If any probe differs, STOP and file a feedback row. Nothing has been written yet.

### 2.4 The stock guide and the review page

`handoff_emit("<repository root>", refresh_stock=true)`. On `63896cf2` it refreshed
`tamheed/README.md` (the stock guide, now of 6.8.0) and moved `tamheed/CLAUDE.md`. It reported 3
restated lines, as under 6.7.0.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.8.0"`. `package_close()`. On `63896cf2` the three files that moved were the two above and
`tamheed/review.html`. On the operator's word, commit them as one commit, for example
`tamheed: the 6.8.0 stock guide and review page`. Push by your own rules.

### 2.5 The two feedback rows

FB-023 and FB-024 are `Reported` on `63896cf2`, and 6.8.0 answers both. Ask the operator. On
their word, set each to `Resolved` with a PARTIAL row: `id`, `kind`, `title`,
`lifecycle_status`, `resolved_in` `"6.8.0"` and `upstream_ref`
`"https://github.com/A-H-911/tamheed/blob/v6.8.0/plans/249-field-round-6.8.0.md"`. Commit the
rows on the operator's word.

## 3. An offer to the operator: optional, on their word

### 3.1 A first report under 6.8.0

Your store holds no standup report, because both were withdrawn. So the next
`/tamheed:standup` is a first report, and it asks for the UTC offset. On `63896cf2` the draft
suggested `SL-008` as the current slice and `SL-009` as the next one. The agent states both, and
the operator confirms both at record.

Put the offer to the operator in one interview (`tamheed:operator-interview`). If they accept,
run `/tamheed:standup`. Ask them to read the draft page before the record, in Safari too. If the
page looks wrong in Safari, file a feedback row with what they saw. Commit the report on their
word.

## 4. The way back

Measured on 2026-11-18 with the real 6.7.0, on a copy of `63896cf2` where 6.8.0 had recorded a
report. The store opens and verifies clean, and the gates read as before. `standup_report(action="regenerate")`
redraws the 6.8.0 report in the 6.7.0 look, with no script. The next draft is a daily report on
top of it.

### Route A: the data

Close the package first. Then go back in one step:

```text
git restore --source=PRE --staged --worktree -- tamheed
git commit -m "tamheed: back to the package as it was before 6.8.0"
```

Or `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the package alone. Then
`git clean -nd -- tamheed` lists the files that git does not track and removes nothing.
**`git clean -fd` removes a file for good.** Copy each file that the operator keeps outside the
folder first. Do NOT use `git checkout PRE -- tamheed` after a commit: it leaves new files in place.

### Route B: the plugin

```text
claude plugin marketplace add A-H-911/tamheed#v6.7.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then quit the client and start it again. `server_info` reads `6.7.0`.

- The first command writes `"ref": "v6.7.0"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace record
  named `tamheed`. Run no `plugin update` in another repository while the pin stands, unless that
  repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`. It
  removes the pin. Then run the two update commands.

## 5. The classes: hold, or a feedback row

| # | Class | Holds when |
|---|---|---|
| 1 | The plugin | `server_info` reads `6.8.0`, `012_standup_withdraw.sql`, schema `12` |
| 2 | The open | it moves no file |
| 3 | The gates | the reading of 2.3 equals the reading of 2.1 |
| 4 | The guide | `review_exported_by "6.8.0"` and `review_current true` |
| 5 | The restated scan | `handoff_emit` reports 3 restated lines |
| 6 | The report page (only after 3.1) | the page shows its sections, and its filters and colour switch work, in Chrome and in Safari |

## 6. Not built, and said plainly

- The maintainer never opened the page in Safari. Class 6 is the first test there.
- A report row is about two and a half times as large as under 6.7.0. Each report adds one.
- A correction and a regenerate never refresh a report's lists.
- An older window cannot be counted again: the store keeps current state only.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
