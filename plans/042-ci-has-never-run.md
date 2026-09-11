# Plan 042: Make GitHub Actions actually run `python check.py` (it never has)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- .github/workflows/ci.yml`
> If the file changed since this plan was written, compare the "Current state"
> excerpts against the live file before proceeding; on a mismatch, treat it as a
> STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: dx
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

The repo's merge bar is `python check.py`, and `.github/workflows/ci.yml` is written to
run exactly that on every push to `main` and every PR across a 2-OS × 3-Python matrix.
But the GitHub Actions API reports **zero workflow runs, ever** for this public repo
(`gh api repos/A-H-911/tamheed/actions/runs --jq .total_count` → `0` on 2026-09-10), while
both workflows show as `active`. So every "CI is green" assumption in the program index is
unverified: the only verification that has ever happened is the maintainer's local
`python check.py` on Windows. Until CI runs once, no matrix change (plan 052) can be
evaluated, and a Linux-only failure (path separators, `newline=` handling, cp1252 vs
UTF-8) would ship unnoticed. This plan is an *investigation with one small change*: find
out why nothing ran, add a manual trigger so a run can be forced, and get one green run.

## Current state

- `.github/workflows/ci.yml` — the gate workflow. Triggers today:

  ```yaml
  # .github/workflows/ci.yml:11-14
  on:
    push:
      branches: [ main ]
    pull_request:
  ```

  Jobs: `check` (matrix `os: [ubuntu-latest, windows-latest]`, `python: ['3.10', '3.11', '3.12']`,
  step `python check.py`) and `server-smoke` (installs `uv` via `curl … | sh || true`, then
  `uv run plugins/tamheed/server/tamheed_server.py --selftest`, or prints a `::notice::` and
  SKIPS if uv is unavailable). There is **no `workflow_dispatch:`** trigger.
- `.github/workflows/eval.yml` — the scheduled behavioral-eval spec lint. Out of scope here.
- Repo facts (verified 2026-09-10): `gh repo view` → `A-H-911/tamheed`, default branch `main`,
  visibility `PUBLIC`; `gh workflow list` → `CI active 315231597`, `Behavioral evals (scheduled)
  active 315231598`; `git log` shows all work landing directly on `main` (no feature branches,
  no PRs), so the `push: branches: [main]` trigger *should* have fired on every release commit.
- Likely causes, in order of probability (you will test each):
  1. Actions disabled at the repository level (Settings → Actions → "Disable actions").
  2. Actions disabled at the account/org level, or the workflows were added on a branch/commit
     that GitHub never evaluated.
  3. The pushes were made in a way GitHub doesn't treat as `push` events (e.g. a mirror push
     with `--mirror`, or a `push --all` of a history whose workflow file predates enabling).
- Local baseline you can trust: `python check.py` prints `ALL CHECKS PASSED` on Windows with
  Python 3.13.7 (2026-09-10). Also verified green under `PYTHONWARNINGS=error::DeprecationWarning`.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Local gate | `python check.py` | last line `ALL CHECKS PASSED`, exit 0 |
| Run count | `gh api repos/A-H-911/tamheed/actions/runs --jq .total_count` | integer |
| Actions enabled? | `gh api repos/A-H-911/tamheed/actions/permissions --jq .enabled` | `true` |
| Workflow list | `gh workflow list` | two rows, both `active` |
| Force a run | `gh workflow run CI --ref main` | exit 0, run appears within ~30 s |
| Watch | `gh run list --workflow CI --limit 3` then `gh run watch <id>` | conclusion `success` |
| Failure logs | `gh run view <id> --log-failed` | text |

## Scope

**In scope** (the only files you should modify):
- `.github/workflows/ci.yml` — add `workflow_dispatch:` only.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- `.github/workflows/eval.yml` — scheduled, separate concern.
- The matrix, the `uv` install step, action versions — those are plan 052 and depend on this
  plan's result.
- `check.py`, `tests/**`, anything under `plugins/` — if CI reveals a real failure, that is a
  *report*, not a fix, in this plan (see STOP conditions).

## Git workflow

- The repo works directly on `main` (no branch convention). Make the one-line change on a local
  branch `advisor/042-ci-never-ran` if you prefer, but note that the `push` trigger only fires
  for `main`; a `workflow_dispatch` run can target any pushed ref.
- Commit message style is conventional commits, e.g. `ci: add workflow_dispatch so the gate can
  be forced (plan 042)`.
- **Pushing is required to test this plan and pushing is an operator action.** Do NOT push
  unless the operator instructed you to. If not instructed, finish Step 3, then stop and hand
  the push + Steps 4–6 to the operator with the exact commands.

## Steps

### Step 1: Confirm the premise

Run:

```
gh api repos/A-H-911/tamheed/actions/runs --jq .total_count
gh workflow list
```

**Verify**: first prints `0` (or a small number of *recent* runs if someone ran it since
2026-09-10 — if it prints a number > 0, read `gh run list --limit 10`; if there is already a
successful `CI` run on `main` newer than commit `7e3a92b`, mark this plan DONE with that run's
URL and skip the rest). Second prints two `active` workflows.

### Step 2: Check whether Actions is enabled for the repo

```
gh api repos/A-H-911/tamheed/actions/permissions
```

**Verify**: JSON with `"enabled": true`. If `"enabled": false` → this is the cause. Do not
change repository settings yourself; report to the operator: *"Actions is disabled for the
repository — enable it under Settings → Actions → General → 'Allow all actions and reusable
workflows', then re-run Steps 4–6."* Continue with Step 3 regardless (the dispatch trigger is
still needed).

### Step 3: Add the manual trigger

Edit `.github/workflows/ci.yml` so the `on:` block becomes exactly:

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
  workflow_dispatch:
```

Nothing else in the file changes.

**Verify**: `git diff --stat` → `1 file changed, 1 insertion(+)`; `python check.py` → last line
`ALL CHECKS PASSED` (check.py does not lint workflow files, but run it anyway — it is the habit
this repo enforces).

### Step 4 (operator, or executor if instructed): commit and push

```
git add .github/workflows/ci.yml
git commit -m "ci: add workflow_dispatch so the gate can be forced (plan 042)"
git push origin main
```

**Verify**: within ~60 s, `gh run list --workflow CI --limit 3` shows a run for the new commit
(the `push` trigger). If NO run appears after 2 minutes, run `gh workflow run CI --ref main`
and check again; if still nothing, Actions is disabled above the repo level — STOP and report.

### Step 5: Watch the run

```
gh run list --workflow CI --limit 1
gh run watch <run-id>
```

**Verify**: conclusion `success` for all six `check (py3.1x · <os>)` jobs. The `server-smoke`
job may print `::notice::uv unavailable … SKIPPED` — that is *allowed* by the current workflow
(plan 052 tightens it).

### Step 6: Record the outcome

In `plans/README.md`, set this plan's status to `DONE — first CI run <run URL>, <date>, <N>/6
check legs green`. If any leg failed, set `BLOCKED — <leg>: <first failing line from
gh run view <id> --log-failed>` and report the full failing output.

## Test plan

No code tests — the deliverable is a green run of the existing suite on Linux and Windows
runners. Keep the `gh run view <id> --log-failed` output verbatim in your report if anything
fails.

## Done criteria

- [ ] `.github/workflows/ci.yml` contains `workflow_dispatch:` under `on:` and nothing else changed
      (`git diff 7e3a92b -- .github/workflows/ci.yml` shows one added line)
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `gh api repos/A-H-911/tamheed/actions/runs --jq .total_count` → `>= 1`
- [ ] At least one `CI` run on `main` with conclusion `success` (URL recorded in the index row)
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- `ci.yml`'s `on:` block does not match the excerpt above (drift).
- Actions is disabled (`enabled: false`) — the operator must flip it; you cannot.
- No run appears after both a push and a `gh workflow run` — cause is above the repo level.
- A run fails on a `check` leg. Do **not** patch tests, `check.py`, or the bundle in this plan.
  Report the failing leg and the `--log-failed` output; the fix is a new plan.
- You were not instructed to push and Step 4 is reached — hand over to the operator.

## Maintenance notes

- Plan 052 (matrix + uv step) must not start until this plan's Step 5 has produced a green run;
  otherwise a matrix failure cannot be told apart from "CI still doesn't run".
- A reviewer should check that the *only* change is the trigger line — the point of this plan is
  evidence, not workflow redesign.
- If the cause turns out to be repository settings, record that in the index row so the next
  person who sees `total_count 0` on a fork knows where to look first.
