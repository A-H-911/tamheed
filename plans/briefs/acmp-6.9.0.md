# Brief to ACMP: tamheed 6.9.0 (no migration, four rows answered, a way back)

> **How to use this file.** The ACMP prompt is one line. It names this file at one commit of
> `A-H-911/tamheed`, its sha256, and the commands that read and check it. Run them in Git Bash:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/acmp-6.9.0.md?ref=<commit>" | sha256sum`.
> PowerShell's `>` changes the bytes, so do not save the file through it. If the sum differs
> from the prompt's, STOP. Then execute the brief. Write no report unless a class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-27, on a scratch copy of your
> commit `812c01c9` (`git archive`, so your repository was only read). The measurements are file
> names, counts and the plugin's own answers. No text of your rows is quoted.
>
> **This brief prescribes writes to your record:** one commit of the stock guide and the review
> page, and one commit of four feedback rows. Each commit is the operator's word.

## 1. What 6.9.0 is

A minor release. It answers your four rows, FB-034 to FB-037, and seven rows of the other field
(Jisr). Jisr's ids overlap yours. Leave its rows out of your record.

- **Your FB-034: `create: true`.** An `entity_upsert` item that carries `"create": true` is
  refused when its id exists. The refusal names that row, and the next free id of a family whose
  ids are plain numbers. Every ok item now says `write`: `inserted`, `updated`, `unchanged` or
  `retired`. **The flag is opt-in.** A write without it still updates a row that has the same id,
  as before. The tool's description, the note's table of obligations and the skills teach it.
- **Your FB-035: the refusals name the columns.** `entity_query` (and `entity_export` through
  it), `expect_unchanged` and `substitute` now name the columns that the call takes. Ruling R147
  supersedes R52.
- **Your FB-036: the third path of this brief.** Section 2.1 and 2.2 now say what to do when the
  operator updated the plugin before the prompt. PRE then comes from git and the plugin record.
- **Your FB-037: `sha256: true`.** An item with `"sha256": true` returns the sha256 of each TEXT
  column that it wrote, read back from the store. Compare it with your source file's sha256, and
  read nothing from the store. It works on an insert. `package-writes` section 2 names this route
  and the limits of each check.
- **Also new:** `merge_attributes` sets or removes keys of one row's `custom_attributes`. A
  family can declare fields of its rows' `custom_attributes`, on the operator's word (ADR-0007).

There is no migration of your store. No table or column changed, and the schema stays at `12`.
Measured on `812c01c9` under 6.9.0, the open moves no file. Every gate and readiness rule reads as
under 6.8.0: `ready true`, with no blocking rule failing.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed-package` prints nothing. If it prints a line, STOP: commit or
   discard that work first.
2. Record the commit to go back to. It is called PRE below. Write it into
   `../tamheed-690-pre.txt`, outside the repository, because the restart in 2.2 ends this session.
   - **A re-entry after the restart:** the file exists. Read PRE and the reading of step 3 from it,
     and write nothing.
   - **A first entry, with the old plugin:** `server_info` reads `6.8.0` or older. Write
     `git rev-parse HEAD` into the file.
   - **The operator updated first:** the file does not exist, and `server_info` already reads
     `6.9.0`. PRE is the newest commit before the update. Read `lastUpdated` of this repository's
     `tamheed@tamheed` record in `claude plugin list --json`. Then run
     `git log -1 --before=<lastUpdated> --format=%H`. Write that sha into the file, with the line
     `updated first`. Ask the operator to confirm it.
3. On a first entry with the old plugin, take the reading under that plugin, and add it to the
   same file. Call `server_info` (`version`) and `package_open("tamheed-package")`. Call
   `gate_run()` (`ready`) and `readiness_check("package")` (`ready` and the blocking rules that
   fail). Then call `package_close()`. When the operator updated first, no old reading exists:
   2.3 compares with this brief's values and with your latest handoff's verified facts.
4. **Untracked files.** `git status --short --untracked-files=all -- tamheed-package` lists the
   files that git does not track. On a first entry, write the list into the same file. Ask the
   operator which of them to keep. They copy those outside the repository before any
   `git clean` of section 4, because `git clean` removes such files for good.
5. No file `tamheed-package/data/.lock` exists. Ask the operator to quit every other client that
   has this repository open: the agent cannot see them.
6. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at
   scope `project`. If it also shows a record at scope `user`, STOP and ask the operator.
7. `.claude/settings.json` holds no `ref` under `extraKnownMarketplaces.tamheed.source`. If it
   holds one, the repository is pinned, and the update commands keep the old release. Ask the
   operator. On their word, run `claude plugin marketplace add A-H-911/tamheed --scope project`
   first.

### 2.2 The plugin, and the restart

Run `server_info` first.

- **If it reads `6.9.0`, skip to 2.3.** PRE is in the file of 2.1, by one of its three paths.
- **If it reads `6.8.0` or older,** run the two commands below. Then ask the operator to quit the
  client, start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

In the new session, `server_info` reads `6.9.0`, `012_standup_withdraw.sql`, schema `12`.

### 2.3 The reading after the plugin, BEFORE any write

`package_open("tamheed-package")`. Then `git status --short -- tamheed-package` prints nothing:
the open moved no file. Then read:

| Probe | Expected |
|---|---|
| `gate_run` `ready` | equal to the reading of 2.1 (on `812c01c9`: `true`) |
| `readiness_check("package")` `ready` and the blocking rules that fail | equal to the reading of 2.1 (on `812c01c9`: `true`, none) |
| `package_verify` | `verified true`, `dirty []` |

When the operator updated first, compare with the values in brackets and with the facts that
your latest handoff marks as verified. If any probe differs, STOP and file a feedback row.
Nothing has been written yet.

### 2.4 The stock guide and the review page

`handoff_emit("<repository root>", refresh_stock=true)`. On `812c01c9` it refreshed
`tamheed-package/README.md` (the stock guide, now of 6.9.0) and moved `tamheed-package/CLAUDE.md`.
The note's table of obligations gains one row, on `create: true`. It reported no restated line.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.9.0"`. `package_close()`. On `812c01c9` the files that moved were the two above,
`tamheed-package/review.html` and `tamheed-package/csv/progress_entries.csv`. The CSV moved under
6.8.0 too: it is behind your journal, and the export writes it again. On the operator's word,
commit them as one commit, for example `tamheed: the 6.9.0 stock guide and review page`. Push
and bind by your own rules.

### 2.5 The four feedback rows

FB-034, FB-035, FB-036 and FB-037 are `Confirmed`, and 6.9.0 answers all four. Ask the operator.
On their word, set each to `Resolved` with a PARTIAL row: `id`, `kind`, `title`,
`lifecycle_status`, `resolved_in` `"6.9.0"` and `upstream_ref`
`"https://github.com/A-H-911/tamheed/blob/v6.9.0/plans/256-field-round-6.9.0.md"`. A move inside
Confirmed, Reported and Resolved is bookkeeping: it needs no `operator_confirm`. Then
`export_html()` again, so the review page shows the rows, and `package_close()`. Commit the
rows and the page on the operator's word. End the session with a `handoff` entry
(`tamheed:session-handoff`): it records the upgrade and the rows.

## 3. What is new for the operator

- **A new row carries `create: true`.** Your own rule for new rows can say so. Offer the operator
  one line for your rules: a new row is sent with `create: true`, and a long write asks for
  `sha256: true`. The line is theirs to approve, and the brief does not write it.
- **A count that ACMP filed.** The upgrade briefs of 6.6.0 to 6.8.0 hold the sentence of FB-036 in
  four files, not six. The two 6.6.0 briefs said "PRE and the list". The briefs are dated
  records, so they keep their text. This brief carries the third path.

## 4. The way back

Measured on 2026-11-27 with the real 6.8.0, on a package that 6.9.0 had written. The store opens
and verifies clean, and a 6.8.0 write keeps it clean. 6.8.0 ignores a family's declaration, so it
writes a value that the declaration refuses. 6.8.0 refuses a slate spec or record that holds
`show_recommendations` or a text over 8000 characters. ACMP's store holds no slate.

### Route A: the data

The upgrade changed only the guide, the package note, the review page and the CSV. Close the
package first. Then go back in one step:

```text
git restore --source=PRE --staged --worktree -- tamheed-package
git commit -m "tamheed: back to the package as it was before 6.9.0"
```

Or `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the package alone.
Then `git clean -nd -- tamheed-package` lists the files that git does not track and removes
nothing. **`git clean -fd` removes a file for good.** Copy each file that the operator keeps
outside the folder first. Do NOT use `git checkout PRE -- tamheed-package` after a commit: it
leaves new files in place.

### Route B: the plugin

```text
claude plugin marketplace add A-H-911/tamheed#v6.8.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then quit the client and start it again. `server_info` reads `6.8.0`.

- The first command writes `"ref": "v6.8.0"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace record
  named `tamheed`. Run no `plugin update` in another repository while the pin stands, unless that
  repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`. It
  removes the pin. Then run the two update commands.

## 5. The classes: hold, or a feedback row

| # | Class | Holds when |
|---|---|---|
| 1 | The plugin | `server_info` reads `6.9.0`, `012_standup_withdraw.sql`, schema `12` |
| 2 | The open | it moves no file |
| 3 | The gates | the reading of 2.3 equals the reading of 2.1, or the values in brackets |
| 4 | The guide | `review_exported_by "6.9.0"` and `review_current true` |
| 5 | The rows | FB-034 to FB-037 read `Resolved`, `resolved_in "6.9.0"` |

## 6. Not built, and said plainly

- `create: true` is opt-in. A write without it still updates a row that has the same id.
- A hash of a rolled-back batch describes nothing that was kept. Read `sha256` only when the
  whole batch is ok.
- A headless run cannot answer whether another client has the repository open. The operator
  answers that.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
