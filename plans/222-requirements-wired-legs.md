# Plan 222 -- requirements-wired reads the legs (FB-031, R84)

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- One helper `_requirement_legs(conn)` over the existing view `v_req_links` (schema.sql:844) feeds
  both surfaces: `gate_run().requirements_unwired` (adds `missing: {id: [legs]}`) and the readiness
  rule (`rules[-1]["missing"]`, the srv:3132 idiom). A leg is G-TRACE's reading: any relation to a
  decision or ADR, a work item or slice, a test. The note says so. The rule keeps its `population`
  and its empty-family reading: the helper's list is registered through `measured`, as `ids()` does.
- A waiver for `requirements-wired` clears an id on both surfaces. Readiness already applies it
  (srv:2845). `gate_run` reads the same waivers, removes those ids from `requirements` and lists them
  under `waived`. Without this, FR-156..159 would stay on the every-session surface for good.
- Measured on the repository's own fixtures (the demo sample and the three eval samples): the ruled
  predicate lists nothing, as today's does. No eval assertion names the rule. Only the note's words
  move in the recorded pages.
- Measured on ACMP today: lists FR-156..159 (`Implemented`, no work leg, left out on purpose under
  DEF-063). On the local Jisr copy: nothing. A strict per-relation reading was measured and rejected:
  on ACMP it lists 17 more `Implemented` requirements, whose decision link is a `relates_to`, and it
  would part from the blocking gate's own reading.
- Teaching: `register-liveness:95`, `governance.md:255`, `drift-register:47`, `progress-sync:58`,
  `docs/entities.md:258`, `quality-gates.md`, `content.py` `rule.requirements-wired` EN+AR.
- Tests: re-aim `test_mcp_contract:867`. New: scope-only edges are listed with three legs missing
  (the FB-031 repro, red first). `Implemented` with no work leg lists `["work"]`. `Approved` with one
  leg passes. A `relates_to` decision link counts. `ready` never moves. A waived id leaves both
  lists and is named under `waived`. (The lab fixture's recorded `gates.json` is refreshed at
  the release step, plan 229, with every other recorded export.)
- **Check:** red-first tests, `check.py`, the rule replayed on a scratch copy of ACMP.
  **Expected:** exactly FR-156..159 listed there with `["work"]`, nothing on the four fixtures.

## As built (2026-11-11, branch `round/6.5.0`)

- `_LEGS` and `_requirement_legs(conn)` in the server, read through the view `v_req_links`.
- `gate_run().requirements_unwired`: `requirements`, `missing`, and `waived` when a waiver for
  `requirements-wired` applies (per entity, or the whole rule, never an expired one).
- The readiness rule `requirements-wired`: the same list, registered through `measured`, with
  `missing` for the ids still listed.
- Teaching: `register-liveness` step 13, `governance.md`, `docs/entities.md`, the guide's
  `rule.requirements-wired` in English and Arabic.
- Moved to the release step (plan 229): the recorded `gates.json` of the lab fixture keeps its
  old note until the fixture refresh, which rewrites every recorded export in one pass.

## Validation

- Red first: four tests failed before the engine change (three on the missing `missing` key, one
  on the waiver). After it and the reviews the contract suite runs 234 tests, all green.
- `python check.py`: ALL CHECKS PASSED. Lint 14 found one long sentence in `docs/entities.md`
  first. It was split.
- Replay through the real handlers on a scratch copy of the first field package: the two surfaces
  list exactly FR-156, FR-157, FR-158 and FR-159, each with `["work"]`. `ready` stays true. The
  rule reports its population (236 requirement rows).
- Second review round (the advisor), folded in. No second copy of the old predicate exists in
  code (the server files, `evals/pkg_check.py`, the guide generator). The `gate_run` note no
  longer invites a waiver: it says the operator waives, and that an agent never authors one.
  `package-writes` section 8 now says a requirement that a scope change adds still owes its legs.
  Two behaviours are pinned by tests: a whole-rule waiver clears both surfaces, and a row is out
  of the rule by `retired_in`, as in G-TRACE. So a `Rejected` requirement whose only edge is a
  `scope_removes` is listed until `retired_in` is set. Neither field holds such a live row.
- Owed to plan 228: the review page's readiness table shows a rule's entities and waivers, not
  its `missing` legs.
- An independent code and security review: no critical, high or medium finding. The SQL is
  built from the constant `_LEGS` only. The phase and slice scopes never evaluate the rule. Both
  files parse under the Python 3.10 grammar. Its two low findings were unpinned behaviours, all
  asserted now: an empty family still reads indeterminate, the order is numeric (FR-2 before
  FR-10), a work item is a work leg, `missing` holds exactly the ids still listed, and a waiver
  for one id beats a whole-rule waiver.

## Rulings taken at the review

- **R90 (2026-11-11, at the commit question): the rule reads a requirement as live until its
  `retired_in` is set, as G-TRACE does.** A `Rejected` requirement whose only edge is a
  `scope_removes` is therefore listed until it is retired. The other option, to skip the dead
  statuses too, was declined: one rule would then read "live" differently from the trace gate.
