# Plan 191: release 5.9.0 (the batch record, the README rows, push, tag)

> Maintainer-executed, 2026-10-04. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R23 (the batch ends with the full release recipe including push and tag; the maintainer
> asks once before pushing), R12 (plan 175 round 2 resumes after this batch), R46 (the CHANGELOG
> entry carries the UTC date 2026-10-03, whatever day the tag lands), the guide's release recipe
> (nine steps since plan 190).

## Status
- **Priority**: P1 - **Effort**: S - **Risk**: LOW-MEDIUM (the first Ubuntu run of the guide byte-twin; a failure is a disclosed fix-up commit before the tag) - **IN PROGRESS**

## Steps, in the recipe's order

1. The batch record closed: sections 3 and 4 complete through plan 191, section 5 (not built) complete,
   the rulings table through R48, section 1 and 2 headers true to the count.
2. `plans/README.md`: the cycle heading `### STE batch -- plans 176-191 -> v5.9.0 (2026-10-03 UTC;
   maintainer-executed)`, every row 176-191 DONE with its SHA.
3. The batch memory file updated (the operator's `~/.claude` memory, outside the repository).
4. `python check.py` green on the exact tree. Commit (this plan's own commit).
5. **Ask once** before `git push origin main`.
6. CI green on every job of the matrix (ubuntu + windows, Python 3.10-3.13). The guide's byte-twin has
   never run on Ubuntu: a failure there is a disclosed fix-up commit before the tag.
7. `git tag v5.9.0` on the CI-green commit, `git push origin v5.9.0`.
8. `git diff v5.9.0 HEAD -- plugins/tamheed` empty.
9. Then plan 175 round 2 (the guide review) resumes, outside this batch.

## The release, as it landed

- The release commit: `fc81d83`. `python check.py` ALL CHECKS PASSED on it.
- The push, on the operator's single word (R23): `git push origin main`, `67889cc..fc81d83`, 21 commits
  (the plan-175 follow-ups and plans 176-191).
- CI on `fc81d83`: run 37160543380, every job green (the server smoke job and the eight `check`
  jobs, ubuntu + windows × Python 3.10-3.13). The guide's byte-twin passed on Ubuntu at its first
  run there; no fix-up commit was needed.
- The tag: `v5.9.0` on `fc81d83`, pushed (`refs/tags/v5.9.0` on origin). `git diff v5.9.0 HEAD --
  plugins/tamheed` is empty.
- This ledger's own lines above landed in a follow-up commit after the tag; the bundle did not move.

## Status after the release
- **DONE 2026-10-04** (2026-10-03 UTC for the entry's date, R46). Plan 175 round 2 resumes next.

## Validation
- Green: `python check.py`; CI on the release commit; the tag on that commit; the bundle diff empty.
