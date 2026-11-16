# Brief to ACMP: tamheed 6.7.0 (no sync, two standup actions, a way back)

> **How to use this file.** The ACMP prompt is one line. It names this file at one commit of
> `A-H-911/tamheed`, its sha256, and the commands that read and check it. Run them in Git Bash:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/acmp-6.7.0.md?ref=<commit>" | sha256sum`.
> PowerShell's `>` changes the bytes, so do not save the file through it. If the sum differs
> from the prompt's, STOP. Then execute the brief. Write no report unless a class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-17, on a scratch export of
> your commit `8235a2f9` (`git archive`, so your repository was only read). The measurements are
> file names, counts and the plugin's own answers. No text of your rows is quoted.
>
> **This brief prescribes writes to your record:** one commit of the stock guide and the review
> page. The commit is the operator's word.

## 1. What 6.7.0 is

A minor release. ACMP filed nothing for it. The other field's six rows and two standup actions
that the operator asked for make it up:

- **Withdraw and regenerate a standup report.** `standup_report(action="withdraw")` removes the
  newest daily report or an override report, on the operator's word. `action="regenerate"`
  rebuilds the pages of recorded reports from their rows.
- **The standup list of blocked work reads the blocking row.** A blocker lifts when it is
  settled, such as a met dependency at `Implemented`. A new advisory, `blocks-lifted`, lists
  work that is free to start.
- **The restated scan reads status claims in kickoff prompts only.** A phase prompt's conditions
  are no longer flagged.
- **A register field's closed set can hold `true` and `false`.**
- **`entity_export` can run `slate_read`.** An export never writes inside `slates/`.

There is no migration of your store. Migration `012_standup_withdraw.sql` replaces one trigger,
and the store opens as it is. Measured on `8235a2f9` under 6.7.0, the open moves no file. Every
gate and readiness rule reads as under 6.6.0. The advisory `blocks-lifted` is not emitted,
because ACMP has no `blocked_by` edge.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed-package` prints nothing. If it prints a line, STOP: commit or
   discard that work first.
2. Record the commit to go back to. It is called PRE below. If `../tamheed-670-pre.txt` exists,
   this is a re-entry after the restart. Read PRE and the reading of step 3 from it, and do not
   write it again. Otherwise write `git rev-parse HEAD` into that file. It is outside the
   repository, because the restart in 2.2 ends this session.
3. On a first entry, take the reading under the old plugin, and add it to the same file. Call
   `package_open("tamheed-package")` and `gate_run()` (`ready`). Then call
   `readiness_check("package")` (`ready` and the blocking rules that fail), and `package_close()`.
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

- **If it reads `6.7.0`, skip to 2.3.** PRE and the reading are in the file of 2.1.
- **If it reads `6.6.0`,** run the two commands below. Then ask the operator to quit the client,
  start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

In the new session, `server_info` reads `6.7.0`, `012_standup_withdraw.sql`, schema `12`.

### 2.3 The reading after the plugin, BEFORE any write

`package_open("tamheed-package")`. Then `git status --short -- tamheed-package` prints nothing:
the open moved no file. Then read:

| Probe | Expected |
|---|---|
| `gate_run` `ready` | equal to the reading of 2.1 (on `8235a2f9`: `true`) |
| `readiness_check("package")` `ready` and the blocking rules that fail | equal to the reading of 2.1 (on `8235a2f9`: `true`, none) |
| `package_verify` | `verified true`, `dirty []` |

If any probe differs, STOP and file a feedback row. Nothing has been written yet.

### 2.4 The stock guide and the review page

`handoff_emit("<repository root>", refresh_stock=true)`. On `8235a2f9` it refreshed
`tamheed-package/README.md` (the stock guide, now of 6.7.0) and moved `tamheed-package/CLAUDE.md`.
It reported no restated line.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.7.0"`. `package_close()`. On `8235a2f9` the three files that moved were the two above and
`tamheed-package/review.html`. On the operator's word, commit them as one commit, for example
`tamheed: the 6.7.0 stock guide and review page`. Push and bind by your own rules.

## 3. What is new for the operator

- **Withdraw a standup report.** Only the newest daily report or an override report, and only
  when nothing names it. The operator's words confirm it. The row and its page leave the store.
  The journal keeps a note without the words, and the id is never used again. Git history keeps
  the removed row, so this is no erasure.
- **Regenerate a page.** `standup_report(action="regenerate")` rebuilds recorded pages from
  their rows, with the same facts. It changes no row.
- **Fresh lists** come only from withdrawing the newest daily report and drafting again. A
  correction and a regenerate keep the frozen facts.

The `/tamheed:standup` skill names each step.

## 4. The way back

Measured on 2026-11-16 with the real 6.6.0, on a store that 6.7.0 wrote: it opens, it verifies
clean, and it drafts. Two things differ there:

- **A withdrawn report id comes back.** 6.6.0 takes the highest id left in the table, so its next
  draft takes a withdrawn id again.
- **A register field with a `true`/`false` set** stops every write to that register under 6.6.0.
  Write the set as text first, or drop it, on the operator's word.

### Route A: the data

The upgrade changed only the guide, the package note and the review page. Close the package
first. Then go back in one step:

```text
git restore --source=PRE --staged --worktree -- tamheed-package
git commit -m "tamheed: back to the package as it was before 6.7.0"
```

Or `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the package alone.
Then `git clean -nd -- tamheed-package` lists the files that git does not track and removes
nothing. **`git clean -fd` removes a file for good.** Copy each file that the operator keeps
outside the folder first. Do NOT use `git checkout PRE -- tamheed-package` after a commit: it
leaves new files in place.

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
| 3 | The gates | the reading of 2.3 equals the reading of 2.1 |
| 4 | The guide | `review_exported_by "6.7.0"` and `review_current true` |

## 6. Not built, and said plainly

- A withdrawal is not erasure. Git history keeps the row, its words and the committed pages.
  Real erasure needs a rewrite of the git history.
- A correction and a regenerate never refresh a report's lists.
- A headless run cannot answer whether another client has the repository open. The operator
  answers that.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
