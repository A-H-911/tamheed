# Clarifications — semantic-cache

The brief is unusually honest about its own uncertainty: the core questions (achievable hit-rate vs false-positive trade-off, embedding approach, threshold, invalidation, personalization) are explicitly open and are the point of the work, not gaps to be filled by assumption. The clarifications below pin down the *frame* of the investigation — what success means, what we evaluate against, what "correct" means operationally, and the privacy/latency envelope — so the experiments are measuring the right things against the right bar. They were asked as one batch to avoid round-trips. Where an answer was not returned in time, an assumption is recorded and flagged for confirmation. Critically, none of these clarifications resolves the central trade-off itself: that is left to be *characterized by experiment*, not assumed.

## Clarification batch (asked together)

1. **What cost-reduction target and what maximum acceptable false-positive (wrong-answer) rate together define "success"?**
   Answer (assumed): Not returned with hard numbers in time. The team agreed the success bar should be expressed as a *joint* condition, not two independent numbers, because they trade off. Assumed success bar: **at least 30% LLM-cost reduction at a false-positive rate of at most 1%** on the curated evaluation set. Recorded as ASM-001, pending confirmation. The team confirmed the *shape* (joint cost/false-positive bar) is right even if the exact figures move.

2. **What is the representative evaluation workload, and how is the "correct answer" (ground truth) judged?**
   Answer (assumed): A representative set does not exist yet in usable form; the team agreed one must be created by sampling real workload traffic ("workload Z"). Assumed: a **curated 2,000-prompt evaluation set sampled from real workload Z**, each prompt paired with a reference/"correct" answer judged by a human reviewer or an agreed reference, with a holdout split to guard against overfitting the threshold. Recorded as ASM-002. "Correct" is defined operationally in clarification 7.

3. **What is the latency budget for a cache lookup?**
   Answer (assumed): Not specified numerically. The team's intent is clear: the cache must not erode the latency win it is meant to deliver — a lookup that is slow defeats the purpose. Assumed cache-lookup budget: **p95 ≤ 50 ms** (embedding + similarity search + safety gate), so a hit is decisively faster than an LLM call. Recorded as ASM-004, pending confirmation against real embedding-endpoint latency.

4. **What are the privacy and retention constraints on storing prompts and responses?**
   Answer (given): Cached prompts and responses are **sensitive**. The team confirmed: treat them as sensitive data — **encrypted at rest, no third-party sharing, bounded retention**. Assumed retention window of **≤ 30 days** absent a stricter rule from Compliance. Recorded as ASM-003 and reflected as a hard constraint and invariant; nothing personalized may be served across user/context boundaries.

5. **Is the goal a reusable, productionizable component, or a one-off study?**
   Answer (given): The honest answer is **"it depends on the result."** Phase 1 is a study whose deliverable is knowledge + a go/no-go. *If* the hypotheses hold, the intent is a reusable, productionizable cache layer — so the experiment harness and the cache-layer *contract* should be built cleanly enough to carry forward, but the productionization itself is **gated** on the Phase-1 decision and is explicitly not in Phase 1.

6. **What is the acceptable staleness window for cached answers?**
   Answer (assumed): Not pinned down; the team acknowledged some answers go stale as underlying facts/data change. Assumed starting point: an **age-based invalidation window of 24 hours** as the candidate default, to be characterized — i.e. the question "does a 24h window keep staleness-related wrong answers acceptably low?" is itself an experiment (see HYP-003 / EXP-003), not a settled value. Captured under the invalidation open decision (DEC-003).

7. **What does "wrong answer" mean operationally, so we can measure false positives?**
   Answer (given): The team agreed a served cache hit is counted as a **false positive (wrong answer)** when the cached answer materially differs from the reference answer for the incoming prompt — i.e. it would not be accepted as a correct response to *this* prompt — as judged against the reference set (clarification 2). Borderline cases are adjudicated by the reviewer. This definition is what EXP-001 measures the false-positive rate against.

## Assumptions recorded

| ID | Assumption | Basis | Risk if wrong | Status |
|----|------------|-------|---------------|--------|
| ASM-001 | Success bar = **≥ 30% LLM-cost reduction at ≤ 1% false-positive (wrong-answer) rate**, expressed as a joint condition on the curated eval set. | Clarification 1 (assumed; shape confirmed). Frames the whole go/no-go. | If the real bar is materially stricter (e.g. ≤ 0.1% false positives) or looser, the threshold sweep verdict and DEC-001 go/no-go flip; experiments stay valid but the pass line moves. | Proposed |
| ASM-002 | A **2,000-prompt curated evaluation set** sampled from real workload Z, with human-/reference-judged "correct" answers and a holdout split, is available or will be created before EXP-001. | Clarification 2 (assumed). No representative set exists yet; experiments are meaningless without one. | If the set is unrepresentative or too small, results mislead the go/no-go (see RISK-003). Holdout + real-traffic sampling mitigate. | Proposed |
| ASM-003 | Cached prompts/responses are **sensitive**: encrypted at rest, no third-party sharing, **retention ≤ 30 days**, never served across user/context boundaries. | Clarification 4 (given) + privacy obligation in the brief. | If retention/handling rules are stricter, storage design and INV-002 enforcement tighten; if looser, no harm. Drives NFR-004 and INV-002. | Proposed |
| ASM-004 | **Cache-lookup latency budget ≤ 50 ms p95** (embed + similarity search + safety gate) so the cache does not erode the latency win. | Clarification 3 (assumed). | If real embedding/index latency exceeds the budget, a "hit" may not be meaningfully faster than a model call, undercutting the latency rationale (POC-001 tests this). | Proposed |

## Note on the central trade-off (not a contradiction)

There are **no hard contradictions** in the brief. But the most important thing to flag is that the false-positive tolerance and the achievable hit-rate are a **fundamental trade-off**, not a pair of independently settable targets: tightening the similarity threshold lowers false positives but also lowers hit-rate (and therefore cost reduction), and loosening it does the reverse. The brief's success bar (ASM-001) is therefore only meaningful as a *joint* condition — "≥ X% cost reduction **at** ≤ Y% false positives" — and whether any threshold satisfies it on workload Z is precisely the empirical question EXP-001 exists to answer. We deliberately do **not** assume a threshold or a hit-rate here; assuming the trade-off away would defeat the purpose of the initiative. This is recorded so the trade-off is characterized by experiment and surfaced in the go/no-go, rather than papered over.
