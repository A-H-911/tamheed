# Plan 188: wave 4b - the guide's prose (EN and AR) and the "Writing discipline" section

> Maintainer-executed, 2026-10-04. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R16 (wave 4), R22 (the guide section, the vocabulary table rendered FROM the file),
> R25 (AR mirrored; AR gets the semicolon and length rules), R26 (`_STE_PENDING` empties here),
> R42 (blockquotes follow the rules too). Wave protocol as plans 184-187.

## Status
- **Priority**: P1 - **Effort**: XL - **Risk**: MEDIUM (the byte-twin, the AR rewrite is real writing, `content.py` enters lint 14 by import) - **DONE 2026-10-04** (the commit this ledger lands in, after the operator's review)

## Scope

1. `docs/guide/content.py`: every EN entry under flavored/en, every AR entry under flavored/ar
   (semicolon and length). Linted by import of `content.TEXT`, finding label `content.py:<id>.<lang>`,
   never through the Python-literal extractor (the file is prose, not code).
2. Lint 14: `content.py` rostered by import; `_STE_PENDING = ()`; tests `test_ste_pending_is_empty`,
   `test_ste_roster_covers_the_scope`, and a probe that a `؛` in an AR entry is caught by its id.
3. The "Writing discipline" section (`writing`, after `practices`): three paragraphs, the actions
   table and the terms table rendered from `references/vocabulary.md` through `extract.vocabulary()`
   (the linter's own table parser), the EN meaning asserted equal to the file as `build.py` does for
   `stagetitle.*`, the AR meaning from `vocab.term.<slug>`. `MUST_RENDER` gains `vocab.`. No diagram.
4. `index.html` rebuilt (byte-twin). `git add --renormalize index.html` on this CRLF checkout.

## Baseline (before the rewrite, the planned lint path over `content.TEXT`)

| | Entries | Words | Hard | Of which |
|---|---|---|---|---|
| EN (flavored/en) | 1,284 | 20,054 | 788 in 577 entries | 612 semicolon, 176 long-sentence |
| AR (flavored/ar) | 1,284 | 17,359 | 707 in 547 entries | 610 semicolon (`؛`), 97 long-sentence |
| **Total** | | **37,413** | **1,495** | |

Advisory on EN: passive-voice 227, present-perfect 2, vocabulary 39 (flavored: advisory).

## Method

A mechanical first pass through the AST (`scratchpad/content_tool.py mech`): outside code spans and
parentheses, `; ` becomes `. ` with the next clause capitalised, and `; and|but|or|so|then` becomes
`, and|...`; in AR every `؛` outside code spans and parentheses becomes `.`. Then a hand pass by id
(`content_tool.py apply <spec>`) for every leftover semicolon and every long sentence, EN first, AR
mirrored. Every entry is written back as one JSON-style literal at the AST node's own span, so the
`# src:` comments and the file's order stay.

## Pin ledger

`evidence/scripts-ste/pins-188.md` before (14 phrases), `pins_missing.py` after.

## After the rewrite

| | Entries | Words | Hard |
|---|---|---|---|
| EN (flavored/en) | 1,376 (92 new) | 20,930 | 0 (advisory: passive-voice 237, present-perfect 2, vocabulary 41) |
| AR (flavored/ar) | 1,376 | 17,993 | 0 |

Changed entries: 1,125 (577 EN, 548 AR). The mechanical pass changed 1,003 entries, the hand pass 154
(149 + 5), most of them already touched by the mechanical pass, so the two counts overlap.
Gate line: `lint: plain English (93 files, 150617 words) 0 hard, advisory passive-voice=1126
present-perfect=68 vocabulary=88, allow markers=2, pending 0 surfaces`. `_STE_PENDING = ()`.

## The mechanical pass, reviewed

- Lowercase after a full stop in EN after the pass: one, `review.html` as a sentence start (a file name).
- Sentences that now open with And / Or / So / Then: 25, every one written by the hand pass as the
  second half of a split, none by the mechanical pass.
- `; and|but|or|so|then` → `, and|...`: 154 joins. Each is the compound sentence the semicolon already
  was, now with a comma. Those over 25 words were split by hand afterwards.
- A random sample of 14 mechanically changed EN entries read against HEAD (`scratchpad/compare_188.py`,
  seed 188): every split falls between two independent clauses, no meaning moved. The 548 Arabic
  changes were not sampled as Arabic (R25: AR is mirrored, and the lint checks its `؛` and length).
- 85 column cells now end in a one-word writer sentence ("Label. Caller.", 54 of them exactly
  `Caller`), the former "meaning; who writes it" form split. The column header reads
  "Meaning · who writes it · when", so the fragment matches the header. Put to the operator.

## Invariants (`wave_invariants.py HEAD`)

| File | Difference | Verdict |
|---|---|---|
| docs/guide/content.py | `24` gone, `26` new | R38: 27 skills = 1 front + 26 companions (both languages) |
| docs/guide/content.py | new: `188`, `5.9.0`, `/tamheed:ste-rewrite`, `glossary-term`, `prose-plain-english`, `references/`, `references/vocabulary.md`, `tamheed:plain-english`, `workflow.md` | the new Writing discipline section |
| check.py, build.py, extract.py, render.py, the two tests | `188`, `TEXT`, `content.py:<id>.<lang>`, `FROM`, `25` | the wiring of this plan |

No modal count fell in any file.

## Count corrections (R38)

- `section.what.is.1` (EN and AR): "24 companion skills" → 26 (27 skills since plan 183: one front
  door, 17 scenario, 9 discipline).

## Kept as-is

- Every hedge and every modal. Every `# src:` comment and the file's order (the AST tool writes each
  entry back at its own span).
- `workflow.migrate.s1`: "repaired provenance" → "corrected provenance" (the vocabulary's verb for a
  wrong record). The migrate tool's own result keys are untouched.
- The slogan `section.what.principle` reads "The skill owns the capability. Every entry point is a
  thin wrapper." in both languages (the Arabic keeps its comma).
- `tool.*` ids are the guide's own prose; the registered descriptions the page quotes verbatim are
  wave 1's and unchanged.

## The Writing discipline section

`extract.vocabulary()` parses the three tables through `ste_lint._tables` after `load_vocabulary`
has accepted the headers. `render._writing` sits after Best practices: three paragraphs, the actions
table (action · approved verb · rejected synonyms), the terms table (term · one meaning · never means),
the names table (name · where it is a name). Every English cell on the page IS the file's cell:
`build.py` asserts `content.TEXT[id]["en"]` equals the file for all 77 cells, as it does for
`stagetitle.*`. The Arabic twins are new (`vocab.action.*`, `vocab.term.*`, `vocab.never.*`,
`vocab.name.*`). `MUST_RENDER` gains `vocab.`. No diagram.

## Pins

`pins-188.md`: 14 phrases. `pins_missing.py` after: 0 missing.

## Validation (run)
- `python check.py` ALL CHECKS PASSED on the staged tree. `wave_invariants.py HEAD` (table above).
  `pins_missing.py` 0 missing. `build.py` wrote 946,270 bytes, 1,376 ids, 0 missing. The page carries
  one `id="writing"` section and one TOC link to it.
- New tests: `test_ste_pending_is_empty`, `test_ste_roster_covers_the_scope`, two probes that a `؛` in an
  AR entry and a 26-word EN sentence are caught by `docs/guide/content.py:<id>.<lang>`, and
  `test_vocabulary_table_comes_from_the_file`.

## Validation
- Red: the roster move (1,495 hard findings) and `build.py --missing` on the new ids.
- Green: `python check.py`; `wave_invariants.py HEAD`; `pins_missing.py`; `build.py --check`;
  `test_user_guide.py` (byte-twin, coverage, the vocabulary table equals the file).

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- R43: the 85 one-word writer cells stay; the column header carries the sense.
- R44: the three tables and the 77 Arabic cells stay (R22 widened).
