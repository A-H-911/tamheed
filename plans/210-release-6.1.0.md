# Plan 210: release 6.1.0 (the batch record, the version surfaces, push, tag)

> Maintainer-executed, 2026-10-05. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Source: R23 (the batch ends with the full release recipe including push and tag; the maintainer
> asks once before pushing), G3, G13 (the figures folder ships), G15 (the guide round after 6.0.0's tag).

## Status
- **Priority**: P1 - **Effort**: S - **Risk**: LOW-MEDIUM (a MINOR; the bundle changed in one beat, the
  assets; the figures folder's LF attribute meets the Windows CI jobs for the first time) - **DONE 2026-10-04 UTC**

## Steps, in the recipe's order

1. The batch record closed: the beat map through 210 with every plan's SHA, section 3 and 4 entries
   through 209, the rulings table through G29, section 5 (what was not built).
2. `plans/README.md`: the cycle heading `### The user guide round 2 -- plans 201-210 -> v6.1.0
   (released 2026-10-05; maintainer-executed)`, every row 201-210 DONE with its SHA.
3. The version surfaces: `plugin.json` 6.1.0, the CHANGELOG entry `## [6.1.0] - 2026-10-05` (MINOR: the
   figures folder, the chrome, the two-half framing, the mark and the tagline, the engine readers
   `writes`/`checks`/`inserters`/`rule_tables`/`skill_text`), the three READMEs' release contract
   (lint 8), `index.html` rebuilt (its generator meta names the version).
4. The verification the batch promised: `python check.py` green; the figures folder byte-twin on
   both CI platforms (CI); 390 px no horizontal scroll (measured per beat); Lighthouse accessibility
   on the served page, with the explicit-dark flash of file figures and the digit-only summary
   name known from 203.
5. The batch memory file updated.
6. Commit (this plan's own commit). **Ask once** before `git push origin main`.
7. CI green on every job of the matrix (ubuntu + windows, Python 3.10-3.13).
8. `git tag v6.1.0` on the CI-green commit, `git push origin v6.1.0`.
9. `git diff v6.1.0 HEAD -- plugins/tamheed` empty; the bundle diff against `v6.0.0`, measured on the
   staged tree: eleven files, the five assets and the six the stamp touches (plugin.json, the stock
   guide and its history, the catalog, the server README, the front door), as the CHANGELOG says.

## The release, as it landed

- The release commit: `a48bd35`. `python check.py` ALL CHECKS PASSED on it; the selftest 19/19.
- The push, on the operator's single word (R23): `git push origin main`, `b94c9ac..a48bd35`, ten
  commits (plan 200's ledger follow-up and 201-210), at 23:14 UTC on 2026-10-04.
- CI on `a48bd35`: run 37243052723, every job green (the server smoke job and the eight `check` jobs,
  ubuntu + windows x Python 3.10-3.13). The Windows jobs read the 724 figure files through the LF
  attribute at their first contact; no fix-up commit was needed.
- The tag: `v6.1.0` on `a48bd35`, pushed (`refs/tags/v6.1.0` on origin). `git diff v6.1.0 HEAD --
  plugins/tamheed` is empty. `git diff v6.0.0 v6.1.0 --stat -- plugins/tamheed`: 11 files, the five
  assets and the six the stamp touches, as the CHANGELOG says.
- This ledger's own lines above landed in a follow-up commit after the tag; the bundle did not move.

## Pin ledger

- `plans/evidence/scripts-ste/pins-210.md` (23 pinned phrases); `pins_missing.py`: 0 missing. The
  guide's content did not change in this beat: `index.html` moved by its generator meta alone.

## What landed, beyond the plan

- **The stamp is a script** (`plans/evidence/scripts-210/stamp_610.py`): each surface's current
  version line replaced once, asserted once; the stock guide's body appended under `6.1.0` in
  `stock-history.json` in the same run (the 5.2 lesson: stock text lands with its history key); the
  two lab-tracker eval pins re-aimed with their check sentences.
- **The lab fixture followed through the engine** (`refresh_lab_610.py`, the 198 pattern): `handoff_emit`
  to a scratch target with `refresh_stock=true` reported `refreshed: ["README.md"]`, `export_html`
  stamped the page `6.1.0`, `package_verify` read `verified: true, dirty: [], foreign: [],
  review_current: true, review_exported_by: "6.1.0"`, `gate_run` ready; the emit also wrote the
  package's `CLAUDE.md` note, which the fixture never tracked, and the script removed it. The two
  planning-only fixtures keep their 6.0.0 guide: no tool of theirs rewrites it without a kickoff,
  and the eval pins on the guide's title belong to the lab-tracker case alone.
- **Lighthouse on the served page** (desktop, navigation): accessibility 100, best practices 100,
  SEO 100 (57 audits passed, the one failure under "agentic browsing", not a bar of this batch).
- **The selftest:** 19/19 tools registered, 19/19 descriptions, the longest 387 characters.
- **The Lighthouse run was on the 209 tree**, before the stamp; the stamp moves the generator meta
  alone, nothing an audit reads.
- **The date is UTC** (the 198 and 191 convention): the commit lands on 2026-10-04 UTC at 23:xx, so
  the CHANGELOG heading and the plans index say 2026-10-04; the per-beat ledgers keep their local
  dates, as they were written.
- **The content sweep of the four prose surfaces** (the release contract, not a version bump): the
  root README's guide line now says the guide draws as well as lists; the mark and the tagline moved
  in 209; Keystone appears only as lineage and the migration route; nothing else of this batch's
  making was stale. `git ls-files --eol docs/guide/figures` reads `i/lf` on all 724 files before the
  Windows jobs meet the attribute.

## Rulings taken at the review (2026-10-05 AST, 2026-10-04 UTC)

- Approved: commit as staged, push `main`, tag `v6.1.0` on the CI-green commit (the one word for the
  push, R23).
- **G30, the fixtures follow the engine or stay:** a recorded fixture's stock guide moves only when a
  tool of its own rewrites it; the two planning-only fixtures keep their 6.0.0 guide, as a live
  package created under 6.0.0 would until its next emit.

## Validation

- `python check.py`: ALL CHECKS PASSED on the stamped tree (`lint: plugin.json 6.1.0 == newest
  CHANGELOG release`, `all 6 version-stamped surfaces carry v6.1.0`, `stock history current (17 files,
  107 bodies)`); `docs/guide/build.py` 1,545 ids, 724 files, the meta `tamheed-guide 6.1.0`.
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19.
