# Plan 101: the header read is a superset of the write (FB-015)

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [100-105-batch-findings-29.md](100-105-batch-findings-29.md).

## Status

- **Priority**: P2 - **Effort**: XS - **Risk**: LOW (two more keys in a read; one optional key)

## Why this matters (ACMP's `FB-015`, findings_29 §5)

Plan 094 made six header columns writable; `server_info().package` reported eight and neither
`mvp_definition` (writable) nor `created_at` was among them — a caller could write a column it could
never read back except through the HTML page, which also annotates `(v1-manifest-derived)` where the
tool says nothing.

## What changes

`_PACKAGE_ROW` gains `mvp_definition` and `created_at`; when `custom_attributes` carries
`v1_manifest` (the page's own predicate) the block carries `v1_manifest_derived: ["mode", "profile",
"created_at"]`. Server README row; `docs/entities.md` header paragraph.

## Done criteria

- [ ] RED then GREEN (`:2810` extended to ten keys; the seeded annotation; absent on a fresh package)
- [ ] `python check.py`; dry-run on a fixture copy (write `mvp_definition`, read it back)
- [ ] CI green
