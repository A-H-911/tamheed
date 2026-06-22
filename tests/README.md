# Keystone tests — package validator

This directory holds the **mechanical quality-gate validator** for
Keystone-generated packages and its self-test, both stdlib-only (Python 3.9+,
no pytest, no third-party deps).

## Running

Validate a generated package (human-readable report):

```
python tests/validate_package.py <package-dir>
```

Machine-readable summary (for CI / wrappers):

```
python tests/validate_package.py <package-dir> --json
```

Help:

```
python tests/validate_package.py --help
```

Run the self-test (validates both fixtures and asserts behaviour):

```
python tests/test_validate_package.py
```

Exit codes for `validate_package.py`: `0` = all critical gates pass; `1` = at
least one **Critical** gate failed (package is NOT READY); `2` = usage / IO
error (e.g. the package directory does not exist).

## Coverage

The suite is **stdlib-only** — there is no `coverage.py` dependency. Measure line coverage with the
standard-library `trace` module:

```
python -m trace --count --summary --coverdir=.cov tests/test_validate_package.py
```

Current state: **57 tests**, **100% line coverage** of both executable modules
(`plugins/keystone/scripts/validate_package.py` and `init_skill_repo.py`). Every Critical gate has both a
pass and a finding (negative) test; `G-PROGRESS` is covered in all three modes — PASS (audit covers every
`AC-`), FAIL (coverage gap, blank verdict, out-of-set verdict, or missing Verdict column), and SKIP (no
audit present). `trace` measures **line**, not **branch**, coverage; for branch metrics run
`coverage.py --branch` separately (it is intentionally not a project dependency).

> Heads-up: the gate table and run paths **below this point are stale** — they predate `G-SET`,
> `G-PROGRESS`, and the plugin restructure. The validator now lives at
> `plugins/keystone/scripts/validate_package.py`, there are **seven** Critical gates, and there are three
> fixtures (incl. `incomplete-package/`). See `CLAUDE.md` and
> `plugins/keystone/references/quality-gates.md` for the current set.

## What each gate checks

The validator implements the *mechanical* subset of the gates defined in
`../skill/references/quality-gates.md`. All five are **Critical** — any failure
makes the package NOT READY.

| Gate | Checks |
|---|---|
| **G-IDS** | Identifiers match the `governance.md` formats (FR-NNN, ADR-NNNN, WBS-N.N[.N], …); each is defined only once within its directory family; and every referenced identifier is defined somewhere (no dangling cross-references). Malformed identifiers (right prefix, wrong number format, e.g. `FR-7`) are flagged. |
| **G-DEC-STATUS** | Every `DEC-` row, ADR index row, and standalone ADR document carries an explicit status from the allowed set (Proposed / Approved / Rejected / Superseded / Deferred, plus Accepted / Implemented / Obsolete / Draft for ADR docs). Empty or out-of-set statuses fail. |
| **G-REQ-SRC** | Every `FR-`/`NFR-` row has a non-empty Source / Provenance / Origin (a dash or `n/a` counts as empty). A requirements table with no source column fails. |
| **G-COMPLETE** | No non-template artifact contains an unfinished marker (`TODO`, `TBD`, `FIXME`, `XXX`, `<placeholder>`, `{{…}}`, FILL-IN, LOREM IPSUM) or an empty section (a heading with no body and no child headings). Empty files fail. Code fences/inline code are stripped first so examples aren't misread. |
| **G-TRACE** | In the traceability matrix, every MVP `FR-`/`NFR-` row links to ≥1 decision, ≥1 work item, and ≥1 test. Empty required cells, or a matrix missing one of those columns, fail. Rows marked full-only/later/post-mvp in a scope column are skipped. |

The remaining gates from `quality-gates.md` (the Warn gates, and the
partly-mechanical Criticals G-CONFLICT / G-EXEC / G-HANDOFF / G-OQ) are
judgment checks recorded by a human or agent in the validation report; they are
intentionally **out of scope** for this script.

A gate shown as `SKIP` found no applicable inputs (e.g. no traceability matrix
present yet) — that is neither a pass nor a fail; whether an artifact is
required at all is governed by the artifact-selection rules, not the validator.

### Assumptions / heuristics

The input is semi-structured Markdown optionally mirrored by JSON. The parser
handles GitHub-style pipe tables and flat front-matter only (no nested YAML,
HTML tables, or pipes escaped inside cells). Identifier detection keys off the
governed prefixes; a project that invents a new prefix must add it to
`ID_PATTERNS` in `validate_package.py`. The module docstring and the inline
"Gate reference" comment at the foot of `validate_package.py` document the full
set of assumptions.

## Fixtures

Two tiny end-to-end packages live under `fixtures/`. They share the same shape
(a link-shortener example) so the only difference is the seeded defects.

### `fixtures/valid-package/`

A small but **valid** package that passes all five critical gates. It contains
correctly-linked artifacts: `00-charter.md` (with KPI metrics),
`requirements/functional.md` and `non-functional.md` (every requirement
sourced), `decisions/open-decision-register.md` and `open-question-register.md`
(every decision has a status), `adrs/adr-0001-single-table-storage.md`,
`planning/roadmap.md` and `work-breakdown.md`, `validation/acceptance-criteria.md`,
`test-strategy.md`, and `traceability-matrix.md` (every MVP requirement reaches
a decision, a work item, and a test), plus a `keystone-state.json` mirror.
Every cross-referenced identifier resolves to a definition.

### `fixtures/invalid-package/`

The same package with **seeded defects**, one per critical gate, annotated in
the file that owns each:

- **G-IDS** — `requirements/functional.md` references `DEC-099` (never defined,
  dangling) and contains a malformed `FR-7` token.
- **G-DEC-STATUS** — `decisions/open-decision-register.md` has a `DEC-002` row
  with an empty Status cell.
- **G-REQ-SRC** — `requirements/functional.md` has `FR-002` with an empty
  Source cell.
- **G-COMPLETE** — `00-charter.md` leaves a `TODO` and a `<placeholder>`.
- **G-TRACE** — `validation/traceability-matrix.md` has MVP requirement
  `FR-003` with an empty Tests cell.

The self-test asserts the valid package passes (exit 0, no critical findings)
and that the invalid package fails (exit 1) with each specific defect reported
by the right gate.

## Files

- `validate_package.py` — the validator (CLI + importable `run_gates` /
  `build_summary` API).
- `test_validate_package.py` — stdlib `unittest` runner; exercises the API and
  the CLI (exit codes, `--json`, `--help`) against both fixtures.
- `fixtures/valid-package/`, `fixtures/invalid-package/` — described above.

> Note: `_vp_probe.py` is a throwaway scratch file and is not part of the
> suite; it can be deleted.
