---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Constraint Register — <project-name>

<!-- Constraints are boundaries imposed from OUTSIDE the design space: budget, timeline, mandated
     platform/language, regulatory rules, organizational policy, interoperability requirements.
     A constraint limits HOW you may solve the problem; it is not itself a requirement of the system.
     (Contrast: an INVARIANT is a self-imposed non-negotiable property — see invariant-register.)
     Identified CON-NNN (governance.md). Generation class: Always.
     Lives at: requirements/constraint-register.md. -->

## Conventions

- **Type** — Budget | Timeline | Technical | Regulatory | Organizational | Interoperability | Other.
- **Constraint** — the boundary, stated concretely.
- **Source / authority** — who or what imposes it (so its firmness can be judged).
- **Impact** — what it rules out or forces in the design.
- **Status** — Draft | Proposed | Approved | Deferred | Superseded | Obsolete.

## Constraints

| ID | Type | Constraint | Source / authority | Impact on design | Status |
|---|---|---|---|---|---|
| CON-001 | Technical | Must run on <mandated runtime/version>. | <org standard / STK-001> | Rules out <alternatives>; pins dependency baseline. | Approved |
| CON-002 | Regulatory | Must comply with <regulation/standard>. | <regulation ref> | Adds <controls>; constrains data handling (see `NFR-003`). | Proposed |
| CON-003 | Timeline | <milestone> must be reachable by <date>. | <stakeholder STK-00x> | Forces phasing; affects MVP scope. | Proposed |
| CON-004 | Budget | <cost ceiling / no paid services>. | <sponsor> | Excludes <paid option>; favors <free/OSS option>. | Draft |

<!-- Reference constraints by ID downstream: decisions cite the CON- they respect; the traceability
     matrix and risk register may reference a CON- that drives a risk. -->
