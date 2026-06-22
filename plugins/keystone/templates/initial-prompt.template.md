---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Initial Handoff Prompt — <project-name>

<!-- The FIRST message to paste into a (generically capable, agent-neutral) execution agent. It must
     (1) ORIENT, (2) give ONE bounded task, (3) STOP at an approval gate. It NEVER authorizes building
     the whole system at once. Replace EVERY <placeholder> — a shipped prompt with an unfilled <…> is a
     G-HANDOFF failure. Reference artifacts by real relative paths in this package. List INV- up front.
     Generation class: Always. Lives at: handoff/initial-prompt.md. Shape: references/prompt-templates.md. -->

---

## Prompt (copy below this line)

This repository contains the APPROVED plan for **<project-name>**. You are starting implementation.

<one-paragraph orientation: what the project is, where the plan lives (e.g. `docs/plan/` or this
package root), that the decisions in the ADRs and approved registers are FINAL, and that you must not
expand scope beyond what each step authorizes>.

**Invariants you must respect at all times (do not violate, from the first commit):**
- `INV-001` — <invariant statement>
- `INV-002` — <invariant statement>
<!-- List every INV- explicitly; do not paraphrase loosely. -->

**Standing context:** keep `AGENTS.md` (repo root) loaded for the whole engagement — it is the ambient
control surface (the invariants + the "violation ⇒ new ADR" rule, the hard constraints, and the tracking
protocol below). These steps bootstrap and gate; `AGENTS.md` governs every action in between.

### Step 1 — Orientation (NO code)

Read these plan documents:
- [Charter](../00-charter.md)
- [Architecture](../architecture/architecture.md)
- [Functional requirements](../requirements/functional.md) and [non-functional](../requirements/non-functional.md)
- [Roadmap](../planning/roadmap.md) and [acceptance criteria](../validation/acceptance-criteria.md)
- [Invariant register](../requirements/invariant-register.md)
<!-- List only the few documents needed to orient. Use paths that EXIST in this package. -->

Then give me:
(a) a **<=1-page summary** of what you will build and the invariants you must respect (`INV-001..INV-00n`);
(b) your **execution plan for Phase `PH-1`** with the file layout you propose and a **PASS/FAIL** check per task.

**STOP and wait for my approval.** Do not write code yet.

### Step 2 — <first bounded task> (only after approval)

Work **acceptance-criteria-first**, one bounded task at a time: pick an `AC-`, write the failing test,
implement until it passes, then repeat — e.g. "Implement <thin slice> so that `AC-001` passes. PASS =
<observable>; FAIL = <observable>." Do one task, then **pause for review** — do not batch ahead.

**Track as you go (before each pause / phase gate):** update `../validation/acceptance-criteria.md`
(status + evidence), update `../validation/acceptance-audit.md` (verdict + evidence per `AC-`), append
`../progress/progress-log.md`, and regenerate `../progress/status-report.md`. Keep the acceptance
criteria as the live checklist and report progress against it.

### Rules

- Respect the invariants (`INV-`) at every step.
- Pin dependency versions; introduce no unvetted dependencies (see prerequisites).
- Record any deviation from the plan as a new **ADR** (`adrs/adr-NNNN-*.md`) — never silently deviate.
- Do **not** expand scope beyond Phase `PH-1`.
- When in doubt about an approved decision, ask rather than re-deciding.

### Prerequisites

- Runtime(s): <pinned runtime + version>
- Tooling: <build/test tooling + versions>
- Access/accounts: <any required, or "none">
- Setup pitfalls: <platform-specific gotchas — venv activation, OS path/encoding quirks, never rely on
  system-installed assets/fonts; pin every version you install>.
- MVP definition: see [executive summary](../01-executive-summary.md) / manifest.

<!-- Optional, clearly-labeled agent-specific tips go in an appendix ONLY, never in the body (safeguard 13). -->
