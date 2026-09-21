# Plan 068: Reads announce what they hid; a lesson approval says what still has to happen

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (additive top-level result keys)
- **Category**: legibility (field lessons LL-077, LL-094; the field's DEF-107)
- **Planned at**: commit `3f53c0b`

## Why this matters

Three field incidents, one shape - the tool did the right thing and said nothing about it.
- **LL-077**: "A truncated row set announces itself - `entity_query` returns `total` beside
  every page. A projection announces nothing." A `columns` projection dropped the
  `custom_attributes` blob that held the answer, and an agent concluded no record could settle
  the question.
- **LL-094**: a search for `DEC-208` returned rows that showed only `DEC-209`, recorded as
  "search is FUZZY". **It is not** (verified in source: an escaped substring `LIKE` over every
  TEXT column, `custom_attributes` included). The match was in a column the caller had not
  projected; the result never said which.
- **DEF-107**: a lesson Approved, pinned and operator-attributed sat absent from the
  always-loaded note for two days, "found by accident". Only `handoff_emit` rebuilds the note,
  and nothing said so at the moment a lesson was made to bind.

## What changed

- `entity_query` with `columns` returns `omitted_columns`.
- `entity_query` with `search` returns `matched: {id: [columns]}` for the rows on the page, from
  the same `LIKE` the filter used. Skipped for an empty page.
- `entity_upsert`: a lesson landing `Approved` or `Promoted` carries a per-item `next` hint that
  the note is rebuilt only by `handoff_emit`. Other families and a `Proposed` lesson get none.

All are siblings of `rows` / fields of the per-item verdict. **Row dicts are unchanged** (asserted),
so a consumer iterating `result.rows` sees no difference.

**Not built, and why:** a readiness rule comparing the note with the pinned set. The server does
not store where the note was emitted, so it would need a schema change.

## Tests

`test_reads_announce_what_they_hid_and_where_they_matched` and
`test_lesson_approval_says_the_note_is_rebuilt_only_by_handoff_emit`. RED before, GREEN after.
Two first-run failures were wrong assumptions in the tests, not the code: trace edges are
write-only (`trace_query` reads them) and the per-item verdict list is `items`.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (150)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
