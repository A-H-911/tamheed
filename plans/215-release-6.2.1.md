# Plan 215 -- release 6.2.1: one text for both G-COMPLETE scans

> Status: DONE 2026-10-09 UTC (maintainer-executed, the operator's word before the push).
> PATCH: plan 214 is a fix (two scans read one text, both only lose matches). No schema migration:
> `schema_version` stays 8, the store's bytes do not move. The release reaches the field's machine
> only through this stamp: the cached plugin is pinned by `plugin.json`'s version string.

## The stamp (the 213 pattern)

`plans/evidence/scripts-215/stamp_621.py`: `plugin.json` 6.2.1; the prose surfaces' current-version
lines (the root README twice, the server README, the front door, the artifact catalog); the stock
guide's title line with its body appended under `6.2.1` in `stock-history.json` in the same run
(lint 9: stock text lands with its history key); the two lab-tracker eval pins and their check
sentences; the CHANGELOG `## [6.2.1] - 2026-10-09` entry above the 6.2.0 heading. Then
`python docs/guide/build.py` (`index.html` carries the version), then the fixture refresh.

## The fixture (the 213 pattern)

`plans/evidence/scripts-215/refresh_lab_621.py` (the 213 script with the version moved): in-process
(`_WIRE_ROOT` off, so nothing is wired into the fixture tree), `handoff_emit(..., refresh_stock=true)`
to a scratch target carrying the pointer, `export_html`, `package_verify` clean, `gate_run` ready, the
untracked package note removed after. The two planning-only fixtures keep their 6.0.0 guide (G30: no
tool of theirs rewrites it without a kickoff).

## The migration note for a live package

Nothing to run. A package failing G-COMPLETE on a journal row, on verdict evidence or on a marker
inside backticks passes at its next `gate_run` under 6.2.1. The field sets FB-001 `Resolved` with
`resolved_in` 6.2.1 and `upstream_ref` naming plan 214 and the tag.

## The content sweep

Plan 214 carried its own sweep (quality-gates, governance, package-writes, the server README and
docstrings, entities.md, CLAUDE.md). This commit changes the stamp's surfaces only. Grepped and left
alone: `prompts/README.md`'s "Placeholders and the journal" paragraph (true before and after: the
journal was always exempt from the placeholder scan, and is now exempt from both).

## As it landed

(filled: the commit, the push, the CI run, the tag, the bundle diff, the field's two values)

## Rulings taken at the review

- **R73 (2026-10-09): commit, push, tag on CI green, then push the follow-up, on one word.** The
  push carries two commits: 214 (`1d18b74`) and this release. The tag `v6.2.1` goes on the release
  commit when every CI job is green. The follow-up ledger commit ("As it landed") is pushed on the
  same word (R23: one word before any push, asked once for both).

## Validation

- `stamp_621.py`: every surface replaced once, asserted once; the stock guide's body under `6.2.1`
  in `stock-history.json` in the same run; the two lab-tracker pins and their check sentences
  re-aimed (`plans ..., 213, 215`); the CHANGELOG entry above the 6.2.0 heading, dated 2026-10-09 UTC
  (the stamp ran at 11:56 UTC).
- `docs/guide/build.py`: 1,546 ids, 724 figure files, the meta `tamheed-guide 6.2.1`; no figure moved
  on the stamp (plan 214 had already rebuilt the five gate figures with the final lines).
- `refresh_lab_621.py` (in-process, `_WIRE_ROOT` off): `open.wiring null`, `open.half execution`,
  `handoff_emit` `refreshed: ["README.md"]`, `export_html` stamped `6.2.1`, `package_verify`
  `verified: true, dirty: [], foreign: [], review_current: true, review_exported_by: "6.2.1"`,
  `gate_run` ready; the untracked package note removed; the fixture's root carries no `CLAUDE.md`
  before or after. Measured: lab-tracker's guide `tamheed v6.2.1`; execution-loop, minimal-brief and
  the demo sample keep `tamheed v6.0.0` (G30).
- `python check.py`: ALL CHECKS PASSED (`lint: plugin.json 6.2.1 == newest CHANGELOG release`,
  `all 6 version-stamped surfaces carry v6.2.1`, `stock history current (17 files, 109 bodies)`,
  `3 case(s) checked, 0 failed, 6 skipped`). The tree after the gate: the stamp's 15 entries, nothing
  else.
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19, longest description 387.
- The bundle against `v6.2.0`, measured on the working tree (`git diff --stat v6.2.0 -- plugins/tamheed`):
  ten files, 69 insertions, 74 deletions. The server (118 lines moved: the helper and the two loops),
  three teaching files (`governance.md`, `quality-gates.md`, the `package-writes` skill), the server
  README (214's clause and the stamp), and the stamp's other surfaces (plugin.json, the stock guide's
  title line and `stock-history.json`, the catalog, the front door).
