# Plan 131: two more cues, the stranded rule's population, and the skill guard (findings_33 Q1, §4)

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (additive keys; one new engine journal row)

## Why this matters

findings_33 Q1 measured the cue mechanism under 5.1.0: **no discipline skill loaded without a tool
result naming it**, and the always-loaded note naming all eight cued nothing. `reading-the-record`
and `written-claims` were named by no result at all (the three evidence skills are named by
`audit_record`, unexercised that round). R4 ("hints on phase-start tools only") was revisited on
that evidence — R8. §4 found two engine facts: `lessons-stranded`'s population was the whole
lessons table (111 rows) rather than the Promoted lessons a retired skill can strand, and a skill
row's retirement was the one lifecycle move the engine did not witness (ACMP wrote `PE-1463` by
hand) — R13.

## What changes

- `entity_query`: `skill: "tamheed:reading-the-record"` on every result. `entity_export` drops the
  key from the exported result: a script's input never carries a model cue (and never churns for
  one — ACMP commits its `exports/`).
- `handoff_emit`: `skill: "tamheed:written-claims"` present iff `restated_content`,
  `stale_references`, `oversized_prompts` or an unverified `stock_merged` entry exists.
- `lessons-stranded`: `population = {table: lessons, rows: COUNT Promoted, scoped: false,
  unit: "promoted lessons"}` (the plan-122 hand-set pattern).
- `system:skill-guard` in `entity_upsert` (mirrors the feedback guard): for an EXISTING skills
  row, a `lifecycle_status` change or an `upstreamed_to` / `superseded_by` arriving on a NULL
  column journals one `transition` — `SKILL SKL-NNN -> <now> (was <was>); upstreamed_to X` —
  actor `system:skill-guard`, `subject_id` the skill, result key `skill_audit`. Never on INSERT
  (skill-promote journals `lesson-promoted`); an omitted `lifecycle_status` reads as unchanged
  (the field's retirements were partial rows); an idle re-send journals nothing. The row counts
  toward `handoff-current` (R12).
- Docs: `server/README.md`, `references/governance.md`, `references/quality-gates.md`,
  `docs/entities.md`, `docs/architecture.md` (the RES node), `SECURITY.md`, CHANGELOG.

## Tests

- `test_result_hints_name_the_discipline_skill`: the `entity_query` key; the export file lacks it.
- `test_stale_warning_block_retracts_when_clean`: `handoff_emit`'s key absent on a clean emit,
  `tamheed:written-claims` on the stale one.
- `test_lessons_stranded_passes_once_the_pointer_exists`: the population unit and count.
- `test_skill_lifecycle_moves_are_journalled_by_the_engine`: insert → no row; partial-row
  retirement → one `system:skill-guard` transition with the pointer; idle re-send → none;
  `handoff-current` behind by exactly that row.

## Measured after the change (the ACMP replay, plan §5.1.1)

See the batch record §0.
