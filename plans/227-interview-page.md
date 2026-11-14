# Plan 227 -- the interview page (FB-007, R82) - final shape after Step 0

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `slate_export(slate)`: no caller path. The name passes `_bad_name` (srv:59). The files are always
  `<package>/slates/<name>.html` and `<name>.slate.json`. Checks: unique ids, two or more options, at
  most one recommendation per question, and that one carries its reason (`operator-interview` step
  3). Every quoted id is resolved and embedded verbatim, and the slate file keeps each quoted row's text.
- The page: escaped server-rendered controls, inline CSS, ONE static inline script named by hash:
  `default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-...'; base-uri 'none';
  form-action 'none'`. No inline event handler (a hash does not cover them). No embedded JSON block:
  the script reads ids from the DOM. It keeps state, writes the answers file and reads one back.
  Reuse `export_html.esc`, `viewer.css`, `store._write_fresh`.
- `slate_read(name)`: reads only `<package>/slates/<name>.answers.json`, where the operator puts
  the downloaded file. Size cap, head check, the slate digest, every answer against its question,
  the unanswered list, `changed_rows` (quoted rows whose text now differs from what the page
  showed), `exported_at`, `_INJECT_RE` over free text. It returns a checked transcript and WRITES NOTHING.
- `operator-interview` gains one step: the page carries the questions, the session carries the
  word. The file is confirmed in this session before any write. A file from an earlier session is
  history. A changed quoted row puts its question again.
- Docs: `SECURITY.md` (the page's trust model), `generated-structure.md`, the server README, the
  stock guide (history key at the stamp), the root README, `.gitattributes` for any recorded slate.
- Design checkpoint with 226: the layout is measured against the field workshop page and the
  answers sample (rounds, attendance, an "other" answer) before the build.
- Measured in a browser, never assumed: the hash CSP in a meta tag on a `file://` page, stored
  state, and the download. Chrome here at acceptance, then the field's browser (Step 0 names it)
  through a page probe in the Jisr prompt. Stored state is a convenience, and if the download is
  blocked the page shows the answers as text to copy.
- Tests: new suite `tests/test_slate.py` in `check.py` `SUITES`: byte-identical output, hostile text
  in rows and in the slate, the CSP hash equals the script, no external URL, no inline handler,
  `review.html` still has no script (`test_export_html:737` untouched). `slate_read`: digest
  mismatch, unknown option, a bad name, oversize, a changed quoted row, an injection flag.
- **Check:** red-first tests, `check.py`, a security review of the page and the reader, the browser
  pass with captures. **Expected:** tools 21, suites 13, a slate answered and read back end to end.

## Design checkpoint (2026-11-12, on the second field's export; shapes only)

- The field's own page is one file of 1.3 MB with three script blocks: one is a data block of
  1.2 MB, and the code is 40 KB. It declares NO content policy. It has no inline event handler, no
  file input and no print call. It keeps state in browser storage and saves by a blob download.
  It runs in Chrome 157.
- Measured before the build (2026-11-12, Chrome 157.0.8103.39 on Windows, a `file://` page, the
  policy of this plan in a meta tag): the hashed inline script runs. Stored state works. A blob URL
  is created. A click listener works, and a chosen file is read. An inline handler, a second
  inline script, a script that the page injects and a remote image are each blocked and reported.
  NOT proven: that a click on the blob link writes a file. The automated browser saved none, and
  it logged no policy block for it. So the page also shows the answers as text to copy, and a
  person clicks the download once at acceptance.
- Correction (2026-11-12): this record first said that the page carries a content policy in a meta
  tag. That was a false match: the phrase stands in the page's data text. So the field's page
  proves nothing about a hash policy on a `file://` page. The browser pass of this plan proves it.
- Its views: all questions, one at a time, the whole round. It has an operator mode and a workshop
  mode, and light and dark.
- Its answers file holds the round, attendance, closure, voices, the topics decided and not asked,
  and per answer the selected option, its label, the recommended option and an outcome block.

### Rulings taken at the checkpoint

- **R95 (2026-11-12): the questions come from a slate that the agent passes.** One mechanism. The
  tool still quotes every cited row from the store. Building straight from a register was declined.
- **R96 (2026-11-12): the page includes three extras beyond the core.** A view of one question at
  a time, attendance and closure per round, and an audience mode that hides the recommendations.
  The maintainer had recommended the core only. Each extra is more script to test and to review.

## Final shape (2026-11-12, after the checkpoint and the browser measurement)

Files: `server/slate.py` (checks and rendering), `server/slate.js` (the ONE static script),
`server/slate.css`. The server registers two tools and imports the module as it imports the
review page's.

### `slate_export(slate, replace=false)` - writes two files, never a row

```
slate = {name, title, intro?,
         rounds: [{id, title, intro?, cites?, questions: [
           {id, question, detail?, cites?: [ids], allow_other?,
            options: [{id, label, detail?}], recommended?, reason?}]}]}
```

- `name` passes the package-name rule. Round, question and option ids match one short pattern.
  The id `other` is reserved.
- Refused: a repeated id, fewer than two options, a recommendation that names no option, a
  recommendation with no reason, a cited id that names no row, a text over its cap.
- Every cited row is read from the store and quoted: its id, its family, and every text column
  that holds a value, in column order. No per-family mapping is kept.
- Output: `<package>/slates/<name>.html` and `<name>.slate.json`. The slate file keeps the
  quoted text and one digest per quoted row, and its own digest names the slate.
- No clock: the same slate over the same rows gives the same bytes. A second export with other
  content is refused without `replace`.

### The page

- Policy in a meta tag: `default-src 'none'; style-src 'unsafe-inline'; script-src
  'sha256-...'; base-uri 'none'; form-action 'none'`. The hash is of `slate.js`.
- Every text is escaped at render. The script reads ids from data attributes, sets values and
  classes, and never writes markup. It holds no data block.
- Core: rounds, questions, radio options, one labelled recommendation with its reason, an other
  answer with its text, a note per question, the quoted rows in a fold, save, load, print.
- R96: a view of one question at a time, attendance and closure per round, an audience mode
  that hides the recommendation and its reason.
- State is kept in browser storage under the slate's digest. Save writes the answers file by a
  blob link, and the page also shows the same text to copy.

### `slate_read(name)` - reads, writes nothing

- Reads `<package>/slates/<name>.answers.json`, where the operator puts the saved file.
- Refused: a file over the size cap, a key written twice, a head that names another slate or
  another digest, an answer to an unknown question, an option that the question does not have.
- Returns a checked transcript: each question with its text, the selected option and its label,
  whether it equals the recommendation, the other text, the note. Also the unanswered list,
  attendance and closure per round, and `exported_at`.
- `changed_rows`: the quoted rows whose text differs now from what the page showed, and the
  questions that cite them. Those questions are put again.
- Free text is screened as the handoff is. A hit is named, never removed.
- The answer says what it is: a transcript of a file, never the operator's word.

### Counts that move

Tools 19 to 21. Suites 12 to 13 (`tests/test_slate.py`). No schema move.

## Settled before the code (2026-11-12, after the advisor's review of the shape)

- **R100**: a slate reaches the tool inline, or from `<package>/slates/<name>.spec.json`. The
  caller names no path: the place follows from the name. One set of checks and one renderer
  serve both. Measured on the second field's question bank: a round of 6 questions is 6,608
  bytes, a round of 71 is 66,610 bytes, and all 227 questions are 198,391 bytes.
- The script is hashed as LF text. Measured: a page saved with Windows line endings still runs
  the script whose hash was taken from the LF text. The hash test reads the script out of the
  page, never the file's bytes.
- A quoted row holds every column that has a value, except `last_referenced`, which `work_bind`
  stamps. `custom_attributes` is in, so a register entry shows its declared fields. The quote
  and the row's digest use that one column set.
- The slate file is the record. Its digest is computed from its content at every read, never
  taken from a field. The page is derived and is rewritten at every export, because its style
  and script move with the plugin.
- The recommendation stays hidden until the script has applied the stored audience mode, so a
  shared screen never shows the pick first.
- A round can carry its own intro and its own cited rows, for what was decided and is not asked.
- Slate text takes `dir="auto"`, since a slate may be Arabic.
- Not built, for the second field's prompt: voices, a field for who answered (the note holds
  it), an approval mark per answer (the word stays the session's), a store digest and a build
  time (one digest per quoted row serves, and the page has no clock).

## As built (2026-11-12)

- `server/slate.py`: the slate's checks (`check_slate`), the row quotes (`quote_rows`), the
  record and its digest (`build_record`, `record_text`, `record_digest`), the page (`render`),
  strict JSON (`parse_strict`) and the answers reader (`read_answers`).
- `server/slate.js`: the one static script, ASCII, 9 KB. It reads ids from data attributes, sets
  values and classes, and writes no markup. `server/slate.css` follows the review page's style.
- In the server: `_slate_files` gives the four fixed places of a slate from its name.
  `slate_export(slate, name, replace)` and `slate_read(name)` are registered. Tools: 21.
- The page: rounds, questions, radio options, one marked recommendation with its reason, a free
  answer, a note, every cited row in a fold, attendance and closure per round. Its controls:
  all questions, one at a time, audience mode, save, load, print, clear in two clicks.
- The recommendation is hidden by the style until the script adds `ready`, and the script adds
  it after it has applied the stored audience mode.
- `slate_read` returns `rounds`, `answers`, `unanswered`, `put_again`, `changed_rows`,
  `screened` and `exported_at`. It writes nothing.
- Teaching: operator-interview step 7, two controls in `SECURITY.md`, the package layout, two
  README rows, the changelog, `.gitattributes`. The guide: prose for 8 ids in both languages,
  two effects figures, the tool count. Scripts under `plans/evidence/scripts-227/` wrote them.
- The guide recipe has one more step in this plan: after the line re-aim, run
  `plans/evidence/scripts-227/guide_227.py`, because the re-aim restores the two files first.
- Not built: a per-answer field for who answered, a voices block, an approval mark, a build time.

## Validation (2026-11-12)

- `python check.py` passes on Python 3.13 and on Python 3.10: thirteen suites. The new suite
  `tests/test_slate.py` runs 15 tests. The selftest registers 21 of 21 tools.
- Mutation check: with each of five safeguards switched off in turn, a test fails. The five:
  escaping, the `last_referenced` exemption, the digest from content, strict JSON, the screen.
- Browser pass, Chrome 157 on Windows, a `file://` page built from public demo content:

| Check | Result |
|---|---|
| Hostile text in the title, a row and an option | shown as text: one script, no image element |
| Markup typed into a note | stays text |
| One question at a time | one question and one round show, the pager shows |
| Audience mode | no recommendation mark and no reason shows |
| Reload | answers restored, view and audience mode applied before the pick can show |
| A file of another version of the slate | refused by the page, nothing loaded |
| A file with `__proto__` and `constructor` as ids | loaded, nothing polluted |
| Clear | needs two clicks |
| Arabic text | resolves right to left |
| Console | no error and no warning |

- NOT proven: that a click on Save writes a file. The automated browser saved none. The page
  shows the same text to copy, and a person clicks Save once at acceptance (plan 229).
- One real round on a scratch copy of the second field's package, built by script from its
  question bank and passed through the spec file:

| Slate | Spec | Export | Page | Read |
|---|---|---|---|---|
| 75 questions, 3 rounds, 202 quoted rows | 71 KB | 0.04 s | 945 KB | 0.01 s |
| 227 questions, 10 rounds, 509 quoted rows | 201 KB | 0.06 s | 2.2 MB | 0.03 s |

  A second export moved no byte. The store verified after both, and no row was written.

## Review (2026-11-12)

Two independent reviews (R92): a security brief and a correctness pass. Neither found a critical
or a high defect. The security pass tried to break the page's three claims and did not: every
text escaped, only the one script runs, the script writes no markup. I ran each reproduction
before I used it. What changed:

- Text typed into the free answer and never selected was dropped from the transcript, unscreened.
  Typing now selects the free answer, and the reader returns that text whatever is selected.
- The saved time was returned as any text. It is one fixed form now, or nothing.
- A list where text belongs raised (`recommended`, `selected`, a row of the record). Each is a
  refusal now. A lone surrogate in any text is refused.
- A file that starts with a byte-order mark was refused. It is read now: text copied into a file
  on Windows often starts with one, and the copy route is the fallback of an unproven download.
- The page had no length limit on a field that the reader caps at 8,000. Each field carries it.
- A refusal echoed a file's text whole (1.5 MB in one probe). It echoes 60 characters at most.
- The record is refused when it names another slate, or quotes rows that the slate does not cite.
- A slate folder or file that is a link, or that leads outside the package, is refused. A
  junction at the folder carried a write out of the package. A hard link is not caught.
- One large row cited by 40 questions made a page of 200 MB. The quoted text is counted before
  the page is built, and the record is capped at the same size at export and at read.
- A name with a trailing newline and a Windows device name are refused. The page is built
  before either file is written. A carriage return in a text no longer marks the page as moved.
- The toolbar sat inside the header and scrolled away. It is a child of the body now.
- The result says `provenance: unverified`, and the note says that an empty `screened` proves
  nothing. Three instruction-shaped phrasings passed the screen in the reviewer's probe.
- A new test reads the keys of the script's `collect()` and ties them to the reader.

Not changed, and stated: a chosen option is undone only by Clear. A page opened for the first
time shows the recommendation until audience mode is set (the skill step says so). The first
wording of this plan overclaimed that, and it is corrected in the code's comments.

After the fold: the suite runs 18 tests, the five mutations are still caught, and the gate
passes on Python 3.13 and 3.10.

## Visual review (2026-11-13), and plan 227b

The operator confirmed on 2026-11-12 that Save writes a file in Chrome on Windows. The operator
then held the release: the page had been tested for what it does, not for how it reads. A
visual pass followed, on a public demo slate of eight questions in three rounds, one of them
Arabic. Captured at 1440 and 390 pixels wide, in every view. What it showed:

| # | Finding | Where |
|---|---|---|
| 1 | The sticky bar hides the title of a question that is scrolled to, and text shows through its edge | every view |
| 2 | On a phone the bar is 206 pixels tall, a quarter of the screen, on four rows | 390 wide |
| 3 | A chosen option has no visible state beyond the radio dot. The recommended option has a blue outline, which reads as the chosen one | options |
| 4 | The reason of the agent stands after the free answer box, far from the option it explains | question |
| 5 | Two empty text boxes stand open under every question (free answer, note). A yes or no question is 300 pixels tall | question |
| 6 | The question is the same size as body text, and it has no number of its place | question |
| 7 | A long question breaks the border of its box, because it is a legend | question |
| 8 | A quoted row lists engine columns first and raw (`mvp 0`, `introduced_in 1`, `source_kind`), and `custom_attributes` as raw JSON. The folds weigh more than the question | quoted rows |
| 9 | One question at a time is not a presenter view: the header, the notice, attendance, closure and the raw answers text all stay. The pager stands below them, and no key moves it | one view |
| 10 | The raw answers JSON is always on the page | page end |
| 11 | The header shows the slate name and its digest. Progress is small text there, and it is gone once the page scrolls | header |
| 12 | Arabic: the round title and the detail align right, the question and the options stay left, and punctuation lands on the wrong side. The fixed words are English only | Arabic round |
| 13 | Lines run 1,280 pixels wide. Text boxes span the whole width | 1440 wide |
| 14 | The page is dark only. A projector in a lit room needs a light page | theme |
| 15 | Print, captured: quoted rows print as black bars, labels and details print pale grey, and a note typed into the page is white on white, so the printed record loses it | print |
| 19 | On a phone the bar hides the whole title of a question and its quoted rows, and a wrapped option falls back under its radio | 390 wide, captured |
| 16 | The native file control (`Choose File`, `No file chosen`) sits in the bar | bar |
| 17 | Audience mode shows only as a pressed button | bar |
| 18 | No visible focus ring on the options. Touch targets are small | keys and touch |

### Plan 227b: the page reads as an interview, not as a form dump

No change to the two tools' contract, to the record, or to the answers file. The page's markup,
its style and its one script change. The security doctrine holds: one static script named by
hash, every text escaped, no markup written by the script.

1. **A reading column.** One column of about 52 rem, body text at 16 pixels, the question as a
   heading with its place (`3 of 8`). A heading, not a legend, so a long question wraps.
2. **The bar.** One row with a solid ground and an edge: progress, the two views, audience mode,
   Save. Load, Print and Clear move under a `More` fold, and Load becomes a button. Questions
   take a scroll margin, so the bar never covers a title. One row on a phone.
3. **Options as cards.** The whole card is the click target, with its detail inside it. A chosen
   card is filled. The recommendation is a badge, never an outline, and its reason stands under
   that card.
4. **Less open space.** The free answer is one more card, and its box opens when it is chosen.
   The note is a small `Add a note` control that opens a box, and stays open once it holds text.
5. **Quoted rows.** One line under the question names them (`Rests on: FR-001, CON-002`). An open
   quote shows the title and the main text first, then the status. Engine columns stand under
   `More fields`, and `custom_attributes` shows as a list of keys and values.
6. **A presenter view.** One question fills the screen. The header, the notice, attendance,
   closure and the answers text are out of it. The pager stays at the bottom edge, with the
   round's name. The arrow keys move it. A round's attendance and closure show as its last step.
7. **The round's wrap-up.** Attendance, closed, closed by and the closing note stand together at
   the round's end, as one compact block.
8. **The answers text.** It moves into a closed fold named `Trouble saving?`. The page opens it
   by itself when the download fails.
9. **The header.** The title and the intro. The slate's name and digest move to a small fold at
   the page's end, with the sentence on what the file proves.
10. **Direction and language.** The id stands outside the text, so each text takes its own
    direction, and options align to their text. A slate may name its language (`en` or `ar`).
    The page then sets its direction and shows its fixed words in that language.
11. **Light and dark.** The page follows the system's scheme, and a control overrides it. The
    choice is kept with the other state.
12. **Print.** Dark text on white, quoted rows open, an empty box as a ruled line, a question
    never split over two pages.
13. **Keys and touch.** A visible focus ring, targets of 40 pixels, a banner while audience mode
    is on.

Validation: the suite's structure tests follow the new markup. The script scan and the hash test
stay. Captures at 1440, 768 and 390 pixels, light and dark, the Arabic slate, the presenter
view, and a printed page read as a file. The operator looks at the page before the commit.

Rulings: **R101** approves all 13 steps and asks for a deeper review by eye. **R102** adds the
slate's `language` key. The operator confirmed on 2026-11-12 that Save writes a file in Chrome.

## As built: plan 227b (2026-11-13)

- The page's markup moved to `server/slate_page.py`, with its fixed words in two languages.
  `slate.py` keeps the checks, the record and the reader. `slate.css` is one file with its own
  light and dark tokens, and it no longer takes the review page's style. `slate.js` is still
  the one static script.
- A slate takes an optional `language`, `en` or `ar` (R102). The page sets its language and its
  direction from it. The script reads its own sentences from data attributes of the body, so it
  stays one text for every page.
- The 13 steps are built: the reading column, the bar, option cards with a filled chosen state,
  the badge and its reason in the recommended card, boxes that open on demand, quotes that name
  their row in the summary, the presenter view by steps with arrow keys, the wrap-up block, the
  folded answers text, the header without the digest, both directions, both schemes, print.
- The tools' contract and the answers file did not change. The record gained the `language` key.

What the captures of the new page showed, and what was corrected because of them:

| Seen in a capture | Correction |
|---|---|
| The quote folds had no marker (a flex summary drops it) | the fold draws a corner that turns |
| That marker first rendered as a broken glyph: a control character had entered the style | redrawn with borders, and a test refuses a control character in the style |
| A list field of a register entry showed as raw JSON | a list of text is joined |
| Arabic text in an English page jumped to the far side | each text keeps its direction inside the page's alignment (`bdi`) |
| The place counter read `3 / 1` in the Arabic page | the counter is left to right |
| The audience banner scrolled away | it stays under the bar |
| On a phone the bar scrolled sideways and Save was off the screen | two short rows, with progress, Save and More on the first |
| A quote with only a title printed an empty box | such a row is one line, not a fold |
| In the Arabic page an open fold's marker still pointed sideways | the open rule also holds for a right-to-left page |
| At 768 pixels the bar ran past the edge, More was cut off, and the whole page scrolled sideways | the two-row bar holds up to tablet width. Measured: no sideways overflow at 320, 390, 768 and 1010 pixels |

Captured and looked at: 1440 wide in dark and light, 390 wide, the Arabic page, the presenter
view, audience mode, an open quote of a requirement and of a register entry, the More menu, and
print (the print rules applied on screen, with the folds opened as the script opens them).

Validation: the suite runs 21 tests. Five mutations are caught. `python check.py` passes on
Python 3.13 and 3.10, and the selftest registers 21 tools. Not yet done at this point: the
operator's own look at the page.

## Plan 227c: the page takes over what Jisr's workshop page does (approved 2026-11-13)

The operator did not accept plan 227b's page. This is the approved plan, as revised after a devil's-advocate review.

### Context

Round 6.5.0 (plans 221-229) is on branch `round/6.5.0`, ten commits pushed, CI green. The
interview page (`slate_export` / `slate_read`, plans 227 and 227b) is rebuilt and uncommitted.
The operator looked at ten captures and did not accept it: no audience management, no attendance
confirmation, no rounds management, no end-of-round points, no visibility control. "Did you look
at Jisr?" I had measured Jisr's page for layout only. This plan carries every Jisr feature that
generalizes into the general page, before any commit. The release stays held (R101).

### 1. Weaknesses of the first 227c plan

- **It was written from Jisr's script alone.** I had not opened Jisr's page, and one read of its
  builder had failed without a retry. Looking found three features the list of 20 missed.
- **It hid a contract change.** `slate_read` was to stop refusing a file from an earlier export,
  stated as a detail. That refusal was a reviewed safeguard. Now ruled (R111).
- **It used one word for two things** (`put_again` for a changed row and for a changed question).
- **Its storage design was wrong.** It keyed stored answers by slate name. Measured: every local
  page in Chrome shares one storage area, so two packages with one slate name would overwrite
  each other's answers.
- **It trusted the script without a check.** The gate reads the script as text. A real defect was
  sitting in the current page: an arrow key on a focused option turns the step (measured).
- **It locked attendees out.** Room view locked all rounds but one, but Jisr's attendees read
  their own copy before the workshop.
- **It left the operator's look to the end**, after the script and the reader.
- **It was silent on file-name collisions**, on caps for the new lists, and on its own size.

### 2. Assumptions

**Confirmed by inspection or measurement (2026-11-13)**
- Jisr's page, opened and looked at: header with how-to steps and an owner legend, a round
  navigator, a controls row, the step order (attendance, terms, blocks of cards, already
  decided, points, closure with export), and the card's parts.
- Jisr's builder: the owner is derived (operator-led or approval required), blocks hold at most
  four cards, a decided topic leaves the cards, terms come from glossary rows with `variants`.
- Jisr's round check passes only when every group is present or covered by a named person and
  all four closure fields are filled (`round_record.py`, `check`).
- Jisr's workshops run in Chrome on macOS (`state.txt`). No other browser is a target.
- All `file://` pages share one storage origin in Chrome: a page in another folder read the key.
- My page: an arrow key on a focused option is taken by the pager (`slate.js`, the keydown rule).
- Slate names are lower-case letters, digits and dashes, so no slate name holds a dot.
- The package has `stakeholders` (`STK-`, `title`) and `glossary_terms` (`GT-`, `term`,
  `definition`). A glossary row has no status column.
- Rulings R81-R102 and the Step 0 prompt are in the repository's own plan records.

- Jisr's bank counted against the grammar (numbers only, private copy): 239 asked questions and
  51 decided topics in 13 rounds, the largest of 29. Every question has four options and a
  basis. At most 11 rows are cited by one question (the cap is 30). 65 carry the approval flag.
  All 23 glossary rows are marked approved, 18 carry `variants`.
- ACMP's package folder is `tamheed-package`, Jisr's is `tamheed`. A generic package name is
  normal, so the package name tells two projects apart only by luck.

**Rejected**
- "Lead and consulted name the attending groups." (Counted: 51 questions are led, and 87 are
  consulted, by someone outside the seven attending groups. Cards name 11 people, 7 attend.)
- "`depends_on` names questions of the slate." (18 questions depend on a decided topic.)
- "A key of package name and slate name is unique." (Two projects may both say `tamheed`.)
- "The script is fine because its text is pinned." (The arrow-key defect passed 21 tests.)
- "Stored answers can be keyed by slate name." (One shared storage origin.)
- "Room view can always lock rounds." (Attendees read alone first.)
- "The list of 20 is complete." (Hand-outs, ids named in text, the row an answer settles.)

**Unresolved, each with where it is settled**
- A cloned `<template>` under the hash policy on a `file://` page: step 3, in Chrome.
- The size and export time of all 14 Jisr rounds (about 245 questions with their folds): step 5,
  on the private scratch copy. If the page passes the cap, the count is put to the operator.
- The Arabic fixed words (about 60 new ones) read right to a native reader: step 2a.
- Chrome on the field's Mac saves a per-round file as it does here: the Jisr brief's own check.

### 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A third rejection of the look | Step 2a: static captures beside Jisr's own, before the script exists |
| Script defects that the gate cannot see | A browser check file in the repository, about 40 checks, run at acceptance, output filed. The documents say CI does not run it |
| The Presenter switch read as protection | `SECURITY.md`, the README and both briefs say: a display rule, the hidden text is in the file |
| Another local page reads stored answers | Said in `SECURITY.md`. The key is the page's own path. Nothing is stored beyond what the saved file would show |
| About twenty new slate keys cannot fit a tool description (2,048 characters) | A new bundle reference `references/slate.md` holds the grammar. The description and the skill point at it. A test ties its key list to the code |
| Old answers taken as current | Per-question digest. `question_changed` and `dropped` are their own lists (R111) |
| A saved file the reader never sees (a browser renames a second download) | The reader names every file in `slates/` that starts with the slate's name and that it did not read |
| Two files disagree on one answer | Listed under `conflicts`, neither is picked |
| Hostile text in the new fields | Every new text passes `esc()`. The mutation check gains a case per new field. Still one script, no data block |
| A forged or oversized answers file | Undeclared keys refused by name, caps on text, 200 points a round, the 2 MB file cap as today |
| The work is large (about 2,000 more lines) and context is lost midway | The plan record and memory are written first. One step at a time, each green before the next |
| ACMP's three fixes wait behind a page it does not use | Named here. The release order is the operator's (R101), and is asked again at the end |
| Files past the 800-line rule | New modules `slate_answers.py`, `slate_round.py`. If `slate.js` passes 800 lines it is split, and the page joins the parts in a fixed order under one hash |

### 4. Changes made, and why

- R111 ruled, and the three lists separated (hidden contract change, one word for two things).
- The storage key is built at run time from the page's own path (`location.pathname`), with a
  digest per answer. It differs per folder, survives a re-export, and adds no byte to the page.
  A moved file starts empty: the saved file is the record, the browser's copy is a convenience.
- A participant may be marked `attends: false`: named as lead or consulted, with no attendance
  row (counted on Jisr's bank). `depends_on` may name a question or a decided topic.
- A term matches by its `term` and by `variants` in its attributes, when that is a list of text.
- An answer with no `question_digest` counts as changed. `unread_files` lists names and opens none.
- Arrow keys leave a focused option alone, in both views (measured defect, Jisr guards it).
- R112: the slate decides how a page opens, `reading` or `session` (attendees read alone).
- R113: three features added (hand-outs, ids named in text, the row an answer settles).
- R114: a browser check file in the repository (the gate cannot see script behaviour).
- Step 2a added (the operator's look moved forward).
- Round-file names, case rule, caps and refusals stated (collisions and forged files).

### Rulings (operator, 2026-11-13)

- **R103** All five groups now. **R104** Visibility: filter by owner and group, open and lock
  rounds, hide the recommendation, hide operator-only parts. **R105** A Save per round and a
  Save for the whole page. **R106** Point kinds and closure fields default to Jisr's four each,
  a slate may declare its own, and the reader reports a round complete or names what is missing.
- **R107** Approval is a flag, never a tick. **R108** Participants are STK- rows or plain
  `{id, name}`. **R109** One page with a Presenter switch, a display rule. **R110** Terms are
  the package's GT- rows, matched at export.
- **R111** `slate_read` reads a file from an earlier export and marks per question.
- **R112** Slate key `opens`: `reading` (default: ready rounds readable, operator-only parts and
  recommendations hidden) or `session` (only the open round readable).
- **R113** Hand-outs, ids named in text, and `settles`. **R114** The browser check file.

**My own choices, not ruled:** the Presenter switch does not show recommendations (its own
control). Print gives what the view shows. `known` and `decided` are row ids, `gap` is text. A
round file is `<name>.<round id>.answers.json`, round ids are unique without regard to case, and
the reader builds the names from the record. A round with `ready: false` may have no questions.

### What Jisr has, and where it lands

| # | Jisr feature | In 227c |
|---|---|---|
| 1 | Round navigator, picker, counts, header how-to and legend | sidebar on wide screens, picker on narrow ones |
| 2 | Round "not ready", "N of M ready" | round key `ready` |
| 3 | Per-round progress, a line naming round and step | built |
| 4 | Blocks inside a round | round key `blocks`, or flat `questions` |
| 5 | Per-round export, import, clear with confirm | plus the whole-page ones (R105) |
| 6 | Reopens where it stopped | stored round and step |
| 7-8 | Participant groups, attendance (present, or covered and by whom), guests | `participants` (R108) |
| 9-11 | Owner, lead, consulted, filters, "answered by" | question keys, presenter controls |
| 12-14 | Points, closure, "already decided" with a reopen box | R106, round key `decided` |
| 15-16 | "Unknown", "Requires evidence", the recommendation's basis | reserved ids, key `basis` |
| 17-18 | Context folds by kind, terms per card and per round | `known`, `decided`, `depends_on`, `gap`, GT- rows |
| 19-20 | Old answers marked, storage banner, skip link, announcements | R111, built |
| 21 | Hand-outs for attendees | `<name>.orientation.md`, `<name>.short.md` |
| 22 | Ids in a text named beside it | resolved at export, "Named here" |
| 23 | The row an answer settles | question key `settles` |

Not carried, and said in the Jisr brief: the approval tick (R107), the fixed gate round (an
operator-owned round covers it), adoption of Jisr's old storage keys, the in-page self-test
(R114 instead), bolding an option's lead phrase, and the tool that writes rows from an export.

### Design

Doctrine unchanged: every text passes `esc()`, ONE static script named by hash, no data block,
no inline handler, nothing loaded, nothing sent, the same slate gives the same bytes. The points
block clones a server-rendered `<template>`. The script writes no markup of its own.

- **Slate** (new keys optional): `participants`, `point_kinds`, `closure_fields`, `terms`,
  `opens`. Round: `ready`, `blocks` or `questions`, `decided`. Question: `owner`, `lead`,
  `consulted`, `approval`, `basis`, `known`, `decided`, `depends_on`, `gap`, `settles`,
  `allow_unsure`. Checks: ids unique, every reference resolves, reserved ids refused.
- **Page**: steps per round are context, attendance, terms, questions under block headings,
  already decided, points, closure. Presenter controls: open a round, session locking, show
  recommendations, owner filter, group filter. Both languages, schemes, print, 320 to 1920.
- **Answers file, version 2**: whole page, or one round with `round` in its head. Per answer:
  `selected`, `other`, `note`, `answered_by`, `question_digest`. Per round: `attendance`,
  `guests`, `points`, `closure`, `reopen`, `closed`, `closed_by`.
- **`slate_read(name, round=None)`**: reads every file of the slate. Returns per round
  `complete` and `missing`. Also `rounds_without_file`, `unread_files`, `conflicts`,
  `approval_needed`, `changed_rows`, `question_changed`, `dropped`, and `settles` per answer.
  Still `provenance: unverified`. It writes nothing.
- **Hand-outs**: plain Markdown, the room's questions only. No option, no recommendation, no
  operator-owned question, no decided topic.

### Files

`plugins/tamheed/server/`: `slate.py`, new `slate_answers.py`, `slate_page.py`, new
`slate_round.py`, `slate.js`, `slate.css`, `tamheed_server.py` (`_slate_files`, both tools, both
descriptions, lookups through `quote_rows`). Tests: `tests/test_slate.py`, new
`tests/test_slate_rounds.py` in `check.py` `SUITES` (suites 13 to 14, with every pin that counts
them), new `tests/slate_browser_check.js`. Docs: new `references/slate.md`,
`skills/operator-interview`, the three READMEs, `tests/README.md`, `SECURITY.md`,
`generated-structure.md`, the guide prose EN and AR with `index.html`, CHANGELOG, the stock
guide with its history key and the lab fixture if its body moves, both briefs,
`plans/227-interview-page.md`, the round record, the ledger, memory.

**The browser check file.** The content policy admits one script, so the check is not loaded by
the page. I drive it from Chrome's DevTools protocol against a demo page: it clicks, types,
saves and loads through the DOM and returns pass or fail per behaviour. It is first run against
today's 227b page, where the arrow-key check must FAIL. That proves the check can see a defect.

### How this review was done

- **Read directly:** Jisr's page script (all of it), its builder's main path and hand-out
  writers, its round-record tool, its test names, its `state.txt`. My `slate.py` in full, the
  key handler and storage code of `slate.js`, `_slate_files`, the two schema tables.
- **Measured in Chrome:** the shared storage origin of local pages, the arrow-key defect, and
  Jisr's page looked at in six states.
- **Counted on the private copy:** Jisr's bank against the grammar (the numbers above).
- **Reviewed by the advisor twice.** Its findings are sections 1 to 4. I verified each by a
  read or a count before I used it.
- **Not used:** no sub-agent. No web research: every open point was about this code, Jisr's
  files or Chrome's behaviour, and each could be read or measured here. Nothing in this plan
  rests on a researched source, so there is no researched finding to set apart.

### 5. Execution plan

| # | Step | Validation point | Expected output |
|---|---|---|---|
| 0 | Write the plan record (`plans/227-interview-page.md`, R103-R114) and memory | lints pass | the work survives a lost context |
| 1 | Grammar and record, tests red first | new tests fail, then pass. A 227b slate still exports | `check_slate` takes every new key and refuses each bad one by name |
| 2 | Markup and style, with a Jisr-shaped demo of invented text | suite green, no script change yet | static page in room and presenter view, English and Arabic |
| 2a | **The operator's early look** | captures beside Jisr's own page, state by state | their notes, applied before step 3 |
| 3 | The script, and the arrow-key fix | `tests/slate_browser_check.js` run in Chrome: every check passes | rounds, presenter state, filters, points, files, marks all work |
| 4 | The reader | red-first tests for each list and each refusal | a transcript with the lists of section "Design" |
| 5 | Hand-outs. Then all of Jisr's bank on the private scratch copy | size and time measured. Nothing from it is committed | counts only, in the record |
| 6 | Browser pass: 320, 768, 1024, 1440, both schemes, Arabic, both views, a locked round, each filter, print | every capture looked at, each defect fixed and recaptured | a parity table: each Jisr feature, its capture, its test |
| 7 | The operator's look at the finished page | captures sent, both demo pages by full path | their word, or notes that return to step 3 |
| 8 | Docs, briefs, guide rebuild | `check.py` on 3.13 and 3.10, selftest, mutation check extended, `acceptance_650.py` | all green |
| 9 | Two independent reviews with a security brief (R92), then the advisor | each finding checked by running it | findings fixed or answered in the record |
| 10 | The commit question (227b, 227c, the briefs), push, CI | CI green on every leg | then the release question again |

### 6. Approval checkpoint

Approving this plan approves: rulings R103-R114, my five unruled choices above, the two new
modules, the second suite, the browser check file, two hand-out files per slate, version 2 of
the answers file, and steps 0 to 9 on the working tree. It approves no commit, push, merge, tag
or release: each is asked when reached. Step 2a and step 7 each stop for the operator's look.
Nothing has been executed.

## As built: plan 227c (2026-11-14)

The operator saw the early look at step 2a and said: right direction, continue.

### What was built

- `server/slate.py` is the grammar. New modules: `slate_rows.py` (quoted rows, what the export
  derives, the digests), `slate_answers.py` (the reader), `slate_round.py` (the steps of a
  round), `slate_words.py` (the fixed words in two languages), `slate_handout.py` (two sheets).
  `slate_page.py` is the shell. `slate.js` and `slate.css` are rewritten.
- The server: `_slate_round_files`, `slate_read(name, round=None)`, two more fixed files for
  the hand-outs, and both descriptions. The bundle gained `references/slate.md`.
- Tests: `tests/test_slate.py` (21, re-aimed), `tests/test_slate_rounds.py` (13, new, in
  `check.py`), and `tests/slate_browser_check.js` (43 checks, run in a browser, not in CI).
- Scripts: `scripts-227/demo_227c.py`, `guide_227c.py`, `docs_227c.py`.

### Parity with the field's page

| # | Feature | Where it is pinned |
|---|---|---|
| 1-3 | Round list, not-ready rounds, progress for each round | `test_a_round_is_shown_as_its_steps`, browser checks 20 to 22 |
| 4 | Blocks | `test_a_slate_takes_every_new_key` |
| 5 | A file for each round, load and clear | `test_a_round_file_is_read`, browser checks 31 to 40 |
| 6 | The page reopens where it stopped | the stored `ui` state, seen in a reload of the demo |
| 7-8 | Participants and attendance | `test_a_round_file_is_read`, browser check 23 |
| 9-11 | Owner, lead, consulted, filters, answered by | `test_a_round_is_shown_as_its_steps`, browser checks 26 to 29 |
| 12-14 | Points, closure, decided topics | `test_a_round_file_is_read`, browser check 24 |
| 15-16 | Unknown, Requires evidence, basis | `test_the_page_shows_what_the_operator_decides_from` |
| 17-18 | Context folds, terms | `test_the_export_derives_names_terms_and_named_ids` |
| 19 | Old answers marked | `test_answers_of_an_earlier_export_are_read_and_marked`, browser checks 36 and 37 |
| 20 | Storage banner, skip link, status line | the markup, seen in the captures |
| 21 | Hand-outs | `test_the_export_writes_two_hand_outs_for_the_room` |
| 22 | Ids named in a text | `test_the_export_derives_names_terms_and_named_ids` |
| 23 | The row an answer settles | `test_a_round_file_is_read` |

### What looking and measuring found, and what changed

| Found | Change |
|---|---|
| The older suite bans a timer and `location` in the script. My new script used both | the download's address is not revoked, and the storage key is read from `document.URL` |
| A participant's name stood in an attribute | a name is text of the page, never an attribute's value |
| The page scrolled sideways: a hidden line broke the float of a question's heading | every child of a question clears the heading |
| A jump landed under the presenter's controls | the scroll offset follows the view |
| Attendance boxes stretched to unequal heights | the grid aligns to the start |
| On a phone the controls stayed in view and took 40% of the screen | on a narrow screen only the bar stays in view |
| At 320 pixels the filter buttons passed the edge | they wrap |
| The room banner said that recommendations are hidden when they were shown | the banner names what the room view hides, and nothing else |
| Print in the view of one step showed operator parts in the room view | the print sheet repeats the room view's rule |

### Measured

- The browser check passes 43 of 43 on the demo page in Chrome. On a page built with the
  arrow-key guard removed, its arrow-key check fails. That page stood in for plan 227b's page,
  whose markup lacks the ids that the check drives.
- No sideways overflow at 320, 390, 768, 1024 and 1440 pixels, in both views.
- The field's whole bank as one slate, on the private copy: 13 rounds, 239 questions and 51
  decided topics, no refusal. Export 0.18 seconds. Page 3.7 MB. It loads in 0.4 seconds, and
  an answer registers in 28 milliseconds. One round's file was read back: complete, with its
  two approval marks listed.
- `python check.py` passes on Python 3.13 and 3.10. The selftest registers 21 tools, and the
  longest description holds 921 characters.

### Not done, and said

- CI runs no browser. The script's behaviour rests on the browser check, run by hand.
- The stock operator guide was not changed. Its two sentences about the page stay true.
- The list of rounds shows a round's whole question count. The room view counts fewer.

### The two reviews of plan 227c

Two independent reviews with a security brief (R92). Each finding was reproduced before
its fix: in Node for the script, and as a failing test for the reader.

| Review | Finding | Fix |
|---|---|---|
| Page | A question whose id is a name that every object inherits (`constructor`) read as answered on an earlier version, and its digest was lost on save | the script's maps have no prototype, and a browser check pins it |
| Page | A default export matched every glossary row, with no bound | more than 200 glossary rows are refused, with the route: name the rows under `terms` |
| Reader | A point whose `kind` is a list raised a type error | every value is checked as text before it is looked up |
| Reader | A record edited by hand raised: a quote with no digest, a lone surrogate in an id | a quote's shape is checked, and an id is checked as text that can be written |
| Reader | A forged file's closure key was echoed whole, up to the file's size | the echo is 60 characters at most |
| Reader | 55,000 unknown question ids gave 55,000 `dropped` entries | 50 are listed, and `dropped_more` counts the rest |
| Reader | A saved time with a very long fraction was echoed | nine digits at most, ASCII only |
| Reader | A file name beside the page was echoed raw | only a plain, short name is listed, and `unread_more` counts the rest |
| Reader | An answer that one file holds and another leaves empty stood with no word | it still stands, and `one_file_only` names it and both files |
| Reader | Two files that agree on an answer and name two versions of its question took the first version | the answer is marked as changed and put again |

Both reviews found no way for a text to reach the page as markup, script, policy or SQL,
and no read or write outside `<package>/slates/`. Not verified by either: behaviour on POSIX,
and the SDK's handling of a lone surrogate in a result.

After the fixes of both reviews the browser check passes 44 of 44 on the rebuilt demo page.
The gate passes on Python 3.13 and 3.10, and the acceptance script holds every observation.

### After the advisor's review of the finished work

| Found | Change |
|---|---|
| The session lock hid the other rounds, and the room view could still open one | in a session the room view cannot open another round: the list, the picker and Next all stop |
| The browser check was run as a copy typed into a tool, never as the file | `tests/run_slate_browser_check.mjs` runs the file as it stands, with Node and Chrome |
| Run that way on the Arabic page and on the field's page, the check failed three times each | all six were the check's own faults: English word order, left-to-right keys, a fixed wait. The check now reads the page's words and direction, and waits for the page |
| The check would have thrown on the field's page, whose first round has no question of the room | it picks the first ready round that asks the room a question |
| The mutation check was not rerun, and its old form no longer reached a round's markup | `scripts-227/mutate_227c.py`: twelve safeguards are removed one at a time, and each turns a test red |
| Arabic used one word for the room and for attendance | the room is one word, attendance is another |

The check file passes 48 of 48 on the English demo, on the Arabic demo, and on the page built
from the field's whole bank on the private copy. Run it: `node tests/run_slate_browser_check.mjs
<page.html>`.

The last look, on captures of the final build, found three more defects. Each is fixed and
pinned by a browser check. The view of one step opened with its top off the screen. A block's
heading stayed when a filter hid all its questions. The status read "1 questions shown".
