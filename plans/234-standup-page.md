# Plan 234 -- the standup page (SR15, SR16, SR17, SR35, SR37, SR38, SR43)

> Status: DONE 2026-11-16 on `feat/standup-report`. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

`plugins/tamheed/server/standup_page.py` and `standup.css`. The page is a pure function of the
row: header (draft banner or "Recorded by human:x on <date>", the local window, snap, override,
correction and checkpoint notes, the colour in words and the rule colour when it differs), at a
glance, headline, Needs from you, Where we stand (first report), What we did, Challenges and
decisions, What we expect to do next (the plan labelled "a plan, not a record"), Terms used, a
folded footer that never prints the operator's words. The frame of `review.html`: one escape
point, the same content policy, no script, `#` links only. Lists show 8 items and fold the
rest; a shrink loop keeps the engine part at most 1,400 visible words; one counter serves the
tool and the tests.

- **Check:** goldens `tests/standup_golden/{first,daily,override,correction}.html` with a pinned
  clock and offset (`--regen`); hostile titles render as text; the content policy, no script,
  `#` links only; engine words at most 1,400 on a 500-task, 200-defect, 150-verdict fixture; an
  over-share narrative warns and is counted; the first report exempt and complete; the
  glossary lists only terms in use; times in the row's offset; the operator's words never on
  the page. **Expected:** goldens stable across two runs and both Python versions.

## As built (2026-11-16)

- `standup_page.py`: `render`, `fit` (the shrink loop, the engine part at most 1,400 visible
  words, the narrative never shrunk), `meta` (the header and footer text from the row),
  `visible_words` (one counter for the tool and the tests: no head, style or title, and of a
  closed fold only its own summary), the plain words for statuses and families, the glossary
  of only the terms on the page. `standup.css` (light and dark, print, phone width).
- **Looked at in a browser** (a local server, Playwright, desktop and 390 px): three wording
  faults fixed (a table name in "New rows", plurals, the rule's reasons). The first report
  listed every item as "new"; a catch-up now shows each item's state.
- **Goldens** `tests/standup_golden/{first,daily}.html` with a pinned clock and offset
  (`python tests/test_standup.py --regen`), stable over two runs. `.gitattributes` keeps them
  and every `reports/*.html` LF.
- **Review (a code-review agent):** a narrative colour that is not a string crashed the page
  (now green unless it names a colour); every count now passes `esc()` too. The hostile test
  covers every narrative field and a non-string colour.
- **Tests:** 9 page tests (goldens, the frame, hostile text, the budget on 500 tasks and 200
  defects, the first report whole, the glossary, times and the words never shown, the rule
  colour, the counter); the suite has 32.
