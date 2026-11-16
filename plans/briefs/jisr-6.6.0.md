# Brief to Jisr: tamheed 6.6.0 (the standup report, one guarded sync, a way back)

> **How to use this file.** The Jisr prompt is one line. It names this file at one commit of
> `A-H-911/tamheed` and its sha256. Read the file verbatim:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/jisr-6.6.0.md?ref=<commit>"`.
> Without `gh`, use `curl -fsSL https://raw.githubusercontent.com/A-H-911/tamheed/<commit>/plans/briefs/jisr-6.6.0.md`.
> Check its sha256 against the prompt before you run anything. If they differ, STOP. Then
> execute it. Write no report unless a class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-16, on the export that the
> operator made of your commit `7b1c85c` (branch `feature/sl-008-workshops`). Your repository was
> only read. Every measurement ran on Windows. Nothing here ran on your Mac. The measurements are
> file names, counts and the plugin's own answers. No text of your rows is quoted.
>
> **This brief prescribes writes to your record:** one registry sync and its commits. Each is the
> operator's word. The first standup report is the operator's own step (section 3).

## 1. What 6.6.0 is

A minor release. It adds the standup report: `/tamheed:standup` writes a page for the window
since the last report. The page says what we did, the challenges and decisions, and what we
expect to do next. A team and a manager read it in 5 to 10 minutes.

It also fixes one fault: a journal id such as `PE-1x` made `package_open` raise and leave the
lock behind.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed` prints nothing. If it prints a line, STOP: commit or
   discard that work first.
2. Record the commit to go back to: `git rev-parse HEAD`. It is called PRE below. Write PRE into
   a file outside the repository, such as `../tamheed-660-pre.txt`, because the restart in 2.2
   ends this session.
3. **Untracked files.** `git status --short --untracked-files=all -- tamheed` lists the
   files that git does not track. Write the list into the same file. Ask the operator which of
   them to keep. They copy those to a place outside the repository before a `git clean` of
   section 4, because `git clean` removes such files for good.
4. No file `tamheed/data/.lock` exists. Ask the operator to quit every other client that
   has this repository open: the agent cannot see them.
5. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at
   scope `project`. If it also shows a record at scope `user`, STOP and ask the operator.
6. `.claude/settings.json` holds no `ref` under `extraKnownMarketplaces.tamheed.source`. If it
   holds one, the repository is pinned. Measured: a pinned repository answers "tamheed is
   already at the latest version (6.5.1)" to the update commands. Ask the operator. On their
   word, run `claude plugin marketplace add A-H-911/tamheed --scope project` first.

### 2.2 The plugin, and the restart

Run `server_info` first.

- **If it reads `6.6.0`, skip to 2.3.** PRE and the list are in the file of 2.1.
- **If it reads `6.5.1`,** run the two commands below. Then ask the operator to quit the client,
  start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Measured in a separate configuration folder with Claude Code 2.1.325: the second command
answered "Plugin "tamheed" updated from 6.5.1 to 6.6.0 for scope project". In the new session,
`server_info` reads `6.6.0`, `011_standup_reports.sql`, schema `11`. The start-of-session block
holds no line that starts "BEHIND THIS ENGINE".

### 2.3 The reading before the sync

`package_open("tamheed")`. Record these, because the sync must not move them:

- `gate_run`: `ready`, and the gates that fail.
- `readiness_check("package")`: `ready`, and the blocking rules that fail.
- The journal's last id.

On `7b1c85c`: `ready false`, and three blocking rules failed: `acs-met`, `adrs-approved` and
`risks-discharged`. They failed the same way after the sync, and under 6.5.1. Before the sync,
`standup_report` refuses: "this package's registry does not know the family 'standup-report'
yet. ... Run package_migrate". That refusal writes nothing, and it is the expected answer.
`package_close()`.

### 2.4 The preview, with a STOP

`package_migrate("tamheed")`. It writes nothing. Expected: mode `registry-sync`, it adds
`standup-report`, and no column. If it names anything else, STOP and file a feedback row.

### 2.5 The confirm, on the operator's word

`package_migrate("tamheed", confirm=true)`. Expected: "none (registry-sync is a pure
append)", no backup. It moves `tamheed/data/entity_types.jsonl` and
`tamheed/data/progress_entries.jsonl`, and no other file.

### 2.6 The go or no-go, BEFORE the commit

`package_open("tamheed")` and read:

| Probe | Expected |
|---|---|
| `package_verify` | `verified true`, `dirty []` |
| `gate_run`, `readiness_check("package")` | equal to the reading of 2.3 |
| the journal | one row more than in 2.3: the sync's, with a time in `occurred_at` |

- **Go:** `package_close()`, then commit the two files alone, for example
  `tamheed: registry-sync for 6.6.0`.
- **No-go:** do not commit. Go back by route A, case 1 (section 4).

### 2.7 The stock guide and the review page

`package_open("tamheed")`. Then `handoff_emit("<repository root>", refresh_stock=true)`.
On `7b1c85c` it moved `tamheed/README.md` (the stock guide, now of 6.6.0) and `tamheed/CLAUDE.md`.
It also warns that FB-019 awaits the operator's word. That row is older than this upgrade.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.6.0"`. `package_close()`. Commit what moved as its own commit. Push by your own rules. The agent's part ends here: tell the operator that section 3 is theirs.

## 3. The first standup report (the operator's step)

The operator types `/tamheed:standup` as the whole prompt of a session. The skill loads only
that way. Measured on `7b1c85c`:

- The first report covers the package from its start. The skill asks for the operator's UTC
  offset once, for example `+03:00`. Later reports reuse it.
- The facts call returns about 38 KB. The page is about 161 KB. Its visible words depend on the
  agent's words: 1,924 in the measured run. The tool warns when a page passes 2,000 words. A
  first report is exempt from that budget, so the warning is expected.
- The rule colour read amber: 10 open high risks. The three failing release rules show under
  "Not ready to close yet", and they do not move the colour.
- The narrative check refuses an id that names no row. In a rehearsal it refused two ids that the
  agent had made up, and the agent wrote the sentence again.
- Recording needs the operator's words. They stay in the report's row: the journal note and
  every page leave them out. The row is in `data/`, so a commit puts them in git history.
- The record moved `data/standup_reports.jsonl`, `data/progress_entries.jsonl`,
  `reports/RPT-001.html`, `review.html` and the `csv/` file of each table it wrote. It also
  writes a new `reports/.gitignore`, which keeps `reports/draft.html` out of git. Commit them.

## 4. The way back

Measured on clones of the scratch result, with git itself and with the real 6.5.1 code. After
each git route, `git diff PRE -- tamheed` was empty. 6.5.1 then opened the package and
read the same three blocking rules as before.

### Route A: the data

1. **Before the sync commit:** `git checkout -- tamheed/data`. Two files go back, and
   `git status` is clean.
2. **After the commits, in one step.** Close the package first.

   ```text
   git restore --source=PRE --staged --worktree -- tamheed
   git commit -m "tamheed: back to the package as it was before 6.6.0"
   ```

   Measured with a live draft report: the restore set every tracked file to its PRE form.
3. **Then the files that git does not track.** `git clean -nd -- tamheed` lists them and
   removes nothing. Measured: it listed `tamheed/reports/`, with the draft page in it.
4. **`git clean` removes a file for good.** Git keeps no copy of a file that it never tracked.
   Copy each file of the list that the operator wants to keep (section 2.1) to a place outside
   the folder first. Then `git clean -fd -- tamheed`. Measured: no ignored file stayed.
5. **Or by revert:** `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the
   package alone. Measured: no conflict, and the same end state.

Do NOT use `git checkout PRE -- tamheed` after a commit: it leaves the new files in place.

### The plugin alone, with the data kept

6.5.1 opens a store that 6.6.0 wrote. Measured: 6.5.1 opened it, wrote a journal row, exported
the review page, closed and opened it again. It left `standup_reports.jsonl` and
`csv/standup_reports.csv` as they were. Its `package_verify` names `standup_reports.jsonl` as
dirty, because 6.5.1 does not know that table. That is expected. Back on 6.6.0 again, the next
report started where the last recorded one ended.

**Keep `standup_reports.jsonl`.** Without it, the next report starts over as a first report with
the id `RPT-001`. Its record would write over the committed `reports/RPT-001.html`.

### Route B: the plugin

```text
claude plugin marketplace add A-H-911/tamheed#v6.5.1 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Measured with Claude Code 2.1.325: the last command answered "Plugin "tamheed" updated from
6.6.0 to 6.5.1 for scope project". Then quit the client and start it again. `server_info` reads
`6.5.1`.

- The first command writes `"ref": "v6.5.1"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace record
  named `tamheed`. Run no `plugin update` in another repository while the pin stands, unless that
  repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`. It
  removes the pin. Then run the two update commands.

### What going back loses

Every report recorded after the upgrade, unless you keep the data (the plugin alone).
`git diff --stat PRE -- tamheed` lists the tracked files before you go back.

## 5. The classes: hold, or a feedback row

| # | Class | Holds when |
|---|---|---|
| 1 | The plugin | `server_info` reads `6.6.0`, `011_standup_reports.sql`, schema `11` |
| 2 | The preview | it adds `standup-report` alone, with no column |
| 3 | The confirm | two files move, with no backup |
| 4 | The gates | the reading of 2.6 equals the reading of 2.3 |
| 5 | The guide | `review_exported_by "6.6.0"` and `review_current true` |
| 6 | The first report | it is recorded, and its page holds none of the operator's words |

## 6. Not built, and said plainly

- The report sees new rows, status moves and edits that the store holds. It never sees work that
  nobody recorded. The skill offers `/tamheed:progress-sync` when the store looks behind.
- The release rules (readiness's blocking rules) do not move the colour. They show under "Not
  ready to close yet".
- A headless run cannot answer whether another client has the repository open. The operator
  answers that.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
