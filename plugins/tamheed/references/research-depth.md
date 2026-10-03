# Research depth

Match research and planning effort to **genuine uncertainty and blast radius**, not to a fixed template.
Over-researching a simple project is as much a failure as under-researching a risky one (safeguard 11).

## Depth tiers

| Tier | When | Research behavior |
|---|---|---|
| **Light** | Well-understood domain, proven stack, low risk, small scope | Confirm key facts. Skip experiments. A short comparison only where a real choice exists. |
| **Standard** | Some novel elements, a few real technology choices | Targeted research on the choices. Weighted comparisons. Experiments only for genuine unknowns. |
| **Deep** | High novelty, hard-to-reverse decisions, strict NFRs, regulated, or large scope | Full research plan (it absorbs the backlog role). Hypotheses. Timeboxed POCs before committing, with metric + threshold decided before the run and verdicts Validated / Invalidated / Inconclusive. |

The project profile (Stage 2) sets a starting tier. Specific decision points can be escalated individually.

## Sizing rule

For each decision point, ask: *how costly is being wrong, and how reversible is it?* High cost × low
reversibility ⇒ deeper investigation (an experiment/POC) before deciding. Low cost or easily reversible ⇒
decide now, note it, move on.

## Timeboxing

Every investigation has a timebox and a metric + threshold decided before the run. The verdict
(Validated / Invalidated / Inconclusive) is judged against it. Research without an exit condition is
scope drift. Bound it and record what would end it.

## Verification standard

Do not assert a tool/library/service capability without a citation or a direct check. Tag anything unverified
as `unverified` so G-CLAIM (a prose-tier judgment gate) can catch it. Prefer primary sources (docs, issue trackers, releases) over recall.
