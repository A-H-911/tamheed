# Generated package structure — claims-portal-modernization

The legacy-modernization profile produces a rich package: most directories are present because the work is architecturally significant, risk- and migration-heavy, and compliance-bearing. Research/experiments are kept light (a single de-risking spike). The layout below follows the standard Keystone package layout.

```text
claims-portal-modernization/
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
│   └── hypothesis-register.md          # data-sync consistency spike (HYP-001)
├── experiments/
│   └── exp-001-dual-read-consistency.md
├── architecture/
│   ├── architecture.md
│   ├── technology-comparison.md
│   └── diagrams/
│       ├── context.md
│       ├── component.md
│       ├── deployment.md
│       ├── data-flow.md
│       └── integration.md
├── adrs/
│   ├── adr-0001-strangler-facade-routing.md
│   ├── adr-0002-data-sync-strategy.md
│   └── adr-0003-per-slice-rollback.md
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
│   └── init_repo.sh                    # also init_repo.ps1 for Windows hosts
├── keystone-state.json
└── manifest.json
```

Notes:
- `research/` and `experiments/` are intentionally minimal — one spike (EXP-001) validating the dual-read consistency hypothesis (HYP-001) that gates PH-2. No broader research program.
- `architecture/diagrams/` carries the full five-view set because the strangler seam and data strategy are the heart of this engagement.
- `governance/naming-conventions.md` pins the ID scheme and decision statuses used throughout the package.
- `keystone-state.json` records generation state and the conditional triggers that fired; `manifest.json` records the full file inventory and any omissions with reasons.
