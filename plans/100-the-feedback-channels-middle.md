# Plan 100: the feedback channel's middle (FB-014)

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a journal row, a readiness rule, a warning, a page fold, two stock bodies)

## Why this matters (ACMP's `FB-014`, findings_29 §2)

`handoff_emit` names a feedback row while it awaits the operator (`Proposed`) or the export
(`Confirmed`) and stops the moment it is `Reported`; nothing journals the move within the bound set,
so "outstanding since when" was unanswerable; the page filed unanswered rows under a closing
heading. Between 2026-09-22 and 09-23 ACMP's five open requests were named by nothing in the package.

## What changes

- Engine: a `lifecycle_status` move WITHIN `_FEEDBACK_BOUND` (`Confirmed→Reported`, `Reported→Resolved`)
  is journaled as `transition` by `system:feedback-guard` with bookkeeping text (no word required, and
  the row says so — it never claims attestation); `_FEEDBACK_UNANSWERED_WHERE` is the ONE predicate;
  advisory `feedback-unanswered` (emitted only when the package has feedback rows, the plan-079 pattern;
  registers excluded); a third `handoff_emit` warning, ids only.
- Page: the middle fold splits into "Reported upstream, not yet answered" and "Resolved or rejected
  (kept as evidence)".
- Teaching: note row + template mirror; `prompts/README.md` (+ `4.13.0` key); `register-liveness.md`
  gains walk steps for `feedback-unanswered` AND plan 093's missing `prompt-ids-resolve` (+ key);
  governance; the counts nineteen → twenty.

## Tests

RED first: the journal row, the rule (amber / pass / absent on a feedback-less package), the third
warning, the fold split, the sweep prompt's rule list, the identity test.

## Done criteria

- [x] RED then GREEN; `python check.py` -> `ALL CHECKS PASSED`
- [x] dry-run on a scratchpad COPY of the lab fixture: rule amber `["FB-001"]`, warning names it, the
      recipe write journals the bookkeeping row and clears both (`scratchpad/dryrun_v4130.py`: `PE-036`, `changed_columns` = the three)
- [ ] CI green
