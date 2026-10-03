# Plan 187: wave 4a - the human docs, the root files, the lab and evals READMEs

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R16 (wave 4), R26, R27 (lab/evals READMEs in; brief, scenario, evals.json exempt), R6
> (flavored for human docs). Wave protocol as plans 184-186. Plus the owed plan-175 alignment: the
> `plugin.json` and `marketplace.json` descriptions name both halves of the capability.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: LOW-MEDIUM (lint 8 version strings; README links outside lint 10) - **DONE 2026-10-03** (the commit this ledger lands in, after the operator's review)

## Scope

Flavored, English: `README.md`, `SECURITY.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `docs/*.md`,
`lab/README.md`, `evals/README.md`. The roster moves those globs from pending to rostered. The two
manifest descriptions (`plugins/tamheed/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`) are JSON, outside lint 14, rewritten by hand to the same rules.

Wave-4 pins carried from plan 186: `docs/workflow.md:161` restates the stage shape with `Validate`
(R37: it reads `Check`).

## Baseline (before the rewrite, `ste_lint.py --mode flavored`)

| File | Words | Hard |
|---|---|---|
| README.md | 3,711 | 111 |
| SECURITY.md | 2,282 | 89 |
| CLAUDE.md | 830 | 20 |
| CONTRIBUTING.md | 1,205 | 36 |
| docs/architecture.md | 2,993 | 83 |
| docs/design-decisions.md | 8,333 | 215 |
| docs/entities.md | 10,122 | 342 |
| docs/install.md | 4,353 | 122 |
| docs/methodology.md | 3,208 | 81 |
| docs/migrate-from-keystone.md | 1,373 | 35 |
| docs/workflow.md | 2,012 | 96 |
| lab/README.md | 1,233 | 20 |
| evals/README.md | 728 | 12 |
| **13 files** | **42,383** | **1,262** (727 semicolon, 533 long-sentence, 1 phrasal-verb, 1 dangling-conjunction) |

Under flavored mode the vocabulary rule is advisory, so the baseline carries no vocabulary count.

## Pin ledger

`evidence/scripts-ste/pins-187.md` before, `pins_missing.py` after. Known: lint 8's version strings
(`5.8.1` in README.md and docs/install.md, untouched until plan 189), lint 10's paths, the
`CONTRIBUTING.md:18` suite count (twelve since plan 180).

## After the rewrite

| File | Words | Hard |
|---|---|---|
| 13 files | 42,431 | 0 (458 advisory: passive voice, present perfect, vocabulary under flavored) |

Gate line after the roster move: `lint: plain English (92 files, 111689 words) 0 hard, advisory
passive-voice=889 present-perfect=66 vocabulary=47, allow markers=2, pending 1 surfaces`. The one
pending surface is `docs/guide/content.py` (plan 188).

Two allow markers, each with its reason: `README.md` (the navigation link bar is not a sentence) and
`CLAUDE.md` (the identifier scheme is a list of 36 names). The lint-14 test that counts markers was
`allow markers=1` on a tree with none; it now reads the baseline and asserts baseline + 1.

## Invariants (`wave_invariants.py HEAD`, every difference reviewed)

| File | Difference | Verdict |
|---|---|---|
| CLAUDE.md | token `36` new (the allow marker's reason); the odd-backtick token ` = done-claimed, wbs/slices only; ` became `..., and ` | deliberate: the semicolon went |
| README.md | `11` → `12` | R38: twelve suites since plan 180 |
| docs/architecture.md | `184` new | the marker "stayed `v5` until plan 184" |
| docs/design-decisions.md | `184` new | §13: "(v6 since v5.9, plan 184)" |
| docs/install.md | `11` gone, `5.9.0` new; one odd-backtick token re-paired; `holder observed not-running — package_unlock(confirm=true) on the operator's word` now one token | R38 (twelve suites); the note "v5 since 5.0.0 and v6 since 5.9.0"; the pinned phrase sits on one line now |
| docs/entities.md | modal `unless` 1 → 0 on the first pass | restored ("The write is refused unless the item carries ...") |

No other token set moved. No other modal count fell.

## Count and name corrections (R38)

- `README.md`, `docs/install.md`: eleven suites → twelve (plan 180).
- `docs/entities.md`: "eight discipline skills" → nine, "sixteen operator-invoked scenario skills" →
  seventeen (plan 183). §4c: "Three families reuse the `lifecycle_status` column name" → six (the table
  under it has six rows; the advisor's read found it).
- `docs/architecture.md`: "twenty package-scope liveness advisories" → twenty-five, measured with
  `extract.readiness_rules()` (25 advisory + 5 blocking = the guide's 30 package rules, plan 182).
- `docs/architecture.md`: the note diagram reads `tamheed:note v6`; the prose says the marker stayed
  `v5` until plan 184. `docs/install.md` step 4 and `docs/design-decisions.md` §13 say the same.
- `docs/workflow.md:161`: `Validate` → `Check` (R37).

## Kept as-is

- Every hedge (may, might, could) and every modal, after the one restoration above.
- The slogan now reads "The skill owns the capability. Every entry point is a thin wrapper." in the
  three blockquotes (README, CLAUDE.md, architecture) and in CONTRIBUTING. Its copy in
  `docs/guide/content.py` (`section.what.principle`) waits for plan 188.
- Blockquotes are not linted (lint 13's precedent), but the five semicolons left in blockquotes were
  removed too, so the files carry none outside code.
- "v5.8.1" twice in README.md and once in docs/install.md (lint 8, the stamp is plan 189).
- The templates' HTML comments and the mermaid blocks (fenced) are untouched.
- The manifest sentence (both files): "Turn a project description into a validated, traceable,
  execution-ready planning and handoff package for Claude Code to implement. Then keep it the record
  of the build while execution runs." The README's `<strong>` tagline reads the same two sentences
  (its `&` became `and` so the two match).

## Meaning shifts surfaced for the review (not hedges)

- `docs/install.md`, the hook paragraph: "If your Claude Code build drops plugin `SessionStart` output
  ..." became "Some Claude Code builds drop plugin `SessionStart` output (...). There, the same command
  works ...". A conditional became an assertion grounded by its parenthetical (a bug reported against
  early-2026 builds).
- `docs/design-decisions.md` §18 D-TRACE-VERSION: the colon that carried the reason for the field's
  placement became a sentence break; "The reason:" was put back so the causal link stays.
- The six root/lab/evals files were rewritten before this session's compaction, so their meaning check
  is the token-set invariant, the pin ledger and the operator's diff review, not a second read here.

## Pins

`pins-187.md`: 21 phrases. `pins_missing.py` after the rewrite: 0 missing. Four were missing on the
first run, every one a phrase wrapped across a line break (three in README.md, one in
docs/architecture.md); re-joined.

## Manual checks

- README.md relative links: 22 links and image sources, 0 missing.
- Anchor links into the wave's headings (several `design-decisions.md` headings changed their
  punctuation): `grep -rn "\.md#"` over the docs, the bundle, the guide's prose and the page finds
  none, so no fragment link broke.
- `docs/guide/build.py --check` through `check.py`: the page is unchanged by this wave (the guide reads
  the bundle's workflow.md, not `docs/`).

## Validation
- Red: the roster move (1,262 hard findings).
- Green: `python check.py` ALL CHECKS PASSED on the exact tree; `wave_invariants.py HEAD` (table above);
  `pins_missing.py` 0 missing; the README link check; lint 8 strings untouched.

## Rulings taken at the review (2026-10-03)

- Approved and committed as staged.
- R40: the both-halves sentence pair on the two manifests and the README tagline.
- R41: the forward mention of 5.9.0 stands; the stamp is plan 189.
- R42: blockquotes follow the rules too (standing for plan 188); the linter is unchanged.
