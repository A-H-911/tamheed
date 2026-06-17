---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# Architecture — support-triage-agent

Recommended architecture and component model for the supervised triage agent. This document fixes the
**seams and safety controls**; it deliberately leaves the internal orchestration pattern open (`DEC-005`,
pending `POC-001`). Significant decisions are recorded as ADRs and referenced here, not restated.

## Overview

A single bounded agent (`ADR-0003`) moves each email through a fixed pipeline. Every external system is
reached through a **vendor-neutral port** so no provider is hard-wired (`CON-003`, `ASM-004`). Two
controls wrap the whole pipeline: an **append-only audit log** (`INV-004`) records every action, and a
**PII boundary** (`INV-003`) prevents personal data from reaching unapproved destinations.

```
            ┌──────────────────────── audit log (append-only, INV-004) ────────────────────────┐
            │                                                                                    │
 inbound    │   ingest      classify       retrieve        draft            route / approve      │  send
 email ─────┼─▶ (FR-001) ─▶ (FR-002) ─▶ (FR-003) ─▶ (FR-004, grounded) ─▶ (FR-005 / FR-006) ─────┼─▶ to customer
[DEP-002]   │     │            │            │             │                     │                 │   (only after
            │     │            │            │             │              human approval           │    approval —
            │     ▼            ▼            ▼             ▼               [DEP-004]                │    INV-001)
            │   model/tool ports (vendor-neutral) ── DEP-001 / DEP-003                             │
            └──────────────── PII boundary (INV-003) · bounded loop: allow-list + cost cap (INV-005) ┘
```

## Components

| Component | Responsibility | Key controls |
|---|---|---|
| Ingestor | Pull email from the mailbox/queue; create a triage record. | `FR-001`; writes audit (`INV-004`). |
| Classifier | Assign category + urgency from the taxonomy. | `FR-002`, `ASM-002`. |
| Retriever | Fetch grounding context from the knowledge base. | `FR-003`, `DEP-003`. |
| Drafter | Produce a grounded reply with citations, or defer. | `FR-004`, `ADR-0002`, `INV-002`. |
| Router | Escalate sensitive/low-confidence to a human queue. | `FR-005`, `ADR-0004` (Proposed). |
| Approval gate | Hold every send for explicit human approval. | `FR-006`, `ADR-0001`, `INV-001`. |
| Audit log | Append-only record of actions, tool calls, rationale. | `FR-007`, `INV-004`. |
| Bounded loop runtime | Tool allow-list + per-run cost/iteration cap; fail closed. | `ADR-0003`, `INV-005`. |
| Ports | Vendor-neutral access to model and external tools. | `CON-003`, `ASM-004`. |

## Contracts (seams)

- **Model/tool port.** All model and tool calls go through a narrow interface; application code names no
  provider. Swapping `DEP-001` is a port change, not an application change (`ADR-0003`).
- **Draft contract.** The drafter returns either `{reply, citations[]}` or `{defer, reason}` — there is no
  "ungrounded answer" return shape, which is how `INV-002` is enforced structurally (`ADR-0002`).
- **Send contract.** Send is a separate action that requires an `approval` token referencing a human
  decision; in PH-2 the token may be issued automatically *only* for whitelisted categories (`ADR-0004`).

## Open architectural points

- `DEC-005` — single-pass vs multi-step planner *inside* the bounded loop. Deferred to `POC-001`; the
  external contracts above do not depend on the choice.
- Confidence thresholds and the auto-send whitelist (`ADR-0004`) are set from `EXP-001`, not now.

## Diagrams
See [`diagrams/`](diagrams/): context, component, data-flow, and integration views elaborate this overview.
