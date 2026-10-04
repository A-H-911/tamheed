---
name: phase-close
description: >-
  Invoke to close a phase deliberately. The phase-scope readiness failures are resolved or waived on
  the operator's words, then expired waivers, milestones, human gates, then the guarded Implemented
  transition.
disable-model-invocation: true
argument-hint: "[package]"
---

# Phase close: the guarded exit, done deliberately

Invoke this (`/tamheed:phase-close`) to close a phase of `<package>` (semi-auto). It is
distinct from slice-review: this is the phase-level exit with the guarded transition at the
end.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Close phase `<PH-x>` of the `<package>` Tamheed package:

1. `package_open("<package>")` if not already open.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="phase-close")`. Each carries what is true of this project for this ceremony.
2. `readiness_check("phase", "<PH-x>")`. Resolve every blocking failure. The failures
   are ACs of the phase's slices not latest-Met, slices/work items still open, and open
   critical/high defects. Review counts as open, because done-claimed is not verified. A
   phase with no `WBS-` row at all reads `wbs-done` indeterminate. A recorded
   omission of the family does not stand in for a row at this scope
   (`tamheed:slice-review`). Medium/low defects only surface as the defects-minor
   advisory. Never downgrade severity to pass. Each resolution is recorded, never
   narrated away. Record verdicts with evidence, statuses via full-row upserts, and
   deferrals/scope via `DW-`/`SC-` rows. Record a named-rule exception via a `WVR-`
   waiver (operator-approved only, reported as "waived").
3. **Expired waivers** touching this phase (`expired_waivers` in the readiness
   report): resolve the underlying item. Or ask the operator for fresh words for a new
   `WVR-` (or a full-row upsert with a new `expires`). Never carry one silently
   across a phase boundary.
4. Milestones of the phase (`entity_query("milestone")`): roadmap labels only, with no
   lifecycle, never a gate. Report which read as reached. An unreached one is either
   a conversation with the operator or an explicit `scope-change`, never a status
   flip.
5. `human_required` gates for the phase: read each `GATE-` definition to the operator
   and take their explicit decision. Upsert the gate row's `outcome`
   (Go/Hold/Redirect/Kill), and record it as a `progress_update` (event_type
   "gate-decision", subject_id the `GATE-` id).
6. The transition: upsert the phase full-row with `lifecycle_status: "Implemented"`.
   If the guard refuses, the blockers are real. Resolve them, or for one stubborn
   item ask the operator for a `WVR-` waiver. `"force": true` overrides the whole
   transition and exists ONLY for the operator's explicit words. If forced, the
   server writes the FORCED audit row itself.
7. `gate_run()`, then a closing `progress_update` summarizing the phase (event_type
   "transition", subject_id "<PH-x>", actor "agent:<session>"), THEN `export_html()`.
   The phase readiness panel should now show the exit, and the page carries the
   closing entry (the export follows the last write). Then `package_close()` and
   commit `data/` with the page.
