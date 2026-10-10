# Plan 218 -- release 6.3.0: the flush that reports, tamheed per repository

> Status: DONE 2026-10-10 UTC (maintainer-executed, the operator's word before the push).
> MINOR (R75): plan 217 adds result keys on a failed write, `unflushed` on close, a `warning` on
> open, two new file kinds under `data/` and a changed write set. No schema migration:
> `schema_version` stays 8, the store's bytes do not move. The release reaches a repository only
> through this stamp and its own `claude plugin update tamheed@tamheed --scope project`.

## The stamp (the 213/215 pattern)

`plans/evidence/scripts-218/stamp_630.py`: `plugin.json` 6.3.0; the prose surfaces' current-version
lines (the root README twice, the server README, the front door, the artifact catalog); the stock
guide's title line with its body appended under `6.3.0` in `stock-history.json` in the same run
(lint 9); the two lab-tracker eval pins and their check sentences; the CHANGELOG `## [6.3.0] -
2026-10-10` entry above the 6.2.1 heading, with the migration note. Then `python docs/guide/build.py`
(`index.html` carries the version), then the fixture refresh.

## The fixture (the 213/215 pattern)

`plans/evidence/scripts-218/refresh_lab_630.py` (the 215 script with the version moved, diffed, and
grepped for the old plan number and version): in-process (`_WIRE_ROOT` off), `handoff_emit(...,
refresh_stock=true)` to a scratch target carrying the pointer, `export_html`, `package_verify` clean,
`gate_run` ready, the untracked package note removed after. The two planning-only fixtures and the
demo sample keep their 6.0.0 guide (G30).

## The migration note for a live package

Nothing to run. A package that saw a partial flush flushes the pending file at its next write. A
`.unflushed` sidecar left by an earlier close is named at `package_open` until the operator
reconciles it. The field sets FB-029 `Resolved` with `resolved_in` 6.3.0 and the plan 217 reference.
The install posture: per repository, nothing at user level (plan 216).

## The content sweep

Plans 216 and 217 carried their own sweeps. This commit changes the stamp's surfaces only, and the
plans index rows for 216 and 217 gain their commit SHAs. Grepped and left alone: the stock guide's
"Placeholders and the journal" paragraph (true before and after).

## As it landed

- The release commit `68a0874`; `git push origin main` `64ce9de..68a0874` on 2026-10-10 (three
  commits: `ba613ec` plan 217, `3305d1e` plan 216, `68a0874` this release).
- CI run 38042777874 on `68a0874`: conclusion success, 9 jobs, every job success (eight `check`
  jobs over Python 3.10 to 3.13 on Windows and Ubuntu, the symlink test running on Ubuntu, and
  the MCP server smoke). The watcher polled `gh run list --commit` with the short SHA, which
  matches nothing, so the green run was found by hand: the lesson is in the batch memory.
- Tag `v6.3.0` on `68a0874`, pushed. `git diff v6.3.0 HEAD -- plugins/tamheed`: 0 lines.
- The machine after the release: `claude plugin marketplace update tamheed` (clone at 6.3.0),
  the tamheed repository's local record `6.2.1 -> 6.3.0`; M3 repeated at 6.3.0 in the scratch
  folder (`install --scope project` -> a project record at 6.3.0, the session loaded 6.3.0,
  `uninstall --scope project` after). One record remains: the tamheed repository, local, 6.3.0.
- The field's values. ACMP FB-029: `resolved_in` `6.3.0`, `upstream_ref`
  `https://github.com/A-H-911/tamheed/blob/main/plans/217-flush-only-what-changed.md` (tag
  `v6.3.0`, commit `68a0874`). jisr FB-001 keeps `resolved_in` `6.2.1`. Both repositories install
  their own record with the two prompts handed in the maintainer session.

## Rulings taken at the review

- **R77 (2026-10-10): commit, push, tag on CI green, then push the follow-up, on one word.** The
  push carries three commits: 217 (`ba613ec`), 216 (`3305d1e`) and this release. The tag `v6.3.0`
  goes on the release commit when every CI job is green. The follow-up ledger commit ("As it
  landed") is pushed on the same word (R23, asked once for both). The staged bundle diff against
  `v6.2.1` was re-measured before the commit: 11 files, 209 insertions, 43 deletions.

## Validation

- `stamp_630.py`: every surface replaced once, asserted once; the stock guide's body under `6.3.0` in
  `stock-history.json` in the same run; the two lab-tracker pins and their check sentences re-aimed
  (`plans ..., 215, 218`); the CHANGELOG entry above the 6.2.1 heading, dated 2026-10-10 UTC, saying
  five attempts with four sleeps of 50 to 400 ms (the code's numbers, not the plan's 800).
- `docs/guide/build.py`: 1,546 ids, 724 figure files, the meta `tamheed-guide 6.3.0`; no figure moved
  on the stamp.
- `refresh_lab_630.py` (derived from the 215 script: the diff shows the version, the plan number, the
  temp prefix and the done line only; a grep for "215" and "6.2.1" finds nothing): `open.wiring null`,
  `open.half execution`, `handoff_emit` `refreshed: ["README.md"]`, `export_html` stamped `6.3.0`,
  `package_verify` `verified: true, dirty: [], foreign: [], review_current: true, review_exported_by:
  "6.3.0"`, `gate_run` ready; the untracked package note removed; the fixture's root carries no
  `CLAUDE.md`. Measured: lab-tracker's guide `tamheed v6.3.0`; execution-loop, minimal-brief and the
  demo sample keep `tamheed v6.0.0` (G30).
- `python check.py`: ALL CHECKS PASSED (`lint: plugin.json 6.3.0 == newest CHANGELOG release`,
  `CHANGELOG 53 releases strictly newest-first`, `all 6 version-stamped surfaces carry v6.3.0`,
  `stock history current (17 files, 110 bodies)`, `3 case(s) checked, 0 failed, 6 skipped`).
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19, longest description 387.
- The bundle against `v6.2.1`, measured on the working tree (`git diff --stat v6.2.1 -- plugins/tamheed`):
  eleven files, 209 insertions, 43 deletions. The store (141 lines), the server (68), `CANONICAL.md`,
  the two skills, the server README, and the stamp's surfaces (plugin.json, the stock guide's title
  line and `stock-history.json`, the catalog, the front door).
