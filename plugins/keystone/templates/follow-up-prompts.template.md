---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Follow-up Handoff Prompts — <project-name>

<!-- ONE phase-gate prompt per phase (PH-) plus situational prompts. Each phase prompt RESUMES from the
     prior phase's exit criteria, states the phase goal, gives bounded tasks with PASS/FAIL, restates the
     invariants still in force, and ends at the exit gate. Replace every <placeholder> (G-HANDOFF).
     Reference real artifact paths. Generation class: Conditional (handoff to a coding agent).
     Lives at: handoff/follow-up-prompts.md. Shape: references/prompt-templates.md. -->

## Phase-gate prompts

### → Enter Phase `PH-2` — <phase title>

Phase `PH-1` is complete and approved; its exit criteria were: <restate PH-1 exit criteria>.

**Invariants still in force:** `INV-001..INV-00n` (see [invariant register](../requirements/invariant-register.md)).

**Goal of `PH-2`:** <phase goal> (see [roadmap](../planning/roadmap.md)).

**Tasks (bounded; PASS/FAIL each):**
1. <task> — PASS = <observable>; FAIL = <observable>. Traces to `WBS-2.x`, `AC-0xx`.
2. <task> — PASS = <…>; FAIL = <…>.

**Exit gate:** <the PH-2 exit criteria>. When met, **STOP** and request review before `PH-3`.
Record any deviation as an ADR.

### → Enter Phase `PH-3` — <phase title>

<!-- Repeat the structure: resume from PH-2 exit, goal, bounded PASS/FAIL tasks, invariants, exit gate. -->
Phase `PH-2` is complete and approved; its exit criteria were: <…>.
...

## Situational prompts

<!-- Fill the ones the project needs; delete those it does not. Each references real paths. -->

### Fallback invocation
<!-- When a primary approach hits its trigger and a recorded fallback should be used. -->
`RISK-00x` trigger <observed signal> has occurred. Switch to the recorded fallback: <fallback>. Update
the affected decision (`DEC-/ADR-`) and risk status, then continue Phase `PH-x`.

### Fresh-session refresher
You are resuming **<project-name>** in a new session. Re-read [charter](../00-charter.md),
[roadmap](../planning/roadmap.md), [invariant register](../requirements/invariant-register.md), and the
latest [status report](../progress/status-report.md). Summarize current phase, last completed `WBS-`, and
the invariants in force. Then await the next task.

### Invariant audit
Verify the implementation honors `INV-001..INV-00n`. Report any violation with `file:line` and a proposed
fix. Make no functional changes during the audit.

### Engine / dependency upgrade + baseline regen
A dependency (`DEP-00x`) is upgrading from <old> to <new>. Plan the upgrade, regenerate any golden
baselines that legitimately change, confirm invariants still hold, and record the change as an ADR.

### Bug triage
Given <symptom>, reproduce it, identify the failing `INV-`/`AC-`/`TEST-`, propose the minimal fix scoped to
the current phase, and state the PASS/FAIL that proves it fixed. Pause for approval before large changes.

### Release prep
Confirm Definition of Done (`../execution/definition-of-done.md`) for the release scope, re-run the quality
gates, ensure the readiness report is **go**, and prepare release notes from the progress log.

### Deviation ADR
A change departs from the approved plan. Draft `adr-NNNN-<title>.md` (status Proposed) capturing context,
the decision, consequences, and rejected alternatives. STOP for approval before implementing.

### Status report
Regenerate `../progress/status-report.md` from current state: phase, milestones, completed/in-progress
work, blockers, active risks, and decisions since the last report.
