---
name: loop-iteration
description: >-
  Invoke as the repeated prompt of an unattended loop (an in-session loop or an external harness).
  One fully-auto pass over one work item, ending with the machine-parseable ITERATION line.
disable-model-invocation: true
argument-hint: "[package]"
---

# Loop iteration: one fully-auto pass, machine-parseable end

Invoke this (`/tamheed:loop-iteration`) as the repeated prompt of an unattended loop over
`<package>`. An in-session loop or an external harness invokes it per iteration, and both parse
the ITERATION block. Read the loop guard first, `${CLAUDE_PLUGIN_ROOT}/skills/loop-guard/SKILL.md`.
Its stop conditions override everything here.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Execute ONE iteration against the `<package>` Tamheed package, no pauses:

1. Orient: `server_info` → `package_open("<package>")` → `gate_run()` → the git
   cross-check (`git log --oneline -10`). The `resume` block of `package_open` names the
   latest handoff and the three newest journal entries. Never a read cut by `limit`, which
   returns the OLDEST rows. Classify each unreferenced commit by `git show --name-only`
   (`tamheed:package-writes` §9). A commit whose whole content is a package write is
   unbound by rule and is NEVER bound here. The close-out's last commit, a bind with the
   exported page, is one. Only a commit that touches source or tests is drift. Register
   it via the drift-register steps, `${CLAUDE_PLUGIN_ROOT}/skills/drift-register/SKILL.md`,
   before new work.
2. Check the brakes: evaluate every loop-guard stop condition. Any of them true →
   record the reason as a final `progress_update`, `package_close()`, and emit the
   ITERATION block with `stop=<reason>`. Do nothing else.
3. Pick work: the first open `wbs-item` (`entity_query("wbs-item")`) in phase/slice
   order. No open items → `stop=backlog-empty`.
4. Execute acceptance-criteria-first: failing test → implement → green. Bounded to
   this one work item.
5. Sync (the recording obligations, no exceptions): `progress_update` per unit
   (event_type "work-done", subject_id the `WBS-`, actor "agent:<session>").
   `audit_record` per verified `AC-` with evidence plus `verified_by: "agent"`,
   `verification_method: "auto-test"`, `against_commit`. `work_bind` the commit.
   Discovered defects → `DEF-` rows. Out-of-scope finds → `DW-` rows. A needed
   `scope-change` is NOT yours to make. That is a stop condition.
6. Close: set the finished `wbs-item` to `lifecycle_status: "Review"` (done-claimed,
   because `Implemented` is the verified state, and readiness counts Review as open). If
   the slice's criteria all look Met, `readiness_check("slice", "<SL-x>")`. A blocking
   failure is a stop condition (force or a waiver needs a human). `ready: false` with NO
   blocking failure means a blocking rule could not discriminate. `indeterminate` names
   it (an empty slice: no ACs, no work items). Record the rows the slice lacks, never
   report it as a failure. Then `gate_run()` and `package_close()`.
7. End with EXACTLY this block (the loop driver parses it, one line, fixed order):

   `ITERATION: wbs=<WBS-x|none> slice=<SL-x|none> acs_moved=<n> gate=<pass|fail> ready=<true|false|n/a> stop=<none|reason> lessons_pending=<n>`
