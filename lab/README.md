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
eval runner's checks), never byte-compared like the goldens. Later releases add
**continuation beats** (10: lessons, 11: promotion, 12: paging + `amends` + `package_verify`
+ the server-only refusal, 13: the edge retire + the three-bucket audit split, 14: the
`entity_export` read for committed scripts + the paste guard, 15: the advisor-audit
mechanisms — stale-tree rollback, born-Implemented refusal + force, scoped indeterminate,
whole-rule waiver, omission revision, CSV defusing, the note's skill screen; 16: the
findings_25 mechanisms — the dead holder's lock observed and unlocked, the live holder's
refused, the legible reads (`server_info(detail)`, `omitted_columns`/`matched`, rule
`population`), the phantom id caught by `prose-ids-resolve`, the partial export and its
digest, the retired CSV removed, the stock prompts refreshed; 17: the findings_26
mechanisms — the lost paragraph reported as a length drop, the half-finished supersession
that keeps binding, the two refused unattended retirements and the engine's own retirement
on the operator's word, the backticked phantom reported inert, the open-ended blanket
waiver named, the empty family that measured nothing until its omission was recorded, the
review page that says whether it is current, the completed hand-merge that stops lagging;
18: the findings_27 mechanisms — the registry synced for a new family, the missing function
recorded as feedback instead of scripted, confirmed and exported and reported on the operator's
word, the refused unattended confirmation and the refused rewrite under the operator's own name,
the local tool that exists only on that word, the by-hand lesson retirement the engine journals
and the forged engine row refused on both caller paths, the formula's variable names that trip
no list; 19: the findings_28 mechanisms — the phantom id in the project's own kickoff prompt
reported amber and made inert by backticks, the token census that counts every occurrence, the
go/no-go verdict that lands only on the operator's word — a string never attests — and the
engine's own witness of it, the one-token substitute that touches nothing else and the glued,
immutable and mixed substitutes refused, the review page's Readiness and Feedback sections;
20: the findings_29 mechanisms — the reported request closed by the partial-row disposition
recipe and journaled as bookkeeping that claims no word, the readiness advisory and the handoff
warning that fall silent with it, the MVP definition written and read back beside every other
header column, the current verdict re-sent unattended and refused by the presence check, the
prefix repair that lands once and is refused on the re-run, the partial row whose omitted
column is preserved and the sent drifted one refused; 21: the findings_30 mechanisms — the
empty slice that reads not ready and names the two rules that could not discriminate, made
ready by one bound work item and one criterion with a Met verdict, the recorded omission read
back as a deliberate zero, the pointer warning that says whether it rebuilt or wrote nothing,
the empty unanswered fold that says it is empty, and the `expect_unchanged` that names a
column the item does not carry refused as asserting nothing)
run as incremental real-agent sessions against the recorded package — the fixture is regenerated
by continuation, not from scratch.

## The honesty limit (read this before citing the lab as proof)

The lab proves that every v4 mechanism **fires** under a real agent. It cannot prove
**autonomous drift discharge** — a delegated agent defers to its parent, and headless
permission modes block the MCP tool path (the findings_15/16 instrument lesson). The
only valid instrument for that remains an interactive fresh session driven by a human
operator on a real repo.

A second, smaller limit: `handoff_emit` writes machine-specific absolute paths (the
resolved server script and package root in `.mcp.json` for standalone installs, the
package root in the `CLAUDE.md` note) — by design, so the executor host can find the
server. An emitted target is therefore never committed as a fixture: beats emit to a
scratch target and **quote the note verbatim in their evidence report** (beats 14 and 15
did), which is the durable record of what was emitted.
