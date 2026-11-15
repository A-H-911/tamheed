# Plan 231 -- acceptance, release 6.5.1, the two field prompts (R116, R117)

> Status: DONE 2026-11-15. Cycle: field patch 2026-11, branch `fix/6.5.1`. The record is
> [field-patch-2026-11-record.md](evidence/field-patch-2026-11-record.md).

- **Assurance on copies of both field packages.** The scripts of plan 229 are copied to
  `plans/evidence/scripts-231/assure/`, and each label is read from the bundle's manifest.
  A migration under 6.5.0 and one under 6.5.1 from the same start differ in one field of one
  row. 6.5.1 opens a store that 6.5.0 migrated, with no file moved. 6.5.0 opens a store that
  6.5.1 wrote. The journal file is held, then a later file, on both copies.
- **The stamp.** `stamp_651.py` after `stamp_650.py`: the version on the six surfaces of lint 8,
  the CHANGELOG entry, the stock guide with its history key, the eval pins. The lab fixture
  follows through the engine's own tools (`refresh_lab_651.py`).
- **The briefs.** `plans/briefs/acmp-6.5.1.md`: the plugin alone, no migration. It names the
  seven rows and the optional note (R117). `plans/briefs/jisr-6.5.1.md`: the 6.5.0 brief,
  changed line by line. The facts about the installed release move to 6.5.1. The release
  that carried each fix stays 6.5.0. `jisr-6.5.0.md` says in its first line that it is
  superseded.
- **Rehearsals.** A headless agent runs each brief through the served plugin on a scratch
  repository. Every surprise that it reports goes to the operator before the release question.
- **After the tag.** The plugin going back from 6.5.1 to 6.5.0 is measured in a separate
  configuration folder. No brief quotes an answer for that direction before then.
- **Check:** the gate on both Python versions, CI on eleven jobs, the acceptance script.
  **Expected:** tag `v6.5.1` on a green commit, and two prompts handed to the operator.

## The field assurance of 2026-11-15 (the stamped bundle, from `git archive`)

Scripts: `plans/evidence/scripts-231/assure/worker.py`, `replay.py`, `field_head.py`. Each label
is read from the bundle's manifest. The same result on both copies, unless a line says other.

| Check | Read |
|---|---|
| One start, migrated under 6.5.0 and under 6.5.1 | Each moved the same three files. The results differ in `occurred_at` of the one new row |
| 6.5.1 on a store that 6.5.0 migrated | Opens. No file moved. The preview answers "Nothing to migrate" |
| 6.5.0 on a store that 6.5.1 migrated, then wrote | Opens. No file moved. The same gates, blocking rules, counts, edges and rule count |
| 6.4.0 on a store that 6.5.1 migrated | Stops at "unknown keys ['lifecycle_status']". No file moved |
| The journal's file held | "UNCHANGED", no file moved, no staging file. The second run finished with one row |
| The same case under 6.5.0 | The second run answered that the package is current. The fault of R119, reproduced |
| A later file held | Two files moved, and the answer names them. The second run finished. Two rows, each with a time |
| The hook before the migration | 6.5.0: the header alone. 6.5.1: the line that names the file, the column and the migration |
| The first field's current commit under 6.5.1 | Opens with no migration. The stock refresh moved the guide and one line of the package note. The export moved the page alone |
| The resolve row for FB-033 on that commit | Three columns changed. 6.5.0 opened the result |
| The seven rows with no time | Each id resolves to one commit by `git log --reverse -S` |
| The ref `#v6.5.0`, in a separate configuration folder, Claude Code 2.1.325 | "updated from 6.4.0 to 6.5.0" |

`acceptance_651.py` holds on 16 observations.

Measured after the tag, in the separate configuration folder: "updated from 6.5.0 to 6.5.1",
then "updated from 6.5.1 to 6.5.0" with the ref `v6.5.0`, then "updated from 6.5.1 to 6.4.0"
with the ref `v6.4.0`. Both briefs quote the answer for their own direction.

## Two rehearsals by an agent, through the served plugin (2026-11-15)

A headless session ran each 6.5.1 brief on a scratch repository, with the stamped bundle
loaded. It was denied the `claude` command, so the plugin commands rest on the measurement in
the separate configuration folder.

| | The first field, at its current commit | The second field, from its export |
|---|---|---|
| Turns | 42 | 43 |
| The upgrade | Opens with no migration. Every expected result matched but two wordings | Every step of section 1 matched. The migration's row reads a time |
| The writes | The note, the resolve row, the export, one commit | Three commits, then the way back in one step |
| Checked afterward | 6.5.0 opens what the agent left | 6.4.0 opens the folder with the same gates, rules, counts and edges as before |

What the rehearsals corrected in the briefs: `handoff_emit` needs an open package. The export
also moves the csv file of each changed table. "Do not run package_migrate" barred the preview
that the same section asks for. A result "as before the upgrade" had no earlier reading. The
rows of the second field name 6.5.0 on purpose, and the brief now says why.

What the agents found surprising, each put to the operator before the release question:

| Seen | Reading |
|---|---|
| A root `.mcp.json` appeared | The rehearsal's own artifact: the bundle was loaded from a scratch folder |
| `handoff_emit` warns that confirmed rows are not reported, local-tool rows among them | Read in the source: the warning counts every Confirmed row. A local-tool row never leaves, so it was named at every emit. Older than this round. The operator ruled: fix it. Fixed with a test, after the rehearsals |
| A journal entry sent with no `actor` stores none | By design: the caller names itself |
| The refusal of a bad verdict opens with the raw CHECK text | As in 6.5.0. The plain sentences follow it |
| `package_migrate` describes itself as a v2/v3 to v4 tool | True of its registered description, which does not name the registry sync |
| `handoff_behind` read 0 with two notes after the handoff | By design: it counts work and transition entries |
| The export wrote no csv for an empty table | By design |
