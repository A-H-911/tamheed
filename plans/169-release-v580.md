# Plan 169: release v5.8.0 — the replay, the brief, the close-out, the tag

> Maintainer-executed, 2026-09-30. Batch map: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## Steps

1. **The replay** (`evidence/scripts-fb026-fb027/acmp_replay8.py`, its output beside it) over
   fresh `git archive` copies of the field package at `d47d9938`, with the final bundle and the
   `v5.7.0` tag's engine in its own process: every class of the brief held (the batch record's
   M79), the brief's two feedback moves rehearsed with the exact rows the brief prints, the first
   plain emit read, the hook run after a compaction on an untouched copy, the wire's
   `tools/list` read through `wire_list.py`.
2. **The selftest** under `uv` (SDK 1.28.1): 19/19 registered, 19/19 descriptions as listed,
   longest 387 characters.
3. **The brief** [`briefs/acmp-5.8.0.md`](briefs/acmp-5.8.0.md): the errors owned (O18–O20),
   what a session meets, the corrected condition for a description, the page and the field's
   scan, nine classes with their conditions, what is not built, the two feedback moves with
   their rows and the answers, and no report unless a class fails (R53).
4. The batch record EXECUTED; `plans/README.md`; the memory file and its index line; the 5.7.0
   memory lesson's resume clause.
5. The advisor's close-out pass; the close-out commit; push; CI green on every job; the tag
   `v5.8.0` on the close-out commit. No housekeeping this cycle: no worktree is left.

## Validation

- `git diff v5.8.0 HEAD -- plugins/tamheed` empty after the tag.
- The operator's trace file: 42 lines before and after every run window; every run with
  `env -u TAMHEED_HOOK_LOG`.
