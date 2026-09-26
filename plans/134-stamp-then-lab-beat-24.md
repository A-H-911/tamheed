# Plan 134: the version stamp, then lab beat 24 + the evals

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW (the stamp precedes the beat — lesson 2 of the last cycle held)

## Order, and why

1. **Stamp first**: `plugin.json` 5.2.0; the five lint-8 surfaces (`README.md` ×2, `server/README.md`,
   `prompts/README.md`, the front door, `artifact-catalog.md`); CHANGELOG `## [5.2.0] - 2026-09-26`
   with its MINOR paragraph (an empty `[Unreleased]` above it); the guide's own 5.2.0 text (the
   marker "verified against the bundled history"; the cue list naming `entity_query` and
   `handoff_emit`) and its body appended under `"5.2.0"` in `stock-history.json` — lint 9 requires
   the shipped guide to equal its newest key, which is why plan 129's guide wording waited here.
2. **F-10**: `tests/test_eval_runner.py:96` is the only fixture reader (its prompts dir; untouched).
   **F-6**: `evals.json`'s `handoff=PE-044 behind=0` re-aimed to `PE-047`; the 5.1.0 guide assertion
   kept (still true) and a 5.2.0 one added.
3. **Beat 24** (`lab/scenario.md` item 24; harness `beat24.py`): phase A on the fixture — the
   `entity_query` cue, the partial-row retirement of `SKL-001` behind `tamheed:reading-the-record`
   journalled by `system:skill-guard` (`PE-045`), `lessons-stranded` over `promoted lessons`,
   `handoff-current` behind by exactly that row, the idle re-send, `refresh_stock` to the 5.2.0
   guide, the note without a block, the beat's note `PE-046` and the final handoff `PE-047`;
   phase B on a copy — the export without a cue, the false marker over the 5.0.0 body
   (`missing_by_release {"5.1.0": 11}`), the stale skill sentence behind a pointer (the block in
   the package file, the root constant, the warning's three sentences, the byte-identical restore),
   the hook over `PE-047` after a compaction. Evidence:
   [`evidence/lab-continuation-report-134-2026-09-26.md`](evidence/lab-continuation-report-134-2026-09-26.md).
4. **Evals**: five assertions added (the 5.2.0 guide; the guard's row text; the beat note's
   "a population of promoted lessons"; ≥ 3 handoffs; "promoted lessons" in review.html — U3
   measured: the readiness table prints `population`).
5. **The fixture regolden**: the beat's own writes (`data/`, `csv/`, `review.html`, the refreshed
   guide) through the store and `export_html`; the canonical gate proves an idle open→close writes
   nothing.

## Execution miss owned

The first run's phase B re-Approved the lab skill AFTER the clean emit it compared against, so
"bytes restored" read false for the right reason (the note's span had legitimately changed) and the
pointer warning read "was rebuilt there". The fixture was restored from git and the beat re-run with
the re-Approve before the clean emit; the scenario text was corrected to what the engine says.
