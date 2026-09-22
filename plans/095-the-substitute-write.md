# Plan 095: The `substitute` write — one token, one column, every guard

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM-HIGH (the first departure from whole-row
  replacement; security + Python reviewers) - **Planned at**: `8567632`

## Why this matters (ACMP's `FB-004`)

`entity_upsert` replaces whole rows, so correcting one token in one column forced the whole row
back through the agent's output: the `DEC-208 -> DEC-209` repair cost 24,117 characters across five
rows, and `DW-118` had deferred that repair in writing because the re-transmission's risk exceeded
the defect's harm. It became defensible only because the substitution happened to be
length-preserving. Recorded twice upstream as "not built - speculative"; the field ranked it second
and showed it changed a decision.

## Design (approved after two devil's-advocate rounds)

An item `{"type", "id", "substitute": {"<column>": ["<old>", "<new>"], ...}}` (plus optional
`operator_confirm`, `expect_unchanged`; nothing else - a mixed item is refused). The server
MATERIALIZES the stored row by a raw `SELECT` of every column (stored TEXT, so `custom_attributes`
round-trips byte-stable except the replace), applies an exact substring replace per named TEXT
column, and then sends the result down the ORDINARY full-row path: every guard (lesson drift and
immutability, feedback bound content, transition guards), `expect_unchanged`, `operator_confirm`
and `changed_columns` run unchanged. There is no second guard to have holes in - the lesson of
plan 087's reviews. The result gains `substituted: {column: count}`.

Refused by name: `id`; a non-TEXT or unknown column; zero occurrences (names the column); an empty
`old`; `old == new`; `custom_attributes` that no longer parses as JSON after the replace; the
journal families (`progress-entry`, `audit-verdict` - corrected by compensating rows, never
substituted); composite-key surfaces (`omission`, `trace-edge`, `package`); a row that does not
exist; a malformed `substitute` value.

## Reviews, and what they changed

**Security (one MEDIUM, closed):** `str.replace` has no token boundary, so `DEC-20 -> DEC-21` would
have rewritten `DEC-208` to `DEC-218` and `DEC-2000` to `DEC-2100`, honestly counted and silently
done. A match glued to a digit on either side, or followed by `.digit`, is now refused naming the
longer token - the `PREFIX-NNN` class this store is built on; prose replacements are untouched. The
reviewer traced every guard against a substitute (lesson status, `superseded_by`, `confirmed_by`,
feedback `kind`): each compares VALUES against a fresh re-read of the stored row, so a substitute
is judged exactly like a full row; `trg_lessons_immutable` blocks a same-status content rewrite
independently. **Python (approve; three LOW applied):** return annotation; em-dashes; the JSON
check requires an object or array; a weak `"id"` assertion pinned to `"rewrites id"`. Noted for
maintenance, not this plan: the Python drift guard on lessons fires only on a status CHANGE; the
SQL trigger covers same-status rewrites.

## Tests

`test_a_substitute_write_changes_one_token_and_nothing_else`: two occurrences in a 5,000-char title
-> `substituted: {"title": 2}`, one `changed_columns` entry, every other column byte-identical
(asserted column by column); a JSON-text substitution that still parses lands, one that breaks the
JSON is refused; each refusal by name; a missing row; a journal row; an omission; an Approved
lesson's statement refused by the immutability rule and left unchanged; a bound feedback row's
title refused without the word and accepted with it; a match inside `DEC-208` or `SL-1.2` refused naming it, the whole token accepted. RED (`unknown columns: ['substitute']`)
before, GREEN after; contract suite 170.

## Done criteria

- [x] contract suite OK (170); round-trip suite OK
- [x] security + Python reviewers: one MEDIUM (glued match) closed; three LOW applied; no CRITICAL/HIGH
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
- [x] the Future-options entry ("a patch/append mode … not built") marked superseded
