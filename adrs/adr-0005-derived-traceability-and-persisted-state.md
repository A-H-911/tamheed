---
id: ADR-0005
title: Traceability is derived; state is persisted for resume and update
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0005: Traceability is derived; state is persisted for resume and update

Status: Accepted
Date: 2026-06-17

## Context

Two related needs shaped this decision. First, the traceability matrix
(requirement → decision → work item → test → risk → acceptance criterion) must
always be correct, and a hand-maintained matrix in a long, evolving package
drifts out of date the instant a register changes — stale traceability is worse
than none because it looks authoritative. Second, Keystone runs are long, can
be interrupted, and get revisited as decisions and progress arrive; re-asking
settled questions or losing context across runs is unacceptable.

## Decision

- **Traceability is a derived artifact.** The matrix is generated from the
  registers (decisions cite requirements, WBS items cite requirements, tests
  cite requirements/ACs, risks cite what they threaten), never hand-authored.
  It is re-derived on every update cycle, and a `coverage` flag
  (full/partial/gap) is computed so gaps are visible. Gate **G-TRACE** checks
  the result.
- **State is persisted.** A machine-owned `keystone-state.json` holds the
  normalized registers, scope, the selected artifact set, per-stage status, the
  last completed stage, the traceability rows, and a change log. On `resume`,
  Keystone loads state, detects human edits to artifacts since the last run,
  reconciles (human edits win, recorded), and continues from the last
  incomplete stage. On `update`, it applies the change to the owning register,
  re-derives dependent artifacts, bumps versions, and re-runs affected gates.

## Consequences

- The matrix is always reproducible from its sources; if it cannot be
  regenerated, that is a signal its inputs are wrong, which is itself useful.
- Interrupted and evolving work resumes without losing context or re-asking
  settled questions; every mutation is appended to an auditable change log
  (who/what/when).
- Backward links (a test or work item that traces to no requirement) expose
  orphans — gold-plating or a missing requirement — instead of hiding them.
- **Cost:** there must be a real derivation step and a real reconcile step, and
  a consistency invariant (state and rendered artifacts must agree after any
  operation) that has to be honoured. Hand-editing a derived artifact is now a
  bug, not a shortcut. Accepted: this is exactly the discipline that keeps the
  package trustworthy over time.

## Alternatives considered and rejected

- **Hand-maintained traceability matrix.** Rejected: drifts immediately in an
  evolving package, gives false confidence, and pushes the maintenance burden
  onto whoever edits a register. Deriving it removes a whole class of staleness
  bugs.
- **No persisted state — reconstruct context from the artifacts each run.**
  Rejected: lossy and slow; cannot reliably tell which stage was last completed
  or which questions were already settled, so it re-asks and risks overwriting
  human edits. A normalized state file is the only robust basis for
  resume/update.
- **Human-owned state file.** Rejected: humans edit the rendered artifacts;
  making them also hand-edit normalized JSON invites inconsistency between the
  two surfaces. State is machine-owned and Keystone reconciles (consistent with
  ADR-0003).
