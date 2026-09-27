# Plan 136: the observed lock, the render hint, the hook trace

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).
> Field source: ACMP `findings_34.md` (the session restart §, E2, A2), rulings R16/R17.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

1. After a Claude Code process restart the hook printed `lock file present (pid 48276 …)` and the
   agent needed `package_unlock` to learn the holder was dead (`PE-1474`, forced-override on the
   operator's word). The block named the holder and said nothing about it.
2. Thirteen unpinned approvals moved every lesson the note showed behind "19 more" (E2): the
   approval's `next` said "binds once the note is rebuilt" and nothing about rendering.
3. On two `/reload-plugins` nothing reached context; on the restart and the compaction the whole
   block did. The field could not tell "did not fire" from "fired, not delivered" (A2).

## What changed

- `_resume_block` (`tamheed_server.py`): `lock` gains `observed` + `evidence`. A lock held by THIS
  process (`package_open` after `__enter__`, `server_info` while open) reads `alive` / `held by this
  session` with no probe; a foreign lock goes through the plan-064 seam `_observe_lock` inside
  `try/except` → `unobservable` + the exception class. Measured on this host: a dead pid →
  `not-running` in < 6 ms; an out-of-range pid → `unobservable`, no exception.
- `resume_hook.py`: the lock line prints the observation and the remedy — `not-running`/`reused` →
  `package_unlock(confirm=true) on the operator's word`; `alive` → the server holds it;
  `unobservable` → `package_unlock reports the evidence`. Prefix `lock file present (pid` kept.
- `resume_hook.py` `_trace`: when `TAMHEED_HOOK_LOG` names a file that ALREADY EXISTS, one line per
  run — `<utc> source=… lines=N chars=N status=printed|silent|error:<Class>` — counts only, never the
  entry. A missing path gets nothing (a project's settings `env` block could otherwise aim the hook at
  any writable file). Any trace failure is swallowed.
- The approval hint (`entity_upsert`, Approved only): `; pinned rows always render` or `; it renders
  in the note only if pinned or among the 10 newest unpinned Approved rows - pin it to keep it
  visible`; `pinned` falls back to the stored row when a status-only write omits it. Promoted rows
  keep the old text (they never render).

## Tests

`test_mcp_contract`: `test_resume_block_and_handoff_current` (own lock → `alive` / `held by this
session`); new `test_resume_block_observes_a_foreign_lock_holder` (seam fixed → `not-running`; seam
raising → `unobservable` + class); `test_lesson_approval_says_the_note_is_rebuilt_only_by_handoff_emit`
(pinned, unpinned, status-only flip, Promoted). `test_resume_hook`: the in-process holder line; new
`test_dead_holder_is_observed_and_the_remedy_named` (pid 2**31; nothing removed); new
`test_opt_in_trace_writes_counts_only_to_an_existing_file` (missing path → nothing; existing → one
line; the entry's text absent; unset → nothing more).

## Docs

`server/README.md` (hook paragraph; the `package_open`/`server_info` row), `docs/install.md` (the lock
line; the trace recipe), `SECURITY.md` (observation removes nothing; trace = counts only, existing file
only). The docs sweep (138) carries the diagrams and the design record.

## Validation

`python check.py` green (ALL CHECKS PASSED) before the commit.
