# Plan 043: Make the stale-tree refusal in `entity_upsert` actually roll the batch back

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_mcp_contract.py CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

`entity_upsert` wraps its batch in `SAVEPOINT batch`, then calls `_commit()`, whose job is to
refuse the write when `data/` changed on disk underneath the session (a git checkout, a second
writer — field evidence C31/C1) and to roll the batch back "so it cannot ride a LATER commit".
The rollback is a no-op: the function executes `RELEASE batch` **before** `_commit()`, and in
SQLite releasing the outermost savepoint *commits the transaction*. By the time
`store.commit()` raises `StoreStaleError`, the batch is already durable in the in-memory
database and `conn.rollback()` has nothing to undo. Reproduced on 2026-09-10: after a refused
upsert of `RISK-002`, `entity_query("risk")` returned both `RISK-001` and `RISK-002`, and
`conn.in_transaction` was `False`. Every later read, `gate_run`, `readiness_check`,
`export_html`, and `entity_export` in that session answers from the phantom batch, and the
error text ("the batch was NOT applied") is false. The fix is a one-line deletion; it was
tested on a scratch copy against the full contract suite (124 tests, 0 failures).

## Current state

- `plugins/tamheed/server/tamheed_server.py` — the MCP server, single file.
  - `_commit()` at lines 357–367:

    ```python
    def _commit() -> dict | None:
        """Write-back via the store; a tree that moved underneath the session is refused
        loudly (C31/C1) and the pending batch is rolled back so it cannot ride a LATER
        commit. Returns an error dict to surface, or None on success."""
        try:
            _CURRENT.commit()
        except store.StoreStaleError as exc:
            _CURRENT.conn.rollback()
            return _err(f"{exc} — the batch was NOT applied; close the package, reconcile "
                        "data/ via git, then reopen and retry")
        return None
    ```

  - `entity_upsert` opens the savepoint at line 847: `conn.execute("SAVEPOINT batch")`.
  - The tail of `entity_upsert`, lines 1153–1166 (the bug is line 1159):

    ```python
        if failed:
            conn.execute("ROLLBACK TO batch")
            conn.execute("RELEASE batch")
            return {"ok": False, "applied": 0,
                    "error": "batch rolled back — one or more items violated constraints",
                    "items": results}
        conn.execute("RELEASE batch")          # <-- line 1159: DELETE THIS LINE
        if err := _commit():
            return err
        # C31 (A3): `applied` counts WRITES, not attempts — ignored duplicates are ok
        # per-item (`unchanged`) but never counted as applied.
        return {"ok": True,
                "applied": sum(1 for r in results if r["ok"] and not r.get("unchanged")),
                "items": results}
    ```

  - Every other `SAVEPOINT`/`RELEASE` in the file is the per-item `item{i}` savepoint
    (lines 919–937 and 1058–1117) nested inside `batch`; they are correct and untouched.
- `plugins/tamheed/db/store.py` — `PackageStore.commit()` at lines 226–242 fingerprints
  `data/`, raises `StoreStaleError` if it moved, and only then runs `self.conn.commit()` and
  `dump(...)`. `conn.commit()` ends the transaction and thereby releases every open savepoint —
  which is why simply deleting line 1159 is correct: on success the store's own commit closes
  `batch`; on refusal the connection is still `in_transaction`, so the existing
  `conn.rollback()` in `_commit()` now discards the batch.
- **Do not "move" the RELEASE after `_commit()`** — that was tried: after a successful
  `conn.commit()` the savepoint no longer exists and `RELEASE batch` raises
  `sqlite3.OperationalError: no such savepoint: batch` (108 test errors).
- Test conventions: `tests/test_mcp_contract.py` drives the tool functions in-process
  (`import tamheed_server as srv`), builds packages in a `tempfile.TemporaryDirectory()` set
  as `srv.PACKAGE_ROOT` in `setUp`, closes in `tearDown`. The pattern to copy is
  `test_stale_tree_refused_by_write_tools` (line ~594):

    ```python
    def test_stale_tree_refused_by_write_tools(self):
        make_complete_package("demo")
        path = srv._CURRENT.data_dir / "requirements.jsonl"
        moved = path.read_text(encoding="utf-8").replace("Triage email", "Edited outside")
        path.write_text(moved, encoding="utf-8")
        out = srv.progress_update([{"entry": "should be refused"}])
        self.assertFalse(out["ok"])
        self.assertIn("NOT applied", out["error"])
        self.assertEqual(path.read_text(encoding="utf-8"), moved)   # disk preserved
        closed = srv.package_close()             # a stale tree must not TRAP the session
        self.assertTrue(closed["ok"])
        self.assertIn("WITHOUT the final flush", closed["warning"])
    ```

  `make_complete_package(name)` (top of the file) creates a package containing `RISK-001`
  among other rows. Stdlib `unittest` only — no pytest, no fixtures (D-U3).

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` — lint 4 ties it to the newest
  CHANGELOG release heading.
- Put your CHANGELOG note under the existing empty `## [Unreleased]` heading in `CHANGELOG.md`
  (line 12), using a `### Fixed` subheading like the released entries. That heading carries
  no version, so lints 4/5 ignore it.
- Do NOT edit the version string in the five version-stamped files (root `README.md`,
  `plugins/tamheed/server/README.md`, `plugins/tamheed/prompts/README.md`,
  `plugins/tamheed/SKILL.md`, `plugins/tamheed/references/artifact-catalog.md`).
- Do NOT touch `plugins/tamheed/prompts/*.md` (lint 9 needs a release key for any body change).
- Goldens (`evals/sample-results/**`, `generated-samples/**`) are never hand-edited; this plan
  must not change them at all.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` (125 tests after this plan: 124 + 1) |
| Full gate | `python check.py` | last line `ALL CHECKS PASSED`, exit 0 |
| Grep the bug | `grep -n 'RELEASE batch' plugins/tamheed/server/tamheed_server.py` | exactly one hit (line ~1155, inside the `if failed:` branch) |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — delete one line (1159).
- `tests/test_mcp_contract.py` — add one test.
- `CHANGELOG.md` — one bullet under `## [Unreleased]` / `### Fixed`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- `plugins/tamheed/db/store.py` — `commit()` is correct; the bug is in the caller.
- The `if failed:` branch (lines 1153–1158) — its `ROLLBACK TO batch; RELEASE batch` pair is
  correct (no `_commit()` follows it).
- The per-item `item{i}` savepoints.
- `progress_update`, `audit_record`, `work_bind` — they call `_commit()` without an outer
  savepoint (Python's sqlite3 auto-begins before DML), so their rollback already works; the
  existing stale-tree test covers `progress_update`.

## Git workflow

- Work on `main` or a local branch `advisor/043-stale-rollback` — the repo has no branch
  convention (everything lands on `main`).
- One commit, conventional style: `fix: stale-tree refusal rolls the upsert batch back (plan 043)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Delete the premature RELEASE

In `plugins/tamheed/server/tamheed_server.py`, delete the line
`    conn.execute("RELEASE batch")` that sits immediately before `    if err := _commit():`
(line 1159 at the planned commit). Leave the `if failed:` branch's RELEASE alone.

**Verify**: `grep -n 'RELEASE batch' plugins/tamheed/server/tamheed_server.py` → exactly one
match, and it is inside the `if failed:` block (the line before it is `ROLLBACK TO batch`).

### Step 2: Confirm the suite still passes

**Verify**: `python tests/test_mcp_contract.py` → `OK` (124 tests, 0 failures, 0 errors).

### Step 3: Add the regression test

In `tests/test_mcp_contract.py`, class `McpContractTest`, directly after
`test_stale_tree_refused_by_write_tools`, add:

```python
    def test_stale_tree_refusal_rolls_back_the_upsert_batch(self):
        """Plan 043: `RELEASE batch` before `_commit()` committed the batch in memory,
        so a refused upsert still answered every later read. The refusal must leave
        the in-memory store exactly as it was."""
        make_complete_package("demo")
        path = srv._CURRENT.data_dir / "risks.jsonl"
        moved = path.read_text(encoding="utf-8").replace("PII leak", "Edited outside")
        path.write_text(moved, encoding="utf-8")
        out = srv.entity_upsert([{"type": "risk", "id": "RISK-002", "title": "phantom"}])
        self.assertFalse(out["ok"])
        self.assertIn("NOT applied", out["error"])
        self.assertFalse(srv._CURRENT.conn.in_transaction)      # nothing left dangling
        ids = [r["id"] for r in srv.entity_query("risk", columns=["id"])["rows"]]
        self.assertEqual(ids, ["RISK-001"])                       # RISK-002 never landed
        self.assertEqual(path.read_text(encoding="utf-8"), moved)  # disk preserved
        closed = srv.package_close()
        self.assertTrue(closed["ok"])
        self.assertIn("WITHOUT the final flush", closed["warning"])
```

If `entity_query`'s signature differs from `entity_query("risk", columns=["id"])`, look at
how `test_audit_record_cascades_and_counts_evidence` calls it
(`srv.entity_query("requirement", id="FR-001", columns=["lifecycle_status"])`) and adapt —
the assertion is on the id list only.

**Verify**: `python tests/test_mcp_contract.py` → `OK`, 125 tests. To prove the test bites,
temporarily re-insert the deleted line, run the suite (expect this one test to FAIL on
`assertEqual(ids, ["RISK-001"])`), then delete the line again.

### Step 4: CHANGELOG

Under `## [Unreleased]` in `CHANGELOG.md` add:

```markdown
### Fixed

- `entity_upsert` released its `batch` savepoint before the stale-tree check, so a refused
  write (data/ moved underneath the session) stayed applied in memory and answered every
  later read in that session; the refusal now rolls the batch back as its message always
  claimed (advisor plan 043).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_stale_tree_refusal_rolls_back_the_upsert_batch` (Step 3) — the regression.
- Existing, must stay green: `test_stale_tree_refused_by_write_tools`,
  `test_upsert_partial_row_error_names_cause` (the `if failed:` branch),
  `test_journal_is_append_only`, and the whole `V4EngineTest` class (heavy `entity_upsert` use).
- Verification: `python tests/test_mcp_contract.py` → `OK`; `python check.py` →
  `ALL CHECKS PASSED`.

## Done criteria

- [ ] `grep -c 'RELEASE batch' plugins/tamheed/server/tamheed_server.py` → `1`
- [ ] `python tests/test_mcp_contract.py` exits 0 with 125 tests
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only the four in-scope files modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- Line 1159 is not `conn.execute("RELEASE batch")` followed by `if err := _commit():` (drift).
- After Step 1 any existing test errors with `no such savepoint` — you moved the line instead of
  deleting it, or a second `RELEASE batch` exists outside the `if failed:` branch.
- The regression test passes *with* the bug line re-inserted — the test is not measuring the
  rollback; report rather than loosen it.
- You find yourself wanting to edit `store.py`.

## Maintenance notes

- Invariant to keep: inside `entity_upsert`, `_commit()` must be the thing that ends the
  `batch` transaction. Any future refactor that adds an explicit `RELEASE`/`COMMIT` before
  `_commit()` reintroduces this bug silently — a reviewer should grep for `RELEASE batch`.
- Plan 053 (born-Implemented guard) adds a refusal path inside the same function; it uses the
  `failed = True; continue` pattern and does not touch the transaction tail.
- The same "release-then-check" shape does not exist in `progress_update`/`audit_record`/
  `work_bind` today; if one of them ever gains an outer savepoint, the regression test here
  is the template to copy.
