# Plan 119: release v5.0.0 + the ACMP brief

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (recipe)

## Why this matters

Every plan in the batch DONE; the combined acceptance pass (`accept_v500.py` N/N vs 0/N on an extracted `v4.14.0`; selftest 19/19; §0 on the real bundle; CI) passed.

## What changes

The release recipe (plugin.json == newest CHANGELOG heading; the six stamp lines; the README history key; the annotated tag; tag pushed separately; CI). Then the ACMP brief, transcript-only.

## Done criteria

- [x] tag `v5.0.0`
- [x] CI green on the tag commit (`bbdeb4a completed success`)
- [x] the brief printed

## Execution note (2026-09-25)

Recipe: `plugin.json` 5.0.0 == the newest CHANGELOG heading; the six stamp lines; the guide's
5.0.0 history key re-set to the shipped body; annotated tag `v5.0.0` on `bbdeb4a`; main and the tag
pushed separately. Before the tag: the full gate green on the stamped tree; the three
`--plugin-dir` probes on a copy of the bundle exactly as tagged (`PROBE-OK`; the front door loads
from `skills/tamheed` and reports v5.0.0; the model lists the eight model-invocable skills). The
fixture's guide followed by tool: beat 22 had refreshed it to the INTERIM 5.0.0 body (never a
release; it leaves the history at the stamp, so the tool reads it `customized`) — the follow script
proved the file byte-equal to that interim body and only then let `force` overwrite exactly that
one file (`emitted: ["prompts/README.md"]`, `retired: []`, gate ready, verify true, review
current). Lesson recorded in memory: add a pre-release history key only at the release. The CHANGELOG
lead's "one stock file changes" was corrected before the stamp (advisor): the library is README
alone, sixteen files retired, migration 006 ships. The ACMP brief follows in the transcript.
