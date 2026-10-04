# Plan 200: release 6.0.0 (the batch record, the README rows, push, tag)

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Source: R23 (the batch ends with the full release recipe including push and tag; the maintainer
> asks once before pushing), G15 (the engine change first, the guide round after its tag), the
> guide's release recipe (nine steps since plan 190).

## Status
- **Priority**: P1 - **Effort**: S - **Risk**: LOW-MEDIUM (the first MAJOR since 5.0.0; the fixtures and
  the sample were rewritten by the engine, so the Ubuntu jobs read them for the first time) - **DONE 2026-10-04**

## Steps, in the recipe's order

1. The batch record closed: sections 3 and 4 complete through plan 200 with every plan's SHA, section
   5 (not built) complete, the rulings table through P21.
2. `plans/README.md`: the cycle heading `### Prompts return to the store -- plans 192-200 -> v6.0.0
   (released 2026-10-04; maintainer-executed)`, every row 192-200 DONE with its SHA.
3. The batch memory file updated (the operator's `~/.claude` memory, outside the repository).
4. `python check.py` green on the exact tree; the server selftest 19/19. Commit (this plan's own commit).
5. **Ask once** before `git push origin main`.
6. CI green on every job of the matrix (ubuntu + windows, Python 3.10-3.13).
7. `git tag v6.0.0` on the CI-green commit, `git push origin v6.0.0`.
8. `git diff v6.0.0 HEAD -- plugins/tamheed` empty.
9. Then the user guide round 2 (plans 201-210, batch B, 6.1.0) begins, outside this batch.

## The release, as it landed

- The release commit: `b94c9ac`. `python check.py` ALL CHECKS PASSED on it; the selftest 19/19.
- The push, on the operator's single word (R23): `git push origin main`, `fc81d83..b94c9ac`, ten
  commits (plans 191's ledger follow-up and 192-200).
- CI on `b94c9ac`: run 37198937555, every job green (the server smoke job and the eight `check` jobs,
  ubuntu + windows x Python 3.10-3.13). The engine-rewritten fixtures and the generated sample passed
  on Ubuntu at their first run there; no fix-up commit was needed.
- The tag: `v6.0.0` on `b94c9ac`, pushed (`refs/tags/v6.0.0` on origin). `git diff v6.0.0 HEAD --
  plugins/tamheed` is empty.
- This ledger's own lines above landed in a follow-up commit after the tag; the bundle did not move.

## Validation
- Green: `python check.py`; CI on the release commit; the tag on that commit; the bundle diff empty.
- Before the commit: `python check.py` ALL CHECKS PASSED; `uv run plugins/tamheed/server/tamheed_server.py
  --selftest` 19/19 tools, 19/19 descriptions.
