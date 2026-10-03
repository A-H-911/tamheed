# Plan 189: stamp 5.9.0, the evals re-aimed, `ste-clean`, lab beat 33

> Maintainer-executed, 2026-10-04. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R10 (MINOR 5.9.0 with a migration note), R14 (evals re-aimed, lab beat 33, the
> deterministic `ste-clean` assertion), R24 (one rubric line on lab-tracker and execution-loop),
> R41 (a wave may name 5.9.0 before the stamp). The approved deviation from R14's letter: the
> rewrite skill runs on a SCRATCH copy, and only `handoff_emit(refresh_stock=true)` + `export_html`
> run on the lab fixture, so the rows about 60 eval assertions grep stay untouched.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (a real-agent run; the fixture's page re-flows; six version surfaces) - **DONE 2026-10-04** (the commit this ledger lands in, after the operator's review)

## Scope, in order (the stamp BEFORE the beat)

1. **Stamp.** `plugin.json` 5.9.0. `CHANGELOG.md`: the Unreleased bullets become `## [5.9.0] -
   2026-10-03` (UTC, R46) with the MINOR headline and the migration note (no schema migration, `schema_version`
   7; the note rebuilt as v6 by `refresh_stock`; `/tamheed:ste-rewrite` opt-in; the hook reads v5 and
   v6). The six lint-8 surfaces (root README ×2 lines, server README, prompts README, the front door,
   the artifact catalog, `index.html` by rebuild). The stock README body under `stock-history.json`'s
   `5.9.0` key is the stamped file (lint 9).
2. **`evals/pkg_check.py ste-clean <package>`**: every `<package>/prompts/*.md` byte-equal to a stock
   body after the `{package}` substitution the server performs is linted strict with the bundle
   vocabulary; exit 1 on any hard finding; non-stock files are skipped and named.
3. **`evals/evals.json`**: `tamheed v5.8.1` → `tamheed v5.9.0`, the page's `tamheed-version` meta
   → 5.9.0, "eight **discipline skills**" → nine (the 5.9.0 body names nine), the new deterministic
   assertion `ste-clean` on lab-tracker (`expect_exit 0`), one rubric line on lab-tracker and on
   execution-loop (R24).
4. **Lab beat 33** (`lab/scenario.md`, written in plain English): the scratch phase first, by a real
   agent through the headless harness (`plans/evidence/scripts-fb028/labrun.py`): `/tamheed:ste-rewrite
   package` on a copy of the fixture outside the repository, one in-place rewrite and one supersession
   rehearsed there, no fixture row written. Then on the fixture, in-process through the working-tree
   server (the beat-32 pattern): `handoff_emit(<scratch>, refresh_stock=true)` reports the README
   refreshed to the 5.9.0 body and the note as v6; the closing note (`agent:lab-beat-33`) quotes the
   readiness rule's counts; the handoff LAST; `export_html`; `gate_run`; `package_verify()` green with
   `review_exported_by: "5.9.0"`; `package_close`.
5. The fixture refreshed by the beat (README 5.9.0 body, `review.html` 5.9.0, the closing note), the
   continuation report `plans/evidence/lab-continuation-report-189-2026-10-04.md`, the headless run's
   outputs under `plans/evidence/scripts-ste/labrun-189/`.

## Pins
`CHANGELOG`'s `[Unreleased]` bullets from plan 175 are absorbed into the 5.9.0 entry (the batch record
says so). The eval-spec workflow lint needs `check` + `cmd` + `expect_exit` on the new assertion.

## What the beat found (and changed)

The real agent stopped at batch 1 on a question the skill did not answer: the path for an Approved
row of a family with no supersession column (FR, NFR, ASM, DEC). It recommended in place, Approved,
`expect_unchanged`. The operator's word in T2 took that path, and the skill now states it (step 3
and step 6), plus two more sentences the run exposed: a Promoted lesson is skipped by default like an
Approved one, and the latest handoff entry is never edited (it leaves the rule when the session writes
its own handoff). `skills/ste-rewrite/SKILL.md` stays strict-clean (659 words, 0 hard).

## Results

| Surface | Before | After |
|---|---|---|
| Six lint-8 surfaces | v5.8.1 | v5.9.0 (`lint: all 6 version-stamped surfaces carry v5.9.0`) |
| CHANGELOG | Unreleased bullets | `## [5.9.0] - 2026-10-03` (UTC, R46) + the migration note; 48 releases newest-first |
| Stock README history | `5.9.0` key held the 5.8.1 title | the stamped body (lint 9: 17 files, 105 bodies) |
| Fixture `prompts/README.md` | `tamheed v5.8.1`, eight discipline skills | `tamheed v5.9.0`, nine discipline skills |
| The note (emitted into the package's own `CLAUDE.md` because the target pointed at it) | `tamheed:note v5` (beat 32's scratch) | `tamheed:note v6`, first sentence names the package; the file removed before the commit (it carries an absolute path), the fixture holds no note as before |
| Eval resume pin | `handoff=PE-063 behind=0` | `handoff=PE-065 behind=0` (the beat's handoff) |
| Fixture `review.html` | exported by 5.8.1, 2026-09-30, 1,094 lines | exported by 5.9.0, 2026-10-03 (UTC), 1,101 lines |
| `prose-plain-english` on the fixture | fail, 14 semicolons + 7 long sentences, 36 texts | fail, 13 semicolons + 7 long sentences, 36 texts: the beat's own handoff (plain English) replaced PE-063 in the rule's population; the register rows keep theirs (the rewrite is the operator's choice) |
| Scratch copy after the agent's two writes | 14 / 7 | 10 / 6, `adrs-approved` pass over 2 rows |
| `ste-clean` on the fixture | 1 (the 5.8.1 body, 73 hard) | 0 hard over `README.md`; `project-kickoff.md` skipped by name |
| Eval spec | 168 assertions | 169 assertions, 9 cases well-formed (the CI lint, run locally) |

The headless run: session `c3d04d2d-2e6f-4204-9808-d63220cbfb7a`, T1 23 turns $0.77, T2 21 turns
$1.51, no permission denial, the hook on both turns (`version=5.9.0`, `source=startup` then `resume`).

## Validation
- Red: `tests/test_eval_runner.py` with the re-aimed assertions on the pre-beat fixture (README still
  the 5.8.1 body); lint 8 until every surface carries 5.9.0.
- Green: `python check.py`; `python evals/run_evals.py --results-dir evals/sample-results`; the lab
  report quotes the v6 note and the refreshed README's first line.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- R45: an Approved row of a family with no supersession column is rewritten in place and stays Approved,
  only while the change is punctuation or a sentence split. The Promoted-lesson default and the
  handoff-entry sentence ride on it.
- R46: a release entry carries the UTC date, as earlier releases; `[5.9.0] - 2026-10-03`.
