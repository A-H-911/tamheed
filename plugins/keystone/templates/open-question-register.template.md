---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Open Question Register — <project-name>

<!-- Questions whose answers are not yet known. A BLOCKING question must be answered (or explicitly
     accepted-open with rationale) before readiness — a silently-unanswered blocking question is a
     gate failure (G-OQ). Non-blocking questions may ship open.
     Identified OQ-NNN (governance.md). Generation class: Always.
     Lives at: decisions/open-question-register.md. -->

## Conventions

- **Question** — the specific thing we need to know.
- **Blocking?** — Yes (cannot finalize the plan / a phase without it) | No.
- **raised_by** — origin (intake gap, contradiction, stage analysis, stakeholder).
- **Affects** — the artifacts/IDs that depend on the answer (`FR-`, `DEC-`, `PH-`, …).
- **Resolution** — the answer once known, and where it landed (e.g. "→ ASM-005" / "→ DEC-007" / decided).
- **Status** — Draft | Proposed (open) | Approved (resolved) | Deferred | Rejected (no longer relevant).

## Open questions

| ID | Question | Blocking? | raised_by | Affects | Resolution | Status |
|---|---|---|---|---|---|---|
| OQ-001 | <what is unknown?> | Yes | <intake gap> | FR-003, DEC-002 | <unanswered> | Proposed |
| OQ-002 | <what is unknown?> | No | <stage 9 analysis> | NFR-002 | <recorded as ASM-002> | Approved |
| OQ-003 | <what is unknown?> | Yes | <contradiction between input §a and §b> | scope | <unanswered> | Proposed |

## Accepted-open (shipping with these unresolved)

<!-- Only NON-blocking questions belong here, each with why it is safe to proceed. If a blocking
     question must ship open, that requires an explicit recorded acceptance by the owner. -->
- `OQ-00x` — <why proceeding is acceptable; what to watch>.
