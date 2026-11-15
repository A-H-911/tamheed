# Field patch 2026-11 - the record (ACMP's FB-033, release 6.5.1)

## Context

ACMP upgraded to 6.5.0 on 2026-11-15 and handed up one operator-confirmed row, FB-033. The
journal row that `package_migrate` writes has no `occurred_at`. Jisr was still on 6.4.0.
The row was true. Both rehearsals of the 6.5.0 briefs had reported the same empty time, and
the maintainer session had filed it as no fault of that release. That was wrong: the guide
says of the column "Stamped by the server".

## Evaluation (read or measured on 2026-11-15, before any change)

| Claim | Evidence |
|---|---|
| One writer builds the row with no time, in both modes | `tamheed_server.py:5773-5775` follows the registry-sync branch and the v3 to v4 branch |
| It is old | The same lines stand in `v6.4.0` at 5121. The first commit is `7f5482c`, v4.0.0 |
| It is the only journal row built as a dict | Two dicts in the server carry `actor`. The other one reads a handoff, and it has the time |
| Every SQL journal writer sets the time | 12 `INSERT INTO progress_entries` statements, and each names `occurred_at` |
| The first field holds seven such rows | Read at its commit `08c5d72c`: PE-334, 363, 366, 900, 1329, 1731 and 2658. The row lists six and misses PE-334 |
| The repository's fixtures hold nine | Four fixtures. They are true records of earlier engines, and they stay |
| Nothing orders by this time | The resume block, the hook and the review page show it |
| One test compares two successful migrations | `tests/test_migrate_v3to4.py`, `test_byte_determinism` |

## Rulings (operator, 2026-11-15, R115 was the last)

- **R116** Release 6.5.1 as a patch. The second field goes from 6.4.0 straight to 6.5.1.
- **R117** No old row changes. The first field's brief names its seven rows and offers one
  optional journal note with the time of each migration's commit.
- **R118** Two items that the rehearsals had surfaced join the round: the session-start line,
  and the retry after a stopped migration.
- **R119** The swap writes the journal file first. The operator ruled with three costs
  stated. A stopped sync leaves a row that reads ahead of the files until the retry. A retry
  leaves two rows. One test of 6.5.0 changes what it expects.

## What the rehearsals of 6.5.0 had surfaced, each item checked

| Seen | Verdict | Evidence and outcome |
|---|---|---|
| The migration row has no time | Defect | FB-033. Plan 230 |
| The hook says "(schema 10) - unlocked", then the open refuses | Misleading | `resume_hook.py:116`: the number is the engine's. Plan 230 |
| "Run package_migrate again: it finishes the sync" | False in one case | With the journal file held, the retry answers "Nothing to migrate". Plan 230 (R119) |
| A root `.mcp.json` appeared | An artifact of the rehearsal | `tamheed_server.py:4916`: it is written only when the server is not under `~/.claude/plugins/` |
| `package_open` created a root `CLAUDE.md` | By design since 6.2.0 | Only when the project has none |
| A write of a section or a register adds no journal row | By design | The server journals guarded moves only |
| `clarifications-open` skipped a marker on a missing question | By design | It lists valid markers. `G-COMPLETE` caught the other |
| After going back, the open named only the column | By design | The briefs carry the `git clean` step |
| The lock's time read the day before | No fault | The time is UTC |
| The feedback row's own `recorded_at` is empty | By design | The guide says: the caller's column |

## Research behind R119

Two web searches were run, and their result snippets were read, not the pages. Flyway's
history table carries an `installed_on` time. PostgreSQL's manual says that a data change is
written only after its log record, and that a crash is repaired by redo. The second finding
supports the order alone: this engine's retry recomputes from the files, never from the row.

## The plans

| # | Plan |
|---|---|
| 230 | [A migration's journal row carries its time](../230-migration-row-time.md) |
| 231 | [Acceptance, release 6.5.1, the two field prompts](../231-release-6.5.1.md) |

## The rule that this round adds

Every surprise that a rehearsal agent reports goes to the operator as a list, before the
release question.
