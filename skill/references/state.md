# State, resumption, and updates

Keystone persists normalized state so long, interrupted, or evolving work never loses context or re-asks
settled questions.

## `keystone-state.json`

Conforms to `../schemas/keystone-state.schema.json`. Holds: schema/skill version; `project_profile`; the
raw input + provenance; all registers (requirements, constraints, invariants, assumptions, dependencies,
open questions, decisions, risks, hypotheses, experiments); scope; the selected artifact set; per-stage
status (`not-started`/`in-progress`/`blocked`/`done`) and the last completed stage; the traceability rows;
and a change log. It is **machine-owned** — humans edit the rendered artifacts, and Keystone reconciles.

## Resume

On `resume`: load state, list completed vs pending stages, detect any human edits to artifacts since last
run (compare to what state expects), reconcile (human edits win; record the reconciliation), and continue
from the last incomplete stage. Never silently overwrite a human edit.

## Update cycles (Stage 21)

When new decisions/progress/feedback arrive:
1. Apply the change to the owning register (e.g. flip `DEC-007` Proposed→Approved, or log progress).
2. Re-derive dependent artifacts (traceability, roadmap rollups, readiness, status report).
3. Bump versions per `governance.md`; if an item is replaced, create the successor and set
   `supersedes`/`superseded_by` on both.
4. Re-run affected gates (at least G-TRACE, G-IDS, G-DEC-STATUS).

## Consistency invariants

- State and rendered artifacts must agree after any operation; a mismatch is a bug to repair, not ignore.
- Derived artifacts are always reproducible from state + sources; if you can't regenerate one, it wasn't
  truly derived — fix its inputs.
- Every state mutation appends to the change log with who/what/when so the package's history is auditable.
