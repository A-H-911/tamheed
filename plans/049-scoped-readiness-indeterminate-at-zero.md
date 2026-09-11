# Plan 049: Phase/slice readiness rules report `indeterminate` when they measured nothing

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

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (053 builds on the same code region; run 049 first)
- **Category**: bug
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

The readiness engine has a doctrine for hollow passes (C34 §4, C35/N3): a rule that finds no
failing rows because it *measured nothing* reports `indeterminate` with
`discriminating: false` — "a loud amber", never a green. That doctrine is wired for the
`defects-closed`/`defects-minor` rules via `na_note()` (the `found_in`-unpopulated case), and
package scope has its own vacuous-pass warnings. But the three rules that carry the phase and
slice transition — `acs-met`, `wbs-done`, `slices-closed` — pass silently when the scope has
**no acceptance criteria, no work items, or no slices at all**. A slice with nothing bound to
it reads `ready: true`; the transition guard (which trips only on `fail`) lets it go
`Implemented`. That is the hollow-pass shape the maintainer locked as a deficiency, in the one
place it matters most. The fix follows the existing `na` mechanism exactly: count the
candidate population; if zero, pass an `na` note so `rule()` marks the entry indeterminate.
Doctrine stays intact — `indeterminate` never blocks (maintainer decision, plan 029), so this
changes what the operator *sees*, not what the guard refuses; the born-Implemented question
is plan 053.

## Current state

Line numbers below are at `7e3a92b`; earlier advisor plans (043–046) shift them by a few lines.
Compare the **excerpts**, not the numbers — a matching excerpt at a nearby line is not drift.

- `plugins/tamheed/server/tamheed_server.py`, `_readiness_report(conn, scope, scope_id)` :1441–1762.
  - The `rule()` helper (:1466–1500): `rule(name, severity, entities, note, na=None, extra=None)`.
    When `na` is truthy it sets `entry["discriminating"] = False`, and if `entities` is empty,
    `entry["status"] = "indeterminate"`. That is the whole mechanism — pass an `na` string.
  - The existing population probe (:1505–1511):

    ```python
    def na_note(table: str, column: str) -> str | None:
        total, populated = conn.execute(
            f"SELECT COUNT(*), COUNT({column}) FROM {table}").fetchone()
        if total and not populated:
            return (f" — 0 of {total} {table} rows have {column} set; this rule "
                    f"cannot discriminate (populate {column} to make it meaningful)")
        return None
    ```

  - Phase scope (:1679–1699) — the three rules, no `na`:

    ```python
    elif scope == "phase":
        rule("acs-met", "blocking",
             ids("SELECT ac.id FROM acceptance_criteria ac"
                 " JOIN slices s ON ac.slice_id = s.id"
                 " LEFT JOIN v_latest_verdicts lv ON lv.ac_id = ac.id"
                 " WHERE s.phase_id = ? AND ac.retired_in IS NULL"
                 " AND (lv.verdict IS NULL OR lv.verdict <> 'Met')", (scope_id,)),
             "ACs of this phase's slices whose latest verdict is not Met")
        rule("slices-closed", "blocking",
             ids("SELECT id FROM slices WHERE phase_id = ? AND retired_in IS NULL"
                 " AND lifecycle_status NOT IN"
                 " ('Implemented','Superseded','Obsolete','Rejected')", (scope_id,)),
             "slices of this phase not closed")
        rule("wbs-done", "blocking",
             ids("SELECT w.id FROM wbs_items w"
                 " LEFT JOIN slices s ON w.slice_id = s.id"
                 " WHERE (w.phase_id = ? OR s.phase_id = ?)"
                 " AND w.lifecycle_status NOT IN"
                 " ('Implemented','Superseded','Obsolete','Rejected')",
                 (scope_id, scope_id)),
             "open work items in this phase")
    ```

  - Slice scope (:1719–1730) — `acs-met` (`WHERE ac.slice_id = ? AND ac.retired_in IS NULL …`)
    and `wbs-done` (`WHERE slice_id = ? AND lifecycle_status NOT IN (…)`), same shape.
  - The `defects-closed` rules right after them show how `na=` is threaded:
    `found_na = na_note("defects", "found_in")` then `rule(..., na=found_na, extra=...)`.
- `tests/test_mcp_contract.py`
  - `test_readiness_vacuous_pass_reads_indeterminate` (~:475) — the exemplar for asserting
    `status == "indeterminate"`, `discriminating is False`, `entities == []`, and that `ready`
    reflects only real fails.
  - `test_readiness_phase_and_slice_scope` (~:451) — the scoped-rules exemplar
    (`make_complete_package("demo")`, then `srv.readiness_check("slice", id="SL-001")`).
  - `make_complete_package` seeds `PH-1`/`SL-001`/`AC-001`; a second phase/slice with nothing
    bound can be added with `entity_upsert` (`{"type": "phase", "id": "PH-2", "title": "later"}`,
    `{"type": "slice", "id": "SL-002", "title": "empty", "phase_id": "PH-2"}`).

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files.
- Do NOT touch `plugins/tamheed/prompts/*.md`; do NOT hand-edit goldens. The `lab-tracker`
  eval fixture runs `readiness_check`-derived assertions through `gate_run`/`pkg_check`;
  `python check.py` will tell you if a scoped rule's new status changes an assertion.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — inside `_readiness_report` only.
- `tests/test_mcp_contract.py` — one test.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- Package scope's rules — G-SET/omission rows already govern "a family is empty" there.
- The transition guard (`entity_upsert` :951–980) — `indeterminate` must keep *not* blocking
  (locked doctrine). Plan 053 is where born-Implemented is decided.
- The `rule()` helper's semantics and the `na_note` helper (add a sibling; don't change them).
- `export_html`'s readiness panel — it renders whatever statuses it gets.

## Git workflow

- `main` or a local branch `advisor/049-scoped-readiness-na`; one commit:
  `fix: phase/slice readiness rules read indeterminate at zero candidates (plan 049)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: A sibling probe for "nothing in scope"

Directly after `na_note`, add:

```python
    def empty_note(sql: str, params: tuple, what: str, how: str) -> str | None:
        """Plan 049: a scoped rule with NO candidate rows measured nothing — the
        C35/N3 hollow-pass doctrine, applied to phase/slice scope."""
        (n,) = conn.execute(sql, params).fetchone()
        if n == 0:
            return f" — no {what} in this scope; this rule cannot discriminate ({how})"
        return None
```

### Step 2: Thread it through the five scoped rules

Phase scope:

```python
        rule("acs-met", "blocking", ids(<existing query>, (scope_id,)),
             "ACs of this phase's slices whose latest verdict is not Met",
             na=empty_note("SELECT COUNT(*) FROM acceptance_criteria ac JOIN slices s"
                           " ON ac.slice_id = s.id WHERE s.phase_id = ?"
                           " AND ac.retired_in IS NULL", (scope_id,),
                           "active acceptance criteria",
                           "bind ACs to this phase's slices via slice_id"))
        rule("slices-closed", "blocking", ids(<existing>, (scope_id,)),
             "slices of this phase not closed",
             na=empty_note("SELECT COUNT(*) FROM slices WHERE phase_id = ?"
                           " AND retired_in IS NULL", (scope_id,),
                           "slices", "create SL- rows with phase_id"))
        rule("wbs-done", "blocking", ids(<existing>, (scope_id, scope_id)),
             "open work items in this phase",
             na=empty_note("SELECT COUNT(*) FROM wbs_items w LEFT JOIN slices s"
                           " ON w.slice_id = s.id WHERE w.phase_id = ? OR s.phase_id = ?",
                           (scope_id, scope_id),
                           "work items", "create WBS- rows with phase_id or slice_id"))
```

Slice scope:

```python
        rule("acs-met", "blocking", ids(<existing>, (scope_id,)),
             "ACs bound to this slice whose latest verdict is not Met",
             na=empty_note("SELECT COUNT(*) FROM acceptance_criteria WHERE slice_id = ?"
                           " AND retired_in IS NULL", (scope_id,),
                           "active acceptance criteria", "bind ACs to this slice via slice_id"))
        rule("wbs-done", "blocking", ids(<existing>, (scope_id,)),
             "open work items in this slice",
             na=empty_note("SELECT COUNT(*) FROM wbs_items WHERE slice_id = ?", (scope_id,),
                           "work items", "create WBS- rows with slice_id"))
```

Keep the existing `ids(...)` queries byte-for-byte; only the `na=` argument is new.

**Verify**: `python tests/test_mcp_contract.py` → `OK` (existing scoped tests have populated
scopes, so nothing changes for them).

### Step 3: Regression test

In `McpContractTest`, after `test_readiness_vacuous_pass_reads_indeterminate`:

```python
    def test_scoped_readiness_reads_indeterminate_when_scope_is_empty(self):
        """Plan 049: a slice/phase with no ACs, work items, or slices measured nothing —
        loud amber, never a green; `ready` is untouched (indeterminate never blocks)."""
        make_complete_package("demo")
        out = srv.entity_upsert([{"type": "phase", "id": "PH-2", "title": "later"},
                                 {"type": "slice", "id": "SL-002", "title": "empty",
                                  "phase_id": "PH-2"}])
        self.assertTrue(out["ok"], out)
        sl = {r["rule"]: r for r in srv.readiness_check("slice", id="SL-002")["rules"]}
        for name in ("acs-met", "wbs-done"):
            self.assertEqual(sl[name]["status"], "indeterminate", (name, sl[name]))
            self.assertIs(sl[name]["discriminating"], False)
            self.assertEqual(sl[name]["entities"], [])
        ph = {r["rule"]: r for r in srv.readiness_check("phase", id="PH-2")["rules"]}
        for name in ("acs-met", "wbs-done"):
            self.assertEqual(ph[name]["status"], "indeterminate", (name, ph[name]))
        self.assertEqual(ph["slices-closed"]["status"], "fail")     # SL-002 is open: real
        # populated scope is unaffected
        live = {r["rule"]: r for r in srv.readiness_check("slice", id="SL-001")["rules"]}
        self.assertNotEqual(live["acs-met"]["status"], "indeterminate")
```

**Verify**: `python tests/test_mcp_contract.py` → `OK`; revert Step 2 temporarily and confirm
the new test fails on the first `assertEqual(..., "indeterminate")`, then re-apply.

### Step 4: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- Phase/slice readiness: `acs-met`, `wbs-done` and `slices-closed` now report
  `indeterminate` (discriminating: false) when the scope holds no candidate rows, instead
  of a silent pass — the C35/N3 hollow-pass doctrine applied to the rules that carry the
  transition; `ready` and the transition guard are unchanged (indeterminate never blocks)
  (advisor plan 049).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_scoped_readiness_reads_indeterminate_when_scope_is_empty`.
- Existing that must stay green: `test_readiness_phase_and_slice_scope`,
  `test_readiness_vacuous_pass_reads_indeterminate`, `test_readiness_says_when_it_cannot_discriminate`,
  `test_transition_guard_*`, `test_forced_transition_records_typed_audit`,
  `test_readiness_slice_reports_unlocated_defects`.
- `python check.py` (lab-tracker fixture) → `ALL CHECKS PASSED`.

## Done criteria

- [ ] `grep -c 'empty_note(' plugins/tamheed/server/tamheed_server.py` → `6` (1 def + 5 uses)
- [ ] `python tests/test_mcp_contract.py` → `OK`, one more test than before
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The scoped rule blocks don't match the excerpts (drift).
- `python check.py` fails on a lab-tracker or execution-loop eval assertion — a fixture scope
  is empty and the recorded expectation was the silent pass; report which assertion, do not
  edit the fixture or the eval spec.
- You are tempted to make `indeterminate` block the transition — that is plan 053's question
  and a locked doctrine; do not.

## Maintenance notes

- Any new scoped blocking rule should take an `na=empty_note(...)` — reviewers should ask
  "what does this rule say when the scope is empty?".
- Plan 053 (born-Implemented) sits in `entity_upsert`, not here; after both land, a brand-new
  slice going straight to `Implemented` is refused by 053, and an existing empty slice shows
  amber from this plan — two different questions, deliberately.
