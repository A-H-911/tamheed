# Quality gates

Gates verify the package is complete, consistent, traceable, and executable before handoff. **Critical**
gates block readiness; **Warn** gates surface issues but don't block. Since v2 the gates live in
three tiers (ADR-0001) — the strongest ones stopped being checks and became properties of the
schema. **The Warn gates are judgment-tier, prose-only**: they exist in this document and in the
skill's judgment, never in the engine's `GATE_NAMES` roster — check.py's teaching lint keeps the
three tiers (engine / judgment / warn) synced against this file in both directions.

## The three-tier model

| Tier | Gates | Mechanism | When it fires |
|---|---|---|---|
| **Referential** | G-IDS, G-DEC-STATUS, G-REQ-SRC | FOREIGN KEYs + `entity_index`; CHECK constraints on status enums; NOT NULL provenance columns — **and re-verified at gate time** (plan 027): `gate_run` runs `PRAGMA foreign_key_check`, entity_index⇄table consistency, and real status/provenance SELECTs (whitespace-only provenance is caught here; the DDL CHECK cannot see it) | **At write time AND on `gate_run`.** A violating `entity_upsert` fails with the constraint named; the gate report says "verified now", never asserts unchecked integrity. |
| **Coverage** | G-TRACE, G-SET, G-PROGRESS, G-REL | SQL views (`g_trace_failures`, `g_set_failures`, `g_progress_failures`) + the RELATION_RULES edge sweep, executed by `gate_run` | On `gate_run` (stages 19/22, and any time). |
| **Content / judgment** | G-COMPLETE (placeholder scan, mechanical), G-INJECT (handoff screen), G-CONFLICT, G-EXEC, G-HANDOFF, G-OQ, and the Warn gates | `gate_run`'s content scan; `handoff_emit`'s injection screen; your judgment, recorded | `gate_run` / `handoff_emit` / stages 19+22. |

## Gate definitions

| Gate | Severity | Checks |
|---|---|---|
| G-REQ-SRC | Critical | Every requirement has `source_kind` + `source_span` (NOT NULL — schema). |
| G-IDS | Critical | IDs well-formed (CHECK), unique (PK), no dangling refs (FKs via `entity_index`; deleting a referenced entity fails). |
| G-DEC-STATUS | Critical | Decision status ∈ {Proposed, Approved, Rejected, Superseded, Deferred, Implemented} (CHECK — `Draft` is unrepresentable). |
| G-SET | Critical | Every Always-class family (per the `entity_types` registry) has rows or a recorded `omission` with a reason. View: `g_set_failures`. |
| G-PROGRESS | Critical | When any audit verdict exists, every non-retired AC has one. View: `g_progress_failures`. |
| G-TRACE | Critical | Every MVP requirement reaches ≥1 decision/ADR, ≥1 slice/work item, ≥1 test via `trace_edges`. View: `g_trace_failures`. When zero `mvp=1` rows exist the view is vacuously empty — `gate_run` attaches an explicit **warning** so the green is never silent (plan 017, D-017-1). |
| G-COMPLETE | Critical | No placeholder text (TODO/TBD/FIXME/`{{…}}`/`<placeholder>`) in any LIVE entity's text columns; each failure names the row, the column, AND the `matched` token. Code spans are stripped first (the retired v1 gate's `strip_code` semantics, D-017-4) — so QUOTING a token in prose is legal inside backticks. Exempt (never graded): `custom_attributes` (C14 — provenance preserved verbatim), the append-only report columns `progress_entries.entry` + `audit_verdicts.evidence` (findings_21/C42 — a report of what happened cannot be "unfinished", and an unrepairable row must never fail a gate forever), and Superseded/Obsolete rows (history, not the plan — supersession is the sanctioned repair and must actually repair). G-INJECT still screens everything at emission. v4: `[NEEDS-CLARIFICATION: OQ-NNN]` markers are validated here — legal only while the cited OQ exists and is unresolved; a marker with no id, a dangling id, or a resolved cite fails. |
| G-REL | Critical | Every stored trace edge satisfies the typed endpoint rules (RELATION_RULES). Blocking since v4.0.0 — safe because the migrate tool retypes violating edges to `relates_to` at conversion, adopt reports them at adoption, and `entity_upsert` rejects them at write time. |
| G-CONFLICT | Critical | No unresolved hard contradiction past scope lock. (Judgment + open-question audit.) |
| G-EXEC | Critical | Each phase has slices + exit criteria; leaf WBS items actionable + testable. (Judgment over the planning rows.) |
| G-HANDOFF | Critical | Prompt FILES in `<package>/prompts/` reference only existing entities; Claude-Code-appropriate; no dangling instructions (the stale scan flags dead relative links). (Judgment + `handoff_emit` checks.) |
| G-OQ | Critical | No blocking open question silently unanswered; open ones listed accepted-open. |
| G-ASM-VISIBLE | Warn | Assumptions consumed by stages carry `risk_if_wrong`. |
| G-CLAIM | Warn | Capability claims in Approved artifacts cited or tagged `unverified`. |
| G-RISK | Warn | High-impact requirements/decisions have a risk view; no risk stuck `open` with a stale mitigation. |
| G-COUPLING | Warn | The *plan* couples to no vendor/stack needlessly; executor coupling to Claude Code is intentional. |
| G-BLOAT | Warn | No family merely restates another; no empty ceremonial rows. |
| G-CMD-THIN | Warn | Entry points carry no methodology. (The MCP server is not an entry point — it is the capability's mechanical half.) |
| G-INJECT | Critical at emission | Brief-derived text never becomes an imperative; `handoff_emit` scans every `<package>/prompts/*.md` (project + stock) and refuses emission on instruction-shaped text. |

## Running gates

- `gate_run` (MCP tool) → the full mechanical report: referential tier verified NOW
  (foreign_key_check + consistency + real SELECTs), coverage views executed with failing IDs,
  content scan findings, the audit split — over each ACTIVE AC's LATEST verdict (the `acs-met`
  population; superseded verdicts are history — v4.6, findings_23 §2): *evidenced* /
  *narrated* (graded with no evidence — the graded party grading itself; prefer evidence
  refs) / *ungraded* (a Pending placeholder nobody graded), `narrated_ids` and `ungraded_ids`
  naming them (a count that refuses to say where is unactionable, v4.5) — and the **blocking
  G-REL edge sweep** (advisory through v3, blocking since v4.0.0): stored edges violating the
  typed endpoint rules FAIL the gate — retype a wrong edge in ONE `entity_upsert` batch:
  `retire: true` on the old triple plus the correct relation (`relates_to` only when nothing
  typed fits and the link itself is real). Edges are keyed `(from, to, relation)`, so a new
  relation never replaces an old one — it sits beside it until retired (v4.6, findings_23 §1).
- **`readiness_check(scope, id?)`** (plan 027) is the semantic layer ABOVE these gates: at a
  package/phase/slice close boundary it answers "is this actually DONE?" — blocking rules
  (pre-approval decisions/ADRs, ACs not latest-Met, open critical/high defects — medium/low
  advise, undischarged risks, open work incl. the claimed-done `Review` state), waivers
  (operator-approved `WVR-` rows reported `waived`, never silent; expiring), advisory liveness
  rules (twenty at package scope, two of them only when the package has waivers or feedback rows — from overdue open questions through `lessons-confirmed`, `feedback-unanswered` and
  `prose-ids-resolve`, the identifiers written in prose that resolve to no entity, to
  `lessons-note-budget`, which names the lessons rendering past the always-loaded note's
  curation ceiling as promotion candidates), and the `human_required` checklist from declared
  `execution_gates` rows. The same
  blocking rules guard the phase/slice `Implemented` transition. Rule statuses (plans 028-029):
  `pass` / `fail` / **`indeterminate`** — a rule whose keyed column is unpopulated for every row
  of its type carries `discriminating: false`, and when its query finds nothing it reads
  `indeterminate`, never `pass` ("cannot measure" ≠ "verified clean"); only real `fail` blocks.
  The same holds at phase/slice scope: `acs-met`, `wbs-done` and `slices-closed` on a scope
  that holds no rows of that kind read `indeterminate` with `discriminating: false` — an
  empty slice is not a ready slice, and the `Implemented` guard still trips only on `fail`.
  Every query-built rule also reports the `population` it measured (`table`, `rows`,
  `scoped`): read it before trusting a green. **No rule passes over nothing**: a rule whose
  family holds zero rows reads `indeterminate` — unless the family's omission is RECORDED,
  which makes the zero deliberate: the rule reads `pass` and carries `omitted`. So an empty
  family is either explained or amber, never silently green. `prose-ids-resolve` fails only
  on bare, well-formed phantoms; `in_code_spans` and `not_well_formed` are informational
  lists beside it — its entity list is a floor, not a census. The three lists are disjoint
  and width is tested first (a narrow token inside a code span lands under
  `not_well_formed`); each list says when it is cut at 50; `_` is a word character, so a
  token touching an underscore is part of a longer identifier and is not scanned (v4.11).
  The whole-table `indeterminate` note names `scoped: false`; a scoped zero (plan 049)
  carries `scoped: true` — that field tells the two ambers apart. `prompt-ids-resolve`
  (v4.12) applies the same rule to the PROJECT's prompt files — the prose a session reads
  before any tool — never to a stock body; its `population` counts files (`unit: files`).
  Since v4.12 `review.html` renders this report too, evaluated as of its export date.
- Judgment gates: perform the check and record the verdict (a `progress-entry` note with the evidence).
- Stage 19 runs everything; Stage 22 re-confirms criticals + `readiness_check("package")` for the
  readiness verdict.
- **`package_verify(name?, record?)`** (v4.5) sits beside the gates as the STORE's integrity
  instrument: the canonical round-trip reported per file (`dirty`), foreign files in `data/`,
  an unloadable store as a finding (file:line), memory-vs-disk when the package is open, and a
  sha256 `digest` of the canonical files; `record=true` journals a passing verification as the
  server-appended `integrity-verified` event — a citable fact, not tamper-evidence.

## Readiness rule

A package is **execution-ready** only when every Critical gate passes and every Warn gate is either
passing or has an accepted, recorded exception. The readiness verdict lists each gate, its result, and
(for any exception) who accepted it and why. Never report "ready" with a Critical gate failing.
