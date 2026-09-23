# Plan 107: three honesty fixes (findings_30 §3.2-3.3)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [106-111-batch-findings-30.md](106-111-batch-findings-30.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW

## What changes

1. `deferred-work-reviewed` lists `Open` and `Scheduled` only; the note says what discharges each state.
2. The pointer warning says "rebuilt there" only when the note changed, else "is current there; nothing written".
3. The review page renders a one-line "No reported feedback awaits an answer." when the package has
   feedback rows and the unanswered fold is empty.

## Done criteria

- [x] RED then GREEN for each; `python check.py` (step 11 of `register-liveness.md` rewritten here with its `4.14.0` key — it describes this rule)
- [ ] CI green
