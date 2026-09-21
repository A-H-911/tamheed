# Plan 078: A completed hand-merge of a customised prompt is visible

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P3 - **Effort**: S - **Risk**: LOW (two reported fields; one warning narrows)
- **Category**: prompt library (findings_26) - **Planned at**: commit `6d877cf`

## Why this matters

findings_26: "`handoff_emit` cannot tell a completed hand-merge from a pending one."
`integrity-check.md` was hand-merged to 4.9.0 stock, verified, "and it still returns in
`diverged_customized` with `stock_last_changed: 4.9.0` and an unchanged warning ... nothing
records WHEN we merged, so the warning reads identically before and after the work."

## The heuristic I planned, and why the measurement rejected it

I first planned a line-containment test. Measured read-only against ACMP's own files: their
merged `integrity-check.md` is NOT a line-superset of stock (38 of 68 stock lines absent - the
customisation rewrites them), so the heuristic would have called the one file the plan exists
for "not merged". `slice-review.md` and `orient-resume.md` ARE supersets. So:

## What changed

Each `diverged_customized` entry gains two honest, independent signals:

- `stock_merged` - `"declared X.Y.Z"` when the file carries the line
  `<!-- tamheed:stock-merged X.Y.Z -->`, else `null`. The operator's CLAIM, reported as a claim,
  never as a verification. (findings_26's own remedy: "a merged-at marker the tool honours".)
- `contains_current_stock` - whether the file holds every line of the current stock body, in
  order. Mechanical, and true only for customisations that add rather than rewrite.

A file leaves the lag warning when it declares the release the stock last changed at, or
contains the current stock whole. The marker passes the injection screen and the stale scan
(the plan's open question, settled by the test).

## Tests

`test_a_completed_hand_merge_is_visible`: a rewritten file declaring the newest release, a
superset file with no marker, and a rewritten file declaring an old release -> only the last
stays in the lag warning; `handoff_emit` is `ok` with the markers present. RED before, GREEN
after. **One existing test changed deliberately:**
`test_stock_divergence_classified_customized` customised a prompt by APPENDING a line; such a
file contains the current stock whole and is, correctly, no longer lagging. It now rewrites a
stock line, so the lag claim it pins still applies.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (162)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
The prompt guide teaches the marker in plan 082.
