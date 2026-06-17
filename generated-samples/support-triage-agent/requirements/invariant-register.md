---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Invariant Register — support-triage-agent

Non-negotiable properties that must hold for **every** change, in every phase. These are the crown jewels
of the package: the execution agent must respect them from the first commit, and the review prompts audit
against them. An invariant is stronger than a requirement — it is never traded away for a feature.

| ID | Invariant | Rationale | Enforced by |
|---|---|---|---|
| INV-001 | The agent never sends an external reply without human approval — until `FR-008` is explicitly enabled for a specific category via an approved decision (`ADR-0004`). | A wrong reply to a customer does real harm; the approval gate is the primary safety control. | `FR-006`, `ADR-0001`, `AC-003` |
| INV-002 | The agent never fabricates facts in a reply — every claim is grounded in retrieved context, or the agent defers to a human. | Hallucinated answers mislead customers and destroy trust; grounding-or-defer makes fabrication structurally hard. | `FR-004`, `ADR-0002`, `AC-002` |
| INV-003 | No PII leaves the trust boundary — PII is never sent to unapproved tools, models, or logs. | Personal-data exposure is a security and regulatory failure. | `NFR-003`, `ASM-003`, `AC-004` |
| INV-004 | Every action and tool call is logged with inputs, outputs, and rationale, to an append-only audit trail. | Auditability is required to defend decisions and meet review obligations. | `FR-007`, `NFR-005`, `AC-005` |
| INV-005 | The agent operates within an explicit tool allow-list and a per-run cost/iteration budget — no unbounded loops, no off-list tools. | Bounds runaway cost and the blast radius of any failure or injection. | `ADR-0003`, `RISK-004`, `NFR-004` |

## Notes

- `INV-001` is the only invariant that is ever *narrowed*, and only by an approved `ADR-0004` decision
  that names the specific low-risk categories eligible for auto-send. Every other category, and every
  other invariant, continues to hold unconditionally. The narrowing is itself audited (`INV-004`).
- Prompt-injection defense rests on `INV-002` (grounding), `INV-005` (allow-list/budget), and the rule
  that email content is treated as data, never as instructions (`RISK-003`).
