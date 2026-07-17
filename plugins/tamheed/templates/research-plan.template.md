---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Research Plan — <project-name>

<!-- Plan research PROPORTIONAL to genuine uncertainty (do not research the settled). This plan frames
     the unknowns, what evidence would resolve them, and the method/effort to get it.
     Generation class: Conditional (genuine technical uncertainty). Lives at: research/research-plan.md.
     Feeds the hypotheses (HYP-), experiments (EXP-), and POCs (POC-). -->

## Research objectives

<!-- What we must learn to make confident decisions. Tie each to the decision or risk it unblocks. -->
- <objective-1> — unblocks `DEC-00x` / reduces `RISK-00x`.
- <objective-2> — <what it unblocks>.

## Key uncertainties

<!-- The specific unknowns, framed so an answer is recognizable. Link the open questions they map to. -->
| Uncertainty | Why it matters | Linked OQ / DEC / RISK |
|---|---|---|
| <unknown-1> | <impact on the plan> | OQ-001, DEC-002 |
| <unknown-2> | <impact> | RISK-003 |

## Approach

<!-- For each uncertainty, how it will be investigated: literature/doc review, prototype/POC,
     experiment, benchmark, spike, expert input. Keep proportional. -->
| Uncertainty | Method | Evidence sought | Effort / timebox |
|---|---|---|---|
| <unknown-1> | <experiment EXP-001 / POC-001 / doc review> | <PASS/FAIL signal> | <e.g. 1 day> |
| <unknown-2> | <method> | <signal> | <timebox> |

## Information sources

<!-- Where evidence will come from. Tag any claim that will be reused in Approved artifacts so it can
     be cited or marked `unverified` (gate G-CLAIM). -->
- <docs / standards / reference implementations / prior art>

## Deliverables

- Hypotheses recorded in [hypothesis register](hypothesis-register.md) (`HYP-`).
- Experiment plans in [experiments/](../experiments/) (`EXP-`); POC plans in [pocs/](../pocs/) (`POC-`).
- Findings folded back into decisions (`DEC-/ADR-`) and risks (`RISK-`).

## Out of scope for research

<!-- What we are deliberately NOT researching, and why (e.g. settled by a constraint). -->
- <non-investigation> — <reason>.
