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
     PROJECT prompt files in `<package>/prompts/` (purpose-named). Shape: references/prompt-templates.md. -->

## Phase-gate prompts

### → Enter Phase `PH-2` — <phase title>

Phase `PH-1` is complete and approved; its exit criteria were: <restate PH-1 exit criteria>.

**Invariants still in force:** `INV-001..INV-00n` (`entity_query("invariant")`).

**Goal of `PH-2`:** <phase goal> (`entity_query("phase", id="PH-2")`).

**Tasks (bounded; pass/fail each) — work acceptance-criteria-first (failing test → implement → repeat):**
1. <task> — PASS = <observable>; FAIL = <observable>. Traces to `WBS-2.x`, `AC-0xx`.
2. <task> — PASS = <…>; FAIL = <…>.

**Before the exit gate — record through the tools (v4):** `audit_record` per `AC-` with the
full evidence chain (evidence + `verified_by` + `verification_method` + `against_commit`),
`progress_update` typed (`work-done`, `subject_id`, your `actor` string), `work_bind` per
commit, finished work claimed as **`Review`** (Implemented = verified, guarded), then
`gate_run()` and `readiness_check("phase", "PH-2")` — resolve every blocking failure.

**Exit gate:** <the PH-2 exit criteria>. When met, **STOP** and request review before `PH-3`.
Any deviation: `scope-change` row FIRST (`decision_ref` → the deciding `DEC-`/`ADR-`,
delta edges `scope_adds`/`scope_modifies`/`scope_removes` naming the affected rows;
after approval apply the changes and set the `SC-` to Merged). Ambiguity: an `OQ-`
(owner + due_by) + `[NEEDS-CLARIFICATION: OQ-NNN]` in place — never assume. A stubborn
readiness failure: ask the operator for a `WVR-` waiver — never self-authored.

### → Enter Phase `PH-3` — <phase title>

<!-- Repeat the structure: resume from PH-2 exit, goal, bounded pass/fail tasks, invariants, exit gate. -->
Phase `PH-2` is complete and approved; its exit criteria were: <…>.
...

## Situational prompts

<!-- Fill the ones the project needs; delete those it does not. Each references real paths. -->

### Fallback invocation
<!-- When a primary approach hits its trigger and a recorded fallback should be used. -->
`RISK-00x` trigger <observed signal> has occurred. Switch to the recorded fallback: <fallback>. Update
the affected decision (`DEC-/ADR-`) and risk status, then continue Phase `PH-x`.

### Fresh-session refresher
You are resuming **<project-name>** in a new session (or after a context clear/compaction).
Orient through the package, not from memory: `package_open("<package>")`, `gate_run()`, then
`entity_query("progress-entry", limit=10)` and `entity_query("audit-verdict", limit=10)` for
the last recorded activity. **Cross-check git**: `git log --oneline -15` against the recorded
`work_bind` refs — list any package-relevant commits with no recorded binding and flag them;
do not invent verdicts for them. Summarize current phase/slice, last completed `WBS-`, the
invariants in force (`entity_query("invariant")`), and any unrecorded work. Then await the
next task. (The emitted `<package>/prompts/orient-resume.md` is the full version of this.)

### Invariant audit
Verify the implementation honors `INV-001..INV-00n`. Report any violation with `file:line` and a proposed
fix. Make no functional changes during the audit.

### Engine / dependency upgrade + baseline regen
A dependency (`DEP-00x`) is upgrading from <old> to <new>. Plan the upgrade, regenerate any golden
baselines that legitimately change, confirm invariants still hold, and record the change as an ADR.

### Bug triage
Given <symptom>, reproduce it, identify the failing `INV-`/`AC-`/`TEST-`, propose the minimal fix scoped to
the current phase, and state the pass/fail that proves it fixed. Pause for approval before large changes.

### Release prep
Run `readiness_check("package")` — resolve every blocking failure (pre-approval
decisions/ADRs, ACs not latest-Met, open defects, undischarged risks) and confirm the
`human_required` gates with the operator, recording each confirmation via
`progress_update`. Then `gate_run()`, `export_html()`, and release notes from
`entity_query("progress-entry")`. (The emitted `<package>/prompts/release-close-out.md`
is the full version of this.)

### Deviation ADR
A change departs from the approved plan. Upsert the `adr` row (status Proposed) capturing
context, decision, consequences, and rejected alternatives, then the `scope-change` row
with `decision_ref` pointing at it. STOP for approval before implementing.

### Status report
`export_html()` and read `review.html` — overview chips, execution progress, phase
readiness. The report is generated, never hand-maintained.

### Acceptance audit (at each phase gate)
`audit_record` a verdict (Met / Partial / Not-met / Pending) with the evidence chain
(`TEST-`/commit/CI/golden) for every `AC-` this phase covers. Call out Partial/Not-met
honestly with a reason — never rubber-stamp (gate G-PROGRESS checks coverage; verdicts
APPEND — corrections are new rows, and only the latest counts).

### Phase-exit summary
Write a short phase-exit summary: per-item verdicts vs the phase's exit/acceptance criteria, decisions
taken, any plan deviations (→ ADR), engineering notes to carry into the next phase, and a go/no-go
recommendation. STOP for approval before starting the next phase.

### Spike / experiment report
Run a planned `EXP-`/`POC-` (one at a time, timeboxed; a subagent is a good fit for an isolated experiment).
On finish, write its result: the verdict (Validated / Invalidated / Inconclusive) vs the
pre-committed metric + threshold, measurements, surprises/caveats, and implications carried forward. Update the
deciding `DEC-`/`HYP-`. Pause for review before acting on the result.

### Defect log
For a reported bug: reproduce it as a minimal failing test, **`entity_upsert` the `defect`
row (`DEF-`, lifecycle_status Open, honest severity, `found_in` the phase/slice) BEFORE
fixing**, fix to green,
`work_bind` the fix commit to the `DEF-` and affected `AC-`, and flip the DEF- status.
(The emitted `<package>/prompts/defect-triage.md` is the full version of this.)

### Phase 1 — baseline (seed ADRs from the architecture)
Begin Phase 1: seed the `adr` rows from the architecture decisions (status Proposed),
propose the package scaffolding + CI skeleton, and STOP before writing implementation code.
