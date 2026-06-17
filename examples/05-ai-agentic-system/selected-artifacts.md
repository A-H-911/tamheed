# Selected artifact set — support-triage-agent

**Profile: AI-AGENTIC SYSTEM.** A supervised, autonomous-but-bounded agent that acts on customer-facing email. The defining concerns are *safety invariants*, *grounding/no-hallucination*, *PII containment*, *bounded tool use and cost*, *full auditability*, and a *calibration experiment that gates auto-send*. This profile is safety/eval/architecture-heavy and triggers a broad artifact set. The selection below is the package Keystone will generate.

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
| Safety/agentic uncertainty — classification accuracy and confidence calibration are unproven | Research plan, light (`research/research-plan.md`), R&D backlog (`research/rnd-backlog.md`), hypothesis register (`research/hypothesis-register.md`), one experiment (`experiments/exp-001-confidence-calibration.md`), one POC (`pocs/poc-001-bounded-agent-loop.md`) | Accuracy ≥ bar and a confidence threshold that yields a safe auto-send subset are hypotheses (HYP-001), not facts; EXP-001 must validate them before FR-008/ADR-0004 unlock. The bounded-loop POC retires the runaway-cost risk early (RISK-004). |
| Architecturally significant decisions (HITL gate, RAG grounding, bounded loop, confidence routing) | Architecture doc (`architecture/architecture.md`), ADRs (`adrs/`), diagrams (`architecture/diagrams/`) | The approval gate, grounding boundary, bounded agent loop, and routing policy are foundational, safety-bearing, and hard to reverse; they must be documented and decided (ADR-0001..ADR-0004). |
| ≥2 viable options on key choices (agent-orchestration pattern; retrieval approach) | Technology comparison (`architecture/technology-comparison.md`) | Each choice has real competing options that warrant weighted comparison feeding the ADRs. |
| Cross-team delivery (Support Ops, Security, Engineering) | Stakeholder register (within charter), work breakdown (`planning/work-breakdown.md`), milestones (`planning/milestones.md`) | Taxonomy ownership, PII-policy ownership, and a build team require explicit ownership, decomposition, and dated milestones. |
| Non-trivial NFRs (accuracy, latency, cost, PII) | NFR thresholds, quantified (`requirements/non-functional.md`), test strategy + eval strategy (`validation/test-strategy.md`) | Accuracy/latency/cost/PII must be measurable and verifiable, not aspirational; the eval strategy defines how NFR-001 is measured. |
| Privacy / compliance (PII) | Compliance / privacy constraints (`requirements/constraint-register.md`), validation-evidence plan (`validation/test-strategy.md` evidence section) | PII handling imposes controls and evidence obligations (ASM-003, INV-003) that must be tracked from PH-1. |
| Safety invariants present | Invariant register (`requirements/invariant-register.md`) | The five always-true safety properties (INV-001..INV-005) constrain every change and get first-class, referenceable IDs. |
| External dependencies (model, email, KB, queue) | Dependency register (`requirements/dependency-register.md`) | Each external system is a risk and integration surface that must be tracked (DEP-001..DEP-004). |
| Long-ish multi-phase horizon | Progress log (`progress/progress-log.md`), status cadence (`progress/status-report.md`), checkpoints (`execution/checkpoints.md`) | Multi-phase work with a hard gate between PH-1 and PH-2 needs ongoing tracking and explicit gates. |
| Coding-agent handoff | Repo bootstrap (`scripts/init_repo.*`), follow-up + review prompts (`handoff/follow-up-prompts.md`, `handoff/review-prompts.md`), Definition of Ready / Done (`execution/definition-of-ready.md`, `execution/definition-of-done.md`) | An execution agent needs an orientation flow, bounded tasks, review prompts, and explicit DoR/DoD gates. |

Omissions and any not-generated optional artifacts are recorded in `manifest.json`.
