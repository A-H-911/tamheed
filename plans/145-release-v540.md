# Plan 145: tag v5.4.0, the brief file, close-out

> Maintainer-executed, 2026-09-27. Batch map: [141-145-batch-findings-35.md](141-145-batch-findings-35.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## Steps

1. **The copy, refreshed.** A read-only copy of the field's package and control files taken from
   `3071f1f4` with `git archive` (committed bytes, no line-ending rewrite).
2. **The replay on the final bundle** (`acmp_replay3.py`, second run on a fresh copy). Every 5.3 class
   held. New readings are in the batch record's measurements table.
3. **Every Part B recipe run on the copy BEFORE the brief was written.** This step found two things
   the brief would otherwise have carried:
   - the approval recipe first written for the replay (a `substitute` on `lifecycle_status`) is
     refused by name, twice. The approval is a full row;
   - `lessons-confirmed` fails while the field's one Proposed lesson stands, a class the 5.3.0
     baseline did not have.
4. **One sentence in `package-writes` §1**: a move that must carry a column of its own is not the
   cheap status flip; a lesson's approval is a full row. It is where the maintainer's own false
   belief came from (E5 of the brief).
5. **The brief**: [briefs/acmp-5.4.0.md](briefs/acmp-5.4.0.md). Classes only; predictions name roles;
   the maintainer's own errors (E5, D1, D2) beside the field's E1–E4; the live sentences the upgrade
   falsifies, by path and line.
6. **Advisor pass** on the brief and the batch record before the close-out commit.
7. Close-out commit → CI green on all eight jobs → tag `v5.4.0` → nothing after.

## Validation

| Check | Result |
|---|---|
| `python check.py`, the variable unset | ALL CHECKS PASSED |
| `uv run plugins/tamheed/server/tamheed_server.py --selftest` | 19/19 tools registered |
| The operator's trace file | five lines at step 0 and at the close; none inside a suite, beat or replay window |
| `git diff v5.4.0 HEAD -- plugins/tamheed` | empty |
