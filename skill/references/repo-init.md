# Repository initialization

Stage 18 turns the package into a usable initial repository using `../scripts/init_skill_repo.py` (Python
primary; `init_skill_repo.sh` / `.ps1` are thin wrappers). The script **creates a real repo**, not just
printed instructions — but defaults to safe behavior.

## Safety contract

- **Dry-run by default consideration:** always offer/þrun `--dry-run` first and show the user the plan.
- **No overwrite without `--force`:** existing files are never clobbered silently; a dirty/non-empty target
  is refused unless `--force`.
- **Idempotent where practical:** re-running on an initialized repo is safe (skips existing, reports).
- **Validate prerequisites:** checks for `git` (required) and `gh` (only if `--create-remote`); fails
  clearly listing what's missing.
- **Provider-neutral:** local `git init` always works; remote creation is an optional, swappable step
  (GitHub via `gh` by default). No GitHub-only assumptions in the local path (safeguard 14).

## What it creates

Local repo dir; `git init`; the agreed folder structure; baseline files; `README.md` (referencing the
logo); logo assets copied to `docs/assets/`; `.gitignore`; `.gitattributes`; `LICENSE` (selected or
placeholder); `CONTRIBUTING.md`; code-of-conduct placeholder; issue + PR templates; `adrs/`; docs dirs;
skill + command dirs; schema + template dirs; example + test dirs; `CHANGELOG.md`; version metadata; an
initial commit; and — only with `--create-remote` — the remote repo, origin, and an initial push.

## Flags

`--repo-name`, `--owner`, `--visibility {private|public}`, `--default-branch`, `--license`, `--dry-run`,
`--force`, `--no-remote`/`--create-remote`, `--target-dir`. The script prints a final execution summary
(created / skipped / would-create in dry-run).

## When to run vs hand off

If the user wants Keystone to set up the repo now, run it (after a dry-run review and explicit approval for
any remote/push — those are side-effectful). If the user prefers to bootstrap themselves, deliver the script
+ the suggested invocation in the handoff and don't execute it. Never create a remote or push without
explicit approval in the conversation.
