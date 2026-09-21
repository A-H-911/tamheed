# Plan 069: Every readiness rule reports the population it measured

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (one additive key per rule entry; one advisory
  can now read `indeterminate`, which never blocks)
- **Category**: hollow-pass doctrine (C35/N3) - **Planned at**: commit `cf71a56`

## Why this matters

The densest cluster in ACMP's lessons register is the green that measured nothing. Their standing
rule: "A GREEN `lessons-confirmed` CAN MEAN NOTHING WAS RECORDED. It counts `Proposed` rows, so it
goes green when every lesson has been adjudicated and when the session filed none at all - the two
are indistinguishable at the pass bit ... Before trusting a green advisory, ask what its
denominator was." They run a hand-written control (`status="Promoted"` returning 23) beside the
rule to make its zero mean anything. Plans 028/029/049 already applied the doctrine to unpopulated
columns and to empty scopes; the denominator itself was never reported.

## What changed

- Every rule built from an `ids(...)` query carries
  `population: {"table": <family>, "rows": <n>, "scoped": <bool>}`. At package scope `rows` is the
  family's size; at phase/slice scope it is the candidate count the plan-049 `empty_note` already
  computed for THAT scope (`scoped: true`).
- Mechanism, kept to one place: `ids()` remembers the family of the query it ran, `empty_note()`
  adds the scoped count, and `rule()` reports it **only when its entities are that very query's
  result** - so a rule fed from elsewhere (`clarifications-open`, `lessons-note-budget`) claims no
  denominator it did not measure. No call site changed except `lessons-confirmed`.
- `lessons-confirmed` reads `indeterminate` / `discriminating: false` when the package holds no
  lesson at all.

`ready` and the `Implemented` guard are untouched: `indeterminate` never blocks.

**Deliberately not generalised:** "zero rows in the family => indeterminate" for every rule. A
package with no defects reading `indeterminate` on `defects-closed` is arguable doctrine and would
change most small packages' reports; it is recorded as a future option, the denominator now being
visible either way.

## Tests

`test_every_readiness_rule_reports_the_population_it_measured`: `defects-closed` reports
`{defects, 2, unscoped}`; every query-built package rule has an integer population; with no
lessons `lessons-confirmed` is `indeterminate`; one Proposed lesson makes it a real `fail` over a
population of 1; `ready` is identical before and after; a slice-scope rule is `scoped`. RED
(KeyError) before, GREEN after. No eval fixture pins the rule's wording (grepped).

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (151)
- [x] `python check.py` -> `ALL CHECKS PASSED` (incl. the three eval fixtures' readiness checks)
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
