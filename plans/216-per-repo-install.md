# Plan 216 -- tamheed per repository, nothing at user level

> Status: DONE 2026-10-10 UTC (maintainer-executed, the operator's word at the review). Field cycle acmp-FB-029 + per-repo
> install (plans 216-218). Docs and the operator's machine; no version bump in this beat (218 stamps
> 6.3.0). Evidence: `plans/evidence/scopetest-216-2026-10-10.md` (every measurement verbatim).

## What the operator asked

Two repositories use tamheed on this machine, ACMP and jisr. The operator wants each repository to
hold its own install record, updated on its own, and nothing tamheed-related at user level: no user
record, no user enable key, no user-level marketplace declaration.

## What the machine looked like, and the rule that decided the design

Two records: user scope (6.2.0) and local scope for the tamheed repository (6.2.0), both on the
`6.2.0` cache folder. `~/.claude/settings.json` carried `"tamheed@tamheed": false` under
`enabledPlugins` and the `tamheed` marketplace under `extraKnownMarketplaces` (written by
`claude plugin marketplace add`). ACMP and jisr held no record and enabled the plugin in their
`.claude/settings.json`.

**The loading rule, measured 2026-10-09 in a scratch folder (Claude Code 2.1.294):** a local-scope
record at 6.2.1 beside the user record at 6.2.0 loaded **6.2.0**. The user record wins the load when
both exist. The vendor's loading page states no precedence between records (it says plugins load
"from `installed_plugins.json` and the cache"), so the measurement stands. Per-repository versions
therefore need the user record gone. `--plugin-dir` shadows a same-named installed plugin
(measured the same day; the vendor's "Name conflicts" item 2 agrees).

**Vendor facts read directly (code.claude.com, 2026-10-10):** `uninstall --scope` removes that
scope's record only, and the previous version folder keeps an `.orphaned_at` marker for 14 days "so
a session that already loaded the old version keeps running"; `update` without `--scope` picks
local, project, user (v2.1.281+); `marketplace add --scope project` declares the marketplace in the
project's `.claude/settings.json`; `extraKnownMarketplaces` is an object keyed by marketplace name;
a project `true` alone fetches nothing onto a machine with no record, while a `true` in a gitignored
`.claude/settings.local.json` does.

## The design (R74)

- Per repository = a project-scope record per repository and no user record. In each repository:
  `claude plugin marketplace add A-H-911/tamheed --scope project` (the declaration lands in the
  project's `.claude/settings.json`, written by the CLI, never by hand), then `claude plugin install
  tamheed@tamheed --scope project`. One repository moves with `claude plugin update tamheed@tamheed
  --scope project`.
- The user record went first (`claude plugin uninstall tamheed@tamheed --scope user`, R74), with the
  live ACMP session still running from its 6.2.0 cache folder. The user `enabledPlugins` key went
  with it. The user-level marketplace declaration goes last (M8), after the tamheed repository
  declares the marketplace at its own scope.
- The tamheed repository keeps its local record and moves it to the current release.
- The marketplace clone and `known_marketplaces.json` stay per machine: the vendor offers no
  per-project clone, and a repository's declaration re-clones it when missing.

## The measurements (every line verbatim in the evidence file)

- **M1 (step 0, R74).** `uninstall --scope user`: one record left (the tamheed repository, local,
  6.2.0), the user `enabledPlugins` key gone, every cache folder present, no orphan marker yet. The
  ACMP session holding its lock (pid 55128) kept running.
- **M2.** A scratch folder with no record: the session listed no tamheed server (`NONE`).
- **M3.** `marketplace add --scope project` in the scratch folder: "already on disk — declared in
  project settings", the key an object `{"tamheed": {"source": {"source": "github", "repo":
  "A-H-911/tamheed"}}}`; `install --scope project`: a project record at 6.2.1 and the enable in the
  scratch `.claude/settings.json`; the session there loaded **6.2.1**.
- **M4.** The tamheed repository (local record 6.2.0), the same session shape, the same minute:
  **6.2.0**. Two versions on one machine, each repository its own.
- **M5.** `update --scope local` in the tamheed repository: "updated from 6.2.0 to 6.2.1 for scope
  local"; the scratch record untouched.
- **M6.** `uninstall --scope project` in the scratch folder: the record and the enable removed, the
  marketplace declaration kept in the scratch settings; records back to the one tamheed-repo record.
- **M7.** Cache folders 5.0.0 to 6.2.1 all present; `6.2.0` now carries `.orphaned_at` (the vendor's
  14-day rule, seen); `6.2.1` does not.
- **M8.** `marketplace add --scope local` in the tamheed repository (its gitignored
  `.claude/settings.local.json` gained the declaration); the `tamheed` key removed from the user
  settings' `extraKnownMarketplaces` by a script that kept every other key; `claude plugin
  marketplace list` still lists `tamheed`, `known_marketplaces.json` still knows it, the clone is
  present; a session in the tamheed repository loaded **6.2.1**. Two user-level mentions remain
  and are not install state: `env.TAMHEED_HOOK_LOG` and an auto-mode allow phrase ("tamheed MCP
  calling"), both the operator's conveniences, put to the operator at the review.

## The docs (one posture, three copies, one recipe)

`README.md` (the install recipe and the "Per repository" paragraph), `docs/install.md` (the same,
the scope examples, and the new "Moving a project to a newer release"), the guide's install section
(`section.install.plugin.*`, `section.install.scope.*`, EN and AR mirrored, the two `pre` blocks in
`render.py`). Plan 211's ledger stays as written; its memory is amended.

## Rulings taken at the review

- **R74 (2026-10-09, the planning checkpoint): remove the user-scope record now.** The live ACMP
  session keeps its loaded bundle (the vendor's 14-day rule, and the tamheed repository's record
  references the same folder).
- **R76 (2026-10-10, the commit review): the two user-level conveniences stay.** `env.TAMHEED_HOOK_LOG`
  (the opt-in hook trace, plan 136) and the auto-mode allow phrase ("tamheed MCP calling") are the
  operator's own and not install state. "Nothing at user level" means no record, no enable key, no
  marketplace declaration, all three measured gone.

## Validation

- **Pins.** `pins-216.md` taken from HEAD copies of the four docs (the README, `docs/install.md`,
  `content.py`, `render.py` had been patched before the ledger was taken; the HEAD copies restore the
  "before"): 29 pinned phrases; `pins_missing.py`: 0.
- **Lint 14** (flavored surfaces keep the 25-word cap and the semicolon ban): three rounds of
  sentence splits across the README, `docs/install.md` (the per-repository paragraph, the
  collaborator paragraph, the upgrade recipe) and the guide's two scope strings (EN and AR).
  `python check.py lint`: ALL CHECKS PASSED.
- **The posture grep, widened at the advisor's review.** Bare `update`/`install` commands imply
  user scope by default on older builds: four were found outside the new paragraphs (the Upgrading
  section's block, the guide's upgrade `pre` block, the workflow upgrade string EN and AR) and now
  carry `--scope project`. The `/plugin` panel line in the Upgrading section stays: the panel has no
  scope flag and updates the record it finds.
- **The guide.** `docs/guide/build.py`: 1,546 ids, 724 figure files, `--check` fresh, `--missing` 0;
  no figure moved (prose and `pre` blocks only), so no captures (R66's class).
- **The gate.** `python check.py`: ALL CHECKS PASSED (`3 case(s) checked, 0 failed, 6 skipped`).
- **The posture, grepped.** "scope user" occurs in the three copies only as the removal command
  (`uninstall tamheed@tamheed --scope user`).
- **The machine after the beat.** `claude plugin list --json`: one record, local, the tamheed
  repository, 6.2.1 (218 moves it to 6.3.0). `~/.claude/settings.json`: no `tamheed@tamheed` under
  `enabledPlugins`, no `tamheed` under `extraKnownMarketplaces`.
