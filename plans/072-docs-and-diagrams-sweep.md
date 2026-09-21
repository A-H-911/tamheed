# Plan 072: Docs and diagrams sweep for plans 063-071

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md). Run AFTER the code landed - the
> plan-061 lesson: a sweep that runs before the code plans cannot cover them.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (prose + one new diagram; lint-gated)
- **Category**: docs - **Planned at**: commit `a5d08d8`

## Method

A per-behavior `git grep` over README, SECURITY, CONTRIBUTING, `docs/`, SKILL, `references/`, the
server README, CANONICAL and the evals/lab/tests READMEs for every statement the batch made
stale, then a second grep proving each new behavior is documented outside `plans/` and the
CHANGELOG, and a third proving no stale doctrine line survives.

## What changed (nine files)

| Surface | Change |
|---|---|
| `docs/workflow.md` (sequence diagram) | **The diagram was wrong**: it drew canonical JSONL being written back at `package_close`. Every write flushes through the store; close only releases the lock. A field repo carried that same error in its own always-loaded rules until it measured otherwise |
| `docs/architecture.md` | **New section 8 + a state diagram**: the single-writer lock's lifecycle (Free / Held / Orphaned / Observed), the four observation outcomes, the unlock rule, the capability statement, and the flush contract. "fifteen" advisories -> sixteen |
| `plugins/tamheed/server/README.md` | The roster is 19 tools: a `package_unlock` row; `server_info(detail?)` and `package_verify(..., expect?)` signatures; additions on `package_open`, `package_close`, `entity_query`, `readiness_check`, `entity_export`, `package_migrate`, `export_html` |
| `README.md` | Tool table: `package_unlock`, `server_info(detail?)`, `package_verify(expect?)`, the read announcements |
| `SECURITY.md` | Three controls: the exporter deletes only what it provably wrote; **lock observation reads process metadata and nothing else** (a new capability, stated as doctrine: no spawn, no signal, bounded pid, capped strings); one destructive operator-only tool - and that "operator's words" is a convention, not a mechanism |
| `docs/install.md` | Upgrading: reload OR restart (a field observation: `/reload-plugins` sufficed for the MCP server); run `--selftest` with the live server's interpreter; the **dead-holder branch** (`package_unlock`), replacing "the store never guesses" with what it now does |
| `references/quality-gates.md` | sixteen advisories incl. `prose-ids-resolve`; read each rule's `population` |
| `SKILL.md` | `matched` / `omitted_columns`; a refused open reports the holder; `package_unlock` is the operator's word |
| `tests/README.md` | the contract suite's size |

**Diagrams audited, left as they are:** the tool lists in `README.md` block 1 and
`docs/architecture.md` block 1 are illustrative of the planning flow, not rosters, and
`package_unlock` is not part of that flow; `docs/entities.md`'s state and sequence diagrams
describe transitions plans 063-071 did not change. The emitted note's cheat-sheet lists routine
tools only, so the operator-only `package_unlock` is deliberately absent (the prompt guide and
`orient-resume.md` teach it).

## Verification

- `git grep` for "never guesses that", "remove the stale lock deliberately", "delete `data/.lock`
  when EITHER", "canonical JSONL written back", "fifteen at package scope": the only survivors
  are `stock-history.json` (the immutable record of past prompt bodies) and the test that asserts
  the old text is gone.
- Every new behavior greps to at least one doc surface outside `plans/` and the CHANGELOG.
- `python check.py lint` -> no FAIL (incl. lint 9b vocabulary and lint 10 path tokens).

## Done criteria

- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
