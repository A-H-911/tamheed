# Plan 195: `package_migrate` converts prompt files to rows

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Ruling P4; the sequencing change of the plan-194 review (the fixture and the sample migrate in
> plan 198, after the stamp). Ledger first.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (a staged write over a field package's files; abort-on-anomaly) - **DONE 2026-10-04**

## What this beat changes

- `package_migrate` on a v4 store proceeds for a third reason: project prompt files under
  `prompts/` (any `.md` that is not a stock body). The preview lists each file with its proposed
  `PRT-` id, kind (the file `entry_point` names is the kickoff; then a filename containing
  `kickoff` or a front-matter `kind:`; else `situational`), title (the first H1 or the filename),
  the `entry_point` rewrite, the README action (stale -> removed, customised -> moved and named),
  the backup folder `prompts-v5-backup/`, and the G-SET consequence when nothing converts. Confirm
  writes Proposed rows with `custom_attributes.converted_from`, moves the files, handles the README,
  removes the folder, rewrites `entry_point`. Any anomaly (an unreadable file, an id collision, a
  folder already present) aborts with the package untouched. The registry-sync note stops saying
  "no data transform, no backup taken" when files convert.
- A v2 store still passes through `data/prompts.jsonl` -> files -> rows in one confirm; the
  preview's `legacy_note` says so.
- Tests: a three-file package converts (rows, backup, no folder, `entry_point`); the preview writes
  nothing; a collision aborts; a customised README moves and a stale one goes; zero files leaves
  the registry sync alone and names G-SET; the v2 chain ends in rows; the ACMP replay copy
  (`git archive HEAD tamheed-package`) migrates in a scratch root and the result is read back.
- Not in this beat: the lab fixture and the generated sample (plan 198, after the stamp), the
  family's class (Conditional until 198).

## What landed, beyond the plan

- **The plan is computed once, before anything is written, and the rows join the tables before
  the scratch validation.** A row the store would refuse aborts the whole migration with nothing
  on disk; the file moves run only after the store swap succeeded, and a failure there is
  reported with the rows already written (a re-run converts nothing twice: a file a row already
  names in `converted_from` is only moved).
- **What a converted row keeps.** The body loses the front-matter block, the v3 provenance header
  and the title line; each lands in `custom_attributes` (`front_matter`, `v2_id` / `v2_kind`,
  `converted_from`, `kind`), so nothing a file carried is lost. The second H1 of a file stays in
  the body (the v3 converter's rule).
- **Kind inference, in order:** the file `entry_point` names, a filename containing `kickoff`, a
  front-matter `kind:` in the vocabulary, else `situational`. ACMP's `prm-next.md` lands as the
  kickoff by the first rule.
- **A stock body anywhere under `prompts/` is removed** (the pre-v6 guide, a 4.x scenario), never
  moved: it is the maintainer's prose and the history carries it. A customised README moves and is
  named, never converted. A folder holding files that are not `.md` is kept and said so.
- **The G-SET line of the report** appears only when the family is Always and no row exists or
  converts. The family is Conditional until plan 198, and every test here converts rows, so the
  only case that produces the line is untested until 198 (recorded there as owed).
- **The recovery path is reachable** (the advisor's catch): the backup-folder refusal applies
  only when a NEW row would be written; a re-run after a failed move (rows written, files still on
  disk, the folder present) merges into the folder, moves the file and writes no second row.
  Tested. **A dead `entry_point`** (a `prompts/` path that converted as nothing) is cleared and
  said in the report, as P4 reads. **The zero-rows report** says what happened (stock removed, or
  files moved) and names the backup folder only when a move created it.
- **The field replay** (`plans/evidence/scripts-ste/acmp_migrate_replay195.py`, output in
  `.out.txt`): ACMP's five files became four Proposed rows (`prm-next.md` the kickoff, 3,651
  bytes; three situational halves), the stock README was byte-equal and removed, the folder went,
  `entry_point` reads `PRT-001`, G-SET and G-IDS pass, and the emit refuses until the operator
  approves the kickoff: the brief's STOP, measured.
- Lint 14 caught three of my new strings (two semicolons, one long sentence); rewritten.
- **A posture for the review:** a shipped stock body under `prompts/` (the pre-v6 guide, a 4.x
  scenario) is removed on confirm, never moved to the backup, because the bundled history
  reproduces it. The emit removes stale stock only on an explicit `refresh_stock`; the migrate's
  confirm is the operator's explicit word too.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **P16:** on confirm the migration removes a shipped stock body found under `prompts/` (the
  pre-v6 guide, a 4.x scenario), never moves it: the bundled history reproduces every shipped
  body, and the confirm is the operator's explicit word. The backup folder holds the project's own
  files only.

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals).
- `tests/test_mcp_contract.py` OK: the three-file conversion (preview writes nothing; kinds by
  entry point, front matter and default; the stock guide removed; the backup folder; the folder
  gone; `entry_point` follows the kickoff; the emit refuses on the Proposed kickoff; a re-run has
  nothing to migrate), the customised guide moved and named, the backup-folder refusal, a package
  without a folder, and the v2 chain ending in rows with the v2 provenance kept.
- `tests/test_migrate_v3to4.py` 17 OK: `data/prompts.jsonl` is the v6 table after the v3 chain.
- The field replay on a `git archive HEAD tamheed-package` copy: four rows, folder removed,
  `entry_point PRT-001`, G-SET pass, emit refused pending approval (output committed as evidence).
- Lint 14: 0 hard. Python 3.10 grammar parse of the four touched `.py` files.
