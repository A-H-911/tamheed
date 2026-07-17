# Governance: identifiers, statuses, versioning, cross-references

This is the single source of truth for how every Keystone-generated artifact is named, identified,
versioned, and linked. Apply it uniformly — consistent identifiers are what make the traceability matrix
and the handoff trustworthy.

## Identifier scheme

Each identifier is a stable prefix + zero-padded number, unique within a package and never reused (retire,
don't recycle). Use them in registers, in artifact front-matter, and as link targets.

| Entity | ID format | Lives in |
|---|---|---|
| Functional requirement | `FR-NNN` | requirements/ |
| Non-functional requirement | `NFR-NNN` | requirements/ |
| Constraint | `CON-NNN` | requirements/constraint-register |
| Invariant (non-negotiable) | `INV-NNN` | requirements/invariant-register |
| Assumption | `ASM-NNN` | decisions/assumption-register |
| Dependency | `DEP-NNN` | requirements/dependency-register |
| Open question | `OQ-NNN` | decisions/open-question-register |
| Decision (lightweight) | `DEC-NNN` | decisions/open-decision-register |
| Architecture Decision Record | `ADR-NNNN` | adrs/ |
| Risk | `RISK-NNN` | risks/risk-register |
| Hypothesis | `HYP-NNN` | research/hypothesis-register |
| Experiment / POC | `EXP-NNN` / `POC-NNN` | experiments/ , pocs/ |
| Success metric / KPI | `KPI-NNN` | charter / success-metrics |
| Stakeholder | `STK-NNN` | stakeholder-register |
| Phase | `PH-N` | planning/roadmap |
| Milestone | `MS-NNN` | planning/milestones |
| Work item (WBS) | `WBS-N[.N[.N]]` (group `WBS-N`, leaf `WBS-N.N`, sub-leaf `WBS-N.N.N`) | planning/work-breakdown |
| Acceptance criterion | `AC-NNN` | validation/acceptance-criteria |
| Test / validation item | `TEST-NNN` | validation/test-strategy |

`DEC` vs `ADR`: use `DEC-` for any decision in the open-decision register; **promote** a decision to an
`ADR-NNNN` when it is architecturally significant (hard to reverse, broad blast radius). Record the
promotion (`DEC-007 → ADR-0003`) so the link is never lost.

## Lifecycle statuses

Every register row and every standalone document carries a status.

```
Draft → Proposed → Approved → Implemented
                 ↘ Rejected
                 ↘ Deferred  (→ back to Proposed later)
        Approved/Implemented → Superseded (by a newer item)  → Obsolete
```

- **Draft** — being written; not yet offered for approval.
- **Proposed** — offered to the human; awaiting an approval decision. The default for anything Keystone
  authored on its own initiative.
- **Approved** — the human (or an authorized gate) accepted it. Only Approved items constrain execution.
- **Rejected** — considered and declined; kept with the reason (rejected alternatives are evidence).
- **Deferred** — postponed with a trigger/condition for revisiting.
- **Superseded** — replaced by a newer item; row points to its successor (`superseded_by`).
- **Implemented** — realized in the execution repo (set during update cycles).
- **Obsolete** — no longer relevant; retained for history, excluded from active views.

**Decision statuses** are exactly: Proposed, Approved, Rejected, Superseded, Deferred — plus
Implemented once a decision is realized during execution/update cycles. Never render a
Proposed decision as if Approved — this is a core safeguard.

## Versioning

- **Package / skill version:** semver `MAJOR.MINOR.PATCH`. MINOR = additive (new artifacts/fields, no
  break). MAJOR = breaking change to schemas, identifiers, or the handoff contract; ship a migration note.
- **Document version:** each generated document carries front-matter `status`, `version` (semver or `vN`),
  and `updated` (ISO date). Bump on material change.
- **Immutable-after-approval artifacts** (ADRs, approved acceptance criteria): never edit in place. To
  change, add a new item that supersedes the old one. Correcting typos is allowed; changing meaning is not.
- **Derived artifacts** (traceability matrix, readiness report, roadmap rollups) are regenerated, never
  hand-edited; they are reproducible from their sources.

## File & directory naming

- All files and directories: **kebab-case**. ASCII, no spaces.
- Ordered narrative docs: `NN-topic.md` (`00-charter.md`, `10-architecture.md`).
- Registers: `<thing>-register.md` (`risk-register.md`).
- ADRs: `adr-NNNN-short-title.md`.
- One entity family per register file; one ADR per file.

## Cross-reference rules

- Reference any entity by its ID in running text: "mitigated by `RISK-012`'s plan", "depends on `DEC-004`".
- A row that exists because of another entity records the link in a typed field (`derives_from`,
  `mitigates`, `verifies`, `supersedes`, `blocked_by`), not only in prose.
- Every `FR-/NFR-` should be reachable in the traceability matrix to at least one decision, task, test, and
  (where it asserts user-visible behavior) an acceptance criterion. Unlinked requirements are a gate
  failure, not a silent omission.
- Links between files use relative Markdown paths so the package stays portable.

## Supersession & deprecation

- Superseding creates a new ID and sets `superseded_by`/`supersedes` on both ends; the old item stays
  (status Superseded) so history and rationale survive.
- Deprecating marks an item Obsolete with a one-line reason and date; downstream references are updated or
  explicitly noted as historical.
