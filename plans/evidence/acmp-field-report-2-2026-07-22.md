<!-- Archived by plan 018 Phase 4 (field-evidence C17-C19). Verbatim copy of the second
ACMP operator field report (findings_2.md in the ACMP repo), produced during the successful
production migration on 2026-07-21/22 under Tamheed v2.1.0. Verdict: production-quality;
all plan-017 guards fired on real data. Do not edit: this is evidence, not documentation. -->

# Tamheed v2.1.0 — field report: migrating a real Keystone v1 package (`package_migrate`)

**Context.** Feedback from a complete, real-world run of `migrate` mode on 2026-07-21/22:
the ACMP planning package (`docs/`, Keystone v1.0.0, validator-green 7/7, ~90 files) migrated
into a v2 store and fully cut over in one session. Scale: 218 requirements, 74 ACs + 74 audit
verdicts, 33 ADRs, 28 decisions, 58 OQs, 23 deferred-work rows, 155 WBS items, 50 narrative
docs / 483 sections, 1,032 trace edges. Host: Claude Code on Windows 11, plugin-registered
stdio server, `uv` launch path. Every claim below was observed directly (file:line refs are
into the 2.1.0 plugin source).

**Bottom line.** The migration worked end-to-end on the first populate, the staged gates and
fidelity report behaved exactly as documented, and the field-evidence guards (MADR fallback,
D-nn rescue, stale-manifest handling, no-poison-dir cleanup) all fired correctly on real data.
The findings below are ranked; only #1 risks silent data degradation.

---

## 1. Silent status coercion to `Draft` is unreported in the preview (highest priority)

`_status()` (`migrate.py:78-83`) maps any v1 status outside the v2 lifecycle vocabulary to the
default (`Draft`), and **nothing in the stage-2 preview mentions it**. In our package this hit
11 real rows: OQ-034 (`Resolved`), and 10 risk rows (`Open` ×7, `Monitoring` ×2, `Closed` ×1).
A `Resolved` open question and every open risk would have migrated as `Draft` — semantically
*backwards* — and we only caught it by reading `migrate.py` before running. The original cell
survives in `custom_attributes.v1`, so nothing is *lost*, but the coercion itself is invisible:
the preview's `unmapped` ledger is id-granular for other losses, yet says nothing here.

**Suggestion:** add a `status_coerced` ledger to the preview (`[{id, original, coerced}]`),
symmetrical with `unmapped`. That turns "read the parser source before trusting the preview"
into "read the preview." The blessed patch path then covers the fix (it did for us — a 15-row
patch). Bonus: common v1 vocabularies (`Resolved`, `Open`, `Monitoring`, `Closed`, `Active`)
could get default mappings in `STATUS_MAP` with the coercion still reported.

## 2. Phase rows parsed from tables get the id as their title

The roadmap's phase table is headed `| Phase | <name> | Size | Goal |`. The title-alias list in
`_map_register_row` (`migrate.py:188-190`) includes `"phase"`, which matches **column 0 — the id
column itself** — so all 4 phases migrated with `title="PH-0"`…`"PH-3"` and (no status column)
`lifecycle_status=Draft`. Meanwhile *weak-definition* phases get `Approved` (`migrate.py:536-538`)
— so the richer source produced the poorer row. We repaired via patch + deterministic rerun
(painless, see §Positives), but:

**Suggestion:** exclude the id column from title-alias resolution (a title alias that resolves
to the same cell the id came from is never right), and consider a `name` alias. Same class of
fix as #1: report title-fallback rows in the preview.

## 3. `adrs/README.md` prose is dropped, bypassing the C13 catch-all

Everything under `adrs/` routes to `_map_adr` and then `continue`s (`migrate.py:462-464`). An
index/README in that directory yields the unmapped note ("ADR file without front-matter or
heading id") but its **prose never reaches the `doc_kind='other'` narrative catch-all**, which
the code comments promise ("prose is never silently dropped", `migrate.py:502-507`). Same for
`architecture/diagrams/README.md` (unknown diagram stem → skipped ledger only). Both are listed,
so the loss is *visible*, but C13's spirit is that listed-AND-preserved beats listed-only.

**Suggestion:** on ADR-parse failure (and unknown diagram stems), fall through to the narrative
'other' path instead of `continue`.

## 4. `handoff_emit`'s `.mcp.json` is machine- and version-specific

The emitted config (`tamheed_server.py:507-514`) hard-codes an absolute path into the *versioned*
plugin cache (`…\plugins\cache\tamheed\tamheed\2.1.0\server\tamheed_server.py`). Three issues:
it breaks on the next plugin version bump; it's meaningless on any other machine (so committing
it — which the cutover flow implies, since the executor needs it — ships a broken config); and on
a plugin-registered host it double-registers a server named `tamheed`. We gitignored it and rely
on the plugin's own `.mcp.json`.

**Suggestion:** either emit `${CLAUDE_PLUGIN_ROOT}`-relative (as the plugin's own bundled
`.mcp.json` already does), or detect the plugin registration and skip/annotate the write, or
document "gitignore this file on plugin-registered hosts" in the cutover note.

## 5. `review.html` does not scale gracefully to a real package

At our (modest) scale the export is 2.1 MB / ~16k lines, and jump-scrolling it froze the Chrome
renderer for multiple seconds at a time (observed as repeated 30 s CDP screenshot timeouts while
driving the page). Two aggravators: the 1,032-row edge table renders fully expanded, and there is
no visible table of contents — we discovered the `#traceability` anchor by reading
`export_html.py:201-213`, not from the page.

**Suggestion:** wrap the big tables (all-edges, document sections) in `<details>`/`<summary>`
(JS-free, CSP-safe), and add a small sticky TOC of the five section anchors. Both preserve the
zero-JS/deterministic contract.

## 6. Freshness stamp reads as staleness right after migration

The Traceability section shows "Freshness: iteration 1 · latest recorded activity: 2026-07-06" —
correct by design (package-stored timestamps only, never wall clock; the date is the v1
manifest's `generated`), but on day one after migration it *reads* like the export is two weeks
stale. **Suggestion:** label the migrated timestamp for what it is ("v1 package generated
2026-07-06; no v2 activity recorded yet") until the first `progress_update`/`audit_record` lands.

## 7. Narrative documents lose their front-matter status silently

`_status(pf.front_matter.get("status"))` coerces non-lifecycle statuses (our progress docs used
`active`) to `Draft`, and unlike ADRs (`migrate.py:356-357`) the narrative row's
`custom_attributes` stores only the path — the original front-matter is not preserved
(`migrate.py:517-519`). Cosmetic, but it's the one place we found where a v1 value is neither
mapped nor preserved. **Suggestion:** include `front_matter` in narrative `custom_attributes`,
and let ledger #1 cover the coercion.

## 8. Smaller notes

- **Preview could show per-file row counts.** `partial_files` names the files but not how many
  rows each yielded; family-level counts were enough for us, but per-file counts would make a
  bad parse locatable in seconds.
- **`entity_query` default `limit=100`** silently truncates a 218-row family; a `count`-only
  mode (or echoing `total` alongside `rows`) would remove the guesswork. (The fidelity report's
  counts filled this gap for us.)
- **MCP tool descriptions leak internal plan jargon** ("plan 010", "plan 011", "W-V2-7") into an
  operator-facing surface. Cosmetic.
- **Frozen-contract provenance matters:** the bundled frozen v1 validator differs byte-wise from
  the Keystone 1.0.0 plugin's copy yet both pass our package 7/7. Fine — but we have prior scar
  tissue from a *stale* validator copy (a 0.1.0 build) falsely failing G-IDS with 74 findings, so
  a version/commit stamp printed in the pre-flight result would make "which contract judged this"
  auditable.
- **`handoff/` lands at the target root** with fixed names (`prm-00N-<kind>.md`). Our repo already
  had a (frozen) `docs/handoff/`; no collision, but a `target subdir` option would be tidy.

---

## Positives worth keeping exactly as they are

- **The staged flow earns its ceremony.** Preview-first with `zero_families` as a hard tripwire,
  operator confirm, and `allow_zero` as an explicit acknowledgment (not a default) is the right
  shape. Our preview counts matched an independent disk count to the row, including the
  stale-manifest deltas (ADR 33 vs 23, OQ 58 vs 48, AC 74 vs 66, DEC 28 vs 27, WBS 155 vs 20)
  — "disk wins, deltas reported, never reconciled" behaved exactly as the contract says.
- **The field-evidence guards all fired on real data.** MADR fallback caught **all 33** of our
  ADRs (none had YAML front-matter — front-matter-required would have migrated zero, exactly as
  the C12 comment warns); the `D-nn` rescue produced 23 clean `DW-` rows; the AC statement took
  the raw cell (every one of our ACs exceeds 120 chars); "Test ref" resolved as the evidence
  alias; stale omissions beside real rows (milestones) were dropped.
- **Repair loop is genuinely pleasant.** parse → patch → populate with a merge-by-id JSON,
  echoed in the preview, plus deterministic parsing (no wall-clock/PRNG) meant our
  delete-and-rerun produced a byte-identical package modulo the 4 patched rows. `populate`'s
  step-named error context and the no-poison-dir cleanup (`migrate.py:596-659`) meant zero fear
  of a wedged half-package.
- **In-process pre-flight (C11) worked on Windows** — no subprocess wedge, crash isolation
  intact; the single-writer lock took and released cleanly every cycle.
- **Honesty features:** `gate_run`'s evidenced/narrated split (73/1 — the 1 being the package's
  one Pending AC, correctly), the vacuous-G-TRACE warning design, and `fidelity`'s
  "reported, never auto-resolved" stance all reinforce trust instead of asking for it.
- **`handoff_emit` niceties:** append-only CLAUDE.md with idempotence guard, and the stale-v1
  detection (it flagged our `validate_package.py` reference) is a thoughtful cutover tripwire.
  G-INJECT screened 3 real prompt files with zero false positives.
- **Canonical JSONL contract:** LF/no-BOM/PK-ordered output passed a repo-wide gitleaks scan
  and produced row-scoped diffs as promised; `:memory:` SQLite (no DB file to accidentally
  commit) is the right call.

## Verdict

Production-quality for its intended job. Fix #1 (report status coercion) and #2 (id-as-title)
and a careful operator no longer needs to read the parser source before trusting the preview —
which is the tool's own stated bar.
