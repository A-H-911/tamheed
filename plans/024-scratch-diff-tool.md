# Plan 024 (B20): Ship the §8 scratch-diff tool

## Status

**DONE (2026-07-23)** — three phases, `check.py` green at every boundary; released as
**v2.6.0** (MINOR — a new shipped tool is additive functionality). Evidence: the eighth
ACMP field report (`evidence/acmp-field-report-8-2026-07-23.md`), a full-green acceptance:
the JSON-blob-inclusive §8 run returned an **empty UNEXPECTED bucket** (FR-100/107
provenance byte-equal — the amended method proven on the exact case that motivated it),
all three C28 ledger checks verified, dict upserts byte-identical to the migration path,
AGENTS.md drift closed. Cluster **C29**. This report is also plan 023's acceptance
evidence. Six consecutive releases have each closed the previous run's findings list.

## What shipped (per phase, one commit each)

1. **The tool (C29 §E1)** — `plugins/tamheed/scripts/scratch_diff.py`, stdlib-only:
   field-level diff of two canonical-JSONL package `data/` dirs with correct per-table
   keying baked in (`trace_edges` on from/to/relation, `entity_types` on `type_id`,
   `omissions` on entity_type/reason, `packages` as a singleton field-compare — the first
   two are exactly the mis-keyings that cost the operator ~1,000 DUP-KEY noise lines);
   union-of-columns comparison including JSON blobs; duplicates reported, never
   clobbered; exit 0/1/2 with exit 1 the normal mid-life outcome — bucketing into
   VANISHED/REMAINED/UNEXPECTED stays operator judgment (report-never-reconcile). New
   suite `tests/test_scratch_diff.py` (10 tests) registered in check.py `SUITES`.
   **Placement (deliberate divergence from the report's `tools/tamheed-repair/`
   suggestion):** the bundle — the tool versions with the store it reads and every
   package gets it via plugin update; the `scripts/` freeze covers the validator FILE,
   not the directory.
2. **Docs (C29 §E2)** — runbook §8 step 2 (+ docs mirror) invokes the bundled tool (the
   keying and JSON-blob requirements are met by construction); `references/handoff.md`
   names the scan detectors' deliberate anti-false-positive bounds (audit-tally requires
   the word `Met`; restated blocks need ≥3 consecutive id-led lines) — a clean scan is
   evidence, not proof.
3. **Evidence + release** — findings_8 archived (C29); plans/README row + alignment
   record (023 acceptance; the PH-2/3 `default`-basis expectation correction — code
   right, ACMP prompt wrong); CHANGELOG `[2.6.0]` + plugin.json (version-sync lint);
   tag v2.6.0.

## Verification

`check.py` green throughout (~189 tests, 10 new; the new suite runs inside the gate from
Phase 1 on). Golden delta N/A (no parser change). Demo self-diff smoke: the tool on the
committed demo `data/` against itself → exit 0, "no differences" (a registered test).
**Acceptance MET (findings_9, evidence C30)**: the §8 run via the bundled tool reproduced
the retired ad-hoc script exactly (changed-field sets 185 = 185, symmetric difference
empty), zero DUP-KEY noise (`problems: []`), strictly better in-band coverage (live-only
rows/files; the `packages` singleton field-diff), empty UNEXPECTED bucket, ledgers
byte-stable against findings_8. First zero-actionable-findings report of the cycle — no
plan 025 followed.

## Rejected / recorded-not-planned

- `tools/tamheed-repair/` in ACMP — would rot against parser/schema changes; the bundle
  home versions the tool with the store it reads.
- VANISHED/REMAINED auto-bucketing — operator judgment; the tool's contract is
  noise-free raw truth.
- Widening `_AUDIT_TALLY_RE`/`_ID_LED_LINE_RE` — §E2 is operator nuance, not a defect;
  the bounds are deliberate; the honesty line documents them.
- Any change for the §B2 basis labels — `default` on PH-2/PH-3 is the designed outcome;
  the wrong expectation lived in the ACMP prompt, corrected in the alignment record.
