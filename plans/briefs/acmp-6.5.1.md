# Brief to ACMP: tamheed 6.5.1 (FB-033 answered, the plugin alone, no migration)

> **How to use this file.** The ACMP prompt is one line: *read this brief and execute it. Write
> no report unless a class fails.* Every result below is the maintainer's own measurement of
> 2026-11-15, on a scratch working tree of your commit `08c5d72c` and on a clone at `e1e2d937`.
> The measurements are ids, file names, column names and counts. No text of your rows is quoted.
>
> **This brief prescribes writes to your record.** One feedback row resolved, and one optional
> journal note. Each is the operator's word.

## 1. What 6.5.1 is

A patch on 6.5.0. No file of a package changes form, and no migration runs. It holds five fixes.

| Fix | From |
|---|---|
| The journal row that `package_migrate` writes carries its time | your FB-033 |
| A registry sync writes the journal's file first, so a second run finishes a sync that stopped | a rehearsal of the 6.5.0 brief |
| The session-start line names a package that is behind the engine, and names `package_migrate` | a rehearsal of the 6.5.0 brief |
| The hook's failure line withholds a text that reads like an instruction | the review of this patch |
| `handoff_emit` no longer names a local-tool row as "not yet reported" | a rehearsal of this brief |

**What it does not change.** The fix acts when a migration runs. Your package has already
migrated, so your row PE-2658 keeps its empty time. Section 3 says what you can do about it.

## 2. The upgrade

### 2.1 Before anything: four checks, and a STOP if one fails

1. `git status --short -- tamheed-package` prints nothing. If it prints a line, STOP: commit or
   discard that work first.
2. Record the commit to go back to: `git rev-parse HEAD`. It is called PRE below.
3. No file `tamheed-package/data/.lock` exists. Ask the operator whether another client has
   this repository open: the agent cannot see that.
4. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at
   scope `project`. If it also shows a record at scope `user`, STOP and ask the operator.

### 2.2 The plugin

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then **quit the client and start it again**. `claude plugin list --json` reads `6.5.1` for this
repository. `server_info` in the new process reads `6.5.1`, `010_registers.sql`, schema `10`.

### 2.3 The package opens, and nothing migrates

`package_open("tamheed-package")` opens. Run no confirm of `package_migrate`. Its preview is
a probe, and it writes nothing. Measured on your commit:

| Probe | Result |
|---|---|
| an open and a close with no write | no file moved, and `git status` stayed clean |
| `package_migrate("tamheed-package")`, the preview | refused: "Nothing to migrate (the expected answer on a current store)" |
| the session-start line | no line that starts "BEHIND THIS ENGINE" |
| `gate_run`, `readiness_check("package")` | `ready true` on both, and no blocking rule fails |

6.5.0 and 6.5.1 gave the same gates, rules, counts and edges on that commit. Your counts have
grown since an earlier handoff, so compare with a read of today and not with that handoff.

If the open is refused, or the preview offers a migration, STOP and file a feedback row.

### 2.4 The stock guide and the review page

With the package open, run `handoff_emit("<repository root>", refresh_stock=true)`. On your
commit it moved two files. `tamheed-package/README.md` is the stock guide, now of 6.5.1. One
line of `tamheed-package/CLAUDE.md` changed. It left the root `CLAUDE.md` as it was.

It warns that FB-033 is confirmed and not yet reported. That is expected: the row reached the
maintainer as a file, and section 3.4 resolves it.

Do section 3 next. Then run `export_html()` last, so that the page holds the resolved row.
`package_verify` then reads `review_current true` and `review_exported_by "6.5.1"`. On your
commit the export moved `tamheed-package/review.html`. After the writes of section 3 it also
moves the `csv/` file of each table that those writes changed. Close the package, read
`git status`, and commit what moved. Push and bind by your own rules.

## 3. FB-033

### 3.1 What was fixed, and how it was measured

Your package at `e1e2d937` was migrated twice from the same start: once under 6.5.0, and once
under 6.5.1. The two results differ in one column of one row: `occurred_at` of the migration's
row. Under 6.5.1 it holds the time of the confirm call. Every other byte is the same.

### 3.2 Your seven rows keep their empty time

The engine changes no old row, because it has no record of when those migrations ran. Read at
your commit `08c5d72c`, seven rows have no time, and all seven are by `system:migrate`:

```text
PE-334  PE-363  PE-366  PE-900  PE-1329  PE-1731  PE-2658
```

Your FB-033 and your DEC-526 list six. PE-334 is the seventh.

### 3.3 An optional note, on the operator's word

Git holds the commit that first carried each row. This command gives its sha and its time:

```text
git log --reverse --format="%h %cI" -S"\"id\":\"PE-2658\"" -- tamheed-package/data/progress_entries.jsonl
```

Read the first line. Measured on your repository: for PE-2658 it names `ddaaa692`, the commit
that your PE-2662 already names. Each of the six other ids resolved to one commit the same way.

If the operator wants the times in the journal, write ONE `progress_update` entry of kind
`note`. It names each row, its commit and that commit's time. Three rules for its words:

- Say "committed at". The time is the commit's. The migration ran a little before it.
- The note holds seven shas. Check first that each is on your remote, by your own rule for a
  sha in a row.
- Send an `actor`. The tool stores none when the entry has none.
- Send no `corrects`. A correction folds its target on the review page, and these rows are true.
- No answer is also an answer. The rows stay as they are, and nothing breaks.

### 3.4 The resolve row, on the operator's word

Send a PARTIAL row. It holds `type "feedback"`, `id "FB-033"`, the row's own `kind` and `title`,
`lifecycle_status "Resolved"`, `resolved_in "6.5.1"` and this `upstream_ref`:

```text
https://github.com/A-H-911/tamheed/blob/v6.5.1/plans/230-migration-row-time.md
```

On your commit that write changed three columns. It moved `feedback.jsonl` and
`progress_entries.jsonl`: the journal gained one row by `system:feedback-guard`. The engine
asks for no confirmation on this write. This brief asks for the operator's word all the same.

### 3.5 Where you will see the fix

At your next migration. The row that it appends carries a time. If that time is empty, file a
feedback row.

## 4. Two changes that you will meet later

- **A sync that stops.** The journal's file is written first. If that file cannot be written,
  no file moves and the tool says "UNCHANGED". If a later file cannot be written, the journal
  already holds the sync's row. That row reads ahead of the files until you run the confirm
  again. The second run finishes the sync and adds a second row, with its own time.
- **A package that is behind.** After a release that adds a column, the session-start block
  holds a line that starts "BEHIND THIS ENGINE". It names the file, the column and
  `package_migrate`. It is the expected line before that migration.

## 5. Going back to 6.5.0

The plugin goes back alone. Measured on your package: 6.5.0 opens a store that 6.5.1 migrated
or wrote, it moves no file, and it gives the same gates, rules, counts and edges.

```text
claude plugin marketplace add A-H-911/tamheed#v6.5.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then quit the client and start it again. `server_info` reads `6.5.0`.

- Measured in a separate configuration folder, on Windows, with Claude Code 2.1.325: that ref
  installs 6.5.0. The measurement left 6.4.0, and the last command answered "updated from 6.4.0
  to 6.5.0". Leaving 6.5.1 is measured after the tag exists.
- The first command writes `"ref": "v6.5.0"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace record
  named `tamheed`. Run no `plugin update` in another repository while the pin stands, unless
  that repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`.
  Then run the two update commands.
- The commits of section 2.4 and section 3 can stay. 6.5.0 reads them.

## 6. Not built, and said plainly

- No old row gains a time. Section 3.3 is the only route, and it is yours.
- The engine has no rule that fails on a journal row with an empty time. Such a rule would fail
  on your seven rows for good.
- A sync that stops at a file whose bytes differ only in spelling can still answer "Nothing to
  migrate" on the second run. `package_verify` then names that file as `dirty`, and the next
  write puts it right.
