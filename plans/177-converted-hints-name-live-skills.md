# Plan 177: `_CONVERTED_HINTS` names live skills

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: the STE census (R19b). A fix beat, no STE rewrite yet.

## Status
- **Priority**: P2 - **Effort**: S - **Risk**: LOW - **DONE** (2026-10-03)

## What the census found

`_CONVERTED_HINTS` (`tamheed_server.py:3708-3716`) tells the operator which stock text now covers
the generic half of a converted v2 prompt. Its "initial" hint named
`package-onboarding.md/slice-kickoff.md`, files the library stopped shipping in 5.0.0 when the
scenario prompts became slash skills. The "follow-up" and "review" hints name bare skill names
without the `/tamheed:` form the guide uses. The hint repeats on every `handoff_emit` until the
operator curates the file, so a stale hint is read many times.

## What changed

| File | Before | After |
|---|---|---|
| `tamheed_server.py` `_CONVERTED_HINTS` | "generic half now covered by package-onboarding.md/slice-kickoff.md; keep only project-specific content (and check any restated state for staleness)" | three hints that name live slash skills in the `/tamheed:<name>` form, one sentence each, no semicolon |
| `tamheed_server.py` `_CONVERTED_CURATE` | one sentence joined by a dash | unchanged in meaning, split where it carried two instructions |
| `tests/test_mcp_contract.py` | — | `test_converted_hints_name_live_skills`: no `<name>.md` token, every `/tamheed:<name>` resolves to a shipped skill folder, each hint names at least one |

## Validation
- Red: the new test fails on "package-onboarding.md/slice-kickoff.md".
- Green: `python check.py` ALL CHECKS PASSED (the converted-prompt lifecycle test at L1801 still passes).
