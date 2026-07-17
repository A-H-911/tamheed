# Plan 007 (B2): The v2 data model — ADR, DDL, and canonical text format

> **Executor instructions**: Design + build plan. The deliverables are an ADR, a DDL file, a
> canonical-serialization spec, and a round-trip test — no MCP server yet (plan 008), no skill
> changes yet (plan 009). STOP conditions are binding.
>
> **Drift check (run first)**: you are in the **tamheed repository** (Track B home);
> `plans/deliverables-review.md` must exist there with maintainer approval (plan 006's gate).
> Without it, STOP.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED (every downstream plan consumes this)
- **Depends on**: plans/006-b7-artifact-set-review.md (approved artifact set)
- **Category**: architecture
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

This is the heart of Tamheed v2 (maintainer decision D-STORE): generated packages stop being loose
Markdown files and become a **relational database** — entity-modeled, integrity-enforced, queried
through MCP. Done right, most mechanical quality gates stop being code that scans documents and
become properties of the schema itself. Done wrong, every downstream plan (MCP server, migration,
viewer, adopt mode) inherits the flaws. The maintainer's explicit requirement: model each
item/document/deliverable as entities — never "a document saved in a table."

## Locked design decisions (from the approved program plan — do not relitigate)

- **D-STORE**: canonical storage = deterministic **text (JSONL) per table**, committed to git;
  SQLite (stdlib `sqlite3`) is the *runtime* the MCP server loads text into and enforces
  integrity with; normalized text is written back after every mutation.
- **Three-tier gate mapping** (adversarial finding W-V2-4 — the honest version):
  - *Referential* gates → schema constraints: G-IDS (dangling refs) = FOREIGN KEYs; G-DEC-STATUS
    = CHECK constraints; G-REQ-SRC = `NOT NULL` on provenance columns.
  - *Coverage* gates → SQL VIEWs executed by a `gate_run` operation: G-TRACE (every MVP
    requirement reaches decision+work-item+test), G-SET (required entity types present or
    recorded-omitted), G-PROGRESS (every AC has an audit verdict when an audit exists).
  - *Content/judgment* gates stay outside the schema: G-COMPLETE (placeholder text scan),
    G-INJECT and the judgment gates (model/human).
  - `PRAGMA foreign_keys = ON` must be set in the single connection factory — SQLite disables FK
    enforcement per-connection by default (classic footgun; W-V2-4).
- **Immutability via supersession**: approval-bearing rows (`adrs`, approved
  `acceptance_criteria`) are never UPDATEd after approval; changes INSERT a successor row and set
  `superseded_by` on the old one (FK to the successor).
- **Agile/iteration support (D-UPDATE)**: a `scope_changes` table (id, decision ref, description,
  created_at-iteration); requirements/phases/acceptance_criteria carry `introduced_in` /
  `retired_in` iteration refs; phases are appendable after scope lock via a recorded scope change.
- **Extensibility (community, feeds plan 015)**: an `entity_types` registry table (type id, label,
  id-prefix, class Always/Conditional/…, template metadata) + a `custom_attributes` JSON TEXT
  column on every entity table + versioned DDL migration files (`migrations/NNN_*.sql`) so a new
  artifact type is a registry row + migration, not a fork.
- **Doctrinal note for the ADR (W-V2-10)**: the DB+server is the *successor of
  `validate_package.py`* — the mechanical half of the capability the skill owns — NOT an
  entry-point wrapper; the thin-wrapper rule (G-CMD-THIN) continues to govern true entry points.
- **Provenance is load-bearing**: every extracted/derived row carries `source_kind`
  (brief | clarification | code | inferred) + `source_span` (free text: brief line span, file:line,
  commit). `NOT NULL` for requirement-class entities — this is G-REQ-SRC in schema form, and plan
  011 (adopt mode) depends on `source_kind='code'`.

## Deliverables

1. **ADR** — `docs/adr/adr-0001-v2-relational-package-store.md` (create `docs/adr/`): context,
   the D-STORE decision, the three-tier gate mapping, the supersession rule, what supersedes
   design-decisions §2's dual-surface principle (HTML replaces Markdown as the human surface —
   D-REVIEW), and the doctrinal note above. Status: Proposed → maintainer approves → Approved.
2. **DDL** — `plugins/tamheed/db/schema.sql` (+ `plugins/tamheed/db/migrations/001_init.sql`
   as its versioned twin): one table per artifact family from the APPROVED set
   (`plans/deliverables-review.md` is the authoritative list; the baseline family list —
   requirements, constraints, invariants, assumptions, dependencies, open_questions, decisions,
   adrs, risks, hypotheses, experiments, **pocs, tests, kpis, stakeholders** (all four CONFIRMED
   first-class by maintainer 2026-07-17 — note: the stakeholder *register artifact* is dropped
   while the STK- *table* lives), phases, **slices** (see field-evidence additions below),
   wbs_items, acceptance_criteria, progress_entries, audit_verdicts, prompts, defects,
   **deferred_work**, scope_changes — final composition per the approved review) +
   `narrative_documents` / `document_sections` for charter-class prose +
   `trace_edges` (from_type, from_id, to_type, to_id, relation; UNIQUE + FK-per-type via
   triggers or a normalized entity index) + `entity_types` + `packages` (one row per package:
   name, profile, mode, iteration counter, versions).

   **Field-evidence schema requirements (2026-07-17 — from forensic analysis of three real
   Keystone deployments; binding inputs, full evidence in `plans/README.md` notes):**
   - **Three-axis status (C5)**: separate `lifecycle_status`, `verdict`, and `disposition`
     columns with independent CHECK enums. Dispositions = {superseded, accepted-with-deviation,
     void}, each with a mandatory `reason_ref` FK to the deciding decision/ADR. Real-world
     driver: Marid's AC-007 carried verdict "Not-met" solely because the vocabulary had no
     `Superseded` — "the criterion is void, not failed."
   - **Risk lifecycle (C5)**: risks get a state machine (open/mitigated/materialized/retired) +
     FK to the AC/test that discharges them — tarseem shipped with 29 risks stuck at "Draft".
   - **Requirement auto-advance (C5)**: trigger advances a requirement's lifecycle when all its
     linked ACs reach `Met` — Marid shipped v0.3.0 with 77/78 requirements still `Draft`.
   - **`deferred_work` table (C2)**: severity, activation trigger, invariant-at-stake FK,
     status incl. Won't-do — all three field projects hand-rolled exactly this outside the ID
     scheme.
   - **Two-level roadmap (C6)**: `phases` → `slices` as a native relation; slices are the unit
     branches/PRs/ACs bind to (acmp invented a P1–P19 "slice ladder" because PH- was too coarse).
   - **Derived data = views only (C1)**: identifier counts, artifact membership, traceability
     coverage, and backlog are SQL views — never stored snapshots (all three projects' stored
     manifests/matrices froze on first generation and rotted).
   - **`last_referenced` per entity (C3)** — updated by the plan-008 binding surface — so
     operators can see load-bearing vs generated-and-forgotten registers.
   - **Design-ahead state (C9)**: approved-but-unimplemented is a modeled, healthy state
     (Marid's PH-7 was fully gated before any code); approved ADR ≠ built.
   - **Package-resident execution planning (C8)**: per-slice execution-plan and
     durable-convention entities — replaces the shadow `.claude/memory/` corpora the field
     projects invented.
3. **Canonical serialization spec** — `plugins/tamheed/db/CANONICAL.md`: one JSONL file per
   table under the package's `data/` dir; stable key order (schema-defined), rows ordered by
   primary key, UTF-8, LF, trailing newline, canonical number/string forms; the spec exists so
   git diffs are minimal and merges are row-scoped (adversarial finding W-V2-5). Also: the
   **single-writer rule** — one loader/writer per package guarded by a lockfile
   (`data/.lock`); concurrent open → fail loud.
4. **Round-trip test** — `tests/test_db_roundtrip.py` (stdlib unittest): load sample JSONL →
   SQLite → write back → byte-identical output; FK violation raises; CHECK violation raises;
   supersession UPDATE attempt on an approved ADR row is rejected (trigger).

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Round-trip test | `python tests/test_db_roundtrip.py` | exit 0 |
| Existing suite | `python tests/test_validate_package.py` | exit 0 (untouched) |
| DDL loads | `python -c "import sqlite3;c=sqlite3.connect(':memory:');c.executescript(open('plugins/tamheed/db/schema.sql',encoding='utf-8').read());print('OK')"` | OK |

## Scope

**In scope**: the four deliverables + `plans/README.md` row. **Out of scope**: MCP server code
(plan 008), SKILL.md/references (plan 009), any v1 file (validator, templates, schemas/*.json —
they remain frozen as the migration source contract), CI wiring (plan 013).

## Steps

1. Read `plans/deliverables-review.md`; derive the final entity list; record any deviation from
   the baseline family list in the ADR.
2. Write the ADR (deliverable 1) and get maintainer approval on it (STOP-and-present — same gate
   style as plan 006).
3. Write the DDL + migration 001; every entity table gets: TEXT primary key using the governed ID
   scheme (`FR-001` style — preserves v1 identifiers through migration), status TEXT with CHECK
   where the family has statuses (sets from `references/governance.md` as amended by plan 002),
   provenance columns per the locked decisions, `custom_attributes` TEXT (JSON), supersession
   columns where approval-bearing, iteration refs where D-UPDATE requires.
4. Write CANONICAL.md; implement a tiny stdlib `plugins/tamheed/db/store.py` (load/dump JSONL ↔
   SQLite honoring the spec + lockfile) — this module is reused by plan 008's server.
5. Write the round-trip test.

**Verify each step** with the commands table; the DDL-loads one-liner must pass before Step 4.

## Done criteria

- [ ] ADR exists and is maintainer-Approved
- [ ] `schema.sql` loads clean; FK/CHECK/supersession enforcement demonstrated by tests
- [ ] Round-trip byte-identity test passes; lockfile behavior tested
- [ ] Existing v1 suite still exit 0; goldens 0/0/1/1 (nothing v1 touched)
- [ ] `plans/README.md` row updated

## STOP conditions

- `plans/deliverables-review.md` missing or lacking approval.
- The approved artifact set demands an entity the locked decisions can't express (e.g. an
  artifact that is neither register-like nor narrative) — present options, don't invent.
- Maintainer rejects the ADR — iterate there, not in DDL.

## Maintenance notes

- Every future artifact type = `entity_types` row + `migrations/NNN_*.sql` — never edit
  `001_init.sql` after it ships (migrations are append-only, mirroring the supersede-don't-edit
  governance rule).
- Reviewer scrutiny: CHECK constraint status sets vs governance.md; FK direction on
  `superseded_by` (successor must exist first — insert order matters).
