# Plan 179: the vocabulary, drafted from a census, settled in one interview round, frozen

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R8. Evidence: `evidence/scripts-ste/vocab_census.py` and its output `vocab_census.md`.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a word approved here is the word every wave uses) - **DONE** (2026-10-03, frozen)

## What this beat produces

`plugins/tamheed/references/vocabulary.md`: three tables with fixed headers that beat 180 parses.

| table | header | meaning |
|---|---|---|
| actions | `action`, `approved verb`, `rejected synonyms` | one verb per action in Tamheed prose; the rejected words are a hard `vocabulary` finding under strict, advisory under flavored |
| terms | `term`, `one meaning`, `never means` | Tamheed's terms of art with their single meaning |
| names | `name`, `where it is a name` | fixed identifiers that contain a rejected word; the linter skips an exact match |

## Method

1. The census script counts inflected uses of every word in the ten upstream groups and six
   Tamheed candidate groups, per surface, outside code spans, fenced code and blockquotes, and
   lists the engine identifiers that contain each word (name positions).
2. The maintainer drafts the tables from the counts and the engine's own usage.
3. One interview round puts the contested rows to the operator (`tamheed:operator-interview`:
   one decision per question). Their rulings go into the rows.
4. The file is committed and FROZEN for the batch. A later change is a new ruling in the batch
   record and re-opens the waves that used the word.

## Validation
- Lints 9, 10 and 13 green on the new reference (`python check.py lint`).
- The three headers present (grep).
- Beat 180's parser and its tests read this file; beat 181's lint 14 enforces it.

## The interview (one round, 2026-10-03)

| # | Question | The operator's answer |
|---|---|---|
| R30 | check / verify / confirm / validate (214 / 114 / 156 / 61 uses) | "Three approved verbs; reject validate in prose": check = a gate ran, verify = a verdict on evidence, confirm = the operator's word; the stage title and the product line stay as names |
| R31 | delete / remove / retire (57 / 92 / 131) | "retire = rows, remove = files/markers/lines, reject delete" |
| R32 | the low-count synonyms | all four rejections approved: repair (fix for code, correct for a record), get and fetch (read), produce (emit, generate or write), decline (refuse for the engine, reject for the operator) |
| R33 | display, journal, log, reference | "Keep all four as noun terms, never reject them"; verb uses are rewritten by hand in the waves |

Frozen from this commit. A change is a new ruling in the batch record and re-opens the waves
that used the word.
