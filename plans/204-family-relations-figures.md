# Plan 204: a relations figure per family

> Maintainer-executed, 2026-10-04. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G4 (per family: a relations figure, then the three flow figures in 205), G13 (file
> figures), G17 (the frame), G3. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (one figure per family, derived from the engine's
  relation rules, so the count follows the registry; the label-width rule bounds every label) - **DONE 2026-10-04**

## What this beat changes

- **One relations figure per family**, derived from `RELATION_RULES` as D5 is: the family in the
  centre, one node per incoming relation kind on one side and per outgoing kind on the other, each
  listing the partner families' prefixes (the plan's sketch had one node per partner family; the
  shape is owned below). A family with no typed relation says so in one line instead of an empty
  figure. File figures (`docs/guide/figures/rel-<type>-<lang>[-dark].svg`), embedded in each family's
  fold through `figure_file()`.
- The caption and the lane-free layout; the kinds and prefixes are the engine's identifiers, never
  translated; the family's label is the alt text's head.
- Captures: the densest family in English light and dark and Arabic light, the smallest in English;
  the embed path and its 390 px behaviour are the 203 primitives, measured there.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-204.md` (23 pinned phrases in the six guide files, none
  on the families' folds). After: `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-204.md` (4 files, 3 with a token difference,
  no modal drop).

## What landed, beyond the plan

- **The shape changed from the plan's sketch.** One node per partner family would have put twelve
  boxes beside `decision`; the figure has one node per relation KIND, listing the partner families'
  prefixes (wrapped by the width estimate), the family in the centre, the incoming kinds on the
  left, the outgoing on the right, and a "within the family" node below when the table carries
  `superseded_by`. Derived from `RELATION_RULES` through the facts, as D5 is: 28 families get a
  figure, 9 get the sentence (`ui.rel.none`), and the count follows the registry.
- **The file models are computed from the facts** (`file_models(f)`): the swimlanes are static,
  the relations figures exist for the families a typed relation names. `figure_file()` and the
  build's lint pass read that dict.
- **Two geometry rounds.** Every edge into the centre elbowed at the same mid-x and the lint counted
  their overlapping verticals as crossings; each edge now gets its own elbow, ranked by its distance
  from the centre (the farthest hugs the centre), all inside the 60 px gap; with eight kinds the
  first spacing marched the elbows into the column's own box, so the step scales with the count.
  The lint is green on 160 files' models, both copies.
- **A node may carry a plain-text tail** after its resolved label (the same-family node: the
  resolved "within the family" line, then the kinds as identifiers). The renderer appends it.
- **The alt text takes a plain prefix** (`alt_prefix`) because a family's label is engine text, not
  a content id.
- **The Arabic caption named the sides of the English figure.** The mirrored figure puts the
  sources on the right; the Arabic caption says so now (the English capture sides are unchanged).
- **The folder, measured:** 160 files (48 swimlanes + 112 relation figures), 1.1 MB; the dense
  family (acceptance criterion, 7 incoming kinds, 4 outgoing) is 900 x 440 (its centre 82 px tall,
  10 px per arrival so the arrowheads spread; the lint does not see arrowhead overlap, so the
  capture of the densest instance is part of the bar); the small one (lesson) 900 x 146, from
  the files.
- **Captures** under `plans/evidence/captures-204/`: acceptance criterion EN light, EN dark, AR
  light; lesson EN light.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **G19, the shape of a family's relations figure:** one node per relation kind listing the partner
  families' prefixes, never one node per partner family; the family in the centre, incoming kinds on
  the left, outgoing on the right, a "within the family" node where the table can be superseded;
  the centre grows 10 px per arrival.
- **The sentence over an empty figure:** a family no typed relation names gets the one sentence;
  a figure appears the day a rule names it. Today the 9 are: `audit-verdict`, `diagram`, `document-section`, `feedback`, `glossary-term`, `milestone`, `narrative-document`, `prompt`, `waiver`.

## Validation

- `python docs/guide/build.py`: 1,460 ids, 0 missing, 0 orphans, the geometry lint and the label-width
  rule green on both copies of the 40 file models; 160 figure files. `test_user_guide` OK (12 tests).
- `python check.py`: ALL CHECKS PASSED.
