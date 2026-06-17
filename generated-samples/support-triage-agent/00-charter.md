---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Project Charter — support-triage-agent

## Problem statement

The customer-support team's inbound email volume has roughly tripled, and agents spend most of their day
reading, categorizing, and drafting routine replies. Response times are slipping and routine work crowds
out the hard cases. The team wants help triaging and drafting — but a wrong, fabricated, or unsafe reply
to a customer is worse than a slow one, so any automation must be safe and supervised before it is fast.

## Objectives

- Cut the human time spent on triage and routine drafting without lowering reply quality.
- Make every automated step auditable and safe by construction, so support and security can trust it.
- Establish a measured path toward limited auto-send for low-risk categories — earned with evidence, not
  assumed.

## Goals and non-goals

### Goals
- Stand up a supervised triage pipeline: ingest → classify → retrieve → draft → route/approve.
- Keep a human in the loop before any reply is sent at launch.
- Produce a full, reconstructable decision trace for every email handled.
- Measure classification accuracy and confidence calibration on a labeled corpus before relaxing any gate.

### Non-goals
- Replacing human support agents. The agent assists triage and drafting; humans own customer relationships.
- Auto-sending replies at launch. Auto-send is a later, gated capability (`FR-008`), not part of the MVP.
- Building a general-purpose chatbot or a customer-facing live-chat product.
- Modifying the upstream email system, knowledge base, or ticketing system beyond integration.

## Scope

### In scope
- Email ingestion from the existing mailbox/queue (`DEP-002`).
- Classification into the Support-Ops category + urgency taxonomy (`ASM-002`).
- Retrieval-grounded reply drafting with citation-or-defer (`ADR-0002`).
- Confidence-based routing/escalation to the correct human queue (`DEP-004`).
- A human-in-the-loop approval gate before send (`ADR-0001`).
- Append-only audit logging of every action, tool call, and decision (`FR-007`).
- A calibration experiment (`EXP-001`) that measures accuracy and gates auto-send.

### Out of scope
- Auto-sending outside the explicitly whitelisted, approved low-risk categories (and only after `EXP-001`).
- Outbound campaigns, marketing email, or proactive outreach.
- Changes to the company PII/retention policy itself (the agent *complies* with it; `ASM-003`).
- Voice, chat, or social channels.

## Success metrics (KPI-)

| ID | Metric | Baseline | Target | Measurement method | Status |
|---|---|---|---|---|---|
| KPI-001 | Auto-handle / deflection rate (share of emails resolved without human drafting) | 0% (all manual today) | ≥ 30% of eligible low-risk categories by end of PH-2 | Share of handled emails auto-sent under the approved whitelist, from the audit log | Approved |
| KPI-002 | Human handling time saved per triaged email | 0% (baseline manual time captured in PH-1) | ≥ 40% median reduction vs PH-1 baseline | Timer from assignment to send, compared to the PH-1 assisted baseline | Approved |
| KPI-003 | Reply quality / accuracy | n/a | Top-1 category accuracy ≥ 85% (`NFR-001`); approved-reply edit rate ≤ 20% | Labeled-corpus eval (`EXP-001`) + sampled human review of approved replies | Approved |

## Stakeholders (STK-)

| ID | Stakeholder / role | Interest in the project | Influence (H/M/L) |
|---|---|---|---|
| STK-001 | Product lead | Owns scope, KPIs, and the go/no-go on auto-send | H |
| STK-002 | Security lead | Owns the PII/retention policy and the egress boundary (`INV-003`) | H |
| STK-003 | Engineering lead | Owns delivery, the invariants, and the bounded-loop design | H |
| STK-004 | Support Ops manager | Owns the category/urgency taxonomy, escalation rules, and the auto-send whitelist | H |
| STK-005 | Support agents | End users of the assistive drafts and approval queue | M |

## Constraints and assumptions (summary)

- Key constraints: see [constraint register](requirements/constraint-register.md) (`CON-`) — supervised
  launch, PII policy compliance, bounded cost.
- Non-negotiables: see [invariant register](requirements/invariant-register.md) (`INV-001`..`INV-005`).
- Key assumptions: see [assumption register](decisions/assumption-register.md) (`ASM-001`..`ASM-005`).
- External dependencies: see [dependency register](requirements/dependency-register.md) (`DEP-001`..`DEP-004`).

## Approval

- Approved by: product-lead (STK-001), with security (STK-002) and engineering (STK-003) sign-off on the
  invariants.
- Date: 2026-06-17
