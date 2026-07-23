<!-- Archived by plan 022 Phase 3 (field-evidence C27). Verbatim copy of the sixth ACMP
operator field report (findings_6.md): the scratch-diff regression run on v2.5.0 — the
first EMPTY UNEXPECTED bucket (every 2.5.0 fix verified byte-exact on real data; B4's
un-suppressed scan produced 46 marked findings in isolation). Drove v2.5.1: the DW
prose-status prefix carry (B1), the doubly-too-strict phase Status regex that fired zero
times on its motivating fixture (B2), the doubled-H1 strip at prompt emit (D1), and
force-emitted derived CSVs (D2); §E institutionalized as runbook §8.
Do not edit: evidence, not documentation. -->

# Tamheed 2.5.0 — field report: scratch regression run + prompt-row closeout

**Context.** Fifth run against the same frozen Keystone v1 fixture, this time as a **pure
measurement**: a scratch migration (`acmp-scratch`, deleted after) diffed field-by-field against the
live package, an isolated exercise of the new stale-scan marker, and the closeout of the last
prompt staleness. Same validator hash (`58468f4e…`). Live-package writes: the 3 PRM rows only.
Gates 7/7 and audit 73/1 unchanged throughout.

**Bottom line.** 2.5.0 closes the findings_5 B1/B3 classes outright and un-suppresses the B4
signal — verified empirically, not from release notes. The scratch diff's **UNEXPECTED bucket was
empty**: every difference between a fresh 2.5.0 migration and the live package is either a fix
working as promised or post-migration scaffolding no parser can produce. Two parser gaps remain,
both disclosed by the migration's own ledgers. One new tooling gap found (D below).

---

## A. The step-2 regression diff (scratch vs live), bucketed

### VANISHED — the 2.5.0 parser now does these mechanically (verified by absence from the diff)

| findings_5 item | Evidence |
|---|---|
| **B1 — epic titles** | Zero `title` diffs across all 155 wbs_items. The Title-column-first scan (+ id-shaped-title rescue) produces `Platform Foundation`, not `EPIC-01`. |
| **B3 — FR-100/FR-107 escaped-pipe shear** | `requirements` absent from the diff entirely — the sentinel substitution reproduces the hand-repair **byte-exact** (title, statement, priority, source_span). |
| **DW statuses, plain-enum cells** | D-15/D-18/D-19 (`Done`) carried; only 5 DW rows differ (see B1 below). |
| WBS leaf titles, hyphens, `(BL-/EPIC-)` tails | No leaf `title` diffs — hyphen survival still holds. |

### REMAINED — post-migration v2 work, exactly as expected

decisions +1 (DEC-029) · defects +13 · document_sections +1 (SEC-633) · narrative_documents +1
(DOC-069) · phases +1 (PH-4) · progress_entries +129 · scope_changes +1 (SC-001) · slices +19 ·
trace_edges +10 (ADR-amendment set) · acceptance_criteria: all 74 differ on
`lifecycle_status` (Approved vs Proposed) + 60 on `slice_id` (the bind-then-approve work) ·
prompts: 3 bodies (v2 vs v1) · wbs_items: 34 rows on `effort` (20 epics), `phase_id` (span
epics), `lifecycle_status` (the 15-row Deferred triage) · phases: PH-0 **and** PH-1
`lifecycle_status` (see B2).

### UNEXPECTED — **empty.**

## B. The two remaining parser gaps (both self-disclosed by ledgers)

### B1. DW status carry is exact-enum only — 5 of 8 non-Open cells don't carry

The carry map accepts only `{Open, Activated, Scheduled, Done, Won't-do}` after normalization.
ACMP's register has 3 plain `Done` cells (carried ✓) and 5 prose cells — 4× `**✅ Done <date>
(<slice>…)** — <narrative>` and 1× `In progress` — which land `Open` **with an explicit
`unmapped` note each** ("deferred-work status … outside the enum — left Open"). The disclosure is
exactly right; the carry rate on a real-world register is 18/23. **Suggested increment:** a
prefix/contains match for the enum word inside a prose cell (`^\W*Done\b` after markdown
stripping), and map `In progress → Activated` — that alone takes this fixture to 23/23.

### B2. The phase prose-status fix fires ZERO times on this fixture

findings_5 predicted PH-0/PH-1 would carry `Implemented` from `**Status: complete.**`. Neither
did. Two independent regex mismatches (migrate.py:786, `^\**Status\**\s*:\s*\**([A-Za-z][A-Za-z -]*?)\**\s*[.\n]`, `re.M`):
1. **Line-anchored** — ACMP's status sentences sit at the *end* of the `- **Exit gate.** …` bullet,
   never at line start, so `^` never matches.
2. **Parenthesis-blind** — even unanchored, PH-1's `Status: complete (delivered incrementally
   through P12; MVP live).` fails because `(` is outside the character class.
**Suggested fix:** drop the `^` anchor (search anywhere in the section body) and terminate the
capture at `[.(\n]` so a parenthetical qualifier doesn't kill the match.

## C. The B4 fix — verified in isolation, and the runbook premise correction

The runbook expected the live emit to show diverged prm files + the new markers. It showed
**`unchanged ×3` with an empty scan** — because the live PRM rows were already re-authored to the
v2 protocol in the previous session; the staleness the step assumed was closed then. The marker
was exercised instead in isolation: emitting the **scratch** package (v1 PRM rows) against a temp
dir seeded with the v2 files produced:
- `diverged ×3` (protection held), and
- **46 `stale_references` entries**, each tagged `handoff/prm-00X-….md (PRM-00X — not emitted:
  diverged)`, naming every dead relative link (`../planning/roadmap.md`, …), the v1-validator
  instruction (`validate_package.py docs` → "run gate_run via the tamheed MCP tools instead"), and
  the register-editing lines ("v1 hand-edited artifacts — record via progress_update/audit_record
  instead").

The findings_5 B4 suppression is gone: the scan now runs on refused emissions and says so.

## D. New findings on 2.5.0

### D1. The doubled-H1 interaction (root-caused and closed this run)

The PRM renderer emits `# {title}\n\n{body}\n` (2.4.0 did too). Hand-authored bodies that begin
with their own H1 therefore produce a doubled heading on disk — which is what all three emitted
prompts carried since the 2.4.0 cutover. Closed at the root: bodies re-upserted with the in-body
H1 stripped; after one forced emission, the plain emit reports **everything `unchanged`, scan
clean** — DB, disk, reality agree, single H1 per file. **Suggested increment:** strip (or warn on)
a body-leading H1 identical to the title at upsert or emit time — the composition rule is
invisible to prompt authors.

### D2. Managed CSVs with no force path go permanently stale

`export_html` CSVs are managed emissions: after the PRM body fix, `csv/prompts.csv` reported
`diverged` and was refused — but `export_html` takes no `force` parameter, so there is **no
in-tool way to refresh a diverged CSV**. Worked around by deleting the stale *generated artifact*
and re-exporting (`emitted` fresh). **Suggested fix:** CSVs regenerated from the DB are derived
outputs, not operator files — either exempt them from divergence refusal or give `export_html` a
force flag.

### D3. Graph node-count expectation

The relations graph shows **1,686 nodes = the complete `entity_index`** (the "~2,400" estimate
counted non-indexed rows: trace_edges, entity_types, omissions). Full-graph mode (≤4000 limit),
`gz-fit` radio checked by default, `2×/4×/8×` radios present — fit-to-view confirmed at DOM level;
the visual eyeball is the operator's.

## E. Verdict

2.5.0 closes findings_5 B1 (epic titles) and B3 (escaped pipes) outright, un-suppresses B4's
stale scan with a precise marker, and ships a genuinely useful fit-to-view graph. The remaining
gaps are narrow and self-disclosing: the exact-enum DW carry (B1) and the doubly-too-strict phase
prose regex (B2, fires zero times on the very fixture that motivated it — the sharpest item in
this report). D1/D2 are small composition-rule papercuts. The regression-measurement method
itself — fresh scratch migration, field-level diff against the live package, empty UNEXPECTED
bucket as the pass criterion — is cheap and decisive; worth institutionalizing as the standard
post-upgrade check.
