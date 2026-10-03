---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Governance — <project-name>

<!-- The rules of record for THIS package: identifiers, statuses, versioning, and cross-references.
     Derived from Tamheed's governance reference; ships inside the package so it is self-documenting.
     Generation class: Conditional (handoff to Claude Code / repo requested).
     Stored as a narrative-document (doc_kind: governance). Pairs with the naming-conventions
     narrative document. -->

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

- **Review** *(wbs-items and slices only)*: **done-claimed**. The agent asserts the work is
  complete but verification has not confirmed it. Review counts as OPEN everywhere. Only the
  guarded transition to **Implemented** (done-verified) closes work.

- **Decision statuses** are EXACTLY: `Proposed | Approved | Rejected | Superseded | Deferred |
  Implemented`.
  Never render a Proposed decision as Approved. This is a core safeguard.
- **Document statuses:** `Draft | Proposed | Approved | Implemented | Rejected | Deferred | Superseded |
  Obsolete`.
- Only **Approved** items constrain execution. Rejected items are kept (with reason) as evidence.

## Versioning

- **Package version:** semver `MAJOR.MINOR.PATCH`. MINOR = additive. MAJOR = breaking (schemas, identifiers,
  handoff contract) with a migration note.
- **Document version:** front-matter `version` (semver or `vN`) + `updated` (ISO date). Bump on material
  change.
- **Immutable after approval:** ADRs and Approved acceptance criteria. Supersede, never rewrite (typo fixes
  excepted).
- **Derived artifacts** (traceability matrix, readiness report, roadmap rollups, status report) are
  regenerated from sources, never hand-edited.

## Cross-references

- Reference entities by ID in prose ("mitigated by `RISK-012`").
- A row that exists because of another entity records a typed link, not only prose. The typed
  relations are `derives_from`, `mitigates`, `verifies`, `supersedes` and `blocked_by`. The
  scope-delta kinds are `scope_adds`/`scope_modifies`/`scope_removes`. `amends` links a scope change
  to the `DEC-`/`ADR-` ruling it carves an exception out of. A `DEC-` merges by full-row upsert,
  an `ADR-` by supersession. `carries` links a wbs-item to the activated `DW-` row it carries.
  `learned_from` says what taught a lesson. `relates_to` is the documented untyped escape hatch.
  Edges are keyed (from, to, relation). A wrong edge is retired (`retire: true` on the trace-edge
  item, journaled by the server) and the correct one written in the same batch. A new relation
  never replaces an old one by itself. A full-row update that only flips a status names the
  columns it did not mean to change (`expect_unchanged`), and the store refuses drift.
- Every `FR-/NFR-` must be reachable in the traceability matrix to >=1 decision, task, and test.
  A behavior-bearing one must also reach an acceptance criterion. Unlinked requirements are a gate failure.
- References are entity IDs, not file paths. The store resolves them, and there are no relative links to
  keep working.

## Supersession & deprecation

- **Supersede:** new ID, set `superseded_by`/`supersedes` on both ends. The old item stays at status Superseded.
- **Deprecate:** mark Obsolete with a one-line reason + date. Update or annotate downstream references.

## Roles and approval

<!-- Who can approve decisions, accept gate exceptions, and lock scope for this project. -->
- Decision approver(s): <role>.
- Gate-exception approver(s): <role>.
- Scope owner: <role>.
