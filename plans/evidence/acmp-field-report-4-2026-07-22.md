<!-- Archived by plan 020 Phase 5 (field-evidence C23-C25). Verbatim copy of the fourth
ACMP operator field report (findings_4.md in the ACMP repo) INCLUDING its in-place verdict
retraction: the v2.3.0 migration was process-clean but a post-cutover column-level diff
found twelve data-degradation classes all row-level checks passed over. Severity note from
the plan-020 adversarial review: table-path rows were recoverable via custom_attributes.v1
all along; weak-definition rows (ACMP 133 WBS leaves) were genuinely unrecoverable.
Do not edit: this is evidence, not documentation. -->

# Tamheed v2.3.0 — field report: third migration of the same Keystone v1 package (`package_migrate`)

> ## ⚠ CORRECTION — 2026-07-22, post-cutover
>
> **This report's original verdict was wrong, and is retracted in place rather than deleted.**
>
> **What was claimed:** §B was headed *"New findings (nothing in this run risks data degradation)"*,
> and the Verdict said *"there is nothing left on it we would block a ship on."*
>
> **Why it is false:** a line-by-line comparison of `docs/` against the populated store, run three
> days after cutover, found **twelve defect classes that degrade data** — including ~415 silently
> truncated fields, 78 requirement `statement`s and 133 WBS titles damaged **beyond recovery from
> the package**, an entire source document discarded, and a permanent structural dead-end.
>
> **Why the original assessment missed them:** every check performed — preview counts, `gate_run()`
> 7/7, `identifier_gaps: []`, the audit split — is a **row-level** check. All of them pass over this
> damage, because every row exists and every count is right. **The damage is at column level.** The
> industry-standard detection for exactly this failure mode is **per-column null-rate profiling,
> source vs. target**, plus a **length histogram** flagging mass at exactly the cap — and the gate
> set performs neither.
>
> **The one-line lesson:** *"zero repair actions"* measured the **migration process**, not the
> **migrated data**. §A's regression verdicts stand — B1–B8 really are fixed. §D below is new.

**Context.** Follow-up to `findings_3.md` (the 2.2.0 run of 2026-07-22, later reverted by operator
choice). Same day, the operator ordered a third from-scratch run of the identical source package
(`docs/`, Keystone v1.0.0, ~90 files) on plugin **2.3.0**, with full cutover, completed in one
session. Scale unchanged and preview-identical to the 2.2.0 run row-for-row: 218 requirements
(FR 155 + NFR 63), 74 ACs + 74 audit verdicts, 33 ADRs, 28 decisions, 58 OQs, 23 deferred-work
rows, 155 WBS items, 21 KPIs, 50 tests, 4 phases, 52 narrative docs / 495 sections, 1,032 trace
edges; same frozen-validator hash (`58468f4e…`, 60,401 B). Host: Claude Code on Windows 11,
plugin-registered stdio server. This is therefore a clean regression fixture: same input, same
operator, third parser. Every claim was observed directly unless marked unverified.

**Bottom line.** The 2.3.0 run needed **zero repair actions of any kind** — no patch, no
delete-and-rerun, no hand edits to tool output. 2.2.0 was "zero repair loops but one 4-row
patch"; 2.3.0 retired the patch too. Every actionable item from findings_3 (B1–B8) is fixed and
verified on real data. What remains is one carried-forward ergonomic suggestion (review.html
scale) and calibration nits on a genuinely useful new ledger.

---

## A. findings_3 (2.2.0) findings — regression status on 2.3.0

| # (2.2.0) | Finding | Status on 2.3.0 |
|---|---|---|
| B1 | Table-parsed phases land `Draft` (no-status-column asymmetry) | **FIXED, verified.** The new `status_defaulted` ledger reports every no-status-column register as one (file, family, count, defaulted_to) line — 12 groups on this package, including `planning/roadmap.md → PH ×4 → Approved`. Phases migrated `Approved` with real titles; the 2.2.0 4-row patch went unused. Exactly the "per-family note, default to Approved for parity, ledger reports it" option we asked for — both halves shipped. |
| B2 | `handoff_emit` stale-v1 warning is append-once, never retracted | **FIXED, verified.** The warning is now its own managed block (`<!-- tamheed:stale-warning -->` markers) whose text says it removes itself. First emit wrote it (4 real stale refs found, file:line + usable suggestions, same precision as 2.2.0); after rewiring, the clean re-run **removed the block** and reported `CLAUDE.md` in `written`. "Re-run emit to verify the cutover" is now fully self-contained. |
| B3 | Re-running emit unconditionally rewrites prompt files | **FIXED, verified.** The verification re-run listed all three `handoff/prm-*.md` under `unchanged` (plus an empty `diverged` bucket — the promised protection for hand-edited emitted files), and the `prompt_library` result carries the same emitted/unchanged/diverged tri-state. `written` is now trustworthy: the second emit listed only the file that actually changed. |
| B4 | `title_fallbacks` noisy at scale (131 rows, ~3% signal) | **FIXED, verified.** Grouped by family with counts; ids expanded only for small groups: `FR 78` and `TEST 50` count-only, `PH 4` with ids. 131 rows → 3 lines; the interesting entries are no longer buried. |
| B5 | `status_coerced` could pre-group by proposed mapping | **FIXED, verified.** `status_coerced_groups` `[{original, proposed, count, ids}]` ships in the preview — 21 rows → 10 groups → 3 operator decisions, mapping 1:1 onto the multi-select confirmation the SKILL prescribes. Row-granular ledger retained alongside. |
| B6 | Compound `status_map` keys work but undocumented | **FIXED (contract).** `references/migration-v1.md` §12 now states a compound literal supplied as a key matches after normalization (C21/B6). Re-used `"Instrumented (P12)"` and `"Met (ADR-0009)"` — both applied, as before. |
| B7 | Progress log → no `PE-` rows, undocumented mapping decision | **FIXED (contract).** The field-mapping table now carries the row: narrative document only, no PE synthesis, timestamps never fabricated (C21/B7). |
| B8 | Cosmetics: confirm-echo ledger basis unlabeled; mixed path separators | **FIXED (basis), verified.** `status_coerced_basis` present and correct at both stages (`"defaults"` in the preview, `"status_map"` in the confirm echo) — the auditor ambiguity is gone. Path separators: all paths observed this run (`written`, `unchanged`, `prompt_library`) were forward-slash; the Windows nit did not reproduce. |
| 2.1.0-#5/#6 | review.html scale / freshness stamp | **Unverified again.** Export succeeded at 2,119,403 B (2.2.0: 2,118,492 B) — same order of magnitude, so the big tables are presumably still fully expanded; the page was not opened this session. Suggestion carried forward unchanged (wrap edge/section tables in `<details>`, add a TOC). |

Also re-confirmed unchanged: preview counts matched the 2.2.0 fixture exactly; the stale-manifest
five (OQ 48→58, DEC 27→28, ADR 23→33, AC 66→74, WBS 20→155) reported, never reconciled;
`zero_families: []`; MADR fallback caught all 33 ADRs; `D-nn`→`DW-` rescue (23 rows); the 3
legitimate omissions (hypothesis/experiment/poc) survived while stale ones stayed dropped;
fidelity `identifier_gaps: []`; gates 7/7 with the honest 73 evidenced / 1 narrated split;
G-INJECT screened 3 prompts, zero false positives.

## B. ~~New findings (nothing in this run risks data degradation)~~ — **heading RETRACTED, see §D**

> **Retracted 2026-07-22.** The parenthetical *"nothing in this run risks data degradation"* is
> false. The three items below are accurate as ergonomic observations and stand as written; the
> claim that they were the *only* new findings does not. **Twelve data-degradation classes are in
> §D.** Read §D before acting on §B or the Verdict.

### 1. `restated_content` (new ledger) — a good idea that behaved well, two calibration notes

`handoff_emit` now scans the agent-control files for restated register content. First emit
flagged AGENTS.md's 7 inline invariant quotes as `kind: "unlabeled"`; after the cutover rewiring
(whose intro line points at `entity_query("invariant")`), the re-run reclassified them
`labeled-snapshot` with a "verify it is still current" suggestion — a correct, useful
distinction, and precisely the drift class (quoted register text rotting in ambient files) that
nothing else watches. It also flagged the hard-coded audit tally on the "Where you are now" line
as `labeled-snapshot` ("goes stale on the first new verdict") — also correct. Calibration:
(a) that tally is already suffixed "at migration", so a dated snapshot arguably self-labels;
a `dated-snapshot` kind (or suppressing entries whose line carries an as-of marker) would keep
the ledger at zero-noise. (b) The operator has no acknowledge/waive mechanism — a deliberate
snapshot will re-report on every emit forever. Fine at 2 entries; consider an
`ack`/suppression list if this ledger grows teeth.

### 2. `package_migrate` ends with no package open; `handoff_emit` requires one

The migration result's `next` breadcrumb does say "open the package and run handoff_emit", but
an operator following muscle memory (or a script) hits `"no package open — call package_create
or package_open first"` on the first emit attempt. Cost: one extra call, clear error, good
message. Polish option: since the migrate result knows the package name, either leave the
package open after post-flight or have `handoff_emit` auto-open the sole package. Not a defect.

### 3. `Living` remains outside the semantic map (expected, worth a line)

The semantic STATUS_MAP still doesn't cover `Living` (proposed `Draft`), while `active` maps to
`Approved`. Both label the same concept in the wild ("living document"). Given the ledger makes
the override a one-click decision this is fine as-is; adding `Living→Approved` alongside
`active` would remove one of the last two recurring operator overrides for typical packages.

## C. Positives worth keeping exactly as they are

- **The zero-intervention bar is now met.** Three runs charted the trajectory: 2.1.0 needed a
  15-row hand patch + parser-source reading; 2.2.0 needed one 4-row patch; 2.3.0 needed
  *nothing* — preview → 3 grouped decisions → populate → gates 7/7 → cutover. The ledger set
  now covers every silent-default class we have hit across three migrations: coercions
  (grouped, basis-labeled), no-status-column defaults, title fallbacks (grouped), per-file
  counts, unmapped fall-throughs, and now restated ambient content.
- **Determinism held again**: sha1 over every canonical file identical across an idle
  `package_open`/`package_close` cycle. Still worth a guarantee sentence in `db/CANONICAL.md`.
- **The stale-warning lifecycle is now a closed loop** — emit, fix, re-run, warning removes
  itself, `stale_references: []`. The cutover has a mechanical done-signal.
- **Grouped ledgers changed the operator experience qualitatively**: the whole confirmation fit
  in one three-question prompt with recommendations, instead of a 21-row table read.

## D. Data-degradation defect classes (found post-cutover, 2026-07-22)

Found by diffing `docs/` against the populated store column-by-column. Every claim below was
observed directly; file:line refers to plugin `2.3.0` unless stated. Severity is blast radius on
this package, which is a *typical* v1 package — none of this is exotic input.

### D-0 — Root cause of D-1/D-2/D-3: the title-fallback path is lossy, and its ledger under-reports severity

`_map_register_row` takes one of two paths (`migrate.py:247-254`):

```python
title = title_col("statement", "given / when / then", …)      # named-column path
if title is None:
    title = _clean_line(" ".join(row[1:2]))                    # FALLBACK path
    plan.title_fallbacks.append({"id": ident, "family": prefix})
```

```python
def _clean_line(line: str) -> str:                             # :147-149
    s = re.sub(r"[#*`>-]+", " ", line).strip()
    return re.sub(r"\s+", " ", s)[:120] or "(untitled)"
```

Downstream every family writes `"title": title[:200], "statement": title` (`:266`, `:272`, `:275`…).
Consequences:

- **On the named-column path**, `title[:200]` truncates the *title* but `statement` keeps the full
  text ⇒ **cosmetic and recoverable**.
- **On the fallback path**, `title` is *already* 120 chars with `#*\`>-` stripped, so
  `"statement": title` persists the **damaged** string. There is no full copy anywhere in the
  package. ⇒ **unrecoverable loss.**
- The `[:200]` on the fallback path is dead code — `_clean_line` already capped at 120.

**This is the finding that matters most:** `title_fallbacks` (findings_3 **B4**, "fixed" by grouping
in 2.3.0) was treated as *reporting noise*. It is not. **Every row it names has had its text
destroyed.** B4's grouping made the symptom quieter without anyone noticing it was a data-loss
signal. On this package that ledger names `FR 78`, `TEST 50`, `PH 4`.

**Suggested fix:** (a) never let a fallback title become the `statement` — carry the raw cell
separately; (b) strip markdown syntax positionally, never by character class, and **never strip
`-`**; (c) reclassify `title_fallbacks` from cosmetic to a **data-loss warning** and state the cap
in the ledger line.

### D-1 — Silent truncation, ~415 fields, no warning at any stage — **HIGH**

Verified length histogram (count of fields at *exactly* the cap):

| Family · field | =120 | =200 | Recoverable? |
|---|---|---|---|
| `acceptance_criteria.title` | **74 (100%)** | — | yes — `statement` full |
| `requirements.title` | 78 | 78 | title yes |
| **`requirements.statement`** | **78** | 1 | **NO — fallback path** |
| **`wbs_items.title`** | **133 of 135 leaves** | — | **NO — no `statement` column** |
| `constraints.title` | — | **15 (100%)** | yes |
| `risks.title` | — | **11 (100%)** | yes |
| `invariants.title` | — | 9 | yes |
| `assumptions.title` | — | 8 | yes |
| `open_questions` / `dependencies` / `decisions` / `adrs` | 2 | 3 / 3 / 1 | yes |

Nothing in the preview, the confirm echo, the fidelity report or `gate_run()` mentions truncation.
**Suggested fix:** a `truncations` ledger `[{family, field, count, cap}]`, on by default. The
standard control for silent truncation is to **fail or warn on the write, not adjust it quietly**.

### D-2 — Hyphen deletion corrupts identifiers — **HIGH**

`_clean_line`'s `[#*\`>-]+` class deletes every ASCII hyphen. Observed in `wbs_items`: **0 of 155
titles contain a hyphen**, against a source full of them —
`**WBS-1.1** … Realizes FR-001, FR-003–FR-015. (BL-005 / EPIC-01)` becomes
`WBS 1.1 … Realizes FR 001, FR 003–FR 015. (BL 0`. Governed identifiers are mangled into prose
(`FR-001`→`FR 001`) and the trailing `BL-` cross-reference is severed by the 120-cap. Note the
en-dash survives while the ASCII hyphen does not, so the damage is invisible on a skim.

### D-3 — Typed-column starvation: value in `custom_attributes.v1`, typed column NULL — **HIGH**

| Column | NULL | Value sitting in `custom_attributes.v1` |
|---|---|---|
| `tests.kind` | 50/50 | `Type` ×50 |
| `deferred_work.activation_trigger` | 23/23 | `Trigger to activate` ×23 |
| `kpis.measure` | 21/21 | `Measurement` ×5 + `Cadence` ×16 |
| `wbs_items.phase_id` | 155/155 | `Phase` (on the 20 epics; leaves inherit) |
| `stakeholders.role` | 6/6 | `Stakeholder / role` |

The data is not lost, but every consumer of the typed schema sees an empty column, and no gate
notices. **Suggested fix:** after mapping, assert that a v1 key whose name matches a typed column
was not left in the attribute bag; report as a `column_starvation` ledger.

### D-4 — Positional identifier renumbering — **HIGH**

`D-nn` → `DW-NNN` was assigned by **on-disk row order**. The source register is not sorted
(`D-15` and `D-20` sit out of sequence), so five ids silently shifted:

`DW-015=D-16 · DW-016=D-17 · DW-017=D-18 · DW-018=D-19 · DW-019=D-15 · DW-020=D-21 · DW-021=D-22 · DW-022=D-20`

Every `D-nn` reference in the progress log, ADRs, code comments and commit messages now resolves to
the **wrong** row. The true `#` survives only inside `custom_attributes.v1`. **Suggested fix:**
never map positionally — key on the parsed identifier, persist the legacy id in a typed
`external_id` column, and emit a crosswalk table in the migration result.

### D-5 — Degenerate titles on the WBS epics — **MEDIUM**

The 20 epic rows took the **phase-number cell** as `title`: `WBS-1.title == "1"`,
`WBS-11.title == "1–2"`, `WBS-20.title == "3"`. The real names (`Platform Foundation`,
`Voting Engine`, …) sit unused in `v1.Title`. A degenerate 1–3 character title is a cheap
post-parse assertion.

### D-6 — A source document consumed into rows, its narrative discarded — **HIGH**

`planning/roadmap.md` (127 lines) produced 4 `PH-` rows + 6 `MS-` rows and **no narrative
document**. Lost from the package entirely: each phase's Goal / Scope / Deliverables / Validation /
**Exit gate** / Status prose (`:19-61`), the **authoritative P1–P19 build-slice ladder** (two tables,
`:78-107`), and the **Legacy token map** (`:109-117`) — the only record that `P1–P4` in
`backlog.md` are *priority codes* and that the design package's `P12`/`P15` are a different scheme.
That last one is an active mis-reading hazard for any downstream automation.
**Suggested fix:** when a file yields register rows, still emit the file as a narrative document —
rows and prose are not alternatives.

### D-7 — `##`-only section splitting buries the most recent history — **MEDIUM**

`_sections` (`:131-144`) splits on `## ` only. `progress-log.md` switched to flat
`### YYYY-MM-DD — …` entries partway through, so **23 dated entries covering P15 → P19 → D-23
collapsed into one 82,622-char "Preamble" section** — the most recent and most operationally
relevant stretch became the least navigable. **Suggested fix:** split on the shallowest heading
level actually present below the H1, or split on both and nest.

### D-8 — Emitted prompts are not re-anchored, and contradict the cutover — **HIGH**

`handoff_emit` copies v1 prompt bodies verbatim from `docs/handoff/` to `<repo>/handoff/`. Their
relative links were written for the old depth, so **every one is now dead**
(`../planning/roadmap.md`, `../progress/status-report.md`, `../execution/deferred-work-register.md`,
`../requirements/invariant-register.md`, `../validation/acceptance-criteria.md`, `../adrs/`), and
`../README.md` silently resolves to the **wrong file** (the repo README).

Worse, the bodies instruct the reader to do exactly what the cutover forbids —
`prm-003-review.md:36` says to run `validate_package.py docs` (the **v1 validator on the now-frozen
archive**) and `prm-001-follow-up.md:104` says to hand-edit `progress-log.md` /
`acceptance-audit.md`. They are also stale on state: `prm-002-initial.md:32` announces "P12 is
COMPLETE … remaining: Webex, **Tarseem sidecar**, Knowledge" when P1–P19 shipped and Tarseem was
deferred indefinitely. Since `AGENTS.md` points new sessions at `prm-002-initial.md`, the emitted
kickoff actively misdirects.
**Suggested fix:** rewrite relative links to the emit target's depth; and treat a v1-protocol
instruction inside an emitted prompt as a `stale_references` hit — the existing check only scanned
the *agent-control* files, never the emitted artifacts themselves.

### D-9 — Status defaulting applied where the status **is** present — **MEDIUM**

All four phases defaulted to `Approved` via `status_defaulted` because the roadmap's phase *table*
has no status column. But the status is right there in the prose beneath it:
`**Status: complete.**` (PH-0, PH-1), `substantially delivered` (PH-2), `not started` (PH-3).
The ledger honestly reported the default — it just never looked one line further.

### D-10 — `risks`: v1 status written to the wrong column — **MEDIUM**

v1 `Status` (Open 7 / Monitoring 2 / Closed 1 / Accepted 1) landed in `lifecycle_status`, while the
purpose-built `risk_state` kept its schema default ⇒ **`risk_state = 'open'` on all 11**, so a
`Closed` and an `Accepted` risk both read as open. `risk_state` has an exactly-matching enum
(`open/mitigated/materialized/retired/accepted`).

### D-11 — `v_backlog` is a false register — **MEDIUM**

All 155 `wbs_items` migrated as `lifecycle_status: "Approved"`, and `v_backlog`
(`schema.sql:744`) selects everything not in `(Implemented, Superseded, Obsolete, Rejected)`.
The derived backlog therefore reports **155 open work items** for a project whose ladder is
complete. A migration of a finished package cannot leave every work item open by default.

### D-12 — Ordering bug creates a permanent structural dead-end — **HIGH, unfixable after the fact**

`migrate.py:269/350` post-bumps FR/AC `Draft → Approved` on import. `trg_acceptance_criteria_immutable`
(`schema.sql:710`) then forbids changing `slice_id` on any `Approved` AC. Because v1 has no slice
concept, **every AC is Approved with `slice_id` NULL and can never be bound to a slice** — short of
superseding all 74. `v_phase_exit` (`schema.sql:795`) joins `acceptance_criteria.slice_id`, so it
**returns 0/0/0 for every phase, permanently**. The package ships with a dead view and no way back.
**Suggested fix:** leave imported ACs `Proposed` (or defer the status bump until after any slice
binding), so the immutability guard closes *after* the structure is complete rather than before it
exists.

### The process gap behind all of this

`gate_run()` has no **null-rate**, **mandatory-field-coverage**, or **length-histogram** check, and
the migration reports no **source→target field mapping**. Row-level validation (which is what the
preview counts, `identifier_gaps` and the audit split amount to) is structurally incapable of
catching column-level damage — this is well understood in migration tooling generally, where
row-level validators explicitly do not support schema-reshaping migrations. Two cheap additions
would have caught eight of the twelve classes above:

1. **Post-populate null-rate profile per typed column**, flagging any column at ~100% NULL whose
   source field was populated.
2. **Length histogram per text column**, flagging mass at exactly the cap (a natural distribution
   has no spike at exactly *N*).

## Verdict

2.3.0 closes every actionable finding from findings_3 — verified against the same package that
generated them, in a run whose preview matched the 2.2.0 fixture row-for-row. First
zero-repair, zero-patch migration of the three. ~~Remaining asks are ergonomic only (review.html
`<details>`/TOC; the three calibration nits above). From the operator side, the migration path
is done maturing on this fixture: there is nothing left on it we would block a ship on.~~

> **Verdict amended 2026-07-22 (post-cutover).** The two struck sentences are withdrawn. The
> paragraph above them still stands: the **operator-facing workflow** is mature — preview →
> grouped decisions → populate → cutover really did need zero intervention, and that is a genuine
> achievement across three runs.
>
> But *"zero repair actions"* measured the **process**, not the **product**. §D lists **twelve
> data-degradation classes** in the very run this report certified, four of them HIGH and one
> (**D-12**) permanently unfixable after cutover. **We would now block a ship on D-0/D-1/D-2**
> (silent truncation and hyphen deletion destroying `statement` text with no warning at any stage)
> **and on D-12** (the Approved-before-slices ordering bug that kills `v_phase_exit` forever).
>
> The honest summary of all four runs: **the migration got progressively better at telling the
> operator what it decided, and never once told them what it damaged.** Every ledger added across
> 2.1.0 → 2.3.0 reports *choices*; none reports *fidelity*. The next increment should be a
> fidelity ledger — null-rate, truncation, and field-mapping coverage — not another decision
> ledger.
>
> Standing correction from this exercise: **`title_fallbacks` is not cosmetic.** findings_3 B4
> asked for it to be grouped because it was noisy; 2.3.0 delivered that and we called it fixed.
> Grouping a data-loss signal makes it quieter, not safer. That misread is ours as much as the
> tool's, and it is the single most useful thing in this report.
