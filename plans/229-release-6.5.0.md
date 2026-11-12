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
  the live-package note), `docs/guide/build.py`, `refresh_lab_650.py` (it also re-exports the lab fixture's recorded
  `gates.json`, whose wired-rule note plan 222 changed), a lab beat that exercises a
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
  another machine stays manual, and the memory-snapshot limit of R91). One line that runs the macOS probe through the installed plugin. FB-001, 002, 003, 009,
  011, 004, 005, 006, 007: `Resolved` with plan URLs. FB-003's answer is `Hold`, and GATE-001's outcome is
  the operator's to write. Moving the three registers into the family, and what becomes of the local
  page's FB-008 row, are the operator's calls in Jisr, each put with a recommendation. FB-010's
  script reads the plugin by a versioned cache path: the path moves to 6.5.0.
- Every recipe of both prompts is dry-run on a scratch copy first. The prompts are handed in the
  maintainer session, as for 6.3.0 and 6.4.0.

## Owed to this plan by the earlier ones (added as they landed)

- From 225: the CHANGELOG holds an `[Unreleased]` section that names the migrations. The 6.4.0
  stamp inserted its entry above the newest release heading. A stamp derived from it must
  REPLACE the `[Unreleased]` block with the 6.5.0 entry, or the block stays above the release.
- From 225: the fixtures rewrote `document_sections.jsonl`, so their recorded pages, CSVs and
  exports lag the data. `package_verify` on the lab fixture reads `verified: true`, `dirty: []`,
  `review_current: false`, `review_exported_by: 6.4.0`. The fixture refresh re-exports them.
- From 224a: the stock guide `prompts/README.md` names the lock outcomes. Its body is pinned by
  `stock-history.json`, so its lock paragraph changes with the history key at the stamp.
- From 222: the lab fixture's recorded `gates.json` keeps the old wired-rule note until the refresh.
- From 222, owed to 228: the review page's readiness table does not show a rule's `missing` legs.
- For the Jisr prompt, measured on the export of 2026-11-12: its two review scripts read rows
  by key, so the new `lifecycle_status` key in every section row does not break them. One of
  them skips bank rows whose `custom_attributes.kind` is `superseded`. Two section rows carry
  that mark. One was retired with the typed status on a scratch copy, and every gate kept its status.

## As built: acceptance and the stamp (2026-11-12)

Acceptance on the branch, at the stamped tree:

| Check | Result |
|---|---|
| `python check.py` on Python 3.13 | passes, thirteen suites |
| `python check.py` on Python 3.10 | passes |
| the same with deprecation warnings as errors | passes |
| the selftest | 21 of 21 tools, longest description 677 characters |
| `scripts-229/acceptance_650.py`, one scenario through plans 221 to 228 | 21 observations hold |
| the first field's package on a scratch copy | the sync moves three files, verifies clean |
| the second field's 620 register rows | all admitted with fitted declarations, gates equal |
| the second field's question bank through the slate tools | 75 and 227 questions, store verifies |

The stamp (`scripts-229/stamp_650.py`): six version surfaces, the stock guide's two new
paragraphs with its history key, the lab-tracker pins, and the changelog. The `[Unreleased]`
block is REPLACED by the 6.5.0 entry, which names both migrations and carries the note for a
live package. The fixture refresh (`refresh_lab_650.py`) ran the engine over the lab fixture:
the stock guide, the review page, one CSV and the recorded gate report follow the release.

Deviation from this plan, stated to the operator with the commit question: no register and no
slate were written into the recorded lab fixture. The acceptance scenario exercises both on a
package made for the run. The fixtures stay packages written before 6.5, which is a tested
state: such a package is told the route at its first register write.

Still open at this point: a person clicks Save on an interview page once, the merge and the tag
on the operator's word, and the two field prompts.
