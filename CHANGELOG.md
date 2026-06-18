# Changelog

All notable changes to Keystone are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Repackaged Keystone as a self-contained **Claude Code plugin**. The skill and everything it reads or
  invokes at runtime (templates, schemas, scripts, the artifact catalog, logos) now live in one bundle at
  `plugins/keystone/`, and the repository is its own plugin marketplace (`.claude-plugin/marketplace.json`).
- Install is now one step in Claude Code (`/plugin marketplace add` → `/plugin install`); the bundle is also
  portable as a standalone Agent Skill.
- Reframed the "thin wrapper" principle for the plugin model (the skill is the entry point inside Claude
  Code; the principle still governs external CLI/API/MCP/UI entry points).

### Added
- `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/install.md`, and `docs/design-decisions.md`.

### Fixed
- Self-containment: removed dangling runtime references to repo-root docs and the obsolete "vendor step";
  corrected a stale traceability-schema filename reference.
- `init_skill_repo.py` no longer crashes with `UnicodeEncodeError` on Windows consoles using a legacy code
  page — stdout/stderr are reconfigured to UTF-8 at startup.

### Removed
- Build-history documents from the initial side-task context (`adrs/`, `IMPLEMENTATION-PLAN.md`,
  `NAMING-OPTIONS.md`, `CRITICAL-REVIEW.md`, `ROADMAP.md`, `ACCEPTANCE-CRITERIA.md`) and the redundant
  standalone `commands/keystone.md` wrapper. Durable design rationale was distilled into
  `docs/design-decisions.md`.

## [0.1.0] - 2026-06-18

### Added
- Initial Keystone capability: the methodology, skill specification (`SKILL.md` + references), governance
  model, artifact templates, JSON schemas, the repository-bootstrap script, the package validator with its
  self-test, worked examples, and a demonstration generated package.
