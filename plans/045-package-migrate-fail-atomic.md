# Plan 045: Make `package_migrate(confirm=true)` leave the package untouched on any failure — tests first

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_migrate_v3to4.py CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED (the write-back path of the only migration tool; mitigated by writing the
  characterization tests *before* touching the code)
- **Depends on**: none (execute after 044 if both are scheduled — 044 adds a guard at the top
  of the same function; merge order avoids a conflict)
- **Category**: bug
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

`package_migrate`'s docstring promises *"the result is validated + canonicalized through a
full store round-trip BEFORE it replaces the live files — a package that fails v4 integrity is
left untouched."* Three things break that promise, and there is **no test for any failure
path** of the confirm branch:

1. **The write-back deletes before it writes, on every path.** After validation, the code
   unlinks *every* `data/*.jsonl` and only then copies the new files in. A failure mid-loop
   (disk full, antivirus lock on Windows, a permissions error) leaves a half-empty `data/`.
   This loop also runs on the **v4 registry-sync path** — the one the maintainer runs on the
   live field package every MINOR release — where the report says
   `backup: "none (registry-sync is a pure append)"`. There, git history is the only net.
2. **The v3 path mutates before it validates, then lies about it.** `_convert_legacy_prompts`
   writes `prompts/*.md` and deletes `data/prompts.jsonl` *before* `_read_jsonl_tables` parses
   the rest. If parsing or the store validation then fails, the error says
   *"package UNCHANGED (old files intact, backup at data-v3-backup/)"* — false on the first
   clause — and the leftover `data-v3-backup/` makes the next `confirm` refuse with
   *"a previous migration ran"*. A malformed line in `trace_edges.jsonl` hits `_filter_jsonl`'s
   bare `json.loads` inside the converter and escapes as a raw exception (after the prompts
   were written).
3. **A corrupt `packages.jsonl` skips the v4 refusal.** `_stored_package_version` returns
   `None` on a JSON parse error; `package_open` treats `None` as "no version, proceed" and
   the store load then raises a raw exception out of the tool instead of an error dict.

The fix is small once the tests exist: parse and validate first, write new files beside the
old ones and swap last, restore from the backup on any failure, and make the version reader
report corruption instead of hiding it.

## Current state

- `plugins/tamheed/server/tamheed_server.py` — the MCP server. Relevant regions at the
  planned commit:

  - `_filter_jsonl` :452–469 — `keep(json.loads(line))` with no error handling; called by
    `_convert_legacy_prompts` (:472 onward) to scrub `PRM-` edges/registry rows.
  - `_stored_package_version` :551–562:

    ```python
    def _stored_package_version(pkg_dir: Path) -> str | None:
        """Read package_version straight from data/packages.jsonl (no store open)."""
        path = pkg_dir / "data" / "packages.jsonl"
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    return str(json.loads(line).get("package_version"))
                except ValueError:
                    return None
        return None
    ```

    Callers: `package_open` :574 (`stored = _stored_package_version(pkg_dir)`; refuses only
    when `stored is not None and not stored.startswith("4.")`), `package_migrate` :2578
    (`v4_sync = stored is not None and str(stored).startswith("4.")`).
  - `package_migrate` :2541–2768. The confirm branch, v3 path (:2592–2609):

    ```python
        if confirm and not v4_sync:
            backup = pkg_dir / "data-v3-backup"
            if backup.exists():
                return _err("data-v3-backup/ already exists — a previous migration ran;"
                            " remove or rename it before migrating again")
            backup.mkdir()
            for f in data.iterdir():
                if f.name != store.LOCK_NAME:
                    shutil.copy2(f, backup / f.name)
            try:
                conversion = _convert_legacy_prompts(pkg_dir)
            except ValueError as exc:
                shutil.rmtree(backup)
                return _err(str(exc))
        try:
            tables = _read_jsonl_tables(data)
        except ValueError as exc:
            return _err(str(exc))
    ```

    The validation + write-back (:2726–2749):

    ```python
        with tempfile.TemporaryDirectory() as td:
            tmp_pkg = Path(td) / "pkg"
            (tmp_pkg / "data").mkdir(parents=True)
            for tname, rows in tables.items():
                if rows:
                    (tmp_pkg / "data" / f"{tname}.jsonl").write_bytes(...)
            try:
                ts = store.PackageStore(tmp_pkg).__enter__()
            except Exception as exc:
                return _err(f"migration validation failed — package UNCHANGED"
                            f" (old files intact, backup at data-v3-backup/): {exc}")
            try:
                ts.commit()
            finally:
                ts.__exit__(None, None, None)
            stale = set(tables) | {p.stem for p in data.glob("*.jsonl")}
            for tname in stale:
                (data / f"{tname}.jsonl").unlink(missing_ok=True)
            for f in (tmp_pkg / "data").glob("*.jsonl"):
                shutil.copy2(f, data / f.name)
    ```

    The whole body sits in `try: … finally: os.close(fd); lock.unlink()` (the migrate lock,
    :2566–2569 / :2766–2768). The preview (`confirm=False`) path returns before the
    `TemporaryDirectory` block and writes nothing — keep it that way.
- `plugins/tamheed/db/store.py` — `PackageStore(pkg_dir).__enter__()` loads `data/`, applies
  migrations, runs integrity checks; raises on failure. `store.LOCK_NAME == ".lock"`.
- `tests/test_migrate_v3to4.py` — the migration suite. `build_v3_fixture(root, name="legacy")`
  writes a synthetic v3.2.1 package (every transform exercised, includes `prompts.jsonl` and
  `trace_edges.jsonl`) and returns the package dir; `rows(pkg, fname)` reads a JSONL file.
  `MigrateV3ToV4Test` migrates ONE fixture in `setUpClass` and asserts on the outcome (so it
  cannot host failure-path tests — order-dependent). `MigrateDeterminismTest` shows the
  per-test pattern: fresh `tempfile.TemporaryDirectory()`, `srv.PACKAGE_ROOT = Path(td)`,
  `srv._CURRENT = srv._CURRENT_NAME = None`, `build_v3_fixture(...)`, `package_migrate(...)`.
  Stdlib `unittest` only; `unittest.mock` is stdlib and fine.
- The registry-sync path can be produced in a test by building a **v4** package via the tools
  (`srv.package_create` + `srv.package_close`), then deleting one `entity_types.jsonl` row that
  `BASELINE_ENTITY_TYPES` expects — see how `test_registry_sync_teaches_v4_package_new_types`
  in `tests/test_mcp_contract.py` sets that up, and copy it.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files (root `README.md`,
  `plugins/tamheed/server/README.md`, `plugins/tamheed/prompts/README.md`,
  `plugins/tamheed/SKILL.md`, `plugins/tamheed/references/artifact-catalog.md`).
- Do NOT touch `plugins/tamheed/prompts/*.md`; do NOT hand-edit goldens.
- `MigrateDeterminismTest.test_same_input_same_bytes` must keep passing — the write-back
  change must not alter output bytes.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Migration suite | `python tests/test_migrate_v3to4.py` | `OK` |
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Snapshot helper (in tests) | `{p.name: p.read_bytes() for p in data.glob("*.jsonl")}` | dict; compare before/after |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — `_stored_package_version`, `_filter_jsonl`,
  `package_migrate`, and the two callers of `_stored_package_version`.
- `tests/test_migrate_v3to4.py` — one new test class.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- `plugins/tamheed/server/migrate_v3to4.py` (the row transforms) — not the problem.
- `plugins/tamheed/db/store.py` and `db/migrations/**` (append-only, frozen).
- The preview report's content/shape, `relocate` semantics, `_emit_prompt_library`.
- `docs/migrate-from-keystone.md` — plan 048.
- Making the multi-file swap truly atomic (would need a journal/rename-directory dance) —
  deliberately deferred; "nothing is deleted until every new file is on disk" is the bar.

## Git workflow

- `main` or a local branch `advisor/045-migrate-fail-atomic`. Two commits are natural:
  `test: characterize package_migrate failure paths (plan 045)` (red), then
  `fix: package_migrate leaves the package untouched on any failure (plan 045)` (green).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Write the characterization tests (expect RED)

Append to `tests/test_migrate_v3to4.py` a new class. Each test gets a fresh root; copy the
setup from `MigrateDeterminismTest`. Use these names and assertions:

```python
class MigrateFailurePathTest(unittest.TestCase):
    """Plan 045: confirm=true must leave the package untouched on ANY failure."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        srv.PACKAGE_ROOT = Path(self._tmp.name)
        srv._CURRENT = srv._CURRENT_NAME = None

    def tearDown(self):
        if srv._CURRENT is not None:
            srv.package_close()
        self._tmp.cleanup()

    @staticmethod
    def _snapshot(pkg: Path) -> dict:
        return {p.relative_to(pkg).as_posix(): p.read_bytes()
                for p in pkg.rglob("*") if p.is_file() and p.name != ".lock"}

    def test_unparseable_table_leaves_package_untouched(self):
        pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        (pkg / "data" / "risks.jsonl").write_bytes(b'{"id": "RISK-001", broken\n')
        before = self._snapshot(pkg)
        res = srv.package_migrate("legacy", confirm=True)
        self.assertFalse(res.get("ok"))
        self.assertIn("risks.jsonl", res["error"])
        self.assertEqual(self._snapshot(pkg), before)          # bytes identical
        self.assertFalse((pkg / "data-v3-backup").exists())    # no leftover backup
        self.assertFalse((pkg / "prompts").exists())           # no converted prompts
        again = srv.package_migrate("legacy")                  # a retry is not refused
        self.assertNotIn("previous migration ran", str(again.get("error", "")))

    def test_unparseable_trace_edge_during_prompt_conversion(self):
        pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        with (pkg / "data" / "trace_edges.jsonl").open("ab") as fh:
            fh.write(b"not json\n")
        before = self._snapshot(pkg)
        res = srv.package_migrate("legacy", confirm=True)      # today: raises
        self.assertFalse(res.get("ok"))
        self.assertEqual(self._snapshot(pkg), before)
        self.assertFalse((pkg / "data-v3-backup").exists())

    def test_store_validation_failure_restores_everything(self):
        from unittest import mock
        pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        before = self._snapshot(pkg)
        with mock.patch.object(srv.store, "PackageStore",
                               side_effect=RuntimeError("simulated integrity failure")):
            res = srv.package_migrate("legacy", confirm=True)
        self.assertFalse(res.get("ok"))
        self.assertIn("UNCHANGED", res["error"])
        self.assertEqual(self._snapshot(pkg), before)          # the claim must be true
        self.assertFalse((pkg / "data-v3-backup").exists())
        self.assertFalse((pkg / "prompts").exists())

    def test_write_back_failure_keeps_old_files(self):
        """Nothing is deleted until every new file is on disk (also the v4 sync path)."""
        import os
        from unittest import mock
        pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        before = self._snapshot(pkg)
        real_replace = os.replace
        def boom(src, dst, *a, **k):
            if str(dst).endswith("requirements.jsonl"):
                raise OSError("simulated rename failure")
            return real_replace(src, dst, *a, **k)
        with mock.patch.object(srv.os, "replace", boom):
            res = srv.package_migrate("legacy", confirm=True)
        self.assertFalse(res.get("ok"))
        self.assertEqual(self._snapshot(pkg), before)
        self.assertEqual(list(pkg.glob("data/*.tmp")), [])

    def test_corrupt_packages_jsonl_is_an_error_not_an_exception(self):
        pkg = build_v3_fixture(srv.PACKAGE_ROOT)
        (pkg / "data" / "packages.jsonl").write_bytes(b"{not json\n")
        res = srv.package_open("legacy")
        self.assertFalse(res.get("ok"))
        self.assertIn("packages.jsonl", res["error"])
        self.assertIsNone(srv._CURRENT)
        res = srv.package_migrate("legacy")
        self.assertFalse(res.get("ok"))
        self.assertIn("packages.jsonl", res["error"])
```

**Verify**: `python tests/test_migrate_v3to4.py` → the five new tests FAIL or ERROR (expected:
`test_unparseable_trace_edge…` errors with a JSON exception, `test_corrupt_packages_jsonl…`
errors with an exception out of `package_open`, the others fail on the snapshot/backup
assertions). The pre-existing tests still pass. If `test_write_back_failure_keeps_old_files`
*passes* before the fix, the mock is not intercepting anything (the old code uses
`shutil.copy2`, not `os.replace`) — that is fine; it will start measuring after Step 4.

### Step 2: `_stored_package_version` reports corruption

Change the function so a parse failure is an error the callers can surface:

```python
def _stored_package_version(pkg_dir: Path) -> str | None:
    """Read package_version straight from data/packages.jsonl (no store open).
    Raises ValueError on a corrupt file (plan 045: None used to mean both 'no row'
    and 'unreadable', and the unreadable case then escaped as a raw exception)."""
    path = pkg_dir / "data" / "packages.jsonl"
    if not path.exists():
        return None
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                return str(json.loads(line).get("package_version"))
            except ValueError:
                raise ValueError(f"data/packages.jsonl:{lineno} is not valid JSON — the"
                                 " package row is unreadable; repair it (git) before"
                                 " opening or migrating") from None
    return None
```

At both callers wrap the call:

```python
    try:
        stored = _stored_package_version(pkg_dir)
    except ValueError as exc:
        return _err(str(exc))
```

(In `package_migrate` the call is inside the lock `try:` — the `finally` releases the lock; the
early `return` is fine.)

**Verify**: `python tests/test_migrate_v3to4.py` → `test_corrupt_packages_jsonl_is_an_error_not_an_exception`
passes; `python tests/test_mcp_contract.py` → `OK`.

### Step 3: Parse first, convert second, restore on any failure

Restructure the confirm branch so that **nothing under the package is modified until every
input has parsed**, and any exception after the first write restores the backup:

1. Add a **parse-only pre-check** above the `if confirm and not v4_sync:` block:

   ```python
        try:
            _read_jsonl_tables(data)   # plan 045: every input parses BEFORE any write
        except ValueError as exc:
            return _err(str(exc))
   ```

   and **keep** the existing `tables = _read_jsonl_tables(data)` where it is (after the
   conversion). Two reads, deliberately: the conversion deletes `data/prompts.jsonl` and
   scrubs the `PRM-` edges and `prompt` registry/omission rows, so `tables` must be read
   *after* it or the transform carries rows the v4 store FK-rejects (that would turn every
   v3 confirm red). The first read is what makes test 1 refuse with no backup left behind.
2. Make `_filter_jsonl` raise `ValueError(f"{path.name}:{lineno} unparseable JSON")` instead of
   letting `json.JSONDecodeError` escape (wrap the `json.loads` like `_read_jsonl_tables` does).
   `_convert_legacy_prompts` already documents "Raises ValueError … on refusal", so the caller's
   `except ValueError` now catches it.
3. Wrap everything from `backup.mkdir()` to the end of the write-back in one `try`, and on
   *any* exception restore:

   ```python
   def _restore_from_backup(data: Path, backup: Path, conversion: dict | None) -> None:
       """plan 045: undo a partial confirm — copy every backed-up file back, drop files the
       conversion wrote, delete the backup so the operator can retry."""
       for f in data.glob("*.jsonl"):
           f.unlink()
       for f in data.glob("*.tmp"):
           f.unlink()
       for f in backup.iterdir():
           shutil.copy2(f, data / f.name)
       for rel in (conversion or {}).get("prompts_converted", []):
           (data.parent / rel).unlink(missing_ok=True)
       prompts = data.parent / "prompts"
       if prompts.is_dir() and not any(prompts.iterdir()):
           prompts.rmdir()                      # the converter created it; leave no husk
       shutil.rmtree(backup)
   ```

   and the error returned is the *true* statement:
   `_err(f"migration failed — package restored from data-v3-backup/ (now removed): {exc}")`.
   The existing "validation failed" branch becomes one of these callers (its message loses
   the false "old files intact" clause for the v3 path; for the v4 sync path — no backup —
   "UNCHANGED" stays true because Step 4 guarantees nothing was deleted).

   Keep `conversion` in scope for the restore (`prompts_converted` is the list the test
   `test_confirm_backs_up_converts_prompts_and_rewrites` asserts on; check the key name in
   `_convert_legacy_prompts`'s return value and use exactly that).

**Verify**: `python tests/test_migrate_v3to4.py` → the first three new tests pass; all old ones
pass.

### Step 4: Write beside, then swap

Replace the unlink-then-copy loop with write-all-tmp → unlink-stale → rename-all:

```python
            new_files = sorted((tmp_pkg / "data").glob("*.jsonl"))
            staged = []
            try:
                for f in new_files:                      # 1) every new byte on disk first
                    dst = data / (f.name + ".tmp")
                    shutil.copy2(f, dst)
                    staged.append(dst)
                stale = set(tables) | {p.stem for p in data.glob("*.jsonl")}
                for tname in stale:                      # 2) then retire the old files
                    (data / f"{tname}.jsonl").unlink(missing_ok=True)
                for dst in staged:                       # 3) then swap names
                    os.replace(dst, data / dst.name[:-4])
            except Exception as exc:
                for dst in staged:
                    dst.unlink(missing_ok=True)
                raise
```

On the v3 path the outer `try` from Step 3 restores from the backup. On the v4 sync path there
is no backup and no outer `try`, so the `raise` above would escape the tool as a traceback —
wrap the swap for that path so it returns an error dict instead:

```python
            try:
                <the swap block above>
            except Exception as exc:
                if v4_sync:
                    return _err(f"registry sync failed — package UNCHANGED (nothing was"
                                f" deleted; staged .tmp files removed): {exc}")
                raise   # v3 path: the outer restore-from-backup handles it
```

Because step 2 (unlink stale) only runs after step 1 completed, a failure in step 1 leaves the
old files intact and the "UNCHANGED" text is true. A failure in step 3 is the residual window
(rename failures on the same filesystem are rare) — document it in a comment; do not build a
journal.

Test note: `test_write_back_failure_keeps_old_files` patches `srv.os.replace` to fail on
`requirements.jsonl`; with the order above, by then the stale files are already unlinked on
the **v3** path, and the restore-from-backup (Step 3) makes the snapshot equal again — that is
what the test asserts. Because `sorted()` puts `acceptance_criteria` and others before
`requirements`, some renames have succeeded; the restore must therefore unlink *all*
`*.jsonl` before copying the backup back (the helper above does).

**Verify**: `python tests/test_migrate_v3to4.py` → `OK` (all five new tests pass);
`MigrateDeterminismTest` still passes (same bytes).

### Step 5: Registry-sync path stays green

**Verify**: `python tests/test_mcp_contract.py` → `OK`, in particular
`test_registry_sync_teaches_v4_package_new_types` and
`test_registry_sync_names_reserialized_columns`; `python check.py` → `ALL CHECKS PASSED`
(the `lab-tracker` eval fixture is a v4 package that has been through registry sync).

### Step 6: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- `package_migrate(confirm=true)` is fail-safe: inputs are parsed before anything is
  written, new files land beside the old ones and are swapped in last (the registry-sync
  path had no backup and deleted before it copied), and any failure restores `data/` from
  `data-v3-backup/` and removes it so the retry is not refused; a corrupt
  `data/packages.jsonl` is an error naming the file, not a traceback (advisor plan 045).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New class `MigrateFailurePathTest` (Step 1): five tests — unparseable table, unparseable
  trace edge during conversion, simulated store-validation failure, simulated rename failure,
  corrupt `packages.jsonl`. Pattern: `MigrateDeterminismTest` (fresh root per test).
- Existing: all of `MigrateV3ToV4Test` and `MigrateDeterminismTest`; contract-suite
  registry-sync tests; `test_convert_unparseable_line_blocks_migrate`,
  `test_v3_confirm_removes_stale_converted_file`, `test_migrate_relocates_converted_file_out_of_data`.
- Verification: `python tests/test_migrate_v3to4.py` → `OK`; `python check.py` →
  `ALL CHECKS PASSED`.

## Done criteria

- [ ] `python tests/test_migrate_v3to4.py` → `OK`, with `MigrateFailurePathTest` present (5 tests)
- [ ] `grep -n 'old files intact' plugins/tamheed/server/tamheed_server.py` → no matches
- [ ] `grep -n 'os.replace' plugins/tamheed/server/tamheed_server.py` → ≥1 match inside `package_migrate`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The excerpts in "Current state" don't match the live code (drift).
- `_convert_legacy_prompts`'s return dict has no list of written prompt paths (needed by the
  restore) — report the actual keys rather than guessing.
- `MigrateDeterminismTest` fails after Step 4 — the swap must not change bytes; do not
  "fix" the golden.
- The lab-tracker eval fixture or any golden shows a diff after `python check.py`.
- A test needs `mock.patch` on something other than `srv.store.PackageStore` or
  `srv.os.replace` to fail — report; do not weaken the assertion to make it pass.

## Maintenance notes

- Invariant for reviewers: in `package_migrate`, the first filesystem write happens only
  after `_read_jsonl_tables` returned, and every write after `backup.mkdir()` is inside the
  restore-guarded `try`. New steps added to the confirm path go inside that `try`.
- The residual non-atomic window is step 3 of the swap (rename loop). If the field ever
  reports a half-swapped `data/`, the next shape is "rename `data/` → `data-old/`, rename a
  fully-built `data-new/` → `data/`" — one directory rename each way.
- Plan 048 rewrites the operator-facing migration docs; the error texts changed here
  ("package restored from data-v3-backup/ (now removed)") should be quoted there if the
  docs ever list them.
