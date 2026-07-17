#!/usr/bin/env python3
"""Bootstrap a GitHub-ready repository for a Keystone-style skill + slash command.

This script creates a *real*, usable repository on disk: it runs ``git init``,
lays down the agreed folder structure, writes baseline governance files
(README, LICENSE, CONTRIBUTING, CHANGELOG, issue/PR templates, a seed ADR,
etc.), and makes the initial commit. Remote creation/push is an explicit,
opt-in step (GitHub via ``gh``) so the local path is fully provider-neutral and
works with no network and no ``gh`` installed.

Standard library only (Python 3.9+). No third-party dependencies.

Safety model
------------
- ``--dry-run`` prints every planned action and writes *nothing*.
- A non-empty / dirty target directory is refused unless ``--force``.
- An existing file is never overwritten unless ``--force`` (otherwise skipped
  and reported). Re-running on an initialized repo is therefore idempotent.
- Prerequisites are validated up front: ``git`` is always required; ``gh`` is
  required only when ``--create-remote`` is requested. Missing tools cause a
  clear, listed failure with a non-zero exit code.
- The remote repo is created/pushed only when ``--create-remote`` is passed.

Suggested invocation
---------------------
    python scripts/init_skill_repo.py \\
        --repo-name keystone \\
        --owner <github-owner-or-org> \\
        --visibility private \\
        --default-branch main \\
        --license MIT

Add ``--dry-run`` first to preview, then re-run without it to apply. Add
``--create-remote`` only when you intend to create and push to GitHub.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Callable, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_VERSION = "0.1.0"
COMMIT_MESSAGE = "chore: bootstrap keystone skill repo"

# A repository name must be a single, safe path segment. This blocks path
# traversal (CWE-22): a value like "../../etc" or an absolute path would
# otherwise escape --target-dir when building <target-dir>/<repo-name>.
REPO_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def validate_repo_name(repo_name: str) -> Optional[str]:
    """Return a human-readable problem string if repo_name is unsafe, else None."""
    if not repo_name or not REPO_NAME_RE.match(repo_name):
        return ("invalid --repo-name " + repr(repo_name) + ": must be a single path "
                "segment matching [A-Za-z0-9._-]+ (no '/', '\\', or other separators).")
    if repo_name in {".", ".."}:
        return "invalid --repo-name: '.' and '..' are not allowed."
    return None

# Directories created in the generated repo. Each gets a `.gitkeep` if it would
# otherwise be empty (i.e. no baseline file is written into it below).
#
# Two layouts (see --layout):
#   plugin  (default) — a self-contained Claude Code plugin bundle under
#                       plugins/<name>/, plus a repo-root marketplace. This is how
#                       Keystone itself ships and the only layout that installs as
#                       a plugin without restructuring.
#   classic           — the older skill/ + commands/ top-level layout, kept for
#                       projects that are not Claude Code plugins.
CLASSIC_DIRECTORIES: List[str] = [
    "skill",
    "skill/references",
    "commands",
    "templates",
    "schemas",
    "scripts",
    "docs",
    "docs/assets",
    "examples",
    "tests",
    "adrs",
    ".github",
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
]


def plugin_directories(repo_name: str) -> List[str]:
    """Self-contained plugin bundle layout: everything the skill reads at runtime
    lives under plugins/<name>/ with zero outward references."""
    base = "plugins/" + repo_name
    return [
        ".claude-plugin",
        base,
        base + "/.claude-plugin",
        base + "/references",
        base + "/templates",
        base + "/schemas",
        base + "/scripts",
        base + "/assets",
        "docs",
        "docs/assets",
        "examples",
        "tests",
        "adrs",
        ".github",
        ".github/ISSUE_TEMPLATE",
        ".github/PULL_REQUEST_TEMPLATE",
    ]


def repo_directories(layout: str, repo_name: str) -> List[str]:
    return plugin_directories(repo_name) if layout == "plugin" else CLASSIC_DIRECTORIES

# SPDX license ids we ship full text for. Anything else gets a clear placeholder.
SPDX_FULL_TEXT = {"MIT"}


# --------------------------------------------------------------------------- #
# Small result/colour helpers
# --------------------------------------------------------------------------- #

def _configure_stdio() -> None:
    """Best-effort: make stdout/stderr able to encode the glyphs we print
    (arrows, bullets, box-drawing) even on legacy code pages such as Windows
    cp1252, where the default would raise UnicodeEncodeError."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


_COLOR = _supports_color()


def _c(text: str, code: str) -> str:
    if not _COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def info(msg: str) -> None:
    print(_c("•", "36"), msg)


def ok(msg: str) -> None:
    print(_c("✓", "32"), msg)


def warn(msg: str) -> None:
    print(_c("!", "33"), msg)


def err(msg: str) -> None:
    print(_c("✗", "31"), msg, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Prerequisite checking
# --------------------------------------------------------------------------- #

def check_prereqs(create_remote: bool) -> List[str]:
    """Return a list of human-readable problems. Empty list == all good."""
    problems: List[str] = []

    if shutil.which("git") is None:
        problems.append(
            "git is required but was not found on PATH. Install Git: "
            "https://git-scm.com/downloads"
        )

    if create_remote and shutil.which("gh") is None:
        problems.append(
            "--create-remote was requested but the GitHub CLI (gh) was not "
            "found on PATH. Install it (https://cli.github.com/) and run "
            "`gh auth login`, or drop --create-remote to bootstrap locally only."
        )

    return problems


# --------------------------------------------------------------------------- #
# Git helpers
# --------------------------------------------------------------------------- #

def run_git(args: List[str], cwd: Path, dry_run: bool) -> Tuple[int, str]:
    """Run a git command. In dry-run mode, only print what *would* run."""
    printable = "git " + " ".join(args)
    if dry_run:
        info(f"[dry-run] would run: {printable}  (cwd={cwd})")
        return 0, ""
    info(f"running: {printable}")
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        err(f"git command failed ({printable}):\n{out.strip()}")
    return proc.returncode, out


def is_git_repo(path: Path) -> bool:
    git_dir = path / ".git"
    return git_dir.exists()


def working_tree_is_dirty(path: Path) -> bool:
    """True if `path` is a git repo with uncommitted changes."""
    if not is_git_repo(path):
        return False
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        # If we cannot determine status, be conservative and call it dirty.
        return True
    return bool(proc.stdout.strip())


# --------------------------------------------------------------------------- #
# Target directory safety
# --------------------------------------------------------------------------- #

def directory_is_nonempty(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.is_dir():
        return True  # a file where we want a dir: definitely "occupied"
    return any(path.iterdir())


def validate_target(target: Path, force: bool) -> List[str]:
    """Check target-directory safety. Returns blocking problems (empty == ok)."""
    problems: List[str] = []

    if target.exists() and not target.is_dir():
        problems.append(f"target path exists but is not a directory: {target}")
        return problems

    if directory_is_nonempty(target) and not force:
        # A pre-existing initialized repo is allowed (idempotent re-run); the
        # per-file skip logic protects existing content. We only block when the
        # target is non-empty *and* not already a git repo, OR is a dirty repo.
        if not is_git_repo(target):
            problems.append(
                f"target directory is not empty and is not a git repo: {target}\n"
                f"    Re-run with --force to write into it anyway (existing "
                f"files are still never overwritten without --force)."
            )
        elif working_tree_is_dirty(target):
            problems.append(
                f"target is a git repo with uncommitted changes: {target}\n"
                f"    Commit/stash first, or pass --force to proceed anyway."
            )

    return problems


# --------------------------------------------------------------------------- #
# Baseline file content
# --------------------------------------------------------------------------- #

MIT_LICENSE_TEMPLATE = textwrap.dedent(
    """\
    MIT License

    Copyright (c) {year} {holder}

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """
)

LICENSE_PLACEHOLDER_TEMPLATE = textwrap.dedent(
    """\
    {spdx} License

    Copyright (c) {year} {holder}

    This project is licensed under the {spdx} license (SPDX identifier: {spdx}).

    The full license text was not embedded by the bootstrap tool because only a
    curated set of licenses ship verbatim. Replace this file with the official
    text for {spdx}, available from https://spdx.org/licenses/{spdx}.html
    (or https://choosealicense.com/), before publishing or distributing.
    """
)


def license_content(spdx: str, holder: str, year: int) -> str:
    if spdx.upper() in SPDX_FULL_TEXT:
        return MIT_LICENSE_TEMPLATE.format(year=year, holder=holder)
    return LICENSE_PLACEHOLDER_TEMPLATE.format(spdx=spdx, year=year, holder=holder)


def plugin_description(repo_name: str) -> str:
    return repo_name + ": a reusable Claude Code skill, packaged as a self-contained plugin."


def marketplace_json_content(repo_name: str, owner: str) -> str:
    data = {
        "name": repo_name,
        "owner": {"name": owner or "the repository owner"},
        "plugins": [
            {
                "name": repo_name,
                "source": "./plugins/" + repo_name,
                "description": plugin_description(repo_name),
            }
        ],
    }
    return json.dumps(data, indent=2) + "\n"


def plugin_json_content(repo_name: str, owner: str, license_id: str) -> str:
    data = {
        "name": repo_name,
        "description": plugin_description(repo_name),
        "version": DEFAULT_VERSION,
        "author": {"name": owner or "the project authors"},
        "license": license_id,
    }
    return json.dumps(data, indent=2) + "\n"


def starter_skill_md_content(repo_name: str) -> str:
    return textwrap.dedent(
        f"""\
        ---
        name: {repo_name}
        description: >-
          One to three sentences on WHAT this skill does and WHEN to use it, written so
          the model can decide to invoke it. Keep under 1024 characters. Replace this.
        ---

        # {repo_name}

        Replace this body with your skill's methodology. `SKILL.md` is the always-loaded
        front door — keep it lean (under ~500 lines) and push on-demand depth into
        `references/`. Everything the skill reads at runtime must live inside this
        bundle (`plugins/{repo_name}/`) with no references pointing outside this
        directory, because Claude Code copies the plugin directory to a cache on install.

        ## How to use

        1. Edit this file and add reference files under `references/`.
        2. Put blank artifact forms in `templates/` and data shapes in `schemas/`.
        3. Put any tooling in `scripts/` (executed, not loaded into context).
        """
    )


def readme_content(repo_name: str, owner: str, layout: str) -> str:
    owner_line = f"`{owner}`" if owner else "the repository owner"
    if layout == "plugin":
        skill_path = f"plugins/{repo_name}/SKILL.md"
        refs_path = f"plugins/{repo_name}/references/"
        logo_src = f"plugins/{repo_name}/assets/logo.svg"
        kind = "a self-contained **Claude Code plugin** (the repo doubles as its own marketplace)"
        layout_block = textwrap.dedent(
            f"""\
            .claude-plugin/marketplace.json     # repo = marketplace; lists the one plugin
            plugins/{repo_name}/                 # THE BUNDLE — self-contained, copied intact on install
            ├─ .claude-plugin/plugin.json
            ├─ SKILL.md                          # always-loaded front door (the methodology)
            ├─ references/  templates/  schemas/  scripts/  assets/
            docs/                                # human-facing docs (not part of the bundle)
            examples/  tests/  adrs/  .github/
            """
        )
    else:
        skill_path = "skill/SKILL.md"
        refs_path = "skill/references/"
        logo_src = "docs/assets/logo.svg"
        kind = "a reusable **skill + thin entry-point wrapper**"
        layout_block = textwrap.dedent(
            """\
            skill/                 # SKILL.md + references/  (the methodology)
            commands/              # thin entry-point wrapper(s)
            templates/             # blank artifact templates
            schemas/               # machine-readable data shapes (JSON Schema)
            scripts/               # tooling (incl. this bootstrap script)
            docs/                  # documentation; docs/assets/ holds the logo
            examples/  tests/  adrs/  .github/
            """
        )
    return textwrap.dedent(
        f"""\
        <p align="center">
          <img src="{logo_src}" alt="{repo_name} logo" width="160" />
        </p>

        # {repo_name}

        {kind}, bootstrapped with the Keystone repository initializer. The skill carries
        the methodology and references; any external entry point is a thin wrapper that
        only invokes it.

        > Logo: see [`{logo_src}`]({logo_src}). Drop your own artwork there (same
        > filename) to rebrand.

        ## Layout

        ```
        {layout_block}```

        ## Getting started

        1. Read [`{skill_path}`]({skill_path}).
        2. Browse the references under [`{refs_path}`]({refs_path}).
        3. See [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR.

        ## Maintainers

        Owned by {owner_line}. See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
        [`CHANGELOG.md`](CHANGELOG.md).

        ## License

        See [`LICENSE`](LICENSE).
        """
    )


GITIGNORE_CONTENT = textwrap.dedent(
    """\
    # ---- Python ----
    __pycache__/
    *.py[cod]
    *$py.class
    *.egg-info/
    .eggs/
    build/
    dist/
    .venv/
    venv/
    env/
    .env
    .pytest_cache/
    .mypy_cache/
    .ruff_cache/
    .coverage
    htmlcov/
    .tox/

    # ---- Node ----
    node_modules/
    npm-debug.log*
    yarn-debug.log*
    yarn-error.log*
    pnpm-debug.log*
    .pnpm-store/
    dist/
    .cache/

    # ---- Editors / IDEs ----
    .idea/
    .vscode/
    *.swp
    *.swo
    *~

    # ---- OS ----
    .DS_Store
    Thumbs.db
    Desktop.ini
    """
)

GITATTRIBUTES_CONTENT = textwrap.dedent(
    """\
    # Normalize line endings on commit; check out native.
    * text=auto eol=lf

    # Explicit text types
    *.py     text diff=python
    *.md     text
    *.json   text
    *.yml    text
    *.yaml   text
    *.sh     text eol=lf
    *.ps1    text eol=crlf

    # Treat these as binary (no diff/merge munging)
    *.png    binary
    *.jpg    binary
    *.jpeg   binary
    *.gif    binary
    *.ico    binary
    *.pdf    binary
    """
)


def contributing_content(repo_name: str) -> str:
    return textwrap.dedent(
        f"""\
        # Contributing to {repo_name}

        Thanks for your interest in improving **{repo_name}**.

        ## Ground rules

        - Be respectful — see [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
        - Discuss substantial changes in an issue before opening a large PR.
        - Keep the methodology in the skill (`SKILL.md` + `references/`); any external
          entry point stays a *thin* wrapper that only invokes the skill.

        ## Development workflow

        1. Fork and create a feature branch (`feat/<short-description>`).
        2. Make focused commits with clear messages (Conventional Commits
           encouraged: `feat:`, `fix:`, `docs:`, `chore:`…).
        3. Add or update tests under `tests/` where applicable.
        4. Update `CHANGELOG.md` under the **Unreleased** heading.
        5. Open a PR using the template and link any related issues.

        ## Architecture decisions

        Significant, hard-to-reverse choices are recorded as ADRs in `adrs/`.
        Add a new `adr-NNNN-*.md` rather than editing an approved one in place.

        ## Reporting bugs / requesting features

        Use the issue templates under `.github/ISSUE_TEMPLATE/`.
        """
    )


def code_of_conduct_content() -> str:
    return textwrap.dedent(
        """\
        # Code of Conduct

        > **Placeholder.** Replace this with your project's adopted code of
        > conduct. A widely used starting point is the
        > [Contributor Covenant](https://www.contributor-covenant.org/).

        ## Our pledge

        We as members, contributors, and leaders pledge to make participation in
        our community a harassment-free experience for everyone.

        ## Expected behavior

        - Be welcoming, respectful, and considerate.
        - Give and gracefully accept constructive feedback.
        - Focus on what is best for the community.

        ## Reporting

        Replace this section with a real contact (email / form) for reporting
        unacceptable behavior before publishing.
        """
    )


def changelog_content(version: str) -> str:
    today = datetime.date.today().isoformat()
    return textwrap.dedent(
        f"""\
        # Changelog

        All notable changes to this project will be documented in this file.

        The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
        and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

        ## [Unreleased]

        ### Added
        - Initial repository scaffold (skill, command wrapper, templates, schemas,
          docs, tests, ADRs, governance files).

        ## [{version}] - {today}

        ### Added
        - Project bootstrapped from the Keystone repository initializer.
        """
    )


def bug_report_template() -> str:
    return textwrap.dedent(
        """\
        ---
        name: Bug report
        about: Report something that isn't working as expected
        title: "[bug] "
        labels: bug
        ---

        ## Summary

        A clear, concise description of the bug.

        ## Steps to reproduce

        1.
        2.
        3.

        ## Expected behavior

        What you expected to happen.

        ## Actual behavior

        What actually happened (include error output / logs).

        ## Environment

        - OS:
        - Version / commit:
        - Other relevant context:
        """
    )


def feature_request_template() -> str:
    return textwrap.dedent(
        """\
        ---
        name: Feature request
        about: Suggest an idea or enhancement
        title: "[feat] "
        labels: enhancement
        ---

        ## Problem / motivation

        What problem does this solve? Who benefits?

        ## Proposed solution

        Describe the change you'd like.

        ## Alternatives considered

        Other approaches you weighed and why you set them aside.

        ## Additional context

        Mockups, links, or references.
        """
    )


def pull_request_template() -> str:
    return textwrap.dedent(
        """\
        ## Summary

        What does this PR change and why?

        ## Related issues

        Closes #

        ## Type of change

        - [ ] Bug fix
        - [ ] New feature
        - [ ] Documentation
        - [ ] Refactor / chore

        ## Checklist

        - [ ] I updated `CHANGELOG.md` (Unreleased).
        - [ ] I added/updated tests where applicable.
        - [ ] I recorded any architecturally significant decision as an ADR.
        - [ ] The slash-command wrapper stays thin and delegates to the skill.
        """
    )


def seed_adr_content() -> str:
    today = datetime.date.today().isoformat()
    return textwrap.dedent(
        f"""\
        # ADR-0000: Record architecture decisions

        - Status: Accepted
        - Date: {today}

        ## Context

        We need a durable, reviewable record of the architecturally significant
        decisions made on this project — the choices that are costly to reverse
        or have broad blast radius — so that future contributors understand not
        just *what* was decided but *why*, and can revisit decisions with full
        context.

        ## Decision

        We will use **Architecture Decision Records (ADRs)**, stored as Markdown
        files in `adrs/` named `adr-NNNN-short-title.md`. Each ADR captures the
        context, the decision, and its consequences. ADRs are immutable once
        accepted: to change a decision we add a new ADR that supersedes the old
        one (the old record stays for history).

        This format follows Michael Nygard's original ADR pattern.

        ## Consequences

        - Significant decisions are discoverable in one place and travel with the
          code.
        - Reviewers and newcomers can trace rationale without archaeology.
        - There is a small, deliberate overhead to writing an ADR — applied only
          to decisions that warrant it (lightweight decisions live elsewhere).
        """
    )


def agents_md_content(repo_name: str) -> str:
    return textwrap.dedent(
        f"""\
        # AGENTS.md — standing operating context for {repo_name}

        Claude Code auto-loads `CLAUDE.md` at the repo root every session, and `CLAUDE.md` imports this
        file — so this is where the plan's non-negotiables keep governing the work after the one-time
        kickoff. The content lives here; `CLAUDE.md` is the loaded entry that pulls it in.

        ## The contract
        - The approved plan/spec is the contract — read it first (e.g. `docs/plan/` or the handoff
          package: charter, architecture, roadmap, acceptance criteria). Decisions in the ADRs are final;
          do not re-litigate settled decisions.

        ## Invariants — a violation requires a new ADR
        - Treat the project's invariants (see the invariant register in the plan) as non-negotiable.
          Breaking one is **not** a silent option: record a new ADR under `adrs/` (status Proposed) and
          stop for approval.

        ## Hard constraints
        - Respect the constraint register and the NFR thresholds in the plan (licenses, dependencies,
          performance, security). Refuse work that crosses them.

        ## Operating conventions
        - Work **acceptance-criteria-first**: pick an `AC-`, write the failing test, implement, repeat.
        - **Track as you go (every phase gate):** keep the acceptance criteria current (status +
          evidence), update the acceptance audit (verdict + evidence per `AC-`), append the progress log,
          regenerate the status report — then stop at the gate for review.
        - No phase starts with red CI; keep changes small and reviewable; record deviations as ADRs.
        """
    )


def claude_md_content() -> str:
    return textwrap.dedent(
        """\
        # CLAUDE.md

        Claude Code auto-loads this file every session. It **imports** `AGENTS.md` below — the standing
        operating context: the invariants (a violation requires a new ADR), the hard constraints, and the
        track-as-you-go conventions. Keep that context in force for the whole engagement.

        @AGENTS.md
        """
    )


def gitkeep_content() -> str:
    return (
        "# This file keeps an otherwise-empty directory under version control.\n"
        "# Remove it once real content is added.\n"
    )


# --------------------------------------------------------------------------- #
# Action planning
# --------------------------------------------------------------------------- #

class Action:
    """A single planned filesystem mutation."""

    DIR = "dir"
    FILE = "file"
    COPY = "copy"

    def __init__(
        self,
        kind: str,
        path: Path,
        content: Optional[str] = None,
        source: Optional[Path] = None,
    ) -> None:
        self.kind = kind
        self.path = path
        self.content = content
        self.source = source


def plan_actions(target: Path, args: argparse.Namespace) -> List[Action]:
    """Build the ordered list of filesystem actions (no side effects)."""
    actions: List[Action] = []

    directories = repo_directories(args.layout, args.repo_name)

    # 1) Directories.
    actions.append(Action(Action.DIR, target))
    for rel in directories:
        actions.append(Action(Action.DIR, target / rel))

    # 2) Baseline files (path -> content).
    year = datetime.date.today().year
    holder = args.owner or "the project authors"

    file_specs: List[Tuple[str, str]] = [
        ("README.md", readme_content(args.repo_name, args.owner, args.layout)),
        (".gitignore", GITIGNORE_CONTENT),
        (".gitattributes", GITATTRIBUTES_CONTENT),
        ("LICENSE", license_content(args.license, holder, year)),
        ("CONTRIBUTING.md", contributing_content(args.repo_name)),
        ("CODE_OF_CONDUCT.md", code_of_conduct_content()),
        ("CHANGELOG.md", changelog_content(DEFAULT_VERSION)),
        ("VERSION", DEFAULT_VERSION + "\n"),
        (".github/ISSUE_TEMPLATE/bug_report.md", bug_report_template()),
        (".github/ISSUE_TEMPLATE/feature_request.md", feature_request_template()),
        (
            ".github/PULL_REQUEST_TEMPLATE/pull_request_template.md",
            pull_request_template(),
        ),
        ("adrs/adr-0000-record-architecture-decisions.md", seed_adr_content()),
        ("AGENTS.md", agents_md_content(args.repo_name)),
        ("CLAUDE.md", claude_md_content()),
    ]

    # Plugin layout adds the marketplace + plugin manifests and a starter SKILL.md
    # so the bootstrapped repo installs as a Claude Code plugin with no restructuring.
    if args.layout == "plugin":
        base = "plugins/" + args.repo_name
        file_specs.extend([
            (".claude-plugin/marketplace.json",
             marketplace_json_content(args.repo_name, args.owner)),
            (base + "/.claude-plugin/plugin.json",
             plugin_json_content(args.repo_name, args.owner, args.license)),
            (base + "/SKILL.md", starter_skill_md_content(args.repo_name)),
        ])

    for rel, content in file_specs:
        actions.append(Action(Action.FILE, target / rel, content=content))

    # 3) .gitkeep for directories that received no baseline file.
    dirs_with_files = {(target / rel).parent for rel, _ in file_specs}
    for rel in directories:
        d = target / rel
        if d in dirs_with_files:
            continue
        actions.append(Action(Action.FILE, d / ".gitkeep", content=gitkeep_content()))

    # 4) Best-effort logo copy. In the plugin layout the logo belongs to the bundle
    #    (plugins/<name>/assets) so the bundle stays self-contained; classic keeps it
    #    in docs/assets. Either way the generated README points at the right path.
    assets_rel = (
        "plugins/" + args.repo_name + "/assets" if args.layout == "plugin" else "docs/assets"
    )
    for src in discover_logo_sources():
        dest = target / assets_rel / src.name
        actions.append(Action(Action.COPY, dest, source=src))

    return actions


def discover_logo_sources() -> List[Path]:
    """Find logo files in the bundle's assets dir, if any (best-effort)."""
    # This script lives at <bundle>/scripts/init_skill_repo.py, so the bundle's
    # logo assets are at <bundle>/assets.
    here = Path(__file__).resolve()
    candidates: List[Path] = []
    assets_dir = here.parent.parent / "assets"
    if assets_dir.is_dir():
        for f in sorted(assets_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".ico"}:
                candidates.append(f)
    return candidates


# --------------------------------------------------------------------------- #
# Action application
# --------------------------------------------------------------------------- #

class Stats:
    def __init__(self) -> None:
        self.created = 0
        self.skipped = 0
        self.would_create = 0


def apply_actions(actions: List[Action], args: argparse.Namespace, stats: Stats) -> None:
    """Execute (or, in dry-run, narrate) the planned actions."""
    for action in actions:
        if action.kind == Action.DIR:
            _apply_dir(action.path, args, stats)
        elif action.kind == Action.FILE:
            _apply_file(action.path, action.content or "", args, stats)
        elif action.kind == Action.COPY:
            _apply_copy(action.source, action.path, args, stats)


def _rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _apply_dir(path: Path, args: argparse.Namespace, stats: Stats) -> None:
    base = args._target
    if path.is_dir():
        # Already exists: nothing to do, not counted as skipped (dirs are cheap).
        return
    if args.dry_run:
        info(f"[dry-run] would create dir:  {_rel(path, base) or '.'}")
        stats.would_create += 1
        return
    path.mkdir(parents=True, exist_ok=True)
    ok(f"created dir:  {_rel(path, base) or '.'}")
    stats.created += 1


def _apply_file(path: Path, content: str, args: argparse.Namespace, stats: Stats) -> None:
    base = args._target
    exists = path.exists()

    if exists and not args.force:
        if args.dry_run:
            warn(f"[dry-run] would skip existing file:  {_rel(path, base)}")
        else:
            warn(f"skipped existing file:  {_rel(path, base)}")
        stats.skipped += 1
        return

    if args.dry_run:
        verb = "overwrite" if exists else "create"
        info(f"[dry-run] would {verb} file:  {_rel(path, base)}")
        stats.would_create += 1
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if exists:
        ok(f"overwrote file:  {_rel(path, base)}")
    else:
        ok(f"created file:  {_rel(path, base)}")
    stats.created += 1


def _apply_copy(source: Path, dest: Path, args: argparse.Namespace, stats: Stats) -> None:
    base = args._target
    exists = dest.exists()

    if exists and not args.force:
        if args.dry_run:
            warn(f"[dry-run] would skip existing asset:  {_rel(dest, base)}")
        else:
            warn(f"skipped existing asset:  {_rel(dest, base)}")
        stats.skipped += 1
        return

    if args.dry_run:
        info(f"[dry-run] would copy asset:  {source}  ->  {_rel(dest, base)}")
        stats.would_create += 1
        return

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        ok(f"copied asset:  {_rel(dest, base)}")
        stats.created += 1
    except OSError as exc:  # best-effort: never fatal
        warn(f"could not copy asset {source} -> {dest}: {exc}")


# --------------------------------------------------------------------------- #
# Git initialization, commit, and optional remote
# --------------------------------------------------------------------------- #

def init_git_repo(target: Path, args: argparse.Namespace) -> bool:
    """Initialize the repo (idempotent). Returns False on hard failure."""
    if is_git_repo(target):
        info(f"git repo already initialized at {target} (leaving as-is)")
        # Ensure the default branch name where practical (only if no commits yet).
        return True

    # `git init -b <branch>` needs Git >= 2.28; fall back if unsupported.
    code, out = run_git(["init", "-b", args.default_branch], target, args.dry_run)
    if code != 0 and not args.dry_run:
        warn("`git init -b` failed (older git?). Falling back to `git init` + checkout.")
        code, _ = run_git(["init"], target, args.dry_run)
        if code != 0:
            return False
        # Best-effort branch rename; ignore failure on empty repo.
        run_git(["symbolic-ref", "HEAD", f"refs/heads/{args.default_branch}"], target, args.dry_run)
    return True


def make_initial_commit(target: Path, args: argparse.Namespace) -> None:
    run_git(["add", "-A"], target, args.dry_run)

    if args.dry_run:
        info(f'[dry-run] would commit: "{COMMIT_MESSAGE}"')
        return

    # Avoid an empty/failed commit if there is nothing staged (idempotent re-run).
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(target),
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        info("nothing to commit (working tree clean) — skipping initial commit")
        return

    code, _ = run_git(["commit", "-m", COMMIT_MESSAGE], target, args.dry_run)
    if code != 0:
        warn(
            "initial commit failed. Configure git identity, e.g.:\n"
            '    git -C "%s" config user.email you@example.com\n'
            '    git -C "%s" config user.name "Your Name"\n'
            "then re-run, or commit manually." % (target, target)
        )


def create_remote(target: Path, args: argparse.Namespace) -> None:
    """Create the GitHub remote and push (only ever called with --create-remote)."""
    if not args.owner:
        warn("--create-remote requires --owner; skipping remote creation.")
        return

    repo_slug = f"{args.owner}/{args.repo_name}"
    gh_args = [
        "repo",
        "create",
        repo_slug,
        f"--{args.visibility}",
        "--source",
        ".",
        "--remote",
        "origin",
        "--push",
    ]
    printable = "gh " + " ".join(gh_args)

    if args.dry_run:
        info(f"[dry-run] would run: {printable}  (cwd={target})")
        return

    info(f"running: {printable}")
    proc = subprocess.run(["gh", *gh_args], cwd=str(target), capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        ok(f"created remote and pushed: {repo_slug}")
    else:
        err(f"`gh repo create` failed:\n{out.strip()}")
        warn("The local repo is fine; you can create/push the remote manually.")


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #

def print_summary(args: argparse.Namespace, stats: Stats, target: Path) -> None:
    print()
    print(_c("── Summary ─────────────────────────────────────────────", "1"))
    if args.dry_run:
        print(f"  Mode:           DRY RUN (nothing was written)")
        print(f"  Would create:   {stats.would_create}")
        print(f"  Would skip:     {stats.skipped} (existing files)")
    else:
        print(f"  Created:        {stats.created}")
        print(f"  Skipped:        {stats.skipped} (existing files, no --force)")
    print(f"  Target:         {target}")
    print(f"  Repo name:      {args.repo_name}")
    print(f"  Default branch: {args.default_branch}")
    print(f"  License:        {args.license}")
    print(f"  Layout:         {args.layout}")
    print(f"  Remote:         {'create + push' if args.create_remote else 'none (local only)'}")
    print()

    print(_c("── Next steps ──────────────────────────────────────────", "1"))
    if args.dry_run:
        print("  1. Review the planned actions above.")
        print("  2. Re-run without --dry-run to apply.")
        if not args.create_remote:
            print("  3. (Optional) add --create-remote to also create/push to GitHub")
            print("     (requires `gh` and explicit intent).")
    else:
        skill_md = (
            f"plugins/{args.repo_name}/SKILL.md" if args.layout == "plugin" else "skill/SKILL.md"
        )
        print(f"  1. cd {target}")
        print("  2. Inspect the tree and the initial commit: `git log --stat`")
        print(f"  3. Edit {skill_md} to define your skill.")
        if not args.create_remote:
            print("  4. Create a remote when ready, e.g.:")
            print(
                f"       gh repo create {args.owner or '<owner>'}/{args.repo_name} "
                f"--{args.visibility} --source . --remote origin --push"
            )
    print()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def default_target_dir() -> Path:
    """~/source/repos if its parent exists, else the current directory."""
    home_repos = Path.home() / "source" / "repos"
    if home_repos.parent.exists():
        return home_repos
    return Path(".").resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="init_skill_repo.py",
        description=(
            "Bootstrap a GitHub-ready repository for a Keystone-style skill + "
            "thin slash-command wrapper. Creates a real local repo; remote "
            "creation/push is opt-in via --create-remote."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              # Preview only (writes nothing):
              init_skill_repo.py --repo-name keystone --owner my-org --dry-run

              # Create the local repo and initial commit:
              init_skill_repo.py --repo-name keystone --owner my-org

              # Also create the GitHub remote and push (requires gh):
              init_skill_repo.py --repo-name keystone --owner my-org --create-remote
            """
        ),
    )
    parser.add_argument("--repo-name", default="keystone", help="Repository name (default: keystone)")
    parser.add_argument("--owner", default="", help="GitHub owner/org (required for --create-remote)")
    parser.add_argument(
        "--visibility",
        choices=["private", "public"],
        default="private",
        help="Remote repo visibility when created (default: private)",
    )
    parser.add_argument(
        "--default-branch",
        default="main",
        help="Initial branch name (default: main)",
    )
    parser.add_argument(
        "--license",
        default="MIT",
        help="SPDX license id (default: MIT). Full text embedded for MIT; "
        "others get a labelled placeholder.",
    )
    parser.add_argument(
        "--layout",
        choices=["plugin", "classic"],
        default="plugin",
        help="Repository layout. 'plugin' (default) scaffolds a self-contained "
        "Claude Code plugin bundle under plugins/<name>/ plus a repo-root "
        "marketplace.json + plugin.json (installs as a plugin with no "
        "restructuring). 'classic' scaffolds the older skill/ + commands/ "
        "top-level layout for non-plugin projects.",
    )
    parser.add_argument(
        "--target-dir",
        default=None,
        help="Parent directory for the repo (default: ~/source/repos if its "
        "parent exists, else current dir). The repo is created at "
        "<target-dir>/<repo-name>.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print every planned action and write nothing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow a non-empty/dirty target and overwrite existing files.",
    )

    remote = parser.add_mutually_exclusive_group()
    remote.add_argument(
        "--create-remote",
        dest="create_remote",
        action="store_true",
        help="Create the GitHub remote and push (requires gh; off by default).",
    )
    remote.add_argument(
        "--no-remote",
        dest="create_remote",
        action="store_false",
        help="Do not create any remote (default).",
    )
    parser.set_defaults(create_remote=False)

    return parser


def resolve_target(args: argparse.Namespace) -> Path:
    parent = (Path(args.target_dir).expanduser() if args.target_dir else default_target_dir()).resolve()
    target = (parent / args.repo_name).resolve()
    # Defense in depth (validate_repo_name is the primary guard): the repo must be
    # created directly inside the chosen parent, never above or beside it.
    if target.parent != parent:
        raise ValueError(
            "resolved target " + str(target) + " escapes parent " + str(parent)
            + " (check --repo-name)"
        )
    return target


def main(argv: Optional[List[str]] = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)

    # Validate the repo name before building any filesystem path (CWE-22).
    name_problem = validate_repo_name(args.repo_name)
    if name_problem:
        err(name_problem)
        return 2

    target = resolve_target(args)
    args._target = target  # used by apply helpers for relative display

    print(_c(f"Keystone repo bootstrap → {args.repo_name}", "1"))
    print(f"  target: {target}")
    if args.dry_run:
        print(_c("  (dry-run: no files will be written)", "33"))
    print()

    # 1) Prerequisites.
    prereq_problems = check_prereqs(args.create_remote)
    if prereq_problems:
        err("Prerequisite check failed:")
        for p in prereq_problems:
            print(f"    - {p}", file=sys.stderr)
        return 2

    # 2) Target safety (skipped in dry-run so users can preview anywhere).
    if not args.dry_run:
        target_problems = validate_target(target, args.force)
        if target_problems:
            err("Target directory is not safe to write to:")
            for p in target_problems:
                print(f"    - {p}", file=sys.stderr)
            return 3

    # 3) Plan + apply files/dirs.
    stats = Stats()
    actions = plan_actions(target, args)
    apply_actions(actions, args, stats)

    # 4) Git init + commit (idempotent).
    if not init_git_repo(target, args):
        err("git initialization failed; see output above.")
        return 4
    make_initial_commit(target, args)

    # 5) Optional remote (guarded — only with --create-remote).
    if args.create_remote:
        create_remote(target, args)

    # 6) Summary + exit.
    print_summary(args, stats, target)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        err("interrupted")
        sys.exit(130)
