---
status: Approved
version: 1.0.0
updated: 2026-06-17
owner: product-lead (STK-001)
---

# Executive Summary — support-triage-agent

## In one paragraph

Support email volume has tripled and agents spend their days on routine triage and drafting. We will build
a **supervised AI triage agent** that classifies each email, retrieves knowledge-base context, drafts a
grounded reply, and routes it to a human for approval before anything is sent. Safety is the design
center: a human approves every send at launch, the agent never fabricates facts, PII never leaves the
trust boundary, every action is audited, and the agent runs in a bounded loop with a cost cap. Once a
calibration experiment proves accuracy, we may enable **auto-send for a narrow whitelist of low-risk
categories** — but only with that evidence.

## Problem and objective

Routine triage crowds out hard cases and slows responses. The objective is to cut human time on triage and
routine drafting **without** lowering reply quality or risking an unsafe reply to a customer.

## Recommendation

Ship a fully supervised assistive pipeline first (PH-1), then earn limited automation with measurement.
See [architecture](architecture/architecture.md); key decisions `ADR-0001` (human-in-the-loop gate),
`ADR-0002` (grounded drafting), `ADR-0003` (bounded loop). The auto-send decision `ADR-0004` is held
**Proposed** until the calibration experiment passes.

## Why this over the alternatives

- Considered: auto-send from day one; assistive-only forever; supervised-then-gated-automation.
  Chose **supervised-then-gated** because it captures most of the efficiency upside while keeping the only
  safety control (human approval) until accuracy is measured.
- Auto-send-from-day-one was rejected outright (`ADR-0001`): no evidence, unacceptable customer risk.

## Scope at a glance

| | Summary |
|---|---|
| MVP delivers | Supervised triage: classify, retrieve, grounded draft, route, human-approved send, full audit. |
| Full target adds | Calibrated confidence routing + auto-send for an approved low-risk whitelist (gated). |
| Explicitly out of scope | Auto-send before the calibration gate; replacing human agents; other channels. |

## Plan and effort

- Phases: `PH-1` supervised pipeline → `PH-2` calibrated auto-send (conditional) → `PH-3` broaden +
  monitor. See [roadmap](planning/roadmap.md). A bounded-loop POC and a calibration experiment precede
  any automation.

## Top risks

- `RISK-001` wrong/hallucinated reply harms a customer — handled by `INV-001` (approval) + `INV-002`
  (grounding).
- `RISK-002` PII leakage — handled by `INV-003` boundary + security policy (`ASM-003`).
- `RISK-003` prompt-injection via email — email treated as data; bounded allow-list (`INV-005`).
- `RISK-005` mis-calibration enabling unsafe auto-send — auto-send gated on `EXP-001` + `ADR-0004`.

## What we are asking for

Approval to execute **PH-1** as specified, and agreement that **PH-2 auto-send** is gated on `EXP-001`
passing and `ADR-0004` being approved with a Support-Ops/Security-signed whitelist.
