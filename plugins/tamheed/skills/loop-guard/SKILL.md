---
name: loop-guard
description: >-
  Invoke to read the brake for fully-auto execution: the stop conditions an unattended loop
  evaluates every iteration. Scope decisions and forced transitions always need a human.
disable-model-invocation: true
argument-hint: "[package]"
---

# Loop guard: the brake for fully-auto execution

Keep this (`/tamheed:loop-guard`) beside `/tamheed:loop-iteration` when running `<package>`
unattended. The loop stops the moment ANY condition below is true. Scope decisions and forced
transitions always need a human.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Stop conditions (evaluate at the start of every iteration and before closing a slice):

1. `gate_run()` verdict degraded vs the previous iteration (a gate that passed now
   fails).
2. The same `AC-` records Not-met twice in a row. The loop is not converging on it.
3. A `scope-change` row would be required (something must be deferred, cancelled, or
   expanded). Scope is a human decision. Register NOTHING and stop.
4. `readiness_check` reports a blocking failure at a slice/phase close. Both outs
   are the operator's alone: `"force": true` for the whole transition, a `WVR-`
   waiver for a single named rule. So the loop stops and surfaces the failing rules
   verbatim.
5. Open `DEF-` count grew by more than 2 in one iteration. The code is fighting back.
6. Two consecutive iterations yielded nothing worth a `progress_update`.
7. Any store error (locked, stale tree, refused batch). Never retry around the
   single-writer or stale-tree guards.

Standing rule, not a stop condition: **the loop NEVER carries
`"operator_confirm": true`**. Recording lessons (born Proposed) is encouraged.
Approving or promoting them is the operator's interview, and the store refuses the
transition without their flag in every mode. Proposed lessons accumulate, and the
ITERATION line's `lessons_pending` count keeps the queue visible.

On stop: record the reason as a final `progress_update` (event_type "escalation",
the one write that is always allowed). Then `package_close()`, and emit the
ITERATION block with `stop=<reason>`
plus a short verbatim report of what triggered it. The operator restarts the loop after
resolving. Never restart yourself.
