# Plan 053: Refuse a phase or slice that is *born* `Implemented` unless the operator forces it

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_mcp_contract.py plugins/tamheed/references/governance.md plugins/tamheed/templates/governance.template.md CHANGELOG.md`
> Plans 043, 049 and 051 edit `tamheed_server.py` first — expect diffs; the transition-guard
> block quoted below must still read as quoted. On a mismatch, treat it as a STOP condition.

## Status

- **Priority**: P3
- **Effort**: S
- **Risk**: MED (a tool-contract change: a previously legal write becomes a refusal; the
  maintainer confirmed the decision on 2026-09-10)
- **Depends on**: 049 (same code region; 049 makes an empty scope *visible*, this plan makes a
  brand-new row *refusable*), 043 (transaction tail settled).
- **Category**: bug
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

Declaring a phase or slice `Implemented` is guarded (plan 027, maintainer-locked): the blocking
readiness rules must pass, or the operator writes `"force": true` and the server journals a
typed `forced-override` audit row. The guard runs on the *transition edge* — "current status is
not Implemented, new status is Implemented" — and the code treats a row that does not exist yet
(`current is None`) as an edge. But the readiness report it then runs is for a scope id with
**no rows bound to it** (the row is being created in this very statement), so every blocking
rule finds nothing and passes; after plan 049 they read `indeterminate`, which by locked
doctrine never blocks. Net effect: `entity_upsert([{"type": "slice", "id": "SL-009", …,
"lifecycle_status": "Implemented"}])` on a new id is accepted with no blockers, no force, no
audit row — the guard is bypassed by the one write shape it cannot measure. The maintainer's
own future-options note records the adjacent case (an AC born on an Implemented slice) as an
open question; for phases and slices the maintainer decided on 2026-09-10 to **refuse** the
born-Implemented write unless forced. `force` keeps its meaning (operator words, self-audited),
so brownfield/adoption flows that genuinely need a done-on-arrival phase still have a route.

## Current state

- `plugins/tamheed/server/tamheed_server.py`, `entity_upsert`, the transition guard (:950–980):

  ```python
        forced_note = None
        if (etype in ("phase", "slice") and cols.get("id")
                and cols.get("lifecycle_status") == "Implemented"):
            # Plan 027 (maintainer decision): declaring a phase/slice DONE is guarded
            # by the blocking readiness rules. Transition-edge detection: a full-row
            # re-upsert of an ALREADY-Implemented row must not re-fire (entity_upsert
            # requires FULL rows even for updates). Rejected/Obsolete/… are never
            # guarded — only the success-terminal status is a claim of completion.
            current = conn.execute(f"SELECT lifecycle_status FROM {table} WHERE id = ?",
                                   (cols["id"],)).fetchone()
            if current is None or current[0] != "Implemented":
                rep = _readiness_report(conn, etype, cols["id"])
                blockers = [r for r in rep["rules"]
                            if r["severity"] == "blocking" and r["status"] == "fail"]
                if blockers and not force:
                    detail = "; ".join(...)
                    results.append({
                        "index": i, "ok": False, "id": cols["id"],
                        "error": f"readiness: {cols['id']} cannot transition to"
                                 f" Implemented — {detail} — resolve the blockers, or"
                                 " re-run this item with \"force\": true after EXPLICIT"
                                 " operator confirmation"})
                    failed = True
                    continue
                if blockers:  # forced past blocking failures: the record is automatic
                    forced_note = "; ".join(
                        f"{r['rule']} ({len(r['entities'])})" for r in blockers)
  ```

  Later (:1084–1097), when `forced_note` is set, the server inserts a `progress_entries` row
  with `event_type = "forced-override"`, `actor = "system:transition-guard"`, and puts
  `res["forced"] = True`, `res["forced_audit"] = pe_id` on the item result. The text of that
  entry is `f"FORCED transition: {cols['id']} -> Implemented past blocking readiness failures ({forced_note}) — operator-confirmed override"`.
- `force` is parsed at :857 (`force = bool(item.get("force"))`) and stripped from `cols`.
- Tests (`tests/test_mcp_contract.py`):
  - `test_transition_guard_edge_detection` (~:503) — asserts a `Rejected` new slice is accepted,
    a re-upsert of an Implemented row does not re-fire, and wbs-items are unguarded. It creates
    `SL-002` with `Rejected`, never with `Implemented` — unaffected.
  - `test_forced_transition_records_typed_audit` (`V4EngineTest`) — the forced path; the
    assertion pattern for the audit row (`event_type == "forced-override"`, `actor ==
    "system:transition-guard"`) is the one to copy.
  - `V4EngineTest.setUp` creates `PH-1` (`Approved`) and `SL-001` (`Approved`) — neither is
    born Implemented, so the seed is unaffected.
- `plugins/tamheed/references/governance.md` documents the transition guard in prose;
  `plugins/tamheed/templates/governance.template.md` is its "necessary copy" (lint 11 checks
  needles, not this sentence). `grep -n 'Implemented' plugins/tamheed/references/governance.md`
  finds the guard paragraph.
- Migration (`migrate_v3to4.transform_tables`) and adopt write rows directly / as `Proposed`,
  not through this guard; the lab fixture and eval fixtures create phases/slices `Approved`
  and transition them later (`grep -rn '"lifecycle_status": "Implemented"' evals/*.json lab/`
  before you start — see STOP conditions).

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Changed` (contract change).
- Do NOT edit the version string in the five version-stamped files.
- `governance.md` is a bundle prose file: lint 9b (vocabulary) and lint 10 (paths) apply —
  the sentence you add names only `force`, `Implemented`, `entity_upsert`, all existing vocabulary.
- Do NOT touch `plugins/tamheed/prompts/*.md`; goldens unchanged.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Fixture scan | `grep -rn 'Implemented' evals/evals.json lab/ --include='*.json' --include='*.md' \| grep -i 'born\|create' ` | (informational) |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — the guard block only.
- `tests/test_mcp_contract.py` — one test.
- `plugins/tamheed/references/governance.md` — one sentence in the guard paragraph.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- Acceptance criteria born on an Implemented slice — recorded open question, not decided.
- `wbs-item` rows — never guarded (locked).
- The readiness rules, `force` semantics, the audit-row shape.
- `governance.template.md` — lint 11 needles unaffected; leave the template alone unless the
  governance paragraph you edit is mirrored verbatim there (check with `grep -n 'transition' plugins/tamheed/templates/governance.template.md`; if it is, apply the same sentence).

## Git workflow

- `main` or a local branch `advisor/053-born-implemented`; one commit:
  `feat: refuse a phase/slice born Implemented unless forced (plan 053)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Refuse the born-Implemented write, keep `force`

Inside the guard, replace `if current is None or current[0] != "Implemented":` and its body
with two branches — new row first:

```python
            if current is None:
                # Plan 053 (maintainer decision 2026-09-10): a row cannot be BORN done —
                # the readiness rules have nothing to measure for an id that does not
                # exist yet, so the guard was bypassed by exactly this write shape.
                if not force:
                    results.append({
                        "index": i, "ok": False, "id": cols["id"],
                        "error": f"readiness: {cols['id']} cannot be created as"
                                 " Implemented — create it (Proposed/Approved), bind its"
                                 " work, then transition; or re-run this item with"
                                 " \"force\": true after EXPLICIT operator confirmation"})
                    failed = True
                    continue
                forced_note = "born-Implemented (no readiness measured)"
            elif current[0] != "Implemented":
                rep = _readiness_report(conn, etype, cols["id"])
                ... (the existing body, unchanged)
```

The existing forced-audit insertion (:1084–1097) fires for the new `forced_note` unchanged —
its entry text will read `FORCED transition: SL-009 -> Implemented past blocking readiness
failures (born-Implemented (no readiness measured)) — operator-confirmed override`. Good
enough; do not reword the audit template.

**Verify**: `python tests/test_mcp_contract.py` → `OK` (no existing test creates a phase/slice
as Implemented without `force`; if one fails, see STOP conditions).

### Step 2: Regression test

In `V4EngineTest`, after `test_forced_transition_records_typed_audit`:

```python
    def test_phase_or_slice_born_implemented_is_refused_unless_forced(self):
        """Plan 053: readiness measures nothing for an id that does not exist yet."""
        for etype, row in (("phase", {"id": "PH-9", "title": "done on arrival"}),
                           ("slice", {"id": "SL-009", "title": "done on arrival",
                                      "phase_id": "PH-1"})):
            refused = srv.entity_upsert([dict(row, type=etype,
                                              lifecycle_status="Implemented")])
            self.assertFalse(refused["ok"], refused)
            self.assertIn("cannot be created as Implemented", refused["items"][0]["error"])
            self.assertEqual(srv.entity_query(etype, id=row["id"])["rows"], [])  # nothing landed
            forced = srv.entity_upsert([dict(row, type=etype,
                                             lifecycle_status="Implemented", force=True)])
            self.assertTrue(forced["ok"], forced)
            pe_id = forced["items"][0]["forced_audit"]
            pe = [r for r in srv.entity_query("progress-entry")["rows"] if r["id"] == pe_id][0]
            self.assertEqual(pe["event_type"], "forced-override")
            self.assertEqual(pe["subject_id"], row["id"])
            self.assertIn("born-Implemented", pe["entry"])
        # unguarded shapes stay legal: Approved on arrival, Rejected on arrival, wbs-items
        ok = srv.entity_upsert([{"type": "slice", "id": "SL-010", "title": "s",
                                 "phase_id": "PH-1", "lifecycle_status": "Approved"},
                                {"type": "wbs-item", "id": "WBS-9", "title": "w",
                                 "slice_id": "SL-001", "lifecycle_status": "Implemented"}])
        self.assertTrue(ok["ok"], ok)
```

If `entity_query(etype, id=…)` returns an error dict for an unknown id rather than an empty
`rows` list, assert on that error instead (the intent: the refused row did not land).

**Verify**: `python tests/test_mcp_contract.py` → `OK`; revert Step 1 temporarily and confirm
the test fails on `assertFalse(refused["ok"])`, then re-apply.

### Step 3: Governance prose + CHANGELOG

- `plugins/tamheed/references/governance.md`: in the paragraph that describes the
  phase/slice → `Implemented` guard, add one sentence: *"A phase or slice cannot be created
  already `Implemented` — the rules have nothing to measure for a new id; `force` (operator
  words, self-audited) is the only route."* Mirror it in `governance.template.md` only if that
  paragraph is copied there verbatim.
- `CHANGELOG.md` under `## [Unreleased]` → `### Changed`:

  ```markdown
  - `entity_upsert` refuses a phase or slice created directly as `Implemented` — the
    transition guard ran readiness for an id with nothing bound and passed vacuously;
    `"force": true` (operator-confirmed, journaled as `forced-override`) remains the route
    for done-on-arrival rows (advisor plan 053; maintainer decision 2026-09-10).
  ```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_phase_or_slice_born_implemented_is_refused_unless_forced`.
- Existing: `test_transition_guard_edge_detection`, `test_transition_guard_refuses_then_forces_with_audit`,
  `test_forced_transition_records_typed_audit`, `test_templates_teach_v4_recording`
  (governance prose is part of the teaching surface), all eval fixtures via `python check.py`.

## Done criteria

- [ ] `grep -c 'cannot be created as Implemented' plugins/tamheed/server/tamheed_server.py` → `1`
- [ ] `python tests/test_mcp_contract.py` → `OK`, one more test than before
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `grep -c 'cannot be created already' plugins/tamheed/references/governance.md` → `1`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The guard block does not read as quoted (drift from 049/043 — re-locate by the comment
  `Plan 027 (maintainer decision)` and proceed only if the logic is identical).
- Any existing test, eval fixture (`python check.py`), or `lab/` scenario creates a phase or
  slice as `Implemented` without `force` — that is a legitimate flow the decision did not
  anticipate; report it before changing the fixture or the rule.
- `test_templates_teach_v4_recording` fails after the governance edit — the template mirror
  is checked by that test; apply the same sentence to `governance.template.md` and re-run;
  if it still fails, report.

## Maintenance notes

- This is the first refusal on a *create*; reviewers should confirm the error text names the
  remedy (create → bind → transition, or force) — plan 040's doctrine: a remedy named by a
  refusal must be an operation the server exposes. Both are.
- The adjacent open question (an AC born on an Implemented slice) stays recorded in
  `plans/README.md` "Future options"; if it is ever decided, the same two-branch shape applies
  in the AC path with the `SC-` linkage check the note describes.
