# Plan 166: the review page — one row per line

> Maintainer-executed, 2026-09-30. Batch map: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md).
> Source: the field's `DEF-224` / `ADR-0052` (the page's history was the whole cost of its
> secret scan; not filed as feedback), the maintainer's measurement, ruling R57.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field measured, and what I measured

- The field: its required secret scan (gitleaks over the full history) ran 15–32 minutes and
  was cancelled once at its budget. Locally at two CPUs: 8m37s for the full history, 14.4 s
  without `review.html`'s past versions, 2.5 s for the page alone. Under an ADR it now skips
  the page's past versions and scans the current page separately.
- Why (M72): the generator joined table rows and graph elements with no newline. The field's
  page held four lines of 840–912 KB — both graphs and the journal table twice — and each
  carried something that moves on every export (a freshness stamp, a count), so every export
  added about 4 MB of patch text. gitleaks reads `git log -p`; a scanner that reads patches
  pays for every changed line's bytes. Over the field's last 15 page commits: 13 added 3.9 to
  4.9 MB each.

## The ruling (R57)

Each table row and each graph element on its own line, and one docs paragraph (plan 167)
for a project that scans history.

## What changed (`export_html.py`, 37 changed lines)

| Site | Before | After |
|---|---|---|
| `_table` | rows joined by `""` | rows joined by `\n`; `<tbody>` and `</tbody>` on their own lines |
| `_fold` | `</summary>` then the inner | a newline after `</summary>` |
| `_graph_svg` (both graphs, the aggregate path too) | edges, nodes, labels joined by `""` | one element per line; the three `<g>` layers on their own lines |
| `_graph_full`, `_flow` node groups | the hidden incident `<path>` copies joined by `""` | one per line |
| `render` | the freshness paragraph then the section body | a newline between them |

Nothing else. The inline radio/label runs, `<text>`, `<td>` content and the handoff `<pre>`
are untouched (a newline there would render).

## Validation

- Tests first, red then green: every `<tr id=` starts its line; no line holds two `</tr>`,
  two `<path ` or two `<g class=`; `<tbody>` on its own line; the inline runs adjacent; the
  handoff `<pre>` verbatim; the aggregate graph path; after one journal write the added
  lines hold no pre-existing row and stay under 12,000 bytes (the demo fixture: 162,364
  before the change). The 44 export tests and `python check.py` green.
- **The byte check** (`scripts-fb026-fb027/bytecheck.py`, `render_with.py`): the v5.7.0
  tag's engine and this tree render the same store on the same date; the pages are EQUAL
  once the newlines between tags are removed, the stamp replaced, and plan 165's one new
  readiness row taken out — on the field copy at `d47d9938` (35,884 → 60,273 lines) and on
  the lab fixture (295 → 1,081 lines).
- **The browser check** (Playwright, Chromium, both pages served from localhost, every fold
  opened): the field page reads 111,576 elements, 11,915 rows, 10,340 paths, 12,020,187
  characters of `innerText` with an equal SHA-256, and a scroll height of 5,949,160 px on
  both engines; the lab page 4,329 / 428 / 182 / 129,283, equal but for plan 165's "28
  rows" → "29 rows". Full-page screenshots of the lab page (`plans/evidence/pages-166/`)
  differ in 64 pixels, one 9×11 region: that digit.
- **The field's diff, measured in git** (`export_diff.py`): on a fresh copy, the first
  5.8.0 export re-flows the page once — `26396` added, `2006` removed, a 20.2 MB patch (the plan-166 tree, stamped 5.7.0 still, read one line fewer: the stamp's line had not moved),
  `csv/` unchanged; the next export after one journal write: `20` added, `17` removed, a
  34,191-byte patch, 5,727 added bytes, longest added line 2,511 characters. Against about
  4 MB before.
- `ecc:python-reviewer`: no blocking finding; two MEDIUM on the tests, taken — `<text ` and
  `<circle` joined per line too (the aggregate graph's nodes are bare `<a>` elements; the
  reviewer's `<a ` count was wrong — the page's nav line holds eleven anchors — and the
  first commit of this plan carried that failing assertion for one commit), the added
  line cap raised from 2,000 to 4,000 above the measured 1,720; a LOW hoisted a set out of a
  comprehension. It measured the demo fixture at 27 added lines, 6,170 bytes. It edited the
  test file for a print and reverted it, against its brief; the diff was re-read whole.
- `ecc:security-reviewer`: nothing above INFO — every newline sits between a closing and an
  opening tag, no attribute or escaped datum is touched, the `href` set is unchanged, the
  prologue check still holds. Its reading of the docs paragraph goes into plan 167: attribute
  the ADR's claim, say history is not rewritten, name the store's free-text fields as where a
  secret would enter (covered by the full `data/` scan), and call the field's setup its own
  decision, neither recommended nor validated.

## What stays as it is

A write that adds a node or an edge to the connected graph re-emits both graphs (every
position moves): the field's `3a6dd21b` case, 1.3 MB simulated. A smaller page, a stable
geometry, the journal rendered twice: out of scope, said in the design record.
