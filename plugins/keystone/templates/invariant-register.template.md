---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Invariant Register — <project-name>

<!-- Invariants are NON-NEGOTIABLE properties that must hold at ALL times, in every phase, for every
     change. They are the rules an execution agent must never violate — they appear up front in the
     handoff prompts so the executor respects them from the first commit.
     (Contrast: a CONSTRAINT is externally imposed and may relax; an invariant is a chosen guarantee
     about the system's behavior or structure that does not relax.)
     Identified INV-NNN (governance.md). Generation class: Conditional (when invariants are present).
     Lives at: requirements/invariant-register.md. -->

## Conventions

- **Invariant** — stated as a property that is always true ("X never happens", "Y always holds").
- **Rationale** — why this must never break.
- **How enforced / verified** — mechanism (type system, test, schema validation, review gate, CI check).
- **Violation consequence** — what breaks if it is violated (justifies its non-negotiable status).
- **Status** — Draft | Proposed | Approved | Superseded | Obsolete.

## Invariants

| ID | Invariant | Rationale | How enforced / verified | Violation consequence | Status |
|---|---|---|---|---|---|
| INV-001 | <e.g. The same input always produces byte-identical output (determinism).> | <reproducibility is a core promise> | <golden-file tests in CI; TEST-00x> | <breaks reproducibility guarantee> | Approved |
| INV-002 | <e.g. No core module imports a specific vendor SDK.> | <vendor-neutrality> | <import-lint check; design review> | <couples core to one provider> | Approved |
| INV-003 | <invariant statement> | <rationale> | <mechanism> | <consequence> | Proposed |

<!-- List these IDs explicitly in the handoff initial prompt and in the invariant-audit review prompt.
     Each invariant should be verifiable by at least one TEST- where mechanically possible. -->
