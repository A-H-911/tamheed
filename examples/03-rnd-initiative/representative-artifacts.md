# Representative artifacts — semantic-cache

Real filled excerpts from the generated package, chosen to show the research-forward shape of this profile and the cross-referencing that holds it together: hypotheses drive experiments which gate decisions which gate acceptance (HYP-001 ↔ EXP-001 ↔ DEC-001 ↔ AC-001), the safety invariant is locked by the one ADR and verified in acceptance (INV-001 ↔ ADR-0001 ↔ AC-002), and the approach decisions stay **Deferred pending experiment** (tech-comparison verdict = needs EXP-002 ↔ DEC-002 Deferred). These are illustrative slices of the full artifacts.

## Research questions / functional requirements (excerpt)

Provisional product FRs — what the cache *would* do if productionized — paired with their research framing. Most are **Proposed and contingent on DEC-001 (go)**; they are not committed build scope.

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| FR-001 | The cache shall return a stored response when prompt similarity ≥ the configured threshold **AND** the safety gate passes; otherwise it shall miss and defer to the LLM API. (*Research framing: the right threshold is unknown and is the object of EXP-001; this FR defines the behavior, not the threshold value.*) | input.md; INV-001; HYP-001 | Must (if productionized) | Proposed — contingent on DEC-001 |
| FR-002 | The cache shall record, for every lookup, hit/miss, the similarity score, and the source key, to support evaluation and audit. (*Research framing: this instrumentation is required by the eval harness in PH-1 regardless of the go/no-go.*) | input.md (measurability); INV-003 | Must | Proposed — PH-1 harness needs it now |
| FR-003 | The cache shall support invalidation by age (TTL) and by explicit key, to keep answers fresh. (*Research framing: the effective TTL is unknown and is the object of EXP-003; this FR defines the mechanism, not the window.*) | input.md (freshness); HYP-003 | Should (if productionized) | Proposed — contingent on DEC-001 |
| FR-004 | The cache shall never serve a stored response across user/context boundaries for personalized or context-dependent prompts. | input.md (personalization); INV-002; ASM-003 | Must | Proposed — contingent on DEC-001 |

## Non-functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|----|-----------|--------|----------|--------|
| NFR-001 | False-positive (wrong-answer) rate on the curated eval set ≤ the ASM-001 bar (≤ 1%). | input.md; ASM-001; INV-001 | Must | Proposed |
| NFR-002 | LLM-cost reduction on the curated eval set ≥ the ASM-001 target (≥ 30%), measured at a threshold that simultaneously satisfies NFR-001. | input.md; ASM-001 | Must | Proposed |
| NFR-003 | Cache-lookup latency (embed + similarity search + safety gate) p95 ≤ the ASM-004 budget (≤ 50 ms). | input.md (latency win); ASM-004 | Must | Proposed |
| NFR-004 | Cached prompt/response data handling meets the privacy/retention bar: encrypted at rest, retention ≤ 30 days, no third-party sharing, no cross-user serving. | input.md (privacy); ASM-003; INV-002 | Must | Proposed |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | Never return a cached answer unless prompt similarity ≥ the configured threshold **AND** the safety gate passes. A cache **miss is always safer than a wrong hit**. | A false positive (confidently wrong/stale answer) is worse than a miss — it silently degrades quality and trust, while a miss merely costs one model call. This is the load-bearing safety property of the whole initiative; any approach that can serve a below-bar answer is disqualified. |
| INV-002 | No cached answer is served across user/context boundaries that would leak personalized or sensitive content. | Cached prompts/responses are sensitive (ASM-003); cross-user serving would both produce wrong-context answers and breach privacy. A compliance and correctness failure, not a tuning issue. |
| INV-003 | Every served cache hit is logged with its similarity score and source key, for auditability and evaluation. | Without per-hit provenance the false-positive rate cannot be measured, the safety gate cannot be audited, and the go/no-go has no evidence base. Auditability is a precondition for trusting any result. |

## Hypotheses (register excerpt)

| ID | Hypothesis | Confirms-if (signal) | Refutes-if | Linked experiment | Status |
|----|------------|----------------------|------------|-------------------|--------|
| HYP-001 | ≥ 30% of workload-Z prompts have a semantically-equivalent prior prompt such that caching yields **≥ 30% cost reduction at ≤ 1% false-positive rate** at some similarity threshold. | A threshold exists on the sweep where cost-reduction ≥ 30% **and** false-positive ≤ 1% simultaneously, holding on the holdout split. | No threshold on the sweep satisfies both bars together (the trade-off curve never enters the success region). | EXP-001 | Proposed / Open |
| HYP-002 | A **lightweight embedding approach** reaches within 2 points of the best approach on accuracy/separation, at materially lower lookup latency and cost. | Lightweight approach's accuracy/separation is within 2 pts of the best, with p95 lookup latency comfortably under the ASM-004 budget. | The lightweight approach loses > 2 pts of separation, forcing a heavier model to meet NFR-001. | EXP-002 | Proposed / Open |
| HYP-003 | **Age-based invalidation with a 24h window** keeps staleness-related wrong answers ≤ 0.5% on the eval set. | Staleness-induced false positives ≤ 0.5% at a 24h TTL on prompts whose reference answers change over time. | Staleness-induced false positives exceed 0.5% at 24h, requiring a shorter TTL or event-based invalidation. | EXP-003 | Proposed / Open |

## Experiments (one full, plus index)

### EXP-001 — Hit-rate vs false-positive characterization on workload Z (FULL)

**Status:** Planned
**Hypothesis under test:** HYP-001.
**Timebox:** 2 weeks (hard stop; if inconclusive at timebox, report inconclusive — that is a valid result that informs DEC-001).

**Method.**
1. Take the curated 2,000-prompt evaluation set sampled from workload Z (ASM-002), each prompt paired with a reference "correct" answer, split into a tuning set and a holdout set.
2. Replay the set through the cache harness. For each prompt, embed it, retrieve the most-similar prior prompt from the index, and record the similarity score and the candidate cached answer.
3. **Sweep the similarity threshold** across a range. At each threshold, classify each prompt as hit (similarity ≥ threshold and safety gate passes) or miss, and for each hit compare the cached answer to the reference answer (operational definition of "wrong answer" per clarification 7) to mark true-positive vs false-positive.
4. At each threshold compute **hit-rate**, **estimated cost reduction** (fraction of prompts served from cache × per-call cost), and **false-positive rate**. Plot the trade-off curve.
5. Confirm findings on the **holdout split** to guard against threshold overfit (RISK-003).

**PASS criteria.** There exists at least one threshold at which **cost reduction ≥ 30% AND false-positive rate ≤ 1%** simultaneously (ASM-001), holding on the holdout split. HYP-001 is **confirmed**.

**FAIL criteria.** No threshold on the sweep satisfies both bars together — the trade-off curve never enters the success region. HYP-001 is **refuted**. (This is a legitimate, valuable outcome: it says semantic caching does not pay off on workload Z under the agreed bar.)

**Decision it unblocks.** **DEC-001 — "Productionize semantic cache?"** EXP-001 PASS (with acceptable EXP-003 staleness) → DEC-001 can move to Approved (go); EXP-001 FAIL → DEC-001 moves to Rejected (no-go) with the refutation documented.

**Index of remaining experiments / POC:**
- **EXP-002 — Embedding-approach comparison.** Tests HYP-002. Replays the same eval set under each candidate embedding approach, comparing accuracy/separation, latency, and cost. PASS: lightweight approach within 2 pts of best at lower latency/cost → adopt it. FAIL: lightweight loses > 2 pts → heavier approach needed. **Timebox: 1.5 weeks.** Unblocks DEC-002.
- **EXP-003 — Invalidation / staleness characterization.** Tests HYP-003. Measures staleness-induced false positives across candidate TTLs (incl. 24h) on time-sensitive prompts. PASS: ≤ 0.5% staleness false positives at a viable TTL. FAIL: exceeds 0.5% at all viable TTLs → event-based invalidation required. **Timebox: 1 week.** Unblocks DEC-003 and feeds DEC-001.
- **POC-001 — Cache-lookup latency.** Validates NFR-003. Measures end-to-end lookup (embed + index search + safety gate) p95 against the ASM-004 budget. PASS: p95 ≤ 50 ms. FAIL: p95 > 50 ms → the latency rationale is weakened; revisit approach. **Timebox: 3 days.**

## Technology comparison (excerpt)

Scope: **embedding / similarity approach** for the cache. Vendor-neutral — options are described as capability tiers, not products. **Weights are stated before scoring.** Verdict is explicitly *deferred to experiment* — this matrix frames the options; it does not pick one.

**Criteria and weights:** Eval accuracy / separation (0.40) — the dominant factor, since false positives are the core risk; Lookup latency (0.25); Cost per lookup (0.20); Operational simplicity (0.15). Scored 1 (poor) – 5 (strong); weighted total is illustrative pending real measurement.

| Criterion (weight) | Option A: lightweight embedding | Option B: heavyweight embedding | Option C: domain-tuned embedding |
|--------------------|---------------------------------|----------------------------------|----------------------------------|
| Eval accuracy / separation (0.40) | 3 — adequate, unproven on workload Z | 4 — likely strongest general separation | 4 — potentially best *if* tuning data exists |
| Lookup latency (0.25) | 5 — fast | 2 — heavier, may threaten ASM-004 | 3 — depends on size |
| Cost per lookup (0.20) | 5 — cheapest | 2 — most expensive | 3 — moderate |
| Operational simplicity (0.15) | 4 — simple | 3 — moderate | 2 — needs tuning pipeline |
| **Weighted total (illustrative)** | **4.05** | **3.00** | **3.35** |

**Verdict: NEEDS EXPERIMENT — no premature pick.** The dominant criterion (accuracy/separation) is exactly the thing that **cannot be scored by reasoning on our workload** — it must be measured. The illustrative totals favor the lightweight option on latency/cost, but that is meaningless if it cannot hold the ≤ 1% false-positive bar (NFR-001). **The choice is deferred to EXP-002** (HYP-002), and the decision is recorded as **DEC-002 = Deferred — pending EXP-002 result**. No embedding approach is committed in the package.

## One ADR

### ADR-0001 — Cache-layer contract and mandatory safety gate
**Status:** Approved

**Context.** The internals of a semantic cache are genuinely uncertain (which embedding approach, which index, what threshold, what invalidation) and must not be locked before the experiments resolve. But one thing *is* safe — indeed necessary — to fix now: the **seam**. We need a stable contract for how callers interact with the cache and a non-negotiable rule that protects the load-bearing safety property (INV-001), so that the experiment harness and any future productionization share the same shape and the same safety guarantee regardless of which internals win.

**Decision.** Define the cache-layer contract as a single operation: **`lookup(prompt, context) → {hit(answer, similarity, source_key) | miss}`**. Every `hit` **must** pass a mandatory **similarity + safety gate** before it is returned: similarity ≥ the configured threshold **and** the safety gate passes (including the cross-user/context check, INV-002). The gate is **not optional and not bypassable**. Every lookup is logged with its similarity score and source key (INV-003, FR-002). The **internals behind this contract are pluggable** — embedding approach, index, threshold, and invalidation strategy are all swappable and are decided later by experiment (DEC-002, DEC-003) — but no implementation may weaken or skip the gate.

**Alternatives considered.**
- *Return the best match without a mandatory gate* — **rejected**: this is precisely the false-positive failure mode; it would allow confidently-wrong answers and directly violate INV-001.
- *Make the gate or the logging optional for "performance"* — **rejected**: bypassing the gate forfeits the only safety property; bypassing logging makes the false-positive rate unmeasurable and the result untrustworthy (violates INV-003).

**Consequences.** Locks the safe part (the seam + the safety guarantee) while leaving the uncertain part (internals) open — this is the no-premature-architecture safeguard made concrete. The harness in PH-1 is built against this contract, so experiment code carries forward if DEC-001 = go. Every approach option compared in `technology-comparison.md` must satisfy this contract, narrowing the option space safely.

**References:** INV-001, INV-002, INV-003, FR-001, FR-002, AC-002.

## Open decisions (register excerpt)

Demonstrates the **Deferred-pending-experiment** discipline: the substantive choices are not made until their experiment reports. None is rendered as Approved.

| ID | Decision | Status | Trigger to revisit |
|----|----------|--------|--------------------|
| DEC-001 | Productionize the semantic cache? | **Deferred** | EXP-001 **PASS** (a threshold meets NFR-001 + NFR-002) **AND** acceptable EXP-003 staleness result. Go → Approved; refutation → Rejected. |
| DEC-002 | Which embedding / similarity approach? | **Deferred** | EXP-002 result (HYP-002). Becomes Proposed→Approved for the winning approach *only after* the experiment; tech-comparison verdict is "needs EXP-002". |
| DEC-003 | Which cache-invalidation strategy (TTL window vs event-based)? | **Deferred** | EXP-003 result (HYP-003). Adopt 24h TTL if staleness ≤ 0.5%; otherwise shorter TTL or event-based. |

## Risk register (excerpt)

| ID | Risk | Impact | Likelihood | Mitigation | MVP/Full |
|----|------|--------|------------|-----------|----------|
| RISK-001 | False positives ship **confidently-wrong** answers (loose threshold serves wrong-context/stale answers as if correct). | High (violates INV-001; degrades trust) | Medium | Mandatory safety gate (INV-001 / ADR-0001) + a deliberately **conservative threshold** chosen from the EXP-001 curve + the **go/no-go gate** (DEC-001) prevents productionizing at all unless the bar is met. | Full |
| RISK-002 | Privacy exposure from storing user prompts/responses, or cross-user leakage of personalized answers. | High (compliance breach; wrong-context answers) | Low-Medium | Encryption at rest, retention ≤ 30 days, no third-party sharing (ASM-003 / NFR-004); cross-user/context serving forbidden (INV-002 / FR-004), verified in AC-004. | Full |
| RISK-003 | The evaluation set is **unrepresentative**, so experiment results mislead the go/no-go (over-optimistic hit-rate or under-counted false positives). | High (a wrong go/no-go) | Medium | Sample the eval set from **real workload Z** (ASM-002) and validate every EXP-001 finding on a **holdout split**; document sampling method in the test strategy. | Full |

## Roadmap (phases)

### PH-1 — De-risk via experiments
**Goal.** Run EXP-001, EXP-002, EXP-003 and POC-001 to produce **validated or refuted hypotheses** (HYP-001/002/003) and a **go/no-go recommendation** on productionization. Phase 1's deliverable is *knowledge*, not a product.
**Deliverables.** The evaluation harness (replays the curated eval set, computes hit-rate / cost-reduction / false-positive across a threshold sweep, enforces the safety gate per ADR-0001); the four experiment/POC reports with explicit PASS/FAIL against their criteria; a written **recommendation** synthesizing the results.
**Exit criteria.** **DEC-001 is decided** — each of HYP-001/002/003 marked confirmed or refuted with evidence, the cost/false-positive trade-off characterized, and a go/no-go stated. (Exit is "the decision is made," not "the decision is go.")

### PH-2 — Productionize (CONDITIONAL on PH-1 go)
**Goal.** Build the production cache layer per the winning embedding approach (DEC-002) and invalidation strategy (DEC-003), against the ADR-0001 contract, with the safety gate enforced.
**Deliverables.** Production cache layer; full productionization architecture (the deferred diagrams and broad WBS, generated now that DEC-001 = go); rollout plan with monitoring of the live false-positive rate.
**GATE (unmistakable).** **PH-2 does not begin unless DEC-001 = go (Approved).** If DEC-001 = no-go (Rejected), PH-2 is not entered at all; the initiative concludes with the documented refutation and recommendation. No productionization work — none — happens before this gate is passed. DEC-002 and DEC-003 must also have been resolved from Deferred to Approved by their experiments before their parts of the build start.

## Acceptance criteria (excerpt)

Framed as experiment PASS/FAIL plus provisional product AC. Given/When/Then where natural.

| ID | Criterion | Traces to |
|----|-----------|-----------|
| AC-001 | **Given** the curated eval set and the threshold sweep, **when** EXP-001 runs, **then** it either produces a threshold meeting **NFR-001 (≤ 1% false positives) and NFR-002 (≥ 30% cost reduction)** on the holdout, confirming HYP-001 — **or** it produces a documented **refutation** showing no threshold satisfies both. Either outcome is a PASS for the *experiment* (a clear result); only the absence of a clear result is a FAIL. | HYP-001, EXP-001, DEC-001, NFR-001, NFR-002 |
| AC-002 | **Given** a candidate hit whose similarity is below the configured threshold or that fails the safety gate, **when** the harness processes it, **then** the safety gate (INV-001) **blocks** it and the request falls through to a miss — provably, in the harness, with no below-bar answer ever returned. | INV-001, ADR-0001, FR-001 |
| AC-003 | **Given** the lookup path (embed + index search + safety gate), **when** POC-001 measures latency, **then** p95 ≤ the ASM-004 budget (≤ 50 ms), satisfying NFR-003 — or the shortfall is documented as a risk to the latency rationale. | NFR-003, POC-001, ASM-004 |
| AC-004 | **Given** personalized or context-dependent prompts and sensitive cached data, **when** lookups are processed, **then** no cached answer is served across user/context boundaries (INV-002) and cached data handling meets the retention/encryption bar (NFR-004 / ASM-003). | INV-002, FR-004, NFR-004, ASM-003 |

---

**Cross-reference summary.** HYP-001 ↔ EXP-001 ↔ DEC-001 ↔ AC-001 (the central go/no-go chain). INV-001 ↔ ADR-0001 ↔ AC-002 (the safety gate, locked and verified). HYP-002 ↔ EXP-002 ↔ DEC-002 (Deferred) and HYP-003 ↔ EXP-003 ↔ DEC-003 (Deferred) — the approach choices stay Deferred-pending-experiment, matching the tech-comparison verdict ("needs EXP-002"). Every FR/NFR carries a source; every decision carries an explicit status; the only Approved decision is ADR-0001 (the seam), and it is Approved precisely because it does not pre-empt the uncertain internals.
