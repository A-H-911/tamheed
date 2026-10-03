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
- **The contract:** the Tamheed package `<package-name>`. The charter and registers come through
  `entity_query`, and the human surface is `<package-name>/review.html`. Decisions in approved
  `DEC-`/`ADR-` rows are FINAL. Do not re-litigate settled decisions.
- **Where you are now:** the `resume` block `package_open` / `server_info` return. It holds the
  latest `handoff` journal entry with its corrections, and the plugin's SessionStart hook prints it.
  Then `gate_run()` + `readiness_check(scope)` + the newest journal entries the block names
  (`last_entries`). A read cut by `limit` returns the OLDEST rows. Never a stale copy in this
  file. A status sentence written here ("phase N complete", "N criteria Met") goes stale on the
  next write and then reads as current. `handoff_emit` reports such sentences and id-dense
  paragraphs in this file (`restated_content`) so the query can replace them.

## Invariants — never violate (a violation requires a new ADR)

- `INV-001` — <one-line invariant>.
- `INV-002` — <one-line invariant>.
- Full list + rationale: `entity_query("invariant")` or `review.html#registers`.
- **Rule:** breaking an invariant is not a silent option. Upsert a new `adr` row (status
  Proposed) and STOP for approval.

## Hard constraints (refuse work that crosses these)

- <e.g. license / dependency bans, performance budgets, "no network at <stage>">.
- Full list: `entity_query("constraint")` + the NFR thresholds in
  `entity_query("requirement", status="Approved")`.

## Recording obligations (mandatory — unrecorded work is drift)

<!-- v5.2 (plan 132): this file no longer carries a copy of the obligations table. The table is
     the TOOL-OWNED note `handoff_emit` writes into `<package-name>/CLAUDE.md` (imported by the root
     CLAUDE.md) and rebuilds on every emit; a second copy here drifted, and a copy of register
     content is exactly the shape `handoff_emit`'s restated-content scan reports. -->

The obligations table says what to record before moving on. That is defects, deferred work, scope
changes, open questions, lessons and feedback. It is also work-done entries, `Review` claims,
verdicts, bindings, and readiness before any done-claim. The table is the
tool-owned tamheed note in `<package-name>/CLAUDE.md`, which this file's `CLAUDE.md` imports. It
is never copied here. If you cannot record (lock held, package missing), STOP and tell the operator.
Do not proceed unrecorded.

Before a compaction, at session end or on a handover, write a `handoff` journal entry LAST
(`tamheed:session-handoff`). It holds the resume point, the in-flight ids and what awaits the
operator. It holds the verified facts with the query that measured each, and what not to carry. The
`handoff-current` advisory names a missing or stale one, and the next session reads it first.

## Operating conventions

- Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement,
  `audit_record` with evidence, repeat.
- No phase starts with red CI. Keep changes small and reviewable.
- **The HOW of every package write, read and git crossing is the tamheed plugin's
  `tamheed:package-writes` skill** (v5). Commit the package `data/` before branch operations,
  and run `git status --porcelain -uall` immediately before any branch operation (recording
  FLUSHES `data/*.jsonl` after the commit it records). Read registers through the tools,
  never the files: `entity_query` pages, `entity_export` for a committed script,
  `package_verify()` for the canonical proof. A status flip on a long row names its
  untouched columns (`expect_unchanged`) or uses `substitute`. `tamheed:reading-the-record`
  before citing a row, `tamheed:operator-interview` at every STOP.

## Kickoff

Start from the kickoff prompt in `<package-name>/prompts/` (project-authored). The recurring
situations are the plugin's slash skills. `/tamheed:package-onboarding` is for an agent that has
never seen the package. Then `/tamheed:orient-resume`, `/tamheed:slice-kickoff`,
`/tamheed:progress-sync`, and the rest. `<package-name>/prompts/README.md` maps every situation.
