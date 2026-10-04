# Plan 194: the stock operator guide at `<package>/README.md`

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Ruling P5. Ledger first.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (the managed-emission machinery and twelve stock tests move with the path) - **DONE 2026-10-04**

## What this beat changes

- `_emit_prompt_library` emits the stock operator guide at the package root (`<package>/README.md`)
  for all four callers (`package_create`, `handoff_emit`, `package_migrate`, `package_adopt`). The
  leftover pass classifies a `prompts/README.md` still on disk: byte-equal to any shipped body
  (after the `{package}` substitution) is `leftover_stale_stock` and is removed on `refresh_stock`;
  a customised one is `leftover_customized`, named and left. The emit never removes the folder (the
  migration does, plan 195).
- The stock body: the sentences about "this folder" and the project's prompt files become the
  package root and the prompt rows; the "Which skill, when" table's last row names the prompt rows
  bound by `plugin_skill`; the body lands under `"6.0.0"` in `stock-history.json` (lint 9).
- The note's sentence names `<package>/README.md`. A new `_STALE_PATTERNS` entry names
  `prompts/README.md` and `prompts/<name>.md` paths in the target's agent-control files, so the
  emit names a field's own pointers at the old location.
- `evals/pkg_check.py ste-clean` reads the stock file at the root.
- The guide's prose that names the path (`tool.package_create`, `tool.handoff_emit`, the package
  tree, `dia.package.*`, `glossary.stock.def`, `section.package.*`) follows; `index.html` rebuilt.
- Tests: `package_create` writes `<package>/README.md` and no `prompts/`; a stale `prompts/README.md`
  is classified and removed on refresh; a customised one is left and named; the twelve stock tests
  the plan assigns to this beat re-aimed to the new path; the note needle moves.

## What landed, beyond the plan

- **The stock-merged check labels a file by its location.** `_stock_merged_check` built every
  label as `prompts/<name>`; the root guide now passes its own label, so a declared marker on
  `<package>/README.md` is reported there and a leftover's under `prompts/`.
- **`ste-clean` reads the root first and falls back to `prompts/`.** The lab fixture is not
  migrated until plan 195, and a field package that skips the migrate keeps its guide under
  `prompts/`; both still lint. The eval that pins `ste-clean` on the fixture stays green this beat.
- **The new stale pattern** names `prompts/README.md` and any `prompts/<name>.md` path in the
  target's agent-control and skill files (the field's `AGENTS.md` names the old location); the
  scan stays report-only, as every stale pattern is.
- **The stock body is strict-lint clean and lands under `"6.0.0"`** in the history before the
  stamp (R41's precedent); plan 198 overwrites the key with the stamped body. The header still
  says v5.9.0 (lint 8 pins it to the plugin version until the stamp).
- **The guide's path mentions moved with the engine** (the package tree, D4's node, D1's package
  label, the package and target paragraphs, `col.packages.entry_point`, the two tool paragraphs,
  stage 20, the new-project recipe, the glossary), EN + AR. The broader wording waits for 197.
- The pre-v6 copy test and the stale-pattern test are new; eighteen `"prompts/README.md"` labels,
  six package paths, the note needle and the guide-title needle moved in the stock tests; the
  tests that plant 4.x leftovers create the folder themselves (a v6 package has none).
- Lint 14 caught one long sentence of mine in the recipe prose (EN + AR split).
- **The stale pattern is scoped to the package's own layout** (the advisor's catch): the static
  entry matches the `<package>/prompts/` placeholder only, and `_stale_patterns()` adds, per emit,
  `<this package's directory>/prompts/<file>.md`. A bare `prompts/<file>.md` is a project's own
  business (the precision doctrine the Keystone case set). The test carries a negative control.
- **`TOOLS["handoff_emit"][1]`** said "the stock prompts README"; it says "the stock README at the
  package root" (the O13 surface a client reads; the guide quotes it and was rebuilt).
- **`_stock_names()` is removed**: its only caller left with plan 193's file loop, and its
  docstring described a refusal that no longer exists.
- **A disclosure for the review and the brief:** the managed emit at the package root puts a
  package-root `README.md` inside `force`'s blast radius for the first time. An operator's own
  file at that path (none of the three packages has one today) reads as `diverged_customized` on
  a plain emit and is overwritten by `force=True`.
- Runtime strings that still say `prompts/`, classified: the leftover warnings ("remain in
  `<package>/prompts/`") are true; `package_migrate`'s v2 preview note ("will be converted to
  `prompts/*.md`") is plan 195's, where the chain becomes files-then-rows; the stage-20 comment
  at `package_create` is a code comment.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged; the two disclosures accepted (a package-root `README.md` of
  the operator's own is inside `force`'s blast radius, the brief says so; the fixture and the
  sample migrate in plan 198 after the stamp, never to an unreleased stock body).

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals).
- `tests/test_mcp_contract.py` OK: `package_create` writes `<package>/README.md` and no folder;
  the pre-v6 copy is `leftover_stale_stock` -> `retired` on refresh, a customised one is kept and
  named; the stale scan names `prompts/README.md` in `AGENTS.md`; the twelve stock tests hold at
  the new path; the note names `demo/README.md`.
- `python docs/guide/build.py`: 1,386 ids, 0 missing; `test_user_guide` OK (D4's node moved with
  the geometry lint green).
- Lint 9: the stock history carries the current body under `6.0.0`. Lint 14: 0 hard.
- Python 3.10 grammar parse of the six touched `.py` files (CI's matrix is the real check).
