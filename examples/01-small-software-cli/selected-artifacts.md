# Selected artifact set — repostat

repostat is a **small software project**: one developer, no genuine technical uncertainty, a single
architecturally-relevant seam (how reports are rendered to multiple formats), and a couple of real
correctness invariants. Per Keystone's artifact-selection rules, the package keeps the full **Always**
set and otherwise **collapses toward minimal** — conditional artifacts are included only where a trigger
genuinely holds, and included in their smallest useful form.

## Always (generated)

- Charter (`00-charter.md`)
- Executive summary (`01-executive-summary.md`)
- Functional requirements (`requirements/functional.md`, FR-)
- Non-functional requirements (`requirements/non-functional.md`, NFR-)
- Constraint register (`requirements/constraint-register.md`, CON-)
- Assumption register (`decisions/assumption-register.md`, ASM-)
- Open-question register (`decisions/open-question-register.md`, OQ-)
- Open-decision register (`decisions/open-decision-register.md`, DEC-)
- Risk register (`risks/risk-register.md`, RISK-)
- Phased roadmap (`planning/roadmap.md`, PH-)
- Acceptance criteria (`validation/acceptance-criteria.md`, AC-)
- Traceability matrix — *derived* (`validation/traceability-matrix.md`)
- Handoff initial prompt (`handoff/initial-prompt.md`)
- Execution-readiness report (`handoff/execution-readiness-report.md`)
- Package manifest (`manifest.json`)
- README for the package (`README.md`)

## Conditional (triggered / not triggered)

| Trigger | Decision | Why |
|---|---|---|
| Architecturally significant decisions | **Included, minimal** — `architecture/architecture.md` (one short doc) + one ADR (`adrs/adr-0001-export-format-and-rendering-seam.md`). | Exactly one seam matters: a format-agnostic report model rendered by pluggable formatters (FR-005). No diagrams/ — a paragraph carries it. |
| ≥2 viable technology options | **Omitted** (`architecture/technology-comparison.md` not generated). | The only open choice is runtime/packaging, recorded as ASM-002, not a weighted multi-option trade-off. A comparison matrix would be ceremony. |
| Genuine technical uncertainty | **Omitted** — no `research/`, `experiments/`, `pocs/`. | Reading `.git` and computing counts is well-understood. There is no hypothesis to test; nothing to prototype. |
| Cross-team / multi-actor delivery | **Minimal** — `planning/work-breakdown.md` and `planning/milestones.md` kept terse; **no** stakeholder register. | Single developer is the only actor; STK- analysis would be empty. WBS/milestones still help the executing agent sequence work. |
| Non-trivial NFRs (perf / correctness / scale) | **Included** — `validation/test-strategy.md` (TEST-). | Output correctness and determinism (NFR-001) plus the ~50k-commit budget (NFR-002, ASM-003) are non-trivial and must be verified, not asserted. |
| Invariants present | **Included** — `requirements/invariant-register.md` (INV-). | Two hard invariants: never mutate the target repo (INV-001) and byte-identical output for identical input (INV-002). |
| External dependencies | **Included** — `requirements/dependency-register.md` (DEP-). | The tool depends on git being available/readable on the host (DEP-001) and on the pinned runtime (DEP-002). |
| Repo requested / handoff to coding agent | **Included** — `scripts/init_repo.*`, `handoff/follow-up-prompts.md`, `handoff/review-prompts.md`, and DoR/DoD (`execution/definition-of-ready.md`, `definition-of-done.md`). | The plan is handed to a separate coding agent, so it needs a bootstrap, phase-gate prompts, audit prompts, and explicit ready/done bars. |
| Long execution horizon | **Omitted** — no `progress/` log or status-report cadence. | Two short phases; a running progress log would add overhead without operational value. `execution/checkpoints.md` covers the gates. |
| Regulatory / compliance input | **Omitted** — no compliance constraints or validation-evidence plan. | An offline read-only stats tool has no regulatory surface. |

Dropped artifacts are recorded in `manifest.json` with an explicit omission reason, per the artifact-selection rules.
