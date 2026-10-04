# Plan 205: the three flow figures per family (lifecycle, data path, trace path), the Writes parser

> Maintainer-executed, 2026-10-04. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G4, G13, G17, G19, G3. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM-HIGH (a parser over prose; two hand maps that
  must be bounded by tests; three figures per family on a page already carrying 160 files) - **DONE 2026-10-04**

## What this beat changes

- **The Writes parser** (`extract.writes()`): for every stage of `workflow.md`, the `**Writes:**`
  clause to its sentence end (a period before whitespace, so `packages.profile` keeps its dot and
  the prose after stage 7's clause is not a write), plus the clause's own `Also ...` sentence
  (stage 21), wrapped lines joined, parentheticals and code spans stripped, split on commas, `then`
  and `Also`; each token a store table, an alias (`narrative_documents/sections`, `sections`,
  `narrative-document`) or a known non-table (`none`, `packages.*`, `canonical JSONL`,
  `handoff_emit`, `affected rows`); any other token fails the build. A stage with no clause (3) is
  `None`, never a guess. A test pins the 22 stages, every token a table, stage 7's exclusion and
  stage 21's second sentence.
- **The data path per family** (`data-<type>`): the stage pills whose clause names its table (the
  guide's stage titles, EN + AR, with the number; a bare "no stage names it" label when none does),
  the writers (a census of the server's `INSERT INTO` statements by function: `entity_upsert`
  through its generic insert for most families, `audit_record` alone for the verdicts, six for the
  journal; the public functions are drawn, the header helper `_write_package_header` is named here
  only), `data/<table>.jsonl` with its CSV, then `review.html` and its section.
- **The trace path per family** (`trace-<type>`): the gates that read its table (a map of five with
  the view or server line in a comment, plus `G-SET` for every Always family; `G-IDS` and
  `G-COMPLETE` read every table and are said in the sentence, never drawn) and the readiness rules
  whose population it is, read from a readiness run on an empty scratch package (the server names
  the table it measured), blocking or advisory by the rule roster. 20 families get the figure, 17
  the sentence.
- **The lifecycle:** one file figure for STD8 (D6 without the Review state, in the statuses
  section beside D6, which is STD9); each family's fold carries one line: a link to the set for
  STD8 and STD9, the values as pills for a domain set (the engine states no transition table, so
  none is drawn), or the sentence that the family has no lifecycle.
- Captures: the requirement family's data and trace paths EN light and dark and AR light, the
  journal's data path (the writers from the source), STD8, and the data path at 390 px.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-205.md` (23 pinned phrases in the guide files). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-205.md` (5 files, 4 with a token difference,
  no modal drop).

## What landed, beyond the plan

- **The rule side is derived, not authored.** The plan said two hand maps; the readiness report
  already names each rule's population table (`population.table`), so `extract.rule_tables()`
  runs `readiness_check("package")` on a scratch package and reads 22 of the 30 package rules
  (the rest have no table: `prose-plain-english` names a scope, the header and journal-shape rules
  none). Only the gate map is authored, five entries with their source lines in the comment.
- **Every table's writers come from the source** (`extract.inserters()`: the `INSERT INTO`
  statements of the server by enclosing function), not from the plan's words: the verdicts have one
  writer (`audit_record`), the journal six (`work_bind` among them, the 4.13 finding), every other
  table `entity_upsert`'s generic insert. The test pins the three.
- **Three families have no writing stage** (`invariants`, `glossary_terms`, `feedback`, measured
  from the parsed clauses): their data path carries the bare label instead of an empty frame. An
  observation on `workflow.md`, not a fix here: its stage spec names no writer for those tables.
- **STD8 is not D6.** D6 carries the Review branch, which is STD9's (slices, work items). The STD8
  file is D6 without Review, Approved to Implemented direct. A domain set has no figure: its
  values are the pills the statuses table and the fold already show, and no arrow the engine does
  not state is drawn.
- **One file per figure id, however many folds embed it:** `figure_file()` registers an id once.
  Nineteen folds link to the STD8 figure rather than embedding it nineteen times.
- **The hub routing is one helper** (`_hub`, the 204 elbow ranking with the gap as a parameter):
  the data path fans the stage column into the tool, the trace path fans the family out to the
  gates and the rules. Two geometry rounds: the first elbows marched into the stage column (the
  gap there is 40 px, not 60), and seven arrivals piled on a 30 px node (narrative document), so the
  tool node grows 10 px per arrival as the 204 centre does.
- **Three stale-patch minutes.** A rewritten patch script could not be written over its unread
  predecessor and the old one ran; the three files it touched (content, diagrams, the test file)
  carried nothing else uncommitted and were restored from HEAD before the new script ran. Lesson:
  a rewritten script takes a new name.
- **The parser refuses a variant.** A stage block that says "Writes" in any form the regex does not
  read fails the build; stage 3's block says nothing of the kind (its Out is "working notes, not
  yet rows"), so its `None` is the file's own statement.
- **The STD8 figure, viewed:** D6's note (approved ADRs, criteria and lessons are immutable) and the
  "verified" word on Approved to Implemented are STD8 facts, so both stay.
- **The folder, measured:** 392 files (12 swimlanes, 28 relations, 37 data paths, 20 trace paths,
  1 lifecycle), 2.2 MB; the page 1,171,796 bytes, 1,473 content ids. From the browser: the
  requirement data path 900 x 154, its trace path 620 x 266, the relations figure 900 x 496; at
  390 px the page's scroll width is 375.
- **Captures** under `plans/evidence/captures-205/`: `data-requirement` EN light, EN dark, AR light,
  390 px; `trace-requirement` EN light, EN dark, AR light; `data-progress-entry` EN light;
  `data-feedback` EN light (no writing stage); `life-STD8` EN light. The data-path captures were
  retaken on the final build after the writers census changed the tool node.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **G20, the fold layout:** the columns table, the relations figure or its sentence, a Data path
  sub-heading with its figure, a Trace path sub-heading with its figure or the sentence that only
  G-IDS and G-COMPLETE read the table, then one lifecycle line (a link to the standard set, the
  values as pills for a domain set, or "No lifecycle"). STD9 is D6; STD8 is drawn once and linked.
- **G21, domain sets:** pills in CHECK order and no arrow, because the engine's facts state no
  transition table; a figure appears the day one exists.

## Validation

- `python docs/guide/build.py`: 1,473 ids, 0 missing, 0 orphans, the geometry lint and the label-width
  rule green on both copies of the 98 file models; 392 figure files. `test_user_guide` OK (13 tests,
  the parser test new).
- `python check.py`: ALL CHECKS PASSED.
