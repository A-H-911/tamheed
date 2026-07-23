<!-- Archived by the plan 024 acceptance close-out (field-evidence C30). Verbatim copy of
the ninth ACMP operator field report (findings_9.md): the §8 run via the bundled
scratch_diff.py on v2.6.0 — a tooling-only release, migration path byte-identical to
2.5.2. Verifies: tool-vs-script reconciliation EXACT (changed-field sets 185 = 185,
symmetric difference empty), zero DUP-KEY noise (problems: []), the tool strictly better
in-band (only_live rows/files, packages singleton field-diff), empty UNEXPECTED bucket,
ledger shape byte-stable against findings_8, emit + gates clean. The operator's scratchpad
diff script is RETIRED. First report of the cycle with zero actionable findings — no plan
025, no release. Do not edit: evidence, not documentation. -->

# Tamheed 2.6.0 — field report: §8 via the bundled scratch_diff.py + tool-vs-script verdict

**Context.** Eighth run against the same frozen Keystone v1 fixture. 2.6.0 is the C29 response
to findings_8 §E1 and is a **tooling-only release**: every file in the migration path is
byte-identical to 2.5.2 (migrate.py, tamheed_server.py, export_html.py, viewer.css, schema.sql,
store.py, validate_package.py, adopt.py, both SQL migrations — all line-compared); the release
is `scripts/scratch_diff.py` + the runbook §8 step-2 amendment naming it. Live-package writes
this run: **zero**; tree clean throughout; gates 7/7, audit 73/1.

**Bottom line.** The bundled tool reproduced my ad-hoc script's field-diff set **exactly —
185 = 185, symmetric difference empty** — with zero DUP-KEY noise (the §E1 keying classes are
baked in), and it is strictly *better* than the script in one structural way (§C). The §8
UNEXPECTED bucket is **empty**. The scratchpad diff script is retired.

---

## A. The §8 bucket table (tool-produced)

Tool invocation: `python <cache>/2.6.0/scripts/scratch_diff.py tamheed-package/data
acmp-scratch/data` — exit **1** in both modes (differences exist — the documented normal
mid-life outcome), `problems: []`.

### VANISHED — nothing new (correct: no parser change), everything previously closed stayed closed

`requirements`, `deferred_work`, `phases` (shared rows), `entity_types`, and all other
register families are **absent from the report** — the 2.5.x fix chain (epic titles, pipe
shear, DW carry 23/23, phase statuses, FR-100/107 provenance) holds under the bundled tool.

### REMAINED — v2 scaffolding, in the tool's vocabulary, all exactly as predicted

| Tool output | Content |
|---|---|
| `file only in live` ×4 | defects · progress_entries · scope_changes · slices |
| `only_live` rows | decisions: DEC-029 · document_sections: SEC-633 · narrative_documents: DOC-069 · phases: PH-4 · trace_edges: ×10 (ADR-amendment set) |
| `changed` | acceptance_criteria **74 rows / 134 field lines** (lifecycle_status ×74 + slice_id ×60) · wbs_items **34 rows / 47 field lines** (effort ×20 + lifecycle_status ×15 + phase_id ×12) · prompts 3 (body) · packages `(package)` → `name` |

### UNEXPECTED — **empty.**

## B. Ledger-shape confirmation

The migration preview is **identical to the findings_8 run** — 5 DW notes (4 prose-carry +
the D-02 semantic-alias), per-entry `basis` with PH-0/1 `semantic-default` and PH-2/3
`default`, `status_coerced_basis: "mixed"`, same counts/crosswalk/fidelity ledgers/validator
hash. Expected and load-bearing: with the parser byte-identical, *any* ledger delta would have
been an environment problem, and there was none.

## C. Tool vs ad-hoc script — verdict

Mechanical set reconciliation (tool `--json` vs the script's output file, keys normalized):

- **Changed-field sets identical**: 185 = 185, `in script only: 0`, `in tool only: 0`.
- **No noise added**: `problems: []` — the two keying classes my script got wrong across two
  runs (`trace_edges` composite, `entity_types.type_id`) are correct by construction, and the
  duplicate-key path *reports* instead of silently clobbering.
- **The tool sees more, in-band**: my script iterated scratch keys only, so live-only rows
  (DEC-029, SEC-633, DOC-069, PH-4, the 10 edges) and live-only files were invisible to it —
  I covered that with a separate row-count pass each run. The tool reports `only_live` and
  `file only in`, folding the two-step method into one command.
- **Nothing the tool misses**: union-of-columns including `custom_attributes` (string columns
  byte-compared — the C28 lesson), plus a `packages` singleton special-case that reports the
  structural `name` diff as a field diff rather than two spurious only-rows.
- Small ergonomics note: human output caps values at 160 chars — fine for scanning; the
  reconciliation should always use `--json` (full values), which is what this run did.

**The scratchpad script is retired.** findings_8 §E1 asked for the diff implementation to get
a committed home; shipping it *with the store it reads* is the better answer — the KEYS map
lives next to the code that defines the tables.

## D. Emit + gates sanity

`handoff_emit`: prm ×3 + CLAUDE.md + library ×5 all `unchanged`, `stale_references: []`,
`restated_content: []` (the findings_8 AGENTS.md cleanup holds). `gate_run()`: 7/7, audit
73/1. Nothing regenerated; nothing to commit but memory.

## E. Verdict

2.6.0 institutionalizes the last hand-held piece of the §8 method: measurement (scratch
migrate) and comparison (scratch_diff.py) are now both bundled, keyed correctly, and
JSON-blob-inclusive by construction; the operator's remaining job is exactly the part that
should stay human — bucketing VANISHED / REMAINED / UNEXPECTED against the run's own history.
Seven consecutive releases have each closed the previous findings list; this one closes the
loop on the method itself. Nothing unexpected to report.
