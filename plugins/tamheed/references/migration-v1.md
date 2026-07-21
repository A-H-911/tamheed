# Migrating a v1 Keystone package to Tamheed v2

`package_migrate` walks a **conformant v1 package** (Markdown registers + `manifest.json` +
optionally `keystone-state.json`) into the v2 relational store — once. After migration the package
lives under the v2 flow (ASM-A: v1 is supported for migration only). The operator-facing runbook is
`docs/migrate-from-keystone.md` in the program repo; this file is the mapping contract.

## Routing rule (C10)

- **Conformant v1** (passes the frozen v1 validator; has a manifest) → `package_migrate`.
- **Keystone-lineage but nonconformant** (no manifest/state, hand-coined ID namespaces) → refused
  at pre-flight with a pointer to `package_adopt` (plan 011), which *reconstructs* with provenance.
- Migration is **operator-initiated, always** (D-REPO-5): detect → inform → STOP until instructed.

## The staged walkthrough

| Stage | What happens | Gate |
|---|---|---|
| 1. Pre-flight | The frozen v1 validator runs **in-process** (imported as a library — no subprocess from the stdio server, C11). Critical failure → refuse with its report; a validator crash is isolated and reported distinctly. | v1 gates |
| 2. Parse + map | Dry mapping: per-family counts, parsed-vs-manifest **count deltas**, **zero-families** list, **partial/skipped file ledgers** (C13), unmapped-content list, optional `patch` echo. | — |
| 3. Confirm | The dry report goes to the operator. Nothing written yet. A family parsing to **zero** against a nonzero manifest count blocks populate unless acknowledged via `allow_zero=[...]`. | **operator** |
| 4. Populate | One transaction into a fresh v2 package; canonical JSONL written back. A failure leaves no partial package. | schema |
| 5. Post-flight | `gate_run` + the fidelity report (below). | v2 gates |
| 6. Review | Operator reviews (HTML view once plan 012 lands; text report until then). | **operator** |

## Fidelity criterion (NOT byte equality)

1. **(a) Identifier sets match** — every governed ID *defined* in the v1 files exists in v2 as an
   entity row (or, for reference-only occurrences, resolves through `trace_edges`).
2. **(b) Family counts match** the v1 manifest's `identifier_counts` where present. Disk wins over
   a stale manifest (real v1 manifests freeze — e.g. a manifest declaring 23 ADRs with 32 on disk);
   deltas are *reported*, not silently reconciled.
3. **(c) Verdict monotonicity** — a v1-passing package must pass v2 `gate_run`, except where v2 is
   deliberately stricter; any such case is reported to the operator, never auto-resolved.

## The v1 source contract (verified quirks the parser absorbs)

1. **Manifest divergence.** Real manifests differ from `package-manifest.schema.json`: top-level
   `package` *or* `project`; extra `mode`/`profile`/`status`; artifact entries with
   `class`/`trigger`/`note`; status value `Planned`; `omitted_artifacts[].kind` *or* `.path`. The
   manifest **as found** is authoritative input: both key spellings accepted, extras preserved in
   `packages.custom_attributes`.
2. **State-schema mode enum.** `keystone-state.json` `project_profile.mode` mixes depth and mode:
   `quick|standard|deep|research` → `custom_attributes.research_depth`; `update|resume` → discarded
   (transient). A missing `project_profile` (or missing state file entirely) is normal.
3. **Registers are Markdown tables** with the ID in column 0. Parsing reuses the frozen v1
   validator's helpers (`parse_markdown_tables`, `col_index`, `ID_PATTERNS`,
   `collect_identifiers`) — never a second parser. Entities defined outside tables (`## PH-1`
   headings, `- **WBS-1.1**` bold leaders) are captured as *weak definitions* and synthesized as
   minimal rows (id + defining-line title).
4. **Narrative docs** (charter, exec summary, architecture, README, agent-control) →
   `narrative_documents` + one `document_sections` row per `##` heading. ADR files → `adrs` rows:
   front-matter id/status when present, else the **MADR fallback** (C12) — id from the
   `# ADR-NNNN:` heading, status from a `- Status:` bullet (the shape Keystone v1 itself
   emitted). The decision column prefers the "Decision Outcome" section and never the
   "Decision Drivers" list. Any other `.md` that matches no kind **and yields no register
   rows** migrates as a `doc_kind='other'` narrative document (C13: prose is never silently
   dropped); row-bearing files keep rows-only and are listed in the preview's
   `partial_files` ledger instead.
5. **Traceability matrix rows → `trace_edges`.** The matrix is derived in v1; edges are the truth
   in v2 (the G-TRACE view re-derives coverage). Register link columns (`Verifies`, `Realises`)
   contribute the same edges; duplicates collapse.
6. **AC dialect (C12).** The statement column may be headed "Given / When / Then" or
   "Criterion"; both are aliases, and `acceptance_criteria.statement` takes the **raw
   cell** — it never inherits the 120-char title cap.
7. **Audit dialect (C12).** "Test ref" is an evidence alias; the remaining audit columns
   ride each verdict's `custom_attributes` like every register row.
8. **MoSCoW (C14).** Priority `M`/`Must…` (and any cell containing "MVP") → `mvp=1`, so
   G-TRACE never passes vacuously over an all-`mvp=0` migration.
9. **Deferred-work register (C13).** `execution/deferred-work-register.md` rows keyed by
   the ungoverned `D-nn` convention map to governed `DW-NNN` rows (severity normalized to
   the schema enum, original row preserved in `custom_attributes`).
10. **Decision `Promoted to` (C12).** Only `ADR-*` tokens qualify (the column is an FK
    into `adrs`); a cell citing other governed ids stores NULL plus an `unmapped` note.
11. **Manifest spellings (C12).** `generated` is accepted alongside `generated_at`; the
    raw `profile` string is preserved in `custom_attributes.v1_manifest` (normalization is
    lossy). An omission recorded for a family that also migrated rows is stale and dropped.

## Field mapping (v1 → v2)

| v1 | v2 |
|---|---|
| manifest `package` \| `project` | `packages.name` (kebab-normalized), `.title` |
| manifest `profile` (e.g. `ai-agentic-system`) | `packages.profile`, normalized to {enterprise, rnd, legacy, ai-agentic, unknown} |
| manifest `mode` / missing | `packages.mode` / `full` |
| manifest `mvp_definition`, `entry_point`, `go_no_go`, `generated_at` | same-named columns |
| manifest extras (status, gated_items, identifier_counts, omitted_artifacts, per-artifact class/trigger/note) | `packages.custom_attributes.v1_manifest` |
| manifest `omitted_artifacts[].kind\|path` + reason | `omissions` rows where the kind maps to a v2 entity type; the rest stay in `custom_attributes` |
| state `project_profile.mode` | `custom_attributes.research_depth` (depth values) / discarded (transient values) |
| register row: ID col | entity `id` (v1 identifiers preserved verbatim) |
| register row: Statement/Requirement/Constraint/… column | entity `title` (and `statement` where the column is long-form) |
| register row: `Source` | `requirements.source_span`; `source_kind` = `clarification` when the source cites an `OQ-`/clarification, else `brief` |
| register row: `Priority`/`Scope` contains "MVP" | `requirements.mvp = 1` |
| register row: `Status` | `lifecycle_status` (`Accepted`→`Approved`, `Planned`→`Proposed`; decisions never carry `Draft` — pre-flight guarantees it) |
| assumption `Risk if wrong` / invariant `Enforced by` / OQ `Resolution` / decision `Rationale`, `Promoted to` / risk `Impact`·`Likelihood`·`Mitigation` / KPI `Target`·`Measurement method` / test `Kind` | the corresponding v2 columns |
| every other cell | `custom_attributes.v1` (nothing is dropped) |
| acceptance-audit rows (AC, Verdict, Evidence) | `audit_verdicts` (`AV-NNN` assigned; `—` evidence → NULL/narrated) |
| roadmap phase rows/headings | `phases` (sort_order = phase number) |
| milestone rows (`Phase` cell) | `milestones` (`phase_id` = the `PH-` token found in the row) |
| WBS ids `WBS-N.N` | `wbs_items` with `parent_id` derived from the ID (parents first) |
| diagrams by filename | `diagrams` (`context`/`component`/`integration` → Conditional; `data-flow`/`deployment` → On-request) |
| handoff prompt files | `prompts` (`initial`/`follow-up`/`review`) |
| experiment/POC files | `experiments`/`pocs` (front-matter id/status; body preserved in `custom_attributes`) |
| readiness report, status report, backlog | **not migrated** — derived views in v2 (regenerated from the rows) |

## Repair path (D1) and cutover (C15)

- **Repair** happens **before populate, never after**: `package_migrate(..., patch=<file>)`
  applies merge-by-id row overrides (JSON: `{"<table>": [{"id": ..., <columns>}, ...],
  "audits": [{"ac_id": ..., <fields>}, ...]}`) to the parsed plan, echoed in the preview.
  Approved-entity immutability is never bypassed; parse → patch → populate is the blessed
  sequence for fixing migration gaps without breaking governed ids.
- **Cutover**: a successful migration ends with a pointer to `handoff_emit`, which writes
  the executor `.mcp.json` and the `CLAUDE.md` tracking note. The operator then updates
  stale v1 pointers (AGENTS.md/CLAUDE.md) and freezes the v1 source tree — until that is
  done, two sources of truth coexist and agents may keep editing the dead one.

## What migration never does

- Never edits, deletes, or reorders the v1 source (read-only input; the frozen validator +
  schemas are the contract).
- Never invents data: unmappable content is listed in the stage-2 report and preserved in
  `custom_attributes`, not guessed into columns.
- Never proceeds past a stage gate on the operator's behalf.
