# Plan 061: Documentation sweep for the shipped behaviors of plans 042–060

> Executed directly by the reviewer (maintainer-delegated, 2026-09-12) after the maintainer
> asked whether every documentation surface had followed the advisor batch. Plan 048 was a
> drift sweep, but it ran before most code plans landed, so no surface outside `plans/` and
> the CHANGELOG had been checked against the batch's shipped behavior.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW (prose only; lint 9b/10 guard the bundle files)
- **Depends on**: 042–060 DONE
- **Category**: docs
- **Planned at**: commit `8934b8b`, 2026-09-12

## Audit method

`git diff --stat 7e3a92b..HEAD -- '*.md'` (24 non-plan files touched by the batch) crossed
with a per-behavior `git grep` over README/SECURITY/CONTRIBUTING/docs/SKILL/references/server
README/evals README/lab README, and a grep of every mermaid block's vocabulary (seven files).
No diagram depicts CI triggers, CSV export, the note screen, scoped readiness or waiver
citation, so no diagram needed a change.

## Gaps found and closed

| Plan | Shipped behavior | Surface silent before | Closed in |
|---|---|---|---|
| 050 | CSV formula-injection guard (`_csv_safe`, CWE-1236) | SECURITY.md, server README | SECURITY.md "Controls in place" bullet; `export_html` row |
| 054 | skill names/levels screened by G-INJECT; note-marker literals defused | handoff.md Lessons bullet | one sentence after the skills line |
| 049 | scoped `acs-met`/`wbs-done`/`slices-closed` read `indeterminate` at zero rows | quality-gates.md (had only the column-level doctrine) | one sentence after "only real `fail` blocks" |
| 056 | ninth suite `test_check_lints.py` | CONTRIBUTING, README tree, tests/README (three "eight" sites, no row) | counts corrected; suite row added |
| 052 | CI matrix 3.10–3.13 × Ubuntu/Windows + `uv` smoke; triggers | CONTRIBUTING | one sentence in the `check.py` bullet |
| 057 | numeric id order in the viewer | server README | `export_html` row |
| 060 | per-entity waiver cited before the whole-rule one | server README | `readiness_check` row |

Covered already by their own plans (checked, not re-edited): 043 (server README, handoff),
044 (SECURITY.md), 045 (docs/migrate-from-keystone), 046 (quality-gates, server README),
051 (SKILL, entities, workflow), 053 (governance, entities, SKILL), 055 (adopt.md).

## Done criteria

- [x] `git grep -n "eight test suites\|eight suites\|eight files" -- '*.md' ':!plans' ':!CHANGELOG.md'` → nothing
- [x] `git grep -l "CWE-1236" -- SECURITY.md plugins/tamheed/server/README.md` → both
- [x] `python check.py lint` → no `FAIL`
- [x] no file under `plugins/tamheed/references/` references a repo-root path (bundle never links out)

### Release discipline

- No `plugin.json` bump; CHANGELOG under `## [Unreleased]`; stamps, stock prompts, goldens untouched.
