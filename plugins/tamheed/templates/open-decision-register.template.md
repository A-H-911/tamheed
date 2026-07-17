---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Open Decision Register — <project-name>

<!-- Lightweight decisions and their current status. CRITICAL SAFEGUARD: a Proposed decision is never
     rendered or treated as if Approved (G-DEC-STATUS). Decision statuses are EXACTLY:
     Proposed | Approved | Rejected | Superseded | Deferred.
     PROMOTION: when a decision is architecturally significant (hard to reverse, broad blast radius),
     promote it to an ADR and record the link (e.g. "DEC-007 -> ADR-0003") so it is never lost.
     Identified DEC-NNN (governance.md). Generation class: Always.
     Lives at: decisions/open-decision-register.md. -->

## Conventions

- **Decision** — the question being decided, phrased as a choice.
- **Options** — the candidates considered (keep the rejected ones; they are evidence).
- **Recommendation** — the proposed option (with the deciding reason).
- **Rationale** — why the recommendation beats the alternatives.
- **Links** — requirements it serves (`FR-/NFR-`), constraints respected (`CON-`), promoted ADR.
- **Status** — Proposed | Approved | Rejected | Superseded | Deferred (no other values).
- **Deviation (⚠)** — when the Approved outcome differs from the Recommendation, mark the row ⚠ and state
  the consequence in Rationale, so a reversal from the recommended path is never silent.

## Decisions

| ID | Decision | Options | Recommendation | Rationale | Links | Status |
|---|---|---|---|---|---|---|
| DEC-001 | <choice to be made> | <opt A / opt B / opt C> | <opt B> | <why B> | FR-001, CON-002 | Proposed |
| DEC-002 | <choice to be made> | <opt A / opt B> | <opt A> | <why A> | NFR-001 | Approved |
| DEC-003 | <choice to be made> | <opt A / opt B> | <opt B> | <why> | FR-004 | Deferred |

## Promotions to ADR

<!-- Record every promotion so the DEC <-> ADR link survives. -->
| Decision | Promoted to | Reason for promotion |
|---|---|---|
| DEC-00x | ADR-000x | <architecturally significant: hard to reverse / broad blast radius> |

<!-- On supersession: create a new DEC- (or ADR-) and set supersedes/superseded_by on both ends; keep
     the old row at status Superseded. Only Approved decisions constrain execution. -->
