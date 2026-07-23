# Migrating a v1 Keystone package to Tamheed v2

`package_migrate` walks a **conformant v1 package** (Markdown registers + `manifest.json` +
optionally `keystone-state.json`) into the v2 relational store — once. After migration the package
lives under the v2 flow (ASM-A: v1 is supported for migration only). The operator-facing runbook is
the bundled [`migration-runbook.md`](migration-runbook.md) (C26/B6 — the bundle links inward,
never out; the program repo's `docs/migrate-from-keystone.md` mirrors it); this file is the
mapping contract.

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
12. **Status vocabulary (C17).** `Accepted`/`Planned` map silently (canonical pairs). Common
    v1 vocabulary maps semantically — `Resolved→Implemented`, `Open→Approved`,
    `Monitoring→Approved`, `Active→Approved`, `Closed→Obsolete` — and **every** such
    coercion (plus any unknown-word → default) is reported in the preview's
    `status_coerced` ledger `[{id, original, coerced}]`. The operator confirms or
    overrides via `package_migrate(..., status_map={word: lifecycle-value})` on the
    confirm call (keys normalized like status cells; values validated). Compound cells
    ("Resolved (rule) / threshold pending EXP-001") never auto-map — exact match only,
    default + ledger entry — **but a compound literal supplied as a `status_map` key DOES
    match after normalization** (`"Instrumented (P12)": "Implemented"` applies; C21/B6).
    Note: the FR/AC Draft→Approved post-bump is a separate parser decision, not a ledger
    item. An empty status cell takes the default silently (absence, not coercion) — but a
    register with **no status column at all** defaults its rows to `Approved` (parity with
    weak-definition synthesis; `DEC` stays `Proposed` — a proposed decision is never
    rendered approved) and is reported per (file, family, count) in the preview's
    `status_defaulted` ledger (C21/B1). The preview also ships grouped views
    (`status_coerced_groups`, grouped `title_fallbacks`) — the operator decision unit is
    the group; and `status_coerced_basis` says whether the ledger reflects defaults or a
    supplied `status_map`.
13. **Titles never come from the id column (C17).** A title alias resolving to the same
    cell the id came from is never right (a `| Phase | ... |` roadmap once titled every
    phase "PH-0"); `name` is a title alias. Rows whose title fell back to the second cell
    are reported in the preview's `title_fallbacks` ledger.
14. **Parse-failure fall-through (C17).** An `adrs/` or `experiments/`/`pocs/` file that
    fails id parsing, and any diagram with an unknown stem, falls through to the narrative
    catch-all (README-named files land as `readme`, other prose as `other`) — listed in
    `unmapped` AND preserved. Narrative documents keep their full v1 `front_matter` in
    `custom_attributes`.
15. **Validator provenance (C17).** The pre-flight result carries the frozen validator's
    sha256 + byte size — "which contract judged this" is auditable from the result alone.
    `partial_files` reports per-file migrated-row counts.
16. **Text fidelity (C23/C24 — the retracted-verdict lessons).** Long-form columns
    (statement/question/decision/description) always take the RAW cell — a fallback
    title is cleaned for display but never becomes the statement. Title cleaning is
    positional (hyphens and governed ids survive) with ONE cap (200; AC titles 120).
    Weak-definition rows preserve their raw defining line in
    `custom_attributes.v1.raw_line`. `title_fallbacks` is a **data-loss warning**, not
    cosmetics: every named row's title was cleaned+capped — the full text lives in the
    long-form column or the attribute bag.
17. **Fidelity ledgers (C23).** The post-flight fidelity report carries column-level
    checks row-level validation cannot see: `truncations` (length-histogram mass at
    exactly a cap), `column_starvation` (typed columns ≥90% NULL whose
    `custom_attributes.v1` holds a matching key), `field_mapping` (v1 columns riding the
    attribute bag per family), and an `execution_state_note` (imported packages carry no
    execution state — v_backlog shows all work items open until synced via update mode).
18. **Identity & structure (C24).** `D-nn` deferred rows key on the PARSED number
    (`D-15`→`DW-015`, never positional; duplicates get the next free number + a note;
    the full crosswalk ships in the preview). Imported ACs land **Proposed**, never
    Approved — the immutability trigger freezes `slice_id` at Approved and v1 has no
    slices (bind, then approve). Row-bearing files ALSO migrate as narrative documents
    (rows and prose are not alternatives). Sections split on the shallowest heading
    level below the H1. A phase table without a Status column takes an explicit
    `Status: <word>` line from the section whose heading carries that PH- id (ledgered);
    risks map their v1 status into `risk_state` too (Open/Monitoring→open,
    Mitigated→mitigated, Closed→retired, Accepted→accepted). `Living`/`Complete` join
    the semantic status map. Migrate leaves the package OPEN after post-flight so
    `handoff_emit` follows directly. Emitted prompt bodies are scanned for v1-protocol
    instructions and dead relative links (reported, never rewritten).
19. **Table-shape tolerance II (C26).** Escaped in-cell pipes (`\|`) parse as literal
    pipes inside ONE cell — rows no longer shear at the escape. Title resolution is
    two-pass: an exact `Title`/`Name` column wins outright, then the alias set in column
    order (an `EPIC` crosswalk cell can no longer out-rank the real Title column); the
    long-form text resolves INDEPENDENTLY of the title column, and id-shaped titles
    (`EPIC-18`) trigger the degenerate-title rescue. Deferred-work `Status` carries onto
    the DW enum (off-enum words noted, left `Open`). Phase prose-status sections match by
    heading id OR phase title. Note: `title_fallbacks` measures source SHAPE, not loss —
    post-2.4.0 the count is structural and the loss is zero. Project-specific status
    words (`Instrumented`, `Met`, …) deliberately stay unmapped — confirm them via
    `status_map` each run (the grouped ledger makes replay drift visible).
20. **Status prose tolerance (C27).** A deferred-work status cell that fails exact enum
    matching carries the enum word as a PREFIX after leading punctuation/emoji —
    `**✅ Done 2026-07-12 (P9)** — narrative` carries `Done`, with a preview note per
    prose carry (never a silent inference); `In progress` maps to `Activated`; truly
    off-enum words keep the note and default `Open`. The phase `Status:` matcher is
    unanchored (status sentences ending `- **Exit gate.** …` bullets now match) with a
    word-boundary guard (`ExitStatus:` never matches), and a parenthetical qualifier
    terminates the capture (`Status: complete (delivered …)` carries `complete`).

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
| v1 progress log / running narrative | narrative document only — **no `PE-` rows are synthesized** (v2 progress starts empty; timestamps would be fabricated). The dated history survives in the document body (C21/B7) |

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
