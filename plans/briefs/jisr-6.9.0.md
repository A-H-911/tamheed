# Brief to Jisr: tamheed 6.9.0 (your seven rows answered, longer slate texts, a way back)

> **How to use this file.** The Jisr prompt is one line. It names this file at one commit of
> `A-H-911/tamheed`, its sha256, and the commands that read and check it. Run them in a terminal:
> `gh api -H "Accept: application/vnd.github.raw" "repos/A-H-911/tamheed/contents/plans/briefs/jisr-6.9.0.md?ref=<commit>" | shasum -a 256`.
> Without `gh`: `curl -fsSL https://raw.githubusercontent.com/A-H-911/tamheed/<commit>/plans/briefs/jisr-6.9.0.md | shasum -a 256`.
> If the sum differs from the prompt's, STOP. Then execute the brief. Write no report unless a
> class fails.
>
> Every result below is the maintainer's own measurement of 2026-11-27, on a scratch copy of your
> commit `f0d6f636` (branch `feature/sl-008-workshops`, read with `gh api` as a tarball). Your
> repository was only read. Every measurement ran on Windows. Nothing here ran on your Mac.
>
> **This brief prescribes writes to your record:** one commit of the stock guide and the review
> page, and one commit of seven feedback rows. Each commit is the operator's word. Section 3
> offers more writes. Each is optional, and each is the operator's word.

## 1. What 6.9.0 is

A minor release. It answers your seven rows, and four rows of the other field (ACMP). ACMP's ids
overlap yours. Leave its rows out of your record.

- **FB-043: a slate text holds 32,000 characters.** The cap of an intro and of a detail (of a
  question and of an option) rose from 8000. `references/slate.md` now lists every cap of the
  slate code, and a lint keeps the list equal to the code.
- **FB-032: an intro keeps its line breaks.** The slate's intro and a round's intro render line
  by line.
- **FB-034: a long word wraps.** A word too long for its line no longer pushes a card past the
  width of a phone. In the measurement, no other element of the page moved at 1280 px.
- **FB-033: `show_recommendations: true`.** A slate with this key opens its page with the
  recommendations shown in every view, at every open. The presenter's button can still hide them
  until the page is closed.
- **FB-025 (a): `merge_attributes`.** `{type, id, merge_attributes: {"layer": "twk-setup",
  "old_key": null}}` sets or removes keys of one row's `custom_attributes`, by RFC 7386. The rest
  of the row never passes through the agent. Every other key stays as it was. Also, the skill's
  sentence that called JSON inside `custom_attributes` a refusal is corrected: a `substitute`
  inside a value works.
- **FB-025 (b): a declared set.** A family can declare fields of its rows' `custom_attributes`,
  on the operator's word (ADR-0007). A write that sets them is then checked against the set.
  `required` is never enforced at write. The advisory `declared-attributes` lists the rows that
  lack a required key or break the set.
- **FB-029 answered: the column records the discharge, and the edge records the plan.** See
  section 3.
- **FB-044 answered: a started slice resumes at its handoff.** See section 3.
- **Also new:** `create: true` refuses a write whose id exists, and every ok item says `write`.
  **The flag is opt-in.** `sha256: true` returns the hash of each TEXT column that an item wrote.

There is no migration of your store. No table or column changed, and the schema stays at `12`.
Measured on `f0d6f636` under 6.9.0, the open moves no file. Every gate and readiness rule reads as
under 6.8.0: `ready false`, with the blocking rules `acs-met`, `adrs-approved` and
`risks-discharged` failing. Your 14 slates that have an answers file read under 6.9.0 as under
6.8.0, with no question put again.

## 2. The upgrade, guarded

### 2.1 Before anything: the checks, and a STOP if one fails

1. `git status --short -- tamheed` prints nothing. If it prints a line, STOP: commit or discard
   that work first.
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
   same file. Call `package_open("tamheed")` and `gate_run()` (`ready`). Then call
   `readiness_check("package")` (`ready` and the blocking rules that fail), and `package_close()`.
   When the operator updated first, no old reading exists: 2.3 compares with this brief's values
   and with your latest handoff's verified facts.
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

- **If it reads `6.9.0`, skip to 2.3.** PRE is in the file of 2.1, by one of its three paths.
- **If it reads `6.8.0` or older,** run the two commands below. Then ask the operator to quit the
  client, start it again in this repository, and give the same one-line prompt. Then stop.

```text
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

In the new session, `server_info` reads `6.9.0`, `012_standup_withdraw.sql`, schema `12`.

### 2.3 The reading after the plugin, BEFORE any write

`package_open("tamheed")`. Then `git status --short -- tamheed` prints nothing: the open moved no
file. Then read:

| Probe | Expected |
|---|---|
| `gate_run` `ready` | equal to the reading of 2.1 (on `f0d6f636`: `false`) |
| `readiness_check("package")` `ready` and the blocking rules that fail | equal to the reading of 2.1 (on `f0d6f636`: `false`, with `acs-met`, `adrs-approved`, `risks-discharged`) |
| `package_verify` | `verified true`, `dirty []` |

When the operator updated first, compare with the values in brackets and with the facts that
your latest handoff marks as verified. If any probe differs, STOP and file a feedback row.
Nothing has been written yet.

### 2.4 The stock guide and the review page

`handoff_emit("<repository root>", refresh_stock=true)`. On `f0d6f636` it refreshed
`tamheed/README.md` (the stock guide, now of 6.9.0) and moved `tamheed/CLAUDE.md`. The note's table
of obligations gains one row, on `create: true`. It reported three restated lines, as 6.8.0 does.

A root `.mcp.json` appears only when the plugin is loaded from a local folder. A marketplace
install does not write it. If it appears, remove it and commit nothing of it.

Then `export_html()`. `package_verify` reads `review_current true` and `review_exported_by
"6.9.0"`. `package_close()`. On `f0d6f636` the three files that moved were the two above and
`tamheed/review.html`. On the operator's word, commit them as one commit, for example
`tamheed: the 6.9.0 stock guide and review page`. Push and bind by your own rules.

### 2.5 The seven feedback rows

FB-025, FB-029, FB-032, FB-033, FB-034, FB-043 and FB-044 are `Reported` on `f0d6f636`, and
6.9.0 answers all seven. Ask the operator. On their word, set each to `Resolved` with a PARTIAL row: `id`, `kind`,
`title`, `lifecycle_status`, `resolved_in` `"6.9.0"` and `upstream_ref`
`"https://github.com/A-H-911/tamheed/blob/v6.9.0/plans/256-field-round-6.9.0.md"`. A move inside
Confirmed, Reported and Resolved is bookkeeping: it needs no `operator_confirm`. Then
`export_html()` again, so the review page shows the rows, and `package_close()`. Commit the
rows and the page on the operator's word. End the session with a `handoff` entry
(`tamheed:session-handoff`): it records the upgrade and the rows.

## 3. The two answers, and three offers to the operator

### 3.1 The answers

- **FB-029.** The `discharged_by` column records a risk's discharge, on the operator's word. A
  `discharges` edge records the plan: the AC or test that is meant to retire the risk.
  `risks-discharged` reads the column, as before. Its note now names each listed risk whose edge
  comes from an AC whose latest verdict is Met, or from a Pass test. On `f0d6f636` that is
  RISK-013 alone (AC-004, latest Met). RISK-016 is `retired`, so the rule does not list it. Your
  five edges stay as they are.
- **FB-044.** Orient-resume step 7 now reads two signals for the slice it proposes. Signal 1:
  journal entries whose `slice_id` is the slice. Signal 2: the latest handoff names the slice.
  Both: the slice resumes at the handoff, with no new kickoff. Neither: the kickoff is offered.
  One alone: the agent asks the operator. On `f0d6f636`, SL-008 has 450 entries with its
  `slice_id`. A project's own rule for this can go in a prompt row bound to `orient-resume`.
  Your LL-066 can stay, or retire on the operator's word.

### 3.2 The offers: optional, each on the operator's word

Put the three offers to the operator in one interview (`tamheed:operator-interview`).

1. **RISK-013's discharge.** If the operator says AC-004 retires it, set `discharged_by`
   `"AC-004"` on RISK-013. AC-004 is `Proposed`: the operator judges whether its Met verdict is
   enough. A candidate is never a discharge by itself.
2. **The slate workarounds.** Your scripts FB-031, FB-040 and FB-042 copy each recommendation into
   a card's detail, and spread a long point over four places. On a NEW slate, such as poc-points,
   send `show_recommendations: true` and one detail of up to 32,000 characters instead. The
   scripts are yours to change. Do not add the key to a slate that already has answers: its
   record would change, and those answers would no longer match it.
3. **DEC-214's layer set.** The order matters, because a row that breaks a declaration refuses
   any write that sets its `custom_attributes`, and one refusal fails the whole batch:
   1. Declare the set on each family that carries `layer`, on the operator's word:
      `entity_upsert([{"type": "entity-type", "type_id": "<family>", "operator_confirm": true,
      "custom_attributes": {"fields": [{"name": "layer", "values": [<the values of DEC-214>]}]}}])`.
   2. Read `declared-attributes` in `readiness_check("package")` at once. It lists each row that
      breaks the set, with the cause, and `counts` gives each family's total.
   3. Fix every listed row in ONE batch of `merge_attributes` items.
   4. Only then run your usual batch scripts.

## 4. The way back

Measured on 2026-11-27 with the real 6.8.0, on a package that 6.9.0 had written. The store opens
and verifies clean, and a 6.8.0 write keeps it clean. 6.8.0 ignores a family's declaration, so it
writes a value that the declaration refuses. 6.8.0 refuses a slate spec or record that holds
`show_recommendations` or a text over 8000 characters: such a slate stays 6.9.0's. Your 14
answered slates read under both.

### Route A: the data

The upgrade changed only the guide, the package note and the review page. Close the package
first. Then go back in one step:

```text
git restore --source=PRE --staged --worktree -- tamheed
git commit -m "tamheed: back to the package as it was before 6.9.0"
```

Or `git revert --no-edit PRE..HEAD`, when every commit after PRE touched the package alone.
Then `git clean -nd -- tamheed` lists the files that git does not track and removes nothing.
**`git clean -fd` removes a file for good.** Copy each file that the operator keeps outside the
folder first. Do NOT use `git checkout PRE -- tamheed` after a commit: it leaves new files in
place.

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
| 5 | The rows | the seven rows read `Resolved`, `resolved_in "6.9.0"` |

## 6. Not built, and said plainly

- `create: true` is opt-in. A write without it still updates a row that has the same id.
- The slate page was checked in Chrome. Safari 15.4 and later wrap a long word the same way, by the
  standard, but no Safari run was made.
- A headless run cannot answer whether another client has the repository open. The operator
  answers that.

## 7. If a class fails

File one feedback row for each class that fails: the step, the expected result above, and what
you saw. Then stop.
