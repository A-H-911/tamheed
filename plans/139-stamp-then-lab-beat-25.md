# Plan 139: the version stamp, then lab beat 25 + evals

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW - **DONE**

## Order, as it ran (the 5.2.0 cycle's lesson 1: a stock body lands WITH its history key, before the beat)

1. **The stamp, in one step**: the lint-8 five (`prompts/README.md`, `references/artifact-catalog.md`,
   `server/README.md`, the front door, `README.md` ×2), `plugin.json`, the CHANGELOG heading
   `[5.3.0] - 2026-09-27`; the FINAL `prompts/README.md` body (title `tamheed v5.3.0`; E3 "every
   successful `entity_query` result") appended under `"5.3.0"` in `stock-history.json` (indent 1, as
   every key before it). `python check.py lint`: plugin.json == newest CHANGELOG release; all 5
   surfaces v5.3.0; stock history current (97 bodies). README frozen from here.
2. F-10: `tests/test_eval_runner.py` reads the fixture's prompts dir only. F-6: `evals.json` re-aimed
   after the beat — `handoff=PE-049 behind=0`, the guide's `tamheed v5.3.0`, four handoffs.
3. **Beat 25** (`lab/scenario.md` item 25; harness `beat25.py`): phase A on the fixture — the
   observed lock on `package_open`/`server_info` (`alive` / `held by this session`), the guide
   refreshed to 5.3.0, the note `PE-048`, the handoff `PE-049` LAST, `export_html`, `gate_run` ready,
   `package_verify` green, `package_close`. Phase B on a scratch copy — the render hint on an unpinned
   and a pinned approval, the hook over a dead-pid lock (`holder observed not-running —
   package_unlock(confirm=true) on the operator's word`; nothing removed), the trace (missing path →
   nothing; existing file → one counts-only line whose counts equal the printed block's; unset →
   nothing more). Evidence:
   [`evidence/lab-continuation-report-139-2026-09-27.md`](evidence/lab-continuation-report-139-2026-09-27.md).
4. **Evals**: three assertions added (the note quotes the observed holder, the trace, the render hint).
5. **The fixture regolden**: the beat's own writes (`data/`, `csv/`, `review.html`, the refreshed
   guide) through the store and `export_html`; the canonical gate proves an idle open→close writes
   nothing.

## Execution miss owned

The first run's phase B ran the hook on a copy that carried no `package/CLAUDE.md` — the note the hook
reads is written only by a pointer-target emit, which beat 24's harness had run and this one had not.
The hook printed nothing (its guard), the harness stopped, and phase A had already written to the
fixture. The fixture was restored from git, the harness gained the pointer emit, and the whole beat
was re-run from the restored fixture: every class held on the second run.
