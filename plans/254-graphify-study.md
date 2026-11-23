# Plan 254 (REVISED 2026-11-23, after a devil's-advocate review): the Graphify study

> **Approved by the operator on 2026-11-23. Executed through the STOP and the A/B; section 7 holds the results.** Replaces the finished 6.8.0 plan in this file (its U and V rulings are in
> `plans/249-field-round-6.8.0.md`; V6 never existed). The PARKED plan is untouched and UNAPPROVED.
> **No Tamheed version, no release, nothing shipped in the plugin, no change to your installed Graphify.**

## Context

You asked me to read all of [Graphify](https://github.com/Graphify-Labs/graphify), understand it, and
propose justified ways to use it while BUILDING Tamheed. This plan is the **study**: read, measure,
then propose in a second interview. Adopting anything is a separate approval.

**Your four goals**, the only yardstick: **missed places · session start cost · texts that disagree ·
a map for you.**

**Words used here.** *Map*: Graphify's `graph.json` and its pages. *No-model*: built with no language
model. *Seed*: the file or symbol being changed. *Place*: a file, or one function or heading in a file
over 800 lines. *Hint*: one place a tool suggests. *Rival*: plain search, pyright references, or git
co-change. *STOP*: the point where nothing more is spent without your word.

## Rulings (operator, 2026-11-22/23)

| # | Ruling |
|---|---|
| G1 | All four goals count |
| G2 | Study first, then proposals |
| G3 | Models read every distinct source, test, doc, skill, translation and image. A script reads every byte of the seven machine-written dumps. Copies are proven by git hash. **After the STOP the default is to read on. Only your word ends it early** |
| G4 | Graphify 0.9.115 (`3671f31`) on scratch copies. Your 0.9.7 and the real repo stay untouched |
| G5 | **Deciding** Opus 5.5 high · **bulk** Sonnet 5.5 medium · **light** Haiku 5.5 medium · **judgement** Opus 5.5 high |
| G6 | Agent calls in waves, at most 8 at once. Readers have Read, Grep and Glob only |
| G7 | **Docs pass: decided at the STOP**, after the free count of what it could ever see *(replaces "as Graphify does it, no limits", which rested on my wrong framing)* |
| G8 | All four ties may be proposed if the numbers support them: agent hooks, git hooks, a map in git, a check |
| G9 | Safety reading → free trial → **STOP** → the rest |
| G10 | A clear win, fixed before any run. **For missed places Graphify must beat the BEST rival** *(stricter than before)* |
| G11 | A/B: 6 tasks × 2 arms × 2 repeats, Opus 5.5, at most 15 USD, **asked separately after the STOP** |
| G12 | 80 USD, ask at 60, **in stages**: about 18 (14–22) to the STOP, then the reading, then A/B and docs pass one by one. It covers agents and headless sessions, not this main conversation |
| G13 | Record in `plans/254` and one evidence file, committed only on your word |
| G14 | **Session start line: at least 25% less text read, no fewer right answers, gap larger than the repeats' spread** *(replaces "half")* |

## 1. Weaknesses of the original plan

1. **The trial would have measured nothing for one goal.** `extract --code-only` skips every document
   (`cli.py:4795-4802`). The no-model Markdown links come from `graphify update` (`watch.py:2644-2660`).
2. **You were asked the wrong question about the docs pass, twice** (see G7).
3. **The cost was low by about 1.6×.** Transcripts here show about 2.2 source bytes a token (I used
   3.7) and a 43k-token start for every agent. "20k-token" bundles would have been about 34k, and
   Read refuses anything over 25k.
4. **Graphify was compared only with plain search.** `pyright` is installed and enabled here. Git
   co-change is about 40 lines of standard Python. Either could win.
5. **"Half the tokens" was unreachable by design,** and "half the cost" was hidden by fixed overhead.
6. **The safety check could not pass.** "No difference in `~/.claude`" fails always: this session
   writes there. A dead proxy proves little.
7. **The check test was rigged.** "Names a place the commit did not touch" is true of nearly every commit.
8. **The failure list had no defined seed** and F2's load (about 2.9 MB) was never sized.
9. **"Texts that disagree" was undefined.** Some of the 17 have one location, some sit in Python
   strings, some are text against engine behaviour. No document map can see those.
10. **Overstated lines of mine:** "Bedrock would send the docs" (it would choose Bedrock, then fail:
    `boto3` is absent, `llm.py:2168`). "A hidden folder is skipped by the gate" (lint 14 skips it, but
    `tests/test_check_lints.py:9-17` **copies** it on every gate run). "Haiku 0.10/0.50" (5× above
    100k tokens). "Two git hooks" (four). "0.9.7 never used" (no trace found, which is weaker).
11. **The map's scope was undefined.** 152 of 201 Python files are `plans/evidence` scripts. They would
    flood the map.
12. **`/graphify` in this session loads the July 0.9.7 skill**, not 0.9.115.
13. **A file-level replay would not discriminate.** 172 of 281 replayable commits (61%) touch the server,
    the contract test or `content.py`. Any tool that names those three looks good.

## 2. Assumptions

**Confirmed (read at `3671f31`, run, or measured here; no sub-agent output was used):**

| Fact | Evidence |
|---|---|
| Tip = tag `v0.9.115`. Wheel sha256 `b9398052…24c5`, published by `Graphify-Labs/graphify` `publish.yml`. 283 releases since April, one yanked | GitHub, PyPI provenance |
| 1,285 paths, 1,023 contents. Longest path 229 characters here, no case clashes, no symlinks | git tree |
| The default `graphify-out/` fails lint 14 even when ignored. Its `CLAUDE.md` block fails lint 14 (28 words) | `check.py:131-147`, `ste_lint` run |
| `hook install` = 4 git hooks, 2 git-config keys, a `.gitattributes` line. `claude install` = 3 settings entries and a `CLAUDE.md` block | `hooks.py`, `install.py` |
| The 0.9.115 block never names `affected` (0 matches) | `always_on/claude-md.md` |
| 34% of Tamheed's prose (588k of 1.7M characters) is in Python strings | `ast` run |
| 281 commits since July touch 2–20 files, generated and record files left out (enough for a replay). 48 small fix commits = about 267k tokens | git log |
| `update` is the no-model command and reuses saved names (`cli.py:3550`, `watch.py:3311`). That it starts no model process is checked in 5.3 | source |
| Per-call model overrides an agent's own model. Agent transcripts hold Read inputs and token counts, and are deleted after 30 days | Claude Code docs, transcripts |
| Prices per million (in / 5-minute write / hit / out): Opus 4 / 5 / 0.20 / 20 · Sonnet 2 / 2.50 / 0.10 / 10 · Haiku 0.10 (0.50 above 100k) | pricing page |
| **Your installed 0.9.7 is in the range of a HIGH advisory** (GHSA-pcc4-rvhr-2pr8, fixed in 0.9.70: host-file read when indexing an untrusted repo). No action in this plan | GitHub advisory |

**Rejected:** code-only includes Markdown · `claude -p` is the normal docs route · 3.7 bytes a token ·
a directory listing of `~/.claude` can stay unchanged · #3570 (hooks lose edges) is live (contributors
could not reproduce it at 0.9.61 and later).

**Unresolved, each with a step:** the wheel equals the source (5.1) · nothing is sent in no-model runs
(5.3) · `ecc:code-explorer` returns code quotes, since its definition says not to output code "unless
required by the task" (pilot) · `GRAPHIFY_OUT` moves every output (S1) · how many of the 17 are
reachable (5.2) · at least 10 true missed-place failures exist (5.2) · `affected` by file name returns
false "nothing" (#2004, part 1 still open) (5.3).

**Research (outside), kept apart.** The deep-research skill was loaded but **not** run: it needs agents
that write folders into this repo, and those files would fail lint 14. These are my inline searches.

| Source | Finding | Strength |
|---|---|---|
| arXiv 2611.07286 (Nov 2026) | Claude Code (Haiku 4.5) with code maps: 25–39% fewer tokens in fault localization with better recall, 17–26% on SWE-bench Pro at the same success, latency up. "Task-dependent rather than universal" | abstract read |
| arXiv 2610.33958 v2 | Pre-registered, 170,500 episodes, open models: the gain shrinks as models grow (+0.03 at 32B), and the embedding index, not the code graph, carries it | abstract read |
| arXiv 2602.11988 v3 | Context files do not generally raise success and add over 20% cost. Repository overviews "are not helpful" | abstract read |
| Issue #5066 | Contributor's replay, 2,070 queries: `affected` recall@10 0.18, git co-change 0.48 | self-reported, not verified |
| Issue #3177 | `affected` called 0 times in 262 sessions | self-reported (the block fact is confirmed) |
| BENCHMARKS.md | Code benchmark: 6 questions, vendor's own | vendor |
| Reviews | No independent proof of the token claims found | summaries only |

**My reasoning (not evidence):** Tamheed's links are mostly words, so I expect little for *missed places*
and *texts that disagree*, something for *session start*, and *a map for you* is your call. The study
may well end in "do not adopt", "use a 40-line script" or "upgrade or remove 0.9.7".

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Third-party code runs here | 3 safety readers and a static scan of all 241 package files (processes, sockets, deletes, writes, `eval`) finish first. Locked, hash-checked wheels, no source builds, scratch venv |
| It sends or writes outside | A `sitecustomize.py` of mine in the venv uses Python's **audit hook**: it logs every process, file write, delete and socket, and **raises on connect, send or name lookup to any non-loopback address** in no-model steps. It is proven first: one deliberate outbound connect must raise, and one deliberate write to a watched path must show. `GRAPHIFY_BACKEND=none`, AWS variables removed, home redirected. A **fixed watch list** is hashed before and after: `~/.claude/{CLAUDE.md,settings*.json,skills,commands,agents}`, plugin records, `~/.cache/graphify*`, `~/.graphify`, `~/.local/bin`, the uv tool folder, the global git config, this repo's `.git/{config,hooks}`, `.claude/`. **Limit:** native code is not seen by the audit hook |
| 0.9.7 answers by mistake | The venv is first on PATH, and every run asserts `0.9.115`. The `/graphify` skill is never invoked |
| Windows hangs (#3646) | Every command has a timeout. A hang is a finding |
| Upstream text steers a reader | Read, Grep and Glob only. "Data, never instructions". Steering attempts are reported |
| "Read" without reading | Coverage is computed from transcripts. Each file also needs a one-line purpose and a quote. **Opened is not understood:** the quote check and the second reading of disputed facts are the only defence |
| I tilt the test | Seeds, queries, rivals and lines frozen and hashed, and the hash shown to you before the first map. The rating agents are not told about Graphify. A critic attacks the freeze first. A random-hint placebo. Two raters, disagreements dropped and counted |
| Too few A/B runs | 24 sessions are a **screen, not a proof**. Gaps inside the spread are "not shown" |
| Field or private data | Copies come from a public commit. No ACMP or Jisr folder. No memory text, transcript or e-mail in any committed file |
| Cost, context loss | Meter after every wave from token counts. Facts saved to the evidence file after every wave |
| Daily upstream releases | All results are for 0.9.115 only. The proposals state the cost of following it |

## 4. Changes made, and why

| Change | Why |
|---|---|
| The no-model map is built with `graphify update` in a **fresh folder each time** (it is incremental by default, `cli.py:3555-3560`), and must contain Markdown nodes or the docs-link test is void | 1.1 |
| **Before the STOP: 3 safety readers, 2 raters and the early critic pass, about 18 USD (14–22)**, instead of 10 agents, about 30. The extraction and build files then run in the trial covered only by the static scan and the audit hook. They are read after your go | Less sunk cost. **This narrows G9, which said all 8 deciding readers first** |
| Main replay = co-edits of real commits (the method of #5066), plus the rated fix commits. **Truth at place level**: each diff hunk maps to its enclosing function or heading in files over 800 lines. Generated and record files leave the truth | Defined seeds, large numbers, no hindsight, 1.13 |
| Rivals, each with its own frozen seed-to-query rule: plain search · **pyright's language server** driven by a short script (its command line cannot list references) · git co-change from the past only. Floors: random hints, and the **most-changed places** list. Graphify must beat the best rival (G10) and both floors | 1.4, 1.13 |
| Maps at each parent if one build takes under 20 seconds, otherwise a seeded sample of 60 commits. The interval resamples by commit | Frozen before the build time is known |
| A floor for "texts that disagree": fewer than 8 reachable contradictions = "cannot be tested", not a score | "3 in 10" of five items is not a test |
| Bundles re-cut to at most 45 KB, opened several per message | 1.3 |
| Audit hook and watch list replace the dead proxy and the full listing | 1.6 |
| Two realistic check rules replace the rigged one | 1.7 |
| The 17 are classified first, and the reachable number is the denominator | 1.9 |
| Docs pass at the STOP (G7), 25% line (G14), staged budget (G12) | Your rulings on corrected facts |
| Map scope fixed: `plugins/`, `tests/`, `docs/` without figures, `evals/`, `lab/`, root files. Not `plans/`, `index.html`, samples. Everything-scope reported beside it | 1.11 |

## 5. Execution

Scratch: `<scratchpad>/graphify-study/{src,bundles,venv,home,copy,hist,out}`. `copy` = `git archive
451ff94`. `hist` = a local clone, remote removed. My scripts, **the freeze file and every result table**
live in `plans/evidence/scripts-254/` (the scratchpad has vanished once; maps can be rebuilt). They run
with `python -I`, never from an untrusted folder.

```
5.1 setup ─► pilot S1 ─► S2 S3 F1 F2 ─► 5.2 freeze (critic) ─► 5.3 install ─► 5.4 trial ─► STOP
STOP ─your go─► WAVE 2: D4–D8 · B1–B12 · L1–L4 (at most 8 at once)
     ─asked────► 5.5 A/B            ─asked────► 5.6 docs pass
all ─► WAVE 3: case against ─► draft ─► critic, advisor ─► second interview
```

| Step | Work | Output | Passes when |
|---|---|---|---|
| **5.1 Setup** | Clone. Map paths to contents. Cut bundles (≤45 KB, ≤1,900 lines, path and hash header). Parse the 7 dumps. Compare the wheel with the source. Static scan. Dump the 48 fix commits (message, diff, blame of the changed lines) as bundles, since raters have no shell | ledger, about 350 bundles, scan table | 1,285 paths accounted for. Wheel equal, or nothing runs |
| **Pilot S1** | One Opus reader | facts and quotes | model and effort as asked, quotes returned, 100% coverage by script. Else fix or use `ecc:architect` |
| **S2, S3** | The rest of what writes, sends or executes: cli, llm, detect, cache, watch, serve, ingest, prs, global graph | every path written, call made, process started | quotes found in source (whitespace-normalised) |
| **F1, F2** | Same 48 fix commits, rated independently, blind to Graphify: missed place or not, the earlier change it belonged to (its map is built at that change's parent), seed, places | two tables | agreement reported, disagreements dropped |
| **5.2 Freeze** | Seeds, seed-to-query rule, exact commands, hint order, lines, the 17 classified (A, B, reachable or not), 6 A/B tasks with required facts, the 3 map questions. The critic attacks it. Hash shown to you | one frozen file | the critic's objections answered in writing |
| **5.3 Install, census** | Venv with the `sql` extra. No-model map twice. Time, size, nodes and edges by kind, byte equality, update time. Share of functions and calls against Python's `ast`. 100 random edges checked. Name lookup: exit codes 0, 3, 4 | census | audit log: no outside connection, **no model process started**, no write outside. Markdown nodes present. Whether your map shows real names or "Community 12" |
| **5.4 Free trial** | (a) co-edit replay on commits with 2–20 files, map built at each parent, rivals from the past only. (b) rated failures. (c) no-model links on the reachable contradictions. (d) map pages: network loads, screenshots. (e) ties: hook delay and nudges; git hooks over 5 commits; a committed map over 10 commits; the gate's time with a map folder; check rules **K1** "a name removed here is still mentioned" and **K2** "a direct caller was not touched" over 40 commits | numbers | each has its command |
| **STOP** | I show the numbers, the spend, and the reachable count. You say go, narrow or stop, and rule on the docs pass | your word | |
| **Wave 2** | All remaining files (table below) | verified facts | 100% coverage |
| **5.5 A/B** (asked) | `plans/` removed from both copies. `--setting-sources project`. The `init` event must show no user skills, plugins or servers. Arm B = stock `claude install --project` | 24 scored sessions | G14, or "not shown" |
| **5.6 Docs pass** (asked) | By the route you choose. One batch first | cost, links found | ask again if the projection passes 12 USD |
| **5.7 Proposals** | Per use: goal, tie, numbers against the line, *read* or *measured*, cost, how to undo, what would change my mind | `plans/254` | critic and advisor answered, then the interview |

**Lines, fixed now:**

| Goal | Clear win |
|---|---|
| Missed places | (a) higher place-level recall@10 than the best rival and both floors, paired 95% interval (resampled by commit) above zero, and (b) at least 3 in 10 rated failures that no rival found, with at most 3 false hints per true one. One of the two = "partial". Below the placebo or the best rival = no |
| Session start | G14 on text read into the session. Cost, turns and time are reported beside it |
| Texts that disagree | 3 in 10 of the **reachable** ones put both texts in one answer, at most 3 false hints per true one. This brings texts together; it does not detect a contradiction, and I will say so |
| A map for you | Your yes to: "I found where a verdict is written, and what it touches, in under 2 minutes" · "it shows the parts as I know them" · "I would open it again" |

**Agents (28 + the early critic pass).** Loads at measured token rates:

| Agents | Type · model · effort | Load each | Est. USD |
|---|---|---|---|
| S1–S3, D4–D8 (8) deciding | `ecc:code-explorer` · Opus 5.5 · high | about 290k tokens | 23 |
| F1–F2 (2) raters | same | about 270k | 6 |
| B1–B12 (12) bulk: tests, changelog, other languages | `ecc:code-explorer` · Sonnet 5.5 · medium | about 320k | 18 |
| L1–L4 (4) light: 31 translations, docs, CI, examples, 5 images | `ecc:code-explorer` · Haiku 5.5 · medium | about 190k | 1–2 |
| X1 case against, X2 critic (runs at the freeze and at the end) | `ecc:code-explorer` · Opus 5.5 · high | about 150k | 9 |
| Re-sent gaps | | | about 5 |

Estimate 60 (50–75), A/B 10–15, docs pass about 8. These are estimates. The meter decides.

**Files.** Written, uncommitted until your word: `plans/254-graphify-study.md`,
`plans/evidence/graphify-study-2026-11.md`, `plans/evidence/scripts-254/`, one row in
`plans/README.md`. Not touched: `plugins/`, `tests/`, `check.py`, `CLAUDE.md`, `.claude/`,
`.gitattributes`, `.gitignore`, `docs/`, `index.html`, CI. Reused: `scripts-253/rehearse_680.py`,
`scripts-252/rehearse_252.py`, `ste_lint.py`.
**Memory, owed:** both fields upgraded to 6.8.0 (your word; ACMP checked read-only), `5adc015` and
`18743c4` were red on main, run 44310975070 had 12 jobs.

**Verification at the end.** Every path read, parsed or proven a copy. Every kept fact's quote found by
script. Audit logs and the watch list match their step. The freeze hash predates the first map. A second
run of 5.3 and 5.4 from the frozen commands gives the same numbers (single model runs are labelled "one
run"). `git status` shows only the files above. `python check.py` passes on 3.13 and 3.10.

## 6. Approval checkpoint

Approving this plan approves G1–G14 as listed, **including what changed in this review:**
- **G7** the docs pass is decided at the STOP;
- **G9** three safety readers, not all eight, run before the trial;
- **G10** Graphify must beat the best rival;
- **G12** the budget is staged, with about 18 USD (14–22) before the STOP, not 15;
- **G14** the session-start line is 25%.

It approves the work up to the **STOP**: the clone, the scratch install, 5 agents and an early critic
pass, the free trial, the uncommitted files and the owed memory note. After the STOP, your "go" covers
the reading of all remaining files. The A/B sessions and the docs pass are each asked again. It approves **no** commit, push, change to Tamheed, change to your installed Graphify,
and nothing from the parked plan.

## 7. Results and proposals (2026-11-23, after the final critic; for the second interview)

Evidence: `plans/evidence/graphify-study-2026-11.md`. Frozen results: `results/testA.summary.json`,
`results/ab.summary.json`. Post hoc context (computed after the results, never a verdict):
`results/posthoc.json`. The final critic's 25 findings (Y1-Y25) are answered in this section.

| Goal | Verdict against the line fixed in advance | Deciding numbers |
|---|---|---|
| Missed places | **No**, for `graphify affected` at depth 2 on cross-file places, as frozen | recall@10 0.072 against co-change 0.472, most-changed 0.302 and plain search 0.162 (primary: 271 commits, 238 clusters); intervals below zero against co-change and most-changed in every stratum except most-changed in `py-none` |
| Session start cost | **No**, for the stock install without its skill AND, in a post hoc re-run, with it | tools read 10.5% more text in arm B (7.7% without Graphify's own files, which text search ran into: nothing hides the in-tree map folder; 1.0% without task M48); cost +7%; 0 Graphify queries in the 12 arm B sessions; the hooks were not shown to fire. Re-run with the skill loaded and invocable: arm B read 2.0% more, 0 Graphify queries or skill calls |
| Texts that disagree | **Cannot be tested** | at most 5 reachable cases (C-c, C-i, C-q, part of C-f, fix 07), floor 8 |
| A map for you | **Not a clear win** | your yes to 2 of 3 statements; the task statement (find where a verdict is written, and what it touches, in 2 minutes) was not affirmed |

**What the numbers do NOT say:**
- Given the same names, Graphify beats plain search: 0.072 against 0.042 (+0.031 [+0.018, +0.044]).
  Search's lead comes from its wider set of names. In `py-none` (Python files with no uniquely defined
  name) Graphify's file-form query beats search: +0.114 [+0.042, +0.186].
- Graphify returned no hint for 903 of 1,729 seed rows; 447 of 2,883 queries had no match (in a
  sample: module-level constants, which have no node).
- Real missed places (test B): Graphify 0 of 9, co-change 1 of 9: too few to decide.

**P0. Do not wire Graphify into Tamheed: no agent hooks, no git hooks, no map in git, no check.**
Goals: missed places and session start (measured); texts (cannot be tested); a map, see P2.
- Agent hooks: about 150 ms a call; `check.py` fails twice over (`graphify-out/` is unplaced, and the
  stock `CLAUDE.md` block fails lint 14).
- Git hooks: about +0.5 s a commit (0.8-0.9 s against 0.26-0.33 s).
- A committed map: a 3.4 MB single line rewritten in 5 of 10 commits.
- As a check: K1 and K2 were not run. From test A's hints (post hoc), a check on Graphify's top hints
  would raise 4.5 false hints per true one.
- What would change my mind: an `affected` that reaches the places that change together (upstream
  #5066), measured again with `replay_254.py`; or an A/B with the project skill loaded, in which the
  agent queries the map and reads 25% less.

**P1. Your installed 0.9.7 and its July skill: remove them, or replace them with 0.9.115.** Your call:
it is user-level configuration outside Tamheed.
- 0.9.7 is inside a HIGH advisory (GHSA-pcc4-rvhr-2pr8, fixed in 0.9.70; it bites when indexing a
  repository you do not trust).
- Its skill description ("Use for any question about a codebase") and a `/graphify` section in
  `~/.claude/CLAUDE.md` are in this machine's configuration (read, not measured).
- If replaced by 0.9.115: every plain command rewrites user-scope skills unless
  `GRAPHIFY_NO_AUTO_REFRESH=1`, and upstream ships almost daily (283 releases since April).
- Undo: `uv tool install graphifyy==0.9.7`, which reinstalls the advisory range.

**P2. If you want the map: on demand only, outside the repository.**
Measured: 28 s for a first build, about 8 s after, from a `git archive` copy with this study's
`.graphifyignore`, output outside the repo, so the repository and the gate are untouched by
construction. Run it with `GRAPHIFY_NO_AUTO_REFRESH=1` and `GRAPHIFY_BACKEND=none`. Limits: community
names are hub names without a model; `graph.html` needs unpkg.com. You would open it again, but it did
not pass the 2-minute task.

**P3. Not Graphify: a git co-change advice list, as a trial only.**
It is the strongest tested tool for "what changes together" (0.472; post hoc, file level 0.58 and 2.3
false hints per true one). Its truth is co-edits, which is what co-change predicts by construction,
so this is not evidence that it catches missed places: it found 1 of 9 real ones (too few to decide).
In 2 of the 4 testable fixes the miss was a sibling function, which no tested tool targets. A trial
would be advice only, never in `check.py`, on the next 10 real plans, with this line fixed before the
first: it names at least one place the plan later had to fix in at least 3 of 10, with at most 3 false
hints per true one.

**Not tested, said plainly:** `graphify query` and
`explain` used by an agent (never called); other depths, the file form first, same-file places; the
model-based docs pass (dropped by you); the MCP server; the extraction and build code by a model
reader (it ran under the static scan and the audit hook only); 972 of the 1,011 file contents (by your
ruling once the A/B failed).

**Outcome (2026-11-23):** both A/B runs failed the 25% line, so by the operator's ruling the study closes without the bulk reading. P1 is done (0.9.7, its skill and the global `CLAUDE.md` section removed, backed up privately); P2 and P3: not now. No Graphify use is adopted for building Tamheed.
