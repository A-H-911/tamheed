---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Naming Conventions — <project-name>

<!-- The naming rules for THIS package's artifacts and identifiers, derived from Tamheed governance
     (../references/governance.md — the authoritative table). Ships inside a generated package so
     its conventions are self-documenting. Generation class: Conditional (handoff / repo requested).
     Stored as a narrative-document (doc_kind: naming). -->

## Identifiers

<!-- Stable prefix + zero-padded number; unique within the package; never reused (retire, don't recycle). -->

| Entity | ID format | Example |
|---|---|---|
| Functional requirement | `FR-NNN` | FR-001 |
| Non-functional requirement | `NFR-NNN` | NFR-001 |
| Constraint | `CON-NNN` | CON-001 |
| Invariant | `INV-NNN` | INV-001 |
| Assumption | `ASM-NNN` | ASM-001 |
| Dependency | `DEP-NNN` | DEP-001 |
| Open question | `OQ-NNN` | OQ-001 |
| Decision (any project decision) | `DEC-NNN` | DEC-001 |
| Architecture Decision Record | `ADR-NNNN` | ADR-0001 |
| Risk | `RISK-NNN` | RISK-001 |
| Hypothesis | `HYP-NNN` | HYP-001 |
| Experiment / POC | `EXP-NNN` / `POC-NNN` | EXP-001 / POC-001 |
| Success metric / KPI | `KPI-NNN` | KPI-001 |
| Stakeholder | `STK-NNN` | STK-001 |
| Phase | `PH-N` | PH-1 |
| Milestone (roadmap label) | `MS-NNN` | MS-001 |
| Slice (vertical increment) | `SL-NNN` | SL-001 |
| Work item (WBS) | `WBS-N.N[.N]` | WBS-1.2.1 |
| Acceptance criterion | `AC-NNN` | AC-001 |
| Test / validation item | `TEST-NNN` | TEST-001 |
| Audit verdict | `AV-NNN` | AV-001 |
| Progress entry | `PE-NNN` | PE-001 |
| Defect | `DEF-NNN` | DEF-001 |
| Deferred work | `DW-NNN` | DW-001 |
| Execution gate | `GATE-NNN` | GATE-001 |
| Execution plan | `EP-NNN` | EP-001 |
| Convention | `CONV-NNN` | CONV-001 |
| Scope change | `SC-NNN` | SC-001 |
| Waiver | `WVR-NNN` | WVR-001 |
| Narrative document / section | `DOC-NNN` / `SEC-NNN` | DOC-001 / SEC-001 |
| Diagram | `DIA-NNN` | DIA-001 |
| Glossary term | `GT-NNN` | GT-001 |

`DEC` vs `ADR`: use `DEC-` for ANY decision; **promote** to `ADR-NNNN` when the one-way-door
test says so (hard to reverse, broad blast radius), and record the promotion
(`decisions.promoted_to = ADR-0003`).

## Files and directories

- All files and directories: **kebab-case**, ASCII, no spaces.
- Ordered narrative docs: `NN-topic.md` (e.g. `00-charter.md`, `10-architecture.md`).
- Registers: `<thing>-register.md` (e.g. `risk-register.md`).
- ADRs: `adr-NNNN-short-title.md`; one ADR per file; one entity family per register file.
- Links between files use **relative** Markdown paths (keeps the package portable).

## Project-specific additions

<!-- Any extra identifier families or naming rules this project introduces (register them here so they
     are governed too). -->
- <e.g. `COMP-NNN` for component IDs in the architecture> — <definition>.
