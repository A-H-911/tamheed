# Plan 079: Open-ended blanket waivers are named

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P3 - **Effort**: XS - **Risk**: LOW (one advisory rule, emitted conditionally)
- **Category**: governance (lab beat 16's observation) - **Planned at**: commit `ea2a2cf`

## Why this matters

Lab beat 16: the recorded package's `WVR-002` - a whole-rule waiver with no `applies_to` and no
expiry, approved in beat 15 for the defects that existed then - waived a defect written in beat
16 "the instant it existed". That is the documented meaning of a rule-scoped waiver and it is
reported, never silent; but it keeps absorbing rows written long after the operator approved it.
The store cannot tell "written after the waiver" (most families carry no creation time), so the
honest, mechanical signal is the one it can compute: the waiver is blanket AND unbounded.

## What changed

New package-scope advisory `waivers-open-ended`: waivers with `applies_to IS NULL AND expires IS
NULL`. A per-entity waiver is scoped by construction; an expiring blanket waiver is bounded.
The note sends each to the operator - set `expires` or narrow `applies_to` - and repeats that an
agent never authors or edits a waiver on its own judgment.

**One deliberate deviation from the batch plan, recorded:** the plan said "zero waivers with no
omission reads `indeterminate`" (plan 077's rule). Implemented instead: **the rule is emitted
only when the package has at least one waiver.** Plan 077's zero-row verdict is for families
whose emptiness is a question ("no defects - or none recorded?"). "No waivers" is simply the
healthy state, and a permanent amber about a family nobody uses would teach readers to ignore
ambers - the failure mode this batch keeps trying to avoid.

`prompts/register-liveness.md` step 10 teaches the rule; its body is re-set under the `4.10.0`
history key; the advisory-teaching test's tuple names it.

## Tests

`test_open_ended_blanket_waivers_are_named`: no waivers -> the rule is absent; a blanket waiver
with no expiry is named while a per-entity one is not; an `expires` date clears it. The test was
written together with the rule, so no separate RED run exists; it cannot pass without the
feature (it indexes the rule by name), and the acceptance pass runs it against the `v4.9.0` tree.
The lab fixture's `WVR-002` is named, as the plan predicted (advisory; `ready` unaffected).

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (159); lint clean
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`. One stock prompt changed, `4.10.0` key set.
