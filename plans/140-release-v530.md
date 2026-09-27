# Plan 140: tag v5.3.0, the brief file, close-out

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE** (the release commit; tag `v5.3.0` on it)

## What this plan does

1. The brief `briefs/acmp-5.3.0.md` (read by path; classes only, line counts included): E1–E7 of the
   5.2.0 brief owned; the upgrade (tree equality; no migration; restart is the route; the trace recipe);
   the predicted classes; the twelve absorbed remainders by anchor (the operator may trim those kept
   index lines on their word); the Q1 protocol (the first normal-work session that read no brief);
   `findings_35`'s questions.
2. **The advisor reviews the brief AND the batch record BEFORE the close-out commit** (last cycle's
   post-tag commit came from reviewing after the tag).
3. The close-out commit (batch record EXECUTED, the brief, the index, this file) → push → CI green →
   tag `v5.3.0` on it → push the tag → nothing after.
4. The memory file `tamheed-v530-findings34-batch.md` + the MEMORY.md pointer (outside the repo).

## As it ran

The replay over a read-only copy of ACMP at `e88b051b` held on every class (batch record M2); the
self-test registered 19/19; the advisor reviewed the brief and the batch record before the close-out
commit. That commit's CI was red on ubuntu (a test's pid past Linux's probe bound — batch record note 6);
the fix commit landed before the tag and the tag sits on it; nothing landed after the tag.

## Owed housekeeping (the user's)

- Three orphan worktrees under `.claude/worktrees/` (`agent-a701f7e0…`, `agent-a7dd2ae7…`, `agent-ac6565c6…`).
- The ACMP session runs the brief; Q1 is measured in the first brief-free session; `DEF-218` waits on
  the operator's word.
