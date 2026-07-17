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
`--package-dir <root>` sets the directory packages live under (default: cwd).

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
| `package_create(name, title, profile, mode)` | mutate | Create under the package root; seeds the `entity_types` registry; takes the lock |
| `package_open(name)` | mutate | Open an existing package (takes the lock) |
| `package_close()` | mutate | Write back canonical JSONL, release the lock |
| `entity_upsert(entities[])` | mutate | Batch upsert; items are `{"type": ..., <columns>}`; per-item verdicts; all-or-nothing |
| `entity_query(type, id?, status?, columns?, limit?)` | read | Targeted rows from one family — token-lean |
| `trace_query(entity_id, direction?, relation?)` | read | Traverse typed `trace_edges` (in/out/both) |
| `gate_run()` | read | Referential gates report as write-time-enforced; coverage gates run the SQL views; content tier scans placeholders; audit evidence split evidenced/narrated |
| `progress_update(entries[])` | mutate | Append progress entries (`PE-` ids auto-assigned) |
| `audit_record(verdicts[])` | mutate | AC verdicts, optional `evidence` ref (C7); cascades auto-advance |
| `work_bind(ref, entity_ids[], note?)` | mutate | "This commit/PR satisfies FR-x/AC-y/SL-z" — stamps `last_referenced` (C3) |
| `handoff_emit(target_dir)` | mutate | Emit prompt files + executor-side `.mcp.json` + `CLAUDE.md` note (W-V2-7); injection-screened |
| `package_migrate(source_dir)` | stub | Plan 010 |
| `package_adopt(source_dir)` | stub | Plan 011 |
| `export_html()` | stub | Plan 012 |

Entity `type` values mirror the `entity_types` registry (`requirement`, `decision`, `adr`,
`risk`, `phase`, `slice`, `acceptance-criterion`, `deferred-work`, …) plus two write-only
surfaces: `trace-edge` (relations) and `omission` (G-SET recorded-omitted, with reason).

## Contract

The tool surface is a public contract: additive changes are MINOR, breaking changes are
MAJOR + migration note (governance versioning applies to tools). Handlers are plain
functions — `tests/test_mcp_contract.py` drives them in-process with no transport.
