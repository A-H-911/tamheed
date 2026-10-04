---
name: defect-triage
description: >-
  Invoke when a bug is reported or discovered during execution. The defect row is registered FIRST,
  then the fix, the evidence, the binding and the status flip.
disable-model-invocation: true
argument-hint: "[package]"
---

# Defect triage: register FIRST, then fix

Invoke this (`/tamheed:defect-triage`) when a bug is reported or discovered during execution of
`<package>`.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Triage a defect against the `<package>` Tamheed package. The registration comes
BEFORE the fix, so the record survives even if the session dies mid-fix:

1. `package_open("<package>")` if not already open.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="defect-triage")`. Each carries what is true of this project for this ceremony.
2. Reproduce the symptom as a minimal failing test. No fix yet.
3. Register it: `entity_upsert([{"type": "defect", "id": "DEF-<next>", "title":
   "<symptom>", "severity": "critical|high|medium|low", "lifecycle_status": "Open",
   "found_in": "<PH-x or SL-x>"}])`, a full row. Check the next free id with
   `entity_query("defect")`. Severity is honest impact: critical/high BLOCK
   readiness, medium/low only surface as the defects-minor advisory. Never pick a
   severity to pass a gate.
4. Identify what it touches: the failing `FR-`/`INV-`/`AC-` via `trace_query`. If an
   invariant is at stake, say so loudly.
5. Fix to green. Scope stays minimal. If the real fix needs out-of-scope work, that
   remainder becomes a `deferred-work` row with an activation trigger, not silent
   extra scope.
6. Close the loop: `audit_record` any affected `AC-` with the test as evidence plus
   `verified_by`, `verification_method`, and `against_commit` (the fix commit).
   `work_bind` the fix commit to the `DEF-` and the `AC-`. Flip the `DEF-` status
   (full-row upsert), and re-read its prose in the same write. A closed status over
   sentences that still read as open work invites the next session to re-do it.
   `progress_update` the whole event (event_type "work-done", subject_id the `DEF-`
   id, actor "agent:<session>"). The operator may have RULED on something while the
   defect was open (a trade-off accepted, a fix rejected, a behaviour kept on purpose).
   That ruling is a `decision` row (`DEC-`, `relates_to` the `DEF-`). It is never prose
   inside the closed defect, where no decision sweep will ever find it.
7. Did this defect teach a durable lesson (a class of mistake, not this one
   instance)? Record a `lesson` row (`LL-`, born Proposed, kind improve, the
   statement opening with its rule) + a `learned_from` edge to the `DEF-`. The
   operator confirms later.
8. `gate_run()`: report the verdict delta.
