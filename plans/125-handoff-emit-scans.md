# Plan 125: handoff_emit's scans — the marker verified, the oversized prompt, the skill files, two detectors, the note span stripped

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW (all report-only; one latent false positive fixed)

## Why this matters

FB-019: a `stock-merged 4.9.0` marker that was never true was echoed as a declaration for months.
Note 4: a 3,594-line kickoff prompt carried state nothing could see. FB-021: a distilled skill file
kept the retired "export_html flushes" sentence with no scan over it. Note 2: `AGENTS.md`'s
"P1–P19 COMPLETE" and its 3,000-char feedback mirror passed the restated-content scan, which needs
three consecutive id-led lines. And the scan never stripped the tool-owned note span — a target
with the note inline read its ten lesson lines as restated content on every second emit.

## What changes

- `_stock_merged_check`: the declared release must exist in the file's history and every line it
  ADDED relative to the previous release must be present; `stock_merged: [{file, declared,
  verified, delta_missing, reason}]` (top-level and in `prompt_library`) + a warning when false;
  `leftover_customized` files get the same check (their list shape is unchanged).
- `prompt-oversized`: project prompts over 300 lines or 24,576 bytes → `oversized_prompts` + a
  warning naming where state belongs.
- Skill files: every `target_path` the Approved skills rows name is scanned with `_STALE_PATTERNS`
  (`file: "skill:<name> (<path>)"`), which gains the v5 flush pattern.
- Detectors: `id-dense` (≥ 6 distinct ids of one family in one paragraph) and `status-claim`
  (`COMPLETE|DONE|Implemented|DEFERRED|Approved|Met` within 40 chars of an id or an id range),
  over lines the run detector did not already report.
- `_strip_tool_spans` before every scan; in the pointer-import case `<pkg>/CLAUDE.md` is scanned
  too (`file: "<pkg>/CLAUDE.md"`).

## Done criteria

- [ ] `python check.py` green (four new contract tests; the existing "nothing else fires" holds)
- [ ] dry-run classes recorded in the batch record §0 (M5)
