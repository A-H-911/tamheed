# Plan 220 -- release 6.4.0: the review page reads

> Status: DONE 2026-10-10 UTC (maintainer-executed, the operator's word before the push).
> MINOR: plan 219 changes what the page renders (a `<colgroup>` per table, new stylesheet rules), an
> additive surface by the repository's rule and the operator's ask. No schema migration:
> `schema_version` stays 8, the store's bytes do not move. Two releases carry this UTC date: 6.3.0
> landed earlier on 2026-10-10 (`68a0874`), this one after it.

## The stamp (the 213/215/218 pattern)

`plans/evidence/scripts-220/stamp_640.py`: `plugin.json` 6.4.0; the prose surfaces' current-version
lines (the root README twice, the server README, the front door, the artifact catalog); the stock
guide's title line with its body appended under `6.4.0` in `stock-history.json` in the same run (lint
9); the two lab-tracker eval pins and their check sentences; the CHANGELOG `## [6.4.0] - 2026-10-10`
entry above the 6.3.0 heading (the `head` anchor occurs once although the dates match), with the
migration note and the one line for a contributor who clones the plugin's own repository (R79). Then
`python docs/guide/build.py` (`index.html` carries the version), then the fixture refresh.

## The fixture (the 213/215/218 pattern)

`plans/evidence/scripts-220/refresh_lab_640.py` (the 218 script with the version moved, diffed, and
grepped for the old plan number and version): in-process (`_WIRE_ROOT` off), `handoff_emit(...,
refresh_stock=true)` to a scratch target carrying the pointer, `export_html` (the lab-tracker page is
the one recorded fixture page that follows the release, and this release changes every table's
markup, so its diff is the page's one-time re-render), `package_verify` clean, `gate_run` ready, the
untracked package note removed after. The two planning-only fixtures and the demo sample keep their
6.0.0 guide (G30); minimal-brief's recorded page stays as every release has left it.

## The migration note for a live package

Nothing to run. One `export_html()` under 6.4.0 re-renders the page. The two upgrade prompts do that
and nothing else on the package.

## As it landed

- The release commit `3745944`; `git push origin main` `49454c0..3745944` on 2026-10-10 (two
  commits: `4b3dc37` plan 219, `3745944` this release).
- CI run 38076705513 on `3745944`: conclusion success, 9 jobs, every job success (eight `check`
  jobs over Python 3.10 to 3.13 on Windows and Ubuntu, and the MCP server smoke). The watcher
  polled `gh run list --commit` with the full SHA this time and saw the run.
- Tag `v6.4.0` on `3745944`, pushed. `git diff v6.4.0 HEAD -- plugins/tamheed`: 0 lines.
- The machine after the release: `claude plugin marketplace update tamheed` (clone at 6.4.0),
  the tamheed repository's project record `6.3.0 -> 6.4.0` (R79: a project record, so
  `--scope project`). ACMP's and jisr's records stay 6.3.0 until the operator runs the two
  prompts handed in the maintainer session.

## Rulings taken at the review

- **R80 (2026-10-10): commit, push, tag on CI green, then push the follow-up, on one word.** The
  push carries two commits: 219 (`4b3dc37`) and this release. The tag `v6.4.0` goes on the release
  commit when every CI job is green. The follow-up ledger commit ("As it landed") is pushed on the
  same word (R23, asked once for both). The staged bundle diff against `v6.3.0` was re-measured
  before the commit: 8 files, 60 insertions, 12 deletions.

## Validation

- `stamp_640.py`: every surface replaced once, asserted once; the stock guide's body under `6.4.0`
  in `stock-history.json` in the same run; the two lab-tracker pins and their check sentences
  re-aimed (`plans ..., 218, 220`); the CHANGELOG entry above the 6.3.0 heading (the shared date
  named in the entry). One correction before the first run: a CSS brace pair inside the entry's
  f-string (`tbody tr { scroll-margin-top }`) had to be doubled, which Pyright caught before Python.
- `docs/guide/build.py`: 1,546 ids, 724 figure files, the meta `tamheed-guide 6.4.0`; no figure
  moved on the stamp.
- `refresh_lab_640.py` (derived from the 218 script: 14 differing lines, the version, the plan
  number, the temp prefix and the done line; a grep for "218" and "6.3.0" finds nothing): `open.wiring
  null`, `open.half execution`, `handoff_emit` `refreshed: ["README.md"]`, `export_html` stamped
  `6.4.0`, `package_verify` `verified: true, dirty: [], foreign: [], review_current: true,
  review_exported_by: "6.4.0"`, `gate_run` ready; the untracked package note removed; the fixture's
  root carries no `CLAUDE.md`. The recorded lab-tracker page now carries 47 `<colgroup>` elements,
  one per table: the one-time re-render this release brings. Measured: lab-tracker's guide `tamheed
  v6.4.0`; execution-loop, minimal-brief and the demo sample keep `tamheed v6.0.0` (G30).
- `python check.py`: ALL CHECKS PASSED (`lint: plugin.json 6.4.0 == newest CHANGELOG release`,
  `CHANGELOG 54 releases strictly newest-first`, `all 6 version-stamped surfaces carry v6.4.0`,
  `stock history current (17 files, 111 bodies)`, `3 case(s) checked, 0 failed, 6 skipped`).
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19, longest description 387.
- The bundle against `v6.3.0`, measured on the working tree (`git diff --stat v6.3.0 -- plugins/tamheed`):
  eight files, 60 insertions, 12 deletions: `export_html.py` (41 lines), `viewer.css` (18), and the
  stamp's six surfaces (plugin.json, the stock guide's title line and `stock-history.json`, the
  catalog, the server README, the front door).
