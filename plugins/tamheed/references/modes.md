# Invocation modes

The entry point may pass a mode; if absent, infer from input completeness and **confirm with the user
before doing heavy work**. Modes change where the workflow starts/stops, not the methodology.

| Mode | Purpose | Starts | Stops |
|---|---|---|---|
| `full` | End-to-end inception → handoff | Stage 1 | Stage 22 |
| `intake` | Understand + surface gaps only | Stage 1 | Stage 7 (clarification plan) |
| `plan` | Full plan + entity set, no handoff emission | Stage 1 | Stage 19 + readiness preview |
| `resume` | Continue an interrupted package | last incomplete stage | as configured |
| `stage:<id>` | Run/re-run one stage | that stage | that stage |
| `update` | Apply new decisions/progress/scope (D-UPDATE) | Stage 21 | Stage 22 |
| `migrate` | Import a conformant v1 Keystone package | `package_migrate` (staged: preview → confirm; see `migration-v1.md`) | post-flight fidelity report |
| `adopt` | Onboard a brownfield repository | `package_adopt` (staged: scan/preview → confirm; see `adopt.md`) | gap report + gates |

Parameters: `--profile enterprise|rnd|legacy|ai-agentic|unknown` (registry-backed; community profiles
via the extension registry), `--package-dir <dir>` (validated; created if absent; never inside the
plugin), `--dry-run` (run the stage's mutations inside a SAVEPOINT, report entity counts + gate deltas,
roll back — nothing written).

## Inference when no mode is given

- Sparse / idea-level input → propose `intake` (clarify first), then offer `full`.
- Rich, structured brief with explicit constraints → propose `full`.
- User points at an existing package directory → propose `resume` or `update`.
- User points at an existing v1 package → propose `migrate`; at an existing codebase → `adopt`.
- User asks for "just the plan" → `plan`.

Always state the chosen mode and what it will and will not do, then proceed.

## Mode contracts

- Every mode operates on the package store through the MCP tools; `stage:<id>` requires an existing
  package (`package_open`).
- `plan` and `intake` must be side-effect-free outside the package directory.
- `full` and `update` honor approval gates: do not pass an approval gate on the user's behalf.
- One package open at a time; the store's lockfile makes concurrent writers fail loud.

## `update` — the agile heart of v2 (D-UPDATE)

Three capabilities, each with a concrete tool sequence. All three end with `gate_run` and a write-back
(`package_close` or continued session).

### 1. Diff-aware re-derivation

A change to an entity regenerates its dependents — and only its dependents.

1. `trace_query(entity_id, direction="in")` (repeat transitively as needed) → the impact set.
2. Preview to the operator: the impact set + what would be regenerated. With `--dry-run`, apply inside
   the SAVEPOINT and report gate deltas instead.
3. On approval: `entity_upsert` the changed row; regenerate ONLY dependent narrative sections/prompts;
   derived views need nothing (they are queries).
4. `gate_run` to confirm no new gaps.

### 2. Execution-progress sync

Ingest the executing agent's tracking output into the package.

1. `progress_update([...])` — journal entries (phase/slice-tagged).
2. `audit_record([{ac_id, verdict, evidence}])` — evidence refs (test path, CI run id) make verdicts
   *evidenced*, not narrated; the requirement auto-advance cascade fires in the same transaction.
3. `work_bind(ref, [entity_ids])` — bind commits/PRs to the FR/AC/SL they satisfy; stamps
   `last_referenced` so load-bearing registers are distinguishable from ornaments.
4. `gate_run` → G-PROGRESS reflects the new audit state instantly.

### 3. Agile scope change (mid- or post-execution)

The v1 rule "scope drift after lock requires a recorded decision" is now a mechanism. Scope events are
**typed**: `{defer, reschedule, reclassify, cancel, expand}` — distinct from supersession ("same
decision, changed phase" is a *reschedule*, not a reopen; a cancelled AC is *void*, not failed).

**Always in this order** (the `scope-change` row is written BEFORE any entity mutation):

1. `entity_upsert` a `decision` row authorizing the change (or reference an existing one).
2. `entity_upsert` a `scope-change` row: `decision_ref`, typed description ("expand: add offline
   mode"), `iteration` = current package iteration + 1.
3. Bump the package iteration (packages row).
4. Apply the mutations: new/changed `requirement`/`phase`/`slice`/`acceptance-criterion` rows carry
   `introduced_in` = the new iteration; retired ones get `retired_in` (never deleted). Cancelled
   criteria get `disposition='void'` + `disposition_reason_ref` → the authorizing decision — the
   verdict axis stays clean.
5. Impact pass: capability 1 (trace_query → preview → targeted re-derivation) over the touched set.
6. `gate_run`; report the scope delta to the operator.

Phases are appendable after scope lock only through this flow.

## Writing-discipline rule (applies in every mode)

Inline uncertainty markers — `[unverified: …]`, TBD-with-meaning, "TODO: decide" — are never left in
narrative text or entity fields. Each becomes an `open-question` row with a status; the text references
`OQ-###`. The content gate (G-COMPLETE) flags leftovers.
