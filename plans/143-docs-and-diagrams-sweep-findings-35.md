# Plan 143: docs and diagrams sweep for v5.4.0

> Maintainer-executed, 2026-09-27. Batch map: [141-145-batch-findings-35.md](141-145-batch-findings-35.md).
> Rulings R21–R24; measurements M1–M4 and M6 of the batch record.

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW - **DONE**

## How the list was built

A grep for `reload` and for the trace format over every file outside `plans/`, not a list from
memory. Dated records are corrected by a dated note beside the sentence; a CHANGELOG entry of a
shipped release stays as written and the new entry carries the correction.

## What changed

| File | Change |
|---|---|
| `docs/install.md`, the hook paragraph | the line's format ends `session=<id>`; a line is attributed by it, never by its counts; the wrong inference removed; every session in a project where the plugin is enabled appends; a headless session receives the block |
| `docs/install.md`, Upgrading | a plugin reload does not run `SessionStart`, with its basis (24 reloads, builds, scope, the control) and its limit; the earlier delivery was a restart; one observation that a reload swaps the hook's code; the MCP server reached by reload three times; four issue links dropped; the tree check on LF-normalised bytes |
| `SECURITY.md` | the session id in the trace and the token rule; headless sessions receive the block |
| `plugins/tamheed/server/README.md` | the format; attribution; the reload |
| `docs/architecture.md` | the resume sequence: a reload is not a route, the line carries the session's id; a v5.4 paragraph |
| `docs/design-decisions.md` | two dated corrections in §15; §16 with seven decisions |
| `lab/scenario.md` item 25 | the pid is host-bound; the line ends `session=` from 5.4 |
| `README.md`, front door `SKILL.md` | the trace names its session; a reload runs no hook; the interview's default |
| `CHANGELOG.md` | the `[Unreleased]` body, with a Fixed section for the corrected docs |
| `plans/README.md`, the batch record | the findings_35 section; the measurements table |

Not changed, checked: `references/handoff.md` names neither the reload nor the trace format;
`prompts/README.md` line 103 ("after a plugin reload the holder is usually gone") stays true;
`review.html`'s generator renders no lock and needs no change (§16 D-REVIEW-NO-LOCK).

## Owned

The sweep first stated the gap to the next `SessionStart` as "41 minutes or hours" for all 24
reloads. Two followed within minutes for causes the record names: a compaction entered 5 seconds
after one reload, and the restart. The sentence was corrected before the commit.

## Validation

| Check | Result |
|---|---|
| grep for `reload` outside `plans/` | no sentence says a reload delivers or fires the hook, except inside a dated correction or the 5.3.0 CHANGELOG entry |
| grep for `status=` outside `plans/` | every format quote ends `session=<id>` or names item 26 |
| `python check.py` | ALL CHECKS PASSED |
