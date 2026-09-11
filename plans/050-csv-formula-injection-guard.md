# Plan 050: Neutralize spreadsheet-formula cells in the exported CSVs

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` (section "Advisor audit 2026-09-10") — unless a reviewer
> dispatched you and told you they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 7e3a92b..HEAD -- plugins/tamheed/server/tamheed_server.py tests/test_export_html.py evals/sample-results/lab-tracker/package CHANGELOG.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none. Run after 044 if both are scheduled (same function).
- **Category**: security
- **Planned at**: commit `7e3a92b`, 2026-09-10

## Why this matters

`export_html` writes one CSV per table beside `review.html` "for the operator" — the review
surface links to them with `download`. Cells are written raw via `csv.writer`. Any stored
text beginning with `=`, `+`, `-`, `@`, or a tab/CR is interpreted as a formula when the
file is opened in Excel, LibreOffice or Google Sheets (`=HYPERLINK(...)`, `=cmd|' /C calc'!A0`
on older Excel with DDE enabled) — CSV/formula injection (CWE-1236). The package's text is
untrusted by SECURITY.md's own trust model (brief text, repository content, agent output),
and the CSV is the one emitted artifact a human opens in a spreadsheet. The standard
neutralization — prefix such cells with a single quote — is one helper and one `map`.
Because CSVs are committed goldens for the `lab-tracker` eval fixture, the plan also
regenerates them *by tool*, never by hand.

## Current state

- `plugins/tamheed/server/tamheed_server.py`
  - `import csv as _csv` (:22).
  - `export_html(output=None)` :2799–2836, the CSV loop (:2818–2834):

    ```python
        for table in sorted(set(ENTITY_TABLES.values())):
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            order = (...)
            rows = conn.execute(
                f"SELECT {', '.join(cols)} FROM {table} ORDER BY {order}").fetchall()
            if not rows:
                continue
            buf = io.StringIO()
            writer = _csv.writer(buf, lineterminator="\n")
            writer.writerow(cols)
            writer.writerows(rows)
            status = _managed_emit(csv_dir / f"{table}.csv", buf.getvalue(), force=True)
            csv_out[status].append(f"csv/{table}.csv")
    ```

    `rows` are sqlite tuples: ints stay `int`, `NULL` is `None`, text is `str`. Only `str`
    cells need the guard.
- `tests/test_export_html.py` — `ExportHtmlTest`; `_open_demo_copy()` opens a copy of the demo
  package; `test_csv_links_and_files` (~:275) reads `csv/requirements.csv` and checks the header.
  XSS fixtures at the top of the file show the hostile-content style
  (`XSS_SCRIPT = "<script>alert(1)</script>"` etc.).
- Goldens containing CSVs: `evals/sample-results/lab-tracker/package/csv/*.csv` (committed
  output of `export_html` on that fixture). At the planned commit,
  `grep -l '^[=+@-]\|,[=+@-]' evals/sample-results/lab-tracker/package/csv/*.csv` →
  `document_sections.csv` (a cell starting with `-`, a Markdown bullet). That file's bytes
  will change; `review.html` beside it must not.
- To regenerate the fixture's CSVs by tool (from the repo root):

  ```
  python -c "import sys,pathlib; sys.path.insert(0,'plugins/tamheed/server'); import tamheed_server as s; s.PACKAGE_ROOT=pathlib.Path('evals/sample-results/lab-tracker').resolve(); print(s.package_open('package')); print(s.export_html()['csv']); print(s.package_close())"
  ```

  `package_open`/`package_close` are byte-canonical (an idle open→close is a zero diff — the
  fixture asserts this itself), so only `csv/*.csv` may change. **Verified 2026-09-10 on a
  scratch copy of the fixture at `7e3a92b`:** open → `export_html()` → close reported
  `csv: {'emitted': 0, 'unchanged': 24, 'diverged': 0}` and `diff -rq` against the original
  was empty — the regeneration step moves only what the guard changes.

### Release discipline (this repo's `check.py` will fail you otherwise)

- Do NOT bump `plugins/tamheed/.claude-plugin/plugin.json` (lint 4).
- CHANGELOG note goes under `## [Unreleased]` (line 12), `### Fixed`.
- Do NOT edit the version string in the five version-stamped files.
- Do NOT touch `plugins/tamheed/prompts/*.md`.
- Goldens are regenerated **by the command above**, never hand-edited. Any diff outside
  `csv/*.csv` in the fixture is a STOP.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Viewer suite | `python tests/test_export_html.py` | `OK` |
| Full gate | `python check.py` | `ALL CHECKS PASSED` |
| Fixture diff | `git diff --stat -- evals/sample-results` | only `…/lab-tracker/package/csv/*.csv` lines |

## Scope

**In scope** (the only files you should modify):
- `plugins/tamheed/server/tamheed_server.py` — the CSV loop + one helper.
- `tests/test_export_html.py` — one test.
- `evals/sample-results/lab-tracker/package/csv/*.csv` — regenerated by tool only.
- `CHANGELOG.md` — `## [Unreleased]`.
- `plans/README.md` — your status row.

**Out of scope** (do NOT touch, even though they look related):
- `plugins/tamheed/server/export_html.py` — the HTML escapes through `esc()` already; the
  HTML surface is not the vector.
- The `ORDER BY` expressions, `_managed_emit`, the `force=True` semantics (C27/D2).
- `evals/sample-results/lab-tracker/package/data/**` and `review.html` — must not change.

## Git workflow

- `main` or a local branch `advisor/050-csv-guard`; one commit:
  `fix: neutralize formula-shaped cells in exported CSVs; regenerate lab-tracker csv goldens (plan 050)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: The helper and the map

Above `export_html` add:

```python
_CSV_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(value):
    """Plan 050 (CWE-1236): a text cell that a spreadsheet would evaluate as a formula is
    prefixed with a quote — the standard neutralization. Numbers/NULLs pass through."""
    if isinstance(value, str) and value.startswith(_CSV_TRIGGERS):
        return "'" + value
    return value
```

In the loop replace `writer.writerows(rows)` with
`writer.writerows([tuple(_csv_safe(v) for v in row) for row in rows])`.

**Verify**: `python tests/test_export_html.py` → `OK`.

### Step 2: Test

In `ExportHtmlTest`:

```python
    def test_csv_formula_cells_are_neutralized(self):
        """Plan 050: CWE-1236 — a title like =HYPERLINK(...) must not open as a formula."""
        self._open_demo_copy()
        hostile = ["=HYPERLINK(A1)", "+1+1", "-1-1", "@SUM(A1)"]   # no '"' — csv doubles them
        out = srv.entity_upsert([{"type": "risk", "id": f"RISK-9{i}", "title": t}
                                 for i, t in enumerate(hostile)])
        self.assertTrue(out["ok"], out)
        result = srv.export_html()
        text = (Path(result["path"]).parent / "csv" / "risks.csv").read_text(encoding="utf-8")
        for t in hostile:
            self.assertIn("'" + t, text)          # prefixed
            self.assertNotIn("," + t + ",", text)  # never raw at a cell boundary
        self.assertNotIn("'RISK-9", text)         # ids untouched
```

If `risk` rows require more columns than `id`/`title` (the error names them), add the minimal
ones — copy the shape from `test_gate_complete_flags_placeholders` in `tests/test_mcp_contract.py`
(`{"type": "risk", "id": "RISK-001", "title": "TODO fill this in"}` is the known-good minimum).

**Verify**: `python tests/test_export_html.py` → `OK`.

### Step 3: Regenerate the fixture CSVs by tool

Run the regeneration command from "Current state".

**Verify**: `git status --porcelain evals/sample-results` lists only files under
`evals/sample-results/lab-tracker/package/csv/`; `git diff -- evals/sample-results | grep '^[-+][^-+]' | head`
shows lines whose only change is a leading `'` on a cell. `python check.py` →
`ALL CHECKS PASSED` (the fixture's own byte-canonical assertion still holds — `data/` unchanged).

### Step 4: CHANGELOG

Under `## [Unreleased]` → `### Fixed`:

```markdown
- `export_html`'s per-table CSVs prefix cells beginning with `=`, `+`, `-`, `@`, tab or CR
  with a quote so a spreadsheet never evaluates stored text as a formula (CWE-1236); the
  lab-tracker fixture's `csv/` goldens were regenerated by the tool (advisor plan 050).
```

**Verify**: `python check.py` → `ALL CHECKS PASSED`.

## Test plan

- New: `test_csv_formula_cells_are_neutralized`.
- Existing: `test_csv_links_and_files`, the determinism test in the same file, and the
  lab-tracker fixture via `python check.py`.

## Done criteria

- [ ] `grep -c '_csv_safe' plugins/tamheed/server/tamheed_server.py` → `2`
- [ ] `python tests/test_export_html.py` → `OK`
- [ ] `git status --porcelain evals/sample-results` → only `…/package/csv/*.csv` entries
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status` shows only in-scope files
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The regeneration command changes anything under `…/lab-tracker/package/data/` or
  `review.html` — the fixture was already stale relative to the viewer; report the diff and
  do not commit it under this plan.
- `package_open('package')` on the fixture reports a lock or a refusal — report; do not
  delete `.lock` files by hand.
- Any other golden (`generated-samples/**`, other `evals/sample-results/*`) shows a diff.

## Maintenance notes

- Markdown bullets (`- item`) in long-text columns get a leading quote in the CSV. This is the
  known cost of the standard neutralization; the HTML view is the human surface, the CSV is
  for import. If a field complaint arrives, the alternative is to guard only `=`/`@` and
  `+`/`-` followed by a digit or `(` — narrower, still safe against the common payloads.
- Every future change to emitted CSV bytes needs Step 3 again; reviewers should expect a
  `csv/` diff in the fixture whenever the export loop changes.
