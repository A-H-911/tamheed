---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Technology Comparison — <decision area>

<!-- A weighted, criteria-based comparison of >=2 viable options for a technology/approach choice.
     KEEP THE LOSERS: rejected options are evidence the decision was reasoned (do not delete them).
     Generation class: Conditional (>=2 viable technology options). Lives at:
     architecture/technology-comparison.md. The verdict here feeds a DEC- / ADR-. Stay neutral until
     the matrix is scored. -->

## Decision being made

<!-- The choice, the requirements/constraints it must satisfy, and the decision it feeds. -->
Choose <what> to satisfy `FR-/NFR-/CON-`. Feeds `DEC-00x` / `ADR-000x`.

## Options considered

<!-- List every option taken seriously, including any "build it ourselves" or "do nothing" baseline. -->
- **Opt-A:** <name / category> — <one line>
- **Opt-B:** <name / category> — <one line>
- **Opt-C:** <name / category> — <one line>

## Criteria and weights

<!-- The criteria that matter for THIS decision, each weighted by importance (weights sum to 1.0 or
     use 1-5). Derive criteria from the requirements/constraints, not generic checklists. -->

| Criterion | Weight | Rationale (why it matters here) |
|---|---|---|
| <fit-to-requirement> | 0.30 | <ties to FR-/NFR-> |
| <maturity / support> | 0.20 | <risk reduction> |
| <constraint compliance> | 0.20 | <ties to CON-> |
| <effort / complexity> | 0.15 | <delivery impact> |
| <extensibility / lock-in> | 0.15 | <neutrality; safeguard against coupling> |

## Comparison matrix

<!-- Score each option per criterion. Use a fit rating AND/OR a numeric score.
     Fit ratings (use exactly these): strong | partial | weak | unknown | unsuitable.
     Weighted score = sum(weight x numeric score) if using numbers (e.g. 1-5). -->

| Criterion | Weight | Opt-A | Opt-B | Opt-C |
|---|---|---|---|---|
| <fit-to-requirement> | 0.30 | strong | partial | weak |
| <maturity / support> | 0.20 | strong | strong | unknown |
| <constraint compliance> | 0.20 | strong | unsuitable | partial |
| <effort / complexity> | 0.15 | partial | strong | partial |
| <extensibility / lock-in> | 0.15 | strong | weak | partial |
| **Weighted score** | 1.00 | **<x.x>** | **<x.x>** | **<x.x>** |

## Verdict

<!-- The recommended option and the deciding reasons. Note disqualifiers (an `unsuitable` on a
     must-have criterion eliminates an option regardless of total score). -->
- **Recommended:** <Opt-A> — <why it wins>.
- **Rejected:** <Opt-B> (<reason, e.g. unsuitable on constraint compliance>), <Opt-C> (<reason>).
- **Unknowns to resolve:** <any `unknown` ratings → raise `OQ-`/`EXP-` if they could change the verdict>.

<!-- Record the chosen option as a DEC-; promote to ADR if architecturally significant. -->
