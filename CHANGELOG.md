# Changelog

All notable changes to Tamheed are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Lineage.** Entries ≤ 1.0.x record this project under its former name, **Keystone**, in its
> original repository (<https://github.com/A-H-911/keystone>). Tamheed carries Keystone's full git
> history; the Keystone repository stays frozen at 1.0.x for existing v1 packages.

## [Unreleased]

## [2.3.0] - 2026-07-22

Third field-report hardening (plan 019; evidence **C20–C22** from the v2.2.0 ACMP
re-migration — a clean regression pass: zero repair loops, verdict "Ship it"; archived at
`plans/evidence/acmp-field-report-3-2026-07-22.md`). **No schema migration — existing 2.x
packages are unaffected.**

### Added
- **Managed emissions (C20):** every file `handoff_emit` writes (handoff prompts, the
  scenario prompt library, `.mcp.json`) reports as `written`/`unchanged`/`diverged` — a
  hand-edited file is refused, never silently clobbered; `force=true` replaces it
  deliberately. The stale-v1 warning now lives in a `<!-- tamheed:stale-warning -->` marker
  block that **retracts itself** once the scan is clean — re-running `handoff_emit` is the
  standing "is the cutover done?" verifier. (Note: warnings emitted by pre-2.3.0 versions
  lack markers — hand-remove those once.)
- **Restated-content tripwire (C22):** register content copied into `CLAUDE.md`/`AGENTS.md`
  (≥3 consecutive id-led bullets/table rows, or a hard-coded audit tally) is reported as
  `restated_content` — `unlabeled` copies get a suggested reference rewrite; blocks that
  already cite `entity_query`/`review.html`/`gate_run` are classified `labeled-snapshot`
  and asked only to verify currency. Single ids in prose and product-domain words never
  fire. Doctrine documented: reference, don't restate; state each fact once.
- **Grouped migration ledgers (C21):** `status_coerced_groups` and grouped
  `title_fallbacks` (the operator decision unit is the group — 21 coercions ≈ 6 decisions);
  `status_defaulted` ledger for registers with no status column; `status_coerced_basis`
  annotation (defaults vs supplied `status_map`).
- The three-prompt-surface sync model documented (`references/handoff.md`); the canonical
  byte-stability guarantee stated as contract (`db/CANONICAL.md`).

### Changed
- Migration: registers with **no status column** default their rows to `Approved` (parity
  with weak-definition synthesis; decisions stay `Proposed`) — reported per (file, family)
  in `status_defaulted`. Compound literals documented as valid `status_map` keys; v1
  progress logs documented as narrative-only mapping.
- Viewer: **every table folds closed** behind `<details>` with the count in the summary —
  one consistent affordance replaces the 50-row threshold. Sole exception: gap/screening
  warning cards stay visible (they exist to be seen).
- All emitted/reported paths use forward slashes on every platform.

## [2.2.0] - 2026-07-22

Second field-report hardening (plan 018; evidence **C17–C19** from the first *successful*
production migration — the ACMP run under v2.1.0, verdict "production-quality"; archived at
`plans/evidence/acmp-field-report-2-2026-07-22.md`). **No schema migration — existing 2.x
packages are unaffected.**

### Added
- **Preview honesty ledgers (C17):** `status_coerced` — every v1 status word outside the
  lifecycle vocabulary is reported with its proposed mapping (semantic defaults:
  `Resolved→Implemented`, `Open`/`Monitoring`/`Active`→`Approved`, `Closed→Obsolete`); the
  operator confirms or overrides via `package_migrate(..., status_map={...})`. Plus
  `title_fallbacks`, per-file `partial_files` row counts, and the frozen validator's
  sha256+size in the pre-flight result.
- **Scenario prompt library (C19):** five ready-to-paste prompts (orient-resume with a
  git-history cross-check, progress-sync, integrity-check, generate-report, slice-review)
  ship in the bundle and are emitted into `<package>/prompts/` by migrate, adopt, and
  `handoff_emit`.
- **Cutover tooling (C19):** `handoff_emit(target_dir, subdir=…)`; a full operating-context
  `CLAUDE.md` note with an MCP tool cheat-sheet; a `stale_references` report (v1-flow
  pointers in `CLAUDE.md`/`AGENTS.md` as file:line + suggested replacement — the bare word
  "Keystone" is never flagged).
- **Viewer navigation & scale (C18):** sticky zero-JS section TOC; register families over 50
  rows and the raw trace-edge dump fold behind `<details>`; wide tables now actually scroll
  horizontally; migrated package metadata labeled `(v1-manifest-derived)`.
- `entity_query` returns `total` beside the LIMIT'd rows.

### Changed
- Migration: ADR/experiment/POC parse failures and unknown diagram stems now fall through to
  the narrative catch-all (preserved as documents, still listed in `unmapped`); narrative
  documents keep their full v1 front matter in `custom_attributes`; title aliases never
  resolve to the id column.
- Viewer freshness: a package with no recorded v2 activity says so ("package record dated …;
  no v2 activity recorded yet") instead of presenting the v1 manifest date as activity.
- `handoff_emit` on plugin-hosted servers no longer writes a project `.mcp.json` entry (the
  installed plugin already registers the server; the old emit hard-coded a machine- and
  version-specific plugin-cache path).
- Operator-facing tool descriptions de-jargoned.

## [2.1.0] - 2026-07-21

Field-report hardening (plan 017; evidence **C11–C16** from the first production v1→v2
migration — the ACMP run, archived at `plans/evidence/acmp-field-report-2026-07-21.md`).
**No schema migration — existing 2.x packages are unaffected by upgrade**; every fix is
code-level and applies the moment a package is opened.

### Added
- `server_info` tool: plugin version (single source: the bundled `plugin.json`), resolved
  package root, open package, migrations head — makes startup diagnosable (C11/C16).
- `package_migrate(allow_zero=[...], patch=<file>)`: the family-zero tripwire (a family
  parsing to zero against a nonzero manifest count blocks populate until acknowledged) and
  the blessed parse→patch→populate repair path (D1), both echoed in the preview.
- Preview parity (C13): parsed-vs-manifest `count_deltas`, `zero_families`, and the
  `partial_files`/`skipped_files` loss ledgers are computed **before** the operator confirm.
- v1 dialect tolerance (C12): MADR ADRs without front matter (heading id + `- Status:`
  bullet; "Decision Outcome" preferred over "Drivers"); `Given / When / Then`/`Criterion`
  AC aliases with uncapped statements; `Test ref` audit-evidence alias + verdict
  provenance; MoSCoW `M`/`Must` → `mvp=1`; `D-nn` deferred-work rows → governed `DW-`;
  catch-all `doc_kind='other'` narrative for zero-row unmatched files; `generated`
  manifest spelling; raw profile preserved; stale omissions dropped.
- Adopt fidelity (C13): `Cargo.toml` dependencies parsed; every extraction cap reported in
  the gap report; successful migrate/adopt results end with the cutover pointer (C15), and
  `handoff_emit` flags stale Keystone references in the target's CLAUDE.md.
- Tests: the v1-green **dialect-package** golden (the ACMP quirk profile) + a conservation
  meta-test that catches the next unknown parser fall-through; 25 new tests; a 7th eval
  scenario (`migrate-dialect-fixture`); a version-sync lint in `check.py`.

### Changed
- **Gate-behavior relaxations** (outcomes may change on existing packages, both toward
  honesty): `G-COMPLETE` strips code spans before the placeholder scan (parity with the
  frozen v1 gate) and exempts `custom_attributes` (provenance, not authored content —
  G-INJECT still screens it at emission); `gate_run` attaches an explicit warning when
  `G-TRACE` passes vacuously over zero MVP requirements (D-017-1).
- Package-root resolution is layered — explicit `--package-dir` > `CLAUDE_PROJECT_DIR` >
  cwd — the bundled `.mcp.json` passes `${CLAUDE_PROJECT_DIR}`, and every `package_*`
  result echoes the resolved absolute root (C11: a stdio server's cwd is not guaranteed).

### Fixed
- Windows MCP deadlock (C11): pre-flight runs the frozen v1 validator **in-process**
  (no subprocess from the stdio server) with crash isolation; adopt's git spawn gets
  `stdin=DEVNULL`.
- `promoted_to` FK crash (C12): only `ADR-*` tokens qualify; mixed-token cells store NULL
  plus an unmapped note instead of killing the whole populate.
- Populate failures name the exact table/row/constraint and remove the created `data/`
  dir so retries are never blocked by a poison directory.
- `entity_upsert` documents the full-row requirement and names the actual cause when a
  partial update of an existing row fails NOT NULL.
- The plugin manifest version skew (installs self-identified as 1.0.0 since the v2.0.0
  release) — `plugin.json` now reads 2.1.0 and the sync is lint-enforced.

## [2.0.0] - 2026-07-18

The v2 re-architecture (MAJOR — the storage, interaction, and review contracts all changed; see
**Migration** below). Program record: `plans/`.

### Changed
- **Repository split (D-REPO-1..4):** this repository is **Tamheed** (`A-H-911/tamheed`), the
  successor of Keystone, carrying Keystone's full git history. The plugin bundle moved to
  `plugins/tamheed/` and the plugin/marketplace/skill identifiers renamed to `tamheed`. Install:
  `/plugin marketplace add A-H-911/tamheed` then `/plugin install tamheed@tamheed`; invoke as
  `/tamheed:tamheed`. The old install commands (`marketplace add A-H-911/keystone`) remain valid
  only for **Keystone 1.0.x** at the old repository, which is frozen for existing v1 packages.
- **Storage contract (D-STORE, ADR-0001):** a package is no longer loose Markdown + a state file —
  it is a **relational store**: one SQLite-enforced entity table per artifact family, serialized as
  deterministic canonical JSONL (`data/*.jsonl`, spec in `plugins/tamheed/db/CANONICAL.md`) that the
  operator commits to git. Statuses are three-axis (`lifecycle_status`/`verdict`/`disposition`);
  approval-bearing rows are trigger-enforced immutable-after-approval; derived artifacts are SQL
  views, never stored snapshots; a single-writer lockfile makes concurrent writers fail loud.
- **Interaction contract (D-MCP):** every write goes through the **Tamheed MCP server**
  (`plugins/tamheed/server/`, official Python SDK, launched via `uv`/PEP 723 or `pip install mcp`) —
  the only write path into a package and the successor of the v1 validator: referential gates
  (G-IDS, G-DEC-STATUS, G-REQ-SRC) are schema constraints enforced at write time, coverage gates
  (G-TRACE, G-SET, G-PROGRESS) are SQL views run by `gate_run`, and `handoff_emit` injection-screens
  every emission. Batch mutations are all-or-nothing with per-item verdicts; there is no raw-SQL tool.
- **Review contract (D-REVIEW):** the human review surface is **HTML only** — `export_html` renders
  the package (gate chips, registers, traceability, execution progress, gap/screening notes) as one
  self-contained, escaped, script-free, deterministic `review.html`, committed alongside the data.
  Derived-Markdown snapshots are gone (they are exactly what froze and misled in v1 field use).
- **Update mode is the agile heart (D-UPDATE):** diff-aware re-derivation (`trace_query` the impact
  set, regenerate only dependents), execution-progress sync (`progress_update`, `audit_record` with
  evidence refs, `work_bind` stamping `last_referenced`), and **typed scope changes**
  (defer/reschedule/reclassify/cancel/expand) — the `scope-change` row is written before any
  mutation, and iteration bumps track `introduced_in`/`retired_in`.
- **Python floor raised to 3.10** (ASM-D): the MCP server depends on the official `mcp` SDK
  (`requires-python >= 3.10`); the CI matrix drops 3.9 (now 3.10–3.12 × ubuntu/windows). The frozen
  v1 validator itself still runs on 3.9, but this repository gates on 3.10+.
- **CI rebuilt around one command** (B10): CI job 1 runs exactly `python check.py` — the seven test
  suites, the v1 goldens (0/0/1/1), structure lint (tracked JSON, registry↔DDL sync, v1
  Always-mirror↔catalog sync), a canonical-form round-trip of the committed v2 demo, and the
  deterministic eval runner on its sample fixture. A second ubuntu-only job smokes the uv/PEP 723
  server launch (skips visibly if uv is unavailable). The behavioral eval spec gained *executable*
  deterministic assertions run by `evals/run_evals.py`; assertions with no v2 mechanical equivalent
  are recorded as `retired`, never silently dropped.

### Added
- **`migrate` mode** (`package_migrate`, B5): staged, operator-initiated import of a conformant v1
  Keystone package — pre-flight against the frozen v1 validator, dry parse report, one-transaction
  populate, post-flight fidelity check. Runbook: `docs/migrate-from-keystone.md`; mapping contract:
  `plugins/tamheed/references/migration-v1.md`. A migrated golden ships at
  `generated-samples/support-triage-agent-v2/`.
- **`adopt` mode** (`package_adopt`, B11): staged brownfield onboarding for projects that never used
  Tamheed — nothing inferred is ever Approved, provenance is code-shaped (`source_kind='code'` with
  file:line spans), injection-shaped repo content is fenced as data, and the gap report (what code
  cannot reveal) is a first-class output.
- **Execution-tracking surface:** slices under phases, acceptance-criteria audit verdicts with an
  evidenced-vs-narrated split, defect and deferred-work registers, execution gates, per-slice
  execution plans, durable conventions, progress journal, work bindings (`work_bind`) stamping
  per-entity `last_referenced`, and cascade-on-transition (all ACs of a requirement Met ⇒ the
  requirement auto-advances, in the same transaction).

### Removed
- **The repository bootstrapper** (`init_skill_repo.*`, ASM-B) and with it the `--no-repo` flag:
  a package is data the operator commits to whichever repository they choose; storage
  initialization is the server's `package_create`. Provider neutrality survives in the plan itself
  (safeguard 15).
- **The v1 state file** (`keystone-state.json`): the package *is* the state — `resume`/`update` are
  `package_open` + targeted queries.
- **The chat-only generation path:** environments without an MCP host can hold the planning
  conversation but cannot create or mutate a v2 package.
- **Derived document snapshots** (traceability matrix, status report, readiness report, backlog,
  handoff manifest as files): all are views/queries now, rendered in `review.html`.

### Migration
- v1 packages are **not** read by v2 tools directly. Migration is **operator-initiated, staged, and
  gated** (D-REPO-5): Keystone hints once per session, never forces, and agents never auto-migrate.
  Run `package_migrate(source_dir)` for the preview, then `confirm=True` to populate; the frozen v1
  contract (validator, JSON schemas, templates) stays in this repository as read-only migration
  inputs. Full runbook: `docs/migrate-from-keystone.md`.
- Identifiers survive migration unchanged (`FR-001` stays `FR-001`); v1 document content lands as
  narrative documents + sections; register rows land in their entity tables with provenance intact.
- Anything a v1 package recorded that v2 models differently (e.g. handoff-manifest fields) is
  absorbed into the package row or entity columns — the migration report itemizes every mapping.

## [1.0.0] - 2026-06-22

First stable release. The methodology, schemas, identifiers, and handoff contract are now stable; future
changes ship with a migration note per the versioning rules in `references/governance.md`.

### Changed
- **Downstream executor is now Claude Code (no longer agent-neutral).** Keystone targets **Claude Code**
  (CLI/IDE; cloud coworker acknowledged) as the agent that implements the plans it produces, because
  Keystone is itself a Claude Code plugin. The handoff layer leans into Claude Code: the **agent-control
  surface** is now `CLAUDE.md` **importing** `AGENTS.md` (the file Claude Code auto-loads — Anthropic's
  documented idiom) instead of the prior "AGENTS.md-canonical + CLAUDE.md-shim" pair; the initial /
  follow-up / review prompt templates reference plan mode, TodoWrite, subagents, and a code-review pass
  where useful (named as capabilities, never hard-depended on). Safeguard 13 ("coupling to one agent")
  and the Warn gate `G-COUPLING` are reframed: coupling to Claude Code is now an intentional *harness*
  choice. Updated `SKILL.md`, `README.md`, `plugin.json`/`marketplace.json`,
  `references/{safeguards,quality-gates,handoff,prompt-templates,workflow,artifact-catalog,artifact-rules}.md`,
  `docs/{methodology,workflow}.md`, the handoff templates, and `init_skill_repo.py`.
- **The produced plan stays portable.** Requirements, architecture, and ADRs remain vendor-, provider-,
  and stack-neutral (safeguard 15); the bootstrap stays repo-provider-neutral (safeguard 14). The
  coupling is at the harness layer only, never the architecture.

### Migration
- Packages generated under ≤0.2.0 (AGENTS.md-canonical, agent-neutral handoff) remain valid — no schema,
  identifier, required-artifact, or handoff-manifest-shape change, so the validator accepts them
  unchanged. New packages emit a root `CLAUDE.md` containing `@AGENTS.md` as the loaded standing-context
  entry, plus Claude-Code-targeted handoff prompts. To bring an existing package forward, add a root
  `CLAUDE.md` whose body is `@AGENTS.md`.

## [0.2.0] - 2026-06-22

### Added
- **Execution-tracking layer (Tarseem-inspired).** New mechanical gate **`G-PROGRESS`** in
  `validate_package.py` (acceptance-audit coverage: when an audit is present, every `AC-` carries a verdict
  from {Met, Partial, Not-met, Pending}; SKIPs when no audit exists). New **acceptance audit**
  (`templates/acceptance-audit.template.md` — a derived close-out: criterion → verdict × evidence) and a new
  **agent-control surface** (`templates/agent-control.template.md` → package-root `AGENTS.md` + a `CLAUDE.md`
  shim, also emitted by `init_skill_repo.py`): the agent-neutral, ambient standing context (invariants +
  violation⇒ADR, hard constraints, conventions, and the tracking protocol). Evidence columns added to
  work-breakdown / status-report / acceptance-criteria; optional `evidence` on
  `acceptance-criterion.schema.json` and `acceptance_refs` on `execution-phase.schema.json`. Initial +
  follow-up handoff prompts gained the AC-first/test-first loop, the track-as-you-go cadence, and new
  situational prompts (phase-exit summary, acceptance audit, spike/experiment report, defect log). README
  flow diagram + `CLAUDE.md` + `quality-gates.md` updated (6 → 7 gates). (additive / MINOR)
- **Gate `G-SET`** in `validate_package.py`: every "Always" artifact must be present on disk or recorded in
  `manifest.json` `omitted_artifacts[]` with a reason; the manifest must exist; nothing it declares present
  may be missing. This closes the gap where a hollow package (charter + README only) passed validation
  because every other gate SKIPped on the absent input. Backed by the new
  `references/required-artifacts.json` (machine mirror of the Always class) and a new
  `tests/fixtures/incomplete-package/` regression fixture. (audit AUDIT.md F-01/F-05)
- **Continuous integration** (`.github/workflows/ci.yml`): runs the validator test suite and validates the
  golden packages (valid, invalid, incomplete, demo) on every push/PR across Linux + Windows × Python
  3.9–3.12. (audit F-02)
- **Behavioral eval harness** (`evals/evals.json`, `evals/README.md`, `.github/workflows/eval.yml`): five
  with-skill/without-skill scenarios including a prompt-injection case, plus a scheduled, non-blocking
  eval-spec lint. (audit F-03)
- **`SECURITY.md`**: trust model, untrusted-content posture, and vulnerability reporting. (audit F-04)
- **`init_skill_repo.py --layout plugin|classic`** (default `plugin`): scaffolds a self-contained plugin
  bundle (`marketplace.json` + `plugin.json` + `plugins/<name>/SKILL.md`) that installs as a Claude Code
  plugin with no restructuring; `classic` keeps the older `skill/` + `commands/` layout. (audit F-08)
- `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/install.md`, and `docs/design-decisions.md`.

### Security
- Treat the project brief and any file content as **untrusted data, not instructions** (OWASP LLM01): new
  operating principle 10 in `SKILL.md`, safeguard 18 in `references/safeguards.md`, and a handoff-screening
  step (`references/handoff.md`, gate `G-INJECT`). (audit F-04)
- `init_skill_repo.py` validates `--repo-name` as a single safe path segment and asserts the resolved target
  stays inside `--target-dir`, blocking path traversal (CWE-22). (audit F-09)

### Changed
- Repackaged Keystone as a self-contained **Claude Code plugin**. The skill and everything it reads or
  invokes at runtime (templates, schemas, scripts, the artifact catalog, logos) now live in one bundle at
  `plugins/keystone/`, and the repository is its own plugin marketplace (`.claude-plugin/marketplace.json`).
- Install is now one step in Claude Code (`/plugin marketplace add` → `/plugin install`); the bundle is also
  portable as a standalone Agent Skill.
- Reframed the "thin wrapper" principle for the plugin model (the skill is the entry point inside Claude
  Code; the principle still governs external CLI/API/MCP/UI entry points).
- `quality-gates.md`: added the `G-SET` row and corrected mechanization labels — `G-TRACE` is now "Partly"
  (its behavior-bearing → `AC-` clause is judgment, not mechanized) and `G-COMPLETE` no longer claims to
  verify required-set membership (that is `G-SET`). (audit F-05)
- `SKILL.md`: dropped the non-recognized `compatibility:` frontmatter key (its content moved to a body
  **Requirements** line) and fixed the "GitHub CLT" → "GitHub CLI" typo. (audit F-07/F-11)
- `references/extension.md`: refreshed the stale `commands/` entry-point reference. (audit F-10)
- **Migration (MINOR):** `schemas/package-manifest.schema.json` `generation.mode` now matches the skill's
  invocation modes (`full | intake | plan | resume | update | stage:<id>`) instead of the divergent
  `quick/standard/deep/research/update/resume` enum. A manifest that recorded a removed value
  (`quick`/`standard`/`deep`/`research`) must switch to a real mode; manifests that omit `mode` are
  unaffected. (audit F-06)

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
