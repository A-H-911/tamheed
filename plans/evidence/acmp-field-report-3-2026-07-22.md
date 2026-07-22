<!-- Archived by plan 019 Phase 4 (field-evidence C20-C22). Verbatim copy of the third
ACMP operator field report (findings_3.md in the ACMP repo): the from-scratch re-migration
on Tamheed v2.2.0, 2026-07-22 — a regression pass of the 2.1.0 findings. Verdict: "Ship it";
zero repair loops. Do not edit: this is evidence, not documentation. -->

# Tamheed v2.2.0 — field report: re-migrating the same Keystone v1 package (`package_migrate`)

**Context.** Follow-up to `findings_2.md` (the 2.1.0 run of 2026-07-21/22, later reverted by
operator choice). On 2026-07-22 the operator ordered a from-scratch re-run of the identical
source package (`docs/`, Keystone v1.0.0, ~90 files) on plugin **2.2.0**, with full cutover,
completed in one session. Scale unchanged: 218 requirements, 74 ACs + 74 audit verdicts,
33 ADRs, 28 decisions, 58 OQs, 23 deferred-work rows, 155 WBS items, 21 KPIs, 50 tests,
52 narrative docs / 495 sections, 1,032 trace edges. Host: Claude Code on Windows 11,
plugin-registered stdio server. This report is therefore also a **regression test of the
2.1.0 findings**: same input, same operator, new parser. File:line refs are into the 2.2.0
plugin source. Every claim below was observed directly unless marked unverified.

**Bottom line.** The 2.2.0 run needed **zero repair loops**: one preview, one confirm, first
populate was final. The two findings that mattered most last time (#1 silent status coercion,
#2 id-as-title) are fixed and their fixes behaved exactly as documented on real data. The
operator no longer needs to read the parser source before trusting the preview — the 2.1.0
report's stated bar is met. What remains below is one structural leftover, a handful of
polish items, and confirmations.

---

## A. 2.1.0 findings — regression status on 2.2.0

| # (2.1.0) | Finding | Status on 2.2.0 |
|---|---|---|
| 1 | Silent status coercion to Draft | **FIXED, verified.** `status_coerced` ledger reported all 21 coercions id-granularly; semantic defaults (`Resolved→Implemented`, `Open/Monitoring/Active→Approved`, `Closed→Obsolete`, `migrate.py:34-44`) covered 16 of them sensibly; the remaining 5 project-specific words (`Instrumented`, `Met`, `Living`) defaulted to Draft *visibly* and were overridden via `status_map` on the confirm call. The 15-row hand patch our 2.1.0 run needed is gone. |
| 2 | Phase title = id ("PH-0") | **FIXED (title half), verified.** All 4 phases migrated with real titles ("Discovery & Validation", …) and appeared in the new `title_fallbacks` ledger. See B1 for the surviving status half. |
| 3 | `adrs/README.md` prose dropped | **Fixed per contract, partially verified.** Still listed in `unmapped` ("ADR file without front-matter or heading id") as designed; narrative counts rose 50→52 docs / 483→495 sections vs the 2.1.0 run of the same tree, consistent with the C17 fall-through landing it (and the diagrams README) as `other` docs. We did not query the individual DOC row. |
| 4 | `.mcp.json` machine/version-specific | **FIXED, verified on Windows.** The plugin-hosted check normalizes backslashes before matching (`.replace("\\", "/")`, `tamheed_server.py:566-567`) — a detail we specifically feared would break on Windows paths, and it doesn't. No `.mcp.json` written; the CLAUDE.md note correctly says the plugin provides the server. |
| 5 | `review.html` scale | **Unverified this run.** Export succeeded at 2,118,492 bytes — essentially the same size as 2.1.0's 2.1 MB, which *suggests* the big tables are still fully expanded, but we did not open the page this session. Carrying the suggestion forward unchanged (wrap edge/section tables in `<details>`, add a small TOC). |
| 6 | Freshness stamp reads as staleness | **Unverified this run** (review.html not opened). |
| 7 | Narrative front-matter status lost silently | **FIXED (reporting half), verified.** Narrative statuses now flow through the ledger: DOC-047/048/050/051 `active→Approved` and DOC-052 `Living→Approved` (after override) all appeared in `status_coerced`. Front-matter preservation in `custom_attributes` not independently queried. |
| 8a | Per-file row counts in `partial_files` | **FIXED, verified — and immediately useful.** The counts made two things visible in seconds: FR definitions are split across two files (`requirements/functional.md`: 77 + `domain/user-stories-mvp.md`: 78), and a single stray governed id lives in `domain/architecture-detail.md` (1 row). Exactly the "bad parse locatable in seconds" property we asked for. |
| 8b | `entity_query` default limit silently truncates | **FIXED, verified.** Results now carry `total` alongside `rows` (`limit=1` returned `total: 218`), which is all the count-mode we wanted. |
| 8c | Validator provenance | **FIXED, verified.** Preview carries `validator: {sha256, bytes}` (`58468f4e…`, 60,401 B). |
| 8d | `handoff/` target subdir | **FIXED (present).** `subdir` param exists (default `handoff`); we used the default. |

Also re-confirmed unchanged from 2.1.0: preview counts matched an independent disk count made
before any tool ran; the stale-manifest deltas (OQ 48→58, DEC 27→28, ADR 23→33, AC 66→74,
WBS 20→155) reported and never reconciled; MADR fallback caught all 33 ADRs; `D-nn`→`DW-` rescue
(23 rows); stale omissions beside real rows dropped (milestones, research) leaving exactly the 3
legitimate ones (hypothesis/experiment/poc); G-INJECT screened 3 real prompts with zero false
positives; gates 7/7 with the honest evidenced/narrated split (73/1 — the 1 being the package's
one Pending AC).

## B. New findings (ranked; nothing in this run risks silent data degradation)

### 1. Table-parsed phases still land `Draft` — the status half of 2.1.0-#2 survives

2.2.0 fixed the *title* asymmetry, but the lifecycle asymmetry between parse paths remains:
a roadmap phase **table** with no Status column yields `lifecycle_status=Draft` (empty cell =
"absence, not coercion" → silently defaulted, correctly absent from `status_coerced`), while a
**weak-definition** phase (`## PH-1` heading) gets `Approved` (`migrate.py`, weak-def synthesis).
So the richer source still produces the poorer row on one axis. We knew to look only because of
the 2.1.0 scar; the repair (4-row merge-by-id patch, `updated: 4` echoed in the preview) was
painless — but a first-time operator gets 4 Draft phases with no signal anywhere.

**Suggestion:** a small `status_defaulted` companion ledger (or a per-family note) for rows in
status-bearing families whose register simply has no status column — one line per (file, family,
row-count), not per row. Alternatively: default table-parsed phases to `Approved` for parity with
weak definitions, and let the ledger report it.

### 2. `handoff_emit`'s stale-v1 warning is append-once and never retracted

The first emit correctly appended the CLAUDE.md note **including** the "Stale v1 references
detected" blockquote (`tamheed_server.py:607-612`). After we fixed all four references, the
verification re-run returned `stale_references: []` — but the warning blockquote stays in
CLAUDE.md forever, because the whole note is guarded by the `"## Tamheed progress tracking"`
idempotence check (`:613`) and never re-examined. We hand-deleted it. The warning's lifetime is
coupled to the first append, not to the current scan result.

**Suggestion:** emit the warning as a separately-managed block (its own marker), removed or
rewritten on a subsequent emit whose scan is clean. That would also make "re-run emit to verify
the cutover" — which is otherwise an excellent verification loop — fully self-contained.

### 3. Re-running `handoff_emit` unconditionally rewrites the prompt files

The verification re-run listed all three `handoff/prm-*.md` in `written` although their content
was byte-identical (deterministic rewrite). Harmless today, but (a) `written` overstates what
changed, and (b) if an operator had hand-adjusted an emitted prompt — they are operator-facing
repo files — a verification re-run silently clobbers the edit.

**Suggestion:** skip-if-identical and report such files under `unchanged`; if content differs
from what would be emitted, either overwrite-and-say-so or refuse — but don't silently replace.

### 4. `title_fallbacks` is noisy at real-package scale

131 entries: 77 FR user-story rows (title = truncated statement — expected, arguably not a
"fallback" worth flagging since the statement *is* the only title-like cell), 50 TEST rows (all
correct suite names), and the 4 phases — the only genuinely interesting entries, buried at
position ~78. The ledger did its job, but the signal-to-noise is ~3%.

**Suggestion:** group the ledger by (table, source column) with counts, expanding ids only for
small groups — e.g. `{"requirements": {"count": 77, "note": "title := truncated statement"},
"phases": {"count": 4, "ids": [...]}}`. The operator decision unit is the group, not the row.

### 5. `status_coerced` could pre-group by proposed mapping

Same shape as #4: the 21-row ledger collapses to 6 operator decisions (`Open×7→Approved`,
`Monitoring×2→Approved`, `active×4→Approved`, plus 3 singletons and 2 project words). We
presented it to the operator grouped by original word, which mapped cleanly onto the
multi-select confirmation the SKILL prescribes — the tool could ship that grouping:
`[{original, proposed, count, ids}]`. Row-granular data can stay; the grouped view is what gets
confirmed.

### 6. Compound-cell `status_map` keys work — but the contract doesn't say so

`references/migration-v1.md` §12 says compound cells ("Instrumented (P12)") never auto-map,
exact match only. What it doesn't say is that a compound **literal supplied as a `status_map`
key does match** after normalization — we passed `"Instrumented (P12)": "Implemented"` and
`"Met (ADR-0009)": "Implemented"` and both applied. That's the right behavior; one sentence in
the contract would save the next operator the experiment.

### 7. The v1 progress log never becomes `progress_entries` (by design, but undocumented)

`INSERT_ORDER` (`migrate.py:650-654`) contains no `progress_entries`: the v1 running narrative
migrates as a narrative document (our progress docs are DOC-047/048/050/051), and the v2
progress ledger starts empty — the freshness/iteration surfaces begin from zero while years of
dated history live in a DOC body. Defensible (PE rows are v2-native, timestamps would be
fabricated), but it's a mapping decision the contract's field table doesn't mention.

**Suggestion:** one row in the mapping table ("progress log → narrative document; no PE rows
synthesized") — or, ambitiously, an opt-in that parses dated log bullets into PE rows with the
source date preserved.

### 8. Cosmetics

- **Mixed path separators** in one result: `handoff_emit.written` uses `handoff\prm-…`
  (backslash) while `prompt_library` uses `prompts/…` (forward slash). Windows-only nit.
- **The confirm result embeds a `preview` block whose ledgers show post-override values** —
  correct and actually what you want to archive, but it is *not* identical to the stage-2
  preview (which showed defaults), and nothing labels the difference. An auditor diffing the
  two could read it as nondeterminism. A one-word annotation (`"status_coerced_basis":
  "status_map"` vs `"defaults"`) would remove the ambiguity.
- MCP tool descriptions are now operator-clean (the 2.1.0 "plan 010/W-V2-7" jargon leak is
  gone from every surface we touched).

## C. Positives worth keeping exactly as they are

- **Zero-repair run.** Preview → one grouped operator confirmation (status_map) + one 4-row
  patch → populate → gates 7/7 → cutover. No delete-and-rerun cycle was ever needed; the entire
  2.1.0 repair playbook went unused because the ledgers moved the decisions to *before* populate.
- **Determinism, now proven across the full lifecycle.** The confirm-stage re-parse matched the
  stage-2 preview to the row; and after merge we did an idle `package_open` → `package_close`
  round-trip on the committed store — **zero git diff**. Canonical JSONL is byte-stable across
  open/close cycles, which makes "did anything change?" a `git status` question. That property
  is worth a sentence in `db/CANONICAL.md` as a guarantee, because operators will lean on it.
- **The ledger→override loop is the right shape.** Ledger proposes, operator disposes, confirm
  call carries the decision, originals survive in `custom_attributes.v1` regardless of choice.
  At no point did we have to choose between trusting the tool and reading its source.
- **Per-file counts** (B-8a above) turned two would-be surprises (split FR sources, a stray id
  in a domain doc) into non-events.
- **The cutover tripwire earns its place.** `stale_references` found exactly the four real
  stale sites in AGENTS.md/CLAUDE.md (file:line + a usable suggestion each), including two we
  had initially missed in planning; the precision note about not matching bare "Keystone"
  (`tamheed_server.py:483-485`) held — our "Keystone-integration optional" constraint text
  correctly did not trigger. Re-running emit as the "is the cutover done?" check worked
  (modulo B2/B3).
- **`next` breadcrumbs** on every staged result were accurate enough to follow mechanically
  (including the "two sources of truth coexist until you rewire" warning, which is exactly the
  failure mode that bit the 2.1.0 cutover's planning).

## Verdict

2.2.0 clears the bar 2.1.0 set for itself: the preview is now sufficient grounds to run a
migration — we never opened `migrate.py` out of necessity this time, only to verify claims for
this report. Remaining asks are one structural leftover (B1, the phase-status asymmetry), two
`handoff_emit` lifecycle nits (B2/B3), and reporting ergonomics (B4/B5). Ship it.
