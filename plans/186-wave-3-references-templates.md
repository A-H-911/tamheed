# Plan 186: wave 3 - references, templates, the stock README, the server README, CANONICAL

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R16 (wave 3), R26, R6 (strict for agent-facing, flavored for the two human-facing files).
> Wave protocol as plans 184-185: rewrite, lint 0 hard, invariants, pin ledger, gate, stage,
> advisor read, operator review, one commit.

## Status
- **Priority**: P1 - **Effort**: XL - **Risk**: MEDIUM (numeric sentences pinned by tests; the stock README is a history key) - **DONE: approved as staged 2026-10-03 (rulings R37-R39 in the batch record)**

## Scope

Strict, English: `plugins/tamheed/references/*.md` (18, the vocabulary's own prose included),
`plugins/tamheed/templates/*.md` (16 incl. its README), `plugins/tamheed/prompts/README.md` (the
stock README: its body is re-appended under the `5.9.0` key of `stock-history.json`, the key plan 183
opened). Flavored, English: `plugins/tamheed/server/README.md`, `plugins/tamheed/db/CANONICAL.md`,
`plugins/tamheed/assets/README.md`. The roster moves those globs from pending to rostered.

## Baseline (before the rewrite, `ste_lint.py`)

| Surface | Mode | Files | Hard | Of which |
|---|---|---|---|---|
| references + templates + stock README | strict | 34 | 785 | 454 semicolon, 250 long-sentence, 81 vocabulary |
| server README, CANONICAL, assets README | flavored | 3 | 225 | server README 199, CANONICAL 25, assets 1 |

Largest files: workflow.md 101 hard, artifact-catalog.md 92, handoff.md 79, stock README 73,
governance.md 72, quality-gates.md 56.

## Pin ledger

`evidence/scripts-ste/pins-186.md` before, `pins_missing.py` after. Known from the census:
`tests/test_mcp_contract.py` L3676-3692 (numeric sentences in `artifact-rules.md`, `governance.md`,
the stock README's "the 10 highest-numbered unpinned ones"), lint 11 needles in
`governance.template.md`, the id formats in `naming-conventions.template.md`,
`test_templates_teach_v4_recording`, `test_note_obligations...` template needles,
`test_stock_prompts_teach_the_field_rules` README needles, lint 9's closed triangle, lint 13's shapes,
lint 10's paths.

## What shipped

- 37 files, 1,010 hard findings to 0 (785 strict + 225 flavored). Gate line after the roster move:
  `lint: plain English (79 files, 69252 words) 0 hard, advisory passive-voice=506 present-perfect=33 vocabulary=5, allow markers=0, pending 14 surfaces`.
  The five `vocabulary` advisories are the flavored files' (server README, CANONICAL).
- The roster: six globs moved from `_STE_PENDING` to `_STE_SURFACES` (references, templates, stock
  README strict; server README, CANONICAL, assets README flavored). `vocabulary.md` keeps its
  dedicated first entry, which skips the vocabulary rule for that file (first match wins).
- The stock README body re-appended under the `5.9.0` key of `stock-history.json` (15,300 →
  15,640 chars, `stock_key_186.py`). Lint 9 reads it current.
- Method as waves 1-2: whole-file rewrites through the Write tool, targeted scripts for files with a
  few placeholder semicolons (adr, architecture, naming-conventions, technology-comparison,
  generated-structure), the remaining long sentences listed with their word counts and split.
- Count and name corrections made while rewriting (prose, not tokens, so the invariants do not
  see them): "the sixteen scenarios" → seventeen (artifact-catalog File artifacts row, server README
  `handoff_emit` row); "five sections" → eleven, naming `generate-report` as their list (server README
  review-surface section); handoff.md's v5.1 paragraph "all eight discipline skills" → "every
  discipline skill (eight at 5.1, nine since 5.9)" and its "the marker stays `v5`" rewritten as
  history with "`v6` since plan 184"; server README `handoff_emit` row "the note is `tamheed:note v5`"
  → "became `tamheed:note v5` (and `v6` in v5.9, plan 184)".
- **workflow.md's field label `Validate:` is `Check:` in all 22 stages and the legend** (R31:
  `validate` rejected, `check` approved). The guide reads workflow.md for phase headings, stage
  headings, the ✅ marks and the Loops paragraph only (`extract.py:270-292`), so the byte-twin is
  unmoved. Stage 19's title "Quality validation" is a name (names table) and stays. One restatement
  of the stage shape lives outside the bundle: `docs/workflow.md:161` ("In · Do · Out · Enter · Exit
  · Validate · ..."). It is a wave-4 pin for plan 187. Every other `Validate` hit in `docs/` and
  `content.py` is the verdict value `Validated`, a name.
- artifact-catalog's operating rule "Repair doctrine" is "Fix doctrine" (R32).

## Kept as-is

- **HTML guidance comments in the templates** (`<!-- ... -->`): the extractor drops them (R29's
  marker design), so the lint never reads them and their prose is unchanged. The operator can rule
  them in for a later wave.
- `references/vocabulary.md`'s three own-prose `vocabulary` hits (`begin`, `delete`, `halts` in
  the notes that reject them): skipped by the roster's rule skip for that file, by design (plan 181).
- Quoted eval phrases in the server README (`is current there; nothing written`,
  `holder observed not-running — package_unlock(confirm=true) on the operator's word`): server text
  the lab fixture's journal rows carry, quoted in code spans, where a semicolon is exempt.
- Hedges: none promoted. Every modal drop below is two clauses merged under one modal.

## The invariants (`wave_invariants.py HEAD`)

| File | Difference | Why |
|---|---|---|
| extension.md | `AND` gone | "...AND add the endpoint rule" is "Then add the endpoint rule" (two sentences) |
| handoff.md | gone `LL-NNN`, `RETIRE`, `ROW`, `THIS`, two span fragments; new `- RETIRE THIS ROW (operator)`, `superseded by LL-NNN - pending its approval`, `<!-- tamheed:note v6 -->`, `<!-- tamheed:stock-merged X.Y.Z -->`, `stock_merged`, `184`, `5.9`, `v6` | the original broke four code spans across lines, which the tokenizer read as bare words; the spans are whole now. `184`/`5.9`/`v6` are the marker-history sentence |
| handoff.md | never 14→13 | "never `data/*.jsonl`, never a pasted display" → "It never reads `data/*.jsonl` or a pasted display" |
| handoff.md | must 5→4, then restored | "the executor host must find the server without guessing" had become "so the executor host finds"; restored as "because the executor host must find" |
| server/README.md | `DELETES` → `REMOVES`; new `184`, `9`, `v6`, `generate-report` | R32; the marker-history clause; the eleven-sections sentence names the skill that lists them |
| follow-up-prompts.template.md | `15` and a span fragment gone, `git log --oneline -15` new | the original broke the code span across a line |
| governance.md | (clean after a fix) | my first rewrite broke `"operator_confirm": true` across a line; the invariants caught it |

## Pin ledger (after)

`pins_missing.py pins-186.md`: 0 of 41 missing. Two pins broke during the wave and were fixed
before the review: `tool-owned tamheed note in `<package-name>/CLAUDE.md`` and `STOP and tell the
operator` (agent-control), both by a line wrap inside the phrase. The contract test
`test_note_obligations_match_agent_control_template` failed on the first and passed after the
re-wrap.

## Errors owned

- Three code spans and two pinned phrases broken across lines by my wrapping (governance,
  agent-control twice, loop-iteration in wave 2 before). The token invariant and the pin tool caught
  every one. Rule for waves 4+: a code span or a pinned phrase never straddles a line break.
- "must find the server" weakened to "finds the server" in one handoff sentence; the modal counter
  caught it.
- The first agent-control re-wrap fixed one pin and broke the other.

## Validation
- Red: the roster move.
- Green: `python check.py`; `wave_invariants.py HEAD`; `pins_missing.py`; lint 8 still finds `5.8.1`
  (the stamp is plan 189); lint 9 history current (the stock body under `5.9.0`); lint 10 no dead paths.
