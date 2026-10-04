# Plan 193: the engine paths over prompt rows (the emit precondition, the screens, the scans, note v7)

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings P2, P3, P8, P14. Ledger first.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (the emit's refusal path changes; 25 contract tests name prompt files) - **DONE 2026-10-04**

## What this beat changes

- `handoff_emit`: the per-file loop goes. The emit refuses unless `packages.entry_point` names an
  Approved `kickoff` prompt row (plain English, naming the row and the operator's word). G-INJECT
  screens Approved prompt rows (title + body) and blocks the emit as a lesson's finding does.
  `oversized_prompts`, `converted_prompts`, the stale-line scan and the restated-content scan read
  `prompts.body`. `_STALE_PATTERNS` L3462's suggestion inverts and a new pattern names
  `<package>/prompts/` paths in the target's files. The note gains a prompt roster by skill, the
  "project-authored prompts live in" sentence is rewritten, the marker becomes `v7`.
- `_scan_prompt_ids` reads `prompts.body` (`prompt-ids-resolve`, population `{table: "prompts"}`);
  `_PLAIN_PROSE_COLUMNS["prompts"] = ("title", "body")`; the file branch of `_scan_prose_plain` goes.
- `entity_query(plugin_skill=...)`: an additive exact-match filter, refused for other types; the
  note roster uses the same SQL.
- `resume_hook.py` keeps parsing the first sentence unchanged; `tests/test_resume_hook.py` gains a v7
  fixture; lint 9's blacklist gains `tamheed:note v6`; `references/handoff.md` names v7.
- Tests: the refusal matrix (no kickoff row / Proposed / `entry_point` elsewhere / passes), the
  injection-shaped row blocks, `prompt-ids-resolve` over rows and `indeterminate` at zero rows, the
  `plugin_skill=` query, the roster line and `v7`; `_emit_ready` writes the kickoff row instead of a
  file; the nine contract tests the plan assigns to this beat re-aimed.

## What landed, beyond the plan

- **`prose-ids-resolve` no longer reads the prompt rows.** The generic scan iterates every
  `ENTITY_TABLES` table, so the new family was already inside it after plan 192 and
  `prompt-ids-resolve` over `prompts.body` would have reported every phantom twice (the advisor's
  catch). `prompts` joined `_PROSE_ID_EXEMPT_TABLES`; the prompt rule owns the rows, with its own
  population (`{table: prompts, rows: n, unit: rows}`) and its own zero case. The test asserts the
  generic rule never names a `PRT-` row.
- **The converted-prompt hint reads every live row,** not only the Approved ones: a Proposed row
  converted by the migration is what the review STOP looks at. Provenance is `converted_from` in
  `custom_attributes`; the hint clears when the operator removes it (a retitle keeps it).
- **The v2 `handoff/prm-*.md` leftover compare runs against the rows** (title + body composed as
  the v3 converter composed a file, or the body alone). The old code read the prompts folder and
  raised `NameError` once the folder loop was gone; two tests caught it.
- **Relative-link checking inside prompts is gone:** a row has no file base. The stale-line scan
  (v1-protocol instructions) and the restated-content detectors run over `PRT-NNN.body`.
- **The screens run over Approved rows only** (what the executing agent reads); a Proposed row with
  instruction-shaped text does not block the emit. Tested both ways.
- **The stock README still lives at `prompts/README.md`** in this beat and the note still names it
  there; plan 194 moves it and rewrites that sentence (a second v7 text before the stamp, the field
  sees only the final one).
- The `_STALE_PATTERNS` suggestion for `docs/handoff/` now points at the rows; the pattern that
  names `<package>/prompts/` paths in the target's files waits for 194 (the path is still true).
- Lint 14 caught five of my own new server strings (two semicolons, three long sentences) and one
  guide sentence; all rewritten before the gate.
- `plugin_skill=` on `entity_query` is exact-match and refused for other families; the note roster
  does not query by it (it lists every Approved row with its binding), so the two cannot disagree.
- **Where a client learns `plugin_skill`:** the registered description (`_ENTITY_QUERY_DESC`, what a
  client receives, O13) names no filter at all, only the ordering, `limit`, `after_id` and `total`,
  so it does not change; the parameter reaches the client through the tool schema and its rule
  through the refusal text ("prompt rows only").
- **The stale-warning block** the emit writes into the field's `CLAUDE.md` named "prompt files" as
  part of the scan's scope (plan 130 exists because that block once named a stale scope); it says
  "prompt rows" now, and the pin in the contract suite moved with it.
- **A posture choice the plan did not state:** the injection screen runs over Approved prompt rows
  only. A Proposed row with instruction-shaped text does not block the emit, because the executing
  agent reads Approved rows (the lessons screen works the same way). Put to the operator at the
  review.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged, the disclosures accepted (the generic scan hands the prompt
  rows to their own rule, no relative-link check inside rows, the converted hint on every live row,
  the stock README path until 194).
- **P15:** the injection screen at emit time runs over Approved prompt rows only, as the lessons
  screen does. A Proposed row blocks nothing: the executing agent reads Approved rows.

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals).
- `tests/test_mcp_contract.py` 201 OK: the `plugin_skill=` query (one row, exact match, refused for
  another family), the refusal matrix (empty `entry_point`, names no row, not
  a kickoff, Draft not Approved, then passes), the Approved-only injection screen, stale lines and
  the restated tally over `PRT-NNN.body`, the oversized row, the converted hint's three states,
  the leftover verdicts against rows, `prompt-ids-resolve` over rows with the Obsolete row skipped
  and the generic rule silent on `PRT-`, the note needles (v7, the Prompts roster, v6 gone).
- `tests/test_resume_hook.py` 17 OK: the v7 fixture and the v6-still-resumes case.
- `tests/test_user_guide.py` 10 OK; `index.html` rebuilt (1,386 ids, 0 missing).
- Lint 14: 94 files, 152,822 words, 0 hard. Lint 9 blacklists `tamheed:note v6`.
- Python 3.10 grammar parse of the five touched `.py` files (no 3.10 interpreter here; CI's matrix
  is the real check).
