# Keystone — Roadmap

A phased plan for building **Keystone itself** — the reusable capability that turns a project description
into a validated, traceable, execution-ready planning and handoff package. Phases use `PH-` identifiers and
are ordered, but later phases may begin once an earlier phase's **exit criteria** are met. Each phase lists a
**goal**, **deliverables**, and testable **exit criteria** linked to the `AC-` IDs in
[`ACCEPTANCE-CRITERIA.md`](ACCEPTANCE-CRITERIA.md).

> Keystone is an independent, reusable capability that stays vendor-, agent-, provider-, and stack-neutral
> throughout.

**Milestone mapping:** `PH-1`…`PH-8` deliver the **MVP** (AC-001…AC-012). `PH-9`…`PH-16` deliver the **Full
Target** (AC-101…AC-114). Current status: **v0.1 — reference design + working skill** (PH-1…PH-6 substantially
defined; remaining phases in progress).

---

### PH-1 — Methodology extraction

- **Goal:** Generalize the inception → R&D → architecture-governance → execution-handoff lifecycle into a
  vendor-neutral, reusable methodology and operating principles.
- **Deliverables:** `METHODOLOGY.md`; the operating principles / safeguards; the naming decision
  (`NAMING-OPTIONS.md`).
- **Exit criteria:** Methodology is written, neutral (no project-specific coupling), and states the
  non-negotiable safeguards (never invent requirements; separate facts/decisions/proposals; surface
  assumptions; no premature architecture; preserve the unresolved; verify before claiming; useful over
  ceremonial; stay neutral).

### PH-2 — Skill architecture

- **Goal:** Establish the skill as the single authoritative implementation, with progressive disclosure and
  a thin-entry contract.
- **Deliverables:** `skill/SKILL.md`; the `skill/references/*` index; `ARCHITECTURE.md`; the entry-point
  contract in `extension.md`.
- **Exit criteria:** `SKILL.md` declares "the skill owns the capability," lists the invocation modes and the
  22-stage map, and references depth files on demand; the entry-point contract forbids methodology in any
  wrapper (supports **AC-008**).

### PH-3 — Artifact catalog

- **Goal:** Define every artifact type, when it is generated, and where it lives.
- **Deliverables:** `ARTIFACT-CATALOG.md`; `references/artifact-rules.md`; `references/generated-structure.md`;
  the governance/identifier scheme in `references/governance.md`.
- **Exit criteria:** The Always set and all conditional artifacts are cataloged with a selection trigger and
  an identifier prefix; the generated-package layout (minimal → maximal) is specified (supports **AC-003**,
  **AC-004**, **AC-104**).

### PH-4 — Templates

- **Goal:** Provide blank, single-source-of-truth forms for every artifact and prompt.
- **Deliverables:** `templates/*.template.md` for each cataloged artifact; prompt templates referenced from
  `references/prompt-templates.md`.
- **Exit criteria:** Every catalog row has a corresponding template; templates contain no project-specific
  content; the charter, registers, roadmap, acceptance-criteria, traceability, and handoff templates exist
  (supports **AC-003**, **AC-006**).

### PH-5 — Schemas

- **Goal:** Make data shapes machine-readable and authoritative.
- **Deliverables:** `schemas/project-input.schema.json`, `keystone-state.schema.json`,
  `handoff-package.schema.json`, and register-field schemas.
- **Exit criteria:** Input, state, and handoff manifests validate against their schemas; the skill and
  scripts read these schemas rather than embedding shapes (supports **AC-110**, **AC-111**).

### PH-6 — Slash-command wrapper

- **Goal:** Ship the thin `/keystone` entry point.
- **Deliverables:** `commands/keystone.md` with the help block, argument hints, and the normalize-and-invoke
  flow.
- **Exit criteria:** The command gathers input (string or `@file`), validates **invocation syntax only**,
  normalizes to the input contract, invokes the skill, and routes output — containing **no** methodology and
  making **no** planning decisions (satisfies **AC-008**; supports **AC-001**).

### PH-7 — Repository generator

- **Goal:** Deterministic, reproducible repository bootstrap for a target project.
- **Deliverables:** `scripts/init_skill_repo.py` (+ `references/repo-init.md`); folders, baseline files,
  README + logo, license, ADR/doc dirs, changelog, version, initial commit, optional remote via `git`/`gh`.
- **Exit criteria:** Bootstrap produces a usable repo; is `--dry-run`-capable and idempotent; never
  overwrites without `--force`; and is *not* required for plan-only runs (satisfies **AC-105**; supports
  **AC-011**).

### PH-8 — README & branding

- **Goal:** Make Keystone installable and presentable, and complete the MVP surface.
- **Deliverables:** `README.md`; `docs/assets/logo.svg` (+ `logo-light.svg`, `logo-dark.svg`, `icon.svg`);
  `LICENSE` (MIT).
- **Exit criteria:** README documents the capability, the thin-wrapper principle, install-as-skill/plugin
  steps, usage/slash examples, and example input/output; logo references resolve at `docs/assets/`; license
  is MIT. **MVP exit:** AC-001…AC-012 verifiable on one worked example.

### PH-9 — Validation framework

- **Goal:** Enforce quality mechanically rather than by assertion.
- **Deliverables:** `tests/validate_package.py`; the gate definitions in `references/quality-gates.md`.
- **Exit criteria:** The validator checks identifiers, links, traceability, and decision-status correctness,
  prints per-gate pass/fail, and exits non-zero on a critical failure; every gate in `quality-gates.md` is
  reachable (satisfies **AC-005**, **AC-007**, **AC-106**, **AC-112**).

### PH-10 — Tests

- **Goal:** Lock behavior with automated checks across the capability.
- **Deliverables:** Test suite for the generator (dry-run, idempotency, no-overwrite) and the validator
  (good package passes, broken package fails the right gate); CI invocation.
- **Exit criteria:** Tests pass in a clean environment; failures point at the specific gate/condition;
  generator tests run without writing a real repo (supports **AC-105**, **AC-106**, **AC-107**).

### PH-11 — Example projects

- **Goal:** Prove the capability on diverse, real briefs.
- **Deliverables:** ≥ 5 worked examples in `examples/` (input briefs) and `generated-samples/` (full
  packages), covering distinct project types (greenfield app, R&D mission, legacy/migration, AI-agentic,
  library/CLI).
- **Exit criteria:** Each example's generated package passes `validate_package.py`; the minimal-vs-maximal
  artifact selection is demonstrated; generated output lives only under `generated-samples/` (satisfies
  **AC-107**; supports **AC-104**).

### PH-12 — Documentation

- **Goal:** Complete human-facing docs that agree with the skill.
- **Deliverables:** `WORKFLOW.md` (22-stage walkthrough), `CONTRIBUTING.md`, and confirmation that
  `METHODOLOGY.md` / `ARTIFACT-CATALOG.md` / `ARCHITECTURE.md` match the implementation; documented extension
  points.
- **Exit criteria:** A new contributor can add an artifact type additively by following `extension.md`; docs
  contain no methodology that contradicts the skill (satisfies **AC-109**, **AC-113**).

### PH-13 — Packaging

- **Goal:** Make Keystone install cleanly as a skill/plugin and (optionally) run standalone.
- **Deliverables:** Packaging layout and install instructions; the build step that vendors `templates/` and
  `schemas/` for standalone use (per `ARCHITECTURE.md`).
- **Exit criteria:** Following the README, the skill loads and `/keystone` is available in a clean agent; a
  standalone package includes the vendored templates and schemas (satisfies **AC-113**; supports **AC-108**).

### PH-14 — Versioning

- **Goal:** Apply disciplined, reproducible versioning.
- **Deliverables:** Semver policy for skill/package; document-version front-matter rules; migration-note
  process; supersession (not in-place edit) for immutable-after-approval artifacts.
- **Exit criteria:** Versions are present and bump on material change; a MAJOR change to schemas/identifiers/
  handoff contract ships a migration note; older-version packages still validate (satisfies **AC-111**,
  **AC-114**).

### PH-15 — Release

- **Goal:** Cut a coherent, neutrality-checked release.
- **Deliverables:** A tagged release (target **v1.0**) with changelog; the full-target acceptance review;
  a neutrality audit across skill/scripts/templates/schemas.
- **Exit criteria:** AC-101…AC-114 verified `Approved`; the 5 examples pass; the neutrality audit finds no
  mandatory vendor/agent/stack coupling (satisfies **AC-101**, **AC-108**). **Full Target exit.**

### PH-16 — Continuous evolution

- **Goal:** Grow Keystone from real usage without eroding its principles.
- **Deliverables:** A cadence for harvesting reusable patterns into new artifact types/profiles/gates via the
  additive registries; resume/update hardening from field use.
- **Exit criteria:** New capabilities land additively (no workflow forks); every new entry point obeys the
  thin-entry contract; resume/update remain reliable on real packages (sustains **AC-102**, **AC-103**,
  **AC-109**).

---

## Phase → acceptance-criteria summary

| Phase | Focus | Primary AC coverage |
|---|---|---|
| PH-1 | Methodology extraction | Safeguards underpinning AC-009, AC-010, AC-012 |
| PH-2 | Skill architecture | AC-008 |
| PH-3 | Artifact catalog | AC-003, AC-004, AC-104 |
| PH-4 | Templates | AC-003, AC-006 |
| PH-5 | Schemas | AC-110, AC-111 |
| PH-6 | Slash-command wrapper | AC-008 (+ AC-001) |
| PH-7 | Repository generator | AC-105 (+ AC-011) |
| PH-8 | README & branding | AC-001…AC-012 (MVP exit) |
| PH-9 | Validation framework | AC-005, AC-007, AC-106, AC-112 |
| PH-10 | Tests | AC-105, AC-106, AC-107 |
| PH-11 | Example projects | AC-107 (+ AC-104) |
| PH-12 | Documentation | AC-109, AC-113 |
| PH-13 | Packaging | AC-113 (+ AC-108) |
| PH-14 | Versioning | AC-111, AC-114 |
| PH-15 | Release | AC-101…AC-114 (Full Target exit) |
| PH-16 | Continuous evolution | AC-102, AC-103, AC-109 |
