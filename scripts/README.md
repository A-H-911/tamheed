# Keystone repository bootstrap

`init_skill_repo.py` initializes a GitHub-ready repository to host a
Keystone-style **skill + thin slash-command wrapper**. It creates a *real*,
usable repo on disk — `git init`, the agreed folder structure, baseline
governance files, and the initial commit — while defaulting to safe behavior.

The Python script is the single source of truth. `init_skill_repo.sh` and
`init_skill_repo.ps1` are thin wrappers that only locate an interpreter and
forward arguments; they contain no logic of their own.

## Suggested invocation

```bash
python scripts/init_skill_repo.py \
    --repo-name keystone \
    --owner <github-owner-or-org> \
    --visibility private \
    --default-branch main \
    --license MIT
```

Run it with `--dry-run` first to preview the plan, then re-run without the flag
to apply. Add `--create-remote` only when you intend to create and push to
GitHub.

```bash
# 1) Preview (writes nothing):
python scripts/init_skill_repo.py --repo-name keystone --owner my-org --dry-run

# 2) Apply locally (git init + initial commit, no remote):
python scripts/init_skill_repo.py --repo-name keystone --owner my-org

# 3) Also create + push the GitHub remote (requires gh, explicit intent):
python scripts/init_skill_repo.py --repo-name keystone --owner my-org --create-remote
```

Wrappers (same flags):

```bash
./scripts/init_skill_repo.sh   --repo-name keystone --owner my-org --dry-run   # POSIX
```

```powershell
.\scripts\init_skill_repo.ps1  --repo-name keystone --owner my-org --dry-run   # Windows
```

## Safety guarantees

- **Dry-run shows everything, writes nothing.** `--dry-run` prints every
  planned directory, file, copy, and git command, then exits without touching
  the filesystem.
- **No silent overwrites.** An existing file is never overwritten unless
  `--force` is given; otherwise it is skipped and reported. This makes
  re-running on an already-initialized repo **idempotent**.
- **Refuses unsafe targets.** A non-empty directory that is *not* a git repo,
  or a git repo with uncommitted changes, is refused unless `--force`.
- **Prerequisites validated up front.** `git` is always required; `gh` is
  required *only* when `--create-remote` is passed. Missing tools produce a
  clear, listed error and a non-zero exit code.
- **Provider-neutral by default.** The local repo is fully functional with no
  network and no `gh`. Remote creation/push is an explicit, opt-in step
  (`--create-remote`, GitHub via `gh`) and is the only side-effect that leaves
  your machine.

## Flag reference

| Flag | Default | Description |
|---|---|---|
| `--repo-name NAME` | `keystone` | Repository name; the repo is created at `<target-dir>/<repo-name>`. |
| `--owner OWNER` | _(empty)_ | GitHub owner/org. Required for `--create-remote`. |
| `--visibility {private,public}` | `private` | Visibility of the remote when created. |
| `--default-branch NAME` | `main` | Initial branch name (`git init -b`). |
| `--license SPDX` | `MIT` | SPDX license id. Full text embedded for `MIT`; other ids get a labelled placeholder pointing at the canonical text. |
| `--target-dir DIR` | `~/source/repos` if its parent exists, else `.` | Parent directory for the new repo. |
| `--dry-run` | off | Print the plan and write nothing. |
| `--force` | off | Allow a non-empty/dirty target and overwrite existing files. |
| `--create-remote` | off | Create the GitHub remote and push (requires `gh`). |
| `--no-remote` | on | Explicitly disable remote creation (the default). |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (including a completed dry-run). |
| `2` | Prerequisite failure (`git`, or `gh` when `--create-remote`). |
| `3` | Target directory unsafe (non-empty/dirty) without `--force`. |
| `4` | `git` initialization failed. |
| `130` | Interrupted (Ctrl-C). |

## What it creates

```
<repo>/
├── README.md            # references docs/assets/logo.svg
├── .gitignore           # Python + Node + editor + OS
├── .gitattributes       # line-ending normalization, binary types
├── LICENSE              # full MIT text, or a labelled SPDX placeholder
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md   # placeholder (replace before publishing)
├── CHANGELOG.md         # Keep a Changelog, [Unreleased]
├── VERSION              # 0.1.0
├── skill/               # SKILL.md lives here (you author it)
│   └── references/
├── commands/            # thin slash-command wrapper(s)
├── templates/
├── schemas/
├── scripts/
├── docs/
│   └── assets/          # logo.svg (copied from sibling docs/assets if present)
├── examples/
├── tests/
├── adrs/
│   └── adr-0000-record-architecture-decisions.md
└── .github/
    ├── ISSUE_TEMPLATE/  # bug_report.md, feature_request.md
    └── PULL_REQUEST_TEMPLATE/pull_request_template.md
```

Empty directories receive a `.gitkeep` so they are tracked. Logo assets found
in a sibling `docs/assets/` (next to this `scripts/` directory) are copied on a
best-effort basis. Finally the script runs `git add -A` and commits
`chore: bootstrap keystone skill repo`.
