# Plan 051: An omission's changed `reason` is written, not silently reported `unchanged`

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py plugins/tamheed/scripts/scratch_diff.py tests/test_mcp_contract.py tests/test_scratch_diff.py CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: 043 (the `entity_upsert` tail must be settled first; this plan edits the
  SQL-selection block above it)
- **Category**: bug
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

`omission` rows are the G-SET mechanism: "this Always family is absent *for this reason*". The
row is keyed by `entity_type` alone (`PRIMARY KEY`, `reason NOT NULL CHECK (reason <> '')`).
`entity_upsert` writes omissions with `INSERT OR IGNORE`, the same path as trace edges, and
then reports a zero-rowcount write as `ok: true, unchanged: true` when a row with the same key
exists. For trace edges that is right — the key *is* the whole row. For omissions the `reason`
is the content: an agent that revises the reason ("not needed at this size" → "deferred to
phase 2 per DEC-004") gets `ok: true` and the old reason stays on disk. That is exactly the
"paste guard" class plan 041 fought (`ok: true` with the content lost) — here by design of the
SQL, not by transport. Fix: give omissions the ordinary upsert path with `entity_type` as the
conflict target, and fix the one sibling that hard-codes the wrong key
(`scripts/scratch_diff.py` keys omissions on `(entity_type, reason)`, so a reason change
diffs as delete+add instead of a change).

## Current state

Line numbers below are at `7e3a92b`; earlier advisor plans (043–049) shift them by a few lines.
Compare the **excerpts**, not the numbers — a matching excerpt at a nearby line is not drift.

- `plugins/tamheed/db/schema.sql:68-71`:

  ```sql
  CREATE TABLE omissions (                                 -- G-SET: recorded-omitted with reason
    entity_type       TEXT PRIMARY KEY REFERENCES entity_types(type_id),
    reason            TEXT NOT NULL CHECK (reason <> '')
  );
  ```

- `plugins/tamheed/server/tamheed_server.py`, `entity_upsert`, the SQL selection (:1045–1057):

  ```python
        if etype in ("trace-edge", "omission"):
            sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        elif etype in ("progress-entry", "audit-verdict"):
            # C31 (A4): the journal is APPEND-ONLY — no ON CONFLICT path, so writing an
            # existing id errors instead of silently rewriting recorded history.
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        else:
            updates = ", ".join(f"{c} = excluded.{c}" for c in names if c != "id")
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})"
                   + (f" ON CONFLICT(id) DO UPDATE SET {updates}" if updates else ""))
  ```

  and the zero-rowcount handling right after (:1064–1081):

  ```python
            if etype in ("trace-edge", "omission") and cur.rowcount == 0:
                # C31 (A3): IGNORE dropped the row — distinguish the idempotent
                # duplicate (fine, the reason IGNORE exists) from a constraint
                # rejection (an attempt is not a write and must not count as one).
                pk = (("from_id", "to_id", "relation") if etype == "trace-edge"
                      else ("entity_type",))
                exists = conn.execute(...).fetchone()
                if exists:
                    results.append({"index": i, "ok": True, "unchanged": True,
                                    "id": cols.get("id")})
                else:
                    results.append({"index": i, "ok": False, ...
                                    "error": "row rejected by a constraint "
                                             "(CHECK/NOT NULL) — not written"})
                    failed = True
  ```

  The `applied` count at the tail excludes `unchanged` items.
- `plugins/tamheed/scripts/scratch_diff.py:27-32`:

  ```python
  KEYS = {
      "trace_edges": ("from_id", "to_id", "relation"),
      "omissions": ("entity_type", "reason"),
      "entity_types": ("type_id",),
      "packages": ("name",),  # singleton in practice — see diff_table
  }
  ```

- `export_html`'s CSV `ORDER BY` for omissions is `entity_type, reason` — harmless, leave it.
- Tests: `tests/test_mcp_contract.py::test_gate_set_honors_recorded_omission` (~:1529) writes
  ten omissions and expects G-SET `pass`; `tests/test_scratch_diff.py` has no omission cases
  (`grep -n omission tests/test_scratch_diff.py` → nothing).

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files.
- Do NOT touch `plugins/tamheed/prompts/*.md` or `db/schema.sql`/`db/migrations/**`
  (no schema change is needed — the PK is already right).
- Goldens must not change (an omission written with the same reason is byte-identical).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| scratch_diff suite | `python tests/test_scratch_diff.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — the two excerpts above.
- `plugins/tamheed/scripts/scratch_diff.py` — one tuple.
- `tests/test_mcp_contract.py`, `tests/test_scratch_diff.py` — one test each.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- Trace edges — `INSERT OR IGNORE` is correct there (the key is the row).
- The `applied`/`unchanged` accounting at the function tail (plan 043 territory).
- G-SET itself, the omission template text, `export_html`'s omission ordering.

## Git workflow

- `main` or a local branch `advisor/051-omission-reason`; one commit:
  `fix: an omission's changed reason is written, not reported unchanged (plan 051)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Give omissions a real upsert

Change the SQL selection to:

```python
        if etype == "trace-edge":
            sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        elif etype in ("progress-entry", "audit-verdict"):
            ... (unchanged)
        else:
            # Plan 051: omissions are keyed by entity_type and their reason is content —
            # a revised reason must land, never report `unchanged`.
            key = "entity_type" if etype == "omission" else "id"
            updates = ", ".join(f"{c} = excluded.{c}" for c in names if c != key)
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})"
                   + (f" ON CONFLICT({key}) DO UPDATE SET {updates}" if updates else ""))
```

Then narrow the zero-rowcount block to trace edges only: change
`if etype in ("trace-edge", "omission") and cur.rowcount == 0:` to
`if etype == "trace-edge" and cur.rowcount == 0:` and simplify the `pk = (...)` expression to
`pk = ("from_id", "to_id", "relation")`.

**Verify**: `python tests/test_mcp_contract.py` → `OK` (`test_gate_set_honors_recorded_omission`
still passes; a re-sent identical omission now counts as applied like any id-keyed upsert).

### Step 2: Regression test

In `McpContractTest`, after `test_gate_set_honors_recorded_omission`:

```python
    def test_omission_reason_revision_lands(self):
        """Plan 051: INSERT OR IGNORE dropped a revised reason and said ok/unchanged."""
        srv.package_create("demo", "Demo", "unknown")
        first = srv.entity_upsert([{"type": "omission", "entity_type": "risk",
                                    "reason": "not needed at this size"}])
        self.assertTrue(first["ok"], first)
        second = srv.entity_upsert([{"type": "omission", "entity_type": "risk",
                                     "reason": "deferred to phase 2 per DEC-004"}])
        self.assertTrue(second["ok"], second)
        self.assertNotIn("unchanged", second["items"][0])
        rows = srv.entity_query("omission")["rows"]
        self.assertEqual([r["reason"] for r in rows if r["entity_type"] == "risk"],
                         ["deferred to phase 2 per DEC-004"])
        bad = srv.entity_upsert([{"type": "omission", "entity_type": "risk", "reason": ""}])
        self.assertFalse(bad["ok"])                       # CHECK (reason <> '') still bites
```

If `entity_query("omission")` needs a different type name, use whatever key `ENTITY_TABLES`
maps to `omissions` (`grep -n '"omissions"' plugins/tamheed/server/tamheed_server.py`).

**Verify**: `python tests/test_mcp_contract.py` → `OK`; revert Step 1 temporarily and confirm
the test fails on `assertNotIn("unchanged", …)` or the reason assertion, then re-apply.

### Step 3: `scratch_diff` keys omissions by its primary key

In `plugins/tamheed/scripts/scratch_diff.py` change `"omissions": ("entity_type", "reason"),`
to `"omissions": ("entity_type",),`. Add to `tests/test_scratch_diff.py` a test in the style
of its existing cases (read the file's first test for the fixture-building helper it uses):
two directories whose `omissions.jsonl` differ only in `reason` for `risk` → the diff reports
one *changed* row for `omissions/risk`, not one removed + one added.

**Verify**: `python tests/test_scratch_diff.py` → `OK`.

### Step 4: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- `entity_upsert` on an `omission` whose `reason` changed now updates the row; it used to
  `INSERT OR IGNORE` and report `ok: true, unchanged: true` with the old reason left on disk.
  `scripts/scratch_diff.py` keys omissions by `entity_type` (the table's primary key), so a
  reason change diffs as a change (advisor plan 051).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_omission_reason_revision_lands` (contract); one scratch_diff omission test.
- Existing: `test_gate_set_honors_recorded_omission`, `test_trace_edge_rejection_vs_duplicate`
  (the IGNORE path for edges must be untouched), `test_registry_scrubbed_and_completed`
  (migration writes omission rows).

## Done criteria

- [ ] `grep -c 'INSERT OR IGNORE' plugins/tamheed/server/tamheed_server.py` → `1` (it was 1 before too — the single site is now inside the `etype == "trace-edge"` branch)
- [ ] `grep -n '"omissions": ("entity_type",)' plugins/tamheed/scripts/scratch_diff.py` → one hit
- [ ] `python tests/test_mcp_contract.py`, `python tests/test_scratch_diff.py` → `OK`
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The SQL-selection block does not match the excerpt (drift — plan 043 or 053 may have moved
  lines; re-locate by the comment text `C31 (A4)` and proceed only if the logic is identical).
- `schema.sql`'s omissions PK is not `entity_type` alone.
- Any golden changes.

## Maintenance notes

- Rule for reviewers: `INSERT OR IGNORE` is for tables whose key is the whole row (trace
  edges). Any new non-id-keyed table with content columns goes through the `ON CONFLICT(<pk>)`
  path with its real key.
- `scratch_diff.KEYS` mirrors `_NON_ID_TABLES`; if a lint is ever added for hand-copied
  rosters (the adopt `ALWAYS_TYPES` copy is the other one), this dict belongs in it.
