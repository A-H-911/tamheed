# Plan 066: `server_info` reports the package row; `detail=true` lists the vocabulary

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (additive read fields)
- **Category**: read surface (findings_25 s3) - **Planned at**: commit `d54b989`

## Why this matters

findings_25 s3: `packages` is not an entity family, so the stored package row - name, version,
iteration, go/no-go - was reachable through no tool. Under an MCP-exclusive read rule it was
unverifiable, and an earlier field note called the package header "unfixable by any tool".
Separately, ACMP's export reader carries a hand-built 28-entry family map "obtained by asking
`entity_query` for a type that does not exist and reading the 37 it names back", and its memory
records that for relation rules "the error is the only documentation".

## What changed

- `server_info()` always carries `package`: the stored row (`name, title, profile, mode,
  iteration, package_version, go_no_go, entry_point`) with a package open, `null` otherwise.
  The docstring says the stored `name` is descriptive only - a package resolves by directory.
- `server_info(detail=true)` adds `entity_types` (`type`, `table`, `id_prefix` for every
  queryable family) and `relation_rules` (`from` / `to` endpoint types per relation, sorted
  lists; `SAME_TYPE` spelled out). Default payload stays lean.

Additive top-level keys only. The vocabulary makes a client-side family map unnecessary if a
consumer adopts it; nothing here removes anything a consumer relies on.

## Tests

`test_server_info_reports_the_package_row_and_detail_lists_the_vocabulary`: the row and its
keys; lean default; `entity_types` equals the queryable set with table and prefix; every
relation present, `mitigates -> risk`, `supersedes` as `SAME_TYPE`; the payload is plain JSON;
`package` is null with nothing open. RED (KeyError) before, GREEN after.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (147)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
