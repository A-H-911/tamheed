# Selected artifact set — unify-billing

**Profile: ENTERPRISE PLATFORM.** A new, multi-tenant, financially sensitive platform with cross-team delivery, regulatory exposure (SOC2), architecturally significant decisions, genuine technical uncertainty (metering/ledger), and a coding-agent handoff. This profile triggers a broad, near-maximal artifact set. The selection below is the package Keystone will generate.

## Always (generated)

These are produced for every Keystone package regardless of profile:

- Project charter (`00-charter.md`)
- Executive summary (`01-executive-summary.md`)
- Functional requirements (`requirements/functional.md`)
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

## Conditional (triggered)

| Trigger | Add | Why |
|---------|-----|-----|
| Genuine technical uncertainty (metering accuracy + ledger design) | Research plan (`research/research-plan.md`), R&D backlog (`research/rnd-backlog.md`), hypothesis register (`research/hypothesis-register.md`), one experiment (`experiments/`) and one POC (`pocs/`) | Usage-metering accuracy/latency and ledger-vs-event-log are unproven; needs structured investigation (EXP-001, POC-001, HYP-001) before committing Phase-2 scope. |
| Architecturally significant decisions | Architecture doc (`architecture/architecture.md`), ADRs (`adrs/`), diagrams (`architecture/diagrams/`) | Money model, isolation model, provider boundary, and sync-vs-async invoicing are foundational and hard to reverse; must be documented and decided. |
| ≥2 viable options on key choices (ledger approach; sync vs async invoicing; provider abstraction style) | Technology comparison (`architecture/technology-comparison.md`) | Each choice has real, competing options that warrant weighted comparison feeding ADR-0001/0002/0003. |
| Cross-team delivery (platform team, product teams, finance) | Stakeholder register (`planning/` — within charter/WBS context), work breakdown (`planning/work-breakdown.md`), milestones (`planning/milestones.md`) | Multiple teams and a finance sign-off gate require explicit ownership, decomposition, and dated milestones. |
| Non-trivial NFRs (correctness, scale, isolation) | NFR thresholds (`requirements/non-functional.md`, quantified), test strategy (`validation/test-strategy.md`) | Correctness/scale/isolation must be measurable and verifiable, not aspirational. |
| Regulatory / compliance (SOC2, financial audit) | Compliance constraints (`requirements/constraint-register.md`), validation-evidence plan (`validation/test-strategy.md` evidence section) | SOC2 scope and auditability impose controls and evidence obligations that must be tracked from MVP. |
| Invariants present (money correctness, tenant isolation, idempotency) | Invariant register (`requirements/invariant-register.md`) | These are always-true properties that constrain every change; they get first-class, referenceable IDs (INV-001..INV-004). |
| External dependencies (payment provider, tax service, identity, FX) | Dependency register (`requirements/dependency-register.md`) | Each external system is a risk and integration surface that must be tracked (DEP-001..DEP-004). |
| Long delivery horizon (multi-phase) | Progress log (`progress/progress-log.md`), status cadence (`progress/status-report.md`), checkpoints (`execution/checkpoints.md`) | Multi-phase work needs ongoing tracking and explicit gates between phases. |
| Repo / coding-agent handoff | Repo bootstrap (`scripts/init_repo.*`), follow-up + review prompts (`handoff/follow-up-prompts.md`, `handoff/review-prompts.md`), Definition of Ready / Done (`execution/definition-of-ready.md`, `execution/definition-of-done.md`) | An execution agent needs an orientation flow, bounded tasks, review prompts, and explicit DoR/DoD gates. |

A deep cost/budget model is **on-request only** and is **not** generated for this package.

Omissions and any not-generated optional artifacts are recorded in `manifest.json`.
