---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Stakeholder Register — <project-name>

<!-- Who has a stake in the project: their interest, influence, and what they need from it. Prefer
     ROLES over named individuals so the package stays portable. The charter shows a summary; this is
     the full register. Identified STK-NNN (governance.md).
     Generation class: Conditional (cross-team / multi-actor delivery). Lives at:
     governance/ or charter context (per package layout). -->

## Conventions

- **Stakeholder** — role/group (name a person only if necessary).
- **Interest** — what they care about / need from the project.
- **Influence** — H | M | L (how much sway they have over decisions).
- **Engagement** — how/when they are involved (inform | consult | approve | deliver-to).
- **Linked needs** — requirements or success metrics traced to them (`FR-/NFR-/KPI-`).
- **Status** — Draft | Proposed | Approved.

## Stakeholders

| ID | Stakeholder / role | Interest | Influence | Engagement | Linked needs | Status |
|---|---|---|---|---|---|---|
| STK-001 | <sponsor / decision owner> | <outcome they fund> | H | approve | KPI-001 | Proposed |
| STK-002 | <end user / operator> | <what they need to do> | M | consult | FR-001, FR-003 | Proposed |
| STK-003 | <downstream team / integrator> | <interface they depend on> | M | deliver-to | NFR-002 | Draft |

<!-- Use STK- ids as the `source` of requirements they originate, so traceability connects needs to the
     people who hold them. -->
