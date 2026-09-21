# Plan 081: A stale review page is detectable

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [075-084-batch-findings-26.md](075-084-batch-findings-26.md).

## Status

- **Priority**: P3 - **Effort**: XS - **Risk**: LOW (`review.html` changes bytes once)
- **Category**: derived-output currency - **Planned at**: commit `31637a8`

## Why this matters

ACMP's standing rule: "GIT CLEAN != PACKAGE ARTIFACTS CURRENT: `review.html` and `csv/`
regenerate ONLY on `export_html`", with a commit in their history titled "review.html was stale
on origin while git was clean". The human surface can lag the store and nothing says so.

I rejected this in the 4.9.0 batch because I assumed it needed a render on every check. It does
not: if the export stamps the digest of the state it rendered, currency is a string comparison.

## What changed

- `export_html` inserts `<meta name="tamheed-digest" content="<sha256>">` before `<title>`: the
  digest of the open connection's canonical dump - the same value `package_verify` and
  `entity_export` report. Same state -> same digest, so two exports stay byte-identical.
- `package_verify` reports `review_current`: `true` / `false` against the on-disk digest, `null`
  when there is no page or no stamp (exported before 4.10.0). It reads the first 4 KB only, and
  never flips `verified`: stale is not damaged.

The digest is package-wide, so ANY write - a journal note included - stales the page. That is
the honest reading (the page no longer shows the journal), and it matches the currency rule the
field already applies to slates.

## Consequence, stated

Every package that tracks `review.html` sees a one-line diff on its next export. No lint or eval
assertion reads the stamp; lab beat 17 regenerates the lab fixture's page by tool.

## Tests

`test_a_stale_review_page_is_detectable`: `null` with no page; `true` after an export; two
exports byte-identical; `false` after one upsert while `verified` stays `true`; `true` again
after re-export; `null` for an unstamped page. RED (`KeyError`) before, GREEN after.
`tests/test_export_html.py` (37 tests, incl. byte-determinism) stays green.

## Done criteria

- [x] contract suite OK (161); export suite OK (37)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts untouched.
