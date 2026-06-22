# Keystone Artifact Catalog

The authoritative, human-facing list of every artifact Keystone can produce, with its identifier prefix,
location in a generated package, generation class, lifecycle note, template, and schema. The **decision
logic** for which optional artifacts get generated is in
[`artifact-rules.md`](artifact-rules.md); the **package layout** is in
[`generated-structure.md`](generated-structure.md); the **identifiers,
statuses, and versioning** are in [`governance.md`](governance.md). This
catalog is the per-artifact reference those documents point back to.

## How to read this catalog

**Generation class** — when the artifact is produced:

- **Always** — every package gets it; skipping requires an explicit recorded reason.
- **Conditional** — generated when a trigger holds (project profile, size, risk, regulatory context, repo
  requested, etc.). The trigger is noted.
- **On-request** — produced only when the user asks.
- **Continuous** — created early and refreshed every update cycle (stage 21).
- **Derived** — computed from other artifacts; never hand-authored. Regenerate, don't edit.

**Lifecycle note** — how the artifact changes over time: *versioned-on-change* (carries front-matter
`status`/`version`/`updated`, bumped on material change), *immutable-after-approval* (never edited in meaning;
superseded instead), *derived-regenerate* (reproduced from sources), or *machine-owned* (written and read by
Keystone's runtime, not hand-edited).

**Location** is relative to the generated `<project-package>/` root. **Template** paths are relative to the
Keystone repo-root `templates/` directory; **Schema** paths to the repo-root `schemas/` directory. A `—` in
the Schema column means the artifact is narrative Markdown with no separate structured schema. Multiple
register kinds that share one register file (e.g. open questions / open decisions / assumptions under
`decisions/`) are listed on their own rows for clarity.

> Templates and schemas are bundled alongside this catalog in `../templates/` and `../schemas/` — the skill
> is self-contained. The exact template/schema filenames below follow the naming convention
> `<name>.template.md` / `<name>.schema.json`; if a packaged repo renames one, the catalog row is the place
> that records it.

---

## Charter & scope

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Project charter | (hosts `KPI-`) | `00-charter.md` | Always | versioned-on-change; Proposed→Approved at scope lock (stage 8) | `templates/project-charter.template.md` | — |
| Executive summary | — | `01-executive-summary.md` | Always | versioned-on-change | `templates/executive-summary.template.md` | — |
| Problem statement | — | `00-charter.md` (section) | Always | versioned-on-change | (within charter template) | — |
| Goals / non-goals | — | `00-charter.md` (section) | Always | versioned-on-change; locked at stage 8 | (within charter template) | — |
| Scope / out-of-scope | — | `00-charter.md` (section) | Always | versioned-on-change; scope drift after lock needs a `DEC-` | (within charter template) | — |
| Success metrics / KPIs | `KPI-` | `00-charter.md` (success-metrics section) | Always | versioned-on-change | (within charter template) | — |
| Stakeholder register | `STK-` | `stakeholder-register.md` | Conditional — cross-team / multi-actor delivery | versioned-on-change | `templates/stakeholder-register.template.md` | — |

## Requirements & registers

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Functional requirements | `FR-` | `requirements/functional.md` | Always | versioned-on-change; every row carries a `source` | `templates/functional-requirements.template.md` | `schemas/requirement.schema.json` |
| Non-functional requirements | `NFR-` | `requirements/non-functional.md` | Always | versioned-on-change; every row carries a `source` | `templates/non-functional-requirements.template.md` | `schemas/requirement.schema.json` |
| Constraint register | `CON-` | `requirements/constraint-register.md` | Always | versioned-on-change | `templates/constraint-register.template.md` | `schemas/constraint.schema.json` |
| Invariant register | `INV-` | `requirements/invariant-register.md` | Conditional — invariants present | versioned-on-change; invariants are non-negotiable, surfaced early in handoff | `templates/invariant-register.template.md` | `schemas/invariant.schema.json` |
| Assumption register | `ASM-` | `decisions/assumption-register.md` | Always | versioned-on-change; each row carries `risk_if_wrong` | `templates/assumption-register.template.md` | `schemas/assumption.schema.json` |
| Dependency register | `DEP-` | `requirements/dependency-register.md` | Conditional — external dependencies | versioned-on-change | `templates/dependency-register.template.md` | `schemas/dependency.schema.json` |
| Open-question register | `OQ-` | `decisions/open-question-register.md` | Always | versioned-on-change; first-class, surfaced in readiness report | `templates/open-question-register.template.md` | `schemas/open-question.schema.json` |
| Open-decision register | `DEC-` | `decisions/open-decision-register.md` | Always | versioned-on-change; status ∈ Proposed/Approved/Rejected/Superseded/Deferred | `templates/open-decision-register.template.md` | `schemas/decision.schema.json` |

## Research & experiments

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Research plan | — | `research/research-plan.md` | Conditional — genuine technical uncertainty | versioned-on-change; timeboxed, proportional to risk | `templates/research-plan.template.md` | — |
| R&D backlog | — | `research/rnd-backlog.md` | Conditional — genuine technical uncertainty | versioned-on-change | `templates/rnd-backlog.template.md` | — |
| Hypothesis register | `HYP-` | `research/hypothesis-register.md` | Conditional — unknowns blocking decisions | versioned-on-change; hypotheses are falsifiable | `templates/hypothesis-register.template.md` | `schemas/hypothesis.schema.json` |
| Experiment plans | `EXP-` | `experiments/` | Conditional — decision-blocking hypothesis exists | versioned-on-change; each has PASS/FAIL + timebox | `templates/experiment-plan.template.md` | `schemas/experiment.schema.json` |
| POC plans + results | `POC-` | `pocs/` | Conditional — decision-blocking hypothesis exists | versioned-on-change; results appended, not overwritten | `templates/poc-plan.template.md` | `schemas/experiment.schema.json` |
| Evaluation framework | — | `research/research-plan.md` (or `architecture/technology-comparison.md`) | Conditional — ≥2 viable options to weigh | versioned-on-change; weighted criteria stated before scoring | — (section within research-plan / technology-comparison) | `schemas/comparison-criteria.schema.json` |

## Architecture & decisions

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Architecture document | — | `architecture/architecture.md` | Conditional — architecturally significant decisions | versioned-on-change; must cover all MVP requirements | `templates/architecture.template.md` | — |
| Context diagram | — | `architecture/diagrams/` | Conditional — architecture doc generated | versioned-on-change; only if it adds understanding | — (diagram-as-code in the architecture doc) | — |
| Component diagram | — | `architecture/diagrams/` | Conditional — architecture doc generated | versioned-on-change | — (diagram-as-code in the architecture doc) | — |
| Deployment diagram | — | `architecture/diagrams/` | On-request (beyond MVP) | versioned-on-change | — (diagram-as-code in the architecture doc) | — |
| Data-flow diagram | — | `architecture/diagrams/` | On-request (beyond MVP) | versioned-on-change | — (diagram-as-code in the architecture doc) | — |
| Integration diagram | — | `architecture/diagrams/` | Conditional — multiple integrated systems | versioned-on-change | — (diagram-as-code in the architecture doc) | — |
| Architecture Decision Record | `ADR-NNNN` | `adrs/adr-NNNN-*.md` | Conditional — a significant decision is promoted | **immutable-after-approval**; supersede, never rewrite | `templates/adr.template.md` | — |
| Technology comparison matrices | — | `architecture/technology-comparison.md` | Conditional — ≥2 viable technology options | versioned-on-change; losers retained, claims cited/`unverified` | `templates/technology-comparison.template.md` | — |
| Technology assessments | — | `architecture/technology-comparison.md` (section) | Conditional — a candidate needs a deeper standalone evaluation | versioned-on-change | `templates/technology-comparison.template.md` | — |

## Risk

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Risk register | `RISK-` | `risks/risk-register.md` | Always | versioned-on-change; impact·likelihood·mitigation·trigger·MVP-or-Full | `templates/risk-register.template.md` | `schemas/risk.schema.json` |
| Mitigation plan | — | `risks/risk-register.md` (mitigation fields) | Always (with risk register) | versioned-on-change | (within risk-register template) | `schemas/risk.schema.json` |

## Planning & execution

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Phased roadmap | `PH-` | `planning/roadmap.md` | Always | versioned-on-change; each phase has goal/scope/deliverables/validation/risks/exit | `templates/roadmap.template.md` | — |
| Work breakdown | `WBS-N.N` | `planning/work-breakdown.md` | Conditional — non-trivial / multi-actor delivery | versioned-on-change; leaf items actionable + testable | `templates/work-breakdown.template.md` | — |
| Milestones | `MS-` | `planning/milestones.md` | Conditional — multi-phase delivery | versioned-on-change | `templates/milestones.template.md` | — |
| Execution backlog | — | `execution/backlog.md` | Conditional — handoff to a coding agent | versioned-on-change | — (derived from work-breakdown) | — |
| Deferred-work / tech-debt register | — | `execution/deferred-work-register.md` | Conditional — long execution horizon / handoff | versioned-on-change; durable index of known-not-done + accepted debt (distinct from the forward backlog) | `templates/deferred-work-register.template.md` | — |
| Definition of Ready | — | `execution/definition-of-ready.md` | Conditional — repo requested / handoff | versioned-on-change | `templates/definition-of-ready.template.md` | — |
| Definition of Done | — | `execution/definition-of-done.md` | Conditional — repo requested / handoff | versioned-on-change | `templates/definition-of-done.template.md` | — |
| Checkpoints (review/approval gates) | — | `execution/checkpoints.md` | Conditional — long execution horizon | versioned-on-change | — (no dedicated template) | — |

## Validation & traceability

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Acceptance criteria | `AC-` | `validation/acceptance-criteria.md` | Always | **immutable-after-approval** once accepted; testable, MVP + full target; optional Evidence column | `templates/acceptance-criteria.template.md` | `schemas/acceptance-criterion.schema.json` |
| Acceptance audit | `AC-` (refs) | `validation/acceptance-audit.md` | **Derived** — Conditional (handoff / long execution horizon) | **derived-regenerate** each gate; criterion → verdict (Met/Partial/Not-met/Pending) × evidence; the downstream agent's during/after-execution close-out — distinct from the planner's pre-handoff readiness report; gate **G-PROGRESS** checks AC coverage | `templates/acceptance-audit.template.md` | — |
| Test strategy | `TEST-` | `validation/test-strategy.md` | Conditional — non-trivial NFRs / handoff | versioned-on-change | `templates/test-strategy.template.md` | — |
| Validation strategy | — | `validation/test-strategy.md` (validation-approach section) | Conditional — non-trivial NFRs / regulatory | versioned-on-change | (within test-strategy template) | — |
| Traceability matrix | — | `validation/traceability-matrix.md` | **Derived** (Always) | **derived-regenerate**; FR/NFR → DEC/ADR → WBS → TEST → RISK → AC | `templates/traceability-matrix.template.md` | `schemas/traceability-row.schema.json` |

## Progress

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Progress log | — | `progress/progress-log.md` | Continuous — long execution horizon | append-only; updated each cycle (stage 21) | `templates/progress-log.template.md` | — |
| Status report | — | `progress/status-report.md` | **Derived** / Continuous | **derived-regenerate** each update cycle | `templates/status-report.template.md` | — |

## Handoff

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Handoff instructions (overview) | — | `handoff/` (README/overview) | Always | versioned-on-change | — (no dedicated template) | — |
| Initial prompt | — | `handoff/initial-prompt.md` | Always | versioned-on-change; orient + one bounded task + approval gate | `templates/initial-prompt.template.md` | — |
| Follow-up prompts | — | `handoff/follow-up-prompts.md` | Conditional — multi-phase / repo handoff | versioned-on-change; one per phase gate + situational | `templates/follow-up-prompts.template.md` | — |
| Review prompts | — | `handoff/review-prompts.md` | Conditional — repo handoff | versioned-on-change; audit / readiness-recheck / PR review | `templates/review-prompts.template.md` | — |
| Handoff manifest | — | `handoff/handoff-manifest.(yaml\|json)` | Always | machine-owned; versioned | `templates/handoff-manifest.template.md` | `schemas/handoff-package.schema.json` |
| Final execution-readiness report | — | `handoff/execution-readiness-report.md` | Always | **derived-regenerate**; stage-22 go/no-go on Critical gates | `templates/execution-readiness-report.template.md` | — |

## Governance & repository

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Repository bootstrap script | — | `scripts/init_repo.*` (target repo) | Conditional — repo requested | versioned-on-change; dry-run-capable, idempotent, never-overwrite | — (emitted by `scripts/`, not a template) | — |
| Contribution doc | — | `governance/contributing.md` | Conditional — repo / multi-contributor | versioned-on-change | `templates/contributing.template.md` | — |
| Governance doc | — | `governance/governance.md` | Conditional — repo / multi-contributor | versioned-on-change | `templates/governance.template.md` | — |
| Naming conventions | — | `governance/naming-conventions.md` | Conditional — repo / multi-contributor | versioned-on-change | `templates/naming-conventions.template.md` | — |
| Documentation templates | — | `governance/` (or `docs/templates/`) | On-request | versioned-on-change | — (no dedicated template) | — |
| Review / approval gates (definitions) | — | `execution/checkpoints.md` + readiness report | Always (definitions); applied at gates | versioned-on-change | (within checkpoints template) | — |

## Package-level

| Artifact | ID prefix | Location | Generation class | Lifecycle note | Template | Schema |
|---|---|---|---|---|---|---|
| Package README | — | `README.md` | Always | versioned-on-change; consumption + reading order for the agent | `templates/package-readme.template.md` | — |
| Agent-control surface | — | `CLAUDE.md` (imports `AGENTS.md`) | **Derived** — Conditional (handoff / repo requested) | **derived-regenerate**; the ambient control surface Claude Code auto-loads — `CLAUDE.md` at the package/repo root importing `AGENTS.md`: invariants (violation⇒ADR) + hard constraints + conventions + current-phase pointer + tracking protocol; renders/links the registers (not a second copy); also emitted into a bootstrapped repo by `scripts/init_repo.*` | `templates/agent-control.template.md` | — |
| Package manifest | — | `manifest.json` | Always | machine-owned; lists artifacts present, versions, generation metadata, omission reasons | `templates/package-manifest.template.md` | `schemas/package-manifest.schema.json` |
| Normalized state | — | `keystone-state.json` | Always | **machine-owned**; powers resume/update; never hand-edited | — | `schemas/keystone-state.schema.json` |

---

## Quick view: the Always set

Every package, absent an explicit recorded reason to skip, contains: charter (with problem statement,
goals/non-goals, scope/out-of-scope, success metrics), executive summary, functional and non-functional
requirements, constraint register, assumption register, open-question register, open-decision register, risk
register (with mitigations), phased roadmap, acceptance criteria, traceability matrix (derived), handoff
overview + initial prompt + handoff manifest, execution-readiness report, package README, package manifest,
and normalized state. Everything else is Conditional, On-request, Continuous, or Derived per the rows above
and the triggers in [`artifact-rules.md`](artifact-rules.md).

## Lifecycle quick reference

- **Immutable-after-approval:** ADRs; approved acceptance criteria. Change by superseding, never by rewriting
  meaning (typo fixes allowed).
- **Derived-regenerate (never hand-edit):** traceability matrix, execution-readiness report, status report,
  roadmap rollups.
- **Machine-owned:** `keystone-state.json`, `manifest.json`, the handoff manifest.
- **Continuous:** progress log (append-only), status report (regenerated each cycle).
- **Everything else:** versioned-on-change — carries front-matter `status` / `version` / `updated`, bumped on
  material change, following [`governance.md`](governance.md).

## Anti-bloat reminder

An artifact is generated only when it earns its keep. If it would merely restate another, **derive or link**
instead of duplicating; if a section has no project-specific content, **omit** it rather than emit a
placeholder; prefer one well-populated register over several thin ones; and a diagram must add understanding a
paragraph cannot. Any artifact in the selected set that ends up empty is dropped, and the omission reason is
recorded in `manifest.json` (safeguard 11; gates G-BLOAT and G-COMPLETE).
