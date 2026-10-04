# Plan 202: the chrome: the two-level numbered nav, D3's returns, D5's row headers, the pager in rem

> Maintainer-executed, 2026-10-04. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G5, G6, G10, G3; the round-1 bar. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (the nav is on every screen; the no-JS page must
  still read; D3's returns must pass the geometry lint on both copies) - **DONE 2026-10-04**

## What this beat changes

- **The nav (G10):** numbered sections (the number in the H2 and in the TOC), the chapter structure
  visible (the TOC groups as chapter headings, the same chapters as headers in the body), a two-level
  TOC whose second level is the active section's H3s (a `<details>` per section, the script opens the
  active one; with no script the section links alone read, and the whole nav fits a 1280 x 900 screen),
  sharper section titles where a title is vague.
- **D3 (G5):** the three dashed loop-back arcs become orthogonal dashed returns in a channel above
  their lane, landing on the lane's first pill from the top.
- **D5:** the row header pills (one per bucket, as tall as their row) become plain rounded boxes;
  the column headers stay pills.
- **The pager (G6):** the step bar of D7 and D8 in rem units (font size, height, padding), so the two
  languages render the same bar.
- `index.html` rebuilt; captures: the nav at 1280 (JS on and off), D3 EN/AR, D5 EN/AR, the pager
  EN/AR, 390 px.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-202.md` (23 pinned phrases in the five guide files; the one
  that touches this beat is `ui.toc.contents`, kept verbatim as the outer summary). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-202.md` (4 files, 3 with a token difference, all
  the new vocabulary: `sec-num`, `details.sub`, `SECTION_NUMBERS`, the D3 channel). No modal drop.

## What landed, beyond the plan

- **The nav's fit, measured.** At 1280 x 900, English, every sub-list closed: `nav.toc`
  `scrollHeight == clientHeight == 754` (no scroll), re-measured on the staged build after the last
  CSS edit; Arabic 677 == 677. With the largest sub-list open (workflows, 12 topics) 1226 against
  820: it scrolls, as the plan allows. The first build did
  not fit (1109 and then 945 against 820): each closed `<details>` spent a line on its summary. The
  summary now floats on the section link's own row as the count and a chevron, so a closed
  sub-list adds no height; the link padding tightened from .18 to .12 rem, the group margin from
  .55 to .4 rem.
- **The outer nav CSS had to be scoped** (`nav.toc > details`, `nav.toc > details > summary`):
  the desktop rule `display: contents` and the hidden summary would have matched the new
  sub-lists and opened them all with no summary (the advisor's catch).
- **An H3 that carries its own id keeps it.** The tools section's six headings (`tools-read` and
  friends) were left out of its sub-list until the anchor pass matched `<h3 id="...">` too; the
  ids `{sid}-h{n}` are assigned only to bare H3s.
- **The pager, measured.** English and Arabic bars both 945 x 32 px, every button 38.4 x 32 px,
  mono digits. Before the rem line-height on the bar the Arabic bar was 37 px tall (the label's
  Arabic line-height).
- **The number's margin in RTL.** `.sec-num` carries `direction: ltr`, so `margin-inline-end`
  resolved against its own direction and the Arabic titles sat flush against their numbers
  (measured gap 0 px). Physical margins per `html[dir]` fix it.
- **D3's returns:** s9 and s16 already receive the phase-crossing drop at centre - 14, so the
  returns land at centre + 14; s1 at the centre. The per-return "loop back" label went (the legend
  says it), and `dia.stages.loop` left `content.py` (the orphan check).
- **Three titles sharpened** (put to the operator): "Workflows" -> "Workflows: the recipes",
  "Status sets" -> "Statuses and lifecycles", "Appendix: maintaining the repository" ->
  "Maintaining the repository" (the chapter kicker says Appendix). The other nineteen stand.
- **A page opened narrow and widened lost its nav** (found by a failed capture, not by eye): the
  script closes the outer `<details>` below 960 px, and the desktop rule renders its contents only
  while open. A resize listener opens it at desktop width. Pre-existing, fixed here.
- **On narrow screens the sub-lists hide** and the links take the full column: the two-column
  mobile nav squeezed numbered titles around the floating counts. The second level is a desktop
  affordance; the 390 px capture shows the section links alone.
- **The no-script nav is simulated** (the `js` class removed, the sub-lists closed): the browser
  tool cannot run the page without script. The static HTML carries no open sub-list, which the
  test pins.
- **The sub-list summary's accessible name is a bare digit** ("6"). It is a name, so no failure,
  and the chevron is drawn by CSS. Plan 210's Lighthouse pass meets this knowingly; a visually
  hidden label is the fix if that pass asks for one.
- **Captures** under `plans/evidence/captures-202/`, every one taken on the staged build: the nav
  EN closed, EN with the workflows sub-list open, EN simulated no-script, AR closed, 390 px
  (opened; no horizontal page scroll, `scrollWidth == clientWidth == 375`); D3 EN/AR; D5 EN/AR;
  D7 with its pager EN/AR. The page carries no duplicate id (210 ids, 210 distinct; the nav test
  asserts it).

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- The three sharpened titles kept ("Workflows: the recipes", "Statuses and lifecycles",
  "Maintaining the repository"); the other nineteen stand.
- Two postures accepted: below 960 px the sub-lists hide and the links take the full column (the
  second level is a desktop affordance); the pre-existing nav-vanish defect (a page opened narrow
  and widened) fixed in this beat with a resize listener.

## Validation

- `python docs/guide/build.py`: 1,390 ids, 0 missing, 0 orphans, the geometry lint green on both copies
  with D3's returns. `test_user_guide` OK (11 tests, the nav test in: 22 numbered H2s, 22 numbered TOC
  links, no open sub-list at rest, every sub-link resolves).
- `python check.py`: ALL CHECKS PASSED.
- The numbers above measured in the page at 1280 x 900 and 390 x 844.
