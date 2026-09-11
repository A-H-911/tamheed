# Plan 046: `_scan_markers` must skip Superseded/Obsolete rows like the placeholder scan does

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

`gate_run`'s G-COMPLETE has two scanners. The placeholder scan (`TODO`/`TBD`/`{{…}}`) was
fixed in plan 038 to skip rows whose `lifecycle_status` is `Superseded` or `Obsolete`, with
the reasoning written into the code: *"immutable-after-approval content is unreachable by
edit, and supersession — the sanctioned repair — must actually repair."* The second scanner,
`_scan_markers` (the `[NEEDS-CLARIFICATION: OQ-NNN]` markers), never got that filter. So an
approved decision that carried a marker citing an OQ which is later resolved cannot be
repaired: the row is immutable (trigger-enforced), superseding it leaves the old row in
place with the now-invalid marker, and G-COMPLETE — a **blocking** gate — fails forever with
`OQ-NNN is resolved — remove the marker`. This is the exact trap class plan 038 closed for
placeholders, and its doctrine (plan 040: *"a remedy named by a gate note must be an
operation the server exposes"*) is violated because the named remedy ("remove the marker")
is impossible on an immutable row. One `WHERE` clause fixes it; the readiness `open-markers`
advisory (which also calls `_scan_markers`) gets the same, correct, behaviour.

## Current state

Line numbers below are at `7e3a92b`; earlier advisor plans (043–045) shift them by a few lines.
Compare the **excerpts**, not the numbers — a matching excerpt at a nearby line is not drift.

- `plugins/tamheed/server/tamheed_server.py`
  - `_scan_markers(conn)` :296–328:

    ```python
    def _scan_markers(conn) -> list[dict]:
        """Every [NEEDS-CLARIFICATION…] marker in prose columns; `invalid` is None for a
        legal marker (cites an existing unresolved OQ), else the operator-facing reason."""
        found = []
        for table in ENTITY_TABLES.values():
            text_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")
                         if (r[2] or "").upper() == "TEXT" and r[1] != "custom_attributes"]
            if not text_cols:
                continue
            pk = _NON_ID_TABLES.get(table, "id")
            for row in conn.execute(f"SELECT {pk}, {', '.join(text_cols)} FROM {table}"):
                for col, value in zip(text_cols, row[1:]):
                    ...
    ```

  - The placeholder scan inside `gate_run`, :1352–1363 — the pattern to copy:

    ```python
            all_cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
            text_cols = [...]
            if not text_cols:
                continue
            pk = _NON_ID_TABLES.get(table, "id")
            # Superseded/Obsolete rows are HISTORY, not the plan (plan 038, the
            # trap-class completed): immutable-after-approval content is unreachable
            # by edit, and supersession — the sanctioned repair — must actually
            # repair. Live rows of every family stay fully screened.
            where = (" WHERE lifecycle_status NOT IN ('Superseded','Obsolete')"
                     if "lifecycle_status" in all_cols else "")
            for row in conn.execute(
                    f"SELECT {pk}, {', '.join(text_cols)} FROM {table}{where}"):
    ```

  - Callers of `_scan_markers`: `gate_run` :1378 (invalid markers → G-COMPLETE failures) and
    `_readiness_report` :1654 (valid markers → the `open-markers` advisory).
- Tests: `tests/test_mcp_contract.py`, class `V4EngineTest` (its `setUp` creates package
  `demo` with `PH-1`, `SL-001`, `WBS-1`, `AC-001`, `DEF-001`, … — read the `setUp` body for
  the full seed). Exemplar: `test_marker_validity_in_g_complete`:

    ```python
    def test_marker_validity_in_g_complete(self):
        self.assertEqual(srv.gate_run()["gates"]["G-COMPLETE"]["status"], "pass")
        srv.entity_upsert([{"type": "constraint", "id": "CON-002", "title": "c2",
                            "statement": "see [NEEDS-CLARIFICATION: OQ-099]",
                            "source_kind": "brief", "source_span": "b:2"}])
        gate = srv.gate_run()["gates"]["G-COMPLETE"]
        self.assertEqual(gate["status"], "fail")
        self.assertTrue(any("OQ-099 does not exist" in str(f.get("marker"))
                            for f in gate["failures"]))
    ```

  Constraints have a `lifecycle_status` column (every register table does; confirm with
  `python -c "import sys; sys.path.insert(0,'plugins/tamheed/server'); import tamheed_server as s; print('lifecycle_status' in [r[1] for r in s.store.connect().execute('PRAGMA table_info(constraints)')])"`
  → `True`; if `store.connect()` isn't the right constructor, read `plugins/tamheed/db/store.py`
  for the zero-arg in-memory connect used by `check.py`).

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files (root `README.md`,
  `plugins/tamheed/server/README.md`, `plugins/tamheed/prompts/README.md`,
  `plugins/tamheed/SKILL.md`, `plugins/tamheed/references/artifact-catalog.md`).
- Do NOT touch `plugins/tamheed/prompts/*.md`; do NOT hand-edit goldens.
- The `lab-tracker` eval fixture asserts "The ambiguity marker survives, citing the live OQ
  (G-COMPLETE-legal)" — that marker is on a live row and must still be reported; this plan
  only stops *history* rows from being scanned.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — `_scan_markers` only.
- `tests/test_mcp_contract.py` — one test in `V4EngineTest`.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- The placeholder scan in `gate_run` (already correct).
- `_MARKER_RE`, the OQ validity rules, the `open-markers` advisory text.
- Extracting a shared "live rows" helper for both scanners — tempting, not needed; two
  identical `where` expressions are fine.

## Git workflow

- `main` or a local branch `advisor/046-scan-markers-history`; one commit:
  `fix: G-COMPLETE marker scan skips Superseded/Obsolete rows like the placeholder scan (plan 046)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add the filter

In `_scan_markers`, compute `all_cols` and the `where` clause exactly as the placeholder scan
does, and apply it to the `SELECT`:

```python
    for table in ENTITY_TABLES.values():
        all_cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        text_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")
                     if (r[2] or "").upper() == "TEXT" and r[1] != "custom_attributes"]
        if not text_cols:
            continue
        pk = _NON_ID_TABLES.get(table, "id")
        # Plan 046: parity with the placeholder scan (plan 038) — Superseded/Obsolete
        # rows are history; an immutable row's stale marker is repaired by supersession.
        where = (" WHERE lifecycle_status NOT IN ('Superseded','Obsolete')"
                 if "lifecycle_status" in all_cols else "")
        for row in conn.execute(f"SELECT {pk}, {', '.join(text_cols)} FROM {table}{where}"):
```

**Verify**: `python tests/test_mcp_contract.py` → `OK`.

### Step 2: Regression test

In `V4EngineTest`, after `test_marker_validity_in_g_complete`:

```python
    def test_marker_on_superseded_row_is_history_not_a_failure(self):
        """Plan 046: parity with the placeholder scan — a stale marker on an
        immutable, superseded row cannot be edited away; supersession must repair."""
        live = {"type": "constraint", "id": "CON-010", "title": "c10",
                "statement": "see [NEEDS-CLARIFICATION: OQ-099]",
                "source_kind": "brief", "source_span": "b:10"}
        out = srv.entity_upsert([dict(live, lifecycle_status="Superseded")])
        self.assertTrue(out["ok"], out)
        gate = srv.gate_run()["gates"]["G-COMPLETE"]
        self.assertEqual(gate["status"], "pass", gate)          # history is not the plan
        adv = {r["rule"]: r for r in srv.readiness_check("package")["rules"]}
        self.assertNotIn("CON-010", adv.get("open-markers", {}).get("entities", []))
        out = srv.entity_upsert([dict(live, id="CON-011", lifecycle_status="Approved")])
        self.assertTrue(out["ok"], out)
        gate = srv.gate_run()["gates"]["G-COMPLETE"]
        self.assertEqual(gate["status"], "fail")                # live rows stay screened
        self.assertTrue(any(f.get("id") == "CON-011" for f in gate["failures"]))
```

If the `open-markers` rule is named differently, find it with
`grep -n '"open-markers"\|markers' plugins/tamheed/server/tamheed_server.py` around line 1654
and use that name; if a `Superseded` constraint needs a `superseded_by`-style column to pass a
CHECK, add the minimal column the error names.

**Verify**: `python tests/test_mcp_contract.py` → `OK`; temporarily revert Step 1 and confirm
the new test FAILS on `assertEqual(gate["status"], "pass")`, then re-apply.

### Step 3: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- G-COMPLETE's `[NEEDS-CLARIFICATION]` marker scan now skips `Superseded`/`Obsolete` rows,
  matching the placeholder scan (plan 038): a stale marker on an immutable, superseded row
  was a permanent blocking failure whose only named remedy — edit the row — the store
  forbids (advisor plan 046).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_marker_on_superseded_row_is_history_not_a_failure`.
- Existing that must stay green: `test_marker_validity_in_g_complete`,
  `test_g_complete_journal_exemption_and_matched`, `test_gate_complete_ignores_code_spans_and_custom_attributes`,
  the lab-tracker eval fixture (via `python check.py`).

## Done criteria

- [ ] `grep -c "lifecycle_status NOT IN ('Superseded','Obsolete')" plugins/tamheed/server/tamheed_server.py` → `2`
- [ ] `python tests/test_mcp_contract.py` → `OK`, one more test than before
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- `_scan_markers` or the placeholder scan no longer look like the excerpts (drift).
- `python check.py` reports the lab-tracker eval assertion about the surviving marker failing
  — the fixture's marker row would then be Superseded/Obsolete, which contradicts the
  fixture's own description; report, don't edit the fixture.
- The regression test cannot be made to fail before the fix (it isn't measuring the scan).

## Maintenance notes

- Two scanners, one rule: any future "which rows does G-COMPLETE read" change must be applied
  to both `_scan_markers` and the placeholder loop in `gate_run`. A reviewer should diff the
  two `where` expressions.
- The readiness `open-markers` advisory now also ignores history rows — correct (an operator
  cannot act on them), and worth one line in the release note when this ships.
