# Plan 094: The package header is written on the operator's word

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: MEDIUM (a write to governance state; security-reviewed)
- **Planned at**: `8567632`

## Why this matters (ACMP's `FB-001`)

`server_info().package` reads the header - `name`, `title`, `profile`, `mode`, `iteration`,
`package_version`, `go_no_go`, `entry_point` - and no tool wrote any of it. A package whose go/no-go
verdict changed had nowhere to record it; ACMP's still read "GO - MVP complete" from a moment long
past, and their memory said so ("unfixable by any tool" - true, and now a feedback row).

## What changed

`entity_upsert` accepts `{"type": "package", ...}`, special-cased BEFORE the `ENTITY_TABLES`
lookup (`_write_package_header`): the header is never a family - no register, no CSV, no registry
row, no index (revision 1 of the batch plan would have registered it and changed every field
package's review page; measured in `export_html._registers` and corrected). Writable: `title`,
`mode`, `iteration`, `mvp_definition`, `entry_point`, `go_no_go`. Frozen and refused by name:
`name`, `profile`, `package_version`, `created_at`, `custom_attributes`; naming the OPEN package is
allowed, another name refused. `go_no_go` is the governance verdict: a change is refused without
`operator_confirm` and, on the word, journaled by the engine (`transition`, `system:package-guard`,
returned as `package_audit`). `changed_columns` reports (keyed on `name`). The row's CHECKs (mode)
and NOT NULLs surface as per-item errors. `entity_query(type="package")` is refused with a message
naming `server_info().package` and the write.

## Security review, and what it changed

Three items. **MEDIUM:** `iteration INTEGER` is affinity, not a constraint - `'not-a-number'` would
have been stored and stamped onto every later verdict; the write now requires a real integer.
**LOW-MEDIUM:** the audit row was inserted after the item savepoint was released, so an I/O failure
there could leave the update applied and the witness missing; the row now shares the savepoint.
**MEDIUM (convention, codebase-wide):** `operator_confirm` was truthiness-checked everywhere, so a
string `"false"` attested; one helper, `_operator_word`, now requires the JSON boolean `true` on
every guard (lesson, feedback, header). No finding on guard bypass, SQL construction, injection
(header text never reaches the note; the page escapes every cell), or the round-trip.

## Lab beat 19's finding (fixed before release, `F-4`)

The first dispatch of beat 19 STOPPED at its first header write: `entity_upsert(type="package")`
raised `TypeError` on the recorded fixture. Root cause: the header row was keyed by the DIRECTORY
name (`_CURRENT_NAME`), but a package is resolved by its directory and its stored `name` may differ
(plan 066) - the lab fixture is `package` / `lab-tracker`, and the field's is `tamheed-package` /
`tamheed-package-v2`, so the crash would have reached ACMP on its first use. The suite never saw
it because every test package is made by `package_create`, where the two coincide. Fixed: the
header is the ONE row, read as `server_info` reads it; a sent `name` may be the stored name or the
directory; the pre-image is read before the error checks, so a refusal is a verdict, never a crash.
The test now flips the stored name and re-runs the write and the refusal.

## Tests

`test_the_package_header_is_written_on_the_operators_word`: three columns written and read back
through `server_info`; an unattended verdict refused and unchanged; a confirmed one journaled by
`system:package-guard` with `package_audit`; each frozen column refused by name; the open package's
own name accepted, another refused; `export_html` emits no `packages.csv`; the query refusal
points at `server_info`; a string `"false"` does not attest; a non-integer `iteration` refused. RED (unknown entity type) before, GREEN after; contract suite 169;
round-trip suite green (the header persists canonically).

## Done criteria

- [x] contract + round-trip suites OK
- [x] security reviewer: two MEDIUM + one LOW-MEDIUM found and closed before commit; no CRITICAL/HIGH
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
