---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Non-Functional Requirements — <project-name>

<!-- HOW WELL the system must behave: performance, scalability, reliability, security, usability,
     maintainability, portability, observability, accessibility, compliance.
     One row per requirement, identified NFR-NNN (governance.md). Generation class: Always.
     Lives at: requirements/non-functional.md.
     Every NFR MUST be MEASURABLE (a threshold + how it is measured) and carry a `source` (G-REQ-SRC).
     A vague NFR ("fast", "secure") is a defect — replace it with a number and a method. -->

## Conventions

- **Quality attribute** — the category (Performance, Security, Reliability, …).
- **Threshold** — the measurable target (number + unit + condition). This is what makes it testable.
- **Measurement** — how the threshold is verified (tool, environment, load).
- **Priority** — `MVP` or `Full`. **Source** and **Status** as in functional requirements.

## Requirements

| ID | Quality attribute | Statement | Threshold | Measurement | Source | Priority | Status |
|---|---|---|---|---|---|---|---|
| NFR-001 | Performance | <operation> completes within budget under <load>. | <e.g. p95 < 200 ms at 100 rps> | <load test on ref env> | <source> | MVP | Proposed |
| NFR-002 | Reliability | The system sustains availability over <window>. | <e.g. >= 99.9% monthly> | <uptime probe> | <source> | Full | Proposed |
| NFR-003 | Security | <data class> is protected per <policy>. | <e.g. encrypted at rest + in transit; 0 criticals in scan> | <SAST/DAST + review> | <regulation> | MVP | Draft |
| NFR-004 | Maintainability | <e.g. new <component type> added without core edits>. | <e.g. via registry only; 0 core diffs> | <design review> | <derived from NFR-002> | Full | Proposed |

## Detail (optional, per requirement)

### NFR-001 — <short title>
- **Rationale:** <why this level is required>
- **Verified by:** `TEST-NNN` (see [test strategy](../validation/test-strategy.md)).
- **Trade-offs:** <what this threshold costs, links to relevant ADR/DEC>
