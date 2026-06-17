# Research depth

Match research and planning effort to **genuine uncertainty and blast radius**, not to a fixed template.
Over-researching a simple project is as much a failure as under-researching a risky one (safeguard 11).

## Depth tiers

| Tier | When | Research behavior |
|---|---|---|
| **Light** | Well-understood domain, proven stack, low risk, small scope | Confirm key facts; skip experiments; short comparison only where a real choice exists. |
| **Standard** | Some novel elements, a few real technology choices | Targeted research on the choices; weighted comparisons; experiments only for genuine unknowns. |
| **Deep** | High novelty, hard-to-reverse decisions, strict NFRs, regulated, or large scope | Full research plan + R&D backlog; hypotheses; timeboxed POCs with PASS/FAIL gates before committing. |

The project profile (Stage 2) sets a starting tier; specific decision points can be escalated individually.

## Sizing rule

For each decision point, ask: *how costly is being wrong, and how reversible is it?* High cost × low
reversibility ⇒ deeper investigation (an experiment/POC) before deciding. Low cost or easily reversible ⇒
decide now, note it, move on.

## Timeboxing

Every investigation has a timebox and an explicit PASS/FAIL or decision criterion. Research without an exit
condition is scope drift; bound it and record what would end it.

## Verification standard

Do not assert a tool/library/service capability without a citation or a direct check. Tag anything unverified
as `unverified` so G-CLAIM can catch it. Prefer primary sources (docs, issue trackers, releases) over recall.
