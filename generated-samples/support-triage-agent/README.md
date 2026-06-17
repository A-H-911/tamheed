# support-triage-agent — execution-ready package

This is a **generated Keystone package**: the planning, governance, architecture, and handoff artifacts an
execution agent needs to implement *support-triage-agent* (a supervised AI agent that triages inbound
customer-support email) with discipline. It is a worked sample produced to demonstrate Keystone's output;
it invents a plausible project purely to illustrate Keystone's output.

The lighter, single-pass version of this same scenario is in
[`../../examples/05-ai-agentic-system/`](../../examples/05-ai-agentic-system/). This directory is the
fuller, file-by-file expansion.

## How an agent should consume this package

1. Read [`00-charter.md`](00-charter.md) — why the project exists and what "done" means.
2. Read [`requirements/invariant-register.md`](requirements/invariant-register.md) — the five
   non-negotiable safety properties (`INV-001`–`INV-005`). Respect these from the first commit.
3. Read [`requirements/functional.md`](requirements/functional.md) and
   [`requirements/non-functional.md`](requirements/non-functional.md) — what to build and how well.
4. Read [`architecture/architecture.md`](architecture/architecture.md) and the
   [ADRs](adrs/) — the decided seams; note `ADR-0004` is **Proposed** (gated).
5. Read [`planning/roadmap.md`](planning/roadmap.md) — the phases and the PH-2 gate.
6. Start from [`handoff/initial-prompt.md`](handoff/initial-prompt.md) — orient, do **one** bounded task,
   stop for approval.

## Reading order by question

| If you want… | Open |
|---|---|
| The one-page story | [`01-executive-summary.md`](01-executive-summary.md) |
| What must always be true | [`requirements/invariant-register.md`](requirements/invariant-register.md) |
| Why it's built this way | [`adrs/`](adrs/) + [`decisions/open-decision-register.md`](decisions/open-decision-register.md) |
| What could go wrong | [`risks/risk-register.md`](risks/risk-register.md) |
| How we know it works | [`validation/acceptance-criteria.md`](validation/acceptance-criteria.md) + [`validation/test-strategy.md`](validation/test-strategy.md) |
| Need → evidence map | [`validation/traceability-matrix.md`](validation/traceability-matrix.md) |
| Is it ready? | [`handoff/execution-readiness-report.md`](handoff/execution-readiness-report.md) |

## The non-negotiables (read these first)

- `INV-001` — no external reply is sent without human approval (until `FR-008` is enabled per category via
  an approved decision).
- `INV-002` — every claim in a draft is grounded in retrieved context, or the agent defers.
- `INV-003` — no PII leaves the trust boundary.
- `INV-004` — every action and tool call is logged, append-only.
- `INV-005` — the agent runs in a bounded loop: tool allow-list + cost/iteration cap.

## Status

- **Charter, requirements, invariants, ADR-0001/0002/0003, roadmap, acceptance, traceability:** Approved.
- **`ADR-0004` (confidence routing / auto-send) and `FR-008`:** **Proposed / gated** on `EXP-001` PASS.
- **Readiness:** GO for PH-1; PH-2 conditional. See the readiness report.

## Package layout

```text
support-triage-agent/
├── README.md
├── 00-charter.md
├── 01-executive-summary.md
├── requirements/        functional, non-functional, constraint, invariant, dependency
├── decisions/           open-question, open-decision, assumption registers
├── research/            hypothesis-register
├── experiments/         exp-001-confidence-calibration
├── pocs/                poc-001-bounded-agent-loop
├── architecture/        architecture (+ diagrams/)
├── adrs/                adr-0001..adr-0004
├── risks/               risk-register
├── planning/            roadmap, work-breakdown
├── validation/          acceptance-criteria, test-strategy, traceability-matrix
├── handoff/             initial-prompt, follow-up-prompts, review-prompts, execution-readiness-report
└── manifest.json
```
