# Plan 254, the freeze (version 2, after the early critic; hashed before the first map of Tamheed)

Everything below is fixed before any Graphify map of Tamheed exists. The scripts are frozen by the
sha256 table in `freeze_254.sha256` (written beside this file). A change after the hash is shown to
the operator is a new freeze, reported as such.

## F0. What changed from version 1, and why (critic X1-X30, `readers/X2.report.txt`)

Accepted: X2-X30. X1 was stale (the driver existed when the critic finished). Measured before the
hash: 15 merges since July and date order differs from ancestry order (X6 real); 21 commits have
diff lines that the first parser misread as headers (X7 real); `git grep -w` gives 1,063 matches with
or without a word boundary (X8's boundary worry not real; the commit id is escaped anyway).
Found by my own self-checks while fixing: pyright answered from the open file only until it had
indexed the workspace (1 reference where 71 exist) and URIs came back as `file:///c%3A/...`, which a
standard decoder turns into a path outside the tree. Both would have scored the pyright rival 0
without an error. Both are fixed and self-checked (`lsp_254.py --check`).

**Version 2.1 (2026-11-23, after the first census build; no rule changed):** Graphify extracts in
worker processes, and their audit lines interleaved in one shared log, which crashed the runner on the
second build. The audit hook now writes one file per process and `run_254.py` merges them and counts
any unreadable line. Version 2's hash table (`e40fe910…af0a`, 04:03:30Z) is kept in this file's
history; v2.1's table replaces it.

**Version 2.2 (2026-11-23, after 20 replayed commits; no rule changed):** a harness-health check showed
a Graphify hint `'[references] AUDIT.md'`: a node label may hold `[...]`, and the parser took the label's
bracket for the relation. It now reads the last bracket group (fixture added to `dryrun_254.py`). The
133 rows written under v2.1 are kept as `results/testA.v21-discarded.jsonl` and not scored; test A
restarts from the first commit. The same check showed 66 of 183 queries exiting 4: names of module-level
constants (`RELATION_RULES`, `TOOLS`), for which Graphify has no node. By F1 they score as empty and
are counted apart.

## F1. Commands (Graphify 0.9.115, through `run_254.py`, network blocked)

- **Build:** a fresh folder holds `git archive <parent>`, a fresh home and a fresh output folder outside
  the tree; `graphify update <tree>` with `GRAPHIFY_OUT=<out>`; `.graphifyignore` = `plans/`,
  `index.html`, `CHANGELOG.md`, `docs/guide/figures/`, `generated-samples/`, `evals/sample-results/`,
  `tests/standup_golden/`, `pyrightconfig.json`. After each build: `<out>/graph.json` exists,
  `<tree>/graphify-out` does not, and at least 95% of node `source_file`s are files at the parent, or
  the run stops. All three folders are deleted after the queries.
- **Impact query:** `graphify affected "<seed file>::<name>"` for each name defined exactly once in the
  seed file at the parent, then `graphify affected "<seed file>"`. Depth 2, the default relations.
  Exit 3 or 4 = an empty answer, counted apart, never "nothing depends on it". The whole stdout is read
  from file. `affected` prints breadth-first, so its order is depth order.

## F2. Places and truth

- A place is a file, or in a file over 800 lines at that commit, the innermost function, class,
  multi-line module-level assignment, key of a module-level dict literal (`TOOLS[package_open]`,
  `TEXT[section.tools.upsert.2]`), or Markdown heading (levels 1-3) (`places_254.py`).
- Never a place: `plans/`, `CHANGELOG.md`, `index.html`, `docs/guide/figures/`, `generated-samples/`,
  `evals/sample-results/`, `tests/standup_golden/`.

## F3. Test A, the co-edit replay (goal: missed places)

- **Commits:** non-merge commits from 2026-07-01 to `451ff94`, in ancestry order, touching 2 to 20 kept
  files (273). If one whole commit (build, pyright warm-up, every query) takes under 60 s on the first
  3, every commit; otherwise `random.Random(254).sample(eligible, 60)`.
- **Query:** each kept file the commit touched is a seed. Primary truth = places of the OTHER kept
  files of the commit that exist at the parent; full truth (new places included) is secondary.
- **Seed names:** `places_254.seed_names` (span names by changed lines, then Python names from the
  syntax tree, Markdown code spans by stem, `.js`/`.sql` identifiers; a wide stop list; at most 12).
  Pyright and Graphify get only names defined exactly once in the seed file at the parent, filtered
  BEFORE the cap.
- **One pipeline for every tool:** relative posix path; place at the parent; non-kept dropped; every
  place in the seed's own file dropped; first occurrence kept; cut to 10. Multi-answer tools are
  merged round-robin in seed-name order, the file form last. Pyright lists by reference count.
- **Tools:** (1) search, (1b) search over the defined names only (a symmetric control), (2) pyright,
  (3) git co-change over ancestors of the parent only, (4) Graphify, floors (5) random from the parent's
  places, seed 254 plus the commit's index, (6) most-changed over ancestors.
- **Score:** recall = true hints / min(10, |truth|); hit = at least one. Per commit the mean over its
  seeds; the statistic is the mean over commits. 2,000 bootstrap draws with `random.Random(254)`,
  resampling CLUSTERS (the plan number in the subject, else the commit), the same draws for every tool,
  percentiles 2.5 and 97.5.
- **Strata, all reported:** `py-defined` (non-test Python with at least one defined name), `py-none`,
  `tests`, `md`, `other`; and by truth size 1-3, 4-10, over 10.
- **Secondary analyses:** S1 = commits with 2-4 kept files; S2 = truth and hints without the
  gate-enforced set (`content.py`, the three READMEs, the two plugin manifests); full truth.
- **Verdict (primary only):** Graphify's mean minus each of the 5 others (3 rivals, 2 floors); the
  interval must be above 0 against EACH. Above on the point estimate with an interval reaching 0 =
  "not shown". The conclusion is about `graphify affected` depth 2, not Graphify as a whole.

## F4. Test B, the rated missed places

- Raters F1 and F2 (blind to Graphify) agree on 47 of 48, Cohen's kappa 0.956; 16 both "yes"
  (`rated_missed_places.json`). Mapping rule: `testB_cases.json` (saved with the freeze).
- 4 testable (03, 25, 29, 48); 5 inside the same place as A; 7 with an origin in words only.
- Rules: map at the fix's parent; seed names = place A's name plus names defined inside A (nothing
  from the fix); only place A dropped; a bare-file truth in a file over 800 lines counts as hit by any
  hint in that file.
- **Below the floor of 10: "too few to decide". The highest reachable missed-places verdict is
  "partial" (test A only).**

## F5. The documents goal

- At most 5 reachable cases (C-c, C-i, C-q, part of C-f, fix 07), below the floor of 8:
  **"cannot be tested" on recorded cases.** The no-model Markdown links are counted on them, labelled
  "too few to decide".

## F6. A/B tasks (asked separately after the STOP; rules fixed now)

- Every required fact must match 0 times in the copy's `CLAUDE.md` and in Graphify's stock block
  (checked before any A/B run). O2 (new entity family) fails this rule and is dropped; O3 keeps
  `gate_run`, `_edge_rule_violations`, `RELATION_RULES`.
- Answers end with a fixed JSON block, scored by exact identifiers, recall and false names.
  O1: `{"writer", "callers", "guard", "guard_set_in"}` = `_wire_project`, {`package_create`,
  `package_open`, `package_adopt`}, `_WIRE_ROOT`, `main`.
- M tasks are written from the ORIGIN change only, never the fix: 03 from `88cb788`, 25 from `23f315b`,
  48 from `e9b5bac`. Copies are `git archive` of the build commit, with no `.git`. M truth = places
  both raters name, at their own granularity, minus place A.

## F7. Gates before scoring

- The 20-query gate (`replay_254.py gate`) on the census map at `451ff94`: 10 `<server>::<name>` forms
  and 10 file forms. Fewer than 18 exit 0 = the harness is fixed and a new freeze is reported; nothing
  is scored.
- `update` starts no model process: checked in every build's audit log.
- Versions recorded: Graphify 0.9.115 wheel `b9398052…24c5`; `pyright 1.1.410`; node `v26.12.1`;
  Python 3.13.7.

## F8. The operator's three map questions

1. I found where a verdict is written, and what it touches, in under 2 minutes.
2. It shows the parts as I know them.
3. I would open it again.
