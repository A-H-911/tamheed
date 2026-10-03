---
name: drift-register
description: >-
  Invoke when work happened without recording (a rushed session, a hotfix, an agent that forgot).
  It registers every piece of drift between reality and the package.
disable-model-invocation: true
argument-hint: "[package]"
---

# Drift register: everything the package does not know yet

Invoke this (`/tamheed:drift-register`) when work happened without recording (a rushed session, a
hotfix, an agent that forgot) to bring `<package>` back to truth.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Register every piece of drift between reality and the `<package>` Tamheed package:

1. `package_open("<package>")` if not already open.
2. Enumerate what the package does not know: `git log --oneline -20` vs the recorded
   `work_bind` refs, each unreferenced commit classified by `git show --name-only`
   (`tamheed:package-writes` §9). A commit whose whole content is a package write is
   unbound by rule and is not an orphan. The close-out's last commit is one. List the
   work done, the decisions taken and the problems found, ALL of them, before writing
   anything.
3. Classify and register each item, in this order:
   - a bug that exists → `defect` row (`DEF-`, status Open, `found_in`).
   - needed work that is out of scope → `deferred-work` row (`DW-`) with severity and
     an activation trigger.
   - any deviation from the approved plan (scope grew, shrank, or changed shape) →
     `scope-change` row (`SC-`) FIRST. Its lifecycle is Proposed → Approved → Merged,
     and its `decision_ref` names the deciding `DEC-`/`ADR-`. Upsert the decision row
     (status Proposed) if none exists. Add `scope_adds`/`scope_modifies`/
     `scope_removes` delta edges to the affected plan rows. Add an `amends` edge
     when the change carves an exception out of a RULING (`DEC-` merges by
     full-row upsert, `ADR-` by supersession). STOP for approval. Only
     after it apply the row changes, RE-READ them, and set the `SC-` Merged
     LAST (the scope-changes-merged advisory flags Approved-never-Merged).
   - work simply unrecorded → `progress_update` per unit (event_type "work-done",
     actor "agent:<session>"). A WRONG earlier entry is compensated by a new event
     with `corrects: "<PE-x>"`, because journals are never edited. Add `work_bind` per
     orphan commit, and `audit_record` for any criterion actually verified (evidence plus
     `verified_by`/`verification_method`/`against_commit`).
   - a requirement created during execution → wire its trace edges (`derives_from` /
     `implements` / `tests`) NOW. `work_bind` stamps commits, it does NOT wire
     traceability (`gate_run`'s `requirements_unwired` advisory lists the strays).
   - something durable was learned (a mistake's root fix, a practice that worked) →
     a `lesson` row. The row is `LL-`, born Proposed, kind improve|sustain. The
     statement opens with its rule, plus the impacts. Add a `learned_from` edge to the source
     (`DEF-`/`DEC-`/`RISK-`/`SL-`/`WBS-`/`PE-`). The operator confirms later. Only
     Approved lessons bind.
   - genuine ambiguity about what happened or what was intended → an `OQ-` row
     (owner + due_by) and a `[NEEDS-CLARIFICATION: OQ-NNN]` marker at the exact
     ambiguous spot. Never a guessed record.
4. `gate_run()` and `readiness_check("package")`. Report what was registered and
   what the package now says is blocking.
5. `package_close()` and remind the operator to commit `data/`.
