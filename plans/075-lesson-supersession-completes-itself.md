# Plan 075: A lesson supersession completes itself; retiring a binding lesson needs the operator

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (it changes what binds every session, and
  tightens a write contract)
- **Category**: governance (findings_26 s3) - **Planned at**: commit `0796adc`

## Why this matters

findings_26 s3: ACMP superseded `LL-094` (a lesson asserting something false about
`entity_query`), the operator approved its successor, and `LL-094` kept binding every session -
rendered in the always-loaded note beside the lesson that corrects it, the two lines
byte-identical inside the note's 180-character window.

**The report's mechanism was half right.** A scratch test against 4.9.0 shows the sanctioned exit
works: setting the old row's `lifecycle_status` to `Superseded` drops it from the note AND from
`entity_query("lesson", status="Approved")` - the second binding surface, which
`orient-resume.md` tells every session to read. ACMP had set only the `superseded_by` pointer.
The engine accepted that half-finished state silently (the server read `superseded_by`
nowhere), no doc said the status must change, and the plan-068 hint misfired on it ("BINDS only
once the note is rebuilt"). The same test exposed a hole: binding a lesson needs the operator's
confirmation, retiring one needed nothing.

## What changed (maintainer rulings, 2026-09-21)

- **Status stays the single truth, and the engine finishes the job.** When a lesson is newly
  approved or promoted - a write that already requires `operator_confirm` - every other
  Approved/Promoted lesson whose `superseded_by` names it is set `Superseded` in the same
  transaction, with one `transition` journal row each (actor `system:lesson-supersession`) and
  the ids returned as `superseded` on the item. Precedent for the engine changing a second
  row's status: the requirement auto-advance trigger.
- **A contract tightening.** Moving a stored Approved/Promoted lesson to `Superseded`,
  `Obsolete` or `Rejected` is refused without `"operator_confirm": true`. A Proposed lesson binds
  nothing and may still be rejected freely.
- The half-state gets a truthful `next` hint; the note tags a still-Approved row that has a
  pending successor `[..., superseded by LL-NNN - pending]` - in the tag, because the body is cut
  at 180 characters and a correct supersession keeps the old opening.
- New advisory `lessons-superseded-binding`: Approved lessons pointing at an approved successor.
- `prompts/register-liveness.md` step 14 now says the pointer alone retires nothing; its body is
  appended to the stock history under `4.10.0`, and the advisory-teaching test's tuple names the
  rule. (`skill-promote.md`'s `superseded_by` line is about skill rows and is correct as written.)

Pointing a lesson at a successor that is ALREADY approved retires nothing automatically: that
would unbind a lesson on a pointer, without the operator. The advisory names it and the hint
says how to finish.

## Review round (security + Python reviewers, before commit) - both found the same CRITICAL

- **CRITICAL, found independently by both and verified empirically by one:** my guard named
  three target statuses. Writing `lifecycle_status: "Proposed"` on an approved lesson unbinds it
  just as surely - and, because the immutability trigger fires only while the row is
  Approved/Promoted, a second unattended write could then edit its content. The exact hole the
  plan was written to close. Now: ANY move off a binding status needs the operator's word,
  presence-checked so an upsert that omits the status is never refused.
- **CRITICAL (security reviewer):** `superseded_by` was unguarded, so an agent could point lesson
  A at lesson B in advance; when the operator later approved B for unrelated reasons, the
  auto-completion would retire A - the operator confirmed approving B, never retiring A. Now:
  changing the pointer on a binding lesson needs `operator_confirm` too.
- **HIGH:** the auto-completion ran after the item's savepoint was released; a failure half-way
  through several lessons would have raised "no such savepoint" and left partial writes. It now
  runs in its own savepoint and fails the item cleanly (the batch then rolls back).
- **HIGH:** the note said "pending" even when the successor was ALREADY approved - a state that
  never resolves by itself. The renderer now reads the successor's status and says
  `RETIRE THIS ROW (operator)` there, `pending its approval` otherwise.
- **MEDIUM:** the successor id reached the always-loaded note unscreened, and the DDL's
  `GLOB 'LL-[0-9]*'` admits free text after the first digit. It is printed only if id-shaped.
- **MEDIUM:** the hint and the advisory skipped Promoted lessons. Both cover them now.
- **Known limitation, recorded not fixed:** `transition` is a caller-writable event type, so a
  caller can journal a look-alike row with actor `system:lesson-supersession`. It changes no
  state. Refusing `system:` actors from callers would need a check against migrated field
  journals first; recorded as a future option.

## Tests

`test_approving_a_successor_retires_the_lesson_it_supersedes` (hint, pending tag, automatic
retirement, both binding surfaces, the journal row, the advisory) and
`test_retiring_a_binding_lesson_needs_the_operators_word` (three statuses refused, a Proposed
rejection free, the advisory on an approved successor, the confirmed retirement). RED before,
GREEN after. **One existing test changed deliberately**:
`test_lessons_confirmed_advisory_and_immutability` retired an approved lesson unattended; it now
asserts refused-without and accepted-with the operator's word. The lab scenario retires no
lesson unattended (grepped).

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (156); lint 9 -> stock history current (84 bodies)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] security + Python reviewers' findings addressed; CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`. One stock prompt changed, with its
`4.10.0` history key in this commit. No schema migration, no new event type.
