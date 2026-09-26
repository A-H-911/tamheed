# Plan 127: the version stamp first, then lab beat 23 + the evals

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW once the order is right (memory lesson 2: the
  stamp and the guide's history key land BEFORE the beat refreshes the fixture)

## Steps

1. **Stamp** (done first, one commit with the beat): `plugin.json` 5.1.0; the five lint-8 surfaces
   (`README.md` tagline + version line, `server/README.md`, the front door `SKILL.md:21`,
   `artifact-catalog.md:1`, `prompts/README.md:1`); CHANGELOG heading `## [5.1.0] - 2026-09-26`
   under a fresh `[Unreleased]`; the guide's final body (eight discipline skills, the
   session-handoff row, the hook note on the orient-resume row) appended to `stock-history.json`
   under `"5.1.0"`. Lint green before the beat.
2. **F-10**: `tests/test_eval_runner.py:96` greps the fixture's guide for `Which skill, when` —
   still carried by the 5.1.0 body; `test_check_lints.py` ignores `sample-results`.
3. **Beat 23** (`lab/scenario.md` item 23; `lab/README.md`), fired in-process through the engine's
   tool functions (the same code path the MCP tools call; tamheed's MCP tools are not enabled in
   this repo's session until plan 128's local enable takes effect after a restart). Phase A on the
   fixture; phase B on a scratch copy (never committed). Evidence:
   [`evidence/lab-continuation-report-127-2026-09-26.md`](evidence/lab-continuation-report-127-2026-09-26.md).
4. **Evals**: `pkg_check.py` gains `resume` and `rule`; seven lab-tracker assertions added.

## Done criteria

- [ ] `python check.py` green (suites, lints, canonical, evals incl. the seven new assertions)
- [ ] the fixture's guide is byte-equal to the 5.1.0 history body (the refresh proves it)
- [ ] M4 recorded in the batch record (the model-visible listing on the final bundle)
