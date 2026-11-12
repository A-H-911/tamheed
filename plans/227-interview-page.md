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
