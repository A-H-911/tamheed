# Plan 168: the 5.8.0 stamp with its history key, then lab beat 31 and four eval assertions

> Maintainer-executed, 2026-09-30. Batch map: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## Steps, in order

0. **The stamp first** (F-4/F-5: stamp before the beat, so the beat's refresh lands the shipped
   body). The five lint-8 surfaces moved from `5.7.0` to `5.8.0` (`plugin.json`, the guide's
   title, the artifact catalog, the server README, the front door, the README twice) and the
   guide's new body landed in `stock-history.json` under `"5.8.0"` — its title the only line
   changed (asserted). The changelog's entry left `[Unreleased]` for `[5.8.0] - 2026-09-30`.
   The stamp script stopped once on its changelog line (a heredoc had kept plan 163's needle);
   the six surfaces were already stamped and the two remaining steps ran by hand, asserted.
1. F-6 / F-10 greps: the evals name `PE-059`, `tamheed v5.7.0`, the `5.7.0` stamp and nine
   handoffs; the tests name no fixture file the beat touches.
2. **Beat 31**, `beat31.py`, the scratch phase first with hard assertions — the rule passes on
   the fixture's journal, fails on three handoffs sharing a line (naming the first's id and the
   line's number, not the heading or the short line, and no line's text), passes again after a
   re-measured fourth; the first export re-flows the page and equals the 5.7.0 engine's render
   of the same store on the same date once the newlines between tags are removed — then the
   fixture by R43's order. Held on its first run (18:57:06–18:57:09Z). Report:
   [`evidence/lab-continuation-report-168-2026-09-30.md`](evidence/lab-continuation-report-168-2026-09-30.md).
3. The evals: four re-aimed by script, four added (169 checks). `python check.py` green.

## What the fixture carries now

`PE-060` (the note), `PE-061` (the handoff); the page stamped `5.8.0`, dated `2026-09-30`,
re-flowed once (295 → 1,088 lines; `git diff --numstat` `815 22`); the guide at the 5.8.0 stock.
