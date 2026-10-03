# Plan 181: lint 14, plain English, with a roster that grows per wave

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R3, R17, R26, R27, R29.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a wrong exempt set turns the gate red on a clean checkout) - **DONE** (2026-10-03)

## What this beat produces

A fourteenth lint in `check.py`, in the numbered-comment shape the guide parses:

- `_STE_SURFACES`: the roster, `(glob, mode, lang, skipped rules)` per entry. Every rostered
  file has zero hard findings at every commit. Day one: `references/vocabulary.md` (strict, the
  `vocabulary` rule skipped for that file).
- `_STE_PENDING`: the globs awaiting their wave, written from the enumeration this beat makes.
- `_STE_EXEMPT`: `server/ste_lint.py`, `THIRD-PARTY-NOTICES.md`, `lab/brief.md`,
  `lab/scenario.md`, `lab/seed/`, `evals/evals.json`, `plans/` (the 5.9.0 brief is rostered by
  path in beat 190), `CHANGELOG.md`, `docs/adr/`, `docs/history/`, `stock-history.json`,
  `evals/sample-results/`, `generated-samples/`, `tests/`, `__pycache__`, any path with a
  component that starts with `.`.
- Scope = `rglob("*.md") + rglob("*.py")` under the repository minus the exempt set, never
  `git ls-files` (the lint test runs the gate on a copy without `.git`). Roster + pending must
  equal the scope, else the lint fails naming the unplaced file.
- `content.py` is read by import from the repository under test (its `TEXT` values: EN flavored,
  AR flavored with `lang="ar"`). It is pending until wave 4b.
- The `lint:` line prints files, words, hard count (always 0), advisory counts, allow markers,
  pending surfaces.
- `docs/guide/content.py`: `lint.14` EN+AR; `checkgate.lint` says fourteen. `index.html` rebuilt.

## Validation
- Red: `tests/test_check_lints.py` gains six tests (a semicolon in a rostered file, a wrapped long
  sentence, a hedge-and-terms control that must pass, a semicolon inside a code span that must
  pass, an allow marker without a reason, a prose file in neither tuple) and raises the `lint:`
  floor to 13. They fail until the block exists.
- Red: six failures, then one: the probe for the neither case sat under `docs/`, which the pending glob `docs/*.md` legitimately covers. The test's premise was wrong, not the lint. The probe moved to the bundle root, which no glob covers.
- Green: `python check.py` ALL CHECKS PASSED. The whole lint gate (14 lints) ran in 1.7 s wall with one rostered file (709 words); lint 14's cost with the full roster is measured in beat 188.
- Enumeration at this commit: 91 prose files in scope, 1 rostered, 90 pending, 0 unplaced. The vocabulary file carries one advisory passive and one advisory present perfect, both legal.
