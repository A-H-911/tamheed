# Plan 010 (B5): Migration — walk a v1 Markdown package into the v2 database

> **Executor instructions**: Build plan. Deliverable = the `package_migrate` implementation, the
> documented v1 mapping, and migrated in-tree goldens. STOP conditions are binding.
>
> **Drift check (run first)**: plans 001–004 (fixed v1 validator) AND 007–009 landed. The v1
> validator at `plugins/tamheed/scripts/validate_package.py` must contain the two-step id-column
> idiom (plan 001) — `grep -c "col_index(ID_HEADERS) or" …` → 0. Otherwise STOP: migrating with
> the buggy validator can silently import defective packages.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED (data fidelity)
- **Depends on**: plans/001–004 (Track A), plans/009-b4-skill-v2-rewrite.md
- **Category**: migration
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Existing users hold v1 packages: directories of Markdown registers + `manifest.json` +
`keystone-state.json`. Maintainer decision ASM-A: v2 supports them **for migration only** — one
well-tested walk into the database, then the package lives under the v2 flow. Migration is where
data corruption would happen silently, so it is gated front and back: the *fixed* v1 validator
must pass before conversion, and `gate_run` must pass after.

## Routing rule + real-world corpus (C10, 2026-07-17)

`package_migrate` accepts **conformant v1 packages only** (manifest/state/registers in Keystone
v1 shape — pre-flight validator gates this). Keystone-*lineage* packages that lack the
mechanical layer (no manifest/state, hand-coined ID namespaces) are NOT migrate inputs — the
pre-flight rejects them with a pointer to `package_adopt` (plan 011), which reconstructs with
provenance. Real-world validation corpus (operator's own projects, used with permission):
`C:\Users\ahammo\Repos\acmp` and `C:\Users\ahammo\Repos\opencode` (conformant v1 → migrate;
note acmp's manifest is frozen/divergent — 32 ADRs on disk vs 23 declared — exactly the
tolerance this plan's quirk-handling must absorb) and `C:\Users\ahammo\Repos\tarseem`
(lineage-but-nonconformant → adopt). Exercise the corpus read-only unless the operator
explicitly runs a live migration.

## The v1 source contract (documented quirks — this knowledge is the plan's payload)

The migration parser MUST handle these verified v1 realities (they came out of the audit; the
files are frozen precisely so this mapping stays true):

1. **Manifest divergence**: real v1 manifests differ from `package-manifest.schema.json` — the
   shipped demo (`generated-samples/support-triage-agent/manifest.json`) uses top-level `package`
   (schema says `project`), a top-level `mode`/`profile`/`status`, artifact entries with
   `class`/`trigger`/`note` (not in schema), status value `Planned` (not in schema's enum), and
   `omitted_artifacts[].kind` where the schema (and validator `gate_set`) read `path`. Treat the
   MANIFEST AS FOUND as authoritative input: accept both key spellings (`package|project`,
   `kind|path`), map extras into `custom_attributes`.
2. **State-schema mode enum**: `schemas/keystone-state.schema.json:25-28` `project_profile.mode`
   enum is `quick/standard/deep/research/update/resume` — a depth/mode mix that never matched the
   invocation modes. Migration maps: `quick|standard|deep|research` → package `research_depth`;
   `update|resume` → discard (transient). A missing `project_profile` is normal (the valid-package
   fixture has none).
3. **Registers are Markdown tables** with ID column 0 (`| ID | Statement | Source | ... |`);
   IDs follow `references/governance.md` (`FR-001`, `ADR-0001`, `WBS-1.1`…). Reuse the v1
   validator's parsing helpers (`MarkdownTable`, `col_index`, ID regexes) by importing
   `validate_package.py` — do not rewrite parsers.
4. **Narrative docs** (charter, exec summary, architecture, ADR bodies) → `narrative_documents` +
   `document_sections` by heading; ADR front-matter/status feeds the `adrs` table.
5. **Traceability matrix** rows → `trace_edges` (the matrix is derived in v1; edges are the
   truth in v2 — G-TRACE view re-derives coverage).
6. **Fidelity criterion (W-V2 review)**: NOT byte equality. Success = (a) identifier sets match
   (every governed ID in the v1 files exists as an entity or edge), (b) per-family counts match
   the v1 manifest's `identifier_counts` where present, (c) v2 `gate_run` verdict ≥ the v1
   validator's verdict (a v1-passing package must not fail v2 gates except where v2 is
   deliberately stricter — any such case is reported to the operator, not auto-resolved).

## The walkthrough UX (maintainer: "walk them to migrate" — interactive, staged, resumable)

`package_migrate` runs in stages, each reporting before proceeding:
(1) pre-flight: run the v1 validator (subprocess, `--json`); exit ≠ 0 → stop with the report;
(2) parse + map (dry: counts per entity family, unmapped-content list);
(3) operator confirms; (4) populate DB (one transaction);
(5) post-flight `gate_run` + integrity report; (6) operator reviews via the HTML view (plan 012 —
until it lands, emit the report as text). Resumable: stages record progress in the `packages` row.

## Deliverables

1. `plugins/tamheed/server/migrate.py` — implementation behind the `package_migrate` tool stub.
2. `plugins/tamheed/references/migration-v1.md` — the mapping table (v1 file/field → v2 entity/
   column), including the quirks list above verbatim — this is user-facing migration doc.
3. Migrated goldens IN-TREE: `generated-samples/support-triage-agent-v2/` (the demo, migrated) —
   committed canonical JSONL per plan 007's spec. Keep the v1 demo directory untouched (it
   remains the migration test input).
4. `tests/test_migration_golden.py` — migrates `tests/fixtures/valid-package` and the demo in a
   temp dir; asserts the fidelity criterion (a/b/c above); asserts `invalid-package` and
   `incomplete-package` are REFUSED at pre-flight.
5. `docs/migrate-from-keystone.md` — the **agent-facing migration runbook** (maintainer decision
   D-REPO-4): an executable checklist written FOR an AI agent operating inside a project that
   used old Keystone. Content: **detection** (project contains a Keystone package —
   `manifest.json` + `keystone-state.json` — and/or the keystone plugin is installed) →
   **install Tamheed** (`/plugin marketplace add A-H-911/tamheed` → `/plugin install
   tamheed@tamheed`; approve the MCP server) → **run the staged `package_migrate`** (stages 1–6
   above; stop at each operator gate) → **verify** (`gate_run` passes; fidelity report clean) →
   **re-point the project's `CLAUDE.md`/`AGENTS.md`** references from Keystone artifacts to the
   Tamheed package (HTML view + MCP tools) → **optionally uninstall the keystone plugin**. This
   runbook is linked from BOTH repos' READMEs (plan 014 tamheed-side; plan 016 keystone-side) —
   keep its path stable: `docs/migrate-from-keystone.md`.
   **Consent rule, stated FIRST in the runbook (D-REPO-5):** migration is **operator-initiated**.
   An agent that detects a Keystone package must inform the operator and STOP — it never begins
   `package_migrate` without the operator's explicit instruction. Keystone v1 keeps working;
   staying on it is a valid choice the runbook must respect.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Migration goldens | `python tests/test_migration_golden.py` | exit 0 |
| All prior suites | `python tests/test_validate_package.py` + `test_db_roundtrip.py` + `test_mcp_contract.py` | exit 0 |
| v1 goldens | four validator runs (plan 001 table) | 0/0/1/1 |

## Scope

**In scope**: the four deliverables + `plans/README.md`. **Out of scope**: any v1 source file
(validator, schemas, templates, the v1 demo directory — all read-only inputs), the HTML viewer
(012), adopt mode (011).

## Steps

1. Write `references/migration-v1.md` first (mapping before code).
2. Implement `migrate.py` staged flow; import v1 parser helpers from `validate_package.py`.
3. Migrate the two good fixtures in a sandbox; iterate until the fidelity criterion holds.
4. Commit the migrated demo as deliverable 3; write the golden test.
5. Wire the real implementation into the plan-008 stub; contract test updated to expect staged
   behavior instead of "not implemented".

**Verify** per commands table after steps 3–5.

## Done criteria

- [ ] `test_migration_golden.py` exit 0 (fidelity a/b/c; refusal cases covered)
- [ ] `generated-samples/support-triage-agent-v2/` committed, loads via `store.py`, `gate_run` passes
- [ ] v1 inputs untouched (`git status` on those paths clean)
- [ ] All suites green; `plans/README.md` updated

## STOP conditions

- Pre-flight validator missing plan-001's fix (see drift check).
- A v1 construct in the demo maps to nothing in the plan-007 DDL — report (may require a
  migration in `db/migrations/`, which is plan-007-owned review territory).
- Fidelity criterion (c) fails because v2 is stricter in an *unintended* way.

## Maintenance notes

- The v1 schemas/validator stay frozen in-tree as the migration contract until the maintainer
  retires v1 support explicitly (separate future decision). Under the new-repo strategy
  (D-REPO-1) these frozen v1 sources are the **tamheed repo's own copies** — they arrived via the
  carried history; migration never reads across repos.
- Reviewer scrutiny: the `kind|path` and `package|project` dual-key acceptance; transactionality
  of stage 4 (a failed populate must leave no partial package).
