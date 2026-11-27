# Plan 257: the slate fixes, measured (2026-11-27)

The fixes for Jisr's FB-043, FB-032, FB-034 and FB-033, and R166. Chrome on Windows 11, headless.
The scripts are in `scripts-257/`. The pages are built by `tests/slate_browser_page.py`.

## The check fails on the old code and passes on the new

The same plain page (no `show_recommendations`), built by two bundles, run through
`tests/run_slate_browser_check.mjs`:

| Bundle | Result | The checks that fail |
|---|---|---|
| HEAD before 257 (the 6.8.0 slate code) | 49 passed, 3 failed | an intro keeps its line breaks; the page does not scroll sideways; no card holds content wider than itself at 390 px (7 of 16 cards, up to 491 px over) |
| 257 | 52 passed, 0 failed | none |
| 257, the keyed page | 52 passed, 0 failed | none (the recommendations show at open, with no click) |

The 6.8.0 bundle refuses the keyed page's spec: "the slate has unknown key(s)
['show_recommendations']". That is the expected way back (plan 263 measures the rest).

## What the first check missed

1. The first overflow check compared each element's box with its card. It passed on the old page.
   An unwrapped word runs past its paragraph's box, while the box stays inside the card. The check
   now compares each card's `scrollWidth` with its `clientWidth`. It also reports the width and
   the number of cards that it measured, so a check that measured nothing fails. A code review
   found two more gaps, both fixed. The check ran after the main check had hidden the
   recommendations and the operator's questions, so the scan now switches the presenter view
   and the recommendations on first (16 cards, not 11). A card that grows to fit its content
   is caught by its edge against the column's.
2. With that fixed, the old page still passed. The field's path
   `(raw/85-owasp-api2023-0xa8-security-misconfiguration.html):` wraps at its hyphens under the
   normal rules of line breaking, on this page. The field measured 36 px of overflow on its own page,
   which this page does not rebuild. A sha256 digest has no place to break, and such digests are common
   in a package's texts. Every long text of the page now holds both. The old page then failed as
   the table shows.

## The 1280 px widths did not move

`overflow-wrap: anywhere` lets an element shrink below its longest word, and that could narrow a
grid track or a flex item (MDN). The demo slate of plan 227c, with no long word, was built by the
two bundles. `scripts-257/widths_257.mjs` read the width of every visible element:

| Width | Elements of the reading column | Moved more than 1 px | The round list and the bar | Moved |
|---|---|---|---|---|
| 1280 px | 583 | 0 | 35 | 0 |
| 390 px | 583 | 1: the slate's intro, 4.6 px (its line breaks now show) | 16 | 0 |

So the rule stays on `.column`. The fallback in the plan (the text blocks only, plus
`min-inline-size: 0` on the card) is not needed.

## The 6.8.0 fixture

`scripts-257/fixture_680.py` exports the slate of `tests/test_slate.py` with the bundle of the tag
v6.8.0, and writes an answers file with 6.8.0's own question digests. The current `slate_read`
reads it with no question put again, no changed row and nothing in `put_again`
(`test_a_record_and_answers_that_6_8_0_wrote_still_read`). `.gitattributes` keeps the three files
byte for byte (`-text`).
