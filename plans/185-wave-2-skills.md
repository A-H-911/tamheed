# Plan 185: wave 2 - the 27 skills

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R11, R16 (wave 2), R26. Wave protocol as plan 184: rewrite, lint 0 hard, invariants,
> pin ledger, gate, stage, advisor read, operator review, one commit.

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (descriptions pick the skill; pinned phrases) - **DONE: approved as staged 2026-10-03 (rulings R34-R36 in the batch record)**

## Scope

`plugins/tamheed/skills/*/SKILL.md`, strict, English: the front door, 17 scenario skills, 9
discipline skills. The roster moves the glob from pending to rostered. Every skill description is
quoted verbatim into the guide, so `index.html` rebuilds in this commit.

## What shipped

- Baseline before the wave (`ste_lint.py --mode strict` over the 25 skills that existed before
  plan 183): 818 hard findings. 372 semicolons, 367 long sentences, 78 vocabulary, 1 phrasal verb
  ("Kick off", slice-kickoff). The two skills of plan 183 were born clean.
- After: 27 files, 28,570 words, 0 hard, 200 advisory (passive voice and present perfect, never
  flagged as hard).
- The roster: `("plugins/tamheed/skills/*/SKILL.md", "strict", "en", ())` moved from
  `_STE_PENDING` to `_STE_SURFACES`. Gate line after the move:
  `lint: plain English (43 files, 37644 words) 0 hard, advisory passive-voice=251 present-perfect=25, allow markers=0, pending 50 surfaces`.
- Method, per file: the file rewritten whole, linted, the remaining long sentences listed with their
  word counts, patched by scripts from files (never the shell), re-linted. Rejected words swapped per
  the frozen vocabulary: delete → remove (files) or retire (rows), fetch/get → read, produce → write
  or generate, repair → fix, validate → check, decline → reject, forward → onward, launch → start.
- `references/vocabulary.md` names table: two rows added, `Validated` and `Invalidated` (verdict
  values of experiments, hypotheses and POCs, with Invalidated, Inconclusive, Pending). The linter
  read them as inflections of the rejected `validate`. A name of an engine value cannot change in a
  MINOR. This edits the frozen file (R30-R33). Ruled at the wave review, R34: a names-table row
  for an engine value name does not re-open the freeze, and each addition is listed in the beat's
  ledger.
- `tests/test_check_lints.py`: the lint-13 probe's negative control keeps a semicolon on purpose
  (the window must stop at one). The skill it writes into is now rostered, so the probe carries
  `<!-- ste:allow semicolon: lint-13 probe, the window must not cross a semicolon -->` above the
  block, as a real author would. The gate's own `allow markers=0` is unchanged: the marker exists
  only inside the test's copy.
- `index.html` rebuilt (the 27 descriptions are quoted into the guide).

## Trigger protocol (R11)

`evidence/scripts-ste/triggers-185.md` (before) and `triggers-185-after.md` (after). Every quoted
trigger phrase is identical. The "Use before ..." and "Invoke ..." conditions kept their words and
lost their semicolons: a condition that was one sentence with four clauses is now two to four
sentences, and the script (which reads the first sentence of each) lists each separately. One
punctuation change in the front door: the em dash before `even if the word "Tamheed" is never said`
is a comma. The front door's "produce a charter" is "write a charter" (rejected verb, not a quoted
trigger).

The script reads first sentences, so it cannot attest to the words of a split condition. The
discriminating check is `evidence/scripts-ste/desc_words.py HEAD`: the word multiset of every
frontmatter description, lowercased, punctuation stripped, before against after. Result: 17 of 27
descriptions differ, and every difference is a joiner (it, is, that, the, and, or, also, then, this,
are, use, holds, covers, goes, includes for including, registers for register) except two:
- the front door: `produce` → `write` (R8, the vocabulary, against R11, the condition's words).
  Ruled at the wave review, R36: R8 wins on an unquoted condition word, and only QUOTED trigger
  phrases are verbatim. R35 (same review): a condition split into sentences with its words and
  order kept, joiners added, keeps R11.
- operator-interview: the parenthetical list of examples after "an approval" became a sentence. My
  first form read as a definition ("The approvals are a scope change, ..."), corrected before the
  review to "A confirmation or an approval covers a scope change, ...". The words of the list are
  unchanged.

The front door's first sentence keeps "validated" because the names table (plan 179) holds the
product line `validated, traceable, execution-ready` (README and plugin manifest) as a name. The
linter masks a name before the vocabulary rule, exact and case-sensitive. A probe description with
"A validated package" is flagged, so the pass is the names row, not a hole.

## Pin ledger

`evidence/scripts-ste/pins-185.md` before, `pins_missing.py` after: 22 of 23 pinned phrases still
occur. The one reported missing, `Loop guard — the brake` (evals.json L1750-1752), is a
`grep-tree-absent` assertion on the lab fixture's `prompts/` folder: it asserts the phrase is
ABSENT there. The heading now reads "Loop guard: the brake" and the assertion is about the fixture,
so nothing moves. The pin tool is a presence check and cannot tell the two apart.

Kept word for word: `not yet answered`, `git status --porcelain -uall`, `Every gate is row-level`,
`Search finds candidates` (its semicolon dropped: the needle is the three words), `package_unlock`,
`omitted_columns`, `/tamheed:slice-kickoff`, `/tamheed:package-onboarding`, `STOP for operator
approval`, `` `scope-change` row (`SC-`) FIRST ``, `which words of the trigger`, `no v2 activity
recorded yet`, `for the rest`, the register-liveness numeric sentences.

## Kept as-is (the invariants, `wave_invariants.py HEAD`)

Token sets and modal counts per file against HEAD. Every difference below is deliberate:

| File | Difference | Why |
|---|---|---|
| integrity-check | `foreign: []` → `foreign` + `[]` | one code span became two: "`foreign` must be `[]`" |
| loop-iteration | new `package_open` | the resume block now names its tool: "The `resume` block of `package_open`" |
| measurement-evidence | can 6→5 | "can return several rows" → "may return several rows", a hedge for a hedge |
| package-onboarding | never 7→6 | "never `data/*.jsonl`, never rows you pasted" → "never reads `data/*.jsonl` or rows you pasted by hand", one never over both |
| reading-the-record | DELETES → DROPS | `delete` is rejected |
| register-liveness | new `23` | the closing step renumbered: plan 182 appended item 22 after "22. Close the sweep" |
| skill-promote | ` — CLUSTER` → `. CLUSTER` | dash to full stop |
| tamheed (front door) | QUOTED → QUOTE; `; ` gone; new `references/vocabulary.md`, `tamheed:plain-english`; never 27→26 | the imperative form; the reference table gained the vocabulary row; the discipline list names the new skill; "never `data/*.jsonl`, never a pasted display" → "never reads `data/*.jsonl` or a pasted display" |
| test-evidence | IMPROVES → IMPROVE | "When the work IMPROVES an existing failure … the difference is" → "The work may IMPROVE … Then the difference is": the condition lives in "Then" |
| written-claims | new `tamheed:plain-english` | the one-line cross-reference (plan 183 scope, landed here) |

No hedge was promoted. Every modal drop is two clauses merged under one modal.

## Errors owned

- A code span broken across a line (`git log\n--oneline -10`) in loop-iteration: the invariants
  caught it (`resume` "gone", `10` "new"); the span is on one line now.
- Plan 182 appended register-liveness item 22 after the closing "22. Close the sweep"; this wave
  renumbered the closing step to 23.
- The lint-13 probe test failed on the first gate run after the roster move (its deliberate
  semicolon). Fixed in the test with the allow marker, not by weakening either lint.
- The front door's "stored as a relational package" had lost "stored" in the first rewrite ("It is
  a relational package"). The multiset check found it; the sentence reads "It is stored as a
  relational package" now.
- The operator-interview description's example list was first rewritten as a definition (above).
- A `sed` edit of a regex in `desc_words.py` dropped a backslash and made the pattern match whole
  phrases. Rewritten from a file. Third mangling of this kind in the batch: scripts come from files,
  never from the shell.

## Validation
- Red: the roster move (818 hard before the rewrite).
- Green: `python check.py` ALL CHECKS PASSED (12 suites, 14 lints, canonical, evals);
  `wave_invariants.py HEAD` (table above); `pins_missing.py` (one presence-check false positive,
  explained); `triggers.py` before and after (quoted phrases identical).
