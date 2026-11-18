# Plan 253 — the 6.8.0 field briefs: measured and rehearsed (2026-11-18)

The briefs: `plans/briefs/acmp-6.8.0.md` and `plans/briefs/jisr-6.8.0.md`. Counts and names
only: no field row text.

## The measurements (`scripts-253/measure_253.py`, `wayback_253.py`, `fb023_253.py`)

Scratch copies of ACMP `4b727edf` (`git archive`) and of Jisr's export of `63896cf2`. Each ran
under the v6.7.0 tag's bundle and under the 6.8.0 bundle.

| | Jisr 6.7.0 → 6.8.0 | ACMP 6.7.0 → 6.8.0 |
|---|---|---|
| Engine | migration `012_standup_withdraw.sql`, schema 12 in both | same |
| Files moved by the open | none | none |
| Gate and readiness | `false`/`false` (acs-met, adrs-approved, risks-discharged), unchanged | `true`/`true`, unchanged |
| Restated lines | 3 → 3 | 0 → 0 |
| Moved by emit and export (6.8.0) | `CLAUDE.md`, `README.md`, `review.html` (+ `.mcp.json` from the local plugin folder) | same three |
| First-report draft row | 127 KB → 314 KB | 356 KB → 770 KB |
| Draft page | 180 KB → 566 KB | 480 KB → 1.15 MB |
| Suggested slices | now SL-008, next SL-009 | now SL-043, no next |
| FB-023: "Awaiting the operator" lines in the latest handoff | 1, with a "Rulings given" sentence. 6.8.0 shows the part before it | same |

**The way back.** On the Jisr copy, 6.8.0 recorded a report (scripted operator, scratch only).
Then 6.7.0:
- opened the store and verified it clean;
- read the gates as before;
- regenerated the report in its 6.7.0 look (180 KB, no script);
- drafted the next report on top of it as a daily report.

**Field facts the briefs use:**
- Jisr's FB-023 and FB-024 are `Reported`.
- ACMP's own FB-023 and FB-024 are other rows, already `Resolved`.
- ACMP's committed guide is still stamped 6.6.0.
- Neither field pins a marketplace `ref`.

## The rehearsals (`scripts-253/rehearse_680.py`)

Each brief ran in two headless sessions: the first under the 6.7.0 bundle, then a second, new
process under 6.8.0 that stands in for the restart. Scripted answers stood in for the operator.
Each session was capped at 2 USD.

| Run | Result |
|---|---|
| First pass (void) | The rehearsal harness lacked the "one plain command per shell call" note. The agents chained their git calls, and the allowlist refused every one. 1.87 USD. Nothing in the briefs changed |
| ACMP | 6.7.0 session: the reading taken, stopped at the restart (0.42 USD). 6.8.0 session: re-entry from the PRE file, classes 1–4 hold, the stray `.mcp.json` removed, one commit of exactly the three files (0.66 USD) |
| Jisr | 6.7.0 session: the reading taken, stopped at the restart (0.48 USD). 6.8.0 session: classes 1–5 hold, one commit of the three files, then FB-023 and FB-024 `Resolved` in a second commit (0.94 USD) |

**Not rehearsed:**
- Step 2.1.6 (`claude plugin list`): the harness allows no `claude` command.
- The real plugin update and the real restart: the scripted answers treat both as done.
- Jisr's offer 3.1 (a first report): declined in the script.
- Safari: nothing here ran on a Mac.

**Noted by the agents, outside the briefs:**
- The `upstream_ref` of Jisr's two rows is replaced by the plan URL, as in the 6.7.0 brief.
- On Jisr's copy, `gate_run` counts one id more than its latest handoff states.
