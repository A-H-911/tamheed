# Plan 112: the findings_31 doc cycle (FB-017, the NOT NULL clause, the paste verifier, the brief's five errors)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (prose only)

## Why this matters

ACMP's `FB-017`: `register-liveness.md` step 15 states a false mechanism for the note budget (`_note_lesson_rows` renders pinned + `unpinned[:10]`: any unpin of a pinned lesson removes exactly one line while ten or more unpinned Approved remain; retiring an unpinned lesson removes nothing). findings_31 Q3: "omitted columns are preserved" reads wider than it is (a partial row still carries every NOT NULL column). §3.3: the promotion guard is a paste verifier. And my 4.14.0 brief's five errors are owned in the batch record (§1.1-1.5).

## What changes

Step 15 rewritten with the true arithmetic and its corollary — in the `register-liveness` scenario skill body (plan 116 creates it; the prompt file retires). The NOT NULL clause in the server README recipe, governance.md and the `package-writes` skill. The paste-verifier sentence in `skill-promote`. Executed AFTER 114-116 so the text lands on the surfaces that survive.

## Done criteria

- [ ] RED then GREEN (the skills-teaching test names the new arithmetic and the NOT NULL clause)
- [ ] `python check.py`
- [ ] CI green
