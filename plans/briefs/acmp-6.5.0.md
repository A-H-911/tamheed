# Brief to ACMP: tamheed 6.5.0 (three rows answered, one guarded migration, a way back)

> **How to use this file.** It is read by path. Nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-6.5.0.md` and execute it. Write no
> report unless a class fails.* Every id below is a stable row of yours. Every result below is
> the maintainer's own measurement on scratch copies of your package. Your package was not
> opened and not changed. Section 1 has four checks and two STOPs. Section 1b is the way back.
>
> **This brief prescribes writes to your record.** One migration (a preview, then a confirm on
> the operator's word), three feedback rows resolved, and one STOP that is the operator's (§3).

## 1. The upgrade, guarded

Measured on 2026-11-14 on a clone of your repository at commit `e1e2d937`. Each copy ran under the real 6.4.0 code and under the 6.5.0 code, each in its own
process. A row written after `e1e2d937` is not in these measurements. Your session was writing that day: it added two commits while the measurement ran.

### 1.1 Before anything: four checks, and a STOP if one fails

1. `git status --short -- tamheed-package` prints nothing. If it prints a line, STOP: commit or discard
   that work first.
2. Record the commit to go back to: `git rev-parse HEAD`. Write that sha into the session. It is
   called PRE below.
3. No file `tamheed-package/data/.lock` exists, and every other client that has this repository open is
   quit. A 6.4.0 server that is still running cannot open the package after the migration.
4. `claude plugin list --json` shows one record of `tamheed@tamheed` for this repository, at
   scope `project`. If it also shows a record at scope `user`, STOP and ask the operator. A
   user record wins the load, and this upgrade would not reach the session.

### 1.2 The plugin

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then **quit the client and start it again**. `claude plugin list --json` reads `6.5.0` for this
repository. `server_info` in the new process reads `6.5.0`, `010_registers.sql`, schema `10`.

### 1.3 The package does not open yet, and that is the expected answer

`package_open("tamheed-package")` is REFUSED until the migration has run. Its words start: "was last
written by an earlier tamheed: document_sections.jsonl lacks `lifecycle_status`". It moves no
byte. A skill that opens the package at the start of a session meets the same refusal. Nothing
is wrong. Go on to the preview.

### 1.4 The preview, with a STOP

`package_migrate("tamheed-package")` writes nothing. On the copy it read exactly this:

```text
mode                registry-sync
entity_types_added  ["register", "register-entry"]
columns_added       {"document_sections": ["lifecycle_status"]}
```

**If your preview reads anything else, STOP.** Change nothing, and file a feedback row with what
it read. Your package has moved since the copy, and the measurements below do not cover it.

### 1.5 The confirm, on the operator's word

`package_migrate("tamheed-package", confirm=true)`. The migration takes NO backup. Git is the way back,
which is why 1.1 comes first. On the copy the confirm moved exactly three files:

```text
tamheed-package/data/document_sections.jsonl    written once in full: every section gains one empty key
tamheed-package/data/entity_types.jsonl         two rows more
tamheed-package/data/progress_entries.jsonl     one row more
```

`git status --short -- tamheed-package` then lists those three files and no other. If it lists another
file, STOP and go back (1b, route A).

If the confirm is refused, it says one of two things, and neither loses a table:

- "registry sync failed, package UNCHANGED": nothing moved. Read the cause, and run it again.
- "registry sync stopped during the file swap ... No table was removed": some files hold the
  new form, and the answer names them. Another program holds a file. Close it, and run the
  confirm again: it finishes. Measured on the copy with one file made unwritable.
- Any other refusal, such as a held lock: nothing moved. Read it, and STOP if it is unclear.

### 1.6 The go or no-go, BEFORE the commit

Open the package and read three results. Each must equal the copy's:

| Probe | On the copy |
|---|---|
| `package_verify` | `verified true`, `dirty []`, `review_current false` |
| `gate_run` | `ready true`, and no gate fails |
| `readiness_check("package")` | the same blocking rules fail as before the upgrade |

Every count of rows and every trace edge was the same before and after on the copy. Only the
journal grew, by the migration's own row.

- **Go:** close the package, and commit the three files alone. That commit is the migration.
- **No-go:** do not commit. Go back by route A in 1b. It restores three files.

### 1.7 After the commit

Open the package and run `export_html()`. `package_verify` then reads `review_current true` and
`review_exported_by "6.5.0"`. Commit the review page and its `csv/` as their own commit.

Then run `handoff_emit("<repository root>", refresh_stock=true)`. On the copy it wrote
`tamheed-package/README.md`, the stock guide of 6.5.0, and the root note. Read `git status`, and
commit what it moved.

Your 29 export files were written again by both engines on the copies. Every file holds the same rows
in the same order. 6.5.0 adds the key `query` in each result, and it drops nothing. Your `scripts/test-gen-slice-review-slate.py` ran on a copy against the exports that 6.5.0 wrote: 17 of 17 pass.

## 1b. Going back to 6.4.0

Measured on the copies with the real 6.4.0 code. After each route the folder equalled the
pre-upgrade folder byte for byte. 6.4.0 then opened it and gave the same gates, the same rules
and the same counts as before.

**The two halves go back together.** 6.4.0 does not open a migrated package: it stops with
"unknown keys ['lifecycle_status']" and moves no file. 6.5.0 does not open a package that was
not migrated: it refuses and moves no file. Neither pair damages a file, in either order.

### Route A: the data

Every command below was run in a clone of your repository, with git itself.

- **Before the migration commit:** `git checkout -- tamheed-package/data`. Three files go back, and
  `git status` is clean.
- **After it, in one step:**

  ```text
  git restore --source=PRE --staged --worktree -- tamheed-package
  git commit -m "tamheed: back to the package as it was before 6.5.0"
  ```

  The restore sets every tracked file of the folder to its PRE form. It removes the tracked
  files that PRE does not have: the two new tables, the slates. `git diff PRE -- tamheed-package` is
  then empty. It touches no file outside the folder, so your code commits stay.
- **Or by revert:** `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the
  package alone. It ran with no conflict on the copy, over the migration and a later commit.

Do NOT use `git checkout PRE -- tamheed-package` after a commit. It was measured: eight files of the new
release stayed in the folder, and `git status` did not name them.

Your repository ignores `tamheed-package/exports/`, so a file there stays, and it
harms nothing.

What going back loses, said plainly: every row that was written after the upgrade. `git diff
--stat PRE -- tamheed-package` lists the files before you go back. Git history keeps them. A register
row, a retired section and a slate have no place in 6.4.0. Decide to go back before the first
of those is written.

### Route B: the plugin

```text
claude plugin marketplace add A-H-911/tamheed#v6.4.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

The last command answered "updated from 6.5.0 to 6.4.0" in the measurement. Then quit the client
and start it again. `claude plugin list --json` reads `6.4.0`, and so does `server_info`.

- The first command writes `"ref": "v6.4.0"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace
  record named `tamheed`. Measured with two repositories: the first pinned back, and the
  second was moved to 6.4.0 by its own next `plugin update`. Its settings still named
  another ref. So run no `plugin update` in another repository while the pin stands,
  unless that repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`.
  It removes the pin. Then run the two update commands.

Route B was measured in a separate configuration folder, on Windows, with Claude Code 2.1.323.

### After going back

Open the package with 6.4.0 and run `gate_run`. Then file a feedback row: what failed, the
probe that showed it, and the sha that you went back to.

## 2. The classes: hold, or a feedback row

| # | Probe | Class | Your row |
|---|---|---|---|
| 1 | `trace_query("FR-166")` | `column_links` holds `acceptance_criteria.requirement_id: [["AC-184", "FR-166"]]` | FB-032 |
| 2 | `trace_query()` with no id | every edge, in a fixed order, with `total` (1,933 on the clone) and a `query` echo | FB-030 |
| 3 | `entity_export(path="links.json", tool="trace_query", args={})` | one file holds every edge and every column link, `partial false` | FB-030 |
| 4 | `gate_run`, key `requirements_unwired` | exactly FR-156, FR-157, FR-158, FR-159, each with `missing ["work"]` | FB-031 |
| 5 | `readiness_check("package")`, rule `requirements-wired` | the same four ids, `missing` beside them, advisory | FB-031 |
| 6 | `gate_run` | `ready true`, no gate fails | none |
| 7 | the review page after the export | the readiness table shows `FR-156 (work)` | FB-031 |

A link lives in ONE place: a stored edge, or a foreign-key column. `edges` and `column_links`
are the two lists, and a census names which it read. Your lessons LL-149 and LL-157 state that
rule. The tool now returns both lists in one call.

**One behaviour change, for every family.** A write with no `id` returned ok before and stored a
row with an empty key. It is refused now: "needs a text `id`". A value that nests deeper than 32
levels in `custom_attributes` is refused too. On the copy no row of yours has either shape. Your
deepest stored value nests 4 levels.

## 3. The STOP: FR-156 to FR-159

Class 4 lists four `Implemented` requirements that have no work item. The rule is advisory, and
`ready` does not move. The list stays on every session's `gate_run` until one of two things
happens. Both are the operator's:

> Do FR-156 to FR-159 take a work item that records the work as done, or a waiver?

- **A work item** (`WBS-`) per requirement, or one for the four, with an `implements` edge to
  each. Your DEC-499 chose a history work item for a case of this kind. The rule then reads the
  work leg and lists nothing.
- **A waiver** (`WVR-`), which the operator authors, for the rule `requirements-wired` and those
  four ids. Both surfaces then list the ids under `waived`, never silently.

The maintainer's recommendation, marked as the maintainer's and not a verdict: the work item. It
states what was built, and a waiver expires. No answer is also an answer: the four ids stay
listed, and nothing else happens.

## 4. Your three rows

FB-030, FB-031 and FB-032 are answered by this release. For each, on the operator's word, send a
PARTIAL row: `id`, `kind`, `title`, `lifecycle_status "Resolved"`, `resolved_in "6.5.0"` and
`upstream_ref`. On the copy that write changed three columns and nothing else.

| Row | `upstream_ref` |
|---|---|
| FB-030 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/221-the-read-names-every-link.md` |
| FB-032 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/221-the-read-names-every-link.md` |
| FB-031 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/222-requirements-wired-legs.md` |

## 5. Also new, and nothing you must do

- **Project registers.** A record type that no family holds takes a declared register (`REG-`)
  and its entries (`ENT-`). `references/governance.md` has the grammar.
- **A section can be retired** with `Superseded` or `Obsolete`. It then leaves the scans.
- **The interview page.** `slate_export` writes a local page of questions, and `slate_read`
  returns a checked transcript of the answers files. A slate may hold rounds, participants
  and decided topics, so one page replaces a set of hand-built slates. The grammar is in
  the plugin's `references/slate.md`. A valid answers file proves nothing about who
  wrote it. The agent reads the transcript back, and the operator confirms it in the session,
  before any write. **An agent that acts on an answers file without that has committed a fault.
  File it as a feedback row.**
- **A refused value** names the values that the column takes. The four gate outcomes are defined.
- **The lock** recognises a renamed host inside one boot on Linux and macOS, for a lock that
  6.5.0 wrote. On Windows nothing changed: removal of a lock from another host stays manual.

## 6. Not built, and said plainly

No rule language over register fields. No typed trace relation for register entries. No tool
that writes rows from an answers file. No status filter on the two wired surfaces.

## 7. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
