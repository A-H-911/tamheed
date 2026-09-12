# Plan 057: Order ids numerically in the review surface and sort stock-history versions numerically

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 673d1fa..HEAD -- plugins/tamheed/server/export_html.py plugins/tamheed/server/tamheed_server.py tests/test_export_html.py tests/test_mcp_contract.py CHANGELOG.md`
> On any change, compare excerpts; mismatch = STOP.

## Status

- **Priority**: P3
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (run after 054 if both are scheduled — same server file)
- **Category**: bug
- **Planned at**: commit `673d1fa`, 2026-09-12

## Why this matters

This repo has a recorded bug class: *string-ordered ids* (plans 025/027 — `_next_id` and
`_note_lessons_section` both carry comments about it). `_next_id` zero-pads to three digits,
so tool-minted ids sort correctly below 1000; but callers may supply their own ids (`PH-1`,
`WBS-12`, `ADR-0001`), and executed packages cross 999 progress entries. Eleven `ORDER BY`
clauses in `export_html.py` still sort by the raw id string — so the review surface shows
`PE-1000` before `PE-999`, `PH-10` before `PH-2`, and `WBS-1, WBS-10, WBS-2`. Separately,
`_emit_prompt_library` picks the release a customized prompt "matches" by sorting version
strings lexically (`"4.10.0" < "4.9.0"`), while the next branch of the same function sorts
numerically — the first mis-classification lands at 4.10.0. One SQL expression and one sort
key fix both; the goldens don't change because every fixture id is ≤ one digit or
three-digit padded.

## Current state

Line numbers at `673d1fa`.

- `plugins/tamheed/server/export_html.py` — the string-ordered sites:
  `:290`, `:365` (`entity_index ORDER BY id` — mixed prefixes), `:528`
  (`_registers`: `ORDER BY {cols[0]}` where `cols[0]` is `id`), `:553`, `:555`, `:579`
  (`ORDER BY ac.id`), `:602` (progress log), `:626`, `:634`, `:674`, `:690`. The numeric
  exemplar already in the file: `:472` `order = "ORDER BY CAST(SUBSTR(id, 4) AS INTEGER)"`
  (lessons, `LL-` fixed width). Trace edges (`ORDER BY from_id, to_id, relation`) and
  `phase_id`/`slice_id` orderings are out of scope.
- `plugins/tamheed/server/tamheed_server.py` `_emit_prompt_library` :2070–2093:

  ```python
            matches = next(
                (release for release, body in
                 sorted(history.get(src.name, {}).items(), reverse=True)
                 if body.replace("{package}", name) == on_disk), None)
            ...
                releases = sorted(history.get(src.name, {}),
                                  key=lambda v: tuple(int(p) for p in v.split(".")))
  ```

- Goldens: `generated-samples/support-triage-agent-v2/review.html`,
  `evals/sample-results/lab-tracker/package/{review.html,csv/*}`. Ids in the fixtures that
  are not 3-digit padded: `PH-1..3`, `WBS-1..3`, `ADR-0001..0004` — all single-digit or
  uniformly padded, so string order == numeric order and no golden bytes move.
- Tests: `tests/test_export_html.py` — `_open_demo_copy()`, determinism test
  (`test_two_exports_identical` or similarly named — find with `grep -n determin`),
  `test_execution_readiness_panel`. `tests/test_mcp_contract.py` —
  `test_stale_stock_classified_and_safely_refreshed`, `test_stock_divergence_classified_customized`
  (the `_emit_prompt_library` classification tests).

### Release discipline

- No `plugin.json` bump; CHANGELOG bullet under `## [Unreleased]` → existing `### Fixed`.
- No edits to version-stamped files, prompts, templates. Goldens must not change (verify);
  if they do, STOP.

## Commands you will need

| Purpose | Command | Expected |
|---|---|---|
| Viewer suite | `python tests/test_export_html.py` | `OK` |
| Contract suite | `python tests/test_mcp_contract.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Golden check | `git status --porcelain evals generated-samples` | empty |

## Scope

**In scope**: `plugins/tamheed/server/export_html.py`, `_emit_prompt_library` in
`plugins/tamheed/server/tamheed_server.py`, `tests/test_export_html.py`,
`tests/test_mcp_contract.py`, `CHANGELOG.md`, `plans/README.md` (row).

**Out of scope**: the CSV `ORDER BY` in `export_html()` (`tamheed_server.py`) — the CSVs are
import files, and changing them regenerates goldens for no reader benefit; `_next_id`;
`SUBSTR(id, 4)`/`(id, 5)` literals in `tamheed_server.py` (fixed-width prefixes, correct).

## Git workflow

- One commit: `fix: numeric id ordering in the review surface; numeric version sort in the prompt library (plan 057)`. Do NOT push.

## Steps

### Step 1: One ordering expression in `export_html.py`

Near the top of the module add:

```python
# Plan 057: ids order by (prefix, number) — string order breaks at PH-10 and PE-1000 (this
# repo's recorded bug class, plans 025/027). CAST of a non-numeric tail is 0, then `id`
# breaks the tie deterministically.
def _by_id(col: str = "id") -> str:
    return (f"SUBSTR({col}, 1, INSTR({col}, '-')), "
            f"CAST(SUBSTR({col}, INSTR({col}, '-') + 1) AS INTEGER), {col}")
```

Replace each in-scope `ORDER BY id` with `ORDER BY {_by_id()}` (f-strings), `ORDER BY ac.id`
with `ORDER BY {_by_id('ac.id')}`, and `_registers`' `ORDER BY {cols[0]}` with
`ORDER BY {_by_id(cols[0])}` **only when `cols[0] == "id"`** (keep the old form otherwise —
`_NON_ID_TABLES` have other first columns). Leave `:472` (lessons) as is or switch it to
`_by_id()` — either is correct; switching is cleaner.

**Verify**: `python tests/test_export_html.py` → `OK`; `git status --porcelain evals generated-samples`
→ empty after `python check.py` (the canonical/eval gates re-export nothing, but run it).

### Step 2: Numeric version sort in `_emit_prompt_library`

Define once at the top of the function `_vkey = lambda v: tuple(int(p) for p in v.split("."))`
and use it in both places: `sorted(history.get(src.name, {}).items(), key=lambda kv: _vkey(kv[0]), reverse=True)`
and `sorted(history.get(src.name, {}), key=_vkey)`.

**Verify**: `python tests/test_mcp_contract.py` → `OK`.

### Step 3: Tests

`tests/test_export_html.py`:

```python
    def test_ids_render_in_numeric_order(self):
        """Plan 057: PH-2 before PH-10; PE-999 before PE-1000."""
        self._open_demo_copy()
        out = srv.entity_upsert([{"type": "phase", "id": f"PH-{n}", "title": f"p{n}"}
                                 for n in (10, 2, 9)])
        self.assertTrue(out["ok"], out)
        html = Path(srv.export_html()["path"]).read_text(encoding="utf-8")
        self.assertLess(html.index("PH-2<"), html.index("PH-9<"))
        self.assertLess(html.index("PH-9<"), html.index("PH-10<"))
```

Adapt the `"PH-2<"` needle to how `_registers` renders an id cell (read the HTML once:
`grep -o 'PH-1[^a-z]\{0,12\}' review.html | head`) so the assertion locates the *cell*, not a
substring of another id. If existing demo phases collide with `PH-2`/`PH-9`/`PH-10`, pick
unused numbers.

`tests/test_mcp_contract.py`, beside `test_stock_divergence_classified_customized`:

```python
    def test_stock_history_versions_sort_numerically(self):
        """Plan 057: '4.10.0' is newer than '4.9.0' — never a lexical compare."""
        make_complete_package("demo")
        hist = srv._load_stock_history()
        fname, bodies = next(iter(hist.items()))
        body = next(iter(bodies.values()))
        with unittest.mock.patch.object(srv, "_load_stock_history",
                return_value={fname: {"4.9.0": body + "\n<!-- old -->\n",
                                      "4.10.0": body}}):
            out = srv._emit_prompt_library(srv.PACKAGE_ROOT / "demo", "demo")
        stale = [d for d in out.get("diverged_stale_stock", []) if d["file"].endswith(fname)]
        self.assertTrue(stale, out)
        self.assertEqual(stale[0]["matches"], "4.10.0")
```

If `_emit_prompt_library` reads the history through a different name than
`_load_stock_history`, patch that name (grep for `stock-history.json`). The point of the
test: the on-disk stock file equals the `4.10.0` body, so `matches` must be `4.10.0`, which
lexical `reverse=True` sorting would have reported as `4.9.0`. Verify it fails with Step 2
reverted.

**Verify**: both suites `OK`; `python check.py` → `ALL CHECKS PASSED`.

### Step 4: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- The review surface orders ids by (prefix, number) instead of as strings (`PH-10` sorted
  before `PH-2`, `PE-1000` before `PE-999`), and the prompt library's stale-stock
  classification compares release versions numerically (advisor plan 057).
```

## Done criteria

- [ ] `grep -c "_by_id(" plugins/tamheed/server/export_html.py` → ≥ 12 (def + ≥ 11 uses)
- [ ] `grep -n "ORDER BY id\b\|ORDER BY ac.id" plugins/tamheed/server/export_html.py` → nothing
- [ ] `grep -c "_vkey" plugins/tamheed/server/tamheed_server.py` → `3`
- [ ] Both suites `OK` (+1 each); `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status --porcelain evals generated-samples` → empty; `plans/README.md` row updated

## STOP conditions

- Any golden byte changes after `python check.py` — report the file; do not regenerate.
- A registers table whose `cols[0]` is `id` but whose ids have no `-` (INSTR = 0) — the
  expression still works (prefix `''`, CAST of the whole id), but report it.

## Maintenance notes

- New `ORDER BY` clauses on id columns in the viewer should use `_by_id()`; reviewers grep
  for `ORDER BY id`.
