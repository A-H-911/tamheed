# Plan 229 -- acceptance, release 6.5.0, the two field prompts

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- Acceptance on the merged branch: `python check.py`, once more with
  `PYTHONWARNINGS=error::DeprecationWarning`, a scratch script driving the real handlers through
  every changed behaviour, `uv run plugins/tamheed/server/tamheed_server.py --selftest` (21/21,
  descriptions under 2,048), the browser pass of 227, the replay of both fields on scratch copies.
- Release by the 220 recipe: `stamp_650.py` (six version surfaces, the stock guide body with its
  `stock-history.json` key, the lab-tracker pins, the CHANGELOG entry naming both migrations and
  the live-package note), `docs/guide/build.py`, `refresh_lab_650.py` (it also re-exports the lab fixture's recorded
  `gates.json`, whose wired-rule note plan 222 changed), a lab beat that exercises a
  register and a slate. Then the operator's word: merge, push, `gh workflow run CI`, the tag
  `v6.5.0` on green, the ledger follow-up.
- Records: `plans/221..229`, the `plans/README.md` section, `plans/evidence/` with the fields' private words trimmed (R72).
- **ACMP prompt**: upgrade at project scope, a fresh session, `server_info` quoted. `package_migrate`
  preview then confirm on the operator's word (registry-sync, two families, one column). The
  one-time rewrite of `document_sections.jsonl` committed alone. Probes with expected results:
  `trace_query("FR-166")` shows AC-184 under `column_links`. The census of LL-149 and LL-157 in one
  exported call. `requirements-wired` lists FR-156..159 with `["work"]`, a STOP for the operator
  (a history work item as DEC-499 q2 chose, or a waiver). FB-030, FB-031, FB-032: `Resolved`,
  `resolved_in 6.5.0`, `upstream_ref` the plan URL. What was not built. A failed class is an FB row.
- **Jisr prompt**: the same upgrade. The lock's limits stated (new locks only, not across a restart,
  another machine stays manual, and the memory-snapshot limit of R91). One line that runs the macOS probe through the installed plugin. FB-001, 002, 003, 009,
  011, 004, 005, 006, 007: `Resolved` with plan URLs. FB-003's answer is `Hold`, and GATE-001's outcome is
  the operator's to write. Moving the three registers into the family, and what becomes of the local
  page's FB-008 row, are the operator's calls in Jisr, each put with a recommendation. FB-010's
  script reads the plugin by a versioned cache path: the path moves to 6.5.0.
- Every recipe of both prompts is dry-run on a scratch copy first. The prompts are handed in the
  maintainer session, as for 6.3.0 and 6.4.0.

## Owed to this plan by the earlier ones (added as they landed)

- From 225: the CHANGELOG holds an `[Unreleased]` section that names the migrations. The 6.4.0
  stamp inserted its entry above the newest release heading. A stamp derived from it must
  REPLACE the `[Unreleased]` block with the 6.5.0 entry, or the block stays above the release.
- From 225: the fixtures rewrote `document_sections.jsonl`, so their recorded pages, CSVs and
  exports lag the data. `package_verify` on the lab fixture reads `verified: true`, `dirty: []`,
  `review_current: false`, `review_exported_by: 6.4.0`. The fixture refresh re-exports them.
- From 224a: the stock guide `prompts/README.md` names the lock outcomes. Its body is pinned by
  `stock-history.json`, so its lock paragraph changes with the history key at the stamp.
- From 222: the lab fixture's recorded `gates.json` keeps the old wired-rule note until the refresh.
- From 222, owed to 228: the review page's readiness table does not show a rule's `missing` legs.
- For the Jisr prompt, measured on the export of 2026-11-12: its two review scripts read rows
  by key, so the new `lifecycle_status` key in every section row does not break them. One of
  them skips bank rows whose `custom_attributes.kind` is `superseded`. Two section rows carry
  that mark. One was retired with the typed status on a scratch copy, and every gate kept its status.

## As built: acceptance and the stamp (2026-11-12)

Acceptance on the branch, at the stamped tree:

| Check | Result |
|---|---|
| `python check.py` on Python 3.13 | passes, thirteen suites |
| `python check.py` on Python 3.10 | passes |
| the same with deprecation warnings as errors | passes |
| the selftest | 21 of 21 tools, longest description 677 characters |
| `scripts-229/acceptance_650.py`, one scenario through plans 221 to 228 | 21 observations hold |
| the first field's package on a scratch copy | the sync moves three files, verifies clean |
| the second field's 620 register rows | all admitted with fitted declarations, gates equal |
| the second field's question bank through the slate tools | 75 and 227 questions, store verifies |

The stamp (`scripts-229/stamp_650.py`): six version surfaces, the stock guide's two new
paragraphs with its history key, the lab-tracker pins, and the changelog. The `[Unreleased]`
block is REPLACED by the 6.5.0 entry, which names both migrations and carries the note for a
live package. The fixture refresh (`refresh_lab_650.py`) ran the engine over the lab fixture:
the stock guide, the review page, one CSV and the recorded gate report follow the release.

Deviation from this plan, stated to the operator with the commit question: no register and no
slate were written into the recorded lab fixture. The acceptance scenario exercises both on a
package made for the run. The fixtures stay packages written before 6.5, which is a tested
state: such a package is told the route at its first register write.

Still open at this point: a person clicks Save on an interview page once, the merge and the tag
on the operator's word, and the two field prompts.

## As built: the two briefs (2026-11-12)

- The stamp is `f70a728`. CI run 43217708891 is green on eleven jobs.
- `plans/briefs/acmp-6.5.0.md` and `plans/briefs/jisr-6.5.0.md` are written, and both are on
  the plain-English roster. The second holds ids, statuses and counts only (R72).
- Every recipe was dry-run on a scratch copy of each package with the 6.5.0 engine: the
  preview, the confirm (three files move), the verify, the export, the gate result, the wired
  rule, a partial resolve of a feedback row (three columns change), the export of every link.
- The first field: the wired rule lists exactly FR-156 to FR-159 with the work leg missing, and
  `trace_query("FR-166")` returns AC-184 as a column link. Its three rows stand `Confirmed`.
- The second field: the gate result is the same as before the upgrade. Its eleven rows stand
  `Confirmed`, two of them local tools. Its linter import searches the plugin cache.
- Both briefs carry the operator's note of 2026-11-12: a valid answers file proves nothing
  about who wrote it, and an agent that acts on one without the operator's word in the session
  has committed a fault.

## The field assurance of 2026-11-14

The operator held the release: prove that both fields can take it, give them a tested way
back, and sweep the documents. Every measurement ran on scratch copies of the two real
packages. One was a clone of the ACMP repository, pinned at `e1e2d937` once it was seen that
its live session wrote while the first copies were taken. The other came from the Jisr export
of 2026-11-12. Each engine ran in its own process: the real
6.4.0 code from the tag `v6.4.0`, and the 6.5.0 code. The scripts are in
`plans/evidence/scripts-229/assure/`. They print file names, ids and counts.

### What the measurements found, and what changed

| Found | Change |
|---|---|
| With 6.5.0, an open and a close before the migration wrote `document_sections.jsonl` again in full | R115: the open refuses such a package and names the migration. Two tests |
| `package_migrate` answered "nothing to migrate" for a package that was behind in a column alone | a column alone is a reason for a registry sync |
| 6.4.0 on a migrated package raised a bare error, and moved no file | 6.5.0 refuses a file from a later release in plain words. 6.4.0 itself cannot be changed |
| **A migration that failed in its file swap removed tables** (25 on the ACMP copy) and said "package UNCHANGED". The fault is in every release since plan 045 | each new file takes its place in one step, and no old file is removed first. A stopped swap names what moved, and a second run finishes it. Two tests, both red on the old code |
| The migration takes no backup | both briefs start with a clean tree and a recorded commit |
| The briefs had no way back | section 1b in both, from the measurements below |

### The compatibility matrix (both packages gave the same answers)

| Engine | Package as it is | Migrated package |
|---|---|---|
| 6.4.0, idle open and close | opens, moves no file | stops on an unknown key, moves no file |
| 6.4.0, one write | writes one file | stops on an unknown key, moves no file |
| 6.5.0, idle open and close | refuses and names the migration, moves no file | opens, moves no file |
| 6.5.0, one write | refuses, moves no file | writes one file |

The migration moved three files. Gates, blocking rules, row counts and trace edges were the
same under 6.4.0 before it and under 6.5.0 after it. Only the journal grew.

### The drill

| Case | ACMP copy | Jisr copy |
|---|---|---|
| Three migrated files restored: the tree equals the original byte for byte, and 6.4.0 opens it with the same results | holds | holds |
| The same after the migration, a full exercise of the 6.5.0 tools and an export | holds | holds |
| The 6.5.0 tools over the real rows: every family read, every link, the review page, a register, a retired section, a slate | every check holds | every check holds |
| A migration stopped by one unwritable file: no table lost, one file in the new form, a second run finishes | holds | holds |
| Every export file written again by both engines holds the same rows in the same order | 29 of 29 | 35 of 35 |
| The field's own scripts on the exports that 6.5.0 wrote | generator test 17 of 17 | page equal apart from the digest, 15 tests pass |

### The plugin, forward and back

Measured in a separate configuration folder (`CLAUDE_CONFIG_DIR`), in a scratch repository, at
project scope, with Claude Code 2.1.323 on Windows. The machine's own records were read
before and after, and they did not move.

- `claude plugin marketplace add A-H-911/tamheed#<ref> --scope project` writes the `ref` into
  the repository's `.claude/settings.json`.
- From the branch of this round the plugin installed as 6.5.0. From the tag `v6.4.0`, the two
  update commands answered "updated from 6.5.0 to 6.4.0".
- The installed copies of both bundles ran their selftest (19 and 21 tools). The installed
  6.5.0 copy opened the migrated copies of both packages.

### Tested here, in CI, or only in the field

| Aspect | Where |
|---|---|
| The engine's suites, lints, round-trip and evals | here on Python 3.13 and 3.10, and in CI on three systems |
| The upgrade, the way back, and a stopped migration on the two real packages | here, on copies, on Windows |
| The interview page's script | here, in Chrome, by the browser check. CI runs no browser |
| A real link at a slate's answers path | CI, on Ubuntu and macOS |
| Chrome on the field's Mac, and the lock on a real macOS host | the field, through a probe of its brief |
| Rows that a field wrote after its copy was taken | the field: its preview must equal the brief's, or it stops |
| An agent that reads a brief and runs it through the served plugin | here, twice: see the rehearsals below |

### The way back, with git itself

The first drill restored files by copying them. The briefs prescribe git commands, so the
drill was run again in a clone of ACMP and in a scratch repository made from the Jisr export.

| Command | Result on both |
|---|---|
| `git checkout -- <package>/data`, before the migration commit | three files go back, `git status` is clean, and 6.4.0 opens with the same results |
| `git restore --source=PRE --staged --worktree -- <package>`, after two commits | `git diff PRE` is empty after its commit, and 6.4.0 opens with the same results |
| `git revert --no-edit PRE..HEAD` | no conflict, the same end state |
| `git checkout PRE -- <package>`, as the brief first said | WRONG: eight files of the new release stay, and `git status` does not name them |

The briefs and `docs/install.md` now prescribe the first three and warn against the fourth.
In ACMP's clone one file outside git's view stayed: its `exports/` folder is ignored.

### The pin reaches every repository of a machine

Measured in the separate configuration folder with two scratch repositories. The first was
pinned back to `v6.4.0`. The second, whose own settings still named the branch of 6.5.0, was
moved to 6.4.0 by its own next `plugin update`. One machine keeps one marketplace record of a
name. Both briefs and the install guide say so.

### The review of the swap and of the open's guard

An independent review ran its own experiments. It found no way for the new swap to lose a
table. Its findings, each reproduced by a failing test or by reading, and each fixed:

| Finding | Fix |
|---|---|
| The open judged a file by its first row, and the migration by all rows together. A file with one short row was refused by the open and called current by the migration | one rule for both: a file is behind when any row lacks a column |
| A sync for a column alone wrote a journal row with no content | the row names the table and the column |
| A staging copy that failed halfway left one `.tmp` file while the answer said none was left | the staged name is recorded before the copy |
| A failure of the last step, after every file was in place, was reported as a stopped swap | it says that every file is written, and names the old file to remove |
| A file held for a moment by another program stopped the swap at once | the swap waits as the store's flush does: five tries in under a second |

The review also confirmed that no other entry writes the data of a package that is behind.
`package_verify`, the resume hook and `package_unlock` read, or go through the guarded open.
Left as it is, and said: when a sync of types alone stops after the registry file, a second
run finds nothing to do and the journal row of that sync is not written.

### Not measured

- The committed sample pages were not written again one by one. The gate's own stages cover
  the samples that it reads.
- Route A in the real Jisr repository: its ignore rules were not in the export.

### Two rehearsals by an agent, through the served plugin (2026-11-15)

The operator asked for them. A headless Claude session ran in each scratch repository, with
the brief copied in and the 6.5.0 bundle loaded from the commit. It was told to execute the
brief: section 1, the probes of section 2, and the way back after the migration commit. It
was denied the `claude` command, because that command would have moved the machine's own
plugin records. So check 4 of 1.1, section 1.2 and route B were skipped, and they rest on the
measurement in the separate configuration folder.

| | ACMP clone | Jisr scratch repository |
|---|---|---|
| Turns, and what the upgrade did | 41. Every step of section 1 matched the brief | 57. Every step of section 1 matched the brief |
| The probes of section 2 | all seven classes hold | classes 1 to 7 hold. Class 8 needs a host rename |
| The way back, as the agent ran it | `git diff PRE` empty | `git diff PRE` empty, and three new files that git did not track stayed |
| Checked afterward with the real 6.4.0 code | opens, with the same gates, rules, counts and edges as PRE | the same |

What the rehearsals found in the briefs, each corrected in both:

| Found | Correction |
|---|---|
| The restore handles tracked files alone. A new table and a slate that were never committed stayed in the folder | a step after the restore: `git clean -nd`, read the list, then `git clean -fd`. Measured: the folder then equals PRE byte for byte |
| The probe table led the agent to write throwaway rows: a section, a register, a slate | probes 1 to 4 run now. Classes 5 to 8 are read at the first real use, and no probe row is written |
| "Exactly this" under the preview, while the report holds two more keys | the three keys are named, and so are the two others |
| The refusal's words were quoted without their start | quoted as the tool says them |
| "The same blocking rules as before", with no reading from before | the expected result is stated for each field |
| No commit message, and no word on closing the package before a commit or the restore | a message is given, and both steps say: close the package first |
| The stock refresh was said to write the root note | it rewrites the package's README and the package's own note. The root note stays |
| A bare `trace_query()` returns every link | the probe passes a small `limit` |
| "A PARTIAL row: id, kind, title" did not name the item's `type` | the row's `type` is named |

Seen in the rehearsals and not a fault of the release: a root `.mcp.json` appeared, because the
bundle was loaded from a scratch folder. An installed plugin writes none. The migration's
journal row has no time, as the six earlier ones in ACMP's journal have none. The start hook
says "unlocked" for a package that the open then refuses until its migration.
