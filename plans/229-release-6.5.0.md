# Plan 229 -- acceptance, release 6.5.0, the two field prompts

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- Acceptance on the merged branch: `python check.py`, once more with
  `PYTHONWARNINGS=error::DeprecationWarning`, a scratch script driving the real handlers through
  every changed behaviour, `uv run plugins/tamheed/server/tamheed_server.py --selftest` (21/21,
  descriptions under 2,048), the browser pass of 227, the replay of both fields on scratch copies.
- Release by the 220 recipe: `stamp_650.py` (six version surfaces, the stock guide body with its
  `stock-history.json` key, the lab-tracker pins, the CHANGELOG entry naming both migrations and
  the live-package note), `docs/guide/build.py`, `refresh_lab_650.py`, a lab beat that exercises a
  register and a slate. Then the operator's word: merge, push, `gh workflow run CI`, the tag
  `v6.5.0` on green, the ledger follow-up.
- Records: `plans/221..229`, the `plans/README.md` section, `plans/evidence/` with the fields' private words trimmed (R72).
- **ACMP prompt**: upgrade at project scope, a fresh session, `server_info` quoted. `package_migrate`
  preview then confirm on the operator's word (registry-sync, two families, one column). The
  one-time rewrite of `document_sections.jsonl` committed alone. Probes with expected results:
  `trace_query("FR-166")` shows AC-184 under `column_links`. The census of LL-149 and LL-157 in one
  exported call. `requirements-wired` lists FR-156..159 with `["work"]`, a STOP for the operator
  (a history work item as DEC-499 q2 chose, or a waiver). FB-030, FB-031, FB-032: `Resolved`,
  `resolved_in 6.5.0`, `upstream_ref` the plan URL. What was not built. A failed class is an FB row.
- **Jisr prompt**: the same upgrade. The lock's limits stated (new locks only, not across a restart,
  another machine stays manual). One line that runs the macOS probe through the installed plugin. FB-001, 002, 003, 009,
  011, 004, 005, 006, 007: `Resolved` with plan URLs. FB-003's answer is `Hold`, and GATE-001's outcome is
  the operator's to write. Moving the three registers into the family, and what becomes of the local
  page's FB-008 row, are the operator's calls in Jisr, each put with a recommendation. FB-010's
  script reads the plugin by a versioned cache path: the path moves to 6.5.0.
- Every recipe of both prompts is dry-run on a scratch copy first. The prompts are handed in the
  maintainer session, as for 6.3.0 and 6.4.0.
