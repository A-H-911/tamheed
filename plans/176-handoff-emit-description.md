# Plan 176: `handoff_emit` says what it writes

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: the STE census (R19a). A fix beat, no STE rewrite yet.

## Status
- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE** (2026-10-03)

## What the census found

`TOOLS["handoff_emit"]` (`tamheed_server.py:5046`) read "Emit handoff prompts + executor MCP config
(injection-screened)". The tool has not written prompts into a target since v3. It writes the
CLAUDE.md note, the stock prompts README, and `.mcp.json` only for a standalone install
(`tamheed_server.py:3937-3947` skips it when plugin-hosted). The description is the one text a
client reads about the tool (`TOOLS[name][1]`, plan 160), and the guide quotes it verbatim.

## What changed

| File | Before | After |
|---|---|---|
| `plugins/tamheed/server/tamheed_server.py:5046` | "Emit handoff prompts + executor MCP config (injection-screened)" | "Wire a target project to the package: write the CLAUDE.md note and the stock prompts README, plus `.mcp.json` for a standalone install. Injection-screened." |
| `tests/test_mcp_contract.py` | — | `test_handoff_emit_description_names_its_writes` (red before the change) |
| `index.html` | the old description | rebuilt (`render.py:568` quotes tool descriptions) |
| `plans/README.md` | no rows for plans 170–174 | the FB-028 cycle heading with five rows, and the STE cycle with plan 176 |

## Validation
- Red: the new test fails on the old description (asserts "Emit handoff prompts" absent, the note and `.mcp.json` named).
- Green: `python check.py` ALL CHECKS PASSED.
