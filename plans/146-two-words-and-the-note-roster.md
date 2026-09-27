# Plan 146: two words in the engine, and the note's roster on the review page

> Maintainer-executed, 2026-09-27. Batch map: [146-150-batch-findings-36.md](146-150-batch-findings-36.md).
> Field source: ACMP `findings_36.md` (§1 the note effect, B0, B1, `DEC-234` d2, `PE-1519`), rulings
> R29, R34, R35.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

The field approved one unpinned lesson. The note's roster took it in and pushed the oldest of the
ten out. To tell the operator that cost before the ruling, the agent read the server's source; it
had done the same one round earlier for the 177-character cut. Its handoff then recorded the pushed
row as one that "no longer binds".

Two things in the plugin stood behind that:

- **The review page** listed every Approved lesson, 30 in the field, under a fold titled "rendered
  into the CLAUDE.md note". Ten were rendered. Nothing on the page said which.
- **The bundle defined "binds" two ways.** `governance.md` says status is the single truth for what
  binds. `reading-the-record` (5.2.0, plan 132) says the note's roster binds, "never a lesson's
  register status". The field followed the second. The maintainer's review found the
  contradiction; the field did not report it.

## The ruling (R34, R35)

Two words. **Binds** is the status: the operator's word, retired only on their word. **Rendered**
is the note's roster: what every session is sure to read. A lesson pushed out of the roster still
binds and is read only by query.

## What changed

Three strings, two constants, one data hand-off. The store's shape does not change.

| Where | Before | After |
|---|---|---|
| The approval hint, an Approved row | "this lesson BINDS only once the always-loaded note is rebuilt" | "this lesson binds from this write and is RENDERED only once the always-loaded note is rebuilt" |
| The approval hint, a Promoted row | the same sentence | "this lesson binds from this write; the always-loaded note names its skill only once it is rebuilt" |
| The note's footer | "N more Approved lesson(s): …" | "N more Approved lesson(s) bind too and are not rendered here: …" |
| The `lessons-note-budget` advisory | "unpin what no longer needs to bind every session" | "unpin what no longer needs to be rendered for every session" |

- The hint's cap phrase ("only if pinned or among the 10 newest unpinned Approved rows") is
  byte-identical. Four places pin it; none was re-aimed.
- `_NOTE_LINE_MAX = 180` and `_NOTE_LINE_CUT = 177` name the note's cut. The skills teach the two
  numbers from plan 147 on.
- `export_html` adds `note_roster` (`ids`, `cap`) to the dict it already passes to `render`. The ids
  come from `_note_lesson_rows`, the helper the note itself uses. The page imports nothing new:
  `render`'s own docstring says the server computes "so this module never imports it".
- The Approved fold gains a column, `note (rendered at the next emit)`, with `rendered`,
  `not rendered`, or `not evaluated` when no server state was passed. Its title names the rule. A
  sentence under it says the column is computed from the store, so the note on disk differs until
  an emit has run, and a blocked emit renders nothing.

A Promoted row got its own sentence because the old one was wrong for it twice over under the new
word: a Promoted row is never rendered.

## Not changed, on purpose

- No new key in any tool result (R31).
- The note's heading, "these bind every session": true of the rows it lists.
- The name of the `lessons-superseded-binding` rule: correct under R34.
- The page does not read the note on disk. `handoff_emit` takes its target from the caller; the
  exporter does not know it.

## Tests (written first; each failed before its edit)

`tests/test_mcp_contract.py`:

- `test_note_lessons_section_renders_approved_only`: the new footer; then the review page is
  exported and its marked ids equal the ids the emitted note lists. The row past the cap reads
  `not rendered`.
- `test_lesson_approval_says_the_note_is_rebuilt_only_by_handoff_emit`: the Approved sentence, the
  absence of the old verb, and the Promoted sentence, which carries neither "renders" nor
  "RENDERED".
- `test_lessons_note_budget_advisory_names_promotion_candidates`: the advisory's new wording.
- `test_note_line_cut_is_the_named_constants` (new): a statement of 180 characters prints whole;
  one of 181 is cut to 177 and an ellipsis.

`tests/test_export_html.py`:

- `test_lessons_fold_marks_the_note_roster` (new): 12 unpinned and 1 pinned low-numbered Approved
  rows; marked ids equal the block the emit writes; the old title is gone; `render(…, None)` prints
  `not evaluated` in every cell.

## Validation

| Check | Result |
|---|---|
| The five tests before the engine edits | 3 failures, 2 errors |
| The five tests after | pass |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| The operator's trace file over the two gate windows (20:05:34Z–20:07:00Z, 20:12:45Z–20:14:11Z) | no line inside either |
| The repo's exporter over a `git archive` copy of the field package at `27f63ae8` | 30 rows in the fold; the ten marked ids equal the ten its note lists; the calibration (one id dropped from the expectation) is caught |

The field package's committed `review.html` was not touched: the export wrote to a scratch path.
