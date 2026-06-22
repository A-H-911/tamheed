# Selected artifact set — semantic-cache

This is an **R&D / research-heavy profile**. The deliverable of the first phase is *knowledge* — validated or refuted hypotheses and a go/no-go on productionization — not a finished product. The core questions (achievable hit-rate vs false-positive trade-off, embedding approach, similarity threshold, invalidation/freshness, personalization handling) are genuinely uncertain. The artifact set is therefore weighted heavily toward **research artifacts** — a research plan, an R&D backlog, a hypothesis register, multiple experiments, and a POC, each with explicit PASS/FAIL criteria and timeboxes — while **product artifacts are deliberately thin** until the go/no-go decision. Requirements here are partly framed as *research questions* and *provisional product requirements contingent on the go/no-go*, not as settled features to build now.

## Always (generated)

These are produced for every Keystone package regardless of profile:

- Charter (`00-charter.md`)
- Executive summary (`01-executive-summary.md`)
- Functional requirements (`requirements/functional.md`) — here, partly research questions + provisional product FRs contingent on DEC-001
- Non-functional requirements (`requirements/non-functional.md`)
- Constraint register (`requirements/constraint-register.md`)
- Assumption register (`decisions/assumption-register.md`)
- Open-question register (`decisions/open-question-register.md`)
- Open-decision register (`decisions/open-decision-register.md`)
- Risk register (`risks/risk-register.md`)
- Phased roadmap (`planning/roadmap.md`)
- Acceptance criteria (`validation/acceptance-criteria.md`)
- Traceability matrix (`validation/traceability-matrix.md`)
- Handoff initial prompt (`handoff/initial-prompt.md`)
- Execution-readiness report (`handoff/execution-readiness-report.md`)
- Manifest (`manifest.json`)
- README (`README.md`)

Note: in this profile the "requirements" are partly framed as **research questions plus provisional product requirements contingent on the go/no-go** (DEC-001). Most carry status **Proposed** and are explicitly marked as contingent — they describe what the cache *would* do if productionized, not committed scope.

## Conditional (triggered)

| Trigger | Add | Why |
|---------|-----|-----|
| **Genuine technical uncertainty (the core questions are unknown)** | **Research plan + R&D backlog + hypothesis register + MULTIPLE experiments + POC** (`research/`, `experiments/`, `pocs/`) | This is the heart of the package. The hit-rate/false-positive trade-off, embedding approach, and invalidation strategy are not knowable by reasoning — they must be measured. Hypotheses (HYP-001..003) drive experiments (EXP-001..003) and a latency POC (POC-001), each with PASS/FAIL and a timebox. |
| **≥ 2 viable options for embedding approach, similarity index, and invalidation strategy** | **Technology comparison** (`architecture/technology-comparison.md`) with **"needs-experiment" verdicts** | More than one credible option exists on each axis. The comparison frames the options and weighted criteria but deliberately reaches **no premature pick** — verdicts are "needs experiment EXP-002" etc. This is the no-premature-architecture safeguard in action. |
| **Architecturally significant — but only the cache-layer seam** | **Light architecture doc + ONE ADR** (`architecture/architecture.md`, `adrs/adr-0001-cache-layer-contract-and-safety-gate.md`) | Only the *seam/contract* (request → {hit \| miss}, mandatory safety gate, pluggable internals) is safe to lock now and is recorded as ADR-0001 (Approved). The rest of the architecture (which embedding model, which index, internal layout) is **DEFERRED pending the go/no-go**, not designed now. |
| **Non-trivial NFRs (false-positive rate, latency, cost reduction)** | **NFR thresholds + test/eval strategy** (`requirements/non-functional.md`, `validation/test-strategy.md`) | False-positive rate, cost reduction, and lookup latency are quantified, sourced to assumptions, and given an explicit evaluation methodology (the eval-set replay + threshold sweep + reference judging). |
| **Privacy constraint on stored prompts/responses** | **Compliance / privacy constraints** (`requirements/constraint-register.md`) | Cached prompts and responses are sensitive (ASM-003); encryption-at-rest, bounded retention, no third-party sharing, and no cross-user serving are recorded as hard constraints and traced into INV-002. |
| **Invariants present (safety properties)** | **Invariant register** (`requirements/invariant-register.md`) | Two safety properties are load-bearing: never return an answer below the similarity/safety bar (a miss beats a wrong hit), and never serve cached personalized/sensitive answers across user/context boundaries. Stated as INV-001/INV-002, plus auditability INV-003. |
| **External dependencies** | **Dependency register** (`requirements/dependency-register.md`) | The LLM API, an embedding model, and a vector index are external couplings the experiments depend on; kept vendor-neutral as abstractions. |
| **Handoff to Claude Code for the EXPERIMENT harness** | **Repo bootstrap + follow-up/review prompts + DoR/DoD** (`scripts/`, `handoff/`, `execution/definition-of-ready.md`, `execution/definition-of-done.md`) | The first thing built is an *evaluation harness*, not a product. It needs an init script, staged prompts (including the all-important phase-gate follow-up), and explicit ready/done gates framed as experiment PASS/FAIL. |

**Deferred, not generated now (recorded):** The **full productionization architecture** (component/deployment/data-flow diagrams beyond a context sketch), a **broad work-breakdown** for building the cache layer, and **progress-cadence artifacts** for a long build are **DEFERRED**. They are gated on the Phase-1 go/no-go (DEC-001, status **Deferred**) and would be premature to produce before the experiments resolve. Generating them now would imply a decision that has not been made. This deferral is itself recorded as a decision, not silently omitted.

**Kept minimal:** Greenfield product-discovery artifacts (personas, market analysis) and a deep cost/TCO model are omitted — the cost question here is answered empirically by EXP-001 (measured cost reduction on the eval set), not by a spreadsheet model.

One line: all omissions and deferrals, with their reasons and revisit triggers, are recorded in `manifest.json` and the open-decision register.
