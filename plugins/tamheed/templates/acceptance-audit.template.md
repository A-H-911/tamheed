---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
generation: derived      # regenerated from acceptance-criteria.md + execution evidence each gate
---

# Acceptance Audit — <project-name>

<!-- The DERIVED closing view that proves the built thing met its acceptance criteria. One row per AC-
     from validation/acceptance-criteria.md, each mapped to an honest VERDICT and the EVIDENCE for it.
     Distinct from the execution-readiness report: that is the PLANNER's pre-handoff go/no-go ("is the
     package ready to hand off?"); THIS is the DOWNSTREAM AGENT's during/after-execution record ("did the
     build meet the AC?"). Generation class: Derived / Conditional (handoff or long execution horizon).
     Lives at: validation/acceptance-audit.md. Regenerated each phase gate (stage 21) — not hand-kept
     history (that is the progress log).

     SEEDING + HONESTY RULES (a generated audit MUST satisfy them):
     - At handoff, seed every AC- row with verdict `Pending` and evidence `—`. As work lands, the agent
       flips the verdict to Met / Partial / Not-met and fills the evidence.
     - Verdicts are exactly: Met | Partial | Not-met | Pending. Call out Partial / Not-met honestly with a
       reason — never rubber-stamp.
     - Use `Pending` and `—`; never the literal markers TBD / TODO / angle-placeholder in a *generated*
       audit (those fail gate G-COMPLETE). Strip these guidance comments when filling the template.
     - Every AC- in acceptance-criteria.md must appear here (gate G-PROGRESS checks this coverage). -->

## Conventions

- **Verdict** — `Met` (satisfied, evidence shown) · `Partial` (partly met — explain) · `Not-met`
  (explain + link the open item / `RISK-`) · `Pending` (not yet executed).
- **Evidence** — what proves the verdict: `TEST-` ids, commit/PR, CI run, golden sample, or a demo note.

## MVP acceptance

| AC | Criterion (short) | Verdict | Evidence | Notes |
|---|---|---|---|---|
| AC-001 | <short restatement> | Pending | — | <seeded at handoff; agent updates as work lands> |
| AC-002 | <short restatement> | Pending | — | — |

## Full-target acceptance

| AC | Criterion (short) | Verdict | Evidence | Notes |
|---|---|---|---|---|
| AC-010 | <short restatement> | Pending | — | — |

## Summary

- **MVP:** <m> / <n> Met (<p> Partial, <q> Not-met, <r> Pending).
- **Full:** <a> / <b> Met.
- **Verdict:** <one line — e.g. "MVP acceptance complete; Full pending PH-3">.

## Residual / honest caveats

<!-- Anything Partial or Not-met, with the reason and the tracked follow-up (OQ-/RISK-/deferred AC-). A
     partial that is called out here is worth more than a Met that is not backed by evidence. If nothing
     is outstanding, say so explicitly. -->
- <criterion> — <Partial/Not-met> because <reason>; tracked as <OQ-/RISK-/deferred>.
