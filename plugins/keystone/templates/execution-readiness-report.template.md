---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Execution-Readiness Report — <project-name>

<!-- The Stage 22 go/no-go. Runs the quality gates and reports per-gate results, open items, and
     residual risks. READINESS RULE: a package is execution-ready only when every CRITICAL gate passes
     and every WARN gate is passing or has an accepted, recorded exception. NEVER report "ready" with a
     Critical gate failing. Generation class: Always. Lives at: handoff/execution-readiness-report.md. -->

## Verdict

> **<GO | NO-GO>** — <one-line justification>

| | |
|---|---|
| Package version | <semver> |
| Date | <YYYY-MM-DD> |
| Critical gates | <n/n passing> |
| Warn gates | <n passing, m with accepted exception> |

## Gate results

<!-- One row per gate from references/quality-gates.md. Severity: Critical blocks; Warn does not.
     For any failing/excepted gate, give the offending IDs/paths and who accepted any exception. -->

| Gate | Severity | Result | Evidence / offending IDs | Exception (who / why) |
|---|---|---|---|---|
| G-REQ-SRC | Critical | <pass/fail> | <FR-/NFR- missing source, or none> | — |
| G-IDS | Critical | <pass/fail> | <bad/dangling ids, or none> | — |
| G-DEC-STATUS | Critical | <pass/fail> | <decisions missing status, or none> | — |
| G-TRACE | Critical | <pass/fail> | <MVP reqs with gaps, or none> | — |
| G-COMPLETE | Critical | <pass/fail> | <stub/empty artifacts, or none> | — |
| G-CONFLICT | Critical | <pass/fail> | <unresolved contradictions, or none> | — |
| G-EXEC | Critical | <pass/fail> | <phases/leaves not actionable, or none> | — |
| G-HANDOFF | Critical | <pass/fail> | <dangling prompt refs, or none> | — |
| G-OQ | Critical | <pass/fail> | <blocking OQ unanswered, or none> | — |
| G-ASM-VISIBLE | Warn | <pass/fail> | <assumptions missing risk_if_wrong> | <name / reason> |
| G-CLAIM | Warn | <pass/fail> | <uncited claims in Approved artifacts> | <…> |
| G-RISK | Warn | <pass/fail> | <high-impact items lacking risk view> | <…> |
| G-COUPLING | Warn | <pass/fail> | <needless coupling to one provider/agent> | <…> |
| G-BLOAT | Warn | <pass/fail> | <artifacts merely restating others> | <…> |
| G-CMD-THIN | Warn | <pass/fail> | <methodology leaking into the command> | <…> |

## Open items

<!-- What remains. For NO-GO, these are the blockers to clear. For GO, these are accepted-open. -->
- <blocking item → action / owner> OR <accepted-open item → why safe>.

## Residual risks

<!-- Risks that remain at handoff, even if mitigated. Reference RISK- ids and their triggers. -->
- `RISK-00x` — <residual exposure; trigger to watch; fallback>.

## Accepted exceptions (Warn gates)

<!-- Each Warn gate not passing must be explicitly accepted here, by whom, and why. -->
- `<G-…>` — accepted by <name-or-role> on <date>: <reason>.
