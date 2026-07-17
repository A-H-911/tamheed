# Keystone Templates

Blank, fillable forms Keystone uses to generate a project package. Each is a real template — YAML
front-matter (`status`, `version`, `updated`, `owner`), section headings, `<placeholder>` markers, example
identifier rows, and `<!-- guidance -->` comments telling the filler what goes where.

**Use:** the skill copies the relevant `.template.md` into a generated package per
`../references/artifact-rules.md` and the catalog in `../references/artifact-catalog.md`, fills the placeholders
from project state, and removes the guidance comments. These are blank forms — never filled artifacts; filled
artifacts live in a generated `<project-package>/` (see `../references/generated-structure.md`).

**Conventions:** identifiers, statuses, versioning, and cross-references follow
`../references/governance.md`. All templates are vendor/provider-neutral.

**Generation classes** (see `artifact-rules.md`): **Always** (every package) · **Conditional** (trigger
holds) · **On-request** · **Continuous** (created early, updated each cycle) · **Derived** (generated from
other artifacts; never hand-authored).

## Index

| Template | Produces (artifact / package path) | Generation class |
|---|---|---|
| `project-charter.template.md` | Charter — problem, objectives, scope, success metrics (`KPI-`), stakeholders (`STK-`) → `00-charter.md` | Always |
| `executive-summary.template.md` | One-page summary + recommendation → `01-executive-summary.md` | Always |
| `functional-requirements.template.md` | Functional requirements (`FR-`) → `requirements/functional.md` | Always |
| `non-functional-requirements.template.md` | Non-functional requirements (`NFR-`, measurable) → `requirements/non-functional.md` | Always |
| `constraint-register.template.md` | Constraints (`CON-`) → `requirements/constraint-register.md` | Always |
| `invariant-register.template.md` | Invariants / non-negotiables (`INV-`) → `requirements/invariant-register.md` | Conditional (invariants present) |
| `dependency-register.template.md` | Dependencies (`DEP-`) → `requirements/dependency-register.md` | Conditional (external dependencies) |
| `assumption-register.template.md` | Assumptions (`ASM-`, + `risk_if_wrong`) → `decisions/assumption-register.md` | Always |
| `open-question-register.template.md` | Open questions (`OQ-`) → `decisions/open-question-register.md` | Always |
| `open-decision-register.template.md` | Lightweight decisions (`DEC-`, + ADR promotion) → `decisions/open-decision-register.md` | Always |
| `adr.template.md` | One Architecture Decision Record (`ADR-NNNN`, immutable) → `adrs/adr-NNNN-*.md` | Conditional (significant decisions) |
| `risk-register.template.md` | Risks (`RISK-`) → `risks/risk-register.md` | Always |
| `research-plan.template.md` | Research plan → `research/research-plan.md` | Conditional (genuine uncertainty) |
| `rnd-backlog.template.md` | R&D backlog → `research/rnd-backlog.md` | Conditional (genuine uncertainty) |
| `hypothesis-register.template.md` | Hypotheses (`HYP-`) → `research/hypothesis-register.md` | Conditional (genuine uncertainty) |
| `experiment-plan.template.md` | Experiment plan (`EXP-`, PASS/FAIL) → `experiments/` | Conditional (genuine uncertainty) |
| `poc-plan.template.md` | Proof-of-concept plan (`POC-`, go/no-go) → `pocs/` | Conditional (genuine uncertainty) |
| `architecture.template.md` | Architecture (context, components, contracts) → `architecture/architecture.md` | Conditional (significant decisions) |
| `technology-comparison.template.md` | Weighted comparison matrix (keep losers) → `architecture/technology-comparison.md` | Conditional (>=2 viable options) |
| `roadmap.template.md` | Phased roadmap (`PH-`) → `planning/roadmap.md` | Always |
| `work-breakdown.template.md` | Work breakdown (`WBS-`) → `planning/work-breakdown.md` | Conditional (multi-actor delivery) |
| `milestones.template.md` | Milestones (`MS-`) → `planning/milestones.md` | Conditional (multi-actor delivery) |
| `acceptance-criteria.template.md` | Acceptance criteria (`AC-`, MVP + Full) → `validation/acceptance-criteria.md` | Always |
| `test-strategy.template.md` | Test strategy (`TEST-`) → `validation/test-strategy.md` | Conditional (non-trivial NFRs) |
| `traceability-matrix.template.md` | Traceability `FR/NFR → DEC/ADR → WBS → TEST → RISK → AC` → `validation/traceability-matrix.md` | Derived |
| `stakeholder-register.template.md` | Stakeholders (`STK-`) → `governance/` (or charter context) | Conditional (multi-actor delivery) |
| `definition-of-ready.template.md` | Definition of Ready checklist → `execution/definition-of-ready.md` | Conditional (handoff to Claude Code) |
| `definition-of-done.template.md` | Definition of Done checklist → `execution/definition-of-done.md` | Conditional (handoff to Claude Code) |
| `progress-log.template.md` | Append-only progress history → `progress/progress-log.md` | Continuous (long horizon) |
| `status-report.template.md` | Regenerated status snapshot → `progress/status-report.md` | Continuous (long horizon) |
| `initial-prompt.template.md` | First execution-agent prompt (orient → 1 task → stop) → `handoff/initial-prompt.md` | Always |
| `follow-up-prompts.template.md` | Per-phase + situational prompts → `handoff/follow-up-prompts.md` | Conditional (handoff to Claude Code) |
| `review-prompts.template.md` | Audit / readiness / PR-review prompts → `handoff/review-prompts.md` | Conditional (handoff to Claude Code) |
| `handoff-manifest.template.md` | Handoff contract (mirrors `handoff-package.schema.json`) → `handoff/handoff-manifest.(yaml\|json)` | Always |
| `execution-readiness-report.template.md` | Per-gate go/no-go + residual risks → `handoff/execution-readiness-report.md` | Always |
| `package-readme.template.md` | README for the generated package (reading order, how to consume) → `README.md` | Always |
| `package-manifest.template.md` | Package inventory + metadata (mirrors `manifest.json`) → `manifest.json` | Always |
| `naming-conventions.template.md` | Package naming/identifier conventions → `governance/naming-conventions.md` | Conditional (handoff to Claude Code) |
| `contributing.template.md` | How to change the package without breaking governance → `governance/contributing.md` | Conditional (handoff to Claude Code) |
| `governance.template.md` | Package rules of record (ids, statuses, versioning) → `governance/governance.md` | Conditional (handoff to Claude Code) |

## Notes

- **One entity family per register**, one ADR per file. Filenames are kebab-case (`../references/governance.md`).
- **Derived** templates (`traceability-matrix`) and regenerated snapshots (`status-report`) are produced from
  state/sources — fill once as a starting shape, then regenerate; do not hand-maintain.
- Templates whose structured form mirrors a schema (`handoff-manifest`, `package-manifest`) keep the
  YAML/JSON block authoritative and the Markdown as the readable surface.
- Drop any template whose artifact would be empty for the project, and record the omission in the package
  manifest (anti-bloat, `artifact-rules.md`).
