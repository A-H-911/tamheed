# Plan 062: Cut v4.8.1 — the post-release review (plans 060–061)

> Executed directly by the reviewer (maintainer-delegated, 2026-09-12) on the maintainer's
> words: "cut v4.8.1 after the docs sweep". Same recipe as plan 058; recorded so the index
> row has a self-contained record.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW (mechanical; lints 4, 5, 8, 9 enforce every step)
- **Depends on**: 060, 061 DONE
- **Category**: release
- **Planned at**: commit `0f50378`, 2026-09-12

## Why PATCH

One engine fix (060: waiver citation; verdicts unchanged), one CI chore (the workflow rename
that restored push/schedule/pull_request delivery), one docs sweep (061). No tool-contract
change, no schema change → 4.8.1.

## Steps (as executed)

1. `plugin.json` → `4.8.1`; the six stamp lines (`README.md` ×2, `SKILL.md`,
   `prompts/README.md`, `artifact-catalog.md`, `server/README.md`) → `4.8.1`.
2. `stock-history.json["README.md"]["4.8.1"]` = the README prompt body, via the plan-058
   recipe (`json.dumps(h, indent=1, ensure_ascii=False) + "
"`); diff = `2 insertions, 1 deletion`.
3. CHANGELOG: `## [4.8.1] - 2026-09-12` with the PATCH lead-in paragraph; the `[Unreleased]`
   `### Fixed` / `### Changed` lists moved verbatim under it; `[Unreleased]` empty again.
4. `python check.py lint` → `plugin.json 4.8.1 == newest CHANGELOG release`, `stock history current`.
5. `python check.py` → `ALL CHECKS PASSED`; one commit; annotated tag `v4.8.1`; push with tags;
   CI fires on the push (no manual dispatch needed since the rename).

## Acceptance for this batch (060–062)

- The new test RED on the old order, GREEN after; `tests/test_mcp_contract.py` 138 OK.
- `python check.py` green on the release tree.
- CI green on push for every commit since the rename; `pull_request` and `workflow_dispatch`
  delivery verified the same day; the weekly `schedule` slot is Monday 2026-09-14 06:17 UTC.
- Lab golden byte-identical on re-export after 060 (no beat needed: the citation rule is
  pinned by the suite; beat 15's evidence report keeps the pre-fix observation as history).

## Done criteria

- [ ] `grep -n '"version"' plugins/tamheed/.claude-plugin/plugin.json` → `4.8.1`
- [ ] `grep -n '^## \[4.8.1\] - 2026-09-12' CHANGELOG.md` → one hit under an empty `## [Unreleased]`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git tag -l v4.8.1` → the tag; `gh run list --limit 1` → `push`, success
