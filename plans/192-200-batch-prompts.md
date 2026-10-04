# Plans 192-200: prompts return to the store (v6.0.0), the batch record

> Maintainer-executed, opened 2026-10-04. The approved plan, revised after a devil's-advocate
> review, lives in the operator's plan file; this file is the durable record in the repository:
> the rulings, the field facts, the beat map, what shipped per plan, the errors owned, what was
> not built. One plan and one commit per beat (G3). After the v6.0.0 tag, the user guide round 2
> (plans 201-210) draws the engine as it then is.

## 0. Why

Plan 175 round 2 opened with the operator's notes on the user guide. One note asked whether
project prompts are still files. They were: the kickoff, per-phase and situational prompts an
executing agent starts from lived as `.md` files in `<package>/prompts/`, beside the stock operator
guide. The operator ruled that they stop being files. The field agrees: ACMP's kickoff
(`prm-next.md`, 3.7 KB) had shrunk, by its own rules, to pointers and standing procedure that
restate the SessionStart hook and `/tamheed:orient-resume`; its three other prompt files are each
the project-specific half of one scenario skill; ACMP stored a "RESUME PROMPT" as a narrative
document on its own (DOC-052). Plan 027 moved prompts out of the database in v3 so "the operator
reads the folder and picks" from a stock library; that library became the slash skills in v5.0.0.
The reverse move is MAJOR, as plan 027's was: the handoff contract changes.

## 1. Rulings (interview 2026-10-04, five rounds and the review round)

| # | Ruling |
|---|---|
| G1 | One agent, two halves. D1 and D2 show the operator on top, one "Claude Code + Tamheed" box with two lanes (planning half = stages 1-20 and its tools, execution half = stages 21-22 and its tools), the handoff as the arrow between lanes, MCP server -> package below. "The three actors" is retitled. The README overview image follows D1. |
| G2 | Wording sweep, whole repo: "planning agent / executing agent" becomes "the planning half / the execution half" and "the agent" for Claude Code. Lands in beats 196-197. |
| G3 | Protocol: one plan and one commit per beat; ledger first; `check.py` green; geometry lint green; captures where a page changes; advisor read; the operator's ruling by question; one commit. |
| G4 | Per family: a relations figure plus three flow figures (lifecycle, data path, trace path); stage legs from a parser over workflow.md's Writes lines. |
| G5 | D3: the three dashed loop-back arcs become orthogonal dashed returns above their lane. |
| G6 | Pager (D7, D8): the step bar in rem units, identical in both languages. |
| G7 | Tools: effects canvas and call-sequence strip per tool, effects hand-authored with a server line per claim. |
| G8 | Gates: the pipeline figure, one per mechanical gate, one per judgment and warn gate. |
| G9 | Skills: the lifecycle map, the discipline citation matrix (derived), one strip per skill. |
| G10 | Nav: numbered sections, two-level TOC, sharper titles, visible chapter structure. |
| G11 | Logo and icon: the two-half paving mark with a return arc; `icon.svg` redrawn from it; the tagline reconsidered. |
| G12 | Workflows: one three-lane swimlane per recipe (operator / agent / engine). |
| G13 | Per-item figures as sibling files (`docs/guide/figures/*.svg`) via `<picture>` + a script swap; D1-D8 inline; the byte-twin covers the folder; LF-pinned. |
| G14 | Prompt files leave the engine (P1-P13). |
| G15 | Engine change first (6.0.0), the guide round after its tag. |
| G16 | The word is "half": the planning half, the execution half (the vocabulary gains the terms). "Phase" collides with `PH-` rows; "mode" collides with the package's eight modes and with Claude Code's plan mode, which the kickoff template invokes. |
| P1 | A dedicated family `prompts`, prefix `PRT-` (`PRM-` stays retired as conversion provenance), `kind IN ('kickoff','phase','situational')`, `title`, `body`, optional `phase_id`, optional `plugin_skill` (checked at write against the bundle's skill folder names), STD8 lifecycle, the LIFE/DISP/SRC/TAIL blocks. The note rosters Approved prompts per skill as it rosters lessons. Class Always. |
| P2 | A fresh executing session reads nothing new: the hook's resume block, the note, `/tamheed:package-onboarding` reading the Approved kickoff row; each scenario skill reads the rows bound to it. Nobody pastes a kickoff. |
| P3 | `handoff_emit` precondition: an Approved `kickoff` row named by `packages.entry_point`. G-INJECT screens prompt rows; `prompt-ids-resolve`, `prose-plain-english`, the oversize, stale-line and restated-content scans move from files to `prompts.body`. |
| P4 | Migration by `package_migrate` (preview, the operator's word, confirm): every non-stock `prompts/*.md` becomes a Proposed row (kind: the file `entry_point` names is the kickoff, then the filename or front matter, else `situational`; provenance in `custom_attributes`), `entry_point` is rewritten, the files move to `prompts-v5-backup/`, the stock README is handled (byte-equal to a shipped body: removed; customised: moved and named), the folder is removed. Abort on any anomaly, the package untouched. |
| P5 | The stock operator guide moves to `<package>/README.md`; `refresh_stock`, stock-history (keyed by file name) and lint 9 stay. |
| P6 | The three stage-20 templates and `prompt-templates.md` stay as body shapes for prompt rows; stage 20 writes prompt rows. |
| P7 | 6.0.0 MAJOR; `package_version` stays `4.0.0`; migration `008_prompts.sql`; `schema_version` 8 (the plan-031 pattern). |
| P8 | Note marker v6 -> v7; the sentence the hook parses stays verbatim; lint 9's blacklist gains v6. |
| P9 | An ACMP brief 6.0.0, every class replayed on a `git archive` copy; the STOP is ACMP's operator's. |
| P10 | No typed prompt relation (`relates_to` covers a kickoff -> its first slice); the bundle folder `plugins/tamheed/prompts/` keeps its name. |
| P11 | Approved prompt rows are edited in place, structure and text (the R45 class); no `superseded_by`, no immutability trigger. |
| P12 | Beat 196 split: the bundle (196), the docs + README + guide prose (197). |
| P13 | review.html gains a Prompts section (kind, plugin skill, status, title, the body in a fold). |
| P14 | `plugin_skill` admits the 17 bundled scenario skills only (`disable-model-invocation: true` in the frontmatter), never the front door or a discipline skill (plan 192 review). |
| P15 | G-INJECT at emit time screens Approved prompt rows only, as it screens lessons; a Proposed row blocks nothing because the executing agent reads Approved rows (plan 193 review). |

Measured 2026-10-04 with the live 5.9.0 server on scratch packages (the CHANGELOG states it):
`entity_index` is never serialised, so a 5.9 server opens a 6.0-migrated package, leaves
`prompts.jsonl` untouched as an orphan file, keeps the registry row, and G-SET names `prompt`;
`handoff_emit` refuses there for want of files. If a trace edge touches a `PRT-` row the 5.9 open
fails with a foreign-key load error, raised from `package_open` as an uncaught `IntegrityError`
(engine candidate E3, not built here).

## 2. The beat map

| Plan | Beat | Status |
|---|---|---|
| 192 | The family: migration 008, registry, catalog, governance, guide ids, tests | DONE 2026-10-04 |
| 193 | The engine paths: screen, scans, the emit precondition, `plugin_skill=` on `entity_query`, note v7 | DONE 2026-10-04 |
| 194 | The stock operator guide at `<package>/README.md` | DONE 2026-10-04 |
| 195 | `package_migrate` converts files to rows, proven on temporary packages and the ACMP replay copy | planned |
| 196 | The bundle's teaching surface and the halves wording | planned |
| 197 | The docs, the README and the guide's prose | planned |
| 198 | Stamp 6.0.0; the fixture and the sample migrated by the tool (after the stamp, never to an unreleased body); the family becomes Always; the evals re-aimed; lab beat 34 | planned |
| 199 | The ACMP brief 6.0.0 | planned |
| 200 | Release 6.0.0 | planned |

## 2b. A sequencing change (plan 194 review)

The plan had plan 195 migrate the lab fixture and the generated sample. Two things break there:
the fixture's `prompts/README.md` moves to the root while four `evals.json` lines pin it under
`prompts/` until plan 198, and the root guide the emit writes carries a body no release has
shipped (the v5.0.0 lesson: never refresh a fixture to an unreleased stock body; the STE
precedent is plan 189, stamp first). So plan 195 proves the converter on temporary packages and
on the ACMP replay copy, and plan 198 (the stamp) migrates the fixture and the sample by the tool,
flips the family to Always, and re-aims the evals in the same commit.

## 3. What shipped, per plan

- **192 — the family.** (the commit this record lands in) Migration `008_prompts.sql` (the table, the
  index triggers; `schema_version` 8), `ENTITY_TABLES["prompt"]`, the registry row (`Prompt`, `PRT-`,
  class Conditional until plan 195 seeds the fixture, then Always as P1 rules), the `plugin_skill`
  write guard reading the bundle's skills folder, the catalog row (with the `readme` document
  distinction), the governance and naming-template rows, `PRT` in the guide's id-token regex, the
  guide ids `type.prompt` / `table.prompts` / `col.prompts.*` EN + AR, `index.html` rebuilt; the
  exporter recognises a v2 `prompts.csv` leftover beside the live header; six tests re-aimed, two new.
- **193 — the engine paths.** (the commit this record lands in) `handoff_emit` refuses unless the
  header's `entry_point` names an Approved kickoff row (four refusals, each naming its leg and the
  way out); G-INJECT, the oversize check, the stale-line scan and the restated-content detectors run
  over the Approved prompt rows; the converted hint reads `custom_attributes.converted_from` on every
  live row; the v2 `handoff/` leftover compare runs against rows; the note carries a Prompts roster
  (every Approved row with the skill that reads it) under marker `v7`; `prompt-ids-resolve` and
  `prose-plain-english` read `prompts.title` / `prompts.body` and the generic prose-id scan leaves
  the family to its own rule; `entity_query(plugin_skill=)`; the hook's v7 fixture and the
  v6-still-resumes case; lint 9 blacklists v6; `handoff.md` and the guide name v7.
- **194 — the operator guide at the package root.** (the commit this record lands in)
  `_emit_prompt_library` emits the stock guide at `<package>/README.md` for all four callers; a
  pre-v6 copy at `prompts/README.md` is a leftover (stale -> retired on refresh, customised -> kept
  and named); the stock-merged check labels by location; the stock body speaks of the package root
  and the prompt rows and lands under `6.0.0` in the history; the note names the root; a stale
  pattern names old `prompts/` paths in the field's files; `ste-clean` reads the root with a
  fallback; the guide's path mentions follow (D4's node, the tree, eleven ids EN + AR).

## 4. Errors owned

- **192.** The plan put the new DDL in `schema.sql` as well as the migration; lint 2 forbids it (the
  001 byte-twin). The plan said Always from this beat; the fixture's `G-SET=pass` eval made that
  plan 195's step. The first catalog row broke lint 14 (semicolons, length) and was rewritten.
- **193.** The plan said `prompt-ids-resolve` over `prompts.body` without noticing the generic
  prose-id scan already covered the new table (a double report); the advisor caught it. The first
  pass of the emit left the v2 leftover compare reading the prompts folder (`NameError`); the suite
  caught it. Five new server strings and one guide sentence failed lint 14 before the gate.
- **194.** The stock-merged check carried a hard-wired `prompts/` label the plan did not foresee
  (one test caught it). One recipe sentence of mine failed lint 14.

## 5. Not built, by ruling or on purpose

- A typed relation for prompts (P10). Renaming the bundle's `prompts/` folder (P10). Retiring stock
  files entirely (P5's third option, declined). A `kickoff-approved` readiness advisory (the emit's
  refusal is the signal). E3, the uncaught load error on `package_open`. Arabic review beyond
  mirroring.
