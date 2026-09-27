# Plan 139: the version stamp, then lab beat 25 + evals

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW - **PLANNED**

## Order (the 5.2.0 cycle's lesson 1: a stock body lands WITH its history key, before the beat)

1. Stamp 5.3.0: the lint-8 five, `plugin.json`, the CHANGELOG heading; the FINAL `prompts/README.md`
   body (title `tamheed v5.3.0`; E3 "every successful `entity_query` result") appended under `"5.3.0"`
   in `stock-history.json`. README frozen from here.
2. F-10 grep of `tests/` for fixture readers; F-6: `evals.json` `handoff=PE-047` re-aimed after the beat.
3. `lab/scenario.md` item 25 — on the SCRATCH copy: an unpinned lesson Approved → the hint names the
   10-newest rule; a pinned one → "always render"; a lock naming a dead pid → the hook prints
   `holder observed not-running` and `package_unlock(confirm=true)`; the hook with `TAMHEED_HOOK_LOG`
   naming an existing file → one counts-only line, a missing path → nothing; `package_open` on the
   copy → `lock.observed alive`, `held by this session`. On the fixture: one note (actor
   `agent:lab-beat-25`), the final handoff LAST, `export_html`, `gate_run`, `package_verify` green,
   `package_close`. Evals: `handoff=PE-049 behind=0`; grep-present for the note's quotes.
4. Evidence `plans/evidence/lab-continuation-report-139-<date>.md`; fixture regolden by script;
   `python check.py` green.
