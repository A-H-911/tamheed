# Plan 070: `prose-ids-resolve` - an advisory for references that resolve to nothing

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md). Depends on 069.

## Status

- **Priority**: P2 - **Effort**: M - **Risk**: MEDIUM (a new rule on every package; noise would
  make it ignored) - **Category**: integrity - **Planned at**: commit `f90d06b`

## Why this matters

ACMP's memory: "`G-IDS` passes because it checks foreign keys and the entity index, not
identifiers in prose" - a `DEF-082` cited by three rows never existed, found only because a slate
generator resolved every id and failed loudly. Their LL-094 records a second phantom, `DEC-208`.

## Measured BEFORE it was designed (the approval's gate: stop above 5 false hits per 1,000 rows)

A read-only prototype over (a) the lab fixture through the lock-free `store.load`, and (b) ACMP's
tool-written `exports/*.json` - never their `data/*.jsonl` - judging only references INTO the
eight exported families:

| Corpus | Rows | Distinct dangling refs | Verdict |
|---|---|---|---|
| lab fixture | 74 | 1 (`RISK-002` in `PE-021.entry`) | the journal's honest account of a REFUSED row -> the journal is exempt -> 0 |
| ACMP exports | 1,103 | 3: `DEF-082`, `DEC-208`, `ADR-2026` | the first two are EXACTLY the phantoms the field found by hand; the third is a date-shaped false positive |

About 0.9 false hits per 1,000 rows, under the threshold; two of two known phantoms found.

## What changed

- `_scan_prose_ids(conn)`: prefixes from the baseline registry plus the package's own
  `entity_types` rows (and the secondary `NFR-`/`SEC-`); whole-token match; every TEXT column of
  every live row, `custom_attributes` by JSON **values, never keys**; code spans stripped
  (`_strip_code`); Superseded/Obsolete rows skipped (plan 046's rule); a row's own id is not a
  reference; **`progress_entries` and `audit_verdicts` are exempt** because they are append-only
  - a reference nobody can repair must never hold a rule amber forever (the findings_21 trap).
- `prose-ids-resolve`, advisory, package scope. Entities read `<row>.<column> -> <id>`, capped
  at 50 with the total in the note. An immutable row is repaired by supersession; the note says so.
- `prompts/register-liveness.md` gains step 16 (the close step becomes 17) and its body is
  appended to `stock-history.json` under `4.9.0`. The amber-families test's hard-coded tuple
  gained the rule too - it would otherwise have stayed green while its own docstring went false.

## Tests

`test_prose_ids_resolve_names_references_that_resolve_to_nothing`: clean package passes; a
defect citing a phantom in its title and another in a `custom_attributes` VALUE is named on both,
while a real id, a code-span id, a JSON KEY and a journal entry are not; `ready` unchanged;
fixing the text clears it. RED before (rule missing; playbook silent), GREEN after. All three
eval fixtures scan clean.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (152); lint 9 -> stock history current (79 bodies)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`. **A stock prompt changed** - its `4.9.0`
history key lands in this commit. Goldens untouched; the lab fixture's prompt copy is refreshed
by beat 16.
