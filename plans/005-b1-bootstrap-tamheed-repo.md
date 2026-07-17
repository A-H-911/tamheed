# Plan 005 (B1): Bootstrap the Tamheed repository (new repo carrying Keystone's history)

> **Executor instructions**: Follow step by step; verify each step; STOP conditions are binding.
> Update this plan's row in `plans/README.md` when done. Steps 2–3 create and populate a NEW
> repository — the old Keystone repo is modified by exactly ONE commit in this plan (Step 5's
> plans-index trim) and nothing else.
>
> **Drift check (run first)**: Track A (plans 001–004) merged in keystone AND `plans/` committed
> AND keystone tagged: `git -C <keystone> ls-files plans/ | wc -l` → ≥ 16;
> `git -C <keystone> status --porcelain` → empty; `git -C <keystone> tag -l v1.0.1` → the tag
> exists (maintainer 2026-07-17: v1.0.1 releases immediately after Track A, BEFORE this push,
> so the clone carries a released v1 state). Any failing = STOP.

## Status

- **Priority**: P1 (first Track B plan)
- **Effort**: M
- **Risk**: MED (new public surface; transfer completeness)
- **Depends on**: Track A complete + committed (001–004)
- **Category**: migration
- **Planned at**: commit `0e055f6`, 2026-07-11 (revised same day: new-repo strategy D-REPO-1..4)

## Why this matters

The maintainer decided (D-NAME + D-REPO revision, 2026-07-11) that Tamheed lives in a **new
repository** rather than renaming Keystone in place: the old repo stays intact for v1 users
(frozen later by plan 016), the new repo carries **full git history** (provenance, blame,
CHANGELOG continuity → Tamheed 2.0.0 versioning; and the frozen v1 validator/schemas/demo arrive
automatically as the migration contract — no vendoring). This plan is still deliberately the
*minimal mechanical* bootstrap — identifiers, manifests, directory, CI wiring, a one-line README
notice — the full prose rewrite belongs to plan 014.

## Current state

- Old repo: `A-H-911/keystone`, local at `C:\Users\ahammo\Repos\keystone`; bundle at
  `plugins/keystone/` (plugin.json `"name": "keystone"`, SKILL frontmatter `name: keystone`,
  description 1010/1024 chars); marketplace at `.claude-plugin/marketplace.json`;
  `evals/evals.json` `"skill": "keystone"` asserted by `.github/workflows/eval.yml:30`; CI
  invokes `plugins/keystone/scripts/validate_package.py` (3 places); merged PRs #1–#3 exist —
  therefore GitHub holds `refs/pull/*` for keystone.
- `plans/` (committed per drift check): 001–004 = Track A (keystone-side), 005–016 = Track B
  (tamheed-side after this plan), README.md = index.
- No `tamheed` repo exists yet.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Test suite (in whichever repo) | `python tests/test_validate_package.py` | exit 0 |
| Goldens | four validator runs (plan 001 table; tamheed paths after Step 3) | 0/0/1/1 |
| Transfer completeness | `git ls-remote tamheed` | all keystone branches + tags present |
| Eval-spec check | the `eval.yml` inline python | OK |

## Scope

**In scope**: creating `A-H-911/tamheed` + its local clone (sibling dir
`C:\Users\ahammo\Repos\tamheed`); inside tamheed: directory rename, manifests, SKILL name,
eval field, CI paths, invocation strings, minimal README banner, plans split, CHANGELOG note;
inside keystone: ONLY the `plans/README.md` trim commit.

**Out of scope**: README/docs prose rewrite (plan 014); keystone's successor banner / freeze /
SKILL-description deprecation (plan 016 — do NOT add them now; Tamheed isn't usable yet);
`docs/history/**` and released CHANGELOG entries (old name correct there — never rewrite
history); archiving anything.

## Git workflow

- Tamheed-side work on `main` of the fresh clone (first commits of the new repo's own era);
  commit style follows the inherited convention, e.g.
  `feat!: establish Tamheed — successor of Keystone (D-REPO-1..4)`.
- Keystone-side: one commit `docs: point Track B plans at the tamheed repo`.
- Pushing the new repo is inherent to this plan (Step 2). Do not push keystone unless the
  operator instructed it.

## Steps

### Step 1: Name-collision check

Search PyPI (`https://pypi.org/project/tamheed/`), GitHub (`gh search repos tamheed --limit 10`),
and the Claude plugin ecosystem for a conflicting `tamheed`. Record evidence in the commit
message body. Same-domain collision (another agent skill/plugin or Python package) → STOP.

### Step 2: Create the new repo and push full history

**Do NOT use `git push --mirror`** — keystone's merged PRs mean GitHub holds `refs/pull/*`,
which are hidden refs on a new repo; mirror-pushing them produces rejections. Instead:

```text
gh repo create A-H-911/tamheed --public           # PUBLIC from day one (maintainer, 2026-07-17)
git -C C:\Users\ahammo\Repos\keystone remote add tamheed https://github.com/A-H-911/tamheed.git
git -C C:\Users\ahammo\Repos\keystone push tamheed --all
git -C C:\Users\ahammo\Repos\keystone push tamheed --tags
git clone https://github.com/A-H-911/tamheed.git C:\Users\ahammo\Repos\tamheed
git -C C:\Users\ahammo\Repos\keystone remote remove tamheed
```

**Verify**: `git -C C:\Users\ahammo\Repos\tamheed log --oneline -5` shows keystone's history
(HEAD lineage includes `0e055f6`); `git ls-remote https://github.com/A-H-911/tamheed.git` lists
every keystone branch + tag; `git -C C:\Users\ahammo\Repos\tamheed ls-files plans/ | wc -l` ≥ 16.
Hidden-ref (`refs/pull`) rejections during push are NOT a failure; missing branches/tags ARE.

### Step 3: Mechanical rename inside the tamheed clone

All remaining steps run in `C:\Users\ahammo\Repos\tamheed` (Track B executors open sessions
THERE from now on):

- `git mv plugins/keystone plugins/tamheed`; update `"name"` in
  `plugins/tamheed/.claude-plugin/plugin.json` and the plugin entry in
  `.claude-plugin/marketplace.json`; SKILL.md frontmatter `name: tamheed`.
- Re-point every path: `git grep -n "plugins/keystone"` → update all hits in
  `tests/test_validate_package.py`, `tests/README.md`, `.github/workflows/ci.yml`, `CLAUDE.md`,
  intra-bundle self-references.
- `evals/evals.json` `"skill": "tamheed"`; `eval.yml` assertion to match; invocation strings in
  SKILL.md (`/keystone:keystone` → `/tamheed:tamheed`, `/keystone` → `/tamheed`).
- README: retitle to Tamheed and add the notice line (this is the user-required old-repo
  reference; full rewrite is plan 014):
  "**Tamheed** — successor of [Keystone](https://github.com/A-H-911/keystone) (formerly this
  codebase, ≤ v1.0.x). Keystone remains available for existing v1 packages; migration guide
  coming with v2.0.0.
  ⚠ **v2 under construction** — the docs below describe the system being built; see `plans/`
  for the program."
  (The WIP line exists because the repo is public from day one — visitors land before plan
  014's real README ships.)
- CHANGELOG `[Unreleased]`: note the repo split + new install commands
  (`/plugin marketplace add A-H-911/tamheed` → `/plugin install tamheed@tamheed`).
- Assets: update `<text>` wordmarks in the SVGs if trivial; else note "assets deferred to plan
  014" in the commit body.

**Verify** (in tamheed): `git grep -c "plugins/keystone" -- ':!docs/history' ':!CHANGELOG.md' ':!plans'`
→ 0; test suite exit 0; goldens 0/0/1/1 (new paths); eval-spec check OK; SKILL description
≤1024 chars.

### Step 4: Plans split — tamheed side

In tamheed: `git rm plans/001-* plans/002-* plans/003-* plans/004-*`; edit `plans/README.md` —
keep rows 005–016, replace the Track A rows with one line: "Track A (001–004) lives in the
[keystone repo](https://github.com/A-H-911/keystone) and ships as Keystone 1.0.1." Mark THIS
plan's row DONE in the tamheed copy when finished.

**Verify**: `ls plans/` in tamheed → 005–016 + README (13 files).

### Step 5: Plans split — keystone side (the one permitted old-repo commit)

In keystone: edit `plans/README.md` only — Track B rows (005–016) collapse to a pointer block:
"Track B executes in the [tamheed repo](https://github.com/A-H-911/tamheed) (see its `plans/`);
decisions and order unchanged." Commit.

**Verify**: `git -C <keystone> status --porcelain` → only `plans/README.md` modified then clean
after commit; keystone test suite still exit 0 (nothing else touched).

### Step 6: Residual-name sweep (worklist for plan 014)

In tamheed: `git grep -ln "keystone" -- ':!docs/history' ':!CHANGELOG.md' ':!plans'` — remaining
hits must be prose scheduled for plan 014 or historical text. Record the list in the commit
message body.

## Test plan

No new tests — the inherited suite + goldens + eval-spec check are the regression net for a
mechanical bootstrap.

## Done criteria

- [ ] `A-H-911/tamheed` exists; full history verified (`ls-remote` + log lineage)
- [ ] Bundle at `plugins/tamheed/`; all names/paths/invocations updated; suite + goldens green in tamheed
- [ ] README notice references the keystone repo (user requirement)
- [ ] Plans split complete on both sides; keystone touched by exactly one commit
- [ ] Residual-hits list recorded for plan 014
- [ ] `plans/README.md` rows updated (tamheed copy authoritative from now on)

## STOP conditions

- Same-domain name collision (Step 1).
- `ls-remote` shows missing branches/tags after Step 2 (hidden-ref rejections alone are fine).
- Keystone dirty or `plans/` uncommitted at push time (drift check).
- SKILL.md description exceeds 1024 chars after edits.

## Maintenance notes

- Plan 014 owns the full prose/diagram/asset rewrite (hand it Step 6's list); plan 016 owns every
  keystone-side successor/freeze change — resist doing them early; Tamheed must ship first.
- The old repo's `refs/pull/*` history stays on GitHub with keystone — PR discussion links in
  commit messages keep resolving there; that's correct and expected.
