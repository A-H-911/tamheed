# Plan 192: the `prompts` family (migration 008, the registry, the catalog, the guide)

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings P1, P7, P10, P11. Ledger first.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: LOW (additive DDL; the sync lints catch a partial add) - **DONE 2026-10-04**

## What this beat changes

- `db/migrations/008_prompts.sql`: the `prompts` table with the rationale header (the 005/007
  precedent) and its two `entity_index` triggers. `schema.sql` and `001_init.sql` stay untouched
  (lint 2: new DDL goes in an append-only migration, never in the twins).
- `server/tamheed_server.py`: `ENTITY_TABLES["prompt"] = "prompts"`, the `BASELINE_ENTITY_TYPES`
  row (`Prompt`, `PRT-`, Always), the write guard that refuses an unknown `plugin_skill` (the
  bundle's `skills/*/` folder names are the vocabulary, read from the plugin, self-contained).
- `references/artifact-catalog.md`: the family row, and the distinction between the project's own
  package README (a `readme` narrative document) and the stock operator guide file.
- `references/governance.md`: the id row; the retired-prefix note stays.
- `docs/guide/render.py`: `PRT` in the id-token regex. `docs/guide/content.py`: `type.prompt`,
  `table.prompts`, `col.prompts.*` EN + AR. `index.html` rebuilt.
- Tests: `test_store_migrations::test_migration_008_prompts_lands`; `test_db_roundtrip` prompt rows
  round-trip; `test_mcp_contract`: the kind CHECK, the `plugin_skill` refusal, the `phase_id` FK,
  `schema_version == 8`; `test_user_guide` table count 41 -> 42.

## What landed, beyond the plan

- **The family's class is `Conditional` in this beat, `Always` from plan 195.** The lab-tracker eval
  pins `G-SET=pass` on the fixture, and `g_set_failures` names every Always type with neither a row
  nor an omission. The fixture gains its kickoff row when `package_migrate` converts its prompt file
  (plan 195). The ruling (P1: Always) stands and lands there. Disclosed here, in the batch record and
  in the plans index row for 195.
- **The DDL lives in `008_prompts.sql` only.** Lint 2 forbids new DDL in `schema.sql` (the 001
  byte-twin). The plan said both. The migration carries the table and its two index triggers.
- **A v2 `prompts.csv` leftover is still recognised.** The name is live again, so the exporter now
  matches a stale CSV against the live header and the retired v2 header (`_RETIRED_CSV_HEADERS`).
  Before this beat the retired entry would have been shadowed by the live one.
- **The test that asserted the table gone** (`test_prompts_table_gone`, plan 027) is now
  `test_prompts_table_is_back_as_rows_in_v6`: the table exists with `plugin_skill`, the v2 column
  `prompt_kind` does not, and a `PRM-` id never names a row.
- Re-aimed in the same commit: `migrations_head` 007 -> 008 and `schema_version` 7 -> 8 in the
  contract suite and the hook suite; the v3 converter test expects the v6 `prompt` registry row
  (`PRT-`) after the scrub of the v2 one; `naming-conventions.template.md` gained the `PRT-NNN`
  row (lint 11); the CHANGELOG `[Unreleased]` names migration 008 (lint 7).
- My own catalog row failed lint 14 on first write (three semicolons, a 31-word sentence) and was
  rewritten under the rules.
- **Counts met while rebuilding the guide, fixed under R38:** `section.hero.store` 41 -> 42 tables,
  `section.families.1` 36 -> 37 families and 41 -> 42 tables, `section.families.triggers.1` 72 -> 74
  index triggers (EN + AR). The docs and README counts wait for plan 197, which rewrites them anyway.
- **`plugin_skill` admits the 17 scenario skills only** (`disable-model-invocation: true` in the
  frontmatter), not the front door or a discipline skill: a prompt row is the project half of an
  operator-invoked ceremony. The refusal names the legal set. Put to the operator at the review.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged, the three disclosures (Conditional until 195, the DDL in the
  migration only, the v2 CSV header) accepted.
- **P14:** `plugin_skill` admits the 17 bundled scenario skills only (`disable-model-invocation:
  true`), never the front door or a discipline skill.

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals) on the staged tree.
- `python docs/guide/build.py`: 1385 content ids, 0 strings missing; `index.html` rebuilt.
- `python tests/test_store_migrations.py` 11 OK (incl. `test_migration_008_prompts_lands`);
  `test_mcp_contract` 201 OK (incl. `test_prompt_rows_are_a_family_bound_to_a_bundled_skill`);
  `test_user_guide` 10 OK (42 tables); `test_migrate_v3to4` 17 OK; `test_resume_hook` 16 OK.
- Lint 14: 94 files, 152,539 words, 0 hard.
- Python 3.10: no 3.10 interpreter is installed here, so the touched files were parsed under the
  3.10 grammar (`ast.parse(feature_version=(3, 10))`); the CI matrix (3.10-3.13) is the real check.
- `test_db_roundtrip` seeds a prompt row, so the canonical byte round-trip covers `prompts.jsonl`.
