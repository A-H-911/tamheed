# Plan 219 -- the review page reads: wide tables scroll, long text wraps, the handoff wraps

> Status: DONE 2026-10-10 UTC (maintainer-executed, the operator's word at the review). Field cycle review-page (plans
> 219-220). Released by plan 220 as 6.4.0 (MINOR). Evidence: `plans/evidence/captures-219/` (the
> before/after pictures), `plans/evidence/scripts-219/` (the capture script).

## What the operator asked, and what was verified first

After the 216-218 upgrades the operator asked three things. Verify that ACMP and jisr landed on the
latest release; make `review.html` readable (every data table's columns are narrow, each table should
scroll horizontally and wrap its text; the Resume section's text overflows and must wrap); release a
MINOR, update the docs, print the upgrade prompts, propose more enhancements.

**ACMP, read-only:** `project | 6.3.0`, the marketplace declaration and the enable in
`.claude/settings.json`; the 6.0.0 migration landed (`entry_point` `PRT-001`, four prompt rows, the
`prompt` registry row, no `prompts/` folder), the stock guide at the package root and `review.html`
both at 6.3.0, FB-029 `Resolved` with `resolved_in 6.3.0` and the plan 217 `upstream_ref`,
`AGENTS.md` L39 rewritten to the kickoff row; the post-migration tree uncommitted (21 entries after
the commit "tamheed package before the 6.0.0 migration"); a live session held the lock (pid 122828,
since 17:24 UTC). Nothing to fix.

**jisr, read-only:** `project | 6.3.0`, the page at 6.3.0, FB-001 `Resolved` (`6.2.1`), LL-001
`Obsolete` (the operator retired it), PE-021 (the install transition), PE-022 (the handoff), PE-023
(a correction), the initial commit made, nothing untracked. The stock guide stays 6.1.0 by design (a
planning half refreshes it at the stage 20 emit). Nothing to fix.

**One anomaly, in the plugin's own repository:** two records (`local | 6.3.0` from plan 216 and a
new `project | 6.3.0`) and an untracked `.claude/settings.json` carrying the declaration and the
enable: the operator applied the per-repository recipe here too. `*.local.json` is gitignored (the
211 memory said "a `.claude` rule"; the `.gitignore` has none, `*.local.json` does the work).

## The page, in the code (HEAD `49454c0`)

`export_html.py` embeds `viewer.css` at export under CSP `default-src 'none'; style-src
'unsafe-inline'`, no JavaScript. `_table()` emitted `<div class="tablewrap"><table><thead>...` with
no column sizing; `viewer.css` said `table { width: 100% }` and `td { overflow-wrap: anywhere }`
under the C25 comment "long text WRAPS in place — no horizontal scrolling". A nine-column table (the
progress log) shared the 76rem body, every column narrow and every cell tall. `_resume()` rendered
the handoff as `<pre class="handoff">` with no CSS rule, so the browser's `white-space: pre`
default overflowed the page. The registers section passes raw DDL column names as headers (`_cols`),
so any sizing rule must cover the DDL's 101 TEXT columns, not only the hand-written header lists.

## The design (R78)

- `_table()` emits a `<colgroup>` with one `<col class="w-s|w-m|w-l">` per header, the class from
  `_col_class(header)`: the header normalized (lower-case, `_` to space, cut at ` (`), then `w-l`
  for long prose (entry, statement, rationale, question, body, evidence, ...), `w-s` for ids,
  enums and references (id, corrects, status, lifecycle status, kind, severity, ...), `w-m` for
  everything else, dates and actors included (an ISO stamp is 20 characters, an actor runs to
  `agent:claude-code/session-...`). The function returns one of three constant strings whatever the
  header: no header text reaches a class attribute, and the CSS stays the only unescaped content.
- `viewer.css`: `.tablewrap { overflow: auto; max-height: 70vh }`, `table { table-layout: fixed;
  width: 100% }` with `col.w-s 9rem`, `col.w-m 14rem`, `col.w-l 36rem` (CSS 2.1 §17.5.2.1: the
  table's used width is the greater of its `width` and the sum of its columns, so a wide table grows
  past its fold and the fold scrolls; a narrow one still fills the width), `thead th { position:
  sticky; top: 0 }` on the already opaque header, `tbody tr { scroll-margin-top: 2.4rem }` so a graph
  node's `#id` link lands below the sticky header, `pre.handoff { white-space: pre-wrap;
  overflow-wrap: anywhere }` with the panel styling, and print without the height cap.
- Rejected: `td { max-width }` (undefined for cells, ignored by the engines), `table { width:
  max-content }` (a breakable 2,000-character entry sizes its column to the full line), JavaScript
  (the CSP forbids it), widening the body (the fold scrolls, the page's rhythm stays).

## Rulings taken at the review

- **R78 (2026-10-10, the planning checkpoint, by approval): C25 ("wrap in place, no horizontal
  scrolling") is superseded on the operator's word.** A table wider than its fold scrolls sideways,
  a long one scrolls inside its fold under a header that stays put, text wraps inside columns sized
  by kind.
- **R79 (2026-10-10, the planning checkpoint): the plugin's own repository keeps its project record,
  committed.** The local record is removed in this beat and `.claude/settings.json` lands with it,
  so the tamheed repository follows the posture ACMP and jisr follow.

## Validation

- **R79, measured.** `claude plugin uninstall tamheed@tamheed --scope local`: "Successfully
  uninstalled plugin: tamheed (scope: local)"; `claude plugin list`: three records, one per
  repository (ACMP, the tamheed repository, jisr), all `project | 6.3.0`; the repository's
  `.claude/settings.local.json` keeps `env`, `permissions` and its marketplace declaration with an
  empty `enabledPlugins`; `.claude/settings.json` (the declaration and the enable) lands with this
  commit, added by name.
- **Pins.** `pins-219.md`: 55 pinned phrases over the four files; `pins_missing.py`: 0.
- **Red first.** `test_long_text_wraps_in_place` (re-aimed) failed on HEAD's page (no `overflow:
  auto`, no `colgroup`); `test_colgroup_classes_follow_header_kinds` errored (`_col_class` did not
  exist). Green after the engine; the export suite green (`_one_per_line`, the handoff byte pin, the
  hostile-content tests included).
- **The pictures** (`plans/evidence/captures-219/`, viewport shots at 1280x900 on scratch copies;
  the committed trees untouched, `git status` clean of fixtures): `before-lab-log.png` and
  `before-demo-log.png` show the id column one character wide and every column squeezed;
  `after-*-log.png` show the progress log in sized columns scrolling inside its fold under the header;
  `before-*-resume.png` show the handoff running off the right edge; `after-*-resume.png` show it
  wrapping inside its panel; `after-lab-anchor.png` shows `#FR-001` landing visible at the top of the
  requirements register. The same shots on a scratch copy of ACMP's package (1,700 journal rows, a
  15 MB page) stayed in the scratchpad and showed the same before and after. One tuning from the
  anchor picture: the row's `scroll-margin-top` moved from 2.4rem to 3.2rem, the sections' value, so
  a row link lands below the page's sticky navigation. A second tuning from the same picture: `title`
  moved from the long kind to the middle one (14rem), because a 36rem title column in a register
  pushed `statement` offscreen for eight-word titles; a sentence-long title wraps to three lines.
  Nine pictures are committed (four before, five after), not the plan's five: both the lab fixture
  and the demo sample are shown.
- **The capture script's two corrections.** A copied `.lock` names the live session that holds the
  ORIGINAL, and `package_unlock` rightly refuses a live holder: on a copy the file is a stray and is
  unlinked before the open. An element screenshot of a 1,700-row table exceeds what a screenshot can
  be: the pictures are viewport shots with the target scrolled to the top.
- **The guide.** `docs/guide/build.py`: 1,546 ids, 724 figure files, `--check` fresh, `--missing` 0;
  no figure draws the page, none moved.
- **Lint and gate.** `python check.py lint`: ALL CHECKS PASSED on the first run (the README and the
  guide sentences under the cap). `python check.py`: ALL CHECKS PASSED (`3 case(s) checked, 0 failed,
  6 skipped`), run again after the 3.2rem tuning.
- **The border quirk.** Not visible at the header's resting position in the after pictures;
  `border-collapse: collapse` stays. If a scrolled header shows bare cells in the field, the one-line
  fix is `border-collapse: separate; border-spacing: 0`.
