# Plan 092: `search` with `context` is a census

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P2 - **Effort**: XS - **Risk**: LOW (a read; additive result key) - **Planned at**: `740de71`

## Why this matters (ACMP's `FB-003`)

`entity_query(search=…)` located rows and, since 4.9.0, `matched` named the columns that hit. It
said neither how many times a token occurs nor in what words. Two field rounds needed exactly that
- the `DEC-208` repair had to establish six occurrences across five row-columns, and classifying
`7/7` meant reading 63 hits - and both built scratch probes over `exports/` to get it.

## What changed

`entity_query(…, context=N)`: when `search` matched, the result carries `occurrences:
{id: {column: {"count": n, "snippets": [...]}}}`. Counts are exact on the RAW needle (never the
`%`/`_`-escaped `LIKE` needle) with ASCII-only case folding (`re.IGNORECASE | re.ASCII`), which is
what SQLite's `LIKE` does; snippets are N characters either side, capped at 5 per column and 50 per
response (`_SNIPPETS_PER_COLUMN`, `_SNIPPET_BUDGET`) - counts are never capped. `custom_attributes`
is counted on its stored JSON text. Absent without `context`; `matched` and `rows` unchanged. No new
tool; FastMCP derives the schema from the signature (self-test 19/19).

## Tests

`test_search_with_context_counts_and_shows_every_occurrence`: three case-varied hits in one column
count 3 with the first snippet exact; a JSON-text hit counted; no key for a column without a hit;
`100%` (a `LIKE` special) counted 1; forty hits count 40 with five snippets; no rows -> no key.
RED (`unexpected keyword argument 'context'`) before, GREEN after. One assumption of mine caught by
the test: `matched` lists columns in TABLE order, existing behavior, left alone.

## Done criteria

- [x] contract suite OK; self-test 19/19
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
