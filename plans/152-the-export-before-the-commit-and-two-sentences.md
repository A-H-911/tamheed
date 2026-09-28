# Plan 152: the export before the commit, two skill sentences, and lint 13's negated shape

> Maintainer-executed, 2026-09-28. Batch map: [151-155-batch-findings-37.md](151-155-batch-findings-37.md).
> Field source: ACMP `findings_37.md` (§0.1 the sweep, E1, §6 the handoff, `DEC-235` d2, `PE-1525`),
> rulings R38, R39, R41, R43.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

- **Its handoff commit carried a page exported before the handoff.** The page on the remote lacked
  that handoff until the next commit, which came after the binds. The field's order is bind,
  export, commit both.
- **Four of the plugin's step lists export before their last journal write.** `session-handoff`
  said to write the handoff after `export_html`. `phase-close` exported before its closing entry,
  `release-close-out` before its bind, `skill-promote` before its closing note. `progress-sync`
  named no export at all. The lab's close-outs already export after the handoff.
- **Two handoffs in a row named a change request that had been closed and replaced.** The field's
  next handoff marks every line it carried forward as "carried, not re-measured".
- **One ruling changed what a word means.** The field swept the word, read each hit, covered
  fourteen dated rows with one reading rule in a decision row, and reworded its live files. The
  maintainer's own sweep for the brief had matched five phrasings: it passed a memory line that
  negated the verb, and never opened the kickoff prompt.

## The rulings (R38, R39, R43)

- The commit is the anchor. The export precedes the commit that carries the page, and
  `package_verify` reads `review_current: true` right before it. After a bind: bind, export,
  commit both. That last commit stays unbound.
- `session-handoff` gains the carried-line sentence.
- `written-claims` gains the rule for a ruling that changes a word.

"No write follows the export" was the maintainer's first form of the rule. It cannot hold: a bind
names a commit and must follow it. The advisor caught it before the question was put.

## What changed

One rule, five step lists, two sentences, one lint shape.

| Skill | Before | After |
|---|---|---|
| `package-writes` §4 | no rule on the page | the rule, naming `review_current` and `review_exported_by` |
| `session-handoff`, "Write it LAST" | after the final write, `gate_run` and `export_html` | after the final write and `gate_run`; the export follows the handoff |
| `session-handoff`, the order rule | status moves, handoff, commit, bind | the same, then export, then the commit that carries the bind and the page |
| `phase-close` step 7 | `gate_run`, export, closing entry, close, commit | `gate_run`, closing entry, export, close, commit with the page |
| `release-close-out` steps 6 to 8 | `gate_run`, export, notes, bind, close, commit | `gate_run`, notes, bind, export, verify, close, commit with the page |
| `skill-promote` steps 6 to 7 | emit, export, readiness, closing note, close | emit, readiness, closing note, export, close |
| `progress-sync` step 8 | `gate_run`, close | the same, plus a pointer to the rule for a project that commits its page |
| `prompt-templates.md`, the `release-close-out` row | "export, notes, close" | "notes, bind, export, close" |

- **`release-close-out` gains no commit.** The approved plan's table wrote "notes, commit, bind,
  export". The list binds the release's own tag or commit, which exists before the ceremony, so
  no commit belongs between the notes and the bind. The list changes in its order only.
- **`session-handoff`, one bullet:** a line carried from the previous handoff is re-measured at
  its source or marked carried. A thing outside the store is re-read where it lives.
- **`written-claims`, step 5, one bullet:** sweep the word's every form, word-bounded, and read
  each hit; sweep every file a session reads before acting; a dated record keeps its text under
  ONE reading rule in a decision row; a live file is reworded in the same change.
- **Lint 13** refuses a negation of "bind" followed, inside its own clause, by the emit, the note
  or the roster. The window stops at a full stop, a semicolon and a colon.

## Not changed, on purpose

- `slice-review` step 8 and the release-prep paragraph of `follow-up-prompts.template.md`: each
  exports and then reports or reads. No journal write follows.
- The stock guide. It states no order for the export, so its body changes in the title only
  (plan 154).
- No lint reads step order. The validation below is a read, stated as one.

## Tests (written first)

| Test | What it pins |
|---|---|
| `test_check_lints.py::test_negated_binding_vocabulary_is_caught` | three negated sentences fail, the field's own among them; four controls pass: gated on the operator's word, "binds nothing", and the same correct sentence joined to a clause about the note by a semicolon and by a full stop |

## Validation

| Check | Result |
|---|---|
| The new lint test before the edit | failed on the field's sentence: `None != 1` |
| The pattern over the bundle and `docs/*.md` before any skill edit | 76 files, 0 hits; its first form hit one correct sentence joined by a semicolon, which closed the window at `;` and `:` |
| `tests.test_check_lints` after the edit | 8 tests, OK |
| `python check.py lint` after the skill edits | ALL CHECKS PASSED; lint 13 over 76 files |
| `export_html` over the skills, the references, the templates and the guide | 18 hits, every one read. No list holds a journal write between the export and the commit |
| `prompt-templates.md`, the rows of the five skills | one row stated the old order; corrected |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
