# Generated package structure

The layout Keystone produces **for a target project** (distinct from the Keystone repo itself). Create only
the directories the selected artifact set needs (see `artifact-rules.md`); this is the maximal shape.

```
<project-package>/
├── README.md                      # what this package is, how an agent should consume it, reading order
├── 00-charter.md                  # charter: problem, objectives, goals/non-goals, success metrics (KPI-)
├── 01-executive-summary.md        # one-page summary + final recommendation
├── requirements/
│   ├── functional.md              # FR-
│   ├── non-functional.md          # NFR-
│   ├── constraint-register.md     # CON-
│   ├── invariant-register.md      # INV-
│   └── dependency-register.md     # DEP-
├── decisions/
│   ├── open-question-register.md  # OQ-
│   ├── open-decision-register.md  # DEC- (status: Proposed/Approved/Rejected/Superseded/Deferred)
│   └── assumption-register.md     # ASM- (+ risk-if-wrong)
├── research/
│   ├── research-plan.md
│   ├── rnd-backlog.md
│   └── hypothesis-register.md     # HYP-
├── experiments/                   # EXP- experiment plans
├── pocs/                          # POC- proof-of-concept plans + results
├── architecture/
│   ├── architecture.md            # recommended architecture, component model, contracts
│   ├── technology-comparison.md   # weighted comparison matrices + verdicts
│   └── diagrams/                  # context / component / deployment / data-flow / integration
├── adrs/                          # adr-NNNN-*.md (immutable after approval)
├── risks/
│   └── risk-register.md           # RISK- (impact·likelihood·mitigation·MVP-or-full)
├── planning/
│   ├── roadmap.md                 # PH- phases (goal/scope/deliverables/validation/risks/exit)
│   ├── work-breakdown.md          # WBS-
│   └── milestones.md              # MS-
├── execution/
│   ├── backlog.md
│   ├── definition-of-ready.md
│   ├── definition-of-done.md
│   └── checkpoints.md             # review/approval gates during execution
├── validation/
│   ├── acceptance-criteria.md     # AC- (MVP + full target, testable)
│   ├── test-strategy.md           # TEST-
│   └── traceability-matrix.md     # FR/NFR → DEC/ADR → WBS → TEST → RISK → AC (derived)
├── progress/
│   ├── progress-log.md
│   └── status-report.md           # regenerated each update cycle
├── handoff/
│   ├── initial-prompt.md          # first message for the execution agent
│   ├── follow-up-prompts.md       # one per phase gate + situational prompts
│   ├── review-prompts.md          # audit / readiness-recheck prompts
│   ├── handoff-manifest.<yaml|json>   # conforms to handoff-package schema
│   └── execution-readiness-report.md  # final gate result
├── scripts/
│   └── init_repo.*                # bootstrap for the TARGET project's own repo (optional)
├── governance/
│   ├── naming-conventions.md
│   ├── contributing.md
│   └── governance.md
├── keystone-state.json            # normalized state for resume/update (machine-owned)
└── manifest.json                  # package manifest: artifacts present, versions, generation metadata
```

## Distinctions to preserve

- **Keystone source** (the `plugins/tamheed/` skill bundle) vs **generated output** (a
  `<project-package>/` like the above). Never write generated output into the Keystone source tree except
  under `generated-samples/` for demonstration.
- **Templates** (`../templates/`, blank forms) vs **filled artifacts** (in a generated package).
- **Schemas** (`../schemas/`, data shapes) vs **instances** (`keystone-state.json`, `handoff-manifest`).
- **Machine-readable** data (YAML/JSON: state, manifests, registers' structured fields) vs
  **human-readable** narrative (Markdown). When a register needs both, keep Markdown as the readable
  surface and mirror structured fields the schema defines.

## Minimal vs maximal

A tiny project may collapse to `README.md`, `00-charter.md`, `requirements/`, `decisions/`,
`planning/roadmap.md`, `validation/acceptance-criteria.md`, and `handoff/`. The artifact-selection rules
decide; do not emit empty directories or stub files that add no operational value.
