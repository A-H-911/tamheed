# Plan 184: wave 1 - tool descriptions, server messages, the note as v6, the hook

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R9, R16 (wave 1), R17, R26. Wave protocol: stage, advisor read, operator review, one
> commit after the ruling; a later change is a disclosed fix-up commit under this plan number.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (the note's parsed sentence; pinned phrases) - **STAGED, awaiting the operator's review** (2026-10-03)

## Scope (the roster moves these globs from pending to rostered, strict, English)

`plugins/tamheed/server/*.py` (the linter itself stays exempt), `plugins/tamheed/db/*.py`,
`plugins/tamheed/scripts/*.py`, `check.py`, `evals/*.py`, `docs/guide/*.py` except `content.py`
(wave 4b). Runtime string literals only: the 19 tool descriptions and their three constants, every
`_err(...)`, every `rule(...)` note, every warning, the note block, the hook's own strings, the
viewer's labels, the store's lock text, the migration and adopt messages.

## The note (R9)

`<!-- tamheed:note v5 -->` becomes `v6`. The first sentence becomes "The Tamheed package for this
project is `X` (under `path`)." `resume_hook.py` accepts both the old sentence ("executes Tamheed
package `X`") and the new one. Lint 9's blacklist gains `tamheed:note v5`; `references/handoff.md`
line 131 says `v6`.

## Pin ledger (grep-derived before the rewrite; re-aimed in this commit)

`evidence/scripts-ste/pins-184.md` (106 phrases of four words or more that occurred in the wave's
files before the rewrite) and `pins_missing.py` after it: 8 of them no longer occur, every one
re-aimed in `tests/test_mcp_contract.py` in this commit. The viewer's `review.html` strings and the
hook's strings pinned by `test_export_html.py`, `test_resume_hook.py` and the evals are unchanged.

| pinned phrase (before) | now | where re-aimed |
|---|---|---|
| `<!-- tamheed:note v5 -->` | `<!-- tamheed:note v6 -->` | three asserts, plus `tamheed:note v5` in the gone-list |
| `this table stays here because it is mandatory` | `This table stays here because it is mandatory` | the note needles |
| `pinned rows always render` | `Pinned rows always render` | two asserts |
| `the root file was left untouched` | `The root file was left untouched` | the pointer-import warning |
| `the stale-warning block was removed there` | `The stale-warning block was removed there` | the pointer-import warning |
| `a 5.1-era stale-warning block was removed from the root file` | `A 5.1-era ...` | the pointer-import warning |
| `delete it and re-emit` | `remove it and re-emit` | the customised-stock warning |
| `if a customization predates` | `A customization that predates` | the customised-stock warning |
| `is current there; nothing written` (two) | `is current there. Nothing written` | the pointer-import warning |
| `is current there; the stale-warning block was added there` | `... there. The stale-warning block ...` | the pointer-import warning |
| `deleted (refresh_stock)` | `removed (refresh_stock)` | the retired-leftovers warning |
| `nothing to migrate` (two) | `Nothing to migrate` | two migrate refusals |
| `never Met without proof` (two) | `Never Met without proof` | the tool-owned span test edits that cell |
| `gitignore; if data/ is git-tracked` | `gitignore). If data/ is git-tracked` | the relocate action prefix |
| `safe to delete` | `safe to remove` | the leftover verdict |
| `stock last changed: README.md` | `Stock last changed: README.md` | a three-word pin below the ledger's floor; the floor is now three words |

The last two rows were found by the suite, not by the ledger: one was a three-word phrase (the floor
moved from four to three for the next waves), one was a phrase the ledger listed but the first
re-aim pass missed. `pins_missing.py` is the check that closes the loop.

## Invariants (run before the diff is shown)

`plans/evidence/scripts-ste/wave_invariants.py`: per touched file, the set of backticked tokens,
numbers, `G-`/`FB-`/`WVR-`/`/tamheed:` tokens and ALLCAPS words before and after must be identical
(a deliberate difference is written here with its reason). The count of modal and limiting words
(may, might, could, can, must, never, only, always, until, unless) per file must not fall.

## Kept as-is

Every hedge stays. The modal-word counter per file is unchanged except one: `never` 165 -> 164 in
`tamheed_server.py`, because "never `data/*.jsonl` and never a pasted display" became "It never reads
`data/*.jsonl` or a pasted display" (one `never` governs both, the claim is unchanged). Two compound
tenses stay, both advisory: "a Pending placeholder nobody has graded" (the placeholder is ungraded
NOW, which the simple past would not say) and "has unmapped" in the converted-prompt report (the
same reason).

## What the wave measured

| | before | after |
|---|---|---|
| hard findings on the wave's files (strict) | 207 (130 semicolons, 60 long sentences, 17 vocabulary) in 111 literals | 0 |
| rostered files / words | 1 / 709 | 16 / 9,046 |
| advisory findings | - | passive 73, present perfect 2 |
| pending surfaces | 90 | 77 |
| token-set invariant | - | identical on every touched file (the test files gained the tokens of their own new tests) |
| selftest | - | 19/19 descriptions as listed by the SDK, longest 387 characters |
| hook | the v5 fixture | a v5 and a v6 fixture both print the resume block |

## Errors owned

- The linter read a multi-line Python literal as one flat block, so the note's table rows counted
  as one long sentence each. The literal extractor now hands a multi-line literal to the Markdown
  extractor (a test holds a table inside a literal). The same pass stopped counting layout tokens
  (`|`, `->`) toward "digit-heavy", which brought six f-strings into the lint that the first run
  had skipped as code. All six were prose and were rewritten.
- A shell heredoc turned a `\b` into a literal backspace inside check.py's marker regex, and the
  marker count read 0 with a marker present. The line was rewritten through a file, never the shell.
  Every later script of this batch is written through a file.
- The first draft of the hook test's new fixture and the rewrite of the "when" cell went over the
  cap and were split again. The lint found both.
- The census grep for `tamheed:note v5` covered the bundle and `docs/architecture.md` and missed the
  guide: `content.py` (four ids, EN and AR), `render.py` (the tree diagram) and the architecture
  diagram all said v5. Swept in this commit, so the engine and the public guide move together.
- Three sentences of my own needed the advisor's read: the CHANGELOG said `refresh_stock` rebuilds
  the note (any emit does), "nothing was removed" sat beside "the .tmp files are gone", and "PEP 723
  installs the pin" named the wrong actor (uv installs the pinned SDK). All three corrected.

## Validation
- Red: the roster move (lint 14 red on 207 hard findings until rewritten); the hook test over a v5
  fixture against the v6 regex; ten contract tests on their pinned phrases.
- Green: `python check.py` ALL CHECKS PASSED (12 suites, 14 lints); `uv run ... --selftest` 19/19;
  every changed `.py` parses under the 3.10 grammar; `wave_invariants.py` as recorded above;
  `pins_missing.py` names only the eight phrases re-aimed here.
- `test_tool_descriptions_are_plain_english` was not written as a separate test: the roster now
  reads every `TOOLS` description through lint 14 at every commit, which is the stronger check.
