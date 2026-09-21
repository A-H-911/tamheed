# Plan 076: The prose-id rule says what it skipped and what is not an id

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (two informational lists; the failing list
  only gets smaller) - **Category**: integrity (findings_26 s1-s2)
- **Planned at**: commit `cedb443`

## Why this matters

findings_26 s1: `prose-ids-resolve` "found every phantom this package had", and the code-span skip
is right (it kept design sample data `ADR-2026-001` out) - "but the same skip means the report
tracks formatting rather than correctness": the rule saw 3 of 6 `DEC-208` occurrences, a row was
silenced by reformatting with no citation changed, and "nothing tells a reader whether a clean
result means 'no phantoms' or 'no phantoms outside code spans'". s2: the one false positive,
`SEC-8`, is "not even well-formed" for a family of 633 three-digit ids.

## What changed

`_scan_prose_ids` returns three lists instead of one:

- `dangling` - bare, well-formed, resolves to nothing. **Only these fail the rule.**
- `in_code_spans` - the same, but only inside a code span. Still skipped as a failure, now
  REPORTED on the rule entry, so backticks hide nothing and a clean result says which kind of
  clean it is. This is findings_26's remedy 2, and it makes their remedy 3 (a per-row opt-out)
  unnecessary: a row that documents a phantom backticks it, and the hit stays visible.
- `not_well_formed` - the numeric part is narrower than any id the family holds. **Reported, not
  dropped**: the devil's-advocate review found that dropping would hide a real slip (`DEF-82`
  typed for `DEF-082`).

A token immediately followed by `-<digit>` is not an id (`ADR-2026-001`). Stated cost: a range
written `PE-1300-1310` is not scanned. The note now says **the entity list is a floor, not a
census**. Both new lists are capped like the first.

## Measured (read-only, ACMP's tool-written exports; 1,233 ids, nine families)

| | before (4.9.0) | after |
|---|---|---|
| fails the rule | `DEC-208`, `DEF-082`, `ADR-2026` at the time of plan 070 | nothing |
| `in_code_spans` | invisible | `DEC-208` |
| `not_well_formed` | - | nothing (they had already normalised `SEC-8`) |

So the width rule is justified by findings_26's one case and removes nothing on today's corpus;
that is stated rather than oversold. All three eval fixtures scan empty on all three lists.

## Tests

`test_prose_id_rule_says_what_it_skipped_and_what_is_not_an_id`: one row carrying a backticked
phantom, a too-narrow token, `ADR-2026-001` and a bare phantom -> one entity, one code-span hit,
one not-well-formed hit, `ADR-2026` nowhere, the note says floor; after the bare phantom is
removed the rule passes and the code-span hit is STILL listed. RED before, GREEN after.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (158)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
