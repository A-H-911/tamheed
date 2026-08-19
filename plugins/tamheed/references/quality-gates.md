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
  content scan findings, the evidenced-vs-narrated audit split (a narrated verdict is the graded
  party grading itself — prefer evidence refs), and the **blocking G-REL edge sweep** (advisory
  through v3, blocking since v4.0.0): stored edges violating the typed endpoint rules FAIL the
  gate — retype a wrong edge to `relates_to` (delete + re-add) if the link itself is real.
- **`readiness_check(scope, id?)`** (plan 027) is the semantic layer ABOVE these gates: at a
  package/phase/slice close boundary it answers "is this actually DONE?" — blocking rules
  (pre-approval decisions/ADRs, ACs not latest-Met, open critical/high defects — medium/low
  advise, undischarged risks, open work incl. the claimed-done `Review` state), waivers
  (operator-approved `WVR-` rows reported `waived`, never silent; expiring), advisory liveness
  rules, and the `human_required` checklist from declared `execution_gates` rows. The same
  blocking rules guard the phase/slice `Implemented` transition. Rule statuses (plans 028-029):
  `pass` / `fail` / **`indeterminate`** — a rule whose keyed column is unpopulated for every row
  of its type carries `discriminating: false`, and when its query finds nothing it reads
  `indeterminate`, never `pass` ("cannot measure" ≠ "verified clean"); only real `fail` blocks.
- Judgment gates: perform the check and record the verdict (a `progress-entry` note with the evidence).
- Stage 19 runs everything; Stage 22 re-confirms criticals + `readiness_check("package")` for the
  readiness verdict.

## Readiness rule

A package is **execution-ready** only when every Critical gate passes and every Warn gate is either
passing or has an accepted, recorded exception. The readiness verdict lists each gate, its result, and
(for any exception) who accepted it and why. Never report "ready" with a Critical gate failing.
