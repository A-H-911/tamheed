# Brief to Jisr: tamheed 6.7.0 (your six rows answered, no sync, a way back)

> **How to use this file.** The Jisr prompt is one line. It names this file at one commit of
> `A-H-911/tamheed`, its sha256, and the commands that read and check it. Run them in a terminal:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/jisr-6.7.0.md?ref=<commit>" | shasum -a 256`.
> Without `gh`: `curl -fsSL https://raw.githubusercontent.com/A-H-911/tamheed/<commit>/plans/briefs/jisr-6.7.0.md | shasum -a 256`.
> If the sum differs from the prompt's, STOP. Then execute the brief. Write no report unless a
> class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-17, on the export that the
> operator made of your commit `bab63ce1` (branch `feature/sl-008-workshops`). Your repository
> was only read. Every measurement ran on Windows. Nothing here ran on your Mac.
>
> **This brief prescribes one write to your record:** one commit of the stock guide and the
> review page, on the operator's word. Section 3 offers more writes. Each is optional, and each
> is the operator's word.

## 1. What 6.7.0 is

A minor release that answers the six rows of your export (DEC-173), and adds two standup actions.
The maintainer read your DEC-171 to DEC-173 before writing this brief.

| Row | What 6.7.0 does |
|---|---|
| FB-015 | The texts now say: a section that a register entry replaces is retired with no edge. The entry links it by `relates_to` or by a declared reference field. `supersedes` stays within one family. |
| FB-017 | `entity_export(path, tool="slate_read", args={"name": ...})` writes a round's checked transcript to `exports/`. The read-back to the operator stays required. An export never writes inside `slates/`. |
| FB-018 | The browser check reads the page's shape before it changes anything. A page of one round runs the checks it can and prints SKIP for the rest. A refused page keeps its answers. |
| FB-019 | A register field's closed set can hold `true` and `false`, compared by type: `1` is not `true`. |
| FB-020 | The standup list of blocked work reads the blocking row. A blocker lifts when it is settled, such as a met dependency at `Implemented`. The advisory `blocks-lifted` lists work that is free to start. |
| FB-021 | Status claims in prompt rows are scanned in kickoff prompts only. A phase prompt's conditions are no longer flagged. |

The standup tool can also withdraw a report and regenerate a page (section 3).

There is no migration of your store. Migration `012_standup_withdraw.sql` replaces one trigger,
and the store opens as it is. Measured on `bab63ce1` under 6.7.0, the open moves no file. The
gates and the release rules read as under 6.6.0: `ready false`, with `acs-met`, `adrs-approved`
and `risks-discharged` failing, as before. The advisory `blocks-lifted` is new and passes, with no
row. The restated scan of your ten prompt rows falls from 27 lines to 3: 2 id-dense paragraphs,
and 1 labelled snapshot.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed` prints nothing. If it prints a line, STOP: commit or discard
   that work first.
2. Record the commit to go back to. It is called PRE below. If `../tamheed-670-pre.txt` exists,
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
7. `.claude/settings.json` holds no `ref` under `extraKnownMarketplaces.tamheed.source`. If it
   holds one, the repository is pinned, and the update commands keep the old release. Ask the
   operator. On their word, run `claude plugin marketplace add A-H-911/tamheed --scope project`
   first.

### 2.2 The plugin, and the restart

Run `server_info` first.

- **If it reads `6.7.0`, skip to 2.3.** PRE and the reading are in the file of 2.1.
- **If it reads `6.6.0`,** run the two commands below. Then ask the operator to quit the client,
  start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

In the new session, `server_info` reads `6.7.0`, `012_standup_withdraw.sql`, schema `12`.

### 2.3 The reading after the plugin, BEFORE any write

`package_open("tamheed")`. Then `git status --short -- tamheed` prints nothing: the open moved
no file. Then read:

| Probe | Expected |
|---|---|
| `gate_run` `ready` | equal to the reading of 2.1 (on `bab63ce1`: `false`) |
| `readiness_check("package")` `ready` and the blocking rules that fail | equal to the reading of 2.1 (on `bab63ce1`: `false`, with `acs-met`, `adrs-approved`, `risks-discharged`) |
| the rule `blocks-lifted` | new: `pass`, with no row |
| `package_verify` | `verified true`, `dirty []` |

If any probe differs, STOP and file a feedback row. Nothing has been written yet.

### 2.4 The stock guide and the review page

`handoff_emit("<repository root>", refresh_stock=true)`. On `bab63ce1` it refreshed
`tamheed/README.md` (the stock guide, now of 6.7.0) and moved `tamheed/CLAUDE.md`. It reported 3
restated lines, against 27 under 6.6.0.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.7.0"`. `package_close()`. On `bab63ce1` the three files that moved were the two above and
`tamheed/review.html`. On the operator's word, commit them as one commit, for example
`tamheed: the 6.7.0 stock guide and review page`. Push by your own rules.

### 2.5 The six feedback rows

Each of FB-015 and FB-017 to FB-021 is answered by 6.7.0. Ask the operator. On their word, set
each to `Resolved` with a PARTIAL row: `id`, `kind`, `title`, `lifecycle_status`, `resolved_in`
`"6.7.0"` and `upstream_ref`
`"https://github.com/A-H-911/tamheed/blob/v6.7.0/plans/239-field-round-6.7.0.md"`. Commit the
rows on the operator's word.

## 3. Offers to the operator: each optional, each on their word

Put the three offers to the operator in one interview (`tamheed:operator-interview`). Write
nothing that they do not choose. After the offers they accept, call `export_html()`. Then
commit what moved as one commit, on the operator's word. It holds `data/`, `csv/`,
`review.html`, and each page under `reports/` that a withdrawal removed.

### 3.1 The dependencies, and the two edges to DEP-002

From 6.7.0 a met blocker takes `Implemented`, and its `blocked_by` edge stays as history. Your
DEC-172 ruling 3 retired the two edges to DEP-002 and noted on DEP-002 that it is met. Both
rulings stand. The offers:

- **Review every dependency.** All 15 are `Approved` today. A met one at `Approved` keeps its work
  on the blocked list. These are the rows that block work now:

  | Blocker | Status | Blocks |
  |---|---|---|
  | DEP-001 | Approved | FR-004 (Implemented), SL-005 (Implemented) |
  | DEP-003 | Approved | NFR-002 (Approved) |
  | DEP-004 | Approved | DEC-073 (Deferred), FR-009 (Approved), SL-012 (Approved) |
  | DEP-005 | Approved | FR-002 (Implemented), SL-001 (Implemented) |
  | DW-005 | Open | SL-016 (Approved) |
  | OQ-022 | Proposed | DEC-073 (Deferred) |

  The operator moves each met dependency to `Implemented`, with a full row. DEP-002 is met by
  DEC-172.
- **Write the two edges to DEP-002 again, as history.** `SL-008 blocked_by DEP-002` and `FR-007
  blocked_by DEP-002`. With DEP-002 at `Implemented`, they block nothing. The retire rows of
  DEC-172 stay in the journal as history.

### 3.2 A standup report with fresh lists

RPT-002 corrects RPT-001, and it copied RPT-001's frozen lists. It still lists SL-008 as blocked
by DEP-002. A correction keeps the facts. The route to fresh lists, measured on a copy:

```text
standup_report(action="withdraw", report="RPT-002",
               confirm={"operator_confirm": true, "by": "human:<name>", "words": "<what they said>"})
```

It removes RPT-002 together with RPT-001, the report it corrects. No report is then left. The
next `/tamheed:standup` is a first report, computed from today, and it asks for the UTC offset
again. On the copy, that draft listed SL-012 and SL-016 as blocked, and not SL-008. The ids
RPT-001 and RPT-002 are never used again. Git history keeps the removed rows, their words and
their pages: this is no erasure.

### 3.3 A closed set of true and false

DEC-168 left `confirmation_prompt` of REG-001 free, because a set took text only. A set can now
hold `true` and `false`. If the operator wants it, declare `"values": [true, false]` on that field.

## 4. The way back

Measured on 2026-11-16 with the real 6.6.0, on a store that 6.7.0 wrote: it opens, it verifies
clean, and it drafts. Two things differ there:

- **A withdrawn report id comes back.** 6.6.0 takes the highest id left in the table, so its next
  draft takes a withdrawn id again.
- **A register field with a `true`/`false` set** stops every write to that register under 6.6.0.
  Write the set as text first, or drop it, on the operator's word.

### Route A: the data

Close the package first. Then go back in one step:

```text
git restore --source=PRE --staged --worktree -- tamheed
git commit -m "tamheed: back to the package as it was before 6.7.0"
```

Or `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the package alone. Then
`git clean -nd -- tamheed` lists the files that git does not track and removes nothing.
**`git clean -fd` removes a file for good.** Copy each file that the operator keeps outside the
folder first. Do NOT use `git checkout PRE -- tamheed` after a commit: it leaves new files in place.

### Route B: the plugin

```text
claude plugin marketplace add A-H-911/tamheed#v6.6.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

Then quit the client and start it again. `server_info` reads `6.6.0`.

- The first command writes `"ref": "v6.6.0"` into `.claude/settings.json`. That file is
  committed, so the pin is a change that you commit or revert on purpose.
- **The pin reaches every repository on the machine.** One machine keeps ONE marketplace record
  named `tamheed`. Run no `plugin update` in another repository while the pin stands, unless that
  repository is to go back too.
- To follow releases again: `claude plugin marketplace add A-H-911/tamheed --scope project`. It
  removes the pin. Then run the two update commands.

## 5. The classes: hold, or a feedback row

| # | Class | Holds when |
|---|---|---|
| 1 | The plugin | `server_info` reads `6.7.0`, `012_standup_withdraw.sql`, schema `12` |
| 2 | The open | it moves no file |
| 3 | The gates | the reading of 2.3 equals the reading of 2.1, and `blocks-lifted` passes |
| 4 | The guide | `review_exported_by "6.7.0"` and `review_current true` |
| 5 | The restated scan | `handoff_emit` reports 3 restated lines, not 27 |

## 6. Not built, and said plainly

- A withdrawal is not erasure. Git history keeps the rows, their words and the committed pages.
  Real erasure needs a rewrite of the git history.
- A correction and a regenerate never refresh a report's lists.
- An older window cannot be counted again: the store keeps current state only.
- A headless run cannot answer whether another client has the repository open. The operator
  answers that.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
