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
  leg passes. A `relates_to` decision link counts. `ready` never moves. Regenerate
  `evals/sample-results/lab-tracker/.../exports/gates.json` by script. A waived id leaves both
  lists and is named under `waived`.
- **Check:** red-first tests, `check.py`, the rule replayed on a scratch copy of ACMP.
  **Expected:** exactly FR-156..159 listed there with `["work"]`, nothing on the four fixtures.
