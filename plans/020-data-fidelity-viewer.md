# Plan 020 (B16): Data fidelity + viewer redesign + the ACMP repair path

## Status

**DONE (2026-07-23)** — five phases + release executed, `check.py` green at every boundary;
released as **v2.4.0**. Evidence: the fourth ACMP field report with its **retracted
verdict** (`evidence/acmp-field-report-4-2026-07-22.md`) — a post-cutover column-level diff
found twelve data-degradation classes that three rounds of row-level checks certified as
clean. Clusters: **C23** (column-level fidelity), **C24** (data-integrity defects), **C25**
(viewer graph/export/redesign). **Outstanding: the maintainer's ACMP repair run** —
re-populate on v2.4.0 per runbook §7 (the maintainer chose no-revert + re-populate; the
repair prompt was delivered with the release).

Maintainer decisions (2026-07-23): section order State→Relations→Data · imported ACs land
Proposed (FR bump stays; verified against the immutability trigger + Met-cascade) · CSV
files committed · D-9 narrow prose-parse + D-11 honest note · viewer folds stay all-closed ·
dark maximalist identity. Adversarial review round 4: the weak-definition path (no
custom_attributes) identified as the truly unrecoverable one; CSV emission moved server-side
(circular import); DW dup guard; D-9 pinned to heading-contains-PH-id. The golden
expected-delta review then caught a live bug mid-execution: the 019 Approved-default
front-ran the D-12 AC fix — AC joined DEC in the exclusion.

## What shipped (per phase, one commit each)

1. **Data fidelity (C23/C24)** — positional `_clean_line` (hyphens/ids survive; one 200
   cap); fallback titles never become statements (raw cell carried); weak-def rows preserve
   `raw_line` in attrs; **fidelity ledgers** (truncations length-histogram,
   column_starvation, field_mapping, execution_state_note); five starvation aliases; DW
   keyed on parsed number + crosswalk + dup guard; ACs land Proposed (D-12); degenerate-
   title guard; row-bearing files also emit narrative (D-6); shallowest-heading sections
   (D-7); narrow phase prose-status (D-9); risk_state mapped (D-10); Living/Complete
   statuses; migrate leaves the package open (B2); emitted prompt bodies scanned (D-8);
   `title_fallbacks` reclassified as a data-loss warning. migration-v1.md quirks 16–18;
   9 tests; golden regen (nine families, all enumerated).
2. **Viewer order/wrap/CSV (C25)** — State→Relations→Data order; wrap-in-place (supersedes
   the 019 scroll fix); `<tr id>` row anchors + `reg-<table>` fold anchors; server-emitted
   deterministic `csv/<table>.csv` (managed) with download links; hostile pin evolved
   (# or csv/ only).
3. **Relations graph (C25)** — family-clustered radial chord SVG (deterministic geometry,
   Bézier center-pull, 8-hue families, `<title>` tooltips, pannable fold), every node an
   `href="#<id>"` to its anchored row; family-aggregate degrade above 4,000 nodes; zero JS,
   CSP untouched; every-href-resolves + 300-node determinism + hostile-id tests.
4. **Dark maximalist identity (C25)** — layered dark surfaces, gradient H1, per-section
   accent bars, glow accents, zebra/hover tables; family palette = the dataviz reference
   dark set, VALIDATED by the six-checks script against the actual surface (the old hues
   failed 4/5); status chips reserved; print falls back to light.
5. **Docs/evidence** — runbook §7 "Re-populating after a parser upgrade" (the no-revert
   repair path incl. PRM refresh); contract quirks; evidence archive with the review's
   severity correction; this plan doc; plans/README row + alignment record.

## Verification

`check.py` green at every boundary (~165 tests, 25 new). Golden diff matched the enumerated
list exactly once the AC/D-12 interaction was fixed (the STOP rule's catch). Live smoke: the
regenerated demo review.html renders dark, ordered, wrapped, folded, CSV-linked, and
graph-navigable. **Acceptance (maintainer): the ACMP §7 repair run on v2.4.0** — fidelity
ledgers clean/explained, statements carry full hyphenated text, `v_phase_exit` bindable,
2 MB report navigable, D-8 flags the stale v1 prompts until refreshed.

## Rejected (do not re-audit)

Automatic rewriting of emitted prompt links (report, never rewrite governed content) ·
legacy-id DDL column (parsed-number keying + attrs + crosswalk) · per-relation edge colors /
visible node labels / incident-edge highlight (JS-free ceiling) · D-11 execution-state
inference beyond the honest note · PE-row synthesis (stands).
