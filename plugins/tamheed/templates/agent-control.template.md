---
owner: <name-or-role>
---
<!-- v5.1 (plan 124): no status/version/updated/generation fields. This file is hand-maintained
     and nothing regenerates it; a version stamp or a "derived" claim on it is a promise without a
     mechanism, and the field carried both for two months on a file edited by hand. Live state
     arrives from the store at session start (the resume block); this file holds standing rules. -->


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
- **Where you are now:** the `resume` block `package_open` / `server_info` return (the latest
  `handoff` journal entry with its corrections — the plugin's SessionStart hook prints it), then
  `gate_run()` + `readiness_check(scope)` + the latest `progress-entry` rows — never a stale copy
  in this file. A status sentence written here ("phase N complete", "N criteria Met") goes stale
  on the next write and then reads as current; `handoff_emit` reports such sentences and id-dense
  paragraphs in this file (`restated_content`) so they can be replaced by the query.

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
     (tamheed_server.py, tamheed:note v5) — drift between the two is grep-detectable. -->

| During execution, when… | Record BEFORE moving on |
|---|---|
| you find a defect | `entity_upsert` a `defect` row (`DEF-`, honest severity — open critical/high BLOCK readiness) — then fix it |
| you find needed work that is out of scope | `entity_upsert` a `deferred-work` row (`DW-`) with an activation trigger |
| you deviate from the approved plan in any way | a `scope-change` row (`SC-`) FIRST, `decision_ref` naming the deciding `DEC-`/`ADR-`, delta edges (`scope_adds`/`scope_modifies`/`scope_removes` for plan rows; `amends` for a ruling — DEC-: full-row upsert, ADR-: supersede) naming the affected rows — after approval, apply the row changes, RE-READ them, and only then set the `SC-` to Merged |
| you hit genuine ambiguity | an `open-question` row (`OQ-`, with owner + due_by) and `[NEEDS-CLARIFICATION: OQ-NNN]` at the exact spot — NEVER assume |
| execution teaches you something durable (a mistake's fix, a practice worth repeating) | `entity_upsert` a `lesson` row (`LL-`, born Proposed; kind improve\|sustain, statement + impacts) + a `learned_from` edge to the source — the OPERATOR confirms later; only Approved lessons bind |
| you need a function tamheed lacks, meet a defect or a doc error in it, have a question for its maintainer, or would build a script over the package | a `feedback` row (`FB-`; kind missing-capability\|defect\|doc-error\|question, born Proposed) FIRST — never a side tool: a script is a `local-tool` row that CANNOT be a draft (the OPERATOR's word is a precondition of its insert); it writes nothing tool-owned and, if it reads the STORE, reads `exports/` only; `handoff_emit` names every row until it has left the package, and every reported row until it is answered (`feedback-unanswered`) |
| you finish a unit of work | `progress_update(...)` — event_type `work-done`, `subject_id`, your `actor` string, phase/slice ids |
| you believe a slice/wbs-item is complete | set its `lifecycle_status` to **Review** (done-claimed) — `Implemented` means VERIFIED and is readiness-guarded |
| you verify an acceptance criterion | `audit_record(...)` with evidence + `verified_by` + `verification_method` + `against_commit` — never Met without proof |
| you create a commit or PR | `work_bind(ref, entity_ids=[...])` |
| you declare a slice/phase/release done | `readiness_check(scope)` first — resolve every blocking failure, or ask the OPERATOR for a `WVR-` waiver (their words; you never author your own) — `"force": true` only on the operator's explicit words |

If you cannot record (lock held, package missing), STOP and tell the operator — do not
proceed unrecorded.

Before a compaction, at session end or on a handover, write a `handoff` journal entry LAST
(`tamheed:session-handoff`: resume point, in-flight ids, what awaits the operator, verified facts
with the query that measured each, what not to carry); the `handoff-current` advisory names a
missing or stale one, and the next session reads it first.

## Operating conventions

- Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement,
  `audit_record` with evidence, repeat.
- No phase starts with red CI; keep changes small and reviewable.
- **The HOW of every package write, read and git crossing is the tamheed plugin's
  `tamheed:package-writes` skill** (v5): commit the package `data/` before branch operations
  and run `git status --porcelain -uall` immediately before any branch operation (recording
  FLUSHES `data/*.jsonl` after the commit it records); read registers through the tools,
  never the files (`entity_query` pages, `entity_export` for a committed script,
  `package_verify()` for the canonical proof); a status flip on a long row names its
  untouched columns (`expect_unchanged`) or uses `substitute`. `tamheed:reading-the-record`
  before citing a row; `tamheed:operator-interview` at every STOP.

## Kickoff

Start from the kickoff prompt in `<package-name>/prompts/` (project-authored); the
recurring situations are the plugin's slash skills — `/tamheed:package-onboarding` for an
agent that has never seen the package, then `/tamheed:orient-resume`, `/tamheed:slice-kickoff`,
`/tamheed:progress-sync`, … (`<package-name>/prompts/README.md` maps every situation).
