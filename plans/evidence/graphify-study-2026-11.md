# Plan 254: the Graphify study, evidence (2026-11-23, final)

Counts, commands and facts only. Every quote of Graphify's source was checked by script against the
clone at `3671f31` (tag `v0.9.115`). Scripts, the freeze file and every table are in
`plans/evidence/scripts-254/`.

## 5.1 Setup

| Check | Result | Command |
|---|---|---|
| Clone | `3671f31`, 1,285 paths, sizes on disk equal the blobs | `git clone --depth 1 --branch v0.9.115` |
| Contents | 1,023 distinct: 1,011 assigned to model readers (39 read; the rest not read, by the operator's ruling), 5 images, 7 dumps by script; 262 proven copies. The extraction and build code ran under the static scan and the audit hook only | `setup_254.py` → `ledger.csv` |
| Bundles | 399 reading bundles for 23 readers (plus 17 for the two raters), largest 45,375 bytes; every file rebuilt from them byte for byte | `verify_bundles_254.py` |
| Wheel | sha256 matches PyPI; all 240 package files equal the source; publisher `Graphify-Labs/graphify` `publish.yml` | inline, recorded in this file |
| Static scan | 103 Python files: 28 process starts, 25 network entry points, 5 dynamic imports, 88 deletes, 122 writes | `scan_254.py` → `scan.csv` |
| Dumps | `uv.lock`: 202 packages, one registry (pypi.org), no package without a hash, 2 source-only (jieba, nuitka). The 4 `graph.json` and `manifest.json` parsed whole | `dumps.json` |
| Venv | 33 locked packages (`uv export --frozen --no-dev --extra sql`), `--require-hashes --only-binary :all:`, plus the checked wheel `--no-deps`. Python 3.13 | inline |
| Audit hook proof | a deliberate lookup of `example.com` was blocked; a loopback bind passed; a write, a delete and a `git` start were logged; the write landed in the redirected home | `run_254.py … probe` |
| Watch list | 46,981 entries; a control run with nothing running changed 0 (after `~/.codex` was narrowed: a running Codex app changes its own databases) | `watch_254.py` |

## Readers

| Reader | Model, effort (from its transcript) | Bundles whole | Facts kept / rejected | USD |
|---|---|---|---|---|
| S1 (pilot) | `claude-opus-5-5`, high | 12 / 12 | 263 / 0 | 2.82 |
| S2 | `claude-opus-5-5`, high | 14 / 14 | 261 / 0 | 2.68 |
| S3 | `claude-opus-5-5`, high | 18 / 18 | 207 / 0 | 3.06 |
| F1, F2 | `claude-opus-5-5`, high | 17 / 17 each | (tables) | 3.43 + 3.45 |
| X2 (critic) | `claude-opus-5-5`, high | (design files) | 30 findings | see meter |

**From S1, changing the trial set-up:** any ordinary command re-copies user-scope skills whose version
stamp is older (`graphify/__main__.py`, `_refresh_stale_skills`; off with `GRAPHIFY_NO_AUTO_REFRESH=1`).
Run plainly, 0.9.115 would overwrite the operator's 0.9.7 skill. Every run therefore gets a redirected
home and that variable.

**From S2 and S3, fixing the freeze:**
- `update`, `watch` and hook rebuilds are AST-only; no step starts a model, not even community naming (hub-name fallback). `GRAPHIFY_BACKEND=none` also turns off the `claude -p` labelling fallback of `cluster-only` and `label`.
- `affected`: depth 2 by default; exit 3 on an ambiguous name, 4 on no match. It accepts `path::Symbol`, which resolves only to a unique node (`affected.py`, `resolve_reference_forms`). Frozen seed rule: `<file>::<name>`, plus the file itself.
- Dot-folders are scanned by default and nothing skips `plans/` or `tests/`: a `.graphifyignore` is needed, and the output folder must sit outside the tree.
- Two reports came back through a hand-back channel, not the transcript; `meter_254.py --report` scores those.

## Raters and the freeze

- F1 and F2 (Opus 5.5 high, blind to Graphify): 17 of 17 bundles each; agree on 47 of 48 fixes, Cohen's
  kappa 0.956; 16 both "yes". 3.43 and 3.45 USD.
- Of the 16: 4 can be posed to an impact tool; 5 sit inside the same function as the origin; 7 have an
  origin described only in words. Below the floor of 10: "too few to decide".
- Critic X2 (Opus 5.5 high): 30 findings, 4 blockers, all but one (stale) accepted. Checked by running:
  15 merges since July (ancestry order needed), 21 commits that the first diff parser misread, `` in
  `git grep` harmless. My own fixes then broke pyright twice in silence (no warm-up: 1 reference where 71
  exist; `file:///c%3A/` URIs read as outside the tree); both caught by self-checks before any result.
- Freeze v2 `e40fe910` (04:03:30Z), v2.1 `259fe6d6` (04:09:44Z, per-process audit logs), v2.2 `cd014dc1`
  (04:27:43Z, label brackets in the `affected` parser; 133 v2.1 rows set aside). Analysis script hashed
  04:28:30Z, before any v2.2 row existed (`analyze_254.sha256`).

## 5.3 Census of `451ff94` (no model, network blocked)

| Measure | Result |
|---|---|
| Build | 7.8 s twice, byte-equal `graph.json`; first cold build 28 s; update after a one-line edit 8.4 s, unchanged 0.9 s |
| Map | 3,701 nodes, 7,144 edges (6,237 EXTRACTED, 907 INFERRED); `graph.json` 3.4 MB, `graph.html` 3.6 MB, report 38 KB |
| Python definitions | 1,578 of 1,584 found as nodes (99.6%) |
| 100 random call edges | 100 have the callee's name on the cited line |
| Markdown | 89 files with nodes; 902 `references` edges |
| Gate of 20 queries | 20 of 20 exit 0 |
| Module-level constants | no node (`RELATION_RULES`, `TOOLS`): exit 4 |
| Safety | 0 blocked connections, no model process, 3 process starts (its own re-exec, `git rev-parse` twice), watch list unchanged |
| Map page | loads `vis-network@9.1.6` from unpkg.com (with an integrity hash): it needs the network to draw |

## 5.4 The free trial (so far)

**Ties, each on a throwaway git copy:**

| Tie | Measured |
|---|---|
| Agent hooks (`claude install --project`) | 5 repo paths changed: `.claude/settings.json` (+38, three hooks), `CLAUDE.md` (+11), new `.claude/CLAUDE.md`, `settings.json.graphify-bak`, a skill copy under `.claude/skills/`; a lock file in the home. Delay per Read/Grep/Glob/Bash call: median 145-154 ms over 20 calls. `check.py` on that copy: FAILS in 133 s (`graphify-out/GRAPH_REPORT.md` unplaced), and the lint tests fail with it |
| Git hooks (`hook install`) | 4 hooks, 2 `merge.graphify.*` keys with an absolute interpreter path, `.gitattributes` modified, `graphify-out/` untracked, a log in the home. A commit returns in 0.8-0.9 s against 0.26-0.33 s with the hooks skipped; rebuilds run detached. Without a `.graphifyignore` the map takes in `plans/` (8,154 nodes) |
| A committed map | over the last 10 commits the map files changed in 6; `graph.json` (one line of 3.2-3.4 MB) was rewritten whole in 5; `GRAPH_REPORT.md` up to 294 lines; 7 versions pack to 402 KiB |
| A check in the gate | judged from test A's false hints (a check flags every top hint the commit did not touch); a "removed name still mentioned" rule needs no map |

**Test B (4 testable rated missed places):** true places found, of 9: Graphify 0, plain search 0,
pyright 0, co-change 1 (fix 03, `SECURITY.md`), random 0, most-changed 0. Fixes 29 and 48 needed the
same guard in SIBLING functions, which are not callers; `affected` lists dependents. "Too few to decide".

**Documents (no model):** both sides in one `graphify query` answer for 1 of 4 reachable cases (C-c).
Some second sides are my reading of the parked plan's short text, not recorded locations. "Too few to
decide".

## Test A, the co-edit replay (freeze v2.2; analysis hashed before any row)

273 commits (one run; the analysis is deterministic given the rows), 1729 seeds; every map built; pyright 0 timeouts; Graphify queries: 2436 answered, 447 with no node (module-level names). Primary: 271 commits in 238 clusters.

Mean recall@10 (true places among 10 hints, divided by min(10, truth)), by commit:

| Analysis | Commits | Graphify | Search | Pyright | Co-change | Most changed | Random | Frozen verdict |
|---|---|---|---|---|---|---|---|---|
| **primary** | 271 | 0.072 | 0.162 | 0.032 | 0.472 | 0.302 | 0.029 | no: below search, cochange, most_changed |
| stratum md | 191 | 0.044 | 0.201 | 0.000 | 0.457 | 0.308 | 0.027 | no: below search, cochange, most_changed |
| stratum other | 111 | 0.000 | 0.028 | 0.000 | 0.505 | 0.365 | 0.040 | no: below search, pyright, cochange, random, most_changed |
| stratum py-defined | 166 | 0.167 | 0.216 | 0.133 | 0.422 | 0.362 | 0.030 | no: below search, cochange, most_changed |
| stratum py-none | 64 | 0.149 | 0.035 | 0.000 | 0.331 | 0.218 | 0.025 | no: below cochange, most_changed |
| stratum tests | 181 | 0.001 | 0.167 | 0.000 | 0.396 | 0.224 | 0.031 | no: below search, cochange, random, most_changed |
| truth 1-3 | 130 | 0.119 | 0.206 | 0.084 | 0.549 | 0.290 | 0.037 | no: below search, cochange, most_changed |
| truth 4-10 | 135 | 0.054 | 0.135 | 0.018 | 0.454 | 0.331 | 0.019 | no: below search, cochange, most_changed |
| truth 11-1000000 | 52 | 0.041 | 0.139 | 0.009 | 0.279 | 0.249 | 0.032 | no: below search, cochange, most_changed |
| S1 commits with 2-4 files | 123 | 0.091 | 0.186 | 0.058 | 0.538 | 0.269 | 0.028 | no: below search, cochange, most_changed |
| S2 without gate-enforced files | 270 | 0.060 | 0.154 | 0.033 | 0.449 | 0.237 | 0.030 | no: below search, cochange, most_changed |
| full truth | 273 | 0.066 | 0.147 | 0.028 | 0.416 | 0.259 | 0.023 | no: below search, cochange, most_changed |

Graphify minus each other tool, primary, with the 95% cluster-bootstrap interval:

- search: -0.090 [-0.110, -0.069]
- pyright: +0.041 [+0.028, +0.053]
- cochange: -0.400 [-0.439, -0.362]
- random: +0.043 [+0.024, +0.062]
- most_changed: -0.229 [-0.266, -0.195]

**Verdict (frozen rule): no**, for `graphify affected` at depth 2 on cross-file places. Graphify is below git co-change
in the primary analysis, in every stratum and every truth-size band (intervals below zero), and below most-changed
everywhere except `py-none` (interval reaches zero). It is below plain search everywhere except `py-none`, where its
file-form query beats search (+0.114 [+0.042, +0.186], post hoc). Given the same names, it beats search: 0.072
against `search_defined` 0.042 (+0.031 [+0.018, +0.044], post hoc). In stratum `other`, Graphify and pyright tie at 0
(the script's word 'below' there is a tie). Graphify returned no hint for 903 of 1,729 seed rows.

## After the STOP (operator, 2026-11-23): A/B first, docs pass dropped, map 2 of 3

- **Operator's rulings:** A/B first, and read the remaining files only if it passes; drop the docs pass
  (not scorable); on the map, "it shows the parts as I know them" and "I would open it again" are true,
  "found where a verdict is written in 2 minutes" was not affirmed: **partial**.
- **Snapshots moved out of the repository** (they list file names from the operator's home); the watch
  script writes to a private scratch folder. Only the results stay here.

## 5.5 A/B sessions (freeze v3, `ab_freeze_v3.sha256`, 17:48:46Z, before any scored session)

24 headless Opus 5.5 sessions, 6 tasks x 2 arms x 2 repeats, `--setting-sources project
--strict-mcp-config --disable-slash-commands`; the `init` event showed only Claude Code's built-in plugins,
no MCP server, no skill. Arm B: Graphify's stock `claude install --project` plus a no-model map.

| Arm | Right | False | Text read (characters) | USD | Turns |
|---|---|---|---|---|---|
| A, no Graphify | 23 of 28 | 26 | 220,207 | 2.99 | 77 |
| B, Graphify installed and mapped | 24 of 28 | 17 | 243,374 | 3.21 | 79 |

- **G14 verdict: fail**, for the stock install WITHOUT its project skill: `--disable-slash-commands` turned off the
  skill that `claude install` adds (init `skills: []`). Arm B's tools read 10.5% more text; 7.7% more without lines
  from Graphify's own files, which text search ran into (nothing hides `graphify-out/`: Tamheed's `.gitignore` does
  not list it and the installer adds no ignore line, so this is a cost of the stock in-tree map); 1.0% more
  without task M48. The two repeats' ranges overlap in 4 of 6 tasks; in M48 arm B read more both times, in O2 less both times.
- **0 Graphify queries in the 12 arm B sessions** (counted by command name, `posthoc.json`). The scorer's
  substring rule had labelled 5 shell calls as Graphify calls (2 in arm A from the path `graphify-study`, 3 in arm B
  from `grep -v graphify-out`); all 5 were `awk` commands denied by the permission mode. The operator's 0.9.7 stayed
  on arm A's PATH and was not called. Whether arm B's hooks fired is not visible in the session stream, and the
  query log that could have shown it was off.
- Freeze v3 (before any scored session) changed the A/B tasks from F6: O1's keys and truth (`package_open` neutral),
  a new O2 (`_scan_markers`), `gate_run` neutral in O2 and O3; one pilot session (O2, arm B) ran at 17:47Z, before
  the scorer's bug fix and the final hash at 17:48:46Z, and is one of the 24 scored. The session transcripts hold
  home-folder paths and are kept privately, outside the repository; only the scores are here.
- The watch list was unchanged after the sessions (`s9-final` to `s10-after-ab`).
- By the operator's ruling, the bulk reading (972 more file contents) does not run. Models read 39 of 1,011 contents.

## The 17 recorded contradictions (parked plan, section C), by where their two sides live

| Two sides | Items | Reachable by a document map |
|---|---|---|
| Markdown and Markdown | C-c, C-i, C-q (C-f in part); plus the raters' fix 07 | yes (at most 5 in all) |
| Text and engine behaviour | C-b, C-d, C-e, C-f, C-j, C-k, C-l, C-m, C-n, C-o, C-p | no |
| Markdown and a Python string | C-a, C-g | no (`.py` is never sent to the docs pass) |
| Location not recorded | C-h | cannot be scored |

At most 5 are reachable counting the raters' fix 07 (C-c, C-i, C-q, part of C-f, fix 07; 4 of them were posed as queries), below the frozen floor of 8.

## The A/B re-run with skills on (post hoc, freeze v4 `ab_freeze_v4.sha256`, 18:25:04Z, before the pilot)

The operator chose a re-run after critic Y1. Same tasks, same 25% line. Skills on in both arms, `Skill` allowed:
arm B loaded 20 skills including Graphify's project skill (all 12 sessions), arm A 19 and no Graphify skill.

| Arm | Right | False | Text read (characters) | USD | Turns |
|---|---|---|---|---|---|
| A, no Graphify | 23 of 28 | 20 | 241,337 | 3.15 | 79 |
| B, stock install WITH its skill, mapped | 24 of 28 | 17 | 246,234 | 3.45 | 88 |

- **G14 verdict: fail.** Arm B read 2.0% more, not 25% less; spreads overlap in 5 of 6 tasks.
- **0 Graphify queries and 0 Graphify skill calls in the 12 arm B sessions**, counted by command and tool name.
  Offered the stock install in full, Opus 5.5 did not choose the map for these tasks.
- By the operator's ruling the bulk reading does not run: the study closes. Probes and re-run: 7.00 USD.

## After the study (operator's rulings, 2026-11-23)

- P1 done: Graphify 0.9.7 uninstalled (`uv tool uninstall graphifyy`), `~/.claude/skills/graphify` deleted, the
  3-line `~/.claude/CLAUDE.md` (only the `/graphify` section) deleted; 13 files backed up privately. The
  `skillUsage/graphify` counter in `~/.claude.json` is Claude Code's own usage count; no MCP server was registered.
- P2 (map recipe) and P3 (co-change trial): not now.
- `check.py` with every study file present: ALL CHECKS PASSED on Python 3.13 and 3.10.
- Spend: agents 19.25 USD (two critic passes included), A/B 6.20, probes and re-run 7.00: **32.45 USD** of 80.
