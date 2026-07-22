# Tamheed MCP server

The **only write path** into a Tamheed v2 package (ADR-0001). Agents interact with a package
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
- **Single writer.** Opening a package takes `data/.lock` (from `db/store.py`); a second
  opener fails loud. The lock releases on `package_close` or process exit.
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
| `gate_run()` | read | Referential gates report as write-time-enforced; coverage gates run the SQL views; content tier scans placeholders (code spans stripped per the frozen v1 contract; `custom_attributes` exempt as provenance); warns when G-TRACE passes vacuously (0 MVP rows); audit evidence split evidenced/narrated |
| `progress_update(entries[])` | mutate | Append progress entries (`PE-` ids auto-assigned) |
| `audit_record(verdicts[])` | mutate | AC verdicts, optional `evidence` ref (C7); cascades auto-advance |
| `work_bind(ref, entity_ids[], note?)` | mutate | "This commit/PR satisfies FR-x/AC-y/SL-z" — stamps `last_referenced` (C3) |
| `handoff_emit(target_dir, subdir?)` | mutate | Emit prompt files (into `<target>/<subdir>`, default `handoff/`) + executor-side `.mcp.json` (omitted on plugin-hosted servers — the installed plugin already registers `tamheed`) + the `CLAUDE.md` operating note with the tool cheat-sheet; emits the scenario prompt library into `<package>/prompts/`; reports `stale_references` (v1-flow pointers in CLAUDE.md/AGENTS.md, file:line + suggestion); injection-screened |
| `package_migrate(source_dir, name?, confirm?, allow_zero?, patch?, status_map?)` | staged | Migrate a conformant v1 package (preview, then `confirm`); `status_map` confirms/overrides the preview's `status_coerced` proposals; emits the prompt library on success |
| `package_adopt(source_dir, name?, confirm?)` | staged | Adopt a brownfield repo (scan/preview, then `confirm`); emits the prompt library on success |
| `export_html(output?)` | export | Render the HTML review surface to `<package>/review.html` — sticky TOC, folded large tables, honest freshness |

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
