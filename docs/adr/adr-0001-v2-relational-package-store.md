# ADR-0001: The v2 relational package store

- **Status:** Approved (maintainer, 2026-07-17 — interactive gate, plan 007 step 2)
- **Date:** 2026-07-17
- **Deciders:** maintainer (Eng. Anas Hammo)
- **Plan:** `plans/007-b2-data-model-adr-ddl.md` (B2); input contract `plans/deliverables-review.md`
  (APPROVED 2026-07-17)

## Context

In Keystone v1 a generated package is loose Markdown plus a machine-owned `keystone-state.json`;
the mechanical quality gates are `validate_package.py` scanning documents with regexes. Forensic
analysis of three real deployments (acmp, Marid, tarseem) showed the failure mode of that shape:
registers rot (tarseem shipped 29 risks stuck at "Draft"), statuses stall (Marid shipped 77/78
requirements still "Draft"), derived documents freeze on first generation, and every project
hand-rolled missing structure (deferred-work registers, slice ladders) outside the ID scheme.

Plan 006 decided the v2 artifact set (`plans/deliverables-review.md`); maintainer decision
**D-STORE** locked the storage strategy. This ADR records the resulting data model doctrine that
every downstream plan (008 MCP server, 009 skill, 010 migration, 011 adopt, 012 viewer) consumes.

## Decision

### 1. Storage: canonical text, relational runtime (D-STORE)

- **Canonical form:** one deterministic **JSONL file per table** under the package's `data/`
  directory, committed to git. Determinism spec in `plugins/tamheed/db/CANONICAL.md` (stable
  schema-defined key order, rows ordered by primary key, UTF-8, LF, trailing newline) so diffs
  are minimal and merges row-scoped.
- **Runtime:** stdlib `sqlite3`. The loader reads JSONL into SQLite, enforces integrity there,
  and **writes normalized text back after every mutation**. `PRAGMA foreign_keys = ON` is set in
  the single connection factory — SQLite disables FK enforcement per connection by default.
- **Single-writer rule:** one loader/writer per package, guarded by `data/.lock`; concurrent
  open fails loud.

### 2. Entity model

One table per artifact family from the approved set. **Register entities:**

`packages` · `entity_types` (extensibility registry) · `requirements` (FR/NFR via `kind`) ·
`constraints` · `invariants` · `assumptions` · `dependencies` · `open_questions` · `decisions` ·
`adrs` · `risks` · `hypotheses` · `experiments` · `pocs` · `tests` · `kpis` · `stakeholders`
(register *document* dropped; STK- table first-class) · `phases` · `slices` · `milestones` ·
`wbs_items` · `acceptance_criteria` · `audit_verdicts` · `progress_entries` · `defects` ·
`deferred_work` · `execution_gates` · `execution_plans` · `conventions` · `diagrams` · `prompts` ·
`scope_changes` · `trace_edges` (typed relations, from/to entity index) ·
`narrative_documents` + `document_sections` (charter-class prose per the approved
narrative-vs-register split).

**Deviations from plan 007's baseline family list (recorded per step 1):**

1. **`milestones` added as a table.** The review merged the milestones *document* into the
   roadmap but kept MS- data alive "inline on phases"; a table with an FK to `phases` is the only
   shape that preserves v1 `MS-` identifiers through migration. The document stays dead.
2. **`execution_gates` added** — the review-approved merge of DoR/DoD/checkpoints/gate
   definitions into one artifact.
3. **`diagrams` added** — the review collapsed five catalog rows into one family whose kind and
   per-kind generation class are data.
4. **`execution_plans` + `conventions` added** — field-evidence requirement C9/C8
   (package-resident execution planning replaces the shadow `.claude/memory/` corpora all three
   field projects invented).

**Derived data is views only (C1):** traceability matrix, status report, execution backlog,
readiness report, phase-exit report, identifier counts, and artifact membership are SQL views —
never stored snapshots. Files rendered from them are exports.

### 3. Three-tier gate mapping (W-V2-4)

| Tier | Gates | Mechanism |
|---|---|---|
| Referential | G-IDS (dangling refs), G-DEC-STATUS, G-REQ-SRC | FOREIGN KEYs; CHECK constraints on status enums; `NOT NULL` provenance columns |
| Coverage | G-TRACE, G-SET, G-PROGRESS | SQL VIEWs executed by a `gate_run` operation (plan 008) |
| Content / judgment | G-COMPLETE, G-INJECT, judgment gates | Outside the schema — text scan / model / human |

### 4. Status doctrine

- **Three-axis status (C5):** separate `lifecycle_status`, `verdict`, and `disposition` columns
  with independent CHECK enums. Dispositions = {superseded, accepted-with-deviation, void}, each
  with a mandatory `reason_ref` to the deciding decision/ADR. (Driver: Marid's AC-007 read
  "Not-met" solely because the vocabulary had no way to say "void, not failed".)
- **Lifecycle sets** come from `references/governance.md`: Draft → Proposed → Approved /
  Rejected / Deferred → Implemented, plus Superseded → Obsolete; decision statuses are exactly
  the five + Implemented (D-U1).
- **Immutability via supersession:** approval-bearing rows (`adrs`, approved
  `acceptance_criteria`) are never UPDATEd after approval; a change INSERTs a successor and sets
  `superseded_by` on the old row (trigger-enforced; successor inserted first).
- **Risk lifecycle (C5):** `risks` gain open/mitigated/materialized/retired states + FK to the
  AC/test that discharges them.
- **Requirement auto-advance (C5):** a trigger advances a requirement's lifecycle when all its
  linked ACs reach Met.
- **Design-ahead is healthy (C9):** approved-but-unimplemented is a modeled state; approved ≠
  built.

### 5. Provenance is load-bearing

Every extracted/derived row carries `source_kind` (brief | clarification | code | inferred) +
`source_span` (free text: brief line span, file:line, commit). `NOT NULL` for requirement-class
entities — G-REQ-SRC in schema form; plan 011 (adopt mode) depends on `source_kind='code'`.
Every entity row also carries `last_referenced` (C3), updated by plan 008's binding surface, so
operators can see load-bearing vs generated-and-forgotten registers.

### 6. Agile updates (D-UPDATE)

A `scope_changes` table (id, decision ref, description, iteration); `requirements`, `phases`,
`acceptance_criteria` carry `introduced_in` / `retired_in` iteration refs; phases are appendable
after scope lock via a recorded scope change. Two-level roadmap (C6): `phases` → `slices` is a
native relation; slices are the unit branches/PRs/ACs bind to.

### 7. Extensibility (feeds plan 015)

A new artifact type is an `entity_types` registry row + an append-only migration
(`plugins/tamheed/db/migrations/NNN_*.sql`) — never a fork, never an edit to `001_init.sql`
after it ships. Every entity table carries a `custom_attributes` TEXT (JSON) column.

## What this supersedes

- **design-decisions §2 (dual surface: Markdown + JSON Schemas).** In v2 the single source of
  truth for data shape is the DDL + canonical JSONL; the human review surface is **HTML**
  (D-REVIEW), not Markdown. v1 templates/schemas are not deleted — they are **frozen as the
  migration source contract** (read-only inputs to plan 010).
- **design-decisions §4's `keystone-state.json`.** The relational store *is* the normalized
  state (plan 006 review, R3); no parallel JSON state file.

## Doctrinal note (W-V2-10)

The database + MCP server is the **successor of `validate_package.py`** — the mechanical half of
the capability the skill owns — **not** an entry-point wrapper. The thin-wrapper rule
(G-CMD-THIN) continues to govern true entry points (CLI/UI/API); it does not apply to the store,
which is inside the capability boundary.

## Consequences

- (+) Referential gates stop being scanner code and become schema properties; a class of defects
  (dangling refs, illegal statuses, missing provenance) becomes unrepresentable.
- (+) Row-scoped git diffs; agile scope changes, supersession, and execution tracking are
  first-class data instead of document conventions.
- (−) A runtime dependency on `sqlite3` (stdlib — no new installs) and a single-writer
  constraint per package.
- (−) Schema evolution carries migration discipline: append-only `migrations/NNN_*.sql`,
  MAJOR-version bump on breaking shape changes per governance versioning rules.
