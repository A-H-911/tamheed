# Plan 116: sixteen scenario skills + engine v5 (note v5, README-only library, leftovers)

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: L - **Risk**: HIGH (the handoff contract changes; every project's note is rebuilt; files are deleted on refresh)

## Why this matters

Interview: the 16 stock prompts become `/tamheed:<name>` slash skills (`disable-model-invocation: true` — the operator invokes, as they paste today; descriptions cost nothing ambient). The note loses the cheat-sheet (its rules live in `package-writes`); `<package>/prompts/` keeps project prompts + README; stale-stock leftovers are deleted by `refresh_stock=true`, customised ones warned.

## What changes

Sixteen `skills/<scenario>/SKILL.md` from the prompt bodies (`{package}` → the note's package or `$ARGUMENTS`; cross-references classified: operator-next-step → `/tamheed:<name>`, agent-reads-now → Read `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`). `_stock_names()` = current stock ∪ history keys for `:470`, `:2975`, `:3259`. `_emit_prompt_library`: README only + the leftover pass (`leftover_stale_stock` → `retired` on refresh; `leftover_customized` warned). Note v5 (`<!-- tamheed:note v5 -->`). `agent-control.template.md` conventions → a pointer (the table identical). `prompts/README.md` rewritten (5.0.0 history key; the three eval needles kept). Tests rewritten.

## Done criteria

- [x] RED then GREEN (`:1539` retired; `:1606-1713` re-aimed; new leftover tests; `:3205` re-aimed at the skills)
- [x] dry-run on a fixture copy: 16 `retired`, README refreshed, `project-kickoff.md` untouched, note v5 in the workspace copy
- [x] `-p "/tamheed:slice-kickoff"` resolves on a bundle copy
- [x] `python check.py`
- [ ] CI green

## Execution note (2026-09-25)

RED: seven tests (the re-aimed library tests, the note v5 test, the new leftover test) failed before
the engine change; GREEN after it, plus five more tests re-aimed at the skills' paths and the v5
marker (172 OK). Dry-run on a fixture COPY: 16 `leftover_stale_stock` on a plain emit, 16 `retired` on
`refresh_stock`, README refreshed, `project-kickoff.md` untouched, the workspace note rebuilt as v5
(cheat-sheet gone, skills named, the obligations table kept), `prompt-ids-resolve` population 1,
`package_verify` true. Probe on a copy of the current bundle: `/tamheed:slice-kickoff` loaded verbatim;
the model's own skill list shows exactly the eight model-invocable skills — the sixteen
`disable-model-invocation` scenarios stay out of context, as the docs say. The note's flush sentence is
corrected in the same rebuild (plan 115's review, HIGH 1). The scenario skills were born with plan
112's step-15 and NOT-NULL text (their files are created here; 112 commits the server README).
