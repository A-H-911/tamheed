# Migrating from Keystone v1 to Tamheed — agent runbook

An executable checklist written **for an AI agent** operating inside a project that used old
Keystone. Follow it top to bottom; stop at every operator gate.

## Consent rule — read this first (D-REPO-5)

**Migration is operator-initiated.** If you detect a Keystone package, **inform the operator and
STOP.** Never begin `package_migrate` without the operator's explicit instruction in this
conversation. Keystone v1 keeps working; staying on it is a valid choice — respect it. Do not
nag: mention migration once per session at most.

## 1. Detection

The project used Keystone v1 if either holds:

- a package directory contains `manifest.json` **and/or** `keystone-state.json` alongside
  Markdown registers (`requirements/`, `decisions/`, `validation/` …), or
- the `keystone` plugin is installed in this Claude Code environment.

Tell the operator what you found and where. Then **stop and wait** (consent rule above).

## 2. Install Tamheed (operator approved)

```
/plugin marketplace add A-H-911/tamheed
/plugin install tamheed@tamheed
```

Approve the `tamheed` MCP server when prompted (it launches via `uv run`; Python ≥3.10 —
`pip install mcp` is the fallback, see `plugins/tamheed/server/README.md`).

## 3. Run the staged migration

`package_migrate` is staged and resumable; each stage reports before the next. Mapping contract:
`plugins/tamheed/references/migration-v1.md`.

1. **Pre-flight** — `package_migrate(source_dir)` runs the frozen v1 validator first.
   - Validator fails → STOP; show the operator the report. Fix under v1, or —
   - "no manifest.json / not a conformant v1 package" → this is a Keystone-*lineage* project;
     route to `package_adopt` (plan 011) instead. Do not force a migration.
2. **Preview** — the same call returns the dry report: per-family counts, trace-edge count,
   omissions, manifest-count deltas, unmapped-content list. Show it to the operator verbatim.
3. **Operator confirms** — an explicit "yes, migrate" in the conversation. STOP until you have it.
4. **Populate** — `package_migrate(source_dir, confirm=true)`: one transaction; a failure leaves
   no partial package.
5. **Post-flight** — the call returns the fidelity report: identifier gaps (must be empty),
   count deltas (stale-manifest divergences are *reported*, e.g. a manifest declaring fewer ADRs
   than disk holds — disk wins), and `gate_run` results.
6. **Operator reviews** — through the HTML view once available (plan 012); until then, present
   the fidelity report as text.

## 4. Verify

- `gate_run` on the migrated package: every critical gate passes.
- Fidelity report: `identifier_gaps` empty; every count delta explained to the operator.
- The v1 source directory is untouched (migration is read-only on it).

## 5. Re-point the project

Update the project's `CLAUDE.md` / `AGENTS.md`: references to Keystone artifacts
(`validation/traceability-matrix.md`, `keystone-state.json`, register files) become references to
the Tamheed package — the MCP tools (`entity_query`, `trace_query`, `gate_run`,
`progress_update`, `audit_record`, `work_bind`) and the HTML view. The executing agent records
progress through the tools from now on.

## 6. Optional cleanup (operator approved)

- Keep the v1 package directory as an archival snapshot (recommended), or remove it once the
  operator confirms the v2 package is the source of truth.
- Optionally `/plugin uninstall keystone`.
