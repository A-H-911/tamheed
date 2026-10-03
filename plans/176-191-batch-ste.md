# Plans 176–191: the plain-English (ASD-STE100) batch → v5.9.0

> **Status: IN PROGRESS** (started 2026-10-03). The approved plan (revision 2 after the
> maintainer's own devil's-advocate pass, the operator's strict review and three advisor calls)
> lives in the maintainer's plan file; its substance is here. Upstream:
> [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (MIT, (c) 2026 Dustin
> Yuchen Teng, `master` at `7d4a135`). Commits land one per plan; this record is updated with each.

## 1. What the operator asked for, and what was read

The operator asked to study the ASD-STE100 skill and merge its discipline into every part of
Tamheed: the engine, the skills, the references and templates, the generated guide, the repo docs,
and a migration path for the live field project (ACMP). Read in full: the upstream `SKILL.md`
(v0.4.0), `references/writing-rules.md`, `scripts/ste-lint.py`, `examples/before-after.md`,
`examples/linter-edge-cases.md`, `LICENSE`, the four closed issues (#1, #10, #11, #12). Three
censuses of this repo (prose surfaces, client and migration paths, test and plan conventions) were
taken and every line number used below was re-read in the files at `dfb34dd`.

Measured before any change (the upstream linter unmodified): semicolons 2,503 in prose (skills 389,
references 358, templates 88, root `*.md` 708, `docs/` 572, `lab/` 314); synonym-rotation 169 (mostly
Tamheed terms of art); long sentences 66 by the upstream per-line split, against a paragraph-joined
census of 445 skill sentences over 20 words (32%) and 302 over 25 (21%); passive 915 and present
perfect 88 (advisory). Python runtime literals: `tamheed_server.py` 104 semicolons, `content.py`
559 in English and 543 Arabic semicolons in Arabic.

## 2. Rulings (R1–R29 from the interview of 2026-10-03, 32 answers; R30–R48 from the wave and beat reviews, 2026-10-03 and 2026-10-04)

| # | Ruling |
|---|---|
| R1 | Scope: all four layers. Tamheed's own English (skills, references, templates, stock README, tool descriptions, server messages); a discipline skill for package prose; an advisory readiness rule on client prose; guide EN + README + `docs/*.md` + SECURITY + CLAUDE.md + CONTRIBUTING. Frozen: released CHANGELOG entries, `plans/` (except the new brief), `docs/adr`, `docs/history`, `stock-history.json`, `evals/sample-results`, `generated-samples`. |
| R2 | Semicolons banned in every prose surface (Rule 8.1). Code spans, fenced code and frozen records exempt. |
| R3 | Big-bang rewrite. Lint baseline 0 for every rostered file from the day it is rostered. No ratchet. |
| R4 | Client migration: Tamheed-owned text re-emitted, the readiness rule reports, and `/tamheed:ste-rewrite [package]` proposes rewrites row by row with one STOP per batch. Draft/Proposed rows in place with `expect_unchanged`; prompt files in place; immutable rows by supersession. Never silent. |
| R5 | New discipline skill `tamheed:plain-english`; `written-claims` cross-references it. Counts 1 / 17 / 9. |
| R6 | Strict for agent-facing text; STE-flavored for human docs. |
| R7 | Passive voice and compound tenses: advisory in the lint, removed by the rewrite where an actor exists. |
| R8 | `references/vocabulary.md` (actions, terms, names), lint-enforced, drafted from a usage census, settled in one interview round, then frozen for the batch. `GT-` rows extend it per project. |
| R9 | The note sentence the hook parses is reworded; the hook accepts old and new; marker `tamheed:note v5` becomes `v6`; the ACMP brief owns the class-5 change. |
| R10 | MINOR 5.9.0 with a CHANGELOG migration note. |
| R11 | Trigger phrases in skill descriptions survive verbatim. |
| R12 | This batch first; the guide review (plan 175 round 2) after. |
| R13 | Readiness rule `prose-plain-english`, advisory: register statement columns, `prompts/*.md`, the latest handoff; counts per rule with row ids. |
| R14 | Evals: re-aim changed greps; lab beat 33; a deterministic `ste-clean` assertion over Tamheed-owned prompt files; one rubric line. |
| R15 | Port the linter as `server/ste_lint.py` with the MIT notice and `THIRD-PARTY-NOTICES.md`; skill text written fresh. |
| R16 | Waves: (1) tool descriptions + server messages + note, (2) skills, (3) references + templates + stock README, (4) docs + guide. Operator reviews each wave's diff; the advisor reads it first. |
| R17 | Lint 14 reads Markdown and Python runtime string literals via `ast`; `content.py` by import. |
| R18 | One plan per beat, one commit per beat, a `plans/README.md` row each; rows for 170–174 added. |
| R19 | Three accuracy defects fixed first as `fix:` beats (176–178). |
| R20 | ACMP brief 5.9.0: update, migrate preview, `handoff_emit(refresh_stock=true)`, `export_html`, readiness, then a STOP where ACMP's operator chooses whether to run the rewrite. |
| R21 | Lint cap 25 words in both modes; the skill holds steps to 20. Headings and table headers exempt from length, never from semicolons. |
| R22 | Guide: a "Writing discipline" section rendering the vocabulary tables from the file. |
| R23 | The batch ends with push and tag; ask once before the push. |
| R24 | One rubric line on lab-tracker and execution-loop. |
| R25 | Arabic mirrors the English and takes the semicolon and length rules. |
| R26 | Roster, not ratchet: `_STE_SURFACES` and `_STE_PENDING`; a prose file in neither fails the lint; the last wave asserts pending is empty. |
| R27 | `lab/README.md` and `evals/README.md` in scope; `lab/brief.md`, `lab/scenario.md`, `evals/evals.json` exempt. |
| R28 | Runtime string literals only; docstrings and comments exempt. |
| R29 | Allow marker with a mandatory reason; a marker without one is a hard finding; the count is printed. |
| R30 | check = a gate ran, verify = a verdict on evidence, confirm = the operator's word; `validate` rejected in prose, kept in the stage-19 title and the product line as names (plan 179). |
| R31 | retire = rows, remove = files, markers and lines; `delete` and `erase` rejected (plan 179). |
| R32 | Rejected: repair (fix / correct), get and fetch (read), produce (emit / generate / write), decline (refuse / reject) (plan 179). |
| R33 | display, journal, log and reference stay as noun terms, never rejected; verb uses are rewritten by hand (plan 179). |
| R34 | A names-table row for an engine value name (`Validated`, `Invalidated`) does not re-open the vocabulary freeze; each addition is listed in the beat's ledger (wave 2 review, plan 185). |
| R35 | A frontmatter condition split into sentences with its words and their order kept, joiners added, keeps R11; waves 3-4 do not re-litigate the split (wave 2 review, plan 185). |
| R36 | On an unquoted condition word, R8 (the vocabulary) wins over R11: "produce a charter" is "write a charter". Only QUOTED trigger phrases are verbatim (wave 2 review, plan 185). |
| R37 | The vocabulary applies to the spec's own field labels: workflow.md's `Validate:` is `Check:` in all 22 stages and the legend; `docs/workflow.md:161` follows in plan 187 (wave 3 review, plan 186). |
| R38 | A stale count or name met while rewriting the sentence it sits in is corrected in the wave and disclosed in the ledger, not split into a `fix:` beat (wave 3 review, plan 186). |
| R39 | The templates' HTML guidance comments stay as they are, permanently: the extractor drops them by design, they never reach an agent's context, and a filled template removes them (wave 3 review, plan 186). |
| R40 | The plugin and marketplace descriptions and the README tagline carry one both-halves sentence pair: "Turn a project description into a validated, traceable, execution-ready planning and handoff package for Claude Code to implement. Then keep it the record of the build while execution runs." (the plan-175 debt, closed in plan 187). |
| R41 | A wave may name the release it ships in ("v6 since 5.9.0") before plan 189 stamps it; lint 8 greps the current stamp and is unaffected (wave 4a review, plan 187). |
| R42 | Blockquotes follow the structural rules too, although lint 14 skips them (lint 13's precedent): a wave removes their semicolons and splits their sentences, and the linter stays as it is (wave 4a review, plan 187; standing for 188). |
| R43 | A table cell whose header names its parts may end in a one-word sentence ("Label. Caller." under "Meaning · who writes it · when"): the header carries the sense, and the cell is not running prose (wave 4b review, plan 188). |
| R44 | The guide's Writing discipline section renders all three tables of `references/vocabulary.md` (actions, terms, names) with an Arabic twin for every cell, the English cells asserted equal to the file by `build.py` (wave 4b review, plan 188; widens R22's two tables). |
| R45 | `/tamheed:ste-rewrite`: an Approved row of a family with no supersession column (a requirement, a constraint, an assumption, a dependency, a decision) is rewritten in place and stays Approved, only while the change is punctuation or a sentence split; a change of meaning is a new row through the `update` flow. A Promoted lesson is skipped by default like an Approved one, and the latest handoff entry is never edited (lab beat 33's Q0, plan 189 review). |
| R46 | A CHANGELOG release entry carries the UTC date of its release, as earlier entries do: `[5.9.0] - 2026-10-03` (plan 189 review). |
| R47 | A brief's STOP carries the maintainer's recommendation, marked as the maintainer's and not a verdict (D-RECOMMEND-DEFAULT applied to the field brief): for 5.9.0, `GT-` rows first, then Draft and Proposed rows, immutable rows only on opt-in (plan 190 review). |
| R48 | O23 is recorded with its second half: the rewrite skill's missing Approved-row path was the first gap a real agent found that a scripted beat could not have found, in the design record and the brief (plan 190 review). |

Approved with the plan (2026-10-03): the wave protocol (stage, advisor read, operator review, one
commit after the ruling, fix-ups disclosed); beat 33 runs the rewrite skill on a scratch copy and
only the emit on the fixture; the readiness rule reads every register family's statement columns
but not `document_sections.body`; `ste-rewrite` skips Approved ACs with Met verdicts and Approved
lessons unless the operator opts in per row; ledger-first plan files.

## 3. What shipped, per plan

- **176 — `handoff_emit` says what it writes.** `d7ca9f8`. The description names the note, the stock README and `.mcp.json` for a standalone install. README rows for 170–174.
- **177 — the converted-prompt hints name live skills.** `3e10ba1`. Three hints in the `/tamheed:<name>` form, one sentence each.
- **178 — `handoff.md` no longer claims the template twin.** `70e63d9`. The plan-132 test reads the reference too.
- **179 — the vocabulary.** `74a6725`. The census (`evidence/scripts-ste/vocab_census.md`, 16 groups, name positions), four rulings R30–R33, `references/vocabulary.md` with 26 actions, 22 terms and 5 names. Frozen.
- **180 — the linter module.** `b0733b4`. `server/ste_lint.py` (port of upstream `ste-lint.py`, MIT notice, `THIRD-PARTY-NOTICES.md`), 21 tests in the twelfth suite, the four count surfaces, the guide id.
- **181 — lint 14.** `dd1cc85`. The roster (`_STE_SURFACES`, `_STE_PENDING`, the exempt set, `_ste_scope` by rglob), the block in the numbered-comment shape, six lint tests, `lint.14` in the guide, fourteen lints on the page.
- **182 — the readiness rule.** `8ec513b`. `prose-plain-english`, advisory, thirtieth package rule: register statement columns, the project's prompt files, the latest handoff, `GT-` terms as names, counts per rule, the skill cue in the note; `register-liveness` item 22; the guide's `rule.*` id.
- **183 — the two skills.** `a537a1e`. `plain-english` (discipline) and `ste-rewrite` (scenario), the note's skills line, the stock README under `5.9.0`, every count surface (1 / 17 / 9, 27 skills), two tests.
- **184 — wave 1.** `883412b`. 207 hard findings to 0 across 16 rostered files: the 19 tool descriptions, every refusal, every readiness note, every warning, the note as v6 (the hook reads v5 and v6), lint 9 blacklists `tamheed:note v5`; 16 pins re-aimed; the linter learned to read a multi-line literal as Markdown.
- **185 — wave 2.** `8beaecd`. 818 hard findings to 0 across the 27 skills, the glob rostered (43 files, 0 hard, pending 50), every quoted trigger identical, 22 of 23 pins word for word (the 23rd an absence assertion on the fixture), the word-multiset check of every description (`desc_words.py`) showing joiners only plus `produce` → `write`, two names-table rows (R34), one allow marker inside the lint-13 probe test, rulings R34–R36.
- **186 — wave 3.** `3f281eb`. 1,010 hard findings to 0 across 37 files (references, templates, the stock README strict; the server README, CANONICAL, the assets README flavored), six globs rostered (79 files, 0 hard, pending 14), 41 pins word for word, the stock body under `stock-history.json`'s `5.9.0` key, `Validate:` → `Check:` in workflow.md, four count/name corrections (seventeen scenarios, eleven sections, nine discipline skills, the v6 marker).
- **187 — wave 4a.** `f745edb`. 1,262 hard findings to 0 across 13 files (README, SECURITY, CLAUDE, CONTRIBUTING, `docs/*.md`, the lab and evals READMEs, all flavored), seven globs rostered (92 files, 0 hard, pending 1: `content.py`), 21 pins word for word, both manifest descriptions as the both-halves sentence (the plan-175 debt), six count corrections under R38 (twelve suites in README and install, six domain-lifecycle families in entities.md, nine discipline and seventeen scenario skills in entities.md, twenty-five package advisories in architecture.md, the v6 note marker in install.md and design-decisions.md), the blockquote semicolons removed too (the linter skips blockquotes; the five that remained were the slogan and two asides), the lint-14 allow-marker test made count-relative.
- **188 — wave 4b.** `1d4408b`. 1,495 hard findings to 0 over the 1,284 bilingual entries of `docs/guide/content.py` (EN 612 semicolons + 176 long sentences, AR 610 `؛` + 97 long sentences): a mechanical pass through the AST (1,003 entries: `; ` → `. ` with the next clause capitalised, `; and|but|or|so|then` → `, and|...`, AR `؛` → `.`) and a hand pass of 154 entries, EN first and AR mirrored. Lint 14 reads `content.py` by import, every entry under its own language, label `docs/guide/content.py:<id>.<lang>`; `_STE_PENDING = ()` (93 files, 150,617 words, 0 hard). The Writing discipline section: `extract.vocabulary()` through the linter's own table parser, the three tables rendered with the file's EN cells (asserted equal in `build.py`) and 92 new bilingual ids (77 Arabic cells, three paragraphs, headers). One count correction under R38 (24 → 26 companion skills, both languages). 14 pins word for word.
- **189 — the stamp, the evals, lab beat 33.** `90947b8`. `plugin.json` 5.9.0, the CHANGELOG's `[5.9.0] - 2026-10-03` entry (UTC, R46) (MINOR headline, the migration note: no schema migration, the note rebuilt as v6 by `refresh_stock`, `/tamheed:ste-rewrite` opt-in, the hook reads v5 and v6), the six lint-8 surfaces, the stock README body re-keyed under `5.9.0`, `index.html` rebuilt. `evals/pkg_check.py ste-clean`, three eval re-aims (nine discipline skills, `tamheed v5.9.0`, the page's 5.9.0 meta), the `ste-clean` assertion on lab-tracker, two rubric lines (R24). Beat 33: the scratch phase by a real agent through the headless harness (two turns, $2.29, no denial, the hook on both turns under 5.9.0): batch 1 proposed and STOPPED, then on the operator's words one in-place rewrite (ASM-001) and one supersession (ADR-0001 → ADR-0002, approved), counts 14/7 → 10/6; the fixture phase in-process: the guide at 5.9.0 naming nine discipline skills, the note v6, the closing note, the handoff LAST, the page at 5.9.0, gate ready, verify green. The agent found three gaps in the rewrite skill (the Approved non-immutable path, the Promoted lesson in the default-skip list, the latest handoff entry); all three are in the skill now. Evidence: `plans/evidence/lab-continuation-report-189-2026-10-04.md`.
- **190 — the ACMP brief 5.9.0.** `7f11e41`. `plans/briefs/acmp-5.9.0.md` under the strict rules (1,135 words, 0 hard), rostered by its path (`_ste_scope` admits a rostered file under an exempt prefix, with a test that the 5.8.1 brief is not scanned). Every class replayed on a `git archive` copy of the field at `8b7d8bd1` (`plans/evidence/scripts-ste/acmp_replay10.py`, its output beside it): `server_info` 5.9.0 / 7; verify `review_exported_by 5.8.1`; 24 advisories, `prose-plain-english` fail with 2,342 semicolons, 3,602 long sentences, 631 vocabulary hits over 1,290 texts (1,146 named, 50 shown); the emit with `refresh_stock` refreshed the guide and rebuilt the note as v6 (14 of 41 lines, the first sentence, the skills line); the export 5 added 4 removed, 11 KB, csv unchanged, exported by 5.9.0; the hook over the v5 note and the v6 note, both `version=5.9.0`; `ste-clean` 73 hard before the emit, 0 after, four project files skipped by name; the wire's three contract lengths unchanged. The brief owns O23 (the rewrite skill's missing Approved-row path) and the class-5 change of 5.8.1 (the note changes). The STOP: whether `/tamheed:ste-rewrite` runs, with its cost on the copy (about 115 batches) and the `GT-` route named first. The guide's release recipe gains step 9 (roster the brief).
- **191 — the release.** (the commit this record lands in) The batch record closed (sections 2-5, the rulings through R48, the SHAs), `plans/README.md`'s cycle heading and sixteen rows with SHAs, the memory file, `check.py` green, the commit; then, on the operator's single word, the push, CI on every job, the tag `v5.9.0` on the CI-green commit, and `git diff v5.9.0 HEAD -- plugins/tamheed` empty. Plan 175 round 2 resumes after it.

## 4. Errors owned

- **184.** Bash heredocs unescaped backslashes twice (a test insert, a lint regex); every script since is written to a file first. The tool-owned test failure was a pin (capitalisation), not instability, proved by two identical emits.
- **185.** A code span broken across a line in loop-iteration (the token invariant caught it). "stored as" dropped from the front door's first sentence and an example list rewritten as a definition in operator-interview (the description multiset check caught both before the review). A `sed` edit of a regex dropped a backslash (the third shell mangling of the batch). Plan 182 had appended register-liveness item 22 after the closing step; renumbered here. The lint-13 probe's deliberate semicolon failed lint 14 on the first gate run after the roster move; fixed in the test with an allow marker, not in either lint.
- **186.** Three code spans and two pinned phrases broken across lines by my wrapping (the token invariant and the pin tool caught every one; a contract test failed once on a pin). One "must" weakened to a plain statement in handoff.md (the modal counter caught it; restored). Rule from here: a code span or a pinned phrase never straddles a line break.
- **187.** A multi-file edit script failed on its first assertion and silently skipped the manifest and roster edits behind it; the gate's `pending 14 surfaces` line exposed it, and the two edits were redone in a script of their own. Rule from here: one script, one file, or assert-all-first. Four pinned phrases wrapped across lines (three in README from the pre-compaction rewrite, one in architecture.md from the splitter) and one modal (`unless`) dropped in entities.md; the pin tool and the modal counter caught every one, all restored. A count I wrote from memory (twenty-four package advisories) was wrong; the engine says twenty-five, measured with the guide's own extractor before the ledger was written.
- **188.** The AST tool's first run changed nothing (`TEXT` is an annotated assignment, not `ast.Assign`), and its second run would have corrupted the file (`ast` columns are UTF-8 byte offsets, the text is characters) had `ast.parse` not refused the result before the write; both fixed before any byte landed. The lint label the helper built was dropped by the gate's own loop (`rel:line`), so the two new probe tests were red until the loop printed the finding's file. A test asserted 25 actions as 26 from memory; the file has 25 (the memory file said 26). The chain rule from 187 held: the two edits a failed script skipped there were redone first here.
- **189.** The rewrite skill shipped in plan 183 with no path for the commonest Approved row (a requirement or a decision has no `superseded_by`), and the planning review of 183 did not catch it; the real agent did, in its first batch. It was the first gap a real agent found that a scripted beat could not have found (R48). The T2 words were written before T1 ran and had to be rewritten after reading the agent's STOP (the words answer the agent's question, not the maintainer's guess). The fixture's page date moved to 2026-10-03 (UTC) while the CHANGELOG entry carried 2026-10-04 (the operator's date) until the review set it to the UTC date (R46). The first fixture phase wrote a note and a handoff with five semicolons and long sentences, against the rule this release ships (a beat script's `pe()` texts are agent prose under the same rules); the advisor caught it, the fixture was restored from HEAD and the phase re-run. The T2 operator's words on Q0 were the harness operator's (the maintainer's), written into the skill before the real operator ruled; put to the operator at the review and accepted as R45.
- **190.** The roster entry for the brief was written before the scope helper could see it: `_ste_scope` skips every path under `plans/`, so a rostered path there was never linted until the helper admitted exact rostered files. Caught while writing the test, before the gate ran. The replay's emit wrote `.mcp.json` into the copy because the in-process server is standalone there; the brief says a plugin-hosted server writes none, as the 5.8.1 brief had measured.
- **191.** None at the time of writing; the push and the tag are recorded in this plan's ledger after they land.

## 5. Not built, by ruling or on purpose

- **Arabic grammar beyond the two structural rules.** The lint checks Arabic for `؛` and sentence length only (R25). Every rewritten English entry was mirrored into Arabic, and the Arabic was never reviewed as Arabic (the plan-175 ruling stands).
- **ASD's dictionary.** Issue 9 forbids redistribution; `references/vocabulary.md` is Tamheed's own, and the vocabulary rule is advisory under the flavored mode.
- **Rewriting the frozen set** (R1): released CHANGELOG entries, `plans/` (except the 5.9.0 brief), `docs/adr`, `docs/history`, `stock-history.json`'s older bodies, `evals/sample-results`, `generated-samples`, `lab/brief.md`, `lab/scenario.md` beats 1-32, `evals/evals.json`'s fixtures and `THIRD-PARTY-NOTICES.md`. The lint exempts them by path.
- **The linter reading blockquotes** (R42's third option, declined): blockquotes follow the rules by hand, and lint 13's precedent (blockquotes dropped) stands.
- **Expanding the 85 one-word writer cells** of the guide (R43): the column header carries the sense.
- **The readiness rule over `document_sections.body`** (charter-class prose, human-facing): excluded by the approval checkpoint; the rule reads the register statement columns, the project's prompt files and the latest handoff.
- **An engine rewrite of any client's prose.** The rule reports; `/tamheed:ste-rewrite` proposes on the operator's word, batch by batch; the field's STOP is its operator's (R20, R47).
- **A supersession column for requirements, constraints, assumptions, dependencies and decisions.** R45 took the in-place path for structure-only changes instead of a MAJOR-shaped schema change.
- **A `newest` parameter on `entity_query`** (R50 stands) and **`server_info` returning the descriptions** (R58 stands).
- **The engine candidates E1/E2 of plan 175 and plan 175 round 2** (the guide review): after this batch (R12).
- **A reload or restart of the field's sessions by the maintainer**: the route is in the brief; the field runs it.

