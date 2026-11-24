# Plan 255: missed places, evidence (2026-11-24)

Counts and commands only. Every number below is re-run by `scripts-255/measure_255.py` (stdlib, read-only on
git, pinned commits). It writes `scripts-255/results/measure.json` and exits 1 if a number differs from this file.

## The baseline (from plan 254)

- Plan 254's picker (the word fix/fixes/fixed in the subject, 1 to 6 code or text files) gives **48 commits** from
  2026-07-01 up to `451ff94`.
- Its two blind raters marked **16 of the 48** as finishing an earlier change that had missed a place
  (`scripts-254/rated_missed_places.json`; they agree on 47 of 48, kappa 0.956).
- Both raters name the same origin commit for **8** of the 16: fixes 01, 03, 21, 24, 25, 26, 39 and 48.

## The measurements of the plan 255 review

| Measure | Result | Pinned at |
|---|---|---|
| Commits since July that the 254 picker did not rate, named for a fix or a correction (1 to 12 code or text files, `release:` left out) | **18** (7 with the word fix, 11 with a correction word) | `ec5686a` |
| The old-text signal: a removed line, at least N characters and 2 identifiers, not re-added, with 1 to C copies left in kept files (tests and records left out) | fires on **44, 42 and 40** of 100 commits at N/C = 20/5, 30/3, 40/2. Median 0.14 s a commit | the 100 commits ending at `451ff94` |
| Origin-to-fix gap of the 8 agreed origins, in commits | 1, 135, 11, 1, 36, 34, 3, 13 (0 to 50 days) | `rated_missed_places.json` |

**What this decided.** At about 1 testable miss per 50 commits, the operator's noise line (at most 10
interrupted commits per caught miss) allows a firing rate of about 20% at perfect recall, and about 7% at a
recall of 1 in 3. The signal fires on about 40%, so a commit-time script cannot pass. The operator ruled
**rule only**. Co-change stays "not now"; it was never measured against the noise line.

## Outside sources (search snippets and abstracts, not full papers)

| Source | Finding |
|---|---|
| Park, Kim, Ray, Bae, MSR 2012 | 22 to 33% of resolved bugs needed more than one fix attempt. Counted per bug, not per fix commit |
| Zimmermann et al., ICSE 2004 (ROSE) | Commit-time warnings at confidence 0.9: recall about 4%, precision over 50%, on simulated omissions |
| Meng, Kim, McKinley, ICSE 2013 (LASE) | Systematic-edit locations from examples: 95 to 99% precision, 88 to 89% recall (by version), Java, a curated set |

## The rule (in `CLAUDE.md`, linted with 0 findings)

The section "Before a commit: the places a change leaves behind": search the old form and change every copy
that must match it; dated records keep their old text; read same-prefix functions; search the text that states
a behaviour, `SECURITY.md` included.

## The tally (frozen 2026-11-24, due 8 weeks after T0)

- `measure_255.py --tally T0 END OUT` picks the fix commits after T0 with the 254 picker. It writes one entry
  each: the message, the `-U4` diff (420 rows a file), who wrote the changed lines, and a suggested origin
  (a suggestion only). The operator marks each entry: a missed place, yes or no.
- **Reading:**
  - Fewer than 10 picked fixes means "too few to read".
  - A count inside the central 95% binomial range for that number of fixes at 16/48 means "no visible
    change". For 20 fixes, that range is 3 to 11.
  - A count below the range means "lower, not causal".
  - **"No visible change" does not mean the rule failed.** At 20 fixes the baseline expects about 7 misses, and
    only 0 to 2 would read as lower. The tally can show a large drop, not a small one.
- Reported as "one window, different judges" (the operator, not the Opus raters). The rule stays unless the
  operator removes it.
