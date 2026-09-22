# Plan 086: The by-hand lesson retirement is journaled by the engine

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [085-090-batch-findings-27.md](085-090-batch-findings-27.md).

## Status

- **Priority**: P1 - **Effort**: XS - **Risk**: LOW-MEDIUM (a write path on the binding surface;
  security-reviewed) - **Category**: audit completeness - **Planned at**: commit `97827e3`

## Why this matters (findings_27 §4, with the operator's ruling that it matters)

`lifecycle_status` on a lesson decides what binds every future session. The store guards that
transition hardest on the way IN (`operator_confirm`, a byte-identity gate, an audit row per approval)
and, until this plan, recorded nobody on the way OUT: the field's package holds six lessons correctly
`Superseded` with no journal row for the status write, and only four of the six have an approval row
either. 4.10.0's advisory tells an agent to take the by-hand path, and that path was the unrecorded one.
I had known this and parked it for the field to say whether it mattered; the field said yes.

## What changed

In the lesson block of `entity_upsert`: when a stored `Approved`/`Promoted` row moves to any other
status WITH `operator_confirm` (the only way it can), the engine inserts one `progress_entries` row
after the write succeeds, inside the item's savepoint - the approval-audit pattern:
`event_type: transition`, `actor: system:lesson-guard`, entry
`LESSON LL-N -> Superseded (was Approved) on the operator's word, by hand — operator_confirm attested;
confirmed_by <the STORED approver>; superseded_by <pointer if sent>`; the id is returned as
`lesson_audit`. The automatic path keeps `system:lesson-supersession`, so the two routes to
`Superseded` stay distinguishable in the journal. A refused write journals nothing; a Proposed lesson
never bound, so rejecting it stays free and unjournaled.

**Correction to the batch plan as first drafted:** findings_27's remedy said "with the caller's
actor". `entity_upsert` carries no caller actor; the engine's actor is the honest one, and the
approver is read from the store, not from what the caller re-sent.

## Security review, and the ruling it produced

Four items clean (savepoint atomicity, the guard's mutual exclusion with the refusal, journal
interpolation, flag disjointness). One MEDIUM: any caller could forge the new row - `actor:
"system:lesson-guard"`, an entry claiming `operator_confirm attested` - through `progress_update` or
the `progress-entry` upsert path, which did not even refuse the server-only event types. Measured: no
eval, prompt, doc or ACMP practice writes a `system:` actor as a caller. Maintainer ruling
2026-09-22: reserve `system:` for the engine. `_caller_journal_error` now guards BOTH caller paths
(server-only events and `system:` actors); the docstring convention reads `human:<name> |
agent:<session>`. This closes the forgery for every engine row at once (lesson-guard,
lesson-supersession, edge-retire, and plan 087's feedback-guard). A reviewer LOW, shared with the
pre-existing audit blocks and not fixed: the audit INSERT runs after the item savepoint is released
(the batch savepoint gives atomicity); it cannot raise under current constraints.

## Tests

`test_a_by_hand_lesson_retirement_is_journaled_by_the_engine`: refused write leaves the journal
count unchanged; the confirmed retirement returns `lesson_audit` and exactly one `transition` row by
`system:lesson-guard` naming `by hand` and `confirmed_by anas`; rejecting a Proposed lesson adds no
row; the forged `system:` row is refused on both paths and the server-only event on the upsert path; an `agent:` actor still writes. RED (`KeyError: lesson_audit`) before, GREEN after; contract suite 164.

## Done criteria

- [x] contract suite OK (164)
- [x] security reviewer: one MEDIUM found and closed on the maintainer's ruling; no CRITICAL/HIGH
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; no new event type (`transition` exists).
