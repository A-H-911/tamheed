# State, resumption, and updates

**The package is the state.** In v2 there is no state file: the relational store (ADR-0001) holds
every register row, narrative section, trace edge, the `packages` row (profile, mode, iteration,
versions), and the execution-tracking tables. Canonical form is JSONL per table under `data/`,
committed to git; SQLite is the runtime the MCP server loads it into.

(`keystone-state.json` is v1's state file. It is read exactly once more — by `package_migrate`
in plan 010 — and never written again. Its schema stays frozen in `../schemas/` as the migration
source contract.)

## Resume

`resume` = `package_open(name)` + orient:

1. `entity_query` the working families (requirements by status, open questions, decisions Proposed).
2. `gate_run` — the gate report tells you which stage the package is effectively in (missing
   families → Understand/Explore; trace gaps → Stage 17; no prompts → Stage 20).
3. Continue from the last incomplete stage; never re-ask settled questions.

Human edits between sessions are not a reconciliation problem by construction: humans review through
the rendered surfaces and change things through the tools. A hand-edit to `data/*.jsonl` at rest is
legal (text-canonical storage is the point) and is validated on next load — FK/CHECK violations fail
loud, nothing is silently repaired.

## Update cycles (Stage 21)

The three D-UPDATE capabilities and their tool sequences are specified in `modes.md`. The properties
that make them safe live in the schema:

- **Cascade-on-transition:** one recorded transition (an AC verdict, an ADR approval, a slice
  completion) updates every dependent view in the same transaction — there is no "reconcile trackers"
  step to forget.
- **Supersession, not edits:** approval-bearing rows (`adrs`, approved `acceptance_criteria`) reject
  content UPDATEs at the trigger level; INSERT the successor, then point `superseded_by` at it.
- **Iteration refs:** `introduced_in`/`retired_in` on requirements/phases/slices/ACs make every scope
  change reconstructible per iteration.

## Consistency invariants

- Derived data (traceability, status, backlog, readiness, identifier counts) is **views only** — it
  cannot drift from the rows because it *is* the rows.
- Every mutation ends with canonical write-back; `data/` in git is always loadable to an identical
  store (round-trip byte identity, `../db/CANONICAL.md`).
- One writer per package (`data/.lock`); a second opener fails loud, never waits, never steals.
