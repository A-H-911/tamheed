# Generated package structure — repostat

The package below is **pruned to the selected set** (see `selected-artifacts.md`): research,
experiments, POCs, architecture diagrams, a long-horizon progress log, and a stakeholder register are
all omitted because no trigger holds. What remains is the Always set plus the few conditional artifacts
a handed-off small software project genuinely needs.

```text
repostat-package/
├── README.md                      # what this package is; reading order for the executing agent
├── 00-charter.md                  # problem, objectives, goals/non-goals, success metrics (KPI-)
├── 01-executive-summary.md        # one-page summary + recommendation
├── requirements/
│   ├── functional.md              # FR-001..FR-005 (+ filters as Full)
│   ├── non-functional.md          # NFR-001..NFR-003
│   ├── constraint-register.md     # CON- (offline-only, read-only, single binary/package)
│   ├── invariant-register.md      # INV-001 (read-only), INV-002 (deterministic output)
│   └── dependency-register.md     # DEP-001 (git on host), DEP-002 (pinned runtime, ASM-002)
├── decisions/
│   ├── open-question-register.md  # OQ- (e.g. timezone normalization for activity buckets)
│   ├── open-decision-register.md  # DEC- (incl. deferred author-identity merging)
│   └── assumption-register.md     # ASM-001..ASM-003
├── architecture/
│   └── architecture.md            # single short doc: report model + formatter seam (no diagrams/)
├── adrs/
│   └── adr-0001-export-format-and-rendering-seam.md   # immutable after approval
├── risks/
│   └── risk-register.md           # RISK-001 (huge repos), RISK-002 (author identity)
├── planning/
│   ├── roadmap.md                 # PH-1 (MVP), PH-2 (Full)
│   ├── work-breakdown.md          # WBS-1.x / WBS-2.x (terse, single developer)
│   └── milestones.md              # MS-001 (MVP usable), MS-002 (Full export set)
├── execution/
│   ├── definition-of-ready.md     # DoR for picking up a task
│   ├── definition-of-done.md      # DoD: tests pass, invariants honored, docs updated
│   └── checkpoints.md             # the PH-1 and PH-2 approval gates
├── validation/
│   ├── acceptance-criteria.md     # AC-001..AC-00n (Given/When/Then)
│   ├── test-strategy.md           # TEST- (fixture repos, golden-output determinism, perf budget)
│   └── traceability-matrix.md     # FR/NFR → DEC/ADR → WBS → TEST → AC  (DERIVED — regenerate)
├── handoff/
│   ├── initial-prompt.md          # first message to the execution agent (orient + 1 task + gate)
│   ├── follow-up-prompts.md       # one per phase gate + situational prompts
│   ├── review-prompts.md          # invariant audit, readiness recheck, PR-vs-AC review
│   ├── handoff-manifest.json      # conforms to handoff-package schema
│   └── execution-readiness-report.md  # Stage-22 go/no-go
├── scripts/
│   └── init_repo.sh               # bootstrap the TARGET repo (pin runtime per ASM-002)
├── keystone-state.json            # normalized state for resume/update (machine-owned)
└── manifest.json                  # artifacts present + versions + omission reasons
```

## Pruned (omitted) vs maximal

| Omitted | Reason |
|---|---|
| `research/`, `experiments/`, `pocs/` | No genuine technical uncertainty — nothing to investigate, test, or prototype. |
| `architecture/diagrams/` | The one seam is explained in a paragraph + ADR-0001; a diagram would add no understanding (anti-bloat). |
| `architecture/technology-comparison.md` | No ≥2-option weighted trade-off; the only runtime choice is ASM-002, not a comparison. |
| `planning/` stakeholder register | Single developer; a stakeholder register would be empty. |
| `progress/` (progress-log, status-report cadence) | Short two-phase horizon; `execution/checkpoints.md` covers the gates without a running log. |
| `governance/` (naming/contributing/governance) | Solo OSS tool; baseline governance lives in the charter/README, no separate suite needed. |
| `execution/backlog.md` | The roadmap + work-breakdown already sequence the work; a separate backlog would restate them. |

Each omission above is also recorded in `manifest.json` with its reason, so the dropped artifacts are
auditable rather than silently missing.
