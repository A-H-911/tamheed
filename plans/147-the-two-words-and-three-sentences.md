# Plan 147: the two words and three sentences in the skills and references

> Maintainer-executed, 2026-09-27. Batch map: [146-150-batch-findings-36.md](146-150-batch-findings-36.md).
> Field source: ACMP `findings_36.md` (§1 E3, B0, B1, miss 3, `DEC-234`), rulings R28, R32, R34.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

- The field recommended leaving a lesson Proposed without working out how the note would print it.
  The statement opened with its story; the note prints the opening only. The miss was the second
  in two rounds about the same cut.
- Its advisor made it state an approval's cost before the ruling: the row the new one pushes out.
- The maintainer's 5.4.0 brief retired a question by a correction on the handoff that named it.
  The recipe had run clean on a copy. The same question stood as a clause of an approved ruling,
  which a journal correction does not discharge. The field wrote a new ruling.

## What changed

**The two words (R34).**

| File | Change |
|---|---|
| `references/governance.md` | the definition: a lesson binds by its status, from the write that approves it; it is rendered when the note lists it; the roster's rule with its number; pinning, unpinning and promotion change what is rendered, never what binds |
| `skills/reading-the-record` | the paragraph that said the roster binds, "never a lesson's register status", is rewritten. It keeps its real rule: an Approved lesson is rendered by no note until the emit has run. It gains the converse: a lesson did not stop binding because the note no longer lists it |
| `references/artifact-rules.md` | "only Approved lessons reach the always-loaded note" becomes the roster's rule |
| `skills/package-onboarding` step 5 | every Approved lesson binds; the note renders some of them |
| `skills/register-liveness` step 15 | unpinning changes what is rendered; the row still binds |

**The three sentences (R28).**

| Sentence | Home |
|---|---|
| Open the statement with the rule; the cut, with its two numbers | `references/artifact-rules.md`, the one full statement |
| The same, as a short clause | `drift-register`, `progress-sync`, `slice-review`, `defect-triage`, and the front door: every skill that writes a lesson |
| Before an approval: read the row's note line, and state the approval's cost in the question. Three cases: the highest-numbered unpinned approval pushes the lowest of the ten out; a pinned approval pushes nothing out; an unpinned approval numbered below the ten is never rendered | `register-liveness` step 14 |
| An obligation is discharged in the family that made it; a dry-run proves the write lands, not that it discharges what is owed | `written-claims` step 5 |

Revision 1 of the design named two homes for the rule-first sentence. Five skills write lessons, so
the sentence has one full statement and five short clauses.

**Lint 13, the binding vocabulary** (`check.py`). It refuses the shapes that gate BINDING on the
emit or on the roster: "binds nothing until the emit", "BINDS only once", "needs to bind every
session", "what binds a session is the … roster", "roster of what binds".

- Scope: every `.md` and `.py` under the bundle, and `docs/*.md`.
- Out of scope: `stock-history.json` (it quotes old releases), `plans/` and `CHANGELOG.md` (dated
  records), and any blockquote line, because a dated correction quotes the text it corrects.
- A sentence that gates binding on the operator's word passes. "Binds nothing until the operator
  says so" is correct under R34.

## Tests

`tests/test_check_lints.py`:

- `test_blurred_binding_vocabulary_is_caught` (new): each of four blurred sentences, appended to a
  skill in a copy of the repo, fails the lint by name, one of them wrapped over two lines. Two
  controls pass in one run: the operator-gated sentence, and a blockquoted correction quoting the
  old hint.
- `test_lints_pass_on_the_repo_copy`: the lint count rises by one and the new lint is named.

`tests/test_mcp_contract.py`, `test_note_line_cut_is_the_named_constants`: the numbers are read
back out of the shipped text and compared with the engine's constants, in `artifact-rules.md`,
`governance.md` and `register-liveness`.

## Validation

| Check | Result |
|---|---|
| The two lint tests before lint 13 existed | both failed |
| `python check.py lint` | 13 lints pass; the vocabulary lint read 76 files |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| Lint 12 over the edited skills | no id, no stack word |
