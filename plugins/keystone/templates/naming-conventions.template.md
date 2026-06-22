---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Naming Conventions — <project-name>

<!-- The naming rules for THIS package's artifacts and identifiers, derived from Keystone governance.
     Ships inside a generated package so its conventions are self-documenting.
     Generation class: Conditional (handoff to Claude Code / repo requested).
     Lives at: governance/naming-conventions.md. Keep aligned with governance.template.md. -->

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
| Decision (lightweight) | `DEC-NNN` | DEC-001 |
| Architecture Decision Record | `ADR-NNNN` | ADR-0001 |
| Risk | `RISK-NNN` | RISK-001 |
| Hypothesis | `HYP-NNN` | HYP-001 |
| Experiment / POC | `EXP-NNN` / `POC-NNN` | EXP-001 / POC-001 |
| Success metric / KPI | `KPI-NNN` | KPI-001 |
| Stakeholder | `STK-NNN` | STK-001 |
| Phase | `PH-N` | PH-1 |
| Milestone | `MS-NNN` | MS-001 |
| Work item (WBS) | `WBS-N.N[.N]` | WBS-1.2.1 |
| Acceptance criterion | `AC-NNN` | AC-001 |
| Test / validation item | `TEST-NNN` | TEST-001 |

`DEC` vs `ADR`: use `DEC-` for register decisions; **promote** to `ADR-NNNN` when architecturally
significant, and record the promotion (`DEC-007 → ADR-0003`).

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
