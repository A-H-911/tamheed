---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Initial Handoff Prompt — <project-name>

<!-- The FIRST message for Claude Code (CLI/IDE) to start implementation. It must
     (1) ORIENT, (2) give ONE bounded task, (3) STOP at an approval gate. It NEVER authorizes building
     the whole system at once. Replace EVERY <placeholder> — a shipped prompt with an unfilled <…> is a
     G-HANDOFF failure. Reference entities by real ids. List INV- up front.
     Generation class: Always. A PROJECT prompt file in `<package>/prompts/` (purpose-named).
     Shape: references/prompt-templates.md. -->

---

## Prompt (copy below this line)

This repository contains the APPROVED plan for **<project-name>**. You are starting implementation.

<one-paragraph orientation: what the project is, where the package store lives (the `data/*.jsonl`
directory the MCP server opens), that the decisions in the ADRs and approved registers are FINAL, and that you must not
expand scope beyond what each step authorizes>.

**Invariants you must respect at all times (do not violate, from the first commit):**
- `INV-001` — <invariant statement>
- `INV-002` — <invariant statement>
<!-- List every INV- explicitly; do not paraphrase loosely. -->

**Standing context:** Claude Code auto-loads `CLAUDE.md` (repo root), which imports `AGENTS.md` — the ambient
control surface (the invariants + the "violation ⇒ new ADR" rule, the hard constraints, and the tracking
protocol below). These steps bootstrap and gate; that standing context governs every action in between.

### Step 1 — Orientation (use plan mode; NO code)

Read the plan:
- the charter: `entity_query("narrative-document")` (doc_kind `charter`) → its `document-section` rows
- the architecture narrative the same way (doc_kind `architecture`)
- `entity_query("requirement", status="Approved")` and `entity_query("invariant")`
- `entity_query("phase")`, `entity_query("slice")`, `entity_query("acceptance-criterion")`
- the human surface: `<package>/review.html`
<!-- Orientation is QUERIES, not files — the store is the record (v2+). -->

Then give me:
(a) a **<=1-page summary** of what you will build and the invariants you must respect (`INV-001..INV-00n`);
(b) your **execution plan for Phase `PH-1`** with the file layout you propose and a **pass/fail** check per task.

**STOP and wait for my approval.** Do not write code yet.

### Step 2 — <first bounded task> (only after approval)

Work **acceptance-criteria-first**, one bounded task at a time: pick an `AC-`, write the failing test,
implement until it passes, then repeat — e.g. "Implement <thin slice> so that `AC-001` passes. PASS =
<observable>; FAIL = <observable>." Do one task, then **pause for review** — do not batch ahead.

**Track as you go (v4, plan 031 — the MCP tools ARE the record):** keep a live task list
with TodoWrite; per unit of work `progress_update(...)` (event_type `work-done`,
`subject_id`, your `actor` string); per verified criterion `audit_record(verdicts=[{ac_id,
verdict, evidence, verified_by, verification_method, against_commit}])` — the full
evidence chain, never Met without proof; per commit/PR `work_bind(ref, entity_ids=[...])`.
Work you believe complete is claimed as **`Review`** (full-row upsert) — `Implemented`
means VERIFIED and the slice/phase transition is readiness-guarded. The package is the
live checklist — report progress against `gate_run()` / `readiness_check(scope)`, never a
hand-maintained copy.

### Rules

- Respect the invariants (`INV-`) at every step.
- Pin dependency versions; introduce no unvetted dependencies (see prerequisites).
- Any deviation from the plan: a `scope-change` row (`SC-`) FIRST, `decision_ref` naming
  the deciding `DEC-`/`ADR-` (upsert the decision if none exists) — never silently
  deviate. A defect found → `defect` row (`DEF-`) before fixing; out-of-scope discovery
  → `deferred-work` row (`DW-`) with an activation trigger.
- Genuine ambiguity is never assumed away: an `open-question` row (`OQ-`, owner +
  due_by) and `[NEEDS-CLARIFICATION: OQ-NNN]` at the exact ambiguous spot.
- A readiness rule failing on one item you cannot resolve: ask the operator for a
  `WVR-` waiver — never author one yourself; `"force": true` only on their words.
- Do **not** expand scope beyond Phase `PH-1`.
- When in doubt about an approved decision, ask rather than re-deciding.

### Prerequisites

- Runtime(s): <pinned runtime + version>
- Tooling: <build/test tooling + versions>
- Access/accounts: <any required, or "none">
- Setup pitfalls: <platform-specific gotchas — venv activation, OS path/encoding quirks, never rely on
  system-installed assets/fonts; pin every version you install>.
- MVP definition: see the executive summary (doc_kind: executive-summary) / the package metadata.

<!-- Executor is Claude Code (CLI/IDE). On the autonomous cloud coworker — which runs to a PR rather than
     pausing between tasks — read each "STOP and wait for my approval" as "finish the bounded task, open a
     PR, and pause for review there." -->
