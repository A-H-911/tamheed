# Plan 128: tag v5.1.0, this repo's local enable, the ACMP brief, close-out

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (the release recipe of plans 090/099/119)

## Steps

1. Push `main`; watch CI to completion on the release commit; tag `v5.1.0` there; push the tag.
2. This repository: `.claude/settings.local.json` gains `enabledPlugins: {"tamheed@tamheed": true}`
   (user scope is `false` since the field's FB-022; sessions here regain the tamheed tools after a
   restart).
3. `plans/README.md` statuses (120–128 DONE with their commits); the batch record EXECUTED; the
   memory file `tamheed-v510-findings32-batch.md` + its `MEMORY.md` line.
4. The ACMP brief — transcript, TWO parts (the 5.0.0 brief's §7 was truncated in the paste):
   A = the upgrade with pre-registered prediction CLASSES and the 5.0.0 brief's errors owned;
   B = the ACMP-side work (the first handoff entry, the `prm-next.md` diet, `AGENTS.md` and root
   `CLAUDE.md`, the memory consolidation list, the seven twins, FB-021's hand-edit, FB-019's file,
   the queued Claude Code bug, `findings_33`'s questions). The FB-019–022 answers are in it
   (`resolved_in` 5.1.0, `upstream_ref` plans 124 / 122 / 124 / 126).
5. Owed housekeeping named, not done: the six orphan agent worktree folders under
   `.claude/worktrees/` (the user removes them).

## Done criteria

- [ ] tag `v5.1.0` on a CI-green commit
- [ ] the index, the batch record and the memory say DONE / EXECUTED with the commits
- [ ] the brief delivered in two parts
