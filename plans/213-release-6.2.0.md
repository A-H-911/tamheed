# Plan 213 -- release 6.2.0: the repository wired at birth

> Status: DONE 2026-10-08 UTC (maintainer-executed, the operator's word before the push).
> MINOR: plan 212 is additive (a new write at the package's birth and at open, a new result key, a new
> field in the resume block). No schema migration: `schema_version` stays 8, the store's bytes do not
> move. The release reaches the operator's machine only through this stamp: the cached plugin is
> pinned by `plugin.json`'s version string.

## The stamp (the 210 pattern)

`plans/evidence/scripts-213/stamp_620.py`: `plugin.json` 6.2.0; the prose surfaces' current-version
lines (the root README twice, the server README, the front door, the artifact catalog); the stock
guide's title line with its body appended under `6.2.0` in `stock-history.json` in the same run
(lint 9: stock text lands with its history key); the two lab-tracker eval pins and their check
sentences; the CHANGELOG `## [6.2.0] - 2026-10-08` entry above the 6.1.0 heading. Then
`python docs/guide/build.py` (`index.html` carries the version), then the fixture refresh.

## The fixture (the 210 pattern)

`plans/evidence/scripts-213/refresh_lab_620.py`: in-process (`_WIRE_ROOT` off, so nothing is wired
into the fixture tree), `handoff_emit(..., refresh_stock=true)` to a scratch target carrying the
pointer, `export_html`, `package_verify` clean, `gate_run` ready, the untracked package note removed
after, as 210 did. The two planning-only fixtures keep their 6.0.0 guide, measured
(`grep -o 'tamheed v6\.[0-9]\.0' evals/sample-results/*/package/README.md`: execution-loop and
minimal-brief 6.0.0, lab-tracker 6.2.0; the generated sample 6.0.0). G30: no tool of theirs
rewrites it without a kickoff.

## The migration note for a live package

Nothing to run. The first `package_open` under 6.2.0 in a repository without a Tamheed section in
its root `CLAUDE.md` writes the pointer section (a stub when the file is absent) and the package's
own `CLAUDE.md` with the planning note, once; the result's `wiring` names what moved. A repository
already carrying the pointer or an inline note reads `present/present` and nothing is written.

## The content sweep (the release contract, not a version bump)

Three sentences the mechanism made false, fixed in this commit: `adopt.md` "never writes outside
the new package directory" (the confirm now writes the root pointer section); `modes.md` "`plan`
and `intake` must be side-effect-free outside the package directory" (the one exception named);
`generated-structure.md`'s tree (the package's `CLAUDE.md` added, the root's described as the
pointer or the inline note). The server README's rows for `package_create`, `package_open`,
`package_adopt` and `handoff_emit` gain one clause each. Pins: `pins-213.md` over the three
references, `pins_missing.py` 0. Grepped and left alone: "the only write path into a package"
(SECURITY.md, architecture, install, extension) stays true, the wiring is the server's.

## As it landed

- The release commit `f0d31c6`; `git push origin main` `d2cf2a6..f0d31c6` at 11:58 UTC on
  2026-10-08 (three commits: `6085448`, `ff4c09a`, `f0d31c6`).
- CI run 37773642894 on `f0d31c6`: conclusion success, 9 jobs, every job success (the Windows jobs
  included; the symlink test skips there and runs on Ubuntu).
- Tag `v6.2.0` on `f0d31c6`, pushed. `git diff v6.2.0 HEAD -- plugins/tamheed`: 0 lines.
- The operator's machine: `claude plugin marketplace update tamheed`, then `claude plugin update
  tamheed@tamheed`, which updated "for scope local (C:\Users\ahammo\Repos\tamheed)" only: the
  `enable --scope local` of plan 211 had re-created a local-scope install record beside the user one.
  `claude plugin update tamheed@tamheed --scope user` moved the user record too; both records read
  6.2.0 (`claude plugin list`, the registry). Measured, recorded in the batch memory.
- Handed to the operator for `jisr`: a fresh session after the update; the planning session that
  ran under 6.1.0 may still hold the lock, so the first `package_open` may refuse on a lock naming a
  dead process (`package_unlock(confirm=true)` on their word); the open then reports
  `wiring: {root: created, package_note: planning}`, and the session after prints PE-003 through
  the hook.

## Rulings taken at the review

- **R70 (2026-10-08): commit, push, then tag on CI green.** The push carries three commits: 212
  (`6085448`), the symlink-guard follow-up (`ff4c09a`) and this release. The tag `v6.2.0` goes on
  the release commit when every CI job is green.

## Validation

- `stamp_620.py`: every surface replaced once, asserted once; the stock guide's body under `6.2.0`
  in `stock-history.json` in the same run; the two lab-tracker pins and their check sentences
  re-aimed (`plans ..., 213`); the CHANGELOG entry above the 6.1.0 heading, dated 2026-10-08 UTC.
- `docs/guide/build.py`: 1,546 ids, 724 figure files, the meta `tamheed-guide 6.2.0`; no figure moved
  on the stamp (the 212 follow-up had already rebuilt the five gate figures with the final lines).
- `refresh_lab_620.py` (in-process, `_WIRE_ROOT` off): `open.wiring null`, `open.half execution`,
  `handoff_emit` `refreshed: ["README.md"]`, `export_html` stamped `6.2.0`, `package_verify`
  `verified: true, dirty: [], foreign: [], review_current: true, review_exported_by: "6.2.0"`,
  `gate_run` ready; the untracked package note removed; the fixture's root carries no `CLAUDE.md`
  before or after.
- `python check.py`: ALL CHECKS PASSED (`lint: plugin.json 6.2.0 == newest CHANGELOG release`,
  `all 6 version-stamped surfaces carry v6.2.0`, `stock history current (17 files, 108 bodies)`).
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19, longest description 387.
- The bundle against `v6.1.0`, measured on the staged tree (`git diff --stat v6.1.0 -- plugins/tamheed`):
  ten files. The server (+132 lines), three teaching files (`handoff.md`, `workflow.md`, the
  agent-control template) and the stamp's six surfaces (plugin.json, the stock guide's title line
  and `stock-history.json`, the catalog, the server README, the front door). The CHANGELOG's first
  draft said "four teaching files" from the plan's list; corrected to the measured three.
