# Plan 130: the stale-warning block's home, text and removal (the field's FB-024)

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (tool-owned bytes only; byte-identity tested)

## Why this matters

FB-024 (ACMP, 5.1.0), three faults in one emission: (1) with the recognised pointer pattern
(root `CLAUDE.md` imports `@<pkg>/CLAUDE.md`) the stale-warning block was appended to the ROOT
file while the emission's warning said "the root file was left untouched"; (2) the block read
"Stale v1 references detected … freeze the v1 tree" for a v5-era sentence in a project skill
file; (3) `_STALE_BLOCK_RE.sub("\n", …)` replaced the block's own leading and trailing newline
with one, so each stale emit added a newline and the clean emit left the file two blank lines
longer than it began — ACMP removed them by hand.

## What changes

- `_STALE_BLOCK` (one constant) names agent-control, prompt and skill files and the result key.
- `_strip_stale_block(text)`: a tail match is removed whole; a block elsewhere keeps one newline.
- Pointer branch: the package `CLAUDE.md` is read, stripped, the span applied, the block appended
  when the scan found something; `rebuilt` speaks of the span alone; the warning gains "; the
  stale-warning block was added | removed there" and "; a 5.1-era stale-warning block was removed
  from the root file" (the root is stripped once, never appended to). Non-pointer targets keep the
  block in the root beside the note.
- Docs: `references/handoff.md`, CHANGELOG.

## Tests

- `test_stale_warning_block_retracts_when_clean`: clean bytes captured; stale → stale (unchanged,
  same bytes) → clean → bytes identical; the block's text.
- `test_pointer_case_stale_block_lives_in_the_package_claude_md`: root bytes constant across the
  cycle; the package file carries then loses the block, restored byte-identical; the warning's
  three sentences; a legacy root block stripped once, then idle.

## Known ceiling

Whitespace an operator adds AFTER a tail block leaves one blank line once and is stable
thereafter (`ponytail:` comment in `_strip_stale_block`); the tool never writes that shape.
