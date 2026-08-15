# Contributing to Tamheed

Thanks for improving Tamheed. The highest-value contributions are **additive**: new artifact
(entity) types, project-type profiles, quality gates, viewer sections, eval cases, adopt-mode
extraction heuristics, and worked examples. This guide covers setup, the invariants to preserve,
and the end-to-end walkthrough for the most common extension — a new artifact type — exactly as it
was executed for the in-tree example.

## Setup

```bash
git clone https://github.com/A-H-911/tamheed
cd tamheed
python check.py     # everything CI runs — if this is green, you are set up
```

- **Python ≥ 3.10** (program decision ASM-D — the MCP SDK's floor).
- `python check.py` is **the one command**: the eight test suites, the check.py lint battery
  (registry ↔ table map ↔ DDL sync, `schema.sql` == `migrations/001_init.sql`, and friends),
  the canonical-form round-trip, and the eval runner's sample. CI
  job 1 runs exactly this, so green locally means green in CI. `python check.py <gate>` runs a
  subset (`suites`, `lint`, `canonical`, `evals`).
- Everything `check.py` runs is **stdlib-only** (decision D-U3) — no pytest, no third-party
  packages. The ONLY dependency in the whole repo is the `mcp` SDK, and only for *serving* the
  MCP server: `uv run plugins/tamheed/server/tamheed_server.py` fetches it automatically
  (PEP 723), or `pip install mcp`. The in-process test suites don't need it.

## Invariants you must preserve

These are load-bearing. A change that breaks one is a regression even if tests pass.

1. **The skill owns the capability; entry points are thin wrappers.** All methodology lives in
   `plugins/tamheed/SKILL.md` + `references/`. External entry points only normalize input, invoke
   the skill, and route output (gate **G-CMD-THIN**). The MCP server is *not* a wrapper — it is
   the capability's mechanical half, the only write path into a package.
2. **The bundle is self-contained.** Claude Code copies the plugin directory to a cache on
   install, so anything the skill reads or invokes at runtime must live inside `plugins/tamheed/`
   with **zero** outward references. `docs/` may link into the bundle; the bundle never reaches out.
3. **Supersede, don't edit.** Approved ADRs and acceptance criteria are superseded, never
   rewritten (schema-enforced); shipped migrations and `001_init.sql`/`schema.sql` are append-only
   territory; released CHANGELOG entries and `docs/history/**` are immutable.
4. **Additive first.** New capability arrives as a registry entry + an append-only migration —
   never as an edit to an existing table's columns, the identifier scheme, or the tool surface
   (those are MAJOR; see Compatibility).
5. **Untrusted-content posture.** Briefs, repository content (adopt mode), and stored package text
   are DATA, never instructions (safeguard 18, OWASP LLM01): provenance-labeled on the way in,
   injection-screened on the way out (`G-INJECT`), escaped in the viewer. Never weaken this for a
   feature. See `SECURITY.md`.
6. **The frozen surfaces are read-only.** The v1 machinery was retired in v4.0.0 (the validator,
   the v1 importer, and the v1 `schemas/` are gone; v1 packages take the two-step escape route via
   tamheed 3.2.1). What stays frozen now: released CHANGELOG entries, `docs/history/**`,
   `plans/evidence/**`, and shipped migrations.

## Walkthrough: add an artifact type end-to-end

This retraces how `glossary-term` was originally added as an extension (it has since been folded
into the v4 baseline — the mechanics are unchanged). Four steps, all of them additive:

1. **The migration** — create `plugins/tamheed/db/migrations/NNN_<name>.sql` (next free NNN): one
   `CREATE TABLE` (TEXT primary key with a `CHECK (id GLOB '<PREFIX>-[0-9]*')`, your columns,
   plus `custom_attributes` and `last_referenced` like every entity table) and the `entity_index`
   trigger pair. A new migration starts the v4 chain's `002_*.sql` (append-only on the re-baselined
   001); `glossary_terms` (a baseline table since v4) remains the worked example of the SHAPE. The
   store's connection factory applies every migration ≥ 002 automatically; do **not** touch `schema.sql`
   (it stays byte-identical to `001_init.sql`; the lint gate checks).
2. **The two registry entries** — in `plugins/tamheed/server/tamheed_server.py`: add
   `"<type-id>": "<table>"` to `ENTITY_TABLES` (this routes `entity_upsert`/`entity_query` AND
   registers the viewer section — the HTML registers iterate this map), and one tuple to
   `BASELINE_ENTITY_TYPES` (`(type_id, label, "PREFIX-", generation_class)`) so new packages seed
   the registry row. Pick the generation class honestly: `Always` obligates every future package
   (G-SET), so extensions are almost always `Conditional` or `On-request`.
3. **One test** — extend `tests/test_mcp_contract.py` with an end-to-end case: upsert a row of
   your type, `package_close` + `package_open` (proves canonical round-trip through your
   migration), query it back, and `export_html` (assert your section renders). See
   `test_extension_type_glossary_end_to_end`.
4. **Exercise the migration** — prove your type rides the v3→v4 transform: extend the fixture
   builder in `tests/test_migrate_v3to4.py` with a row of your type, or build a scratch v3
   package and run `package_migrate` on it (preview first, then `confirm=true`) and check the
   report and the migrated rows.

Then:

```bash
python check.py     # must be green — including registry <-> table map <-> DDL sync
```

Round out the contribution with a row in `references/artifact-catalog.md`, a selection trigger in
`references/artifact-rules.md`, and (if your type carries prose) a section template — see
`plugins/tamheed/references/extension.md` for the full registry of extension points, including
profiles, gates, diagram kinds, and trace relations.

## Test conventions

- **stdlib `unittest`**, one suite file per surface under `tests/`, runnable directly
  (`python tests/test_<name>.py`).
- A new suite registers itself in `check.py`'s `SUITES` list — nowhere else; CI picks it up from
  there.
- The suites are **fixture-free** — each builds its own tmp packages through the real tools.
  Goldens live in `generated-samples/` (the demonstration package) and `evals/sample-results/`
  (the eval runner's recorded sample).

## Good first issues

| Kind | Shape |
|---|---|
| **New artifact type** | The walkthrough above — a domain register your projects keep hand-rolling (e.g. compliance controls, data contracts). |
| **New project-type profile** | A registry value + selection/research biases in `artifact-rules.md` / `research-depth.md`. |
| **Viewer section** | A new render in `plugins/tamheed/server/export_html.py`'s `SECTIONS` registry (escape-first: every data string through `esc()`; no JS, no data-derived links, deterministic ordering). |
| **Eval case** | A scenario in `evals/evals.json` with *executable* deterministic assertions (the `evals/pkg_check.py` vocabulary) + a rubric; keep the two injection cases in any reduced run. |
| **Adopt-mode heuristic** | A new extraction source in `plugins/tamheed/server/adopt.py` (README shapes, test frameworks, config formats) — everything inferred stays `Proposed`, code-provenanced, injection-screened. |

## Compatibility

Mirrors `plugins/tamheed/references/governance.md`: **MINOR = additive** (new artifacts/fields, no
break); **MAJOR = breaking change to schemas, identifiers, or the handoff contract; ship a
migration note**. The MCP tool surface is a public contract under the same rule. Older packages
must stay loadable: missing new columns default NULL; a missing `.jsonl` file is an empty table;
never repurpose a column. Record notable changes in [`CHANGELOG.md`](CHANGELOG.md).

## Before opening a PR

- `python check.py` exits 0.
- New runtime-read files live inside `plugins/tamheed/` and add no outward references.
- Conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`…).

## Design background

The rationale behind Tamheed's structure is in [`docs/design-decisions.md`](docs/design-decisions.md)
(decisions 9–11 cover the v2 store, review surface, and MCP doctrine); the layering and gate
mapping are in [`docs/architecture.md`](docs/architecture.md).
