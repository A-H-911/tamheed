# Plan 067: An export file describes itself; slate currency is a boolean

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (additive envelope keys, one optional argument)
- **Category**: read surface (the field's export consumers) - **Planned at**: commit `6e319ed`

## Why this matters

ACMP's shared export reader documents both gaps in its own comments. (1) "The file's `result`
carries ok/count/total/next_after but NOT `partial` - that field is on the tool's return value
only ... asserting `partial === false` here would be a check that can never pass", so it
hand-rolls a three-clause short-read guard. (2) Every generated slate ends "run
`package_verify()`; the same digest means nothing has changed" - currency checked by a human
comparing two hex strings, and because the digest is package-wide ANY later write (a
`progress_update` included) silently stales the slate.

## What changed

- `entity_export`: when the inner result is a row result, the `tamheed_export` envelope carries
  `count`, `total`, `partial`. The file stays deterministic (no clock); non-row tools
  (`gate_run`, `readiness_check`, ...) get no such keys.
- `package_verify(expect=<digest>)` adds `matches_expected`. Absent unless asked. A mismatch
  means STALE, not damaged: `verified` is independent of it.

## Tests

`test_export_file_describes_itself_and_verify_answers_currency`: a `limit=1` export of two
defects reads `(1, 2, True)` in the FILE; the full export `(2, 2, False)`; a second export is
byte-identical; a `gate_run` export has no `partial`; `expect` matches, then one upsert makes it
`False` while `verified` stays `True`. RED (KeyError) before, GREEN after.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (148)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
The lab fixture's committed exports are rewritten only by beat 16's own re-export.
