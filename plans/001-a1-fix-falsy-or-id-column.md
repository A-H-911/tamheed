# Plan 001 (A1): Fix the falsy-`or` ID-column bug in three validator gates

> **Executor instructions**: Follow this plan step by step. Run every verification command and
> confirm the expected result before moving to the next step. If anything in the "STOP conditions"
> section occurs, stop and report — do not improvise. When done, update the status row for this
> plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat 0e055f6..HEAD -- plugins/keystone/scripts/validate_package.py tests/test_validate_package.py`
> If either file changed since this plan was written, compare the "Current state" excerpts against
> the live code before proceeding; on a mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

`validate_package.py` is the mechanical quality gate that declares a generated package READY. In
three gates the ID column of a Markdown table is located with
`table.col_index(ID_HEADERS) or _guess_id_column(table)`. `col_index` returns the **index** of a
matching header — which is `0` when the ID column is the first column. `0` is falsy in Python, so
the correct answer is discarded and a heuristic guess runs instead. Keystone's own templates put
`ID` in the first column (e.g. `plugins/keystone/templates/functional-requirements.template.md:25`
is `| ID | Statement | Source | Priority | Status |`), so this hits the *default* document shape.
When the heuristic then fails (any table whose ID cells aren't ≥60% clean ID tokens), the whole
table is silently skipped and its gate passes — a defective package validates as READY. This is a
false-pass path in the tool whose only job is to be trustworthy. It also gates the upcoming v1→v2
package migration (see `plans/README.md`), which requires v1 packages to validate correctly first.

## Current state

Files:

- `plugins/keystone/scripts/validate_package.py` — the validator (stdlib-only, Python 3.9+). All
  changes in this plan are in this file plus its test suite.
- `tests/test_validate_package.py` — self-test, run directly with Python (NO pytest — this repo is
  deliberately stdlib-only; do not add any dependency or pytest-style tests).

The three defective sites (verbatim at `0e055f6`):

```python
# validate_package.py:578  (inside gate_dec_status, per-table loop)
            id_col = table.col_index(ID_HEADERS) or _guess_id_column(table)

# validate_package.py:626  (inside gate_req_src, per-table loop)
            id_col = table.col_index(ID_HEADERS) or _guess_id_column(table)

# validate_package.py:785  (inside gate_trace, per-table loop)
            req_col = table.col_index(ID_HEADERS) or _guess_id_column(table)
```

The correct idiom already used elsewhere in the SAME file (this is the pattern to copy):

```python
# validate_package.py:437-440 (gate_ids)
            id_col = table.col_index(ID_HEADERS)
            if id_col is None:
                id_col = _guess_id_column(table)
            if id_col is None:
                continue
```

Supporting facts:

- `ID_HEADERS = {"id", "ref", "key", "identifier"}` — `validate_package.py:124`.
- `col_index` (`:179-184`) returns `Optional[int]`; `0` is a legitimate success value.
- `_guess_id_column` (`:349-368`) returns a column only when ≥60% of its non-empty cells
  `fullmatch` a governed ID token; messy-but-real cells (`FR-001 (see note)`, `DEC-001 / DEC-002`)
  make it return `None`.
- At `:626` and `:785` the assignment is immediately followed by `if id_col is None: continue`
  (resp. `if req_col is None: continue`) — keep those lines; only the assignment changes.
- At `:578` there is NO `continue` after the assignment — `gate_dec_status` deliberately proceeds
  (it can still flag a table via its Status column). Only replace the assignment; do not add a
  `continue` there.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Test suite | `python tests/test_validate_package.py` | exit 0, all tests pass |
| Golden pass | `python plugins/keystone/scripts/validate_package.py tests/fixtures/valid-package` | exit 0 |
| Golden pass | `python plugins/keystone/scripts/validate_package.py generated-samples/support-triage-agent` | exit 0 |
| Golden fail | `python plugins/keystone/scripts/validate_package.py tests/fixtures/invalid-package` | exit 1 |
| Golden fail | `python plugins/keystone/scripts/validate_package.py tests/fixtures/incomplete-package` | exit 1 |

## Scope

**In scope** (the only files you may modify):

- `plugins/keystone/scripts/validate_package.py` (three assignments only)
- `tests/test_validate_package.py` (add two tests)

**Out of scope** (do NOT touch):

- `_guess_id_column` itself — its heuristic limits are documented and deliberate.
- The correct-idiom sites (`:437-440`, `:930-934`, `:970-974`) — already right.
- Fixtures under `tests/fixtures/` and `generated-samples/` — goldens must stay byte-identical.
- Any `*.template.md` file.

## Git workflow

- Branch from `main`: `fix/validator-falsy-or-id-column`.
- One commit; message style follows repo convention (see `git log --oneline`), e.g.
  `fix: don't discard column-0 ID header match in G-DEC-STATUS/G-REQ-SRC/G-TRACE`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Replace the three assignments with the two-step idiom

At `:578`, `:626`, `:785`, replace the single `X or Y` assignment with (using the local variable
name already at each site — `id_col` at 578/626, `req_col` at 785):

```python
            id_col = table.col_index(ID_HEADERS)
            if id_col is None:
                id_col = _guess_id_column(table)
```

Keep the pre-existing `if ... is None: continue` lines at 626/785 exactly as they are. Add nothing
else at 578.

**Verify**: `python tests/test_validate_package.py` → exit 0 (existing suite must stay green) and
`grep -n "col_index(ID_HEADERS) or" plugins/keystone/scripts/validate_package.py` → no matches.

### Step 2: Add regression test — G-REQ-SRC no longer skips a first-column-ID table with messy cells

In `tests/test_validate_package.py`, add a test (model its structure after the existing negative
tests in the same file, e.g. `test_dec_status_defect_detected` around line 134, and use the file's
existing temp-package helper pattern). The test builds a package whose
`requirements/functional.md` contains exactly one table:

```markdown
| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| FR-001 (rev A) | The tool exports CSV. | | Must | Approved |
```

Assert that `gate_req_src` (or a full `run_gates` on the package) reports a **G-REQ-SRC** finding
(missing source). Rationale to encode in the test name/docstring: the header `ID` is column 0, so
`col_index` returns 0; before this fix `0 or _guess_id_column(...)` re-guessed, the messy cell
`FR-001 (rev A)` failed the guess, and the table was silently skipped. Other gates (e.g. G-IDS)
may also report findings on this input — assert the presence of the G-REQ-SRC finding, not an
exact total count.

**Verify**: `python tests/test_validate_package.py` → exit 0, including the new test. Temporarily
reverting Step 1 must make this test fail (fail-before/pass-after property — check it once, then
re-apply Step 1).

### Step 3: Add regression test — G-DEC-STATUS no longer misses a status-less decision table

Same file, second test. Package contains `decisions/open-decision-register.md` with exactly one
table that has NO Status column and a messy first-column ID:

```markdown
| ID | Decision | Rationale |
|---|---|---|
| DEC-001 / DEC-002 | Use a single storage table. | Simplicity. |
```

Assert a **G-DEC-STATUS** finding whose message contains `no Status column`. Before the fix:
`id_col` collapsed to `None`, `has_decision_ids` stayed False, `status_col` was None, and the gate
`continue`d — the missing Status column was never reported.

**Verify**: `python tests/test_validate_package.py` → exit 0, including this test.

### Step 4: Run the golden packages

**Verify**: all four golden commands from "Commands you will need" return their expected exit
codes. (Clean tables produce identical results before/after — the guess happened to return the
same index — so no golden output may change.)

## Test plan

Two new tests (Steps 2–3), both regression tests for the specific false-pass path, added to
`tests/test_validate_package.py` following its existing conventions (plain `unittest`, no pytest,
temp dirs cleaned up). No existing test may be modified.

## Done criteria

- [ ] `grep -n "col_index(ID_HEADERS) or" plugins/keystone/scripts/validate_package.py` → 0 matches
- [ ] `python tests/test_validate_package.py` → exit 0, test count increased by 2
- [ ] All four golden package runs return their expected exit codes
- [ ] `git status` shows only the two in-scope files modified
- [ ] `plans/README.md` status row for 001 updated

## STOP conditions

- The excerpts above don't match the live file (drift since `0e055f6`).
- Step 2's test does NOT fail when Step 1 is temporarily reverted — the reproduction is wrong;
  report instead of adjusting the test until it passes.
- Any golden package changes exit code after Step 1 — the fix changed behavior on clean input,
  which must not happen.

## Maintenance notes

- Any future gate that locates a table column must use the two-step `if x is None` idiom; `0` is a
  valid column index everywhere in this file. A reviewer should reject any new `col_index(...) or`
  expression.
- Deferred (deliberately): `_guess_id_column`'s best-ratio-across-all-columns behavior can still
  mis-pick a cleaner ID-like column in tables with NO recognized ID header. Lower priority once
  the header path works; noted in `plans/README.md` as a rejected finding.
