# Plan 055: `record.py` / `adopt.py` debt — hard import, dead v1 ledgers, registry-derived roster, file-size cap, post-flight error

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 673d1fa..HEAD -- plugins/tamheed/server/record.py plugins/tamheed/server/adopt.py tests/test_adopt_sample.py CHANGELOG.md`
> On any change, compare excerpts; mismatch = STOP.

## Status

- **Priority**: P3
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: tech-debt
- **Planned at**: commit `673d1fa`, 2026-09-12

## Why this matters

Five small, independent debts in the adopt/record layer — each a one-screen change, bundled
because they share two files and one test file:

1. `record.py` swallows an `ImportError` of the registry and continues with
   `BASELINE_ENTITY_TYPES = []`, `ENTITY_TABLES = {}` — an adopted package would be created
   with an empty type registry and every family unmapped, silently. The comment says "no
   import cycle", and there is none (`tamheed_server` imports `record`/`adopt` lazily inside
   handlers), so the fallback protects nothing.
2. `record.Plan` carries v1-migration ledgers nothing reads or writes any more
   (`manifest_counts`, `status_coerced`, `status_map`, `title_fallbacks`, `status_defaulted`,
   `dw_crosswalk`, `partial_files`, `skipped_files`) plus three module constants
   (`_PIPE_SENTINEL`, `_TITLE_ALIASES`, `_LONGFORM_ALIASES`) with zero references. The
   `count_deltas` block in `fidelity()` iterates `plan.manifest_counts`, which no code
   populates — it can never fire.
3. `adopt.ALWAYS_TYPES` / `_TYPE_TABLE` hand-copy the registry's Always class. Every other
   copy of that roster is lint-guarded (`check.py` lints 2–3); this one isn't, and adopt
   already imports from `tamheed_server`. Derive it; delete the copy.
4. `adopt._walk` yields every regular file with no size bound; a 2 GB log in a scanned tree
   is read into memory by the extractors. (The earlier "follows symlinks" claim was wrong:
   `Path.rglob("*")` does not descend symlinked directories; a symlinked *file* still hits
   the size cap.)
5. `run_adoption`'s post-flight returns `{"ok": False, ...}` with no `error` key when gates
   fail — every other `ok: False` dict in the server carries `error`, and `package_adopt`'s
   callers read it.

## Current state

Line numbers at `673d1fa`; compare excerpts, not numbers.

- `plugins/tamheed/server/record.py`
  - :22–26:

    ```python
    try:  # no import cycle: tamheed_server imports this lazily inside handlers
        from tamheed_server import BASELINE_ENTITY_TYPES, ENTITY_TABLES  # noqa: E402
    except ImportError:  # pragma: no cover
        BASELINE_ENTITY_TYPES = []
        ENTITY_TABLES = {}
    ```

  - :53–63: `_PIPE_SENTINEL = "\x00"`, `_TITLE_ALIASES = frozenset({...})`,
    `_LONGFORM_ALIASES = frozenset({...})` — `grep -rn "_PIPE_SENTINEL\|_TITLE_ALIASES\|_LONGFORM_ALIASES" plugins tests evals check.py`
    → only their definitions.
  - `class Plan.__init__` :68–90 — fields. Live ones (referenced elsewhere): `rows`, `edges`,
    `audits`, `omissions`, `unmapped`, `defined`, `package`, `prompt_files`. Dead ones (only
    the `__init__` line): `manifest_counts`, `partial_files`, `skipped_files`,
    `status_coerced`, `title_fallbacks`, `status_map`, `status_defaulted`, `dw_crosswalk`.
    **Verify each with `grep -rn "\.<field>" plugins tests evals` before deleting** — delete
    only fields whose sole hit is the `__init__` assignment.
  - `fidelity()` :196–295: the block from `prefix_tables = {...}` through
    `deltas[prefix] = {...}` (:200–216) exists only to compute `count_deltas` from
    `plan.manifest_counts`; the return dict (:283) carries `"count_deltas": deltas`.
    `grep -rn count_deltas plugins tests evals docs` → only record.py.
- `plugins/tamheed/server/adopt.py`
  - :21–22 imports: `import record` and `from tamheed_server import _INJECT_RE`.
  - `_walk` :33–36:

    ```python
    def _walk(root: Path):
        for p in sorted(root.rglob("*")):
            if p.is_file() and not (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS):
                yield p
    ```

  - `scan()` :47–63 returns `{"readmes", "configs", "test_files", "code_files", "modules",
    "git_history", "_code_list"}`; `run_adoption` builds `scan_report` from it minus
    `_code_list` and puts it in the preview under `"scan"`.
  - :240–248:

    ```python
    ALWAYS_TYPES = ("requirement", "constraint", "assumption", "open-question", "decision",
                    "risk", "phase", "acceptance-criterion", "narrative-document",
                    "document-section")
    _TYPE_TABLE = {"requirement": "requirements", ... "document-section": "document_sections"}
    ```

    used at :279–280 (`for etype in ALWAYS_TYPES: if not plan.rows.get(_TYPE_TABLE[etype])`).
  - `run_adoption` post-flight :296–300:

    ```python
        fid = record.fidelity(plan, Path(dest_root) / name)
        return {"ok": fid["ok"], "stage": "post-flight", "preview": preview,
                "package_dir": pop["package_dir"], "gap_report": gaps,
                "gate_failures": fid["gate_failures"], "unmapped": fid["unmapped"],
                "next": record._CUTOVER_NEXT if fid["ok"] else None}
    ```

- `plugins/tamheed/server/tamheed_server.py`: `BASELINE_ENTITY_TYPES` is a list of 4-tuples
  `(type_id, label, id_prefix, generation_class)`, e.g.
  `("requirement", "Requirement (FR-/NFR-)", "FR-", "Always")`; `ENTITY_TABLES` maps
  `type_id -> table`. `check.py` lint 3 asserts the registry's Always class equals the
  artifact catalog's — that is the one source of truth this plan derives from.
- Tests: `tests/test_adopt_sample.py` — `AdoptSampleTest` writes a small synthetic repo
  (`SAMPLE` dict) to a temp dir and calls `adopt.run_adoption(...)`; `AdoptFidelityTest`
  likewise. Copy their setup.

### Release discipline

- No `plugin.json` bump; CHANGELOG bullets under `## [Unreleased]` → existing `### Changed`
  (these are internal changes) — one bullet for the whole plan.
- No edits to version-stamped files, prompts, templates, or goldens.
- `check.py` lint 3 already guards the registry ↔ catalog; nothing new to lint once the copy
  is gone.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Adopt suite | `python tests/test_adopt_sample.py` | `OK` |
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |

## Scope

**In scope**: `plugins/tamheed/server/record.py`, `plugins/tamheed/server/adopt.py`,
`tests/test_adopt_sample.py`, `CHANGELOG.md`, `plans/README.md` (row).

**Out of scope**: `record.populate()` / `_sections()` / `_kebab()` bodies; `SKIP_DIRS`,
`CODE_EXT`, the extractors; `references/adopt.md` (plan 048 already fixed its drift);
`tamheed_server.package_adopt`.

## Git workflow

- One commit: `refactor: record/adopt debt — hard import, dead v1 ledgers, registry-derived roster, size cap, post-flight error (plan 055)`. Do NOT push.

## Steps

### Step 1: Hard import in `record.py`

Replace the try/except with a plain `from tamheed_server import BASELINE_ENTITY_TYPES, ENTITY_TABLES  # noqa: E402`.

**Verify**: `python tests/test_adopt_sample.py` → `OK`; `python -c "import sys; sys.path.insert(0,'plugins/tamheed/server'); import record, adopt; print(len(record.BASELINE_ENTITY_TYPES))"` → a number > 20.

### Step 2: Delete the dead ledgers

Delete `_PIPE_SENTINEL`, `_TITLE_ALIASES`, `_LONGFORM_ALIASES`; delete the dead `Plan`
fields confirmed by the grep rule in "Current state" (and their comment lines); delete the
`prefix_tables`/`deltas` block in `fidelity()` and the `"count_deltas": deltas` entry from
its return dict.

**Verify**: `python tests/test_adopt_sample.py` and `python tests/test_mcp_contract.py` → `OK`;
`grep -rn "count_deltas\|_PIPE_SENTINEL\|manifest_counts" plugins tests evals` → nothing.

### Step 3: Derive the Always roster in `adopt.py`

Change the import to `from tamheed_server import _INJECT_RE, BASELINE_ENTITY_TYPES, ENTITY_TABLES`
and replace the two literals with:

```python
# Plan 055: the Always class comes from the registry (lint-guarded against the catalog),
# never a hand copy. Order = registry order.
ALWAYS_TYPES = tuple(t for t, _label, _prefix, cls in BASELINE_ENTITY_TYPES if cls == "Always")
_TYPE_TABLE = {t: ENTITY_TABLES[t] for t in ALWAYS_TYPES}
```

**Verify**: `python -c "import sys; sys.path.insert(0,'plugins/tamheed/server'); import adopt; print(adopt.ALWAYS_TYPES)"`
→ the same ten names as the old literal (any order difference is fine; a *set* difference is a
STOP — it would mean the hand copy had drifted from the registry, which is a finding to report).

### Step 4: Size cap in `_walk`

```python
MAX_FILE_BYTES = 2_000_000  # plan 055: adopt reads files whole; a stray archive/log must not


def _walk(root: Path, skipped: list[str] | None = None):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS):
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            if skipped is not None:
                skipped.append(str(p.relative_to(root)).replace("\\", "/"))
            continue
        yield p
```

In `scan()`, create `skipped_large: list[str] = []`, pass it to `_walk(source, skipped_large)`,
and add `"skipped_large": skipped_large` to the returned dict (it flows into the preview's
`scan` report automatically). Check every other `_walk(` caller (`grep -n '_walk(' adopt.py`)
still works with the new optional parameter.

**Verify**: `python tests/test_adopt_sample.py` → `OK`.

### Step 5: Post-flight `error` key

```python
    ok = fid["ok"]
    return {"ok": ok, "stage": "post-flight", "preview": preview,
            "package_dir": pop["package_dir"], "gap_report": gaps,
            "gate_failures": fid["gate_failures"], "unmapped": fid["unmapped"],
            "error": None if ok else ("post-flight: gate failures "
                                       + ", ".join(sorted(fid["gate_failures"]))
                                       + (f"; unmapped ids: {len(fid['unmapped'])}"
                                          if fid["unmapped"] else "")),
            "next": record._CUTOVER_NEXT if ok else None}
```

### Step 6: Tests (`tests/test_adopt_sample.py`)

- `test_always_roster_is_the_registry`: `adopt.ALWAYS_TYPES` equals
  `tuple(t for t,_,_,c in srv.BASELINE_ENTITY_TYPES if c == "Always")` and every entry maps
  through `srv.ENTITY_TABLES`.
- `test_large_files_are_skipped_and_reported`: write a 2.5 MB `big.log` into the sample repo,
  run the preview, assert `out["scan"]["skipped_large"] == ["big.log"]` and the file is not
  counted in `code_files`.
- `test_post_flight_failure_carries_error`: `unittest.mock.patch.object(adopt.record, "fidelity",
  return_value={"ok": False, "gate_failures": {"G-SET": ["x"]}, "unmapped": []})` around a
  `confirm=True` run → `out["ok"] is False` and `"G-SET" in out["error"]`.

**Verify**: `python tests/test_adopt_sample.py` → `OK` (+3); `python check.py` →
`ALL CHECKS PASSED`.

### Step 7: CHANGELOG

Under `## [Unreleased]` → `### Changed`:

```markdown
- Adopt/record hygiene: the registry import is no longer wrapped in a silent fallback,
  the v1 migration ledgers nothing populated are gone, adopt derives its Always roster from
  the registry instead of a hand copy, files over 2 MB are skipped and listed under
  `scan.skipped_large`, and a failed post-flight now carries an `error` (advisor plan 055).
```

## Done criteria

- [ ] `grep -c 'except ImportError' plugins/tamheed/server/record.py` → `0`
- [ ] `grep -rn 'count_deltas\|_PIPE_SENTINEL\|manifest_counts' plugins tests evals` → nothing
- [ ] `grep -n 'ALWAYS_TYPES = tuple' plugins/tamheed/server/adopt.py` → one hit; no literal ten-name tuple remains
- [ ] `grep -c 'MAX_FILE_BYTES' plugins/tamheed/server/adopt.py` → `2`
- [ ] `python tests/test_adopt_sample.py` → `OK` (+3); `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files; `plans/README.md` row updated

## STOP conditions

- Any of the "dead" fields/constants has a reference outside its definition — keep it and
  report which.
- The derived `ALWAYS_TYPES` differs as a *set* from the old literal.
- Importing `record` or `adopt` standalone raises `ImportError` after Step 1 (a real cycle).
- Any golden changes.

## Maintenance notes

- New Always families now reach adopt automatically via the registry; a reviewer adding a
  family should still run the adopt suite (the omission wording is per-family).
- `MAX_FILE_BYTES` is a ceiling, not a tuning knob; raise only if a real repository's
  README/config exceeds it.
