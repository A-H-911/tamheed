# Plan 004 (A4): Fix the docs that actively mislead, and archive the stale audit

> **Executor instructions**: Follow step by step; verify each step; STOP conditions are binding.
> Update this plan's row in `plans/README.md` when done.
>
> **Drift check (run first)**:
> `git diff --stat 0e055f6..HEAD -- tests/README.md plugins/keystone/references/artifact-catalog.md plugins/keystone/scripts/validate_package.py AUDIT.md .github/workflows/ci.yml evals/README.md`
> Mismatch with the excerpts below = STOP.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (independent of 001–003; can run in parallel)
- **Category**: docs
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Wrong documentation is worse than missing documentation: it sends a contributor (or an agent) down
a path that fails. Four documents are actively wrong today: `tests/README.md` gives run commands
that point at a **nonexistent file** and claims coverage that is false; the artifact catalog denies
the existence of three schemas that exist and are consumed; the validator's own docstring shows a
wrong usage path; and a 387-line audit sits at the repo root asserting, in present tense, problems
that were fixed months ago ("there is no CI"). During the upcoming v2 program these files are what
contributors will read first — they must tell the truth.

## Current state (verified excerpts at `0e055f6`)

1. **`tests/README.md`** — run commands at lines 12, 18, 24 say
   `python tests/validate_package.py <package-dir>` but the validator lives at
   `plugins/keystone/scripts/validate_package.py` (there is no `tests/validate_package.py`).
   Line 46 claims "**57 tests**, **100% line coverage** of both executable modules" — false
   (`create_remote` in `init_skill_repo.py:1069-1100` has zero coverage; verified by grep: the
   only `gh`-related test mocks `check_prereqs`, lines 491–500 of the test file). Lines 62–71:
   "All five are **Critical**" + a 5-gate table — there are SEVEN critical gates (G-SET and
   G-PROGRESS missing). Line 61 references `../skill/references/quality-gates.md` — no `skill/`
   directory exists (it is `plugins/keystone/references/`). The file's own stale-content warning
   sits at lines 53–57 and only covers content BELOW it — the wrong run commands are above it.
2. **`plugins/keystone/references/artifact-catalog.md`** — the legend at line 28 says template
   paths are "relative to the Keystone **repo-root** `templates/` directory"; there is no
   repo-root `templates/` (line 33 of the same file correctly says they are bundled at
   `../templates/`). Schema column shows `—` (meaning "no schema" per the legend at line 29–30)
   for three artifacts whose schemas exist and are consumed by
   `schemas/keystone-state.schema.json` (at its lines 92, 122, 174):
   - line 86 (Architecture Decision Record) → `schemas/adr-metadata.schema.json`
   - line 101 (Phased roadmap) → `schemas/execution-phase.schema.json`
   - lines 124–125 (Progress log / Status report) → `schemas/progress-update.schema.json`
3. **`plugins/keystone/scripts/validate_package.py:42-45`** — module docstring Usage block:

   ```text
   Usage:
       python tests/validate_package.py <package-dir>
       python tests/validate_package.py <package-dir> --json
       python tests/validate_package.py --help
   ```

   Wrong path (same stale location); the argparse `prog`/epilog around `:1065-1069` are correct —
   only the docstring lies. A similar stale path appears in the notes region near `:1230` —
   search the file for `tests/validate_package.py` and fix every occurrence.
4. **`AUDIT.md`** (repo root, 387 lines, dated 2026-06-21) — asserts in present tense: a hollow
   package "passes as OK", "there is no CI", "no prompt-injection safeguard". All remediated in
   v0.2.0/v1.0.0 (see `CHANGELOG.md`). Live references to it: `.github/workflows/ci.yml:5`
   (comment: "This is finding F-02 from AUDIT.md") and `evals/README.md:44`
   ("See `AUDIT.md` §11.8"). A third mention in `CHANGELOG.md:59` is a historical release note —
   it must NOT be edited.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Test suite | `python tests/test_validate_package.py` | exit 0 |
| Goldens | the four validator runs (see plan 001) | 0/0/1/1 |
| Stale-path sweep | `grep -rn "tests/validate_package.py" --include="*.md" --include="*.py" .` | 0 matches when done |

## Scope

**In scope**: `tests/README.md`, `plugins/keystone/references/artifact-catalog.md`,
`plugins/keystone/scripts/validate_package.py` (docstring/comments only — zero behavior change),
`AUDIT.md` (move), `docs/history/` (create), `.github/workflows/ci.yml` (one comment line),
`evals/README.md` (one line).

**Out of scope**: `CHANGELOG.md` (historical entries are immutable); `scripts/README.md` (its
layout-tree staleness is deliberately NOT fixed — the whole bootstrap is deleted in plan 009);
any `*.template.md`; any behavior in any `.py` file.

## Git workflow

- Branch: `docs/truth-sweep`; single commit, e.g. `docs: fix stale validator paths/claims, archive AUDIT.md`.
- Use `git mv` for the AUDIT.md move so history follows.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Rewrite `tests/README.md`'s wrong content

- Fix the three run commands (lines 12/18/24) to `python plugins/keystone/scripts/validate_package.py …`.
- Replace line 46's claim with an honest statement: state the suite is stdlib-`unittest`, point at
  the `python -m trace` command already documented there for measuring coverage, and do NOT state
  a percentage (coverage numbers rot; the file proves it).
- Replace the 5-gate table and "All five are Critical" (lines 59–71) with the seven-gate list
  (G-IDS, G-DEC-STATUS, G-REQ-SRC, G-COMPLETE, G-TRACE, G-SET, G-PROGRESS) — source the one-line
  descriptions from `plugins/keystone/references/quality-gates.md` and `CLAUDE.md`'s gate summary.
- Fix line 61's `../skill/references/quality-gates.md` → `../plugins/keystone/references/quality-gates.md`.
- Mention all THREE fixtures (valid, invalid, incomplete) where the file lists two.
- Delete the now-redundant stale-content warning block (lines 53–57) once the content below it is
  actually true.

**Verify**: every command quoted in the file runs successfully as pasted from the repo root;
`grep -n "skill/references" tests/README.md` → 0 matches.

### Step 2: Fix the artifact catalog

- Line 28: change "repo-root `templates/` directory" wording to "the bundle's `templates/`
  directory (`../templates/` relative to this file)" — consistent with line 33.
- Fill the three Schema cells identified above with their real schema paths, formatted like the
  other populated rows (e.g. `schemas/adr-metadata.schema.json`). If a note is needed, use
  "(state-owned)" to signal the schema is consumed via `keystone-state.schema.json`.

**Verify**: `grep -n "adr-metadata.schema.json" plugins/keystone/references/artifact-catalog.md`
→ ≥1 match; same for `execution-phase.schema.json` and `progress-update.schema.json`.

### Step 3: Fix the validator's docstring paths

Replace every occurrence of `tests/validate_package.py` in
`plugins/keystone/scripts/validate_package.py` with `plugins/keystone/scripts/validate_package.py`.
No other edits to the file.

**Verify**: `python tests/test_validate_package.py` → exit 0 (proves no accidental behavior
change); the stale-path sweep grep from "Commands" section → 0 matches repo-wide.

### Step 4: Archive AUDIT.md

- `mkdir docs/history` (if absent); `git mv AUDIT.md docs/history/AUDIT-2026-06-21.md`.
- Prepend this banner to the moved file (above its current first line):

  ```markdown
  > **HISTORICAL DOCUMENT (2026-06-21, commit e7e970e).** Every finding below (F-01…F-11) was
  > remediated in v0.2.0/v1.0.0 — see `CHANGELOG.md`. Present-tense claims in this report
  > describe the repository as it was BEFORE those releases. Kept for its research citations
  > and methodology; do not act on its findings.
  ```

- Update `.github/workflows/ci.yml:5` comment: `AUDIT.md` → `docs/history/AUDIT-2026-06-21.md`.
- Update `evals/README.md:44` reference the same way.
- Leave `CHANGELOG.md:59` untouched.

**Verify**: `test -f AUDIT.md` → file absent; `grep -rn "AUDIT.md" --include="*.md" --include="*.yml" . | grep -v history | grep -v CHANGELOG | grep -v plans/` → 0 matches.

### Step 5: Full regression

**Verify**: test suite exit 0; goldens 0/0/1/1 (nothing in this plan can affect them — this
confirms it).

## Test plan

No new tests — docs-only. The verification greps are the regression net.

## Done criteria

- [ ] Stale-path sweep grep → 0 matches repo-wide (excluding `plans/` and `docs/history/`)
- [ ] Every command in `tests/README.md` runs as pasted
- [ ] `AUDIT.md` gone from root; archived copy carries the banner; both live refs updated
- [ ] Suite exit 0; goldens 0/0/1/1
- [ ] Only in-scope files changed
- [ ] `plans/README.md` row updated

## STOP conditions

- Line numbers in "Current state" don't match the live files (drift).
- You find additional stale references to `AUDIT.md` beyond the two listed (report; don't chase
  into out-of-scope files).

## Maintenance notes

- Plan 014 (B8) rewrites README/docs wholesale for Tamheed v2 — this plan only makes v1 docs stop
  lying in the interim; don't gold-plate.
- Reviewer scrutiny: the banner wording on the archived audit (must not read as if findings are
  still open).
