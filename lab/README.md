# The Tamheed lab — a permanent, deliberately imperfect test project

This directory is a **controlled mock project** (plan 031): a tiny CLI task tracker whose
brief and seed code are deliberately flawed so that **every v4 mechanism has a reason to
fire** during a full Understand → Explore → Plan → execute run. It exists so releases can
be exercised against a model-in-the-loop, full-lifecycle scenario — not only unit suites.

## What is seeded, and which mechanism it forces

| Seeded flaw | Where | The mechanism it forces |
|---|---|---|
| An ambiguous requirement ("recurring tasks… somehow") | `brief.md` | `OQ-` row + `[NEEDS-CLARIFICATION: OQ-NNN]` marker (G-COMPLETE-validated) |
| A storage-engine fork the brief leaves open | `brief.md` | `DEC-` → one-way-door test → `ADR-` promotion (+ the `decisions-look-architectural` nag if skipped) |
| An off-by-one bug in `overdue()` | `seed/tracker.py` | `DEF-` row (honest severity) BEFORE the fix; evidence-chained `audit_record` |
| A time-dependent flaky test | `seed/test_tracker.py` | a defect is a defect (the Google flaky-test doctrine) — severity judgment + quarantine-or-fix |
| A mid-execution scope surprise (the "export" ask in the brief's postscript) | `brief.md` | `SC-` Proposed + `scope_modifies` edges → operator approval → apply → Merged |
| A cosmetic leftover (typo in the help text) | `seed/tracker.py` | low-severity defect: `defects-minor` advisory + an operator-approved `WVR-` waiver |
| A slice the operator closes early | scenario step 8 | the readiness refusal, then the operator-words `force` → typed `forced-override` audit |

## How a release exercises the lab

The scripted scenario is `scenario.md`. The resulting package lives at
`evals/sample-results/lab-tracker/package` and is **eval-tier**: model-in-the-loop output
cannot be byte-deterministic, so it is validated by `gate_run` + `readiness_check` (the
eval runner's checks), never byte-compared like the goldens.

## The honesty limit (read this before citing the lab as proof)

The lab proves that every v4 mechanism **fires** under a real agent. It cannot prove
**autonomous drift discharge** — a delegated agent defers to its parent, and headless
permission modes block the MCP tool path (the findings_15/16 instrument lesson). The
only valid instrument for that remains an interactive fresh session driven by a human
operator on a real repo.
