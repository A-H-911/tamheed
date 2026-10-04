# Plan 206: the tool figures (an effects canvas and a call-sequence strip per tool)

> Maintainer-executed, 2026-10-04. Batch record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md).
> Rulings G7, G13, G17, G3. Ledger first. One commit.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (nineteen hand-authored effect sets, each claim
  with a server line; the strips derive from the recipe table) - **DONE 2026-10-04**

## What this beat changes

- **An effects canvas per tool** (`fx-<tool>`, a file figure in the tool's card): the tool in the
  centre; on the left what it needs (an open package or a closed one, the operator's word, the
  lock); on the right what it reads and what it writes (tables, files, the journal event it
  records). Hand-authored in `TOOL_EFFECTS`, every claim with the server line that makes it true,
  cross-checked against a census of the tool's own body (tables, files, event types named).
- **A call-sequence strip per tool** (`seq-<tool>`): the recipes that call it, one row each, the
  recipe's steps as small pills, a step whose label names the tool accented. Derived from `RECIPES` and the
  swimlane labels, so a new recipe appears without a new figure. A tool no recipe names gets one
  sentence.
- Captures: `entity_upsert`'s two figures EN light and dark and AR light, 390 px; `handoff_emit`'s two.

## Pin ledger

- Before: `plans/evidence/scripts-ste/pins-206.md` (23 pinned phrases in the guide files). After:
  `pins_missing.py`: 0 missing.
- Invariants: `plans/evidence/scripts-ste/invariants-206.md` (4 files, 2 with new tokens: the 91
  line numbers of the citations in `diagrams.py`, and `SERVER_SRC`, `TOOL_EFFECTS`, `SKILL`, `206` in
  the test; no modal drop).

## What landed, beyond the plan

- **The effects table, printed from `TOOL_EFFECTS`** (an item starting with `@` is a resolved
  phrase; the number is the line of `plugins/tamheed/server/tamheed_server.py` that makes the claim
  true, in the tool or in the helper it calls, and the test reads that line, the six around it or
  the helper for the item's own token; the def line only for a parameter of the signature or for
  "nothing"; what the store module does on the tool's behalf, the lock and the canonical files, is a
  phrase). The first table cited def lines for reads of three tables, a round number for the
  skill-name check and the nested `emit` def for `.mcp.json`; the advisor caught them and every line
  was re-located in the file, and `audit_record` lost a read it never makes (it maps methods to
  evidence skills, no table):

| tool | needs | reads | writes |
|---|---|---|---|
| `server_info` | `@need.none` L5431 | `plugin.json` L5405, `packages` L5433, `@resume` L5449 | `@nothing` L5412 |
| `package_create` | `@need.closed` L954, `@need.lockfree` L963 | `@nothing` L951 | `entity_types` L967, `packages` L972, `README.md` L984, `@lock_taken` L962 |
| `package_open` | `@need.closed` L1287, `@need.v4` L1294, `@need.lockfree` L1306 | `@canonical` L1305, `@resume` L1311 | `@lock_taken` L1305 |
| `package_close` | `@need.open` L1317 | `@nothing` L1314 | `@canonical` L1322, `@lock_released` L1323 |
| `package_unlock` | `@need.name` L5101, `@need.word` L5142 | `@lock_file` L5138 | `@lock_removed` L5175, `progress_entries` L5192, `forced-override` L5195 |
| `entity_upsert` | `@need.open` L1623 | `@readiness` L1738, `@skill_names` L1858 | `@any_table` L2032, `trace_edges` L1684, `progress_entries` L1693, `lessons` L2127, `@canonical` L2278 |
| `entity_query` | `@need.open` L2319 | `@any_table` L2384 | `@nothing` L2287 |
| `trace_query` | `@need.open` L2456 | `trace_edges` L2465 | `@nothing` L2454 |
| `gate_run` | `@need.open` L2480 | `@all_tables` L2499 | `@nothing` L2475 |
| `readiness_check` | `@need.open` L3269 | `@all_tables` L3284 | `@nothing` L3263 |
| `progress_update` | `@need.open` L3317 | `@nothing` L3295 | `progress_entries` L3334, `@canonical` L3347 |
| `audit_record` | `@need.open` L3388 | `@nothing` L3374 | `audit_verdicts` L3402, `@canonical` L3414 |
| `work_bind` | `@need.open` L3426 | `entity_index` L3436 | `@bound_rows` L3446, `progress_entries` L3453, `@canonical` L3461 |
| `handoff_emit` | `@need.open` L4081, `@need.kickoff` L4098 | `prompts` L4098, `lessons` L3983, `skills` L3989, `feedback` L4237 | `README.md` L4090, `<target>/CLAUDE.md` L4497, `<target>/.mcp.json` L4166, `<package>/CLAUDE.md` L4456 |
| `package_migrate` | `@need.name` L4730, `@need.lockfree` L4770, `@need.word` L4730 | `@canonical` L4810 | `data-v3-backup/` L4806, `data/*.jsonl` L5025, `progress_entries` L4954, `README.md` L5088 |
| `package_adopt` | `@need.source` L5218, `@need.word` L5223 | `@source_repo` L5223 | `@new_package` L5232, `README.md` L5227 |
| `export_html` | `@need.open` L5276 | `@all_tables` L5279, `@readiness` L5282 | `review.html` L5319, `csv/*.csv` L5348 |
| `package_verify` | `@need.name` L1331 | `data/*.jsonl` L1384, `review.html` L1395 | `progress_entries` L1446, `integrity-verified` L1446 |
| `entity_export` | `@need.open` L1510, `@need.path` L1481 | `@tool_result` L1539 | `@export_file` L1561 |

- **Every cited line, as the file reads today** (the test holds each identifier item to its line or
  the helper that line calls):

- L951: `def package_create(name: str, title: str, profile: str, mode: str = "full") -> dict:`
- L954: `if _CURRENT is not None:`
- L962: `s = store.PackageStore(pkg_dir).__enter__()`
- L963: `except store.StoreLockedError as exc:`
- L967: `"INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"`
- L972: `"INSERT INTO packages (name, title, profile, mode, package_version, created_at)"`
- L984: `library = _emit_prompt_library(pkg_dir, name)`
- L1287: `return _err(f"package '{_CURRENT_NAME}' is already open — package_close it first")`
- L1294: `stored = _stored_package_version(pkg_dir)`
- L1305: `s = store.PackageStore(pkg_dir).__enter__()`
- L1306: `except store.StoreLockedError as exc:`
- L1311: `"resume": _resume_block(s.conn, name, pkg_dir / "data")}`
- L1314: `def package_close() -> dict:`
- L1317: `if _CURRENT is None:`
- L1322: `err = _commit()`
- L1323: `_CURRENT.__exit__(None, None, None)`
- L1331: `def package_verify(name: str | None = None, record: bool = False,`
- L1384: `digest = _canonical_digest(on_disk)`
- L1395: `review_current = review_exported_by = None`
- L1446: `"INSERT INTO progress_entries (id, event_type, entry, actor, occurred_at)"`
- L1481: `def entity_export(path: str, tool: str = "entity_query", args: dict | None = None) -> dict:`
- L1510: `if guard := _need_open():`
- L1539: `result = TOOLS[tool][0](**args)`
- L1561: `target.write_text(text, encoding="utf-8", newline="\n")`
- L1623: `if guard := _need_open():`
- L1684: `"DELETE FROM trace_edges WHERE from_id = ? AND to_id = ?"`
- L1693: `"INSERT INTO progress_entries (id, event_type, entry,"`
- L1738: `rep = _readiness_report(conn, etype, cols["id"])`
- L1858: `legal = _plugin_skill_names()`
- L2032: `sql = (f"INSERT INTO {table} ({', '.join(names)})"`
- L2127: `conn.execute("UPDATE lessons SET lifecycle_status ="`
- L2278: `if err := _commit():`
- L2287: `def entity_query(type: str, id: str | None = None, status: str | None = None,`
- L2319: `if guard := _need_open():`
- L2384: `sql = (f"SELECT {', '.join(cols)} FROM {table}{where_sql} ORDER BY {order}"`
- L2454: `def trace_query(entity_id: str, direction: str = "both", relation: str | None = None) -> dict:`
- L2456: `if guard := _need_open():`
- L2465: `sql = f"SELECT from_id, to_id, relation FROM trace_edges WHERE ({' OR '.join(clauses)})"`
- L2475: `def gate_run() -> dict:`
- L2480: `if guard := _need_open():`
- L2499: `checked_ids += conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]`
- L3263: `def readiness_check(scope: str = "package", id: str | None = None) -> dict:`
- L3269: `if guard := _need_open():`
- L3284: `report = _readiness_report(conn, scope, scope_id)`
- L3295: `def progress_update(entries: list[dict]) -> dict:`
- L3317: `if guard := _need_open():`
- L3334: `"INSERT INTO progress_entries (id, event_type, entry, subject_id,"`
- L3347: `if err := _commit():`
- L3374: `def audit_record(verdicts: list[dict]) -> dict:`
- L3388: `if guard := _need_open():`
- L3402: `"INSERT INTO audit_verdicts (id, ac_id, verdict, evidence,"`
- L3414: `if err := _commit():`
- L3426: `if guard := _need_open():`
- L3436: `row = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?",`
- L3446: `conn.execute(f"UPDATE {table} SET last_referenced = ? WHERE id = ?",`
- L3453: `"INSERT INTO progress_entries (id, entry, actor, occurred_at, custom_attributes)"`
- L3461: `if err := _commit():`
- L3983: `"SELECT COUNT(*) FROM lessons WHERE lifecycle_status = 'Approved'").fetchone()`
- L3989: `"SELECT name, level FROM skills WHERE lifecycle_status = 'Approved'"`
- L4081: `if guard := _need_open():`
- L4090: `library = _emit_prompt_library(pkg_dir, _CURRENT_NAME, force=force,`
- L4098: `kickoff = (conn.execute("SELECT id, kind, lifecycle_status FROM prompts WHERE id = ?",`
- L4166: `emit(mcp_cfg_path, json.dumps(cfg, indent=2) + "\n", ".mcp.json")`
- L4237: `"SELECT id FROM feedback WHERE lifecycle_status = 'Proposed' ORDER BY id")]`
- L4456: `pkg_md = PACKAGE_ROOT / _CURRENT_NAME / "CLAUDE.md"`
- L4497: `claude_md.write_text(content, encoding="utf-8", newline="\n")`
- L4730: `def package_migrate(name: str, confirm: bool = False) -> dict:`
- L4770: `return _err(f"package '{name}' is locked ({store._describe_lock(lock)})"`
- L4806: `backup.mkdir()`
- L4810: `shutil.copy2(f, backup / f.name)`
- L4954: `pe_rows = tables.setdefault("progress_entries", [])`
- L5025: `os.replace(dst, data / dst.name[:-4])`
- L5088: `out["prompt_library"] = _emit_prompt_library(pkg_dir, name)`
- L5101: `def package_unlock(name: str, confirm: bool = False) -> dict:`
- L5138: `seen = _observe_lock(lock)`
- L5142: `"would_unlock": seen["outcome"] in _UNLOCKABLE}`
- L5175: `lock.unlink()`
- L5192: `"INSERT INTO progress_entries (id, event_type, entry, actor, occurred_at)"`
- L5195: `(pe_id, f"FORCED lock removal: data/.lock held by pid"`
- L5218: `def package_adopt(source_dir: str, name: str | None = None, confirm: bool = False) -> dict:`
- L5223: `out = adopt.run_adoption(source_dir, PACKAGE_ROOT, name=name, confirm=confirm)`
- L5227: `out["prompt_library"] = _emit_prompt_library(pkg, pkg.name)`
- L5232: `with store.PackageStore(pkg) as s:`
- L5276: `if guard := _need_open():`
- L5279: `report = gate_run()`
- L5282: `readiness = {"report": _readiness_report(_CURRENT.conn, "package", None),`
- L5319: `path.write_text(text, encoding="utf-8", newline="\n")`
- L5348: `status = _managed_emit(csv_dir / f"{table}.csv", buf.getvalue(), force=True)`
- L5405: `manifest = _SERVER_DIR.parent / ".claude-plugin" / "plugin.json"`
- L5412: `def server_info(detail: bool = False) -> dict:`
- L5431: `if _CURRENT is not None:`
- L5433: `f"SELECT {', '.join(_PACKAGE_ROW)}, custom_attributes FROM packages LIMIT 1").fetchone()`
- L5449: `out["resume"] = _resume_block(_CURRENT.conn, _CURRENT_NAME,`

- **The census as the cross-check, not the source.** A scan of each tool's body (one helper level)
  for table names, file names and event types was printed and read against the file; it over-reports
  wherever a tool iterates `ENTITY_TABLES` or runs the readiness report, so the map above is
  authored and the census only had to contain it.
- **The strip's accent is derived at render time.** `RECIPES` lists a recipe's tools, not one per
  step, so the strip cannot know the tool's step from the model; the renderer now resolves a node's
  label before drawing its box and accents a node whose text names the token (`accent_if`). The
  swimlane labels carry the tool names in both languages where a step is the call itself; where a
  recipe calls the tool inside a step that names something else (every `entity_upsert` step), no
  pill is marked, and the caption claims only that. The first caption claimed the mark for every
  row; the `entity_upsert` capture showed none.
- **4 tools no recipe names as a step** (`entity_export`, `entity_query`, `package_create`, `trace_query`) get the
  sentence that the skills call them as they work.
- **One helper for the arrows:** the reads column fans into the tool and the writes column fans out
  of it through `_hub` (205), with a 70 px gap; a "nothing" pill draws no arrow.
- **The folder, measured:** 528 files (132 figure ids: 12 swimlanes, 28 relations, 37 data paths,
  20 trace paths, 1 lifecycle, 19 effects canvases, 15 strips); the page 1,222,012 bytes, 1,506
  content ids.
- **Captures** under `plans/evidence/captures-206/`: `fx-entity_upsert` EN light, EN dark, AR light,
  390 px; `seq-entity_upsert` EN light; `fx-handoff_emit` and `seq-handoff_emit` EN light. The two
  strip captures were retaken after the caption changed (a figure capture includes its caption), and
  the `entity_upsert` canvas captures after its read item changed; `fx-package_open` EN light shows
  the store's claims as phrases (the lock taken, the canonical files).

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- **G22, the effects canvas:** the tool in the centre, reads fanning in from the left, writes fanning
  out to the right, needs beneath; a "nothing" pill draws no arrow; what the store module does on
  the tool's behalf (the lock, the canonical files) is a phrase pinned to the line that calls the
  store, never a file name no server line names.
- **G23, the strip's mark:** a step is marked only where its label names the tool, derived at render
  time; the caption claims only that; no hand map of step indexes.

## Validation

- `python docs/guide/build.py`: 1,506 ids, 0 missing, 0 orphans, the geometry lint and the label-width
  rule green on both copies of the 132 file models; 528 figure files. `test_user_guide` OK (14 tests,
  the effects test new: every tool has a set, every line is a line of the server, every table item
  is a store table).
- `python check.py`: ALL CHECKS PASSED.
