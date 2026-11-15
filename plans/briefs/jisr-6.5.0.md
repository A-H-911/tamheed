# Brief to Jisr: tamheed 6.5.0 (nine rows answered, one guarded migration, a way back)

> **Superseded on 2026-11-15 by [jisr-6.5.1.md](jisr-6.5.1.md). Do not execute this file.**
> 6.5.0 was never installed at Jisr, and the plugin's update now installs 6.5.1. This file
> stays as the record of what was measured for 6.5.0.

> **How to use this file.** It is read by path, or its text is carried to the Mac. The Jisr
> prompt is one line: *read this brief and execute it. Write no report unless a class fails.*
> Every result below is the maintainer's own measurement on a scratch copy of the folder that
> the operator exported on 2026-11-12 (branch `feature/sl-007-interview-register`, commit
> `3616ae6`). The measurements are ids, statuses and counts. No text of your rows is quoted here.
> Section 1 has four checks and several STOPs. Section 1b is the way back to 6.4.0.
>
> **This brief prescribes writes to your record.** One migration (a preview, then a confirm on
> the operator's word), nine feedback rows resolved, and three STOPs that are the operator's (§3).

## 1. The upgrade, guarded

Measured on 2026-11-14 on copies of the folder that the operator exported on 2026-11-12 (commit `3616ae6`). Each copy ran under the real 6.4.0 code and under the 6.5.0 code, each in its own
process. A row written after that export is not in these measurements. Every measurement ran on Windows. Nothing here ran on your Mac.

### 1.1 Before anything: four checks, and a STOP if one fails

1. `git status --short -- tamheed` prints nothing. If it prints a line, STOP: commit or discard
   that work first.
2. Record the commit to go back to: `git rev-parse HEAD`. Write that sha into the session. It is
   called PRE below.
3. No file `tamheed/data/.lock` exists, and every other client that has this repository open is
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

`package_open("tamheed")` is REFUSED until the migration has run. It says: "package 'tamheed'
was last written by an earlier tamheed: document_sections.jsonl lacks `lifecycle_status`". It
moves no byte. A skill that opens the package at the start of a session meets the same refusal. Nothing
is wrong. Go on to the preview.

### 1.4 The preview, with a STOP

`package_migrate("tamheed")` writes nothing. Its report held these three keys, with these
values. It also holds `version_from` and a `note`.

```text
mode                registry-sync
entity_types_added  ["register", "register-entry"]
columns_added       {"document_sections": ["lifecycle_status"]}
```

**If one of the three reads otherwise, STOP.** Change nothing, and file a feedback row with
what it read. Your package has moved since the copy, and the measurements below do not cover it.

### 1.5 The confirm, on the operator's word

`package_migrate("tamheed", confirm=true)`. The migration takes NO backup. Git is the way back,
which is why 1.1 comes first. On the copy the confirm moved exactly three files:

```text
tamheed/data/document_sections.jsonl    written once in full: every section gains one empty key
tamheed/data/entity_types.jsonl         two rows more
tamheed/data/progress_entries.jsonl     one row more
```

`git status --short -- tamheed` then lists those three files and no other. If it lists another
file, STOP and go back (1b, route A).

A confirm that succeeds also names `README.md` under `prompt_library.diverged`. That is the
stock guide of 6.4.0, and step 1.7 refreshes it.

If the confirm is refused, it says one of these, and none loses a table:

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
| `gate_run` | the same result as before the upgrade: `G-PROGRESS` fails, and no other gate does |
| `readiness_check("package")` | three blocking rules fail, as before: `acs-met`, `adrs-approved`, `risks-discharged` |

Every count of rows and every trace edge was the same before and after on the copy. Only the
journal grew, by the migration's own row.

- **Go:** close the package, and commit the three files alone, for example with the message
  `tamheed: migrate the package to 6.5.0 (registry-sync)`. That commit is the migration.
- **No-go:** do not commit. Go back by route A in 1b. It restores three files.

### 1.7 After the commit

Open the package and run `export_html()`. `package_verify` then reads `review_current true` and
`review_exported_by "6.5.0"`. Close the package, then commit the review page and its `csv/`
as their own commit.

Then run `handoff_emit("<repository root>", refresh_stock=true)`. On the copy it rewrote
`tamheed/README.md`, the stock guide of 6.5.0, and `tamheed/CLAUDE.md`. Read `git status`, and commit
what it moved.

Your 35 export files were written again by both engines on the copies. This is a measurement, with nothing to run. Every file holds the same rows
in the same order. 6.5.0 adds the key `query` in each result, and `lifecycle_status` on each section row, and it drops nothing. Your `build_review_page.py` ran on a copy against the exports that 6.5.0 wrote. Its page equals the page from the 6.4.0 exports, apart from the store digest. Your two test files pass: 15 tests.

## 1b. Going back to 6.4.0

Measured on the copies with the real 6.4.0 code. After each route the folder equalled the
pre-upgrade folder byte for byte. 6.4.0 then opened it and gave the same gates, the same rules
and the same counts as before.

**The two halves go back together.** 6.4.0 does not open a migrated package: it stops with
"unknown keys ['lifecycle_status']" and moves no file. 6.5.0 does not open a package that was
not migrated: it refuses and moves no file. Neither pair damages a file, in either order.

### Route A: the data

Every command below was run in a scratch repository made from your exported folder, with git itself.

- **Before the migration commit:** `git checkout -- tamheed/data`. Three files go back, and
  `git status` is clean.
- **After it, in one step.** Close the package first.

  ```text
  git restore --source=PRE --staged --worktree -- tamheed
  git commit -m "tamheed: back to the package as it was before 6.5.0"
  ```

  The restore sets every tracked file of the folder to its PRE form, and it removes the
  tracked files that PRE does not have. `git diff PRE -- tamheed` is then empty. It touches
  no file outside the folder, so your code commits stay.
- **Then the files that git does not track.** A new table or a slate that was never
  committed stays after the restore. `git clean -nd -- tamheed` lists such files, and it
  removes nothing. Read the list. Then `git clean -fd -- tamheed` removes them. Measured
  on the copy: the folder then equalled the PRE folder byte for byte.
- **`git clean` removes a file for good.** Git keeps no copy of a file that it never tracked. An
  answers file that someone saved from an interview page is such a file, and so is a
  slate that nobody committed. Copy each file of the list that you want to keep to a
  place outside the folder first, or commit it on a branch. Then run the clean.
- **Or by revert:** `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the
  package alone. It ran with no conflict on the copy, over the migration and a later commit.

Do NOT use `git checkout PRE -- tamheed` after a commit. It was measured: eight files of the new
release stayed in the folder, and `git status` did not name them.

The scratch repository had no ignore rules. A file that your repository ignores stays.

What going back loses, said plainly: every row that was written after the upgrade. `git diff
--stat PRE -- tamheed` lists the tracked files before you go back, and `git status --short`
lists the new ones. Git history keeps the committed ones, and it keeps nothing of a file that was never
committed. A register
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
| 1 | `gate_run` | `G-PROGRESS` fails, and no other gate does | none |
| 2 | `entity_query("open-question", limit=1)` | the result carries `query`, the arguments it answered | FB-009 |
| 3 | an `audit_record` item with a verdict outside the set | ONE refusal names every bad value and the values that the column takes | FB-002 |
| 4 | `references/governance.md`, "Execution gate outcomes" | `Go`, `Hold`, `Redirect` and `Kill` are each defined | FB-003 |
| 5 | at its first real use: a section sent with `lifecycle_status "Obsolete"` | the write lands, and the section leaves `G-COMPLETE` and the id scan | FB-011 |
| 6 | at its first real use: a `register` row, and then an entry of it | each lands, and the entry holds its declared fields | FB-004 to FB-006 |
| 7 | at its first real use: `slate_export` with a slate | a page, a record and two hand-outs under `tamheed/slates/`, one script in the page | FB-007 |
| 8 | when it happens: the lock, after a host rename inside one boot | `package_open` reads the holder as observed, not as another host | FB-001 |

**Run probes 1 to 4 now. Write no probe row for classes 5 to 8.** A throwaway section, a
throwaway register and a throwaway slate would stay in your record. Each of those classes was
measured on the copy. Read each one at the first real use, and file a row if it fails.

**Class 8 has limits, stated plainly.** It holds for a lock that 6.5.0 wrote, inside one boot,
on macOS and Linux. It does not hold after a restart, and it does not hold for a lock held on
another machine: that removal stays manual. A machine restored from a memory snapshot keeps its
boot session, so two such clones read as one boot. The calls behind it ran on your Mac in the
operator's probe of 2026-11-12, and on the macOS CI legs.

**One behaviour change, for every family.** A write with no `id` returned ok before and stored a
row with an empty key. It is refused now: "needs a text `id`". A `custom_attributes` value that
nests deeper than 32 levels is refused too. On the copy no row of yours has either shape. Your
deepest stored value nests 8 levels.

## 3. The STOPs

### 3.1 Your three registers (FB-004, FB-005, FB-006)

The upgrade moves no row. Your interview topics, your question bank and your evidence findings
stay where they are: open-question rows and sections with their fields in `custom_attributes`.
Moving them into the register family is your scope change, and the operator's call.

Measured on the copy, over your 620 rows of those three kinds:

| Declaration | Topics (292) | Bank (292) | Findings (36) |
|---|---|---|---|
| Strict: every id-bearing field declared a reference | 280 refused | 264 refused | 36 refused |
| Fitted: a field of joined ids declared as plain text | 0 refused | 0 refused | 0 refused |

Every strict refusal had one cause: a reference names no row. A reference is one id or a LIST of
ids. Five of your fields keep ids joined in one text, and two point at a topic number, not at a
row id. A joined text is never split, because it cannot be told from prose that names an id.

> Do the three registers move into the register family now, later, or not at all?

The maintainer's recommendation, marked as the maintainer's and not a verdict. Move them, with a
fitted declaration and no value change: all 620 rows were admitted that way on the copy, in
batches. Record the move as a scope change first. Then turn one field at a time into a
reference, after a script has converted its joined ids to lists. The rule
`register-entries-conform` lists what a tighter declaration no longer admits. Retire the old
rows with their status: a section takes `Superseded` now, with a `supersedes` edge. Two of your
bank sections carry a mark of that kind in their attributes today. No answer is also an answer:
the rows stay as they are, and nothing breaks.

### 3.2 Your workshop page (FB-007, and your local page's FB-008 row)

`slate_export` builds a page from a slate, and `slate_read` reads the answers back. The page was
rebuilt after the maintainer read your page's script and opened your page. It carries what your
page does, as general features. The plugin's `references/slate.md` holds the slate's grammar.

Measured on the copy, with your whole bank as ONE slate:

| What | Result |
|---|---|
| Rounds, questions, decided topics | 13, 239 and 51, with no refusal |
| Export time, page size | 0.18 seconds, 3.7 MB |
| The page in Chrome | it loads in 0.4 seconds, and an answer registers in 28 milliseconds |
| Quoted rows, questions with a glossary term | 484, and 185 (all 23 of your terms match somewhere) |
| One round's file, read back | the round reads complete, and its two approval marks are listed |

How your bank's attributes map to a slate. A script of yours does this: it reads rows by key.

| Your attribute | The slate's key |
|---|---|
| `category` | one round each. A category with no asked question is a round with `ready: false` |
| `block` | the question's block |
| `kind` of `decided` | a decided topic of the round, with its ruling as the `answer` |
| `options`, `recommended`, `recommendation_reason`, `recommendation_basis` | `options`, `recommended`, `reason`, `basis` |
| `lead_id`, `consulted_ids` | `lead`, `consulted`. The seven groups attend. The four others carry `attends: false` |
| `operator_approval_required`, or the operator as lead | `owner: operator`, and `approval: true` |
| `evidence_ids`, `decided_ids`, `depends_on` | `known`, `decided`, `depends_on` |
| `register_row` | `settles` |

What the new page has, each from your page:

- A list of rounds, and blocks inside a round.
- Attendance for each group, with a named cover.
- An owner mark, a lead and the consulted groups on each card.
- The answers "Unknown" and "Requires evidence", and "answered by".
- The basis of a recommendation.
- Folds for what is known and what is decided, and the terms of a card.
- Decided topics with a reopen box, and points from the room.
- The four closure fields, and a save and a load for each round.
- A mark on an answer that an earlier page made.
- Your two hand-outs: the room's questions with their text, and one line for each question.

What differs from your page, said plainly:

- **No approval tick.** A question carries a mark: needs the operator's approval. `slate_read`
  lists such answers under `approval_needed`, and the operator approves in the session.
- **A room view and a presenter view.** The page opens in the room view: the operator's
  questions, attendance, closure and the recommendations are hidden. The switch is in the More
  menu. It is a way to show the page. It protects nothing: the hidden text is in the file.
- **No gate round of its own.** A round whose questions the operator owns does that work.
- **No tool writes rows from a file.** Your `round_record.py` keeps that work, on the operator's
  word. Its check of a round has a twin: `slate_read` says `complete`, or names what is missing.
- **Stored answers follow the page's address.** A page that is moved to another folder starts
  empty. The saved file is the record.

> Does the next workshop run on the new page, or on your own page?

The maintainer's recommendation: run one round on the new page first, beside your own. Keep your
page and its FB-008 row until that round is read back cleanly. Three checks on your Mac, before a
workshop depends on it:

- Click **Save this round** once and see that `<name>.<round id>.answers.json` arrives. The
  operator saw a file arrive in Chrome on Windows. Your Mac's browser is another build. If no
  file arrives, open `Trouble saving?` at the page's end and copy the text into that file.
- A second save of one round gives a file with ` (1)` in its name. `slate_read` does not open it.
  It names it under `unread_files`. Rename it over the first file.
- Run the browser check from the plugin's repository against a COPY of your exported page:
  `node tests/run_slate_browser_check.mjs <page.html>`. It needs Node 22 and Chrome. On a page
  built from your whole bank on the copy it passes 48 checks of 48. **It clears every answer
  that the page holds**, so never run it on a page that people have answered. CI does not
  run it.

**The rule that has no lock.** A valid answers file proves nothing about who wrote it. The reader
checks that the file fits the questions, and its result says `provenance: unverified`. The agent
reads the transcript back to the operator, and the operator confirms it in the session, before
any write. An approval is never taken from the file. **An agent that acts on an answers file
without that has committed a fault. File it as a feedback row.**

### 3.3 Your gate outcome (FB-003)

A No-go whose blockers are recorded, worked and put again is **`Hold`**. `Redirect` means that the
plan or the scope changes first. `Kill` means that the guarded work stops. The outcome of your
GATE-001 is the operator's to write.

## 4. Your rows

FB-008 and FB-010 register local tools. They never resolve. For the nine others, on the
operator's word, send a PARTIAL row. It holds `type "feedback"`, the row's own `id`, `kind` and `title`,
`lifecycle_status "Resolved"`, `resolved_in "6.5.0"` and `upstream_ref`. On the copy that write changed three columns.

| Rows | `upstream_ref` ends with (after `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/`) |
|---|---|
| FB-001 | `224-lock-boot-session.md` |
| FB-002, FB-003 | `223-a-refused-value-names-its-set.md` |
| FB-009 | `221-the-read-names-every-link.md` |
| FB-011 | `225-section-status.md` |
| FB-004, FB-005, FB-006 | `226-project-registers.md` |
| FB-007 | `227-interview-page.md` |

Resolve FB-004 to FB-007 when their STOP is answered, whichever way: the capability exists.

## 5. Not built, and said plainly

No rule language over register fields: "no result on a row that is not approved" stays an
inspection of yours, over typed data. No typed trace relation for register entries. No tool that
writes rows from an answers file. No unlock for a lock held on another machine.

## 6. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
