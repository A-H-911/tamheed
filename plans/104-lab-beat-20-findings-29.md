# Plan 104: lab beat 20 (findings_29)

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (an agent against the recorded package)

## The beat

The dry-run scripts of plans 100-102 are re-run on a scratchpad copy of the fixture FIRST (the
batch-28 lesson) and cited here. Then an agent (opus, worktree) drives the recorded package:
`FB-001` reads amber under `feedback-unanswered` and the third warning names it → disposed by the
recipe → the bookkeeping journal row, pass, warning gone; `go_no_go` same-verdict unattended refused,
attested `ok` without `package_audit`; a one-token repair run twice → the second refused; a partial
row with `expect_unchanged`; `mvp_definition` written and read via `server_info`; the two refreshed
stock prompts. Every new assertion must fail on the pre-beat fixture.

## Done criteria

- [ ] dry-run cited; agent report; assertions re-run by the maintainer's reviewer before ff-merge
- [ ] evidence report `plans/evidence/lab-continuation-report-104-2026-09-23.md`; `lab/scenario.md`
- [ ] `python check.py`; CI green
