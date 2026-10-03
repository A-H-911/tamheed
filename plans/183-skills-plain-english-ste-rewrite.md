# Plan 183: the skills `plain-english` and `ste-rewrite`, and every count surface

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R4, R5, R11; the approval item on the rewrite defaults.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: LOW - **DONE** (2026-10-03)

## What shipped

- `skills/plain-english/SKILL.md` (discipline, `user-invocable: false`): the two modes, eleven
  numbered rules with field evidence from the census, the `Kept as-is:` protocol, the linter
  command, the boundary with `written-claims`, `reading-the-record` and `package-writes`, the
  credit to the upstream project. Written in the discipline it teaches: the linter found eleven
  hard findings in the first draft (two over-long descriptions, four long sentences, rule 7's
  quoted bad examples read as live text) and none in the committed one.
- `skills/ste-rewrite/SKILL.md` (scenario, `disable-model-invocation: true`): the rule's entities
  are the scope, batches of ten, the consequence column, the defaults (an Approved AC with a Met
  verdict and an Approved lesson are skipped unless the operator opts in), the STOP, the writes
  (`expect_unchanged`, supersession, prompt files in place, `GT-` rows for a project's own word),
  the journal note, readiness before and after.
- The note's skills line names `tamheed:plain-english`. The stock README says nine discipline
  skills, lists the new one and maps the new situation to `/tamheed:ste-rewrite`; its body landed
  in the history under `5.9.0` (the file round-trips byte for byte through `json.dumps(indent=1,
  ensure_ascii=False)`).
- Counts moved together: `extract.py` 1/17/9, `test_user_guide.py` 27, `docs/architecture.md`
  (which said 7 discipline), `docs/install.md`, `README.md` (three places), `SECURITY.md`,
  `references/generated-structure.md`, `references/prompt-templates.md` (plus a table row),
  `references/extension.md`, the front door's reference table, the guide (`section.skills.1`,
  `skill.plain-english`, `skill.ste-rewrite`).
- Tests first: `test_user_guide` and `extract.skills()` red at 25 and 1/16/8;
  `test_note_names_every_discipline_skill` (every `user-invocable: false` skill is in the note);
  `test_ste_rewrite_skill_teaches_the_stop_and_supersession`.

## Validation
- `python check.py` ALL CHECKS PASSED: 27 skills under lint 12, stock history current (105 bodies),
  teaching surface clean, no dead paths; `index.html` rebuilt (1,284 ids). Both new skills are
  lint-clean under strict and enter the roster in wave 2.
