---
status: Proposed        # Draft | Proposed | Approved | Rejected | Deferred | Implemented | Superseded | Obsolete
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
id: ADR-NNNN
supersedes: <ADR-NNNN or none>
superseded_by: <ADR-NNNN or none>
---

# ADR-NNNN — <short decision title>

<!-- One Architecture Decision Record per file. ADRs capture architecturally SIGNIFICANT decisions
     (the one-way-door test: hard to reverse, broad blast radius). They are IMMUTABLE after approval: to change a decision,
     write a new ADR that supersedes this one — do not rewrite history (typo fixes excepted).
     Stored as an `adr` row (`ADR-NNNN`); this template shapes its context/decision/consequences/
     confirmation prose. Generation class: Conditional (significant decisions).
     If promoted from a DEC-, note it under Context.
     ADR statuses are the standard lifecycle (governance.md): Draft | Proposed | Approved |
     Rejected | Deferred | Implemented | Superseded | Obsolete — the store CHECK rejects
     'Accepted'/'Deprecated' (use Approved / Obsolete). -->

## Status

<!-- One of the standard lifecycle values (the store CHECK): Draft | Proposed | Approved | Rejected |
     Deferred | Implemented | Superseded | Obsolete. Mirror the front-matter.
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

## Confirmation

<!-- v4 (MADR 4.x): HOW compliance with this decision will be verified — a fitness
     function, a review checklist item, a test, a gate. Stored in the adrs.confirmation
     column; part of the frozen content once approved. An ADR whose confirmation is
     never exercised is drift waiting to be found. -->
- <e.g. TEST-00x asserts the boundary; review checklist item; G-REL edge rule>

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
