# Plan 016 (B12): Keystone close-out — successor banner, freeze policy, agent-findable migration path

> **Executor instructions**: This plan runs in the OLD repo (`C:\Users\ahammo\Repos\keystone`)
> and ONLY after Tamheed 2.0.0 has shipped (plan 014 done in the tamheed repo). Follow step by
> step; STOP conditions are binding. Update this plan's row in the tamheed repo's
> `plans/README.md` (authoritative index after the split).
>
> **Drift check (run first)**: the tamheed repo's CHANGELOG shows a released `[2.0.0]` and
> `docs/migrate-from-keystone.md` exists there (plan 010's runbook). Either missing → STOP:
> announcing a successor that isn't usable strands users.

## Status

- **Priority**: P3
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/014 (Tamheed 2.0.0 shipped)
- **Category**: docs / migration
- **Planned at**: commit `0e055f6`, 2026-07-11 (added in the new-repo-strategy revision)

## Why this matters

Per maintainer decision D-REPO-2, Keystone's end-state is **frozen + successor notice**: the v1
line (1.0.x) stays installable for existing packages, accepts critical fixes only, and every
surface an arriving human or AI agent hits must route them to Tamheed and the migration runbook
in one hop. Without this, the two-repo strategy leaves a live, unmarked v1 attracting new users —
and (W-R3) users with both marketplaces installed get two skills triggering on identical
planning phrases.

## Current state (keystone repo, post-Track-A)

- `README.md` — Tamheed-unaware v1 README (Track A's plan 004 fixed its lies; no successor info).
- `plugins/keystone/SKILL.md` — description (≈1010/1024 chars) triggers on generic planning
  phrases ("plan this project", "scope this out", …) — identical triggers to Tamheed's skill.
- `CHANGELOG.md` — latest released entry 1.0.x (Track A may have added 1.0.1).
- `.github/workflows/eval.yml` — weekly scheduled eval-spec lint still firing.
- No `MIGRATION.md`.

## Scope

**In scope**: `README.md` (banner block only), `plugins/keystone/SKILL.md` (description
frontmatter only), `CHANGELOG.md` (`[Unreleased]` note), new `MIGRATION.md`,
`.github/workflows/eval.yml` (schedule — pending the Step 4 operator choice).

**Out of scope**: archiving the repo (later operator decision); ANY behavior change in scripts,
templates, schemas, references (frozen v1 contract); rewriting README beyond the banner; the
tamheed repo (only its plans-index row gets updated).

## Git workflow

- Branch: `docs/keystone-closeout`; one commit, e.g.
  `docs: mark Keystone superseded by Tamheed; freeze policy + migration pointer`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: README successor banner (first screen)

Insert directly under the logo/title block, before anything else:

```markdown
> ## Keystone v1 — maintenance mode · successor: [Tamheed](https://github.com/A-H-911/tamheed)
> Keystone v1 **keeps working** for projects that use it (critical fixes continue). Its v2
> successor, [Tamheed](https://github.com/A-H-911/tamheed), is recommended for **new** projects
> (`/plugin marketplace add A-H-911/tamheed`). Moving an existing project to Tamheed is **your
> decision as the project operator** — when you choose to, follow the
> [agent migration runbook](https://github.com/A-H-911/tamheed/blob/main/docs/migrate-from-keystone.md)
> or see [MIGRATION.md](MIGRATION.md).
```

**Verify**: banner renders in the first screen of the GitHub README preview; both links resolve
(HTTP 200).

### Step 2: MIGRATION.md (the one-hop pointer for agents landing here)

Create `MIGRATION.md` (~15 lines): what changed (repo split, v2 = DB-backed packages via MCP),
how an AI agent detects a Keystone package (`manifest.json` + `keystone-state.json` in the
project, or the keystone plugin installed), and the single instruction: read + follow the
tamheed runbook (absolute URL as in Step 1). No duplicated runbook content — one hop, one source
of truth.

**Verify**: file exists; contains the absolute runbook URL; contains no step-by-step migration
detail (that lives in tamheed).

### Step 3: SKILL successor hint (D-REPO-5 — hint, never force)

**Governing rule (maintainer directive, 2026-07-11):** the v1 skill must remain **fully
available and working** for projects currently using it — its triggers stay intact, its behavior
unchanged. Moving to Tamheed is the **project operator's decision**; Keystone's job is to
surface the hint, once, politely.

Two changes to `plugins/keystone/SKILL.md`:

1. **Description**: keep the existing trigger text; ADD one sentence (trimming elsewhere as
   needed — current length is ≈1010/1024 chars, so make room first):
   `Note: Tamheed (github.com/A-H-911/tamheed) is the v2 successor — consider it for new
   projects; migrating an existing package is the operator's decision (see MIGRATION.md).`
2. **Body — a "Successor notice" instruction block** (near the top, after Requirements): when
   the skill is invoked, inform the operator ONCE per session that Keystone v1 is in
   maintenance and Tamheed v2 exists, with the MIGRATION.md pointer — then proceed normally.
   Explicit rules in the block: never auto-migrate, never repeat the notice in the same
   session, never block or degrade v1 work because the hint was declined.

**Verify**: description ≤1024 chars (`python -c` length check on the frontmatter string);
original trigger phrases still present (`grep -c "plan this project" plugins/keystone/SKILL.md`
→ ≥1); the body block contains "operator" and "never auto-migrate";
`python tests/test_validate_package.py` → exit 0 (nothing mechanical touched).

### Step 4: disable eval.yml's weekly schedule (RESOLVED — maintainer, 2026-07-17)

Delete the `schedule:` block from `.github/workflows/eval.yml`; keep `workflow_dispatch` so the
lint remains manually runnable. No operator question needed — the choice is recorded.

**Verify**: `grep -c "schedule:" .github/workflows/eval.yml` → 0 and
`grep -c "workflow_dispatch" .github/workflows/eval.yml` → ≥1; CI on the PR is the YAML-validity
check.

### Step 5: CHANGELOG + freeze policy

`CHANGELOG.md` `[Unreleased]`: record the supersession, the freeze policy (v1 = 1.0.x, critical
fixes only), and the pointer to tamheed. Do not touch released entries.

**Verify**: keystone CI green on the branch (suite + goldens 0/0/1/1 — proves the v1 line still
installs and validates).

## Done criteria

- [ ] Banner first-screen; all links resolve
- [ ] MIGRATION.md = one-hop pointer, no duplicated content
- [ ] SKILL description ≤1024 chars WITH original triggers intact + the successor note; body
      carries the once-per-session hint block with the never-auto-migrate rule
- [ ] eval.yml matches the operator's recorded choice
- [ ] CI green; only in-scope files changed
- [ ] Row updated in the tamheed repo's `plans/README.md`

## STOP conditions

- Drift check fails (Tamheed 2.0.0 not actually shipped / runbook missing).
- The successor note can't fit in the description's ≤1024 chars without cutting trigger
  phrases — report with your best candidate text; trigger phrases win over note wording.
- Anyone asks this plan to change v1 behavior "while you're in there" — out of scope, report.

## Maintenance notes

- Archiving keystone (GitHub read-only) is a separate future operator decision — revisit once
  migration traffic dies down; nothing in this plan blocks it.
- Critical-fix policy: fixes land on 1.0.x ONLY for defects that break existing v1 package
  validation/resume — everything else is answered with the migration pointer.
