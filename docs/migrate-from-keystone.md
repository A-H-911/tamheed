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
   omissions, manifest-count deltas, unmapped-content list, and the honesty ledgers —
   `status_coerced` (every v1 status word that maps outside the lifecycle vocabulary, with
   the proposed mapping), `title_fallbacks`, per-file `partial_files` row counts, and the
   frozen validator's sha256 (which contract judged this). Show it to the operator verbatim.
3. **Operator confirms** — an explicit "yes, migrate" in the conversation. STOP until you have
   it. **Present the `status_coerced` proposals as a multi-select confirmation** (per status
   word: keep the proposal or pick another lifecycle value) and carry the answers as
   `status_map={...}`.
4. **Populate** — `package_migrate(source_dir, confirm=true, status_map={...})`: one
   transaction; a failure leaves no partial package. On success the package directory gains
   `prompts/` (the five-scenario library) alongside `data/`.
5. **Post-flight** — the call returns the fidelity report: identifier gaps (must be empty),
   count deltas (stale-manifest divergences are *reported*, e.g. a manifest declaring fewer ADRs
   than disk holds — disk wins), and `gate_run` results.
6. **Operator reviews** — through the HTML view once available (plan 012); until then, present
   the fidelity report as text.

## 4. Verify

- `gate_run` on the migrated package: every critical gate passes. A `G-TRACE` **warning**
  ("0 MVP requirements — passed vacuously") means the MVP flags did not survive — do not
  treat that green as traceability.
- Fidelity report: `identifier_gaps` empty; every count delta explained to the operator. The
  preview's `zero_families` must be empty (or each family deliberately acknowledged via
  `allow_zero`); review `partial_files` (register rows migrated, surrounding prose not) and
  `skipped_files` — that is the complete loss ledger (plan 017, field-evidence C13).
- The v1 source directory is untouched (migration is read-only on it).
- Gaps found after review are repaired by re-running with `patch=<file>` (merge-by-id
  overrides applied before populate) — never by editing approved rows afterwards.

## 5. Cutover — re-point the project (field-evidence C15)

**This step is what makes the migration real.** Until it is done, two sources of truth
coexist: agents keep reading the stale v1 instructions, editing dead registers, and running
the v1 validator — silently undoing the migration.

1. Open the migrated package and run `handoff_emit(<repo>)`: it appends the "Tamheed progress
   tracking" operating note (with the MCP tool cheat-sheet) to the repo's `CLAUDE.md`, emits
   the `<package>/prompts/` scenario library, and returns `stale_references` — every v1-flow
   pointer found in `CLAUDE.md`/`AGENTS.md` as `file:line` + a suggested replacement. Apply
   those replacements; product-domain uses of the word "Keystone" are never flagged. On
   plugin-hosted servers no project `.mcp.json` entry is written (the installed plugin
   already registers the server); standalone installs get the absolute-path entry.
2. Update the project's `CLAUDE.md` / `AGENTS.md` by hand: references to Keystone artifacts
   (`validation/traceability-matrix.md`, `keystone-state.json`, register files) become
   references to the Tamheed package — the MCP tools (`entity_query`, `trace_query`,
   `gate_run`, `progress_update`, `audit_record`, `work_bind`) and the HTML view. The
   executing agent records progress through the tools from now on.
3. Mark the v1 package directory as a frozen archive (a top-line note in its README is
   enough) so no future session mistakes it for the live record.
3b. **Reference, don't restate** (plan 019): when authoring `AGENTS.md`/`CLAUDE.md`, cite the
   package (`entity_query`, `gate_run`, `review.html`, the prompt library) instead of copying
   register content — copies drift silently. If you deliberately quote a load-bearing subset
   (e.g. invariants), label it as a snapshot and keep the reference beside it. Re-running
   `handoff_emit` audits this: `restated_content` findings, the self-retracting stale-warning
   block, and `unchanged` statuses make it the standing "is the cutover done?" check.
4. **Slices need manual backfill**: v1 had no governed slice concept, so the roadmap ladder
   migrates as phases + preserved prose only. Author `slice` rows (and bind ACs to them)
   through the normal v2 flow when execution resumes.

## 6. Optional cleanup (operator approved)

- Keep the v1 package directory as an archival snapshot (recommended), or remove it once the
  operator confirms the v2 package is the source of truth.
- Optionally `/plugin uninstall keystone`.
