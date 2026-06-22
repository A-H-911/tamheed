---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
id: EXP-NNN
---

# EXP-NNN — <experiment title>

<!-- A bounded, timeboxed experiment to test a hypothesis with an explicit PASS/FAIL criterion.
     One experiment per file (or per section if collected). Identified EXP-NNN (governance.md).
     Generation class: Conditional (genuine technical uncertainty). Lives at: experiments/. -->

## Goal

<!-- What this experiment must determine, and the decision/hypothesis it serves. -->
Determine <question>. Tests `HYP-00x`; informs `DEC-00x`.

## Method

<!-- The procedure: setup, variables, what is held constant, environment, sample/inputs, steps.
     Reproducible enough that another agent could run it. -->
1. <setup / environment / pinned versions>
2. <steps>
3. <what is measured and how>

## PASS / FAIL criteria

<!-- The decisive, pre-committed thresholds. Define BEFORE running to avoid post-hoc rationalization. -->
- **PASS if:** <measurable condition, e.g. p95 latency < 200 ms across 3 runs>.
- **FAIL if:** <measurable condition>.

## Timebox

<!-- The maximum effort before stopping and deciding with what we have. -->
<e.g. 1 day; stop and report even if inconclusive>

## Result

<!-- Fill after running. -->
- **Outcome:** <PASS | FAIL | Inconclusive>
- **Evidence:** <numbers, logs, artifact links>
- **Surprises / caveats:** <what was unexpected; the limits of what this experiment proves>
- **Decision impact:** <how this changes DEC-/ADR-/RISK->
- **Implications carried forward:** <what later phases must do because of this result>
- **Date run:** <YYYY-MM-DD>
