# Plan 200: release 6.0.0 (the batch record, the README rows, push, tag)

> Maintainer-executed, 2026-10-04. Batch record: [192-200-batch-prompts.md](192-200-batch-prompts.md).
> Source: R23 (the batch ends with the full release recipe including push and tag; the maintainer
> asks once before pushing), G15 (the engine change first, the guide round after its tag), the
> guide's release recipe (nine steps since plan 190).

## Status
- **Priority**: P1 - **Effort**: S - **Risk**: LOW-MEDIUM (the first MAJOR since 5.0.0; the fixtures and
  the sample were rewritten by the engine, so the Ubuntu jobs read them for the first time) - **IN PROGRESS**

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

(filled after the push and the tag)

## Validation
- Before the commit: `python check.py` ALL CHECKS PASSED; `uv run plugins/tamheed/server/tamheed_server.py
  --selftest` 19/19 tools, 19/19 descriptions.
