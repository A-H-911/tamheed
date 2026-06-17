# Generated package structure — semantic-cache

The R&D / research-heavy profile produces a **research-weighted** package: the `research/` and `experiments/` areas are the richest part, product/architecture artifacts are deliberately thin (a light architecture doc, one ADR for the seam, no heavy diagram set), and productionization scaffolding is **deferred** pending the Phase-1 go/no-go. The layout below follows the standard Keystone package layout, trimmed to what this profile justifies.

```text
semantic-cache/
├── README.md
├── 00-charter.md
├── 01-executive-summary.md
├── requirements/
│   ├── functional.md                 # provisional product FRs + research framing (contingent on DEC-001)
│   ├── non-functional.md             # false-positive rate, cost reduction, latency, privacy thresholds
│   ├── constraint-register.md
│   ├── invariant-register.md         # safety gate + no cross-user serving + auditability
│   └── dependency-register.md        # LLM API, embedding model, vector index (all abstract)
├── decisions/
│   ├── open-question-register.md
│   ├── open-decision-register.md     # DEC-001/002/003 — Deferred pending experiments
│   └── assumption-register.md
├── research/                         # ← richest area in this profile
│   ├── research-plan.md              # questions, method, eval methodology, timeboxes, decision gates
│   ├── rnd-backlog.md                # prioritized de-risking tasks feeding the experiments
│   └── hypothesis-register.md        # HYP-001/002/003 with confirm/refute signals + linked experiments
├── experiments/
│   ├── exp-001-hit-rate-vs-false-positive.md     # the central experiment (gates DEC-001)
│   ├── exp-002-embedding-approach-comparison.md
│   └── exp-003-invalidation-staleness.md
├── pocs/
│   └── poc-001-cache-lookup-latency.md           # validates the ≤50ms p95 lookup budget (NFR-003)
├── architecture/
│   ├── architecture.md               # LIGHT — the cache-layer seam only; internals deferred
│   └── technology-comparison.md      # options + weighted criteria, "needs-experiment" verdicts
├── adrs/
│   └── adr-0001-cache-layer-contract-and-safety-gate.md   # the seam/contract — safe to lock now
├── risks/
│   └── risk-register.md
├── planning/
│   ├── roadmap.md                    # PH-1 = experiments/de-risking; PH-2 = productionize (GATED)
│   ├── work-breakdown.md             # LIGHT — mostly experiment/harness tasks for PH-1
│   └── milestones.md
├── execution/
│   ├── definition-of-ready.md
│   ├── definition-of-done.md         # framed as experiment PASS/FAIL + report produced
│   └── checkpoints.md                # the go/no-go gate after PH-1
├── validation/
│   ├── acceptance-criteria.md        # experiment PASS/FAIL + provisional product AC
│   ├── test-strategy.md              # the EVALUATION methodology (eval set, sweep, reference judging)
│   └── traceability-matrix.md        # HYP ↔ EXP ↔ DEC ↔ AC linkage
├── handoff/
│   ├── initial-prompt.md             # first bounded task = build the EVAL HARNESS, not a product
│   ├── follow-up-prompts.md          # the phase-gate go/no-go synthesis prompt
│   ├── review-prompts.md
│   ├── handoff-manifest.json
│   └── execution-readiness-report.md
├── keystone-state.json
└── manifest.json
```

Notes:
- `research/` is intentionally the **richest area**: this profile exists to produce knowledge, so the research plan, R&D backlog, and hypothesis register carry the most weight, feeding three experiments and one POC.
- `architecture/` is deliberately **thin**. There is a single light `architecture.md` describing only the cache-layer *seam*, and **no heavy `diagrams/` set** — at most a context sketch lives inside `architecture.md`. Designing internal components now would be premature: which embedding model, which index, and the internal layout are all **deferred pending DEC-001**.
- `adrs/` holds exactly **one** ADR (ADR-0001, the cache-layer contract and mandatory safety gate), because that is the only thing safe to lock before the experiments resolve. Internal-approach ADRs are deferred.
- `planning/work-breakdown.md` is **light** — mostly experiment and harness tasks for PH-1. The broad WBS for building the cache layer is not produced now.
- `keystone-state.json` records generation state and the conditional triggers that fired; `manifest.json` records the full file inventory and any omissions/deferrals with reasons.

**Deferred until the Phase-1 go/no-go (DEC-001, status Deferred):** the full productionization directories — a complete `architecture/diagrams/` set (component, deployment, data-flow, integration), a broad `planning/work-breakdown.md` for the build, and `progress/` cadence artifacts (progress log, status cadence). These are *not* generated now because producing them would imply a productionization decision that has not been made. They are recorded as deferred in `manifest.json` with the revisit trigger "DEC-001 = go".
