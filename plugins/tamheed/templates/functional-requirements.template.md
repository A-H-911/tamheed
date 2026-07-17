---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Functional Requirements — <project-name>

<!-- What the system must DO. One row per requirement, identified FR-NNN (governance.md).
     Generation class: Always. Lives at: requirements/functional.md.
     Every FR MUST carry a `source` (gate G-REQ-SRC) and a `status`. Priority is MVP or Full.
     Each FR must be reachable in the traceability matrix to >=1 decision, >=1 task, >=1 test, and
     (if it asserts user-visible behavior) an acceptance criterion. -->

## Conventions

- **Statement** — testable "the system shall …" phrasing. Avoid solutioning; say WHAT, not HOW.
- **Source** — where it came from: input span, `STK-`, `OQ-` resolution, regulation, derived-from `FR-/NFR-`.
- **Priority** — `MVP` (must ship in the minimal viable product) or `Full` (full target).
- **Status** — Draft | Proposed | Approved | Implemented | Rejected | Deferred | Superseded | Obsolete.

## Requirements

| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| FR-001 | The system shall <observable behavior>. | <input §x / STK-002 / OQ-004> | MVP | Proposed |
| FR-002 | The system shall <observable behavior>. | <derived from FR-001> | Full | Proposed |
| FR-003 | The system shall <observable behavior>. | <source> | MVP | Draft |

## Detail (optional, per requirement)

<!-- Use only for requirements that need more than one line. Keep the table above as the index. -->

### FR-001 — <short title>
- **Rationale:** <why this is needed>
- **Acceptance:** links to `AC-NNN` (see [acceptance criteria](../validation/acceptance-criteria.md)).
- **Notes / open points:** <e.g. blocked by OQ-00x>
