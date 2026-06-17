# Generated package structure — support-triage-agent

The AI-AGENTIC SYSTEM profile produces the rich, near-maximal layout below. Each path corresponds to a triggered or always-on artifact from `selected-artifacts.md`.

```text
support-triage-agent/
├── README.md
├── 00-charter.md
├── 01-executive-summary.md
├── requirements/
│   ├── functional.md
│   ├── non-functional.md
│   ├── constraint-register.md
│   ├── invariant-register.md
│   └── dependency-register.md
├── decisions/
│   ├── open-question-register.md
│   ├── open-decision-register.md
│   └── assumption-register.md
├── research/
│   ├── research-plan.md
│   ├── rnd-backlog.md
│   └── hypothesis-register.md
├── experiments/
│   └── exp-001-confidence-calibration.md
├── pocs/
│   └── poc-001-bounded-agent-loop.md
├── architecture/
│   ├── architecture.md
│   ├── technology-comparison.md
│   └── diagrams/
│       ├── context.md
│       ├── component.md
│       ├── data-flow.md
│       └── integration.md
├── adrs/
│   ├── adr-0001-human-in-the-loop-gate.md
│   ├── adr-0002-retrieval-grounded-drafting.md
│   ├── adr-0003-bounded-agent-loop.md
│   └── adr-0004-confidence-routing.md
├── risks/
│   └── risk-register.md
├── planning/
│   ├── roadmap.md
│   ├── work-breakdown.md
│   └── milestones.md
├── execution/
│   ├── backlog.md
│   ├── definition-of-ready.md
│   ├── definition-of-done.md
│   └── checkpoints.md
├── validation/
│   ├── acceptance-criteria.md
│   ├── test-strategy.md
│   └── traceability-matrix.md
├── progress/
│   ├── progress-log.md
│   └── status-report.md
├── governance/
│   ├── naming-conventions.md
│   ├── contributing.md
│   └── governance.md
├── handoff/
│   ├── initial-prompt.md
│   ├── follow-up-prompts.md
│   ├── review-prompts.md
│   ├── handoff-manifest.json
│   └── execution-readiness-report.md
├── scripts/
│   └── init_repo.sh        # and/or init_repo.ps1
├── keystone-state.json
└── manifest.json
```

Note: this same project is fully expanded — with the complete file contents rather than excerpts — under `generated-samples/support-triage-agent/`. The two share the identifier scheme exactly (FR-/NFR-/INV-/DEP-/ADR-/RISK-/HYP-/EXP-/KPI-/PH-/AC-).
