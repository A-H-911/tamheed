# Plan 197: the docs, the README and the guide's prose follow the engine

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings G2, G16, P12 (the second half of the wording wave). Ledger first. Flavored mode (the
> human docs), lint 14 at 0 hard; pins before and after; the invariants reviewed; words only, the
> diagrams' geometry waits for batch B.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: LOW-MEDIUM (human prose; the guide's byte-twin) - **DONE 2026-10-04**

## What this beat changes

- `docs/methodology.md`, `README.md`, `docs/design-decisions.md` (a new decision record: why rows
  again, the field facts, what plan 027 argued and what changed since), `docs/migrate-from-keystone.md`
  (the v1 -> v3 -> v4 history kept, the 6.0 step added), `docs/architecture.md`, `SECURITY.md`
  (boundary 3 rewritten for rows, with the screening posture: a row approved after the last emit is
  unscreened until the next, as a lesson is), `docs/install.md`, `docs/workflow.md`, `CLAUDE.md`,
  `docs/entities.md` where they name prompt files or the two agents. `CONTRIBUTING.md` named
  neither.
- The guide's prose ids that still named prompt files or the two agents (`section.hero.lead`,
  `section.what.*`, `section.actors.*` and the D2 labels' words, `workflow.*`, `section.package.*`,
  `type.*`, `col.*`, `gate.*`, `rule.*`, `glossary.*`, `section.writing.2`), EN + AR; `index.html`
  rebuilt. The D1/D2 boxes keep their geometry (batch B, plan 201); only their words moved.
- Tests: no pinned phrase moved; `test_user_guide` holds.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-197.md` (39 pinned phrases occur in the wave's 12 files).
  One touches this beat's words: `never a stock body` in `docs/architecture.md`, pinned by the
  contract suite. It is true of rows (the stock guide is not a row) and stays in the rewritten
  sentence.
- After: `pins_missing.py`: 0 pinned phrases missing.
- Invariants: `plans/evidence/scripts-ste/invariants-197.md` (13 files changed, 10 with a token or
  modal difference). Every token difference is the file-to-row and the halves vocabulary
  (`<package>/prompts/` gone; `PRT-`, `prompt`, `entry_point`, `<package>/README.md`,
  `prompts-v5-backup/`, `027`, `6.0` new). Two modal words fell: `never` 22 -> 21 in `README.md`
  (the v3 rule "plain `.md` files, never database rows" left with the files) and `may` 3 -> 2 in
  `SECURITY.md` ("the next agent may execute the handoff" became the fact: the agent acts on it).
  No hedge was promoted.
- `desc_words.py`: not run, no skill description changed in this beat.

## What landed, beyond the plan

- **`docs/design-decisions.md` §23, D-PROMPT-ROWS.** Why rows again (what a file escapes: lifecycle,
  approval, the review page, the plain-English rule, `entity_query`, a skill binding; the 3,600-line
  kickoff), the row, the emit, the migration, the measured cross-version behaviour and E3, the
  number, and the error owned: plan 027's "a file is the operator's surface" left the operator with
  no surface the engine renders.
- **A v2-era cell.** `docs/methodology.md`'s boundary table still said the execution-half
  instructions live in "the generated package's `handoff/` prompts". Rows now.
- **The 192 beat's Arabic miss, owned.** `col.packages.entry_point` said a row in English since 192
  and still said a file path (`prompts/project-kickoff.md`) in Arabic. Both languages say the row.
- **"Executor repository" became "target repository"** throughout the guide (the engine's own
  parameter is `target_dir`); "executor-side" config became "target-side".
- **The residue census ran twice.** After the first patch six more lines named the executor
  (`methodology.md` rows 52 and 77, `entities.md` 803, `workflow.md` 84, `README.md` 341, the
  guide's tree comment in `render.py`). The second pass closed them; the final census finds only
  identifiers and aliases (`dia.actors.executor`, the mermaid participant alias `Executor`).
- **The census named its languages and file types this time** (the advisor's three checks). English
  Markdown: `design-decisions.md` L73 still said "prompts another agent will act on", the twin of
  the SECURITY.md sentence rewritten in the first pass; fixed. Its L172 "(agent-control, prompt and
  skill files)" sits in a dated ruling record (v5.x) and stays as history, by choice. Arabic: one
  grep over `content.py` for the agent and file words found `stagetitle.20`, stale in BOTH
  languages ("Execution-agent handoff"), which the English patterns had not matched; fixed. Python:
  `grep` over every `.py` in the bundle (the hooks included) found no engine string that teaches
  prompt files as the live surface; the hits are the v2 converter path (files, then rows), the
  leftover reporting, the migrate plan and its messages ("N prompt file(s) convert to `prompt`
  rows"), and two docstrings. Nothing owed to 198 from this census.
- **One bundle line, a 196 miss owned.** The guide's `stagetitle.20` mirrors the stage heading in
  `plugins/tamheed/references/workflow.md` (the byte-twin test asserts the two agree), and that
  heading still read "Execution-agent handoff": the 196 census pattern was "executing agent", not
  the hyphenated form. The heading now reads "Handoff to the execution half" in the bundle and the
  guide. The same grep found the H1 of `references/handoff.md` and a `methodology.md` section heading; all
  three read "the execution half" now. The two bundle headings are this beat's only bundle edits
  (P12), the first forced by the guide test, the second its twin. A repo-wide grep for the hyphenated
  and lowercase forms then found six more 196 misses: the catalog's own `prompt` row ("an executing
  agent", written in 192), `intake.md` ("execution-agent constraints"), two front-door lines, a server
  comment, and the unreleased CHANGELOG entry. All read the halves now; the sweep G2 asked for lands
  in 196 and 197, so they are finished here and put to the operator at the review. `evals.json`'s one
  intent sentence ("An executing agent that discovers a defect") waits for 198, the beat that
  re-aims the evals.
- `docs/install.md` lost a parenthetical ("at the package root since v6") to the 25-word cap; the
  sentence names `<package>/README.md`, which says it.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged; the errors owned accepted.
- **P18 (P12 read for the sweep's tail):** the nine bundle and CHANGELOG lines the repo-wide census
  found after 196 (the two headings, the catalog's prompt row, `intake.md`, two front-door lines, a
  server comment, the unreleased CHANGELOG entry) land in 197, not 198. G2 ruled the wording sweep
  into 196 and 197, so the tail belongs to the wave's last beat and the census closes empty.

## Validation

- `python check.py`: ALL CHECKS PASSED.
- Lint 14 (flavored): 0 hard after eight of my sentences were split (seven English, one Arabic:
  `workflow.migrate.s3`).
- `pins_missing.py`: 0 missing.
- `python docs/guide/build.py`: 1,390 ids, 0 missing; `test_user_guide` OK.
- Python 3.10 grammar parse of `content.py`, `render.py`, `diagrams.py`.
- The diagram geometry lint (`build.py` runs `diagram_problems` and `diagrams.lint` over both copies)
  passed with the relabelled D1/D2 boxes in both languages.
