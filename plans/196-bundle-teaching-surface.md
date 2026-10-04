# Plan 196: the bundle's teaching surface speaks of prompt rows and the two halves

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings P6, G2, G16, P12. Ledger first. The wave protocol of the STE batch applies: pins before
> and after, the token-set and modal-word invariants, `desc_words.py` on every description touched,
> lint 14 at 0 hard on every rostered file.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (27 skills, 17 references, 15 templates; pinned phrases in the contract suite and the evals) - **DONE 2026-10-04**

## What this beat changes

- The front door `skills/tamheed/SKILL.md`: the stage-20 paragraph and the handoff section say prompt
  rows (the "never database rows" sentence inverts), the header's `entry_point` names the kickoff,
  the operator approves the rows; the two halves wording.
- `references/workflow.md` stage 20 (Do, Writes, Exit, Fail, Human), stages 21-22 wording;
  `references/handoff.md` (the two-surface table becomes the prompt rows and the root guide; the
  stage-20 procedure); `references/prompt-templates.md` and the three templates (row body shapes:
  the fill-in form is the body of a `prompt` row of its kind); `references/artifact-catalog.md`'s
  text around the family; `references/modes.md`, `references/safeguards.md`, every other reference
  that says "planning agent / executing agent".
- `skills/package-onboarding`: reads the Approved kickoff row named by `entry_point`. Every
  scenario skill gains one sentence: read the prompt rows bound to it
  (`entity_query("prompt", status="Approved", plugin_skill="<name>")`). `register-liveness` names
  the rows the two rules read. `ste-rewrite`: rows in place under P11, no file branch.
  `plain-english` mentions. `written-claims` ("a kickoff prompt").
- The server's rule note at the `lessons-pending` advisory and every other runtime string that
  says "executing agent". The stock operator guide's "agent" sentences.
- `references/vocabulary.md`: terms rows for "planning half" and "execution half" (G16), and a
  names row if a fixed name carries the old words.
- Tests: the pinned phrases re-aimed in the same commit; `desc_words.py` clean on every changed
  description; `test_note_names_every_discipline_skill` and the stock-README needles hold.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-196.md` (55 lines; the pins touching this beat's words
  were `amends` for a ruling and `scope-change` row (`SC-`) FIRST, both untouched).
- After: `pins_missing.py` named two phrases gone, `never a stock body` in `ste-rewrite` (pinned by
  the contract suite) and in `register-liveness`; both restored verbatim in sentences that are true
  of rows. Final run: 0 pinned phrases missing.
- Invariants: `plans/evidence/scripts-ste/invariants-196.md` (37 files changed, 33 with a token
  difference, every one the file-to-row vocabulary: `<package>/prompts/`, `prompts/README.md`,
  `kickoff.md`, `prm-NNN-<kind>.md`, `unit: files` gone; `PRT-`, `plugin_skill`, `kickoff`,
  `phase`, `situational`, `README.md` new; two citations left with their file-era sentences, `5.0`
  in handoff.md and `028` in prompt-templates.md). Modal words fell in four files, each a file-era rule
  that left with the files: `handoff.md` ("the v4 baseline never had them"), `prompt-templates.md`
  ("never database rows", "the tool never renames", "any file path a prompt names must exist"),
  `quality-gates.md` ("never to a stock body" became "as their own rule"), `skills/tamheed/SKILL.md`
  ("never database rows"). No hedge was promoted.
- `desc_words.py`: one description differs, `plain-english` ("prompt file" -> "prompt row"), the
  vocabulary swap R11 allows.

## What landed, beyond the plan

- **Sixteen scenario skills gained the sentence, not seventeen.** `loop-guard` has no orientation
  step (it is the brake an operator reads before a loop, with no package call), so a row bound to it
  would be read by nobody. `plugin_skill` still admits the name (P14 admits every scenario skill);
  the brief and the guide say a row binds to a skill that reads the package. Put to the operator at
  the review: keep the admission, or narrow P14 to the sixteen.
- **The vocabulary's two new terms reached the guide:** the Writing discipline section renders the
  terms table from the file, so `vocab.term.*` and `vocab.never.*` ids for the halves were written
  EN + AR and the terms count moved 22 -> 24.
- **Lint 14 caught thirteen of my sentences** (twelve long, one semicolon) on the first pass; all
  split or rewritten.
- The templates' header comments say what each template is now: the BODY of a `kickoff`, `phase`
  or `situational` prompt row. The two references to emitted scenario files
  (`release-close-out.md`, `defect-triage.md`) point at the slash skills.
- `prompt-templates.md`'s wiring rule about relative links became the `prompt-ids-resolve` rule (a
  row has no file base).
- **The inserted sentence first said "the project's own half of this ceremony"**: the word the
  vocabulary froze this very beat, in a third sense, on the bundle's most-read surface (the
  advisor's catch). It says "what is true of this project for this ceremony" now. The bare word
  `half` survives in the bundle only in the older compound "the mechanical half of the capability"
  (four places), "half-done" and "an inherited half", none a term.
- **A census hit skipped without a note:** the grep that opened the beat returned
  `server/README.md` twice and the first patch never touched it, so two registered-tool rows kept
  teaching prompt files and `unit: files` through the first gate run. Both rows, the migrate row,
  `generated-structure.md`'s package tree, `package-writes` (the files written beside the store)
  and the agent-control template's kickoff line were rewritten in the third pass after a wider
  census. The dated-but-true history lines (`CANONICAL.md` on the `.converted` file,
  `governance.md` on the retired prefix) stay.
- **The sixteen insertions were read in place:** each sits as the last line of step 1, before
  step 2, in every skill (the continuation loop stops at the first unindented line).
- `handoff.md`'s Contents list had nested the operator guide under "Prompt rows"; it is its own
  bullet now.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged; the errors owned accepted.
- **P17 (P14 amended):** `plugin_skill` admits only the scenario skills that READ their bound rows,
  the sixteen that carry the step; the brake `loop-guard` reads no package and takes no row. The
  guard is self-describing: a skill that gains the step becomes a legal value. A brake-specific
  caution belongs on `loop-iteration`, which reads its rows every pass.

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals).
- Lint 14: 94 files, 0 hard (the third pass added sixteen long sentences of mine to the tally
  before it was green). Lint 9 (teaching vocabulary) and lint 12 (skills, the
  500-line cap: the longest skill is the front door at 325 lines) green.
- `pins_missing.py`: 0 missing. `desc_words.py`: 1 of 27 descriptions differ (the allowed swap).
- `python docs/guide/build.py`: 1,390 ids, 0 missing; `test_user_guide` OK (24 terms).
- Python 3.10 grammar parse of the three touched `.py` files.
