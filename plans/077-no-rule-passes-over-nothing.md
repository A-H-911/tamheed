# Plan 077: No rule passes over nothing; a recorded omission is a deliberate zero

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: MEDIUM (readiness wording changes on every small
  package; `ready` never moves)
- **Category**: hollow-pass doctrine (C35/N3) - **Planned at**: commit `4c26224`

## Why this matters

findings_26: "`execution-plans-approved` PASSES with `rows: 0` and `hypotheses-measurable` PASSES
with `rows: 0`. Both are vacuous passes, indistinguishable from real ones without `population`";
and at slice scope `execution-plan-approved` passes over zero rows beside two rules that read
`indeterminate`. Plan 069 had reported the denominator but deliberately left the verdict alone,
calling the generalisation "arguable doctrine". The maintainer ruled on 2026-09-21: generalise,
with one exit.

## Measured before it was built

| Package | Rules passing over zero rows at 4.9.0 |
|---|---|
| fresh (`package_create` only) | **17 of 21** |
| lab fixture | 2 (`deferred-work-reviewed`, `hypotheses-measurable`) |
| `minimal-brief` | 7 |
| `execution-loop` | 2 |

None is a blocking failure, so `ready` cannot move.

## What changed

In the one `rule()` helper: a query-built rule whose family holds **zero rows** (and which named
no entities) reads `indeterminate` / `discriminating: false`, at package scope. The exit, on the
maintainer's ruling: if the family's **omission is recorded** (the mechanism G-SET already uses),
the zero is deliberate - the rule reads `pass` and carries `omitted: {entity_type, reason}`.
Without that exit a legitimately empty family would stay amber forever, the trap plan 070 was
built to avoid. A SCOPED zero (a slice with no ACs) keeps plan 049's behavior: a family-level
omission says nothing about one slice.

This replaces plan 069's one-off `empty_is_indeterminate` flag on `lessons-confirmed`.

## Tests

`test_no_rule_passes_over_nothing_but_a_recorded_omission_is_a_deliberate_zero`: every rule with
zero population reads `indeterminate`; a genuinely empty family, chosen at runtime, reads `pass`
and names its omission once that is recorded; `ready` identical before and after; a rule over a
populated family is still judged. RED before, GREEN after.

**The flipped-assertion audit the plan promised:** the suite was run after the change and the
flips listed rather than chosen in advance. **None of the 18 existing `pass` assertions
flipped** - every fixture they run against holds rows for the family they judge. One assertion
changed: plan 069's test checked the old one-off note wording ("no lesson"); it now checks the
general wording ("measured nothing").

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (157)
- [x] `evals/pkg_check.py gates` -> `ready=True` on all three fixtures
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
The doc surfaces follow in plan 082.
