---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Progress Log — <project-name>

<!-- An append-only, chronological record of what happened: work completed, decisions taken, deviations,
     blockers raised/cleared. Newest entries at the top. Continuous artifact — updated each cycle.
     Generation class: Continuous (long execution horizon). Lives at: progress/progress-log.md.
     Append; do not rewrite past entries (correct via a new entry). -->

## How to use

- One entry per working session or meaningful change. Keep entries short and factual.
- Reference IDs (`WBS-/DEC-/RISK-/PH-/MS-`) so entries link to the registers.
- Record deviations from the plan and the ADR that captures them.

## Entries (newest first)

### <YYYY-MM-DD> — <short headline>
- **Done:** <what was completed; WBS-x.y, FR-00x>
- **Decisions:** <DEC-/ADR- taken or status changes, e.g. DEC-007 Proposed→Approved>
- **Deviations:** <any departure from plan → ADR-000x>
- **Blockers:** <new/cleared; OQ-/RISK->
- **Next:** <immediate next step>

### <YYYY-MM-DD> — <short headline>
- **Done:** <…>
- **Decisions:** <…>
- **Deviations:** <…>
- **Blockers:** <…>
- **Next:** <…>

<!-- The status report (status-report.md) is a regenerated SNAPSHOT; this log is the running HISTORY. -->
