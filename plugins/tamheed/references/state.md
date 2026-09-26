# State, resumption, and updates

**The package is the state.** Since v2 there is no state file: the relational store (ADR-0001) holds
every register row, narrative section, trace edge, the `packages` row (profile, mode, iteration,
versions), and the execution-tracking tables. Canonical form is JSONL per table under `data/`,
committed to git; SQLite is the runtime the MCP server loads it into.

(Historical: `keystone-state.json` was v1's state file. Its ingestion path was retired with v1
ingestion in v4.0.0 — the store IS the state, and nothing reads or writes that file anymore.)

## Resume

`resume` = `package_open(name)` + orient. Since v5.1 the first read is free: `package_open` and
`server_info` return a **`resume` block** — the latest `handoff` journal entry with its
`correction` chain, `handoff_behind` (the work-done/transition entries written after it), the
open feedback, the open slices, the last three journal ids, the lock holder and the next step —
and the plugin's SessionStart hook prints the same block into the model's context on every
session start, clear and compaction (after a compaction the package is still open, so
`server_info` is the first call; `package_open` refuses an open package). The handoff is a
journal entry the agent writes LAST before it stops (`tamheed:session-handoff`); the
`handoff-current` advisory names one the journal has moved past. The block is a read of the
store, never a state file — the doctrine above is unchanged.

0. Read the handoff and its corrections; orient from the journal for the entries after it.
1. `entity_query` the working families (requirements by status, open questions, decisions Proposed).
   Registers are read through the tool whatever their size: `limit` cuts rows (never fields),
   `total` is exact, the result's `next_after` pages the rest (`after_id`), `ids=[...]` fetches a
   known set in one call, `search=` sweeps by keyword — never `data/*.jsonl` to dodge a client's
   payload cap.
2. `gate_run` — the gate report tells you which stage the package is effectively in (missing
   families → Understand/Explore; trace gaps → Stage 17; no prompts → Stage 20).
3. Continue from the last incomplete stage; never re-ask settled questions.

Human edits between sessions are not a reconciliation problem by construction: humans review through
the rendered surfaces and change things through the tools (a committed script that quotes the
store reads an `entity_export` file, v4.7). Text-canonical storage means a hand-edit to
`data/*.jsonl` at rest is *validated* on next load — FK/CHECK violations fail loud, nothing is
silently repaired — but it is not a sanctioned path: reads and writes go through the tools,
a script reads `exports/`, and a function the tools lack is a `feedback` row (v4.11), not a
reason to open the store.

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
  store (round-trip byte identity, `../db/CANONICAL.md`) — exercised on demand by
  `package_verify` (per-file byte-equality, foreign files, a citable digest; `record=true`
  journals it as a server-appended `integrity-verified` event).
- One writer per package (`data/.lock`); a second opener fails loud, never waits, never steals.
