# Plan 230 -- a migration's journal row carries its time (FB-033, R118, R119)

> Status: DONE 2026-11-15 (`2c23dbf`, `a4a0e06`). Cycle: field patch 2026-11, release 6.5.1, branch
> `fix/6.5.1`. The record (evaluation, rulings R116-R119, the rehearsal items) is
> [field-patch-2026-11-record.md](evidence/field-patch-2026-11-record.md).

Three edits. Each keeps the server's line count, because the guide pins server lines.

- **The time.** `package_migrate` builds its journal row as a dict, and the dict had no
  `occurred_at`. It now carries `_now()`, the time of the confirm call. Both modes use this
  one writer: the registry sync and the v3 to v4 migration.
- **The order of the swap (R119).** The swap ran in sorted order, so `progress_entries.jsonl`
  came after `entity_types.jsonl`. With the journal file held by another program, the other
  files were written, and a retry answered "Nothing to migrate". The sync then had no journal
  row. The swap now takes the journal file first. A retry then always finds work, and it
  finishes the sync. A sync that stopped at a later file leaves two rows, each with its time.
- **The session-start line (R118).** The hook printed "(schema 10) - unlocked" for a package
  that `package_open` then refused. The number is the engine's. When `_columns_behind` names
  a file, the hook now adds one line: the file, the column, and `package_migrate`. It uses
  the same check as `package_open` (R115), so the two never disagree.
- Tests, red first. The row's time in both modes. `test_byte_determinism` pins the clock, and
  a second test proves that the clock is the only difference between two runs. A class guard
  reads the server's syntax tree: every dict with `actor` and `event_type` has `occurred_at`,
  and every `INSERT INTO progress_entries` names it. The journal file held, then a retry.
  The hook on a package that is behind.
- Not changed: the schema, the rows of earlier migrations, the committed fixtures.
- **Check:** `check.py` on Python 3.13 and 3.10, the selftest, `build.py --check`.
  **Expected:** a migration row that says when it ran, and a retry that finishes.

## As built (2026-11-15, branch `fix/6.5.1`)

- `tamheed_server.py`: the row carries `"occurred_at": _now()`. The staged files are sorted with
  the journal's file first (`journal_first`). The server's line count is unchanged: six lines
  out, six lines in.
- `resume_hook.py`: one line after the header when `_columns_behind` names a file. It reads
  "BEHIND THIS ENGINE", the file, the column, and `package_migrate`.
- One fact differs from the plan. A package with no journal row has no journal file, so a
  stopped sync creates that file. The test reads the new file apart from the changed ones.
- Scripts, each run once: `plans/evidence/scripts-230/tests_230.py`, `fix_230.py`, `docs_230.py`.

## Validation

- **Red first.** On the code of 6.5.0 nine tests failed, each for its reason. Five read
  `None` where a time belongs. The two-clock test found no difference between two runs. The
  class guard named line 5773. With the journal's file held, `entity_types.jsonl` had moved.
  The hook printed no line for a package that was behind.
- **Green.** `test_migrate_v3to4` 18, `test_resume_hook` 19, `test_mcp_contract` 263 with one
  skipped on Windows, `test_user_guide` 16. `python check.py` passes.
- **The guide.** `docs/guide/build.py` wrote `index.html`. Of the 740 figure files, none changed.
- **The cost of the hook's check.** On the first field's copy, 13 MB of data: 0.08 s beside a
  load of 0.148 s.
