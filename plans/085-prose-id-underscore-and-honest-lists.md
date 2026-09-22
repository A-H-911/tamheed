# Plan 085: `_` is a word character; every cut list says so; the two ambers are told apart

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [085-090-batch-findings-27.md](085-090-batch-findings-27.md).

## Status

- **Priority**: P2 - **Effort**: XS - **Risk**: LOW (advisory text and one character in a pattern)
- **Category**: readiness honesty - **Planned at**: commit `831c27a`

## Why this matters (findings_27 §1-§3, each verified in source before this plan)

- §2: `_prose_id_pattern`'s lookbehind and lookahead lacked `_`, so `KPI-17_score` inside a formula
  yielded a hit on `KPI-17`. Every `not_well_formed` entry on the field's package (five) was that one
  false positive. And width is tested before the code-span test, so a narrow token inside a code span
  lands under `not_well_formed` - the lists were read as "prose" vs "code span", which they are not.
- §3: `in_code_spans` and `not_well_formed` were cut at 50 with no total; only the failing list said
  "showing 50 of N". A truncated informational list read as a complete one - the shape of findings_26
  §1's complaint, recurring inside its fix.
- §1: the zero-population flip needs `not scoped`; nothing in the note said `scoped` is the tell
  between plan 049's scoped zero and plan 077's whole-table zero.

## What changed

- `_prose_id_pattern`: `(?<![A-Za-z0-9_-])` and `(?![A-Za-z0-9_])`. Measured before commit: on ACMP's
  nine exported families the new pattern ignores exactly four tokens the old one saw, all
  underscore-joined labels (`from_LL-016_LL-020_LL-040`, `why_DEF-100_STAYS_OPEN`); none a citation.
  On the lab fixture, zero. A slip like `DEF-82` has no `_` and still lands in `not_well_formed`.
- The rule note states the order: the three lists are disjoint and width is tested first.
- The cut clause covers all three lists (`in_code_spans: showing 50 of 52`).
- The plan-077 `indeterminate` note ends `(scoped: false - the whole table is empty; a scoped zero reads
  indeterminate by plan 049 and carries scoped: true)`.

Not done: reordering the classification (findings_27 itself says three disjoint lists is right; only
the labels misled, and the note now carries them).

## Tests

`test_prose_id_scan_sees_an_underscore_and_says_when_a_list_is_cut`: `KPI-17_score`, `KPI-10_score`
and `plain_KPI-16` in no list; `KPI-8` still `not_well_formed`; 52 backticked phantoms -> 50 listed
and the note says `in_code_spans: showing 50 of 52`; the whole-table amber names `scoped: false`.
RED (three variable names reported) before, GREEN after; contract suite 163.

## Done criteria

- [x] contract suite OK (163)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps and stock prompts untouched.
