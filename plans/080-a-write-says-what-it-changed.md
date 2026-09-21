# Plan 080: A write says what it changed

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: MEDIUM (it reads inside the write path)
- **Category**: write legibility (the field's silent-loss lessons) - **Planned at**: commit `f82310a`

## Why this matters

ACMP's sharpest recorded pain (`prm-next.md` trap 14a, LL-045, LL-063): upserts replace whole
rows, so appending one dated block to a defect title meant re-sending all 4,296 characters - and
a re-send that "silently dropped a complete paragraph 3,208 characters in" returned
`ok: true, applied: 1`. "Nothing in the result could have revealed it." Their compensating
apparatus - pre-images, exact-equality assertions, `expect_unchanged` on every guarded column -
exists only for this. `expect_unchanged` cannot help with the column being edited on purpose.

findings_26 adds the converse: their `DEC-208 -> DEC-209` repair became safe only because the
edit was length-preserving, "so byte-length equality per column is a complete check on the paste".

## What changed

For an UPDATE through the `ON CONFLICT` path, the per-item result carries
`changed_columns: [{"column": c, "old_len": n, "new_len": m}, ...]` - computed from the stored
row read just before the write, compared with the existing `_same_value` (JSON columns as parsed
values). Lengths are given when both sides are text or NULL. An INSERT carries no list; an
identical re-send carries `[]`. Trace edges and the append-only journal are untouched.

**Shrunk by the devil's-advocate review:** the batch plan first proposed `if_match` and row
hashes. The store has a single-writer lock, so no concurrent writer exists to be stale against;
the field's problem was content loss within one writer, which a length delta shows directly.

## Review

One reviewer brief covered correctness AND security for this plan (a deviation from the batch
plan's "security + Python", made to conserve a saturated session; recorded, not hidden).
**Result: no CRITICAL, no HIGH.** Confirmed: `table` comes from the fixed registry and `names`
reach the new SELECT only after the unknown-column guard, so every interpolated identifier is
schema-validated; the pre-image read runs only in the `ON CONFLICT` branch (never for trace
edges or the append-only journal); `key` is only read in the branch that just set it; the read
sits inside the batch savepoint and cannot disagree with `expect_unchanged`; no new exposure (a
caller who can write the row can already read it); one indexed SELECT per item is negligible.
**One MEDIUM, documented rather than changed:** JSON columns compare as PARSED values, as
`expect_unchanged` already does, so a blob re-sent with different key order reports as
unchanged although its stored text is rewritten canonically. A change of meaning is what the
list reports; the docstring now says so.

## Tests

`test_a_write_says_what_it_changed`: an insert reports nothing; a status flip reports one column
with its lengths; a truncated re-send of a long title reports the length drop; an identical
re-send reports `[]`; a JSON column is named when it changes. RED (`KeyError`) before, GREEN after.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (160)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] reviewer findings addressed; CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
