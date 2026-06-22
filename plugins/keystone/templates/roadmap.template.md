---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Roadmap — <project-name>

<!-- A phased plan. Each phase (PH-N) is a coherent increment with its own goal, scope, deliverables,
     validation, risks, and an EXIT gate that must pass before the next phase starts (gate G-EXEC).
     The first phase typically delivers the MVP slice. Generation class: Always.
     Lives at: planning/roadmap.md. Phases drive the follow-up handoff prompts (one per phase gate). -->

## Phase overview

| Phase | Goal | Delivers | Exit gate (one line) |
|---|---|---|---|
| PH-1 | <goal> | <headline deliverable / MVP> | <what must be true to proceed> |
| PH-2 | <goal> | <deliverable> | <exit> |
| PH-3 | <goal> | <deliverable> | <exit> |

---

## PH-1 — <phase title>

- **Goal:** <the outcome this phase achieves>
- **Scope:** <what is included; FR-/NFR- addressed (e.g. FR-001..FR-005, NFR-001)>
- **Out of scope (this phase):** <deferred to later phases>
- **Deliverables:**
  - <concrete deliverable 1>
  - <concrete deliverable 2>
- **Validation:** <how the phase is verified — tests TEST-00x, acceptance AC-00x, demo>
- **Risks (phase-specific):** <RISK-00x and how handled in this phase>
- **Exit criteria:** <the gate — measurable conditions that must hold to start PH-2>
- **Dependencies:** <DEP-00x; prior phase outputs>

## PH-2 — <phase title>

- **Goal:** <outcome>
- **Scope:** <FR-/NFR- addressed>
- **Out of scope (this phase):** <…>
- **Deliverables:**
  - <deliverable>
- **Validation:** <…>
- **Risks (phase-specific):** <…>
- **Exit criteria:** <gate>
- **Dependencies:** <PH-1 complete; DEP-00x>

## Cross-phase rules

- Phase gates are demos + checklists, **not dates** — a phase ends when its exit criteria are met.
- **No phase starts with red CI**; keep every change small and reviewable.
- Any mid-phase scope or backend change ⇒ a new **ADR** + a **risk-register** update (never silent).
- The golden/example corpus only grows; nothing ships without its sample and tests green.

<!-- Add PH-3.. as needed. Keep phases few and coherent; do not pad. Every leaf of work belongs to a
     phase and maps to a WBS- item in work-breakdown.md. -->
