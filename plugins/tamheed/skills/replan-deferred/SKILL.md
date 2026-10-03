---
name: replan-deferred
description: >-
  Invoke when deferred-work activation triggers may have fired. Judge each trigger's words against
  current state, propose the scope change, STOP for approval, then activate in order.
disable-model-invocation: true
argument-hint: "[package]"
---

# Replan deferred work: activate what fired

Invoke this (`/tamheed:replan-deferred`) when deferred-work triggers may have fired on `<package>`
(semi-auto: the new scope stops for your approval).

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Review and activate deferred work in the `<package>` Tamheed package:

1. `package_open("<package>")` if not already open.
2. `entity_query("deferred-work")`. For each Open/Scheduled row, judge its
   `activation_trigger` against current state. The triggers are prose, and that judgment
   is the point of this prompt. Report: fired / not fired / unclear, with reasons.
   For every FIRED, say **which words of the trigger** you are matching and what in
   the current state matches them. A row with no progress entries because it was never
   started is not a gap to fill.
3. For each item to activate: the `scope-change` row FIRST, status Proposed. Its
   `decision_ref` names the deciding `DEC-`/`ADR-`. Upsert a Proposed decision if
   none exists. Give it `scope_adds`/`scope_modifies` delta edges to the rows the
   activation will touch. Use an `amends` edge instead when the activation carves an
   exception out of a `DEC-`/`ADR-` ruling. The ruling row is not a plan row.
   **STOP for operator approval of the proposed scope.**
4. After approval, apply each `SC-` IN THIS ORDER, then set it Merged:
   - flip the `DW-` status to Activated (full-row upsert).
   - upsert the `wbs-item`/`slice` rows the work becomes, with `phase_id`/`slice_id`.
   - wire the trace edges (`implements`/`relates_to`) so G-TRACE sees the linkage. Add a
     `carries` edge from each new `wbs-item` to the `DW-` row (v5). The carrier is what
     `deferred-work-carried` reads. When every carrier is Implemented the row is Done.
5. `gate_run()`: the new scope must not break the gates. Report what was
   activated before executing any of it.
