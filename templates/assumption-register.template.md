---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Assumption Register — <project-name>

<!-- When information is missing and asking would not change the plan enough to justify the
     interruption, Keystone records an ASSUMPTION and continues. Every assumption that a later stage
     relied on MUST be visible here with its risk_if_wrong (gate G-ASM-VISIBLE).
     Identified ASM-NNN (governance.md). Generation class: Always.
     Lives at: decisions/assumption-register.md. -->

## Conventions

- **Statement** — what we are taking as true without confirmation.
- **Rationale** — why this is a reasonable default.
- **risk_if_wrong** — what breaks / must be redone if the assumption is false.
- **revisit_if** — the trigger or condition that should prompt re-checking it.
- **Status** — Draft | Proposed | Approved (accepted as a working assumption) | Rejected | Superseded.

## Assumptions

| ID | Statement | Rationale | risk_if_wrong | revisit_if | Status |
|---|---|---|---|---|---|
| ASM-001 | <e.g. Target users run on <platform> with <runtime> available.> | <common in target environment> | <re-do platform decisions; affects DEP-001> | <a user reports a different platform> | Proposed |
| ASM-002 | <e.g. Input volumes stay below <N> per run.> | <observed in similar projects> | <NFR-001 thresholds invalid; re-plan perf> | <volume exceeds <N>> | Proposed |
| ASM-003 | <assumption statement> | <rationale> | <risk> | <trigger> | Draft |

<!-- If an assumption turns out to gate a real decision, raise an OQ- and/or convert to a DEC-.
     A confirmed assumption can be retired (Superseded) once the fact is recorded elsewhere. -->
