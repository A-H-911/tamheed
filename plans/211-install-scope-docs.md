# Plan 211 -- the per-project install refusal: enable, do not reinstall

> Status: DONE 2026-10-08 (maintainer-executed, the operator's rulings by question).
> Docs only. No engine change, no version bump. The approved plan with the devil's-advocate review is
> the operator's plan file; this ledger is the repo's record.

## The problem, as measured on the maintainer's machine (2026-10-08, Claude Code 2.1.294)

The operator installed tamheed at project scope in a new repository. The `/plugin` flow refused:
`Plugin 'tamheed@tamheed' is already installed globally. Use '/plugin' to manage existing plugins.`
After `/reload-plugins` the plugin was still invisible there.

- `~/.claude/plugins/installed_plugins.json` held two records for `tamheed@tamheed`: user scope
  (5.8.1, installed 2026-07-21) and local scope for `C:\Users\ahammo\Repos\tamheed` (5.1.0,
  2026-09-26). The cache held fourteen version directories, 4.13.0 to 6.1.0. No record pointed at 6.1.0.
- `~/.claude/settings.json` said `"tamheed@tamheed": false` (the first step of the FB-022 recipe in
  `docs/install.md`).
- This repository's gitignored `.claude/settings.local.json` said `"tamheed@tamheed": true`. That is
  why the plugin loaded here and nowhere else. `claude plugin list` printed both records as enabled with
  the note "Disabled in ~/.claude/settings.json but still loads".
- The hook log (`TAMHEED_HOOK_LOG`) read `version=5.8.1` on every session since 2026-10-07, this one
  included. The maintainer's own sessions ran the user-scope 5.8.1 copy, two releases behind the repo.
- The refusal is the `/plugin` session flow's. The vendor's troubleshooting page: the message means the
  plugin is installed at user scope (or by managed settings); "there's nothing to add"; the remedy is to
  enable or disable it per scope. The shell form prints a different line, `Plugin "<id>" is already
  installed (scope: user)`, and exits 0.
- `enabledPlugins` merges key by key across scopes, the highest scope that mentions the id wins. A
  project with no entry inherits the user-level `false`. The missing step was `claude plugin enable
  tamheed@tamheed --scope project` in the new repository. `docs/install.md` named it (L49-63) without
  the refusal line a reader meets first; `README.md` showed the user-scope install only; the guide's
  install section printed `claude plugin install tamheed@tamheed --scope project` as its first command,
  the command that refuses once a user-scope record exists.

## The measurement (step 2 of the plan)

On a scratch git directory with no project settings, the user entry at `false`, Claude Code 2.1.294:

- `claude plugin enable tamheed@tamheed --scope project --json` printed
  `{"command":"enable","outcome":"ok","plugin":"tamheed@tamheed","pluginId":"tamheed@tamheed","scope":"project","message":"Successfully enabled plugin: tamheed (scope: project)"}`,
  exit 0. It wrote `.claude/settings.json` = `{"enabledPlugins": {"tamheed@tamheed": true}}` and added
  no record to `installed_plugins.json`. `claude plugin list` from that directory read "Disabled in
  ~/.claude/settings.json but still loads — project settings enable it".
- `claude plugin install tamheed@tamheed --scope project --json` printed
  `{"command":"install","outcome":"ok",...,"scope":"project","message":"Successfully installed plugin: tamheed@tamheed (scope: project)"}`,
  exit 0, and **added a project-scope record** (SHA 01cec0d, the probe's path). So the shell install
  succeeds where the `/plugin` panel refuses; the first draft of this beat said the shell form refuses
  too, from a vendor sentence about the *same* target scope. The record was removed with
  `claude plugin uninstall tamheed@tamheed --scope project --keep-data` from the probe, and the probe
  directory deleted.
- The docs lead with `enable` (one record, one cached copy) and name `install --scope project` for a
  machine with no record (a collaborator's clone).

## The machine (step 3; not committed)

Before: two records (user 5.8.1, local 5.1.0 for this repository), both listed as enabled through the
local settings. The steps, from this repository's root:

1. `claude plugin uninstall tamheed@tamheed --scope local --keep-data`: ok. **It also removed the
   `"tamheed@tamheed": true` from `.claude/settings.local.json`** (the file read `"enabledPlugins": {}`),
   so the plugin would have been disabled here. The two data directories under `~/.claude/plugins/data/`
   are empty; `--keep-data` cost nothing.
2. `claude plugin update tamheed@tamheed`: "updated from 5.8.1 to 6.1.0 for scope user. Restart to apply".
3. `claude plugin enable tamheed@tamheed --scope local`: ok; the local file carries the `true` again.

After: one record, user scope, `cache\tamheed\tamheed\6.1.0`; `claude plugin list` reads
`Version: 6.1.0  Scope: user  Status: enabled` with the local-settings note. `git status` clean of
settings (the local file is ignored). The next session here runs the 6.1.0 bundle; this one keeps 5.8.1
(the running session keeps what it loaded).

## The docs

- `README.md`: a "Project only" paragraph in the Install block.
- `docs/install.md`: the FB-022 paragraph gains the uninstall note; a new paragraph carries the panel's
  refusal line, the two measured shell routes (enable preferred), the update step, the inherited
  `false`, the collaborator sentence. One recorded observation was reworded: the 2026-09-25 line "It
  refuses 'already enabled at project scope' while the user entry exists" now reads "while a user entry
  says `true`". That narrowing is an inference from the adjacent sentence (the enable command checks the
  merged effective state), not a re-measurement: this beat measured the `false` case only, and the
  `true` case stands as the field reported it.
- `docs/guide/content.py` + `docs/guide/render.py`: `section.install.scope.1` reworded (EN + AR),
  `section.install.scope.2` added (EN + AR), the pre-block leads with `enable`; `index.html` rebuilt.

## Handed to the operator

- In the new repository, from its root: `claude plugin enable tamheed@tamheed --scope project`, then a
  fresh session. Acceptance: the session lists `/tamheed:tamheed`, asks to approve the `tamheed` MCP
  server, and the hook log's new line reads `version=6.1.0 source=startup`.

## Rulings taken at the review

- **R65 (2026-10-08): enable preferred, install named.** The approved plan's premise moved at the
  probe (the shell install succeeds beside a user-scope record), so the recommendation was put again.
  The docs lead with `claude plugin enable --scope project` (one record, one cached copy) and name
  `install --scope project` for a machine with no record, a collaborator's clone, where it is the only
  route.
- **R66: no captures for this beat.** Prose-only change in one section, both languages; the browser tools
  did not connect; the byte-twin and lint 14 are the checks. A deviation from G3, accepted once.
- **The commit as staged**, seven files. The machine changes stay uncommitted and recorded above.
- The operator runs the new repository's enable command (ruled at the plan's review).

## Validation

- `python check.py lint` found one hard finding on the first pass: `section.install.scope.1.en` at 26
  words (cap 25). The sentence was split (EN and AR mirrored). Then `python check.py`: ALL CHECKS PASSED
  (lint 14 on the three flavored surfaces, lint 8 unchanged at 6.1.0, the guide byte-twin,
  `docs/guide/build.py --check` fresh, `--missing` 0 over 1,546 ids).
- No captures: the change is prose in one section, no figure, no layout; the byte-twin and the lint are
  the checks. The browser tools were not connected this session.
- `git diff --stat`: README.md +15, docs/install.md +27/-6, docs/guide/content.py +4/-2,
  docs/guide/render.py +5/-4, index.html 4 lines, plus this ledger and the plans index.
