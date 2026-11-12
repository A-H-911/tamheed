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
