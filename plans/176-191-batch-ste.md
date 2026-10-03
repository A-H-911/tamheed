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

## 2. Rulings (R1–R29, interview 2026-10-03; 32 answers)

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

Approved with the plan (2026-10-03): the wave protocol (stage, advisor read, operator review, one
commit after the ruling, fix-ups disclosed); beat 33 runs the rewrite skill on a scratch copy and
only the emit on the fixture; the readiness rule reads every register family's statement columns
but not `document_sections.body`; `ste-rewrite` skips Approved ACs with Met verdicts and Approved
lessons unless the operator opts in per row; ledger-first plan files.

## 3. What shipped, per plan

- **176 — `handoff_emit` says what it writes.** `d7ca9f8`. The description names the note, the stock README and `.mcp.json` for a standalone install. README rows for 170–174.
- **177 — the converted-prompt hints name live skills.** `3e10ba1`. Three hints in the `/tamheed:<name>` form, one sentence each.
- **178 — `handoff.md` no longer claims the template twin.** `70e63d9`. The plan-132 test reads the reference too.
- **179 — the vocabulary.** (this commit) The census (`evidence/scripts-ste/vocab_census.md`, 16 groups, name positions), four rulings R30–R33, `references/vocabulary.md` with 26 actions, 22 terms and 5 names. Frozen.

## 4. Errors owned

(none yet)

## 5. Not built, by ruling or on purpose

(filled at close-out)
