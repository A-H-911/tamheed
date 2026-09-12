# Plan 058: Cut v4.8.0 — the advisor-audit release (plans 042–057 + lab beat 15)

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving on. Touch only the files listed
> as in scope. If any STOP condition occurs, stop and report — do not improvise. Commit
> in the worktree per the git workflow section; do NOT tag or push (the reviewer does).
> SKIP updating `plans/README.md` — the reviewer maintains the index.
>
> **Drift check (run first)**: `git log --oneline -1` must show the commit the reviewer
> named in your dispatch message (plan 059 merged). `grep -c '^## \[Unreleased\]' CHANGELOG.md` → `1`
> and `grep -n '^## \[4.8.0\]' CHANGELOG.md` → nothing (not yet released).

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW (mechanical; every step is lint-enforced by `check.py`)
- **Depends on**: 042–057 DONE, 059 DONE (merged)
- **Category**: release
- **Planned at**: commit `094dd13`, 2026-09-12 (executed against the post-059 `main`)

## Why this matters

Sixteen advisor plans and a lab beat sit under `## [Unreleased]`. The maintainer's release
contract (plan 030, lint-enforced): every release bumps `plugin.json`, gets a dated
CHANGELOG heading with a narrative paragraph, stamps the version into the five documentation
surfaces, and — because `plugins/tamheed/prompts/README.md` is itself a stock prompt whose
body carries the version — appends that README's new body to `stock-history.json` under the
release key (lint 9). `check.py` lints 4, 5, 8 and 9 refuse a release that skips any of
these. Plan 053 changes a tool contract additively (a refusal on a previously legal write)
and 056 adds a suite and harness primitives → **MINOR**: 4.8.0.

## Current state

- `plugins/tamheed/.claude-plugin/plugin.json:4` — `"version": "4.7.0"`.
- `CHANGELOG.md:12` — `## [Unreleased]` followed by one `### Fixed` list and one
  `### Changed` list (the sixteen plans' bullets), then `## [4.7.0] - 2026-09-07`.
  The 4.7.0 block shows the house style: a bold lead-in
  `**MINOR — <title> (plan NNN, findings_NN/CNN).**` followed by a narrative paragraph, then
  `### Added` / `### Changed` / `### Fixed` subsections.
- Version stamps at 4.7.0 (from `git grep -n "4\.7\.0"` excluding CHANGELOG/plans/history/fixtures):
  - `README.md:14` — `<em>Claude Code plugin + MCP-backed agent skill &middot; v4.7.0</em>`
  - `README.md:436` — `**v4.x** (currently v4.7.0).`
  - `plugins/tamheed/SKILL.md:18` — `This skill documents tamheed **v4.7.0**`
  - `plugins/tamheed/prompts/README.md:1` — `# How to use this folder — the \`{package}\` prompt guide (tamheed v4.7.0)`
  - `plugins/tamheed/references/artifact-catalog.md:1` — `(tamheed v4.7.0)`
  - `plugins/tamheed/server/README.md:3` — `as of **tamheed v4.7.0**`
  - `plugins/tamheed/prompts/stock-history.json` — the `"README.md"` entry has a `"4.7.0"` key
    whose value is the README's current body (`{package}` unsubstituted).
  - `lab/scenario.md:145` — beat 14's heading mentions v4.7.0 (history; leave it).
- Lint contracts (`check.py`): 4 — `plugin.json` version == newest CHANGELOG release heading;
  5 — headings strictly newest-first; 8 — the five stamped files contain the current
  version; 9 — every `prompts/*.md` body appears under some release key in
  `stock-history.json`.
- Tags: annotated `vX.Y.Z` (`git cat-file -t v4.7.0` → `tag`), pushed to origin. Release
  commit message style: `feat: v4.7.0 — the sanctioned read for committed scripts + the paste guard (plan 041)`.
- The `[Unreleased]` bullets already cite their plan numbers; the release paragraph cites
  the audit and the beat.

## Scope

**In scope**: `plugins/tamheed/.claude-plugin/plugin.json`, `CHANGELOG.md`, `README.md`,
`plugins/tamheed/SKILL.md`, `plugins/tamheed/prompts/README.md`,
`plugins/tamheed/prompts/stock-history.json`, `plugins/tamheed/references/artifact-catalog.md`,
`plugins/tamheed/server/README.md`.

**Out of scope**: everything else. No code, no tests, no fixture. Do not re-stamp
`lab/scenario.md`, `docs/history/**`, `plans/**`, or the eval fixtures' prompt copies.

## Git workflow

- One commit: `feat: v4.8.0 — the advisor audit: sixteen plans, the lab beat, the first CI runs (plans 042–059)`.
  Do NOT tag, do NOT push — the reviewer tags `v4.8.0` (annotated) and pushes with tags.

## Steps

### Step 1: Bump and stamp

- `plugin.json`: `"version": "4.8.0"`.
- Replace `4.7.0` → `4.8.0` in exactly the six stamp lines listed above (`README.md` ×2,
  `SKILL.md`, `prompts/README.md`, `artifact-catalog.md`, `server/README.md`). Nothing else
  in those files.

**Verify**: `git grep -n "4\.7\.0" -- README.md plugins/tamheed/SKILL.md plugins/tamheed/prompts/README.md plugins/tamheed/references/artifact-catalog.md plugins/tamheed/server/README.md` → no output.

### Step 2: Stock history for the README prompt

In `plugins/tamheed/prompts/stock-history.json`, under the `"README.md"` object, add a
`"4.8.0"` key whose value is the **exact current body** of `plugins/tamheed/prompts/README.md`
(after Step 1; the file's text verbatim, with `{package}` left as is). Do it with a script,
not by hand — this exact recipe reproduces the file byte-for-byte (verified 2026-09-12:
`json.dumps(h, indent=1, ensure_ascii=False) + "\n"` equals the committed file):

```python
import json, pathlib
hist = pathlib.Path("plugins/tamheed/prompts/stock-history.json")
h = json.loads(hist.read_text(encoding="utf-8"))
h["README.md"]["4.8.0"] = pathlib.Path("plugins/tamheed/prompts/README.md").read_text(encoding="utf-8")
hist.write_text(json.dumps(h, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
```

Then `git diff --stat plugins/tamheed/prompts/stock-history.json` → `1 file changed, 2 insertions(+), 1 deletion(-)`
(the previous last key's line loses its comma; one new key). Any larger diff = the recipe
drifted; STOP.

**Verify**: `python check.py lint` → `lint: stock history current (…)` prints and no `FAIL`.

### Step 3: The CHANGELOG entry

Replace the `## [Unreleased]` block with an empty `## [Unreleased]` heading followed by:

```markdown
## [4.8.0] - 2026-09-12

**MINOR — the advisor audit: sixteen plans, the lab beat, the first CI runs (plans
042–059; `/improve deep`, 2026-09-10).** An external advisor audit of v4.7.0 — eight
read-only sweeps, every finding re-read or reproduced before it was planned — produced
sixteen self-contained plans, each executed by an isolated executor, reviewed against its
own done criteria, and integrated on one branch before merge. Two findings were
silent-corruption class: `entity_upsert` released its savepoint before the stale-tree
check, so a refused write stayed applied in memory (043); and `package_migrate` deleted
`data/` before it copied, on the registry-sync path that has no backup (045). One is a
tool-contract change: a phase or slice can no longer be created already `Implemented`
without `force` (053). The rest are hygiene the engine's own doctrine already implied
(name validation on every tool, the marker scan's history filter, hollow scoped readiness,
CSV defusing, the note's skill screen, numeric id order). CI, which had never run on this
repository, ran for the first time on 2026-09-11 (manual dispatch; push events still do
not fire — an account-side setting) and is green on eight legs plus the smoke job. Lab
beat 15 exercised the mechanisms a lab can reach and pinned them with nine assertions.
No schema migration.
```

then the existing `### Fixed` and `### Changed` lists **moved verbatim** under the new
heading (keep bullet text and order; they already cite plan numbers).

**Verify**: `python check.py lint` → `lint: plugin.json 4.8.0 == newest CHANGELOG release`
and `lint: CHANGELOG N releases strictly newest-first`, no `FAIL`.

### Step 4: The gate

**Verify**: `python check.py` → `ALL CHECKS PASSED` (background it). Then commit.

## Done criteria

- [ ] `grep -n '"version"' plugins/tamheed/.claude-plugin/plugin.json` → `4.8.0`
- [ ] `grep -n '^## \[4.8.0\] - 2026-09-12' CHANGELOG.md` → one hit, directly under an empty `## [Unreleased]`
- [ ] `git grep -c "4\.8\.0" -- README.md plugins/tamheed/SKILL.md plugins/tamheed/prompts/README.md plugins/tamheed/references/artifact-catalog.md plugins/tamheed/server/README.md` → each file ≥ 1
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` clean after the one commit; only in-scope files in `git show --stat`

## STOP conditions

- The drift check fails (059 not merged, or 4.8.0 already present).
- `check.py lint` reports a stock-history or version lint failure you cannot make pass by
  the steps above — report the exact `CHECK FAILED` line.
- Any file outside the in-scope list needs a change.

## Maintenance notes

- Reviewer's post-merge steps: `git tag -a v4.8.0 -m "v4.8.0 — the advisor audit"`,
  `git push origin main --tags`, `gh workflow run ci.yaml --ref main` (filename form since the 2026-09-12 rename), then update the index
  and the memory of the release date.
- Next release: beat 16; the `[Unreleased]` heading is empty again.
