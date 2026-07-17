---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Governance — <project-name>

<!-- The rules of record for THIS package: identifiers, statuses, versioning, and cross-references.
     Derived from Keystone's governance reference; ships inside the package so it is self-documenting.
     Generation class: Conditional (handoff to Claude Code / repo requested).
     Lives at: governance/governance.md. Pairs with naming-conventions.md. -->

## Identifiers

Stable prefix + zero-padded number, unique within the package, never reused. Full table in
[naming-conventions.md](naming-conventions.md). Use IDs in registers, front-matter, and as link targets.
Promote a `DEC-` to an `ADR-NNNN` when architecturally significant and record the promotion.

## Lifecycle statuses

Every register row and standalone document carries a status.

```
Draft → Proposed → Approved → Implemented
                 ↘ Rejected
                 ↘ Deferred  (→ back to Proposed later)
        Approved/Implemented → Superseded → Obsolete
```

- **Decision statuses** are EXACTLY: `Proposed | Approved | Rejected | Superseded | Deferred`.
  Never render a Proposed decision as Approved — this is a core safeguard.
- **Document statuses:** `Draft | Proposed | Approved | Implemented | Rejected | Deferred | Superseded |
  Obsolete`.
- Only **Approved** items constrain execution. Rejected items are kept (with reason) as evidence.

## Versioning

- **Package version:** semver `MAJOR.MINOR.PATCH`. MINOR = additive; MAJOR = breaking (schemas, identifiers,
  handoff contract) with a migration note.
- **Document version:** front-matter `version` (semver or `vN`) + `updated` (ISO date); bump on material
  change.
- **Immutable after approval:** ADRs and Approved acceptance criteria — supersede, never rewrite (typo fixes
  excepted).
- **Derived artifacts** (traceability matrix, readiness report, roadmap rollups, status report) are
  regenerated from sources, never hand-edited.

## Cross-references

- Reference entities by ID in prose ("mitigated by `RISK-012`").
- A row that exists because of another entity records a typed link (`derives_from`, `mitigates`, `verifies`,
  `supersedes`, `blocked_by`), not only prose.
- Every `FR-/NFR-` must be reachable in the traceability matrix to >=1 decision, task, and test, and (if
  behavior-bearing) an acceptance criterion. Unlinked requirements are a gate failure.
- Links between files are relative Markdown paths.

## Supersession & deprecation

- **Supersede:** new ID, set `superseded_by`/`supersedes` on both ends; old item stays at status Superseded.
- **Deprecate:** mark Obsolete with a one-line reason + date; update or annotate downstream references.

## Roles and approval

<!-- Who can approve decisions, accept gate exceptions, and lock scope for this project. -->
- Decision approver(s): <role>.
- Gate-exception approver(s): <role>.
- Scope owner: <role>.
