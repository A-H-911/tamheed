# Quality gates

Gates verify the package is complete, consistent, traceable, and executable before handoff. **Critical**
gates block readiness; **Warn** gates surface issues but don't block. In v2 the gates live in three
tiers (ADR-0001) — the strongest ones stopped being checks and became properties of the schema.

## The three-tier model

| Tier | Gates | Mechanism | When it fires |
|---|---|---|---|
| **Referential** | G-IDS, G-DEC-STATUS, G-REQ-SRC | FOREIGN KEYs + `entity_index`; CHECK constraints on status enums; NOT NULL provenance columns | **At write time.** A violating `entity_upsert` fails with the constraint named — the error IS the gate report. These defects are unrepresentable in a stored package. |
| **Coverage** | G-TRACE, G-SET, G-PROGRESS | SQL views (`g_trace_failures`, `g_set_failures`, `g_progress_failures`) executed by `gate_run` | On `gate_run` (stages 19/22, and any time). |
| **Content / judgment** | G-COMPLETE (placeholder scan, mechanical), G-INJECT (handoff screen), G-CONFLICT, G-EXEC, G-HANDOFF, G-OQ, and the Warn gates | `gate_run`'s content scan; `handoff_emit`'s injection screen; your judgment, recorded | `gate_run` / `handoff_emit` / stages 19+22. |

## Gate definitions

| Gate | Severity | Checks |
|---|---|---|
| G-REQ-SRC | Critical | Every requirement has `source_kind` + `source_span` (NOT NULL — schema). |
| G-IDS | Critical | IDs well-formed (CHECK), unique (PK), no dangling refs (FKs via `entity_index`; deleting a referenced entity fails). |
| G-DEC-STATUS | Critical | Decision status ∈ {Proposed, Approved, Rejected, Superseded, Deferred, Implemented} (CHECK — `Draft` is unrepresentable). |
| G-SET | Critical | Every Always-class family (per the `entity_types` registry) has rows or a recorded `omission` with a reason. View: `g_set_failures`. |
| G-PROGRESS | Critical | When any audit verdict exists, every non-retired AC has one. View: `g_progress_failures`. |
| G-TRACE | Critical | Every MVP requirement reaches ≥1 decision/ADR, ≥1 slice/work item, ≥1 test via `trace_edges`. View: `g_trace_failures`. |
| G-COMPLETE | Critical | No placeholder text (TODO/TBD/FIXME/`{{…}}`/`<placeholder>`) in any entity's text columns. |
| G-CONFLICT | Critical | No unresolved hard contradiction past scope lock. (Judgment + open-question audit.) |
| G-EXEC | Critical | Each phase has slices + exit criteria; leaf WBS items actionable + testable. (Judgment over the planning rows.) |
| G-HANDOFF | Critical | Prompts reference only existing entities; Claude-Code-appropriate; no dangling instructions. (Judgment + `handoff_emit` checks.) |
| G-OQ | Critical | No blocking open question silently unanswered; open ones listed accepted-open. |
| G-ASM-VISIBLE | Warn | Assumptions consumed by stages carry `risk_if_wrong`. |
| G-CLAIM | Warn | Capability claims in Approved artifacts cited or tagged `unverified`. |
| G-RISK | Warn | High-impact requirements/decisions have a risk view; no risk stuck `open` with a stale mitigation. |
| G-COUPLING | Warn | The *plan* couples to no vendor/stack needlessly; executor coupling to Claude Code is intentional. |
| G-BLOAT | Warn | No family merely restates another; no empty ceremonial rows. |
| G-CMD-THIN | Warn | Entry points carry no methodology. (The MCP server is not an entry point — it is the capability's mechanical half.) |
| G-INJECT | Critical at emission | Brief-derived text never becomes an imperative; `handoff_emit` refuses emission on instruction-shaped text. |

## Running gates

- `gate_run` (MCP tool) → the full mechanical report: referential tier confirmed
  enforced-at-write-time, coverage views executed with failing IDs, content scan findings, and the
  evidenced-vs-narrated audit split (a narrated verdict is the graded party grading itself — prefer
  evidence refs).
- Judgment gates: perform the check and record the verdict (a `progress-entry` note with the evidence).
- Stage 19 runs everything; Stage 22 re-confirms criticals for the readiness verdict.
- The frozen v1 validator (`../scripts/validate_package.py`) still validates **v1** packages — it is
  the migration source contract (plan 010), not the v2 gate engine.

## Readiness rule

A package is **execution-ready** only when every Critical gate passes and every Warn gate is either
passing or has an accepted, recorded exception. The readiness verdict lists each gate, its result, and
(for any exception) who accepted it and why. Never report "ready" with a Critical gate failing.
