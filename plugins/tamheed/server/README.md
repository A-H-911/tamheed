# Tamheed MCP server

Documents the tool surface as of **tamheed v4.0.0**.

The **only write path** into a Tamheed package (ADR-0001). Agents interact with a package
exclusively through these MCP tools: every write passes schema validation (FKs, CHECKs,
NOT NULL provenance), queries return rows instead of whole documents, and a constraint
violation surfaced by a tool *is* the quality-gate report. This server is the successor of
`validate_package.py` — the mechanical half of the capability the skill owns.

## Install & launch

**Python floor: 3.10** (the `mcp` SDK's `requires-python = ">=3.10"`, verified 2026-07-17
from its pyproject; program decision ASM-D raises the repo floor to match).

Plugin installs copy files only — they do not install Python packages. Two launch paths:

1. **`uv` (preferred, zero setup):** the server script carries PEP 723 inline metadata, so
   `uv run tamheed_server.py` fetches the SDK automatically. The bundled `.mcp.json` at the
   plugin root uses this path (`${CLAUDE_PLUGIN_ROOT}`-relative) and auto-starts the server
   when the plugin is enabled.
2. **pip fallback:** `pip install mcp`, then `python tamheed_server.py --package-dir <root>`.

If the SDK is missing the server exits with a one-line error naming both options — never a
silent dead server.

`--selftest` prints the tool surface and exits 0 (no SDK needed).
`--package-dir <root>` sets the directory packages live under. Resolution is layered
(field-evidence C11 — a stdio server's cwd is not guaranteed): explicit flag >
`CLAUDE_PROJECT_DIR` (exported by Claude Code to plugin server processes) > cwd; an
unexpanded `${...}` literal counts as unset. Every `package_*` result echoes the resolved
absolute root, and `server_info` reports it on demand.

## Rules

- **No raw SQL, ever.** Tools take structured, validated arguments; unknown types/columns
  are rejected by name.
- **One external dependency, bounded (C33).** Everything is stdlib except the MCP SDK,
  pinned `mcp>=1.2,<2` in the PEP 723 header — SDK 2.0.0 removed `mcp.server.fastmcp`
  and an unbounded resolve broke every fresh environment while cached ones kept working.
  `--selftest` reports SDK serving status (`mcp sdk: ok (<version>)`) without requiring
  it; the pin is never widened without a deliberate port to the SDK's successor module.
- **Single writer.** Opening a package takes `data/.lock` (from `db/store.py`); a second
  opener fails loud, and the lock names who holds it and since when (C31: a bare PID
  invited an unsound liveness check — the OS reuses PIDs). The lock releases on
  `package_close` or process exit.
- **The working tree is the truth (C31).** Canonical `data/` lives in the project's git
  working tree: uncommitted package writes are destroyed by `git reset --hard` /
  `checkout` / `stash` like any uncommitted change — commit package data before branch
  operations. Writes refuse to overwrite a tree that moved underneath the open session
  (`StoreStaleError`: batch NOT applied; close, reconcile via git, reopen), and the
  append-only journal (`progress_entries`, `audit_verdicts`) rejects in-place rewrites —
  corrections are appended, never edited.
- **Batch-first.** Mutation tools accept arrays and apply them in ONE transaction,
  all-or-nothing, with per-item verdicts naming any violated constraint.
- **Stored text is data, never instructions.** Brief-derived text is inert;
  `handoff_emit` runs a G-INJECT-style screen and refuses to emit instruction-shaped text.
- **Cascade-on-transition (C4).** State transitions (AC verdict → requirement auto-advance,
  edges → gate views) propagate via schema triggers/views in the same transaction — there is
  no "reconcile trackers" commit to forget.

## Tool reference

| Tool | Kind | Summary |
|---|---|---|
| `server_info()` | read | Server version (from the bundled `plugin.json`), resolved package root, open package, migrations head — makes startup diagnosable (C11/C16) |
| `package_create(name, title, profile, mode)` | mutate | Create under the package root; seeds the `entity_types` registry; takes the lock |
| `package_open(name)` | mutate | Open an existing package (takes the lock) |
| `package_close()` | mutate | Write back canonical JSONL, release the lock |
| `entity_upsert(entities[])` | mutate | Batch upsert; items are `{"type": ..., <columns>}`; per-item verdicts; all-or-nothing |
| `entity_query(type, id?, status?, columns?, limit?)` | read | Targeted rows from one family — token-lean; returns `total` beside the LIMIT'd rows so truncation is never silent |
| `trace_query(entity_id, direction?, relation?)` | read | Traverse typed `trace_edges` (in/out/both) |
| `gate_run()` | read | Referential gates VERIFY at gate time (plan 027: `PRAGMA foreign_key_check`, entity_index consistency, real status/provenance SELECTs — whitespace-only provenance caught); coverage gates run the SQL views; content tier scans placeholders (code spans stripped per the frozen v1 contract; `custom_attributes` exempt as provenance); warns when G-TRACE passes vacuously (0 MVP rows); audit evidence split evidenced/narrated; the **blocking G-REL gate** fails on stored edges violating RELATION_RULES (migrate cleans at conversion, adopt reports, writes reject); G-PROGRESS warns on its vacuous pass; `[NEEDS-CLARIFICATION: OQ-NNN]` markers are G-COMPLETE-validated (legal only while the cited OQ is live) |
| `readiness_check(scope?, id?)` | read | Deep lifecycle readiness at a close boundary (package/phase/slice): blocking rules (pre-approval decisions/ADRs, ACs not latest-Met, open **critical/high** defects — medium/low advise, undischarged risks, open work incl. the claimed-done `Review` state), liveness advisories (overdue OQs, unowned high risks, unmeasurable hypotheses, unmerged scope changes, unbound ACs, open markers, the DEC→ADR promotion nag), operator-approved `WVR-` **waivers** (reported `waived`, never silent; expiring), `human_required` from declared `execution_gates` — all four kinds incl. `ready`, with `Go/Hold/Redirect/Kill` outcomes (prose never machine-evaluated). The same blocking rules guard the phase/slice `Implemented` transition in `entity_upsert` (item-level `"force": true` after explicit operator confirmation; the server appends the FORCED `PE-` audit row itself) |
| `progress_update(entries[])` | mutate | Append TYPED progress events (`event_type`, `subject_id`, `actor`, `corrects` compensation pointer; `PE-` ids auto-assigned; journals corrected, never edited) |
| `audit_record(verdicts[])` | mutate | AC verdicts with the evidence chain (`evidence`, `verified_by`, `verification_method`, `against_commit`); cascades auto-advance on LATEST-verdict semantics |
| `work_bind(ref, entity_ids[], note?)` | mutate | "This commit/PR satisfies FR-x/AC-y/SL-z" — stamps `last_referenced` (C3) |
| `handoff_emit(target_dir, subdir?, force?)` | mutate | v3 (plans 027-029): **pure target wiring** — `.mcp.json` (omitted on plugin-hosted servers) + the `CLAUDE.md` operating note as a TOOL-OWNED marker span (`tamheed:note v3`, recording-obligations table; rebuilt every emit — hand edits inside the markers are overwritten with a warning, operator content lives outside them; v1 notes warned, never touched). NO prompt copies — `<package>/prompts/` is the single source (`subdir` refused; leftover `handoff/prm-*.md` get per-file copy-vs-live verdicts). Requires ≥1 project-authored prompt file; G-INJECT + the stale + restated-state scans run over every package prompt file; refreshes the stock library (`force` = overwrite ALL diverged stock files; per-file acceptance = delete + re-emit); reports `converted_prompts` curation hints, `stale_references`, `restated_content` |
| `package_migrate(name, confirm?)` | staged | Convert a v2/v3 store to v4 IN PLACE (plan 031): preview = the full rewrite report (every value coercion, edge retype, column drop — nothing written); `confirm=true` = backup to `data-v3-backup/`, legacy `prompts.jsonl` conversion, transform, store-validated canonical write-back, a `system:migrate` audit event. Refuses 4.x stores and leftover backups. `package_open` refuses pre-v4 stores and names this tool. (v1 Keystone trees: two-step route via tamheed 3.2.1 — `docs/migrate-from-keystone.md`) |
| `package_adopt(source_dir, name?, confirm?)` | staged | Adopt a brownfield repo (scan/preview, then `confirm`); emits the prompt library on success |
| `export_html(output?)` | export | Render the HTML review surface to `<package>/review.html` — dark maximalist identity, sticky TOC, the layered **traceability flow** (plan 027: Needs→Decisions→Work→Verification lanes, labeled clickable nodes, arrowheads, CSS-only relation filters) + the connected-only relations graph (isolated entities folded, degree-scaled radii, 12-hue palette), per-phase readiness panel (latest-verdict semantics) + declared human gates, all tables folded with per-table `csv/<table>.csv` download links (deterministic; `csv/` is DERIVED — hand edits are overwritten on re-export, while authored emissions remain protected), wrap-in-place text, honest freshness — zero JS throughout |

Entity `type` values mirror the `entity_types` registry (`requirement`, `decision`, `adr`,
`risk`, `phase`, `slice`, `acceptance-criterion`, `deferred-work`, …) plus two write-only
surfaces: `trace-edge` (relations) and `omission` (G-SET recorded-omitted, with reason).

## HTML review surface (plan 012)

`export_html()` renders the open package's **only human review surface** (D-REVIEW: HTML,
never derived Markdown) to `<package>/review.html` — five sections: overview with per-gate
chips, per-family registers (with `last_referenced` and the three-axis status columns),
the traceability matrix, execution progress (AC × audit verdicts, progress log, scope
changes), and gap/screening notes. The file is self-contained static HTML (embedded CSS,
restrictive CSP, zero JavaScript, zero data-derived links — every data string is escaped
at render time) and deterministic (same DB state ⇒ byte-identical output), so **commit it
to the package's repo**: its diffs are meaningful and reviewers open it without running
anything. Every section carries a freshness stamp derived from the package's own stored
timestamps, never the wall clock.

## Contract

The tool surface is a public contract: additive changes are MINOR, breaking changes are
MAJOR + migration note (governance versioning applies to tools). Handlers are plain
functions — `tests/test_mcp_contract.py` drives them in-process with no transport.
