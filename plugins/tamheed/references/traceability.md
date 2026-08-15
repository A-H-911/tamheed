# Traceability

The traceability matrix is what lets an implementing agent navigate from any need to its evidence and back.
It is **derived by construction** — views over typed `trace_edges` rows, never hand-maintained — so it
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

Not every requirement touches every column, but the gate (`G-TRACE`) requires: every MVP `FR-/NFR-` links
to ≥1 decision, ≥1 work item, and ≥1 test; every requirement asserting user-visible behavior links to ≥1
acceptance criterion.

## Representation

The matrix is read, not written: `review.html#traceability` is the human surface, `trace_query` walks
edges per entity, and the `v_req_links` view is what `gate_run` checks. There is no matrix file to keep
current.

## Recording & checking

1. Edges are recorded **live, as typed `trace_edges` rows, at decision time** — `derives_from`,
   `implements`, `tests`, `verifies`, `mitigates`, `discharges`, `learned_from` (a lesson → the
   defect / decision / risk / slice / wbs-item / progress-entry that taught it), plus the
   scope-delta kinds (`scope_adds`/`scope_modifies`/`scope_removes`); `relates_to` is the documented
   untyped escape hatch. There is no after-the-fact "collect the links" pass. Promotion links are
   **columns**, not edges: `lessons.promoted_to` → the `SKL-` skill it was distilled into, the same
   idiom as `decisions.promoted_to` → the ADR.
2. `G-TRACE` fails on any MVP requirement with a gap in a required column — fix by adding the missing
   decision/slice/test edge or by explicitly de-scoping the requirement (recorded).
3. On updates (Stage 21), the views stay current by construction; a superseded item's links move to its
   successor through the supersession flow.

## Bidirectional

The matrix reads forward (need → evidence) and backward (a test/risk → the needs it serves). Backward links
catch orphans: a work item or test that traces to no requirement is either gold-plating or a missing
requirement — investigate, don't ignore.
