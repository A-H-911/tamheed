# Plan 255: a missed-places rule, and a free tally

> **Approved by the operator on 2026-11-24** (revised after a devil's-advocate review). Executed through
> step 4; step 5 (commit and push) on the operator's word; step 6 (the tally) is due 8 weeks after T0.
> No Tamheed version, no release, nothing in `plugins/`. Evidence: `evidence/missed-places-2026-11.md`.

## Context

The raters of plan 254 marked **16 of the 48 picked fix commits since July** as finishing an earlier change that
had missed a place. **My grouping** of the 16, from the raters' free-text places:
- 10 were the same guard or idiom missing in a sibling spot (4 in the same function, 6 in sibling functions);
- 6 were text or registered strings still stating the old behaviour;
- `SECURITY.md` was among the missed places 3 times.

The raters' own labels differ: 12 code-code, 3 code-text and 1 text-text. Fixes 03 and 12, which I count as text,
are labelled code-code.

The first draft of plan 255 put a rule live and tested a script in shadow. The review measured that the script
cannot pass your noise line (section 1), so you ruled **rule only, with a free tally that you mark.**

**Outcome:**
- a 4-line rule in `CLAUDE.md`, read by every session in this repository;
- after 8 weeks, a list of the window's fix commits that you mark, counted against 16 of 48.

## Rulings (operator, 2026-11-24)

| # | Ruling |
|---|---|
| H1 | **Rule only.** No script, no raters, no shadow trial. **Co-change (P3) stays "not now"** (your 2026-11-23 ruling). It is not part of this plan |
| H2 | The rule lives in **`CLAUDE.md`**. Files: `CLAUDE.md` and `plans/` only |
| H3 | **A free tally after 8 weeks:** I list the window's fix commits, and you mark each one as a missed place or not |
| H4 | Superseded by H1: the 15 USD budget, the held-out set, and the noise line of 10 interrupted commits per catch. The noise line did its job: it stopped the script before any spend |
| Standing | Commit or push only on your word. Check main's own CI after a push. No private data in committed files. Nothing from the PARKED plan |

## 1. Weaknesses of the first draft (found in this review)

1. **The script could never pass the noise line.**
   - The old-text signal fires on **44, 42 and 40 of the last 100 commits** at three tightness settings. Tamheed
     keeps many deliberate copies: the three READMEs, briefs, references.
   - At about 1 testable miss per 50 commits, a limit of 10 interruptions per catch allows a firing rate of
     about 20%, even at perfect recall. At the planned recall of 1 in 3, it allows about 7%.
   - The draft would have spent about 13 USD to confirm a failure that cost nothing to measure.
2. **My numbers misled two of your rulings.**
   - "About 30 unrated commits": the picker finds **18** (7 with the word fix, 11 with correction words). Several
     of the 11 are features whose subject contains "stale" or "drift".
   - "About 7 testable misses from 20 fixes": only 8 of 48 fixes had an agreed origin, so about 3.
3. **The script only automated the rule.** Searching for the old form, reading same-prefix functions, and
   searching the stating text is what the rule already asks a session to do.
4. **The draft rule could damage records.** "Change every copy" would push a session to edit dated records
   (`plans/`, `CHANGELOG.md`, the stock history), which must keep their old text. Asking for a commit-message
   note "why it stays" would have added boilerplate to about 40% of commits.
5. **The draft carried an unlinted, stale statistic** ("one fix commit in three"). It is really 16 of 48
   picked commits, and it ages.
6. **It overclaimed in verification.** A script cannot prove that a hash predates a replay inside one commit.
7. **It listed unverified hook facts as "Confirmed".** The agent's copy may have been cached, and the plan
   never used them.
8. **The selection effect was real** (the side agent's note). The rule and the script used the same ideas.
   - The origin-to-fix gap of the 8 agreed origins is 1 to 135 commits, or 0 to 50 days.
   - If fixes were spread evenly over an 8-week window, about two-thirds of the window's misses would trace back
     to changes made after T0. This is computed from the day gaps; it rests on 8 cases.

## 2. Assumptions

**Confirmed (read or run in this review):**

| Fact | Evidence |
|---|---|
| The 254 picker (the word fix, 1 to 6 code or text files) gives exactly 48 commits up to `451ff94` | replicated the rule from `fixes_254.py` |
| No commit after `451ff94` names a fix | `git log 451ff94..HEAD` |
| The old-text signal fires on 44/42/40 of **the 100 commits ending at `451ff94`**, at 20/30/40 characters and at most 5/3/2 copies. Tests and records are excluded. Median 0.14 s a commit | stdin probe, read-only |
| The unrated set is 18 commits at `ec5686a` (HEAD during this review) | the same probe |
| `docs/adr/` and `docs/history/` exist. `CLAUDE.md` says ADRs are superseded, never edited | `ls`, `CLAUDE.md` |
| Origin-to-fix gaps for the 8 agreed origins: 1, 135, 11, 1, 36, 34, 3 and 13 commits (0 to 50 days) | `git rev-list --count` |
| The amended rule (below) gives **0 lint 14 findings** in flavored mode with the vocabulary | `ste_lint.lint_blocks` |
| `CLAUDE.md` is a rostered flavored surface. No test pins its content. `test_check_lints` copies the tree and counts its markers | `check.py:82`, grep of `tests/` |
| The 254 bundle format: `-U4` diffs capped at 420 rows a file, a blame summary, bundles of 42,000 characters | `fixes_254.py:40-80` |

**Researched (search snippets and abstracts, not full papers; the deep-research skill was not run because it
writes folders into this repository, which lint 14 would fail):**

| Source | Finding |
|---|---|
| Park, Kim, Ray, Bae, MSR 2012 | 22 to 33% of resolved bugs needed more than one fix attempt (Eclipse, Mozilla). **Counted per bug, not per fix commit**, so it is not the same measure as 16 of 48 |
| Zimmermann et al., ICSE 2004 (ROSE) | In error-prevention mode (a warning at commit time, confidence threshold 0.9), recall was about **4%** at over 50% precision. That is on **simulated** omissions (one entity left out of a past change), in 2004 projects, not on real incomplete changes |
| Meng, Kim, McKinley, ICSE 2013 (LASE) | Locating systematic edits from examples: 95 to 99% precision and 88 to 89% recall, depending on the version. It uses Java edit scripts on a curated set, a different technique from text search |

**My reasoning, not evidence:** "Only what is pushed acts" rests on one tool (0 Graphify calls in 24 sessions).
A rule in `CLAUDE.md` is pushed into every session, but whether sessions follow it is not observed.

**Rejected:** the script would add value over the rule · the held-out set holds about 30 commits · 20 window
fixes give about 7 testable misses · the tally can show cause.

**Unresolved, stated in the result:**
- Whether sessions follow the rule. Commit messages show it only in part.
- Whether a lower share in the window is due to the rule.
- **Your marks and the Opus raters' marks are different judges**, so the comparison with 16 of 48 is rough.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The rule leads a session to edit dated records | The rule names them: `plans/`, `CHANGELOG.md`, `docs/adr/`, `docs/history/` and the stock history keep their old text. Generated files are already covered by the "never hand-edit" invariants |
| The rule is read the wrong way round | "Change every copy that must match it", not "...that must stay the same" (the first draft could be read as "change the copies that must not change") |
| The tally is read from noise | **Frozen now:** fewer than 10 picked fixes in the window means "too few to read". A count inside the 95% range of a binomial with the window's count and 16/48 means "no visible change". The script computes the range for the actual count |
| The rule fails the gate | It is already linted: 0 findings. `check.py` runs on 3.13 and 3.10 before the commit |
| The tally is read as proof | It is reported as "one window, not causal, different judges". The rule stays unless you remove it |
| I tilt the tally | **Frozen now:** the window, the picker, what each entry shows, and the comparison. My suggested origin is shown as a suggestion, and the mark is yours |
| The tally is forgotten | A memory note with T0 and the due date. At each session start I check whether it is due |
| The rule's tokens and searches | About 80 tokens a session, plus a few searches before a commit. Accepted |
| Private data in committed files | The tally lists public commits only. Your marks are recorded as yes or no |

## 4. Changes made, and why

| Change | Why |
|---|---|
| The script, the shadow replay, the raters and the critic are dropped | Weakness 1: measured to fail the noise line. Weakness 3: the rule covers it |
| Co-change stays "not now", outside this plan | Your ruling. Co-change was never measured against the noise line |
| The rule names the dated records, says "must match it", and drops "say why it stays" | Weakness 4, and the advisor's reading of the draft |
| The tally has a floor and a no-change range, frozen now | About 20 fixes cannot separate 33% from 20% |
| The measurements are pinned to `451ff94` and `ec5686a` | They must reproduce after T0 |
| The statistic is not in `CLAUDE.md` | Weakness 5 |
| The tally is marked by you, for free | Your ruling H3 |
| The review's measurements become a small reproducible script | Their numbers are cited in the plan, so they must re-run |

## 5. Refined execution

| Step | Work | Output | Passes when |
|---|---|---|---|
| **1 Record the measurements** | `plans/evidence/scripts-255/measure_255.py` (stdlib, `python -I`, read-only on git). It re-runs this review's numbers at pinned commits: the picker count (48 up to `451ff94`, 18 unrated at `ec5686a`), the firing rate at the three settings (the 100 commits ending at `451ff94`), and the 8 origin gaps. A `--tally` mode, used in step 6, lists the window and computes the no-change range | `results/measure.json`, evidence file `plans/evidence/missed-places-2026-11.md` | it reproduces 48 · 18 · 44/42/40 of 100 · the 8 gaps exactly |
| **2 The rule** | Add the section below at the end of `CLAUDE.md` | the edit | lint 14 passes |
| **3 Gate** | `python check.py` on Python 3.13 and 3.10 | logs | ALL CHECKS PASSED on both |
| **4 Record** | `plans/255-missed-places-rule.md`, a `plans/README.md` row, and a memory note: T0, due date T0 + 8 weeks, the frozen tally rule | files | `git status` shows only these files and the step 1 files |
| **5 Commit and push (on your word)** | One commit. **T0 = this commit.** Push, then check main's own CI run | sha, run id | 12 of 12 jobs green |
| **6 The tally (due T0 + 8 weeks)** | Pick the window's commits with the 254 picker rule. For each, show the message, the `-U4` diff (420 rows a file), the blame summary, and the earlier commit it may complete (my suggestion). You mark it as a missed place or not | the count and share against 16 of 48, with the split by origin before or after T0 | **frozen reading:** fewer than 10 picked fixes means "too few to read"; inside the 95% binomial range means "no visible change"; below it means "lower, not causal". Labelled "one window, different judges". Then your ruling: keep or remove the rule |

**The `CLAUDE.md` section** (linted: 0 findings):

```
## Before a commit: the places a change leaves behind

- Search for the old form of each line you changed. Change every copy that must match it.
- Dated records keep their old text: `plans/`, `CHANGELOG.md`, `docs/adr/`, `docs/history/` and the stock history.
- Read the functions that share the changed function's name prefix, such as `package_*` or `gate_*`.
- When behaviour changes, search the text that states it: tool descriptions, constants, references and `SECURITY.md`.
```

**Files.**
- **New:** `plans/255-missed-places-rule.md`, `plans/evidence/missed-places-2026-11.md`,
  `plans/evidence/scripts-255/measure_255.py` and `results/measure.json`.
- **Changed:** `CLAUDE.md` (one section at the end) and `plans/README.md` (row 255).
- **Not touched:** `plugins/`, `tests/`, `check.py`, `.claude/`, `.gitattributes`, `docs/`, `index.html`, CI,
  and every plan 254 file.

**Cost:** about 0 USD. No agents. Only this conversation's own work.

## Verification

- `measure_255.py` reproduces the numbers in sections 1 and 2.
- `check.py` passes on 3.13 and 3.10 with the new section.
- Main's own CI on T0 is green.
- `git status` before the commit lists only the files above.
- At the tally, `measure_255.py --tally` gives the same list and range on a second run.

## 6. Approval checkpoint

Approving this plan approves H1 to H3 and steps 1 to 4:
- the measurement script;
- the `CLAUDE.md` section exactly as shown;
- the plan record, the README row and the memory note.

**Step 5 (commit and push) waits for your word.** Step 6 is due 8 weeks after T0. It is free, and you mark it.
This approves **no** script in the workflow, no hook, no change to `.claude/settings.json`, `check.py` or
`plugins/`, no agent spend, no release, and nothing from the PARKED plan.
