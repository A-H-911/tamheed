# Migration runbook — the operator procedure (bundled)

The operational half of `migration-v1.md` (which stays the mapping contract). Shipped in the
bundle (C26/B6): the plugin must be self-contained — findings_5 had to reverse-engineer the
swap mechanics because this file only existed in the program repo
(`docs/migrate-from-keystone.md` there mirrors this one).

## 1–2. Detect, consent, install

Detection: `manifest.json`/`keystone-state.json` beside Markdown registers, or the keystone
plugin installed. **Migration is operator-initiated (D-REPO-5)**: inform, then STOP until
instructed; mention it at most once per session.

## 3. The staged run

1. `package_migrate(source_dir)` — pre-flight (frozen validator, in-process; its sha256 is in
   the result) + the dry preview. Nonconformant-lineage → route to `package_adopt`.
2. Present the preview verbatim: counts, `count_deltas` (reported, never reconciled),
   `zero_families` (blocks populate unless `allow_zero`), grouped `status_coerced` (confirm
   as a multi-select → `status_map`), `status_defaulted`, `title_fallbacks` (a data-loss
   ledger measuring source SHAPE — post-2.4.0 the loss itself is zero), per-file
   `partial_files`, `dw_crosswalk`.
3. Operator confirms → `package_migrate(source_dir, confirm=true, status_map={...})`.
4. Post-flight: identifier gaps must be empty; review the **fidelity ledgers**
   (`truncations` — title/name caps only, never statements; `column_starvation`;
   `field_mapping`; `execution_state_note`). The package is left OPEN.

## 4–5. Verify and cut over

`gate_run` (watch for a vacuous-G-TRACE warning) → `handoff_emit(<repo>)`: managed emissions
(`written`/`unchanged`/`diverged` — hand-edited files are refused without `force=true`), the
operating note + tool cheat-sheet, the self-retracting stale-warning block, the
`stale_references` scan (agent-control files + emitted prompt bodies — including refused
`diverged` PRM rows, marked "not emitted"), and `restated_content` (unlabeled restatement vs
labeled snapshots). Re-running emit is the standing "is the cutover done?" check.
Reference, don't restate; freeze the v1 tree; slices need manual backfill (bind ACs while
`Proposed`, then approve).

## 6. Cleanup (operator approved)

Keep the v1 tree as a frozen archive (recommended) or remove it once the operator confirms.

## 7. Re-populating after a parser upgrade (the no-revert repair path)

1. Update the plugin (`server_info` reports the new version).
2. `package_migrate(<v1 source>, name="<package>-v2new", confirm=true, status_map=<your
   previous map — replay the FULL map; semantic defaults can shift between releases>)`.
3. The old-vs-new canonical JSONL diff IS the repair — review it row-scoped.
4. Carry over post-migration v2 rows (progress, verdicts, scope changes) via the tools.
5. **Swap mechanics** (there is no rename tool; these compose deliberately):
   `populate` refuses an existing `data/` dir; `package_open` keys on the DIRECTORY name;
   `packages.name` is cosmetic after the swap. So: `package_close` → filesystem-rename the
   directories → `package_open(<original name>)`.
6. **After the swap, force-re-emit the prompt library** (`handoff_emit(..., force=true)` once):
   the library files embed the package name, so a directory rename makes them report
   `diverged` — this one divergence is expected and self-inflicted (C26/B5).
7. Re-run `handoff_emit` clean, refresh stale PRM rows (supersede + re-author), then
   `export_html` and commit `review.html` + `csv/`.
