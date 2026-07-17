# Plan 008 (B3): The Tamheed MCP server — the only write path into a package

> **Executor instructions**: Build plan. Deliverable = a working MCP server bundled in the plugin,
> plus its contract tests. STOP conditions are binding.
>
> **Drift check (run first)**: plan 007's deliverables must exist
> (`plugins/tamheed/db/{schema.sql,store.py,CANONICAL.md}` + passing
> `tests/test_db_roundtrip.py`). Missing → STOP.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED (first runtime dependency; new distribution path)
- **Depends on**: plans/007-b2-data-model-adr-ddl.md
- **Category**: architecture / build
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Per maintainer decisions D-MCP and D-STORE, agents interact with a Tamheed package **only through
MCP tools** — that is what makes integrity enforceable (every write passes validation), token use
efficient (queries return rows, not whole documents), and the package host-agnostic. A constraint
violation surfaced by a tool IS the quality-gate report. This server is the successor of
`validate_package.py`: the mechanical half of the capability.

## Verified platform facts (researched 2026-07-11 — cited, not assumed)

- Plugins bundle MCP servers via **`.mcp.json` at the plugin root** (or inline in plugin.json);
  servers auto-start when the plugin is enabled; file refs use `${CLAUDE_PLUGIN_ROOT}`; users
  approve per-server. Sources: code.claude.com/docs/en/mcp, /plugins-reference,
  anthropics/claude-plugins-official → plugin-dev → mcp-integration skill.
- The **official MCP Python SDK** (github.com/modelcontextprotocol/python-sdk, PyPI `mcp`) is
  maintained; its Python floor is **above 3.9 (≥3.10)** — re-verify the exact floor from its
  pyproject at build time and record it (program decision ASM-D: the repo's minimum Python rises
  to the SDK floor).
- Plugin installation **copies files only — it does not install Python packages** (W-V2-1). The
  SDK will not be present on user machines unless the launch strategy provides it.

## Design constraints (locked)

- **Launch strategy (W-V2-1)**: the server script carries **PEP 723 inline script metadata**
  (`# /// script` block declaring `mcp`) and `.mcp.json` launches it via `uv run` when `uv`
  exists; document `pip install mcp` as the fallback; if the SDK import fails, the server must
  exit with an actionable one-line error naming both options — never a silent dead server.
- **No raw-SQL tool. Ever.** Tools take structured, validated arguments.
- **Batch-first (W-V2-8)**: mutation tools accept arrays and apply them in one transaction —
  per-entity round-trips during generation would cost more tokens than v1's file writes.
- **Single-writer**: the server takes the package lockfile from plan 007's store; a second opener
  fails loud.
- **Untrusted-content posture carries over** (safeguard 18): brief-derived text is data; the
  server never interprets stored text as instructions; `gate_run` keeps a G-INJECT-style screen
  on handoff emission.
- **Field-evidence requirements (2026-07-17, binding — evidence in `plans/README.md` notes):**
  - **Cascade-on-transition (C4)**: one recorded state transition (AC verdict, ADR approval,
    slice completion) updates every dependent view in the same transaction — the "reconcile
    trackers" manual-commit class observed in the field (≥8 such commits in one project) must be
    structurally impossible to need.
  - **Work-binding surface (C3)**: a tool that records "this commit/PR satisfies FR-x / AC-y /
    slice-z" (and stamps `last_referenced`). Field data shows FR/AC got ZERO commit references
    across three projects — without a cheap binding surface at work time, requirement IDs stay
    planning ornaments.
  - **Evidence-bound verdicts (C7)**: `audit_record` accepts an optional evidence ref (test
    file, CI run id) and `gate_run` distinguishes evidenced from narrated verdicts — the field
    audits were the graded party grading itself.
  - **Package-resident slice plans (C8)**: entity CRUD covers per-slice execution plans and
    durable conventions, so executing agents stop externalizing them into sidecar folders.

## Tool surface (contract to implement; refine names in-plan, keep the set)

| Tool | Kind | Notes |
|---|---|---|
| `package_create` / `package_open` | mutate/read | create under `--package-dir`; open takes the lock |
| `entity_upsert` | mutate | ARRAY of entities; validates against schema + CHECK/FK on write; returns per-item verdicts naming violated constraints |
| `entity_query` | read | by type/id/status/iteration; targeted columns; token-lean |
| `trace_query` | read | traverse `trace_edges` (e.g. "what depends on DEC-004?") |
| `gate_run` | read | executes the coverage VIEWs + content scans; returns the gate report |
| `handoff_emit` | mutate | assembles prompts/handoff rows; runs the injection screen; ALSO writes the executor-side MCP config into the target project (`.mcp.json` + CLAUDE.md note) — W-V2-7: the executing agent must be able to record progress |
| `progress_update` / `audit_record` | mutate | the execution-tracking loop (used by the downstream agent) |
| `package_migrate` | mutate | stub here; implemented in plan 010 |
| `package_adopt` | mutate | stub here; implemented in plan 011 |
| `export_html` | read | stub here; implemented in plan 012 |

## Deliverables

1. `plugins/tamheed/server/tamheed_server.py` — the MCP server (official SDK, stdio transport),
   PEP 723 header, importing plan 007's `store.py`; connection factory sets
   `PRAGMA foreign_keys=ON`.
2. `plugins/tamheed/.mcp.json` — launch config using `${CLAUDE_PLUGIN_ROOT}` paths.
3. `tests/test_mcp_contract.py` — stdlib-runnable contract tests: drive the server's tool
   functions **in-process** (import and call the tool handlers directly — do not require a live
   MCP transport in CI): create → batch upsert (incl. one row violating a CHECK → per-item error
   naming the constraint) → query → trace → gate_run on a complete vs hollow package → lockfile
   conflict → missing-SDK error path (simulate ImportError).
4. `plugins/tamheed/server/README.md` — install/launch (uv path, pip fallback), tool reference,
   the no-raw-SQL and single-writer rules.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Contract tests | `python tests/test_mcp_contract.py` | exit 0 |
| Server starts (with SDK) | `uv run plugins/tamheed/server/tamheed_server.py --selftest` | prints tool list, exit 0 (implement `--selftest`) |
| Prior suites | `python tests/test_validate_package.py` + `python tests/test_db_roundtrip.py` | exit 0 |

## Scope

**In scope**: the four deliverables + `plans/README.md`. **Out of scope**: SKILL.md/references
(plan 009), migration/adopt/export implementations (010/011/012 — stubs return
"not implemented" errors), v1 validator and schemas (frozen), CI wiring (plan 013).

## Steps

1. Verify the SDK floor from its pyproject; record in server README + `plans/README.md` note.
2. Implement `store`-backed tool handlers as plain functions (testable without transport);
   wrap them with the SDK server; `--selftest` flag lists tools and exits.
3. Write `.mcp.json`; test plugin-local launch if the environment allows.
4. Contract tests (deliverable 3).
5. Server README.

**Verify** per the commands table after steps 2–5.

## Done criteria

- [ ] Contract tests exit 0; constraint-violation errors name the constraint/gate
- [ ] `--selftest` lists the full tool surface, exit 0
- [ ] Missing-SDK path produces the actionable error (tested)
- [ ] `.mcp.json` present, `${CLAUDE_PLUGIN_ROOT}`-relative
- [ ] Prior suites still green; `plans/README.md` updated

## STOP conditions

- The SDK's actual Python floor exceeds 3.12 or its API diverges badly from its documented
  server quickstart — report before hand-rolling anything.
- Tool handlers can't be exercised in-process without a live client — redesign the handler layer,
  don't skip the tests.
- Any tool ends up accepting raw SQL or raw file paths outside the package dir.

## Maintenance notes

- The tool surface is a public contract from here on: additive changes MINOR, breaking = MAJOR +
  migration note (governance rules apply to tools now too).
- Reviewer scrutiny: transaction boundaries on batch upserts; lockfile release on crash
  (context-manager discipline); the handoff-emit injection screen.
