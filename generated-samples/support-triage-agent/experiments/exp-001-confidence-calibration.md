---
id: EXP-001
status: Planned
version: 1.0.0
updated: 2026-06-17
owner: engineering-lead (STK-003)
---

# EXP-001 — Confidence calibration + accuracy measurement on a labeled corpus

## Hypotheses
`HYP-001` (accuracy + a safe auto-send confidence band) and `HYP-002` (retrieval grounding coverage).

## Why this experiment
`FR-008` (auto-send) and `ADR-0004` (confidence routing) must not be enabled on guesses. This experiment
produces the evidence that either unlocks a *narrow, calibrated* auto-send whitelist or keeps the system
fully supervised. It directly resolves `DEC-004`.

## Method
1. Assemble/confirm the labeled corpus (`ASM-001`): emails with category, urgency, and a reference reply.
2. Run classification (`FR-002`) over the corpus; record top-1 category accuracy and urgency accuracy.
3. Calibrate confidence; compute error rate per category and per confidence band.
4. Measure retrieval grounding coverage (`FR-003`) and the resulting deferral rate.
5. Identify whether any confidence threshold isolates a low-risk subset at ≤ X% error (X agreed with
   Support Ops + Security **before** the run).

## PASS criteria
- Top-1 category accuracy ≥ 85% (`NFR-001`), **and**
- a confidence threshold exists that yields a whitelistable low-risk subset at ≤ X% measured error.

## FAIL criteria
- Accuracy below the bar, **or**
- no confidence threshold produces a sufficiently low-error low-risk subset.
  On FAIL, `FR-008` stays deferred, `ADR-0004` is rejected (fallback to fully supervised), and `INV-001`
  holds for every category.

## Timebox
Bounded spike (target ≤ 2 weeks). Results recorded in this file and summarized for the go/no-go.

## Decision it unblocks
`DEC-004` / `ADR-0004` (Proposed → Approved or Rejected), and therefore `FR-008` enablement scope.

## Acceptance linkage
`AC-001` (accuracy on a labeled sample) is the in-harness check of the accuracy half of this experiment.
