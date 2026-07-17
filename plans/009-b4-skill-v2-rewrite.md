# Plan 009 (B4): Rewrite the skill for v2 — MCP-driven stages, enriched parameters, bootstrap removal

> **Executor instructions**: Large rewrite plan. Work reference-file by reference-file; keep the
> bundle self-contained at every commit. STOP conditions are binding.
>
> **Drift check (run first)**: plans 007+008 landed (`plugins/tamheed/db/`, `plugins/tamheed/server/`
> exist; their tests pass). Missing → STOP.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED
- **Depends on**: plans/008-b3-mcp-server.md
- **Category**: architecture / migration
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

The skill (SKILL.md + references) still describes the v1 world: stages that write Markdown files
from templates, a repo bootstrap, and a file-scanning validator. In v2 the 22-stage methodology is
unchanged in *meaning* but every artifact-producing stage now drives MCP tools, `update` becomes
the agile heart of the system (maintainer decision D-UPDATE), and the repo-creation capability is
removed entirely (ASM-B). The methodology IS the product — this rewrite must preserve its
substance (operating principles, gates, governance) while swapping the storage/interaction layer.

## Current state

- `plugins/tamheed/SKILL.md` — 193-line front door; body describes template-driven generation
  (stages 16–18), the bootstrap (`scripts/init_skill_repo.py`), and file-based state
  (`keystone-state.json`).
- `plugins/tamheed/references/` — 17 files; most affected: `workflow.md` (22-stage spec),
  `modes.md`, `state.md`, `artifact-rules.md`, `generated-structure.md`, `handoff.md`,
  `repo-init.md` (deleted), `quality-gates.md` (gate execution now = `gate_run`),
  `safeguards.md` (bootstrap-related safeguards retired; untrusted-content safeguard 18 stays).
- Bootstrap to delete (ASM-B): `plugins/tamheed/scripts/init_skill_repo.py`, `init_skill_repo.ps1`,
  `init_skill_repo.sh`, `plugins/tamheed/scripts/README.md`, `references/repo-init.md`.
- `plugins/tamheed/templates/` — 43 `*.template.md`. In v2, register-class templates become
  entity-type metadata (plan 007's `entity_types` registry defines shape); narrative templates
  (charter, exec summary, ADR, architecture) survive as **section templates** for
  `narrative_documents`. This plan decides per-template disposition using
  `plans/deliverables-review.md` (the approved artifact set).
- The maintainer keeps: SKILL.md and references remain **Markdown** (ASM-C — that is how Claude
  Code loads skills); only *generated package* storage changed.

## D-UPDATE — the three confirmed `update` capabilities (implement all three)

1. **Diff-aware re-derivation**: a change to an entity → `trace_query` computes the impact set →
   preview to the operator → targeted regeneration of dependents only.
2. **Execution-progress sync**: ingest the executing agent's `progress_update`/`audit_record`
   output into the package during update cycles.
3. **Agile scope change** (mid- or post-execution): new/changed requirements enter as a recorded
   `scope_changes` row + decision → impact analysis → re-derived phases/ACs/roadmap → the
   iteration counter increments; entities carry `introduced_in`/`retired_in`. The v1 rule "scope
   drift after lock requires a recorded decision" becomes this mechanism.
   **Field-evidence extension (C4, 2026-07-17)**: scope events are TYPED —
   {defer, reschedule, reclassify, cancel, expand} — distinct from supersede, each mechanically
   linked to the affected entities. All three field projects narrated these in prose ("this is a
   scheduling deferral, not a reopen") because v1 could not express "same decision, changed
   phase." Additionally: the skill's writing discipline resolves inline uncertainty markers
   (`[unverified: …]`, TBD-with-meaning) into `OQ-` entities with status, never free-text tags.

## Parameter contract (enriched per D-UPDATE + program plan)

- `--mode full | intake | plan | resume | update | adopt | migrate | stage:<id>` (adopt/migrate
  documented here; implemented in plans 011/010).
- `--profile <type>` — registry-backed: profiles live in `entity_types`-adjacent registry so the
  community can add them (plan 015).
- `--package-dir <dir>` — explicit, validated (created if absent; must not be inside the plugin).
- `--dry-run` — transactional preview: run the stage's mutations inside a SQLite SAVEPOINT,
  report what WOULD change (entity counts, gate deltas), roll back.
- REMOVED: `--no-repo` (meaningless once there is no repo bootstrap).

## Scope

**In scope**: `plugins/tamheed/SKILL.md`, all `references/*.md`, deletions listed above,
per-template disposition in `templates/`, `plans/README.md`.

**Out of scope**: server code (008), migration/adopt logic (010/011), viewer (012), README/docs
(014), CONTRIBUTING/extension mechanics (015), the v1 validator + JSON schemas
(**frozen — they are the migration source contract; plan 010 reads them**).

## Steps

1. **Dispositions first**: from `plans/deliverables-review.md`, write a short mapping table
   (template → keep-as-section-template | retire-to-entity-type | drop) into the commit message
   body; retire/drop accordingly (`git rm` retired templates — their shape now lives in the
   entity registry).
2. **Delete the bootstrap** (files listed in Current state); sweep references:
   `git grep -n "init_skill_repo\|repo-init\|--no-repo"` → update every hit (SKILL.md stage 18,
   workflow.md, safeguards, quality-gates' bootstrap rows, extension.md if present).
   Stage 18 ("repository initialization") is re-purposed: "package storage initialization"
   (`package_create`).
3. **Rewrite SKILL.md**: keep the 10 operating principles verbatim (they are storage-agnostic);
   swap the "How to run each phase" section to name the MCP tools per stage; update the reference
   index; update Requirements (Python floor per ASM-D; `uv` or `pip install mcp`; MCP-capable
   host). Keep description ≤1024 chars and body <500 lines (platform limits).
4. **Rewrite the affected references**: `workflow.md` per-stage inputs/outputs now name tools +
   entity types; `state.md` — state lives in the DB (`packages` row + entities), file
   `keystone-state.json` is retired (migration reads it; plan 010); `modes.md` adds
   adopt/migrate + the D-UPDATE spec; `quality-gates.md` gains the three-tier mapping table
   (constraints / views / content+judgment) mirroring plan 007's ADR.
5. **End-to-end dry-run**: with the server from plan 008, walk a minimal brief through
   intake → scope → plan → generate → gate_run manually (operator-driven), producing a DB-backed
   package that `gate_run` passes.

**Verify**: after each step, `python tests/test_mcp_contract.py` + `test_db_roundtrip.py` exit 0;
after step 2, `git grep -c "init_skill_repo"` (excluding plans/, docs/history/, CHANGELOG.md) → 0;
after step 5, record the walk-through transcript path in the commit message.

## Done criteria

- [ ] Bootstrap fully deleted; zero live references
- [ ] SKILL.md ≤1024-char description, <500-line body, names MCP tools per stage
- [ ] All three D-UPDATE capabilities specified in modes.md with concrete tool sequences
- [ ] Bundle self-containment holds: `git grep -n "\.\./\.\." plugins/tamheed/` → 0 matches
- [ ] End-to-end manual walk-through produced a gate-passing DB package
- [ ] `plans/README.md` updated

## STOP conditions

- A stage cannot be expressed through the plan-008 tool surface — report the missing tool; do not
  add server code in this plan.
- Template disposition conflicts with the approved deliverables review — the review wins; report
  discrepancies.
- SKILL.md limits (1024/500) can't be met — report, don't silently truncate meaning.

## Maintenance notes

- The 10 operating principles are the product's soul — any future edit to them needs maintainer
  sign-off, storage changes never justify weakening them.
- Reviewer scrutiny: stage 18's re-purposing; that `update` mode's scope-change flow always
  writes a `scope_changes` row BEFORE mutating requirements.
