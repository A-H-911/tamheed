# Clarification protocol

Clarification is how Tamheed avoids both **masking assumptions** and **over-asking**. The test for asking
a question: *would different answers change the plan, scope, architecture, or risk?* If yes, ask. If no,
record an assumption and move on.

## Ask vs assume

- **Ask** when the answer is decision-changing AND you cannot reasonably default it.
- **Assume** when you can proceed with a sensible default. Record an `ASM-` with `statement`,
  `rationale`, `risk_if_wrong`, and `revisit_if`. Surface assumptions in the readiness report.
- **Never** silently choose between materially different options. That is the cardinal failure.

## Batching

Group questions. Do not drip them one at a time. Order by impact. Cap a round at the few questions
that most unblock progress. Offer a recommended default with each so the user can accept quickly.

## Question quality

- Make each question concrete and answerable, with options when possible.
- Tie each to what it unblocks ("this determines whether MVP includes X").
- Prefer multiple-choice with a recommended option for speed. Allow free text.
- Do not ask what the input already answers. Do not ask for detail you do not yet need.

## Targets of clarification

Missing information, contradictions, hidden dependencies, premature solution decisions, undefined NFR
thresholds, unclear acceptance, ambiguous actors/scope, and unstated success metrics.

## Recording

- Answered question → resolve the `OQ-`, update the affected requirement/decision, note the answer's source
  (the user, on date).
- Unanswered but proceeding → `ASM-` + risk. Mark dependent artifacts "provisional".
- A clarification that changes scope → a `DEC-` referencing the scope item (scope is locked at Stage 8).

## When the user is unavailable

Proceed in `intake`/`plan` spirit: write the package under explicit assumptions and mark it
**provisional**. Put the full open-question list at the top of the readiness report so the gaps are
impossible to miss.
