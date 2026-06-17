---
status: Proposed        # Proposed | Accepted | Rejected | Superseded | Deprecated
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
id: ADR-NNNN
supersedes: <ADR-NNNN or none>
superseded_by: <ADR-NNNN or none>
---

# ADR-NNNN — <short decision title>

<!-- One Architecture Decision Record per file. ADRs capture architecturally SIGNIFICANT decisions
     (hard to reverse, broad blast radius). They are IMMUTABLE after acceptance: to change a decision,
     write a new ADR that supersedes this one — do not rewrite history (typo fixes excepted).
     Filename: adr-NNNN-short-title.md. Generation class: Conditional (significant decisions).
     Lives at: adrs/. If promoted from a DEC-, note it under Context.
     ADR statuses: Proposed | Accepted | Rejected | Superseded | Deprecated. -->

## Status

<!-- One of: Proposed | Accepted | Rejected | Superseded | Deprecated. Mirror the front-matter.
     If superseded, link the successor: "Superseded by ADR-000x". -->
<status> — <date and one-line note; e.g. "Promoted from DEC-007">

## Context

<!-- The forces at play: the problem, the requirements/constraints/invariants in tension
     (`FR-/NFR-/CON-/INV-`), assumptions (`ASM-`), and what makes this decision necessary now.
     Neutral and factual — no foregone conclusion. -->
<context>

## Decision

<!-- The choice, stated in the active voice: "We will …". Be specific enough that an implementer
     cannot reasonably misread it. -->
We will <decision>.

## Consequences

<!-- Honest results of the decision — both directions. -->
### Positive
- <benefit>

### Negative / costs
- <cost, limitation, or new obligation>

### Follow-ups
- <e.g. introduces RISK-00x; requires TEST-00x; creates DEP-00x>

## Alternatives considered (and why rejected)

<!-- Keep the losers. Rejected alternatives are the evidence that the decision was reasoned.
     One sub-block per serious alternative. -->
### <Alternative A>
- **Summary:** <what it was>
- **Why rejected:** <the deciding reason>

### <Alternative B>
- **Summary:** <what it was>
- **Why rejected:** <the deciding reason>

## Links

- Requirements served: <FR-/NFR->
- Constraints / invariants respected: <CON-/INV->
- Originating decision: <DEC-00x>
- Related ADRs: <ADR-000x>
