---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Follow-up Handoff Prompts — <project-name>

<!-- ONE phase-gate prompt per phase (PH-) plus situational prompts. Each phase prompt RESUMES from the
     prior phase's exit criteria, states the phase goal, gives bounded tasks with pass/fail, restates the
     invariants still in force, and ends at the exit gate. Replace every <placeholder> (G-HANDOFF).
     Reference entities by real ids. Generation class: Conditional (handoff to Claude Code).
     The BODIES of the project's `phase` and `situational` prompt rows (`PRT-`). Shape: references/prompt-templates.md. -->

## Phase-gate prompts

### → Enter Phase `PH-2` — <phase title>

Phase `PH-1` is complete and approved. Its exit criteria were: <restate PH-1 exit criteria>.

**Invariants still in force:** `INV-001..INV-00n` (`entity_query("invariant")`).

**Goal of `PH-2`:** <phase goal> (`entity_query("phase", id="PH-2")`).

**Tasks (bounded, pass/fail each). Work acceptance-criteria-first (failing test → implement → repeat):**
1. <task>. PASS = <observable>. FAIL = <observable>. Traces to `WBS-2.x`, `AC-0xx`.
2. <task>. PASS = <…>. FAIL = <…>.

**Before the exit gate, record through the tools (v4).** `audit_record` per `AC-` with the
full evidence chain (evidence + `verified_by` + `verification_method` + `against_commit`).
`progress_update` typed (`work-done`, `subject_id`, your `actor` string). `work_bind` per
commit. Finished work is claimed as **`Review`** (Implemented = verified, guarded). Then
`gate_run()` and `readiness_check("phase", "PH-2")`, and resolve every blocking failure.

**Exit gate:** <the PH-2 exit criteria>. When met, **STOP** and request review before `PH-3`.
Any deviation: `scope-change` row FIRST. Its `decision_ref` names the deciding `DEC-`/`ADR-`,
and its delta edges `scope_adds`/`scope_modifies`/`scope_removes` name the affected plan
rows. Add `amends` for a ruling (DEC-: full-row upsert, ADR-: supersede). After approval
apply the changes, RE-READ them, and set the `SC-` to Merged LAST. Ambiguity: an `OQ-`
(owner + due_by) + `[NEEDS-CLARIFICATION: OQ-NNN]` in place. Never assume. A durable
lesson: an `LL-` row (born Proposed, kind improve|sustain) + a `learned_from` edge. The
operator confirms, and only Approved lessons bind. A stubborn
readiness failure: ask the operator for a `WVR-` waiver. Never self-authored.

### → Enter Phase `PH-3` — <phase title>

<!-- Repeat the structure: resume from PH-2 exit, goal, bounded pass/fail tasks, invariants, exit gate. -->
Phase `PH-2` is complete and approved. Its exit criteria were: <…>.
...

## Situational prompts

<!-- Fill the ones the project needs; delete those it does not. Each references real paths. -->

### Fallback invocation
<!-- When a primary approach hits its trigger and a recorded fallback should be used. -->
`RISK-00x` trigger <observed signal> has occurred. Switch to the recorded fallback: <fallback>. Update
the affected decision (`DEC-/ADR-`) and risk status, then continue Phase `PH-x`.

### Fresh-session refresher
You are resuming **<project-name>** in a new session (or after a context clear/compaction).
Orient through the package, not from memory. `package_open("<package>")` returns a `resume`
block that carries the latest handoff and the three newest journal entries. Then `gate_run()`
(its `audit_evidence` reads each active criterion's latest verdict). For the last recorded
activity read those entries with `entity_query("progress-entry", ids=[...])`, never with a
bare `limit`. Rows come in id order and `limit` cuts from the lowest, so a limited read returns
the OLDEST rows. Never read `data/*.jsonl` to dodge a payload cap. **Cross-check git**:
`git log --oneline -15` against the recorded `work_bind` refs. Classify each unreferenced
commit by `git show --name-only`. Package-only writes cannot cite their own sha, so only
source-touching commits are candidates. Flag those, and do not invent verdicts for them.
Summarize the current phase/slice, the last completed `WBS-`, the invariants in force
(`entity_query("invariant")`), and any unrecorded work. Then await the next task. (The plugin's
`/tamheed:orient-resume` skill is the full version of this.)

### Invariant audit
Verify the implementation honors `INV-001..INV-00n`. Report any violation with `file:line` and a proposed
fix. Make no functional changes during the audit.

### Engine / dependency upgrade + baseline regen
A dependency (`DEP-00x`) is upgrading from <old> to <new>. Plan the upgrade, regenerate any golden
baselines that legitimately change, confirm invariants still hold, and record the change as an ADR.

### Bug triage
Given <symptom>, reproduce it and identify the failing `INV-`/`AC-`/`TEST-`. Propose the minimal fix
scoped to the current phase, and state the pass/fail that proves it fixed. Pause for approval before
large changes.

### Release prep
Run `readiness_check("package")`. Resolve every blocking failure (pre-approval
decisions/ADRs, ACs not latest-Met, open defects, undischarged risks). Confirm the
`human_required` gates with the operator, recording each confirmation via
`progress_update`. Then `gate_run()`, `export_html()`, and release notes from
`entity_query("progress-entry")`. (The plugin's `/tamheed:release-close-out` skill is the
full version of this.)

### Deviation ADR
A change departs from the approved plan. Upsert the `adr` row (status Proposed) capturing
context, decision, consequences, and rejected alternatives, then the `scope-change` row
with `decision_ref` pointing at it. STOP for approval before implementing.

### Status report
`export_html()` and read `review.html`: overview chips, execution progress, phase
readiness. The report is generated, never hand-maintained.

### Acceptance audit (at each phase gate)
`audit_record` a verdict (Met / Partial / Not-met / Pending) with the evidence chain
(`TEST-`/commit/CI/golden) for every `AC-` this phase covers. Call out Partial/Not-met
honestly with a reason. Never rubber-stamp. Gate G-PROGRESS checks coverage. Verdicts
APPEND: corrections are new rows, and only the latest counts.

### Phase-exit summary
Write a short phase-exit summary: per-item verdicts vs the phase's exit/acceptance criteria, decisions
taken, and any plan deviations (→ ADR). Add engineering notes to carry into the next phase, and a
go/no-go recommendation. STOP for approval before starting the next phase.

### Spike / experiment report
Run a planned `EXP-`/`POC-` (one at a time, timeboxed). A subagent is a good fit for an isolated
experiment. On finish, write its result. The result is the verdict (Validated / Invalidated /
Inconclusive) vs the pre-committed metric + threshold. Add measurements, surprises/caveats, and
implications carried onward. Update the deciding `DEC-`/`HYP-`. Pause for review before acting on
the result.

### Defect log
For a reported bug: reproduce it as a minimal failing test. **`entity_upsert` the `defect`
row (`DEF-`, lifecycle_status Open, honest severity, `found_in` the phase/slice) BEFORE
fixing.** Fix to green.
`work_bind` the fix commit to the `DEF-` and affected `AC-`, and flip the DEF- status.
(The plugin's `/tamheed:defect-triage` skill is the full version of this.)

### Phase 1 — baseline (seed ADRs from the architecture)
Start Phase 1: seed the `adr` rows from the architecture decisions (status Proposed). Propose the
package scaffolding + CI skeleton, and STOP before writing implementation code.
