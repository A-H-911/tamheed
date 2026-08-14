---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
generation: derived      # regenerated from the package each update cycle
---

# AGENTS.md — standing operating context for <project-name>

<!-- The AMBIENT control surface for Claude Code (the executor). Claude Code auto-loads CLAUDE.md at the repo
     root every session; CLAUDE.md imports this AGENTS.md (Anthropic's documented idiom — "Claude Code reads
     CLAUDE.md, not AGENTS.md; create a CLAUDE.md that imports it"), so this file is where the plan's
     non-negotiables KEEP governing the work after the one-time kickoff prompt. The content lives here in
     AGENTS.md; CLAUDE.md is the loaded entry that pulls it in (@AGENTS.md) and may add Claude-specific notes
     below the import.

     v3 (plan 027): the package is RELATIONAL — entities read via the tamheed MCP tools, reviewed via
     review.html. Reference the package, never restate it: quote the few load-bearing invariants inline,
     point at `entity_query` / `review.html#registers` for the rest. Volatile state (current phase) is a
     query, not a copy. Regenerated each update cycle; do not hand-maintain. -->

## Project state

- **What this is:** <one line>.
- **The contract:** the Tamheed package `<package-name>` — charter and registers via
  `entity_query`, the human surface at `<package-name>/review.html`. Decisions in approved
  `DEC-`/`ADR-` rows are FINAL; do not re-litigate settled decisions.
- **Where you are now:** `gate_run()` + `readiness_check(scope)` + the latest
  `progress-entry` rows — never a stale copy in this file.

## Invariants — never violate (a violation requires a new ADR)

- `INV-001` — <one-line invariant>.
- `INV-002` — <one-line invariant>.
- Full list + rationale: `entity_query("invariant")` or `review.html#registers`.
- **Rule:** breaking an invariant is not a silent option — upsert a new `adr` row (status
  Proposed) and STOP for approval.

## Hard constraints (refuse work that crosses these)

- <e.g. license / dependency bans, performance budgets, "no network at <stage>">.
- Full list: `entity_query("constraint")` + the NFR thresholds in
  `entity_query("requirement", status="Approved")`.

## Recording obligations (mandatory — unrecorded work is drift)

<!-- Keep this table IDENTICAL to the one in the emitted CLAUDE.md operating note
     (tamheed_server.py, tamheed:note v3) — drift between the two is grep-detectable. -->

| During execution, when… | Record BEFORE moving on |
|---|---|
| you find a defect | `entity_upsert` a `defect` row (`DEF-`, honest severity — open critical/high BLOCK readiness) — then fix it |
| you find needed work that is out of scope | `entity_upsert` a `deferred-work` row (`DW-`) with an activation trigger |
| you deviate from the approved plan in any way | a `scope-change` row (`SC-`) FIRST, `decision_ref` naming the deciding `DEC-`/`ADR-`, delta edges (`scope_adds`/`scope_modifies`/`scope_removes`) naming the affected rows — after approval, apply the row changes and set the `SC-` to Merged |
| you hit genuine ambiguity | an `open-question` row (`OQ-`, with owner + due_by) and `[NEEDS-CLARIFICATION: OQ-NNN]` at the exact spot — NEVER assume |
| you finish a unit of work | `progress_update(...)` — event_type `work-done`, `subject_id`, your `actor` string, phase/slice ids |
| you believe a slice/wbs-item is complete | set its `lifecycle_status` to **Review** (done-claimed) — `Implemented` means VERIFIED and is readiness-guarded |
| you verify an acceptance criterion | `audit_record(...)` with evidence + `verified_by` + `verification_method` + `against_commit` — never Met without proof |
| you create a commit or PR | `work_bind(ref, entity_ids=[...])` |
| you declare a slice/phase/release done | `readiness_check(scope)` first — resolve every blocking failure, or ask the OPERATOR for a `WVR-` waiver (their words; you never author your own) — `"force": true` only on the operator's explicit words |

If you cannot record (lock held, package missing), STOP and tell the operator — do not
proceed unrecorded.

## Operating conventions

- Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement,
  `audit_record` with evidence, repeat.
- No phase starts with red CI; keep changes small and reviewable.
- **Commit the package `data/` before branch operations** — package writes live in the
  git working tree like any uncommitted change.

## Kickoff

Start from the kickoff prompt in `<package-name>/prompts/` (project-authored); the stock
scenario prompts there (slice-kickoff, progress-sync, orient-resume, …) cover the
recurring situations — read the folder and pick.
