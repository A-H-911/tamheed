# Plan 178: `references/handoff.md` no longer claims the template twin

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: the STE census (R19c). A fix beat, no STE rewrite yet.

## Status
- **Priority**: P2 - **Effort**: S - **Risk**: LOW - **DONE** (2026-10-03)

## What the census found

`references/handoff.md:32` says "The same table lives verbatim in the agent-control template."
Plan 132 (v5.2, findings_33 R10) ended that twin: the note is the one copy, the template points
at it and carries no obligation row, and `test_note_obligations_match_agent_control_template`
(`tests/test_mcp_contract.py:1021`) fails if a row is copied back. The reference the planning agent
reads at stage 20 contradicted the test for seven releases.

## What changed

| File | Before | After |
|---|---|---|
| `plugins/tamheed/references/handoff.md:32` | "The same table lives verbatim in the agent-control template." | "The agent-control template points at the note and carries no obligation row (plan 132)." |
| `tests/test_mcp_contract.py` `test_note_obligations_match_agent_control_template` | reads the note and the template | also reads `handoff.md`: the old sentence absent, the new one present |

## Validation
- Red: the extended test fails on the old sentence.
- Green: `python check.py` ALL CHECKS PASSED (lint 10 dead paths, lint 13 vocabulary unchanged).
