# Plan 118: lab beat 22 — the fixture meets 5.0.0

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (an agent moves the fixture)

## Why this matters

The lab fixture carries 16 stock prompt files, a v4 note in its workspace and a recorded deferred-work omission. Beat 22 is the first real package meeting the retired library, the note v5 and `carries`.

## What changes

Executor plan written before dispatch (dry-run on a copy + the F-6 grep: `prompts/` names in evals.json and scenario.md; the README's three eval needles). The beat: leftovers retired by `refresh_stock`; the README refreshed; the workspace note v5; `carries` + `deferred-work-carried` on a temp package; step 15's arithmetic on the fixture's lessons; the customised-leftover branch on a copy; scenario.md's `prompts/orient-resume.md` sentence re-aimed.

## Done criteria

- [ ] every new eval assertion fails on the pre-beat fixture (git archive)
- [ ] evidence report + scenario beat 22
- [ ] re-verified by the maintainer before cherry-pick
- [ ] CI green
