# Traceability

The traceability matrix is what lets an implementing agent navigate from any need to its evidence and back.
It is **derived by construction**, views over typed `trace_edges` rows, never hand-maintained, so it
cannot drift from the entities it links.

## The chain

```
Requirement (FR-/NFR-)
   → Decision (DEC-/ADR-)          why it's built this way
   → Slice / work item (SL-/WBS-)  where it gets built
   → AC / Test (AC-/TEST-)         how we know it works
   → Verdict (AV-)                 whether it actually does
   → Risk (RISK-)                  what could go wrong
```

Not every requirement touches every column, but the gate (`G-TRACE`) requires two things. Every MVP
`FR-/NFR-` links to ≥1 decision, ≥1 work item, and ≥1 test. Every requirement asserting user-visible
behavior links to ≥1 acceptance criterion.

## Representation

The matrix is read, not written: `review.html#traceability` is the human surface, `trace_query` walks
edges per entity, and the `v_req_links` view is what `gate_run` checks. There is no matrix file to keep
current.

## Recording & checking

1. Edges are recorded **live, as typed `trace_edges` rows, at decision time**. The relations are
   `derives_from`, `implements`, `tests`, `verifies`, `mitigates`, `discharges`, and `learned_from`.
   A `learned_from` edge links a lesson → the defect / decision / risk / slice / wbs-item /
   progress-entry that taught it. Add the scope-delta kinds (`scope_adds`/`scope_modifies`/
   `scope_removes`, plan rows only). `amends` links a scope change → the `DEC-`/`ADR-` ruling it
   carves an exception out of or re-scopes (v4.5). `carries` links a wbs-item → the activated `DW-`
   row it carries (v5). It is the edge `deferred-work-carried` reads. `relates_to` is the documented
   untyped escape hatch. There is no after-the-fact "collect the links" pass.
   Edges are keyed `(from_id, to_id, relation)`. Writing a new relation between a pair never
   replaces an old one. A wrong edge is RETIRED (`retire: true` on the trace-edge item) and the
   corrected edge is written in the same batch. On a retire the triple is removed and the relation
   rule is not consulted. The server journals it as a `correction` row in the same transaction
   (v4.6, findings_23 §1). Retire a wrong edge only, never to make a gate pass. Promotion links are
   **columns**, not edges: `lessons.promoted_to` → the `SKL-` skill it was distilled into, the same
   idiom as `decisions.promoted_to` → the ADR.
2. `G-TRACE` fails on any MVP requirement with a gap in a required column. Fix by adding the missing
   decision/slice/test edge, or by explicitly de-scoping the requirement (recorded).
3. On updates (Stage 21), the views stay current by construction. A superseded item's links move to its
   successor through the supersession flow.

## Bidirectional

The matrix reads in both directions: from a need to its evidence, and back from a test/risk to the
needs it serves. Backward links catch orphans: a work item or test that traces to no requirement is
either gold-plating or a missing requirement. Investigate, do not ignore.
