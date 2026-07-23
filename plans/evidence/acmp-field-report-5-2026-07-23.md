<!-- Archived by plan 021 Phase 3 (field-evidence C26). Verbatim copy of the fifth ACMP
operator field report (findings_5.md): the runbook-§7 re-populate+swap on v2.4.0 — the
calmest report of the cycle (zero blind repairs; v_phase_exit revived 51/41 + 9/9).
Mechanism correction from the plan-021 adversarial review: B1 was caused by COLUMN-order
scanning (the epic alias on an earlier column), not a missing title alias — the report
suggested fix would have been a no-op. Do not edit: evidence, not documentation. -->

# Tamheed 2.4.0 — field report: re-population after the parser upgrade (runbook §7)

**Context.** Fourth migration of the same Keystone v1 fixture (`docs/`, frozen), this time as a
**re-populate + swap** over a live package that carried execution scaffolding (slices, progress
entries, defects, a scope change) added by the post-2.3.0 hand-repair. 2.4.0 was the direct
response to `findings_4.md` §D. Same frozen validator (`58468f4e…`, 60,401 B). Every claim below
was observed directly in this run.

**Bottom line.** 2.4.0 fixes what it set out to fix — verified on real data, not release notes:
identity DW crosswalk, full-text statements, hyphen survival, roadmap-as-document, ACs landing
`Proposed` (which let us bind slices and **revive `v_phase_exit` from permanently-dead to
51/41 + 9/9**), shallowest-heading section splits, weak-def `custom_attributes` on all 155 WBS
rows. The swap procedure works and the managed emitter's diverged-refusal protected hand-authored
files exactly as designed. What follows is the delta between expectation and observation.

---

## A. findings_4 §D regression status on 2.4.0 (all verified on this run's output)

| §D | Defect | Status on 2.4.0 |
|---|---|---|
| D-0/D-1 | lossy title-fallback / statement truncation | **FIXED.** `truncations` fidelity ledger lists title/name caps only; no `statement` field at any cap. FR-001 statement full. `title_fallbacks` now carries a data-loss warning naming where the full text lives. |
| D-2 | hyphen deletion | **FIXED.** Positional stripping; WBS leaf titles carry their `(BL-nnn / EPIC-nn)` tails; titles-at-cap dropped 133→3. |
| D-4 | positional DW renumber | **FIXED.** `dw_crosswalk` in the preview: identity `D-01→DW-001 … D-23→DW-023`, zero drift. Verified live: DW-015 now holds D-15's content. |
| D-5 | degenerate epic titles | **PARTIAL — see B1.** |
| D-6 | roadmap discarded | **FIXED.** Row-bearing files also emit narrative docs (68 docs / 632 sections vs 52/508). The roadmap landed as a full document with the ladder and the legacy token map as sections. |
| D-7 | `##`-only section split | **FIXED.** Shallowest-heading split; no 82 KB preamble blob. |
| D-9 | phase status prose not parsed | **NOT FIXED (expected).** Phases defaulted Approved via `status_defaulted`; the `**Status: complete**` prose sentence is still unparsed. Re-applied by hand (PH-0/PH-1 → Implemented). |
| D-10 | risk_state wrong column | **FIXED.** New `RISK_STATE_MAP` reproduced `retired`/`accepted` with zero repair — confirmed by value-level diff. |
| D-11 | v_backlog over-reports | **DISCLOSED, not fixed.** `execution_state_note` fired verbatim: "155 work item(s) land open in v_backlog — imported packages carry no execution state; sync verdicts/progress via update mode". Honest disclosure is the right fix for a docs importer. |
| D-12 | ACs Approved-before-slices | **FIXED.** ACs land `Proposed` on both paths (visible in `status_defaulted`: `AC ×74 → Proposed`). We bound 60/74 to slices and then approved — `v_phase_exit` returns PH-1 51/41, PH-2 9/9. The permanent dead-end is gone. |
| — | deferred-work `Status` column | **STILL NOT CARRIED (expected).** `field_mapping` confirms `deferred_work` consumes `trigger to activate` but not `status`; all 23 land `Open`. Identity-keyed truth-up re-applied (Done ×7, Activated ×1). |

## B. New findings on 2.4.0

### B1. The degenerate-title guard picks the EPIC id cell — all 20 epics titled "EPIC-nn"

`_map_register_row`'s alias list (`migrate.py:270-273`) matches `"epic"` and has no `"title"`
alias, so on the WBS crosswalk table (`| EPIC | Title | … |`) the row title becomes `EPIC-18`,
not `Tarseem Diagram Management`. The C24/D-5 guard (`:281-288`) then never fires because
`EPIC-nn` is 7 chars, not ≤3. Net effect: one degenerate title traded for another, on all 20
epic rows. **Suggested fix:** put a `"title"` alias at the *front* of the `title_col` list (it
is absent entirely today), or extend the degenerate check to `^[A-Z]+-\d+$` id-shaped strings.

### B2. `title_fallbacks` cannot shrink, and the operator expectation said it would

The count is structural (78 FR + 50 TEST + 4 PH rows genuinely have no title column), identical
to 2.3.0. What changed is the *consequence* (full text preserved; warning attached). Worth a
docs line: "this ledger measures source shape, not loss; after 2.4.0 the loss is zero but the
count is unchanged."

### B3. Escaped in-cell pipes still shear table rows (FR-100, FR-107)

`| … (Superseded \| Deprecated). … |` splits at the escaped pipe: `priority` receives
`"Deprecated). No backward transitions from Approved."` and the title ends with a stray `\`.
Same corruption class as 2.3.0, unchanged. **Suggested fix:** split cells on `(?<!\\)\|` and
unescape `\|` afterwards. (Repaired by hand this run from the source lines.)

### B4. Diverged-refusal suppresses the prompt-body stale scan

Step 5's emit returned `diverged` for all three `prm-*.md` (correct — protecting hand-authored
v2 files from the freshly-migrated v1 PRM rows) **but `stale_references: []`**. The C24/D-8
tripwire evidently only scans bodies it actually writes, so the one situation the scan exists
for — v1-protocol bodies sitting in the package — produced no signal because the write was
refused. The signal the runbook told the operator to expect never fired. **Suggested fix:**
scan the PRM bodies regardless of emission outcome; report under `stale_references` with a
`(not emitted — diverged)` marker.

### B5. The prompt library embeds the package name → diverges after a directory swap

After renaming `tamheed-package-v2` → `tamheed-package`, the library's own emitted files still
said `package_open("tamheed-package-v2")` and all five reported `diverged` on the next emit.
`force=true` re-emit corrected them. This is the one *functional* consequence of the
name-in-content pattern; the `packages.name` column itself remains cosmetic (open keys on the
directory — verified `tamheed_server.py:200-207`). **Suggested fix:** render the library from
the *directory* name at emit time (it already re-renders — the divergence proves it), and/or
ship the runbook §7 note "after a swap, force-re-emit the prompt library."

### B6. Runbook §7 is referenced but not shipped

`references/migration-v1.md:5-6` points at `docs/migrate-from-keystone.md` "in the program
repo" — absent here. The swap mechanics had to be reverse-engineered from code (dest-exists
refusal, dir-keyed open, populate leaves the package open, no rename tool). They compose into a
working procedure; it should be written down where the reference points.

### B7. KPI status proposals changed between 2.3.0 and 2.4.0

2.4.0's semantic default for the unknown statuses `Instrumented`/`Met` is now **Draft** (2.3.0
era decisions had mapped them to Implemented). Not wrong — but an operator replaying a previous
run's `status_map` of only the *compound* keys would silently get 3 of 5 KPIs at Draft. The
grouped ledger made this visible pre-populate; the full 5-key map was confirmed and applied.

## C. Positives worth keeping exactly as they are

- **The preview is now a real contract.** Identity `dw_crosswalk`, grouped coercions with ids,
  `status_defaulted` naming the AC→Proposed change, `count_deltas` still reporting (never
  reconciling) the stale-manifest five.
- **The fidelity ledgers close the findings_4 process gap.** `truncations` (length histogram at
  the caps), `column_starvation` (null-rate × v1-key), `field_mapping` (consumed-column
  contract), `execution_state_note` — these are exactly the column-level checks whose absence
  let 2.3.0 pass 7/7 over ~415 damaged fields. Both starvation entries this run were explained,
  not losses (stakeholder role ≡ name; WBS leaf phase inheritance).
- **`_managed_emit`'s memoryless diverged-refusal** protected three hand-authored files from a
  legitimate-looking overwrite with zero configuration. Safe-by-default held under adversarial
  conditions (a package whose rows *disagreed* with disk).
- **The 2.4.0 export**: dark default theme, relations graph directly after Overview, per-table
  CSV beside the report (27 files, managed), `overflow-wrap: anywhere` tables. All verified in
  the committed artifact.
- **Weak-def rows now carry `custom_attributes`** (`v1.raw_line` + source ref) — the 135 WBS
  leaves went from the only provenance-free rows in the store to fully provenanced.

## D. Residuals after this run

1. Epic titles + WBS leaf `phase_id` + span epics: repaired by hand again (B1); leaf inheritance
   remains an importer gap (`column_starvation` discloses it).
2. `deferred_work.status`: truth-up still required after any re-migration (§A last row).
3. `packages.name` says `tamheed-package-v2` (cosmetic; no tool writes the packages row; noted
   in `DOC-069`).
4. FR-100/FR-107 shear class (B3) will recur on any future re-migration until the escaped-pipe
   fix lands.
5. 14 of 74 ACs remain slice-unbound by design (platform-foundation FRs spanning P1–P3, audit
   FRs spanning the standalone audit slice + P16, and PH-3 items never built) — bound-while-
   Proposed is no longer possible for them (all 74 are Approved again), so any future binding
   needs supersession. Accepted: nothing reads those rows' slice today.

## Verdict

The 2.4.0 parser closes 8 of the 11 findings_4 §D classes outright, discloses 2 more honestly,
and leaves 1 (deferred-work status) as a documented operator step. The re-populate + swap
procedure is sound but under-documented (B6) and has two sharp edges the tooling itself created
(B4's suppressed scan, B5's name-embedding library). The fidelity-ledger direction requested in
findings_4 — "the next increment should be a fidelity ledger, not another decision ledger" —
shipped, and it measurably worked: this run needed **zero blind repairs**; every hand-applied
correction was named by a ledger or a value-level diff before it was made.
