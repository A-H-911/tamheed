# Plan 023 (B19): Ledger honesty + upsert ergonomics

## Status

**DONE (2026-07-23)** — three phases, `check.py` green at every boundary; released as
**v2.5.2** (PATCH — honesty/ergonomics fixes + one runbook line, no new surfaces).
Evidence: the seventh ACMP field report (`evidence/acmp-field-report-7-2026-07-23.md`),
the first official runbook-§8 run — all four findings_6 gaps closed empirically (DW carry
23/23 including the un-emoji'd D-16; PH-0/PH-1 `Implemented`; one-H1 prompts; CSV force
recovery byte-identical), and the empty-UNEXPECTED criterion caught a **live-data blemish,
not a parser bug**: FR-100/107's `custom_attributes` still held the 2.4.0 pipe-shear
snapshot (operator-repaired same day, PE-130). Cluster **C28**. This report is also plan
022's acceptance evidence.

## What shipped (per phase, one commit each)

1. **Ledger honesty (C28/B1'/B2')** — `In progress → Activated` left the silent exact map
   for a noted semantic-alias step (+ `In-progress` variant): findings_7 caught the C27
   honesty-symmetry comment being untrue while the alias carried silently. Each
   `status_coerced` entry records its `basis` (`status_map` | `semantic-default` |
   `default`) and the top-level `status_coerced_basis` is derived from the entries
   (`mixed` when a supplied map covered only some coerced words — a map no longer takes
   credit for semantic defaults). Quirks 12/20 updated; 2 tests updated + 1 new; golden
   delta empty.
2. **Upsert ergonomics (C28/C2)** — `entity_upsert` serializes dict/list values to JSON
   at binding: a raw dict `custom_attributes` used to fail the whole batch with sqlite's
   opaque "type 'dict' is not supported" (tripped in the field by the FR-100/107
   provenance repair). General rule, no column special-casing; docstring documents both
   accepted forms; 1 test.
3. **Docs, evidence, release** — runbook §8 step 2 gains the compare-JSON-blobs line
   (the exact blind spot findings_6 fell into) + docs mirror; findings_7 archived (C28,
   header includes the record correction: the `restated_content` advisory is 2.3.0-era,
   not new in 2.5.1); plans/README row + alignment record; CHANGELOG `[2.5.2]` +
   plugin.json (version-sync lint); tag v2.5.2.

## Verification

`check.py` green throughout (~179 tests, 2 new). Golden delta script empty after Phase 1
(no fixture carries an `In progress` cell; previews are not goldens; C2 is server-side
only). **Acceptance (maintainer): the next §8 run** — D-02 carries with a semantic-alias
note, phase coercions labeled `semantic-default`, `basis: mixed` when a map is replayed,
dict `custom_attributes` accepted in repairs.

## Rejected / recorded-not-planned

- FR-100/107 provenance repair — already done operator-side (PE-130); live-data, not
  parser.
- PH-2/PH-3 `substantially delivered`/`not started` → default `Approved` — correct
  behavior, operator-confirmed; project-specific words stay `status_map` territory.
- The AGENTS.md restated-content hits (hard-coded 62/11/1 tally, quoted invariant
  subset) — ACMP content drift; the advisory (2.3.0-era, plan 019) worked as designed;
  folded into the next ACMP prompt instead.
- Auto-comparing JSON blobs *inside* §8 tooling — §8 is a procedure, not a tool; the
  runbook line is the fix (the diff script lives operator-side).
