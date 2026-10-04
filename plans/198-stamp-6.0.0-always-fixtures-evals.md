# Plan 198: stamp 6.0.0, the family becomes Always, the fixtures migrate, the evals re-aim, lab beat 34

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Rulings P7, P8, P13, G3; the sequencing change of §2b (the Always flip and every fixture follow
> the stamp, never a fixture on an unreleased stock body). Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: XL - **Risk**: HIGH (the release stamp; the Always flip touches every
  package's G-SET; three recorded fixtures and the generated sample rewritten by the engine; a real
  agent drives the migration in the lab) - **DONE 2026-10-04**

## What this beat changes

### The engine
- `BASELINE_ENTITY_TYPES`: `prompt` is **Always** (the catalog row follows, lint 3). A package with
  no prompt row and no omission fails G-SET naming `prompt`: the planning half writes the kickoff
  at stage 20, or records the omission with its reason before that.
- `package_migrate`'s kickoff rule (P4, rule 1) matches the header's `entry_point` by **file name**
  on any path prefix. The generated sample's header still names the v2 path
  `handoff/initial-prompt.md`; today only a `prompts/` prefix matched, so the sample would have
  landed three situational rows and kept a dead entry point. A dead entry point that names no
  converted file is cleared and said, as P4 already rules for `prompts/`.
- `export_html`: the **Prompts** section (P13), registered after Feedback: a fold for the rows
  awaiting the operator's approval (Proposed, the emit requires the Approved kickoff), a fold for
  the Approved rows (the kickoff `entry_point` names is marked), a fold for the other statuses.
  Columns: id, kind, plugin skill, phase, status, title, body. The body is in the cell, wrapped
  (the page's rule since plan 020: wrap, never scroll); an empty package says what the emit needs.
- `evals/pkg_check.py`: no new subcommand. The kickoff file check becomes `grep-present ... --tables
  prompts` and the rule check is `rule <package> prompt-ids-resolve`, both existing. The `ste-clean`
  help text names the root guide.

### The stamp (P7, P8)
- `plugin.json` 6.0.0; `CHANGELOG.md` `## [6.0.0] - 2026-10-04` replaces the Unreleased block: the
  MAJOR headline, the migration note for a live package, the measured cross-version behaviour
  (a 5.9 server opens a 6.0-migrated package, ignores `prompts.jsonl`, names `prompt` in G-SET; a
  trace edge to a `PRT-` row makes that open fail with an uncaught load error, E3), Added / Changed
  / Removed, migration `008_prompts.sql` named (lint 7).
- The version surfaces: `README.md` (badge line, the version paragraph), the front door, the server
  README, the artifact catalog, the stock guide's title line **with** its `stock-history.json`
  `6.0.0` body (an unreleased key, rewritten in place), `docs/install.md` (the note is v7 since
  6.0.0), `index.html` rebuilt (the guide reads the version from `plugin.json`).

### The fixtures and the sample (the engine does the writing, never a hand edit)
- `evals/sample-results/lab-tracker/package`: lab beat 34, below.
- `evals/sample-results/minimal-brief/package` and `execution-loop/package`: no prompt file, no
  handoff stage was run. An **omission** row for `prompt` with that reason, written through the
  server, then the page re-exported where one exists. Without it the Always flip fails their
  `gates` assertions, and the row is the honest statement of those fixtures.
- `generated-samples/support-triage-agent-v2`: `package_migrate` converts the three files
  (`initial-prompt.md` the kickoff by the header's file name, the other two situational), the
  header's `entry_point` becomes the kickoff row, the folder goes, `prompts-v5-backup/` is removed
  (git holds the files), the root `README.md` is seeded. The canonical gate stays green.

### The evals (`evals/evals.json`)
- The four stock-guide paths -> `{case_dir}/package/README.md`; the kickoff file check -> the
  `prompts` table; `5.9.0` -> `6.0.0` where the check is about the stamp; the review-page grep gains
  `section id="prompts"`; the execution-loop intent sentence speaks of the execution half; lab-tracker
  gains: the note marker `v7`, `count prompt --min 1`, `rule prompt-ids-resolve` pass, the root
  guide's title. The retired v1 assertion text (L70) stays as history.

### Lab beat 34 (`lab/scenario.md`)
- The scratch phase FIRST, by a real agent through the headless harness on a copy of the fixture
  outside the repository: T1 the operator's words run `package_migrate("package")` as a preview and
  the agent reports the plan and STOPS; T2 the words confirm, approve `PRT-001` ("The operator
  approves PRT-001 as the kickoff, 2026-10-04, lab beat 34"), `handoff_emit(refresh_stock=true)`,
  `export_html`, `readiness_check`, the handoff LAST, `package_close`. The hook's resume block on the
  v6 note is observed (a v6 note still resumes).
- The fixture phase in-process (`beat34.py`): the same steps with assertions, the migration's report
  quoted, the note's roster line, the Prompts section, `package_verify` green with
  `review_exported_by: "6.0.0"`, `prompts-v5-backup/` removed from the fixture (the ledger says so),
  no `data/.lock`.
- Evidence: `plans/evidence/lab-continuation-report-198-2026-10-04.md`, scripts and transcripts under
  `plans/evidence/scripts-ste/labrun-198/`.

### Tests
- `test_mcp_contract`: G-SET names `prompt` on a fresh package; a Proposed kickoff or an omission
  clears it; the migrate kickoff rule by file name (a `handoff/` entry point); every existing test
  that created a package and asserted `ready` or `G-SET=pass` re-aimed in this commit by name.
- `test_export_html`: the Prompts section renders kind, plugin skill, status, title and body; the
  empty-package sentence; the TOC test covers the anchor through `SECTIONS`.
- `test_eval_runner` on the regenerated fixtures; `test_check_lints` lint 8 on the stamp.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-198.md`, computed from HEAD's copies of the wave's 13
  files (`git archive HEAD` into a scratch folder, the ledger's paths kept relative): 191 pinned
  phrases occur in them. After: `pins_missing.py` against the working tree: 0 missing. The
  catalog's `prompt` row (a 196 surface) was re-checked against `pins-196.md` and `pins-197.md`
  after its class flipped: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-198.md` (19 changed prose or code files, 16
  with a difference). The modal words that fell are all in the generated sample's three prompt
  files, which the migration moved out of `prompts/` (git holds them, the rows carry the text).
  Everything else is the stamp (`5.9.0` -> `6.0.0`), the Always class, the Prompts section, the
  section count (eleven -> twelve) and beat 34's text.
- `desc_words.py`: not run, no tool description changed in this beat.

## What landed, beyond the plan

- **The words were wrong before the plugin was (owned).** T1's words ordered `package_open` and
  then the preview. `package_migrate` runs on a closed package and refused. The agent STOPPED, did
  not close on its own, and asked. T1b carried the corrected words and the preview landed exactly as
  the scenario says. The 6.0.0 brief must say "closed".
- **The migrate seeds the root guide**, so the emit that follows reports `unchanged: ["README.md"]`,
  never `refreshed`. The report says so, and `beat34.py` checks the file, not the list.
- **The hook is silent on a package with no note** (three sessions, three `status=silent` lines).
  The fixture carries no note: the emitted `package/CLAUDE.md` was removed after the phase, as beat
  33 left it uncommitted.
- **The two planning-only fixtures' registries were four types behind** (`lesson`, `skill`,
  `feedback`, `prompt`): the registry syncs at `package_migrate`, not at open, so G-SET had passed
  vacuously on them. The sync appended one audit journal row each. `minimal-brief` gained `csv/`
  with its re-export (the export writes the CSVs since v4.7).
- **The generated sample's rows carry stem titles** (`initial-prompt`, `follow-up-prompts`,
  `review-prompts`): its files open with a blockquote and no H1. `follow-up-prompts` landed
  situational: the kind rule infers only the kickoff from a name, and a file of several per-phase
  prompts is not one `phase` row. Both are the operator's to fix on Proposed rows, as the design says.
- **The headless server writes a standalone `.mcp.json`** at the workspace root (it is not
  plugin-hosted); the 189 setup removed the same file. Not a defect.
- **Two agent observations taken:** the migrate result does not carry the id of the journal row it
  appends, and an export before the handoff cannot hold the handoff.
- **Four pins re-aimed in this commit:** the resume check (`PE-065` -> `PE-068`, the beat's handoff),
  the handoff count sentence (eleven -> twelve), the guide test's fixture-tree pin (`prompts` ->
  `README.md`), the eval runner's grep-tree test (the package dir, since the folder is gone).
- **The guide gained `review.prompts`** (one id per `SECTIONS` entry) and the Always count moved
  10 -> 11; the D4 label says 12 sections.
- `pkg_check.py` gained no subcommand: `grep-present --tables prompts`, `count --col` and `rule`
  cover the new assertions.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged; the postures accepted (the emitted note removed from the
  fixture dir for parity with beat 33, the T1 words error owned, the sample's rows left Proposed).
- **P19 (P4's rule 1 widened):** the kickoff is the file `entry_point` names, matched by FILE NAME on
  any path prefix (the generated sample's header carried the v2 path `handoff/initial-prompt.md`).
  A dead `.md` entry point that names no converted file is cleared and said. Two tests pin it.
- **P20:** the two recorded planning-only fixtures took the registry sync and one omission row each
  through the server, with a reason true of the fixture, disclosed here and in the lab report. No
  re-recording.

## Validation

- `python check.py`: ALL CHECKS PASSED (12 suites incl. contract 208, export 46, migrate 17,
  round-trip 16, store migrations 11, eval runner 9; 14 lints incl. lint 8 on six version surfaces,
  lint 9 stock history, lint 3 registry Always class 11 types <-> catalog; canonical; the evals:
  minimal-brief, execution-loop, lab-tracker PASS).
- The lab: scratch phase T1 + T1b + T2 (one session, three client processes, $1.33, no denial);
  fixture phase `beat34.py` every assertion; `package_verify` `review_exported_by: "6.0.0"`.
- Pins: 191 in the 198 ledger, 0 missing; 196 and 197 ledgers re-checked after the catalog flip.
- Python 3.10 grammar parse of the ten touched or new `.py` files.
