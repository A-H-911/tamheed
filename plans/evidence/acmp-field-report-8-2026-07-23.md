<!-- Archived by plan 024 Phase 3 (field-evidence C29). Verbatim copy of the eighth ACMP
operator field report (findings_8.md): the JSON-blob-inclusive §8 run on v2.5.2 — empty
UNEXPECTED bucket, FR-100/107 provenance byte-equal (the amended method proven on the case
that motivated it), all three C28 ledger checks verified (incl. the honest `default` basis
on PH-2/PH-3 — the code was right where the ACMP prompt over-predicted `semantic-default`),
dict upserts byte-identical, AGENTS.md drift closed with a clean post-edit scan. Drove
v2.6.0: the bundled scripts/scratch_diff.py (§E1 — correct keying is part of the method)
and the detector-limits honesty line (§E2). Six consecutive releases have each closed the
previous run's findings list. Do not edit: evidence, not documentation. -->

# Tamheed 2.5.2 — field report: §8 regression (JSON-blob-inclusive) + C28 ledger checks + AGENTS.md closeout

**Context.** Seventh run against the same frozen Keystone v1 fixture. 2.5.2 is the C28 response
to findings_7 §B/§C/§D. Same validator hash (`58468f4e…`). Live-package writes this run:
**zero** — the only repo change is the AGENTS.md drift cleanup (a hand-authored file the emit
only *scans*). Gates 7/7, audit 73/1, export byte-identical (review.html 2,869,227 B, all 27
CSVs `unchanged`).

**Bottom line.** All three C28 changes verified live; the §8 diff — now run with the union of
columns **including `custom_attributes`**, per the amended runbook — returned an **empty
UNEXPECTED bucket**, and the `requirements` family is now **fully clean including the JSON
blobs** (the PE-130 repair reproduced the parser's serialization byte-for-byte). Both
`restated_content` hits in AGENTS.md are closed; the post-edit scan is `[]`. One expectation
correction and two tooling notes below.

---

## A. The §8 regression diff (scratch vs live), JSON-blob-inclusive

### VANISHED (vs findings_7)

| Item | Evidence |
|---|---|
| `requirements :: FR-100/FR-107 :: custom_attributes` | Absent from the diff — the live rows (repaired via full-row upsert, PE-130) are **byte-equal** to the fresh 2.5.2 parser output. The findings_7 §C blemish is gone and the JSON-blob-inclusive method is proven on the exact case that motivated it. |

### REMAINED — v2 scaffolding, exactly as predicted

Row deltas: decisions +1 · defects +13 · document_sections +1 · narrative_documents +1 ·
phases +1 (PH-4) · **progress_entries +130** (PE-130 joined) · scope_changes +1 · slices +19 ·
trace_edges +10 (ADR-amendment set; zero field diffs on the shared 1,032). Field diffs (185):
acceptance_criteria 74× lifecycle + 60× slice_id · wbs_items 20× effort + 15× lifecycle + 12×
phase_id · prompts 3× body · packages 1× name (structural). `deferred_work`, `phases`,
`entity_types`, `requirements`: **zero field diffs**.

### UNEXPECTED — **empty.**

## B. The three C28 ledger checks

1. **D-02 no longer silent** ✓ — `unmapped` carries verbatim:
   `D-02: status 'Activated' carried from semantic alias 'In progress'`. Total DW notes now 5
   (4 prose-carry + 1 semantic-alias); the C27 honesty-symmetry comment is true again.
2. **Per-entry `basis`** ✓ on all 25 coerced entries — but **one runbook expectation was half
   wrong**: only PH-0/PH-1 (`complete → Implemented`) are `semantic-default`. **PH-2
   (`substantially delivered`) and PH-3 (`not started`) are labeled `default`** — those words
   are in neither `STATUS_COERCE` nor the operator map, so the entry records the fallback, which
   is exactly what the basis field is for. Predicted from source (`STATUS_COERCE` key set)
   before the run and confirmed by the ledger.
3. **`status_coerced_basis: "mixed"`** ✓ — the replayed 5-key map covered the KPI/DOC-067
   words (`status_map` ×6), the built-in vocabulary covered 17 (`semantic-default`), and PH-2/3
   fell through (`default` ×2). The 2.5.1 label (`"status_map"` on map-presence alone) is gone.

## C. Upsert ergonomics — dict `custom_attributes` accepted

On the open scratch (zero live impact): re-upserted FR-100 passing `custom_attributes` as a
JSON **object** → `ok, applied: 1`. On 2.5.1 the identical call failed the whole batch with
`Error binding parameter 11: type 'dict' is not supported`. The findings_7 papercut is closed;
`json.dumps(..., ensure_ascii=False)` at binding keeps the serialized form identical to the
migration path (same separators — confirmed by the byte-equal §A result).

## D. AGENTS.md drift closeout

Pre-edit scan (findings_7 §D1): 2 hits — the line-17 hard-coded `62 Met / 11 Partial /
1 Pending` tally (already drifted: the live split reads 73/1) and the 7-line quoted invariant
run. Both closed per the findings' suggested rewrites: the tally parenthetical now names the
live forms (`gate_run()` audit_evidence / `review.html#execution`), and the invariant section
now points at `entity_query(type="invariant")` / `review.html#registers` with a one-line
warning that the previous quoted copy had drifted (INV-014 mechanics remain in CLAUDE.md).
**Also trued up in passing** (real drift the detector cannot see): the "Package-data caveat"
paragraph still claimed `DW- ids ≠ D- numbers` and `v_phase_exit permanently zero` — both
false since the 2.4.0 re-population; it now states the identity mapping, the live
`v_phase_exit`, and DEF-012 as the sole open defect. Post-edit `handoff_emit`:
**`restated_content: []`**, `stale_references: []`, prm ×3 + CLAUDE.md + library ×5 all
`unchanged`.

## E. Tooling notes (mine, not the plugin's)

1. The ad-hoc diff script carried two wrong key fields across runs (`trace_edges` on
   `src_id/dst_id` instead of `from_id/to_id`; `entity_types` on `type` instead of `type_id`),
   each producing ~1,000 DUP-KEY noise lines until patched. §8 is now official procedure; its
   diff implementation deserves a committed home (e.g. `tools/tamheed-repair/`) rather than a
   session scratchpad — noise-free keying is part of the method.
2. Detector nuance for operators: `_AUDIT_TALLY_RE` requires the word `Met` — a rewritten
   tally like "73 evidenced / 1 narrated" cannot re-trigger it; `_ID_LED_LINE_RE` needs ≥3
   *consecutive* id-led lines, so scattered id mentions in prose are safe.

## F. Verdict

2.5.2 closes findings_7 §B1 (silent alias), §B2 (basis attribution — including the honest
`default` label the runbook itself under-predicted), §C-method (JSON-blob mandate in §8) and
§D-adjacent (dict upserts). Six consecutive releases have now each closed the previous run's
findings list, and the regression measurement has twice caught things outside the parser
(live-data drift in findings_7, ambient-doc drift here). The loop is working: the ledgers
disclose, the scratch-diff verifies, the UNEXPECTED bucket stays the contract.
