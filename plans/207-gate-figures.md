# Plan 207: the gate figures (the pipeline, one per mechanical gate, one per judgment and warn gate)

> Maintainer-executed, 2026-10-05. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G8, G13, G17, G3. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (nineteen gates across three tiers; the pipeline
  order and each gate's reads come from the server, the stage legs from a parser over the Check
  clauses of workflow.md) - **DONE 2026-10-05**

## What this beat changes

- **The pipeline figure** (`gates-pipeline`): `gate_run`'s mechanical gates in the order the server
  evaluates them, then `readiness_check` above them as the semantic layer, in the gates section.
- **One figure per mechanical gate** (`gate-<name>`): what it reads (the tables, from the 205 gate
  map; every table for G-IDS and G-COMPLETE), how it is evaluated (a view in `schema.sql` or Python
  in the server, with the line), the stages whose Check clause names it (workflow.md, parsed as the
  Writes clauses were), and its vacuous-pass warning where the server has one.
- **One figure per judgment and warn gate**: the stages whose Check clause names it, the agent's
  judgment with the mechanics its definition names, and the journal entry its verdict lands in (the
  plan's "operator where the Human line says so" was not drawn: the Human line marks approval, not
  the gate's evaluator).
- The Check parser (`extract.checks()`): every `**Check:**` clause to its sentence end, the gate
  names in it; a stage with no clause is `None`; a clause naming a gate no tier lists fails the build.
- Captures: the pipeline EN light and dark and AR light; G-TRACE (mechanical) EN light and dark, AR
  light, 390 px; G-INJECT (judgment) and G-RISK (warn) EN light.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-207.md` (23 pinned phrases in the guide files). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-207.md` (5 files with new tokens: the server
  lines and the four map names in `diagrams.py`, `CREATE VIEW` and the Check regex in `extract.py`,
  `WVR` in the content, the test's names; no modal drop).

## What landed, beyond the plan

- **One canvas helper.** The 206 effects canvas and the 207 gate figures are the same shape (a hub,
  a column fanning in, a column fanning out, a column beneath), so `_canvas()` draws both and
  `effects_figure()` is three lines. The canvas grew from 860 to 900 wide so a stage title fits the
  left column; the 19 effects canvases of 206 are re-emitted at that width (their 206 captures show
  the 860 one).
- **The Check clauses, parsed** (`extract.checks()`, the Writes parser's rule): a clause to its
  sentence end, the `G-` names in it, a cited gate no tier lists fails the build, a stage with no
  clause is `None`:

| stage | gates its Check clause cites |
|---|---|
| 1 | - |
| 2 | - |
| 3 | - |
| 4 | - |
| 5 | - |
| 6 | G-CONFLICT |
| 7 | - |
| 8 | - |
| 9 | - |
| 10 | - |
| 11 | - |
| 12 | - |
| 13 | - |
| 14 | G-DEC-STATUS |
| 15 | G-RISK |
| 16 | G-EXEC |
| 17 | G-COMPLETE, G-SET, G-TRACE |
| 18 | - |
| 19 | (no Check clause) |
| 20 | G-HANDOFF, G-INJECT |
| 21 | G-PROGRESS |
| 22 | - |

- **Stage 19 has no Check clause** (its text names `gate_run` and `readiness_check` in its Do line),
  so a mechanical gate no clause names (`G-IDS`, `G-REL`, `G-REQ-SRC`)
  carries the phrase "stage 19 runs every mechanical gate", which is what quality-gates.md's Running
  gates section states; a judgment or warn gate no clause names
  (`G-ASM-VISIBLE`, `G-BLOAT`, `G-CLAIM`, `G-CMD-THIN`, `G-COUPLING`, `G-OQ`) carries "no stage's
  Check names it". An observation on `workflow.md`, not a fix here. The match is by gate id, so a
  stage that checks the thing in words without the id does not count: stage 7 and stage 22 check
  that no blocking open question is left silently (G-OQ's matter), stage 11 that claims are cited or
  `unverified` (G-CLAIM's); their figures say no stage's Check names them. A by-content map would be
  one more hand map to keep true; the ask carries the posture.
- **The verdict's resting place, corrected.** The first figures said a judgment gate's verdict lands
  as a `gate-decision` journal entry; the reference says "a progress-entry note with the evidence",
  and `gate-decision` is the event the phase-close and release skills record for an execution gate
  (`GATE-`), the history L3241 reads. The phrase now says a journal note with the evidence.
- **The reads, from the view and the server, not the 205 comment:** `G-SET` reads `entity_types`,
  `entity_index` and `omissions` (the view's body, L861-865); `G-REL` reads `trace_edges` joined to
  `entity_index` twice (L190-192); `G-IDS` every table against `entity_index` (L2484-2498). The test
  binds every identifier in the reads map to a store table or the two registry tables.
- **The fold chrome, viewed.** The shared dress draws its accent border and dot from `--hue`, which
  each family fold sets inline and a gate fold did not: the computed border width was 0. The fold
  now sets the variable; captured closed and open.
- **The mechanics come from the bundle's own table.** `extract.gate_defs()` reads the Gate
  definitions table of quality-gates.md: the severity cell, and the backticked tokens of the Checks
  cell that are readiness rules, tools, views or tables. Today: `G-IDS`: `entity_index`; `G-SET`: `entity_types`, `g_set_failures`; `G-PROGRESS`: `g_progress_failures`; `G-TRACE`: `trace_edges`, `g_trace_failures`, `gate_run`; `G-REL`: `entity_upsert`; `G-HANDOFF`: `prompt-ids-resolve`, `handoff_emit`; `G-INJECT`: `handoff_emit`.
  The table and the three tiers are asserted equal (check.py's lint already holds them in sync).
- **The pipeline is the server's order**, pinned: `G-IDS` L2510, `G-DEC-STATUS` L2515, `G-REQ-SRC`
  L2518, the three views in one loop L2523 (`G-TRACE`, `G-SET`, `G-PROGRESS`), `G-COMPLETE` L2585,
  `G-REL` L2619; the test reads each line for the gate's own name and the vacuous warnings at L2532
  and L2541. `readiness_check`'s four parts sit above as the semantic layer with no arrow between
  the frames: they are separate calls.
- **The fold.** Each gate's figure sits in a `<details class="fold">` under its tier's table, dressed
  by the family fold's rules through `:is(details.fam, details.fold)`; the family filter's script
  still selects `details.fam` only, so a chip or a search never hides a gate.
- **Two width rounds and one id.** A stage title overflowed the 220 px left column and the vacuous
  phrase the 210 px centre (both shortened or widened); a fold label was registered as
  `ui.ui.gate.fold` because `UI()` prefixes the namespace itself. A patch script's CSS regex carried a
  doubled backslash and matched nothing, so the CSS, content and test steps ran from a second script.
- **The folder, measured:** 608 files (152 figure ids: 132 before, the pipeline, 19 gates), 3.7 MB; the
  page 1,264,242 bytes, 1,529 content ids. From the browser: the pipeline 900 x 184, G-TRACE 900 x
  222, G-INJECT and G-RISK 900 x 186; at 390 px the page's scroll width is 375.
- **Captures** under `plans/evidence/captures-207/`: `gates-pipeline` EN light, EN dark, AR light;
  `gate-G-TRACE` EN light, EN dark, AR light, 390 px; `gate-G-INJECT` EN light; `gate-G-RISK` EN light;
  `fold-G-COMPLETE-closed` and `fold-G-TRACE-open` (the fold chrome with its accent).

## Rulings taken at the review (2026-10-05)

- Approved and committed as staged.
- **G24, the Check match is by gate id:** a gate's stages are the stages whose Check clause cites
  its id; a stage that checks the matter in words without the id does not count (G-OQ at stages 7
  and 22, G-CLAIM at stage 11 today); no by-content map. workflow.md may cite the ids the day it is
  edited.
- **G25, a fold per gate:** each gate's figure sits closed in a fold under its tier's table, dressed
  like the family folds; the pipeline sits open above the tiers.

## Validation

- `python docs/guide/build.py`: 1,529 ids, 0 missing, 0 orphans, the geometry lint and the label-width
  rule green on both copies of the 152 file models; 608 figure files. `test_user_guide` OK (15 tests,
  the gate test new).
- `python check.py`: ALL CHECKS PASSED.
