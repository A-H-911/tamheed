# Tamheed 6.8.0: Jisr's FB-023 and FB-024, and the standup report redesigned as a delivery report

> **Plan 249, the round record (2026-11-18).** The approved plan, recorded as approved. The rulings U1-U20
> and the defaults V1-V10 are PROVISIONAL until the operator says yes to the mock (step C, V7). Field data
> appears as ids and counts only.

> NOT the parked plan, which is committed at
> `plans/PARKED-2026-11-17-loop-findings-and-requirement-cascade.md` (`b5feff4`). It moves to
> 6.9.0. This round takes **ADR-0005**, so the parked plan's ADR becomes ADR-0006 (a dated note
> says so).

## Context

The operator read the version-1 pages (Jisr and ACMP copies) and rejected the reading experience:
"hard to read, and still not as I was expecting". The report is a DELIVERY report. It is the fast
way for a reader new to Tamheed to understand a package's state and progress. It answers four
questions in the window and overall:

1. What we did.
2. What we are working on now.
3. What we expect next.
4. The challenges and decisions.

It has one glossary and one tree of the plan, with the phases as its root.

**State:**

- **Nothing is committed.**
- **Plan 250 is built** (FB-023: 89 of 89 lines cut on the fresh Jisr export; FB-024).
- **Plan 251 v1 is built** and both gates pass.
- **Fresh Jisr export:** `Repos\jisr-export-2026-11-18` (HEAD `63896cf`). Jisr withdrew both
  reports, so its next report is a first report. ACMP has none either.
- **Replay:** `scratchpad/replay_251.py`, with its pages in `scratchpad/replay251/`.

## Rulings (operator, 2026-11-18)

| # | Ruling |
|---|---|
| U1 | **One hash-pinned script** (the slate's rule). `standup.js` is named by SHA-256 in the content policy. It loads and sends nothing, and writes no markup. It drives the filters, the search, expand and collapse all, and the remembered colour. Without it the page shows everything, unfiltered |
| U2 | **Filters:** by state, by kind (task, check, milestone) and by phase, plus a text search |
| U3 | **The current slice is the in-progress unit.** Section 5 shows that whole slice as a detailed tree, each item with its own state, plus any other item in progress. The card counts the slice's open and claimed items with a bar |
| U4 | **Visual tests** run in CI and by hand: a headless-Chrome browser check, with screenshots as evidence. No pixel comparison |
| U5 | **Sections:**<br>• Header;<br>• 1 Summary (KPI cards, the headline);<br>• 2 Needs your decision;<br>• 3 Plan overview (the one tree);<br>• 4 What we did (in this window, and overall);<br>• 5 What we are working on now (detailed tree);<br>• 6 What we expect next;<br>• 7 Challenges and decisions (in this window, and overall);<br>• 8 Glossary;<br>• Record details (folded) |
| U6 | **The agent's shares stay** (25, 150, 150, 100, 125, 100 and 25). Over a share is a warning |
| U7 | **These move to the folded Record details:** journal lines, commits, edited rows, rows added, the last handoff's text and "Where we stand" |
| U8 | **No 30-item freeze and no shrink.** Long lists show 8 items, then a fold. The draft result stays trimmed |
| U9 | **Tree table columns:** Item (title, small id, indent) · Status · Progress (bar, done/total; a check's result) · This window |
| U10 | **One state per row, in this order:**<br>1. done this window;<br>2. claimed this window;<br>3. done earlier;<br>4. blocked;<br>5. in progress (claimed earlier, or touched in the window);<br>6. next (the current slice's untouched open tasks, and the next slice);<br>7. not started.<br>Deferred is "postponed", outside the counts |
| U11 | **One colour statement**, plus the rule's colour and reason when they differ. A draft says "Proposed" |
| U12 | **Keyboard:** native disclosure rows (Tab, then Enter or Space) |
| U13 | **ui-ux-pro-max** is installed from the plugin marketplace at LOCAL scope. Only the core skill's search is used |
| U14 | **Phases and slices show a delivery word** (done, in progress, next, not started) with the record status small beside it. A closed phase with open tasks says so |
| U15 | **The tree holds the work only:** phases → milestones · slices → task groups → tasks · checks. "Outside the plan" is a second root. Decisions, defects, risks and questions live in section 7 |
| U16 | **A first report shows "Overall" only,** and says so plainly. The window halves and the window chips are hidden |
| U17 | **Section 7 "Overall":** the open items, one count line per family, and the full lists in folds |
| U18 | **One term, "this window".** The header gives the dates |
| U19 | **Plan 250 is committed first,** on its own |
| U20 | **Mock first.** The operator reads a static mock before any engine or test work |

**Defaults** (approving the plan approves them):

| # | Default |
|---|---|
| V1 | **A check's state:**<br>• passed in the window: done this window;<br>• passed earlier: done earlier;<br>• latest Not-met or Partial: "failed", which has its own chip and is listed again in section 7;<br>• Pending or no result: "not checked yet", counted with the open work of its slice |
| V2 | **A milestone** has no state. It shows its due date ("due in 7 days", "past due" or "upcoming"), and it is outside the counts |
| V3 | **On a first report** nothing counts as touched. In progress is then the current slice's open and claimed items |
| V4 | **"Done overall %"** = done tasks ÷ live tasks under a phase. "Outside the plan" is its own card line (ACMP 64%, Jisr 46%) |
| V5 | **The plugin** stays enabled at local scope for the round, then is disabled unless the operator says otherwise. The headless runs use `--setting-sources project`, so they do not load it (verified in 252) |
| V7 | **The plan 249 record** marks the U rulings provisional until the mock's yes |
| V8 | **The row size** is re-measured on the mock's facts. It is shown with the horizon to GitHub's 50 MB warning, and a large growth goes back to the operator |
| V9 | **Every row's Status column** shows its STATE word (U10, V1). The record's status is small beside it (U14 extended to tasks) |
| V10 | **The glossary** holds the state and tag words too (done this window, claimed done, in progress, next, blocked, not started, postponed, failed, not checked yet), so the chips and the glossary say the same thing |

**Kept from 251 v1 (full text, in force):**

- **The current and next slice.** The agent states `slice_now` and `slice_next`, and the operator
  confirms them at record.
  - The draft suggests the first open slice in plan order and the one after it.
  - The keys are checked against the FROZEN tree, so a correction works.
  - `slice_now` and `slice` are required while the tree holds an open slice, and `slice_next`
    when it holds two or more.
  - They are refused when there is no tree or no open slice.
  - Record refuses a missing or different id in the confirm.
- **Plan order:** phase `sort_order`, then slice `sort_order`, then the id number. Tasks and
  checks follow the id number, compared as numbers.
- **Inline titles:** at the first mention in each section (8 words, then "…"). The names are
  frozen at the draft for the facts' texts, and at attach for the words. The facts never change
  after the draft. An id inside a row's own title shows its name on hover. The work-done fold
  keeps small ids.
- **The way back:** the facts keep every 6.7.0 key, and the frozen 6.7.0 page copy is the way-back
  test.
- **The 40 family definitions** (truth-checked). A package's own families show their label. The
  kinds come from the row's ids.
- **The colours:** the OS colours plus the switch.
- **FB-023:** the skill and the parser cut, as built.
- **FB-024:** the texts and the refusal, as built.
- **The draft result:** `plan_summary`, and `corrects_narrative` without `_names`.

## 1. Weaknesses of the rejected plan (and of 251 v1)

1. **The CI proof could not run.** The rejected plan pushed a feature branch, but CI runs only on
   a push to main, on a pull request, or by `workflow_dispatch` (`ci.yaml:10-14`).
2. **It put the browser step INSIDE Job 1.** The workflow's own rule says "Job 1 runs EXACTLY
   `python check.py` … all checks are stdlib (D-U3)". The precedent for a non-stdlib check is a
   separate job (`server-smoke`).
3. **It said only "install at local scope".** It missed that `plugin install --marketplace`
   adds the marketplace at USER level, so the marketplace must be added with `--scope local`
   first.
4. **It ignored the readers' browsers.** The Jisr operator works on macOS, and only Chrome would
   be tested. CSS grid on `<summary>` is the known weak spot in Safari.
5. **It claimed ADR-0005 without noticing** that the parked plan had reserved that number.
6. **It named no list of where a new bundle file must be registered.** `slate.js` appears in
   CLAUDE.md, the server README, SECURITY.md, `generated-structure.md`, the reference and the
   tests.
7. **The 250 separation had no concrete method** (shared files: the server, the guide content,
   the CHANGELOG, two test files, `index.html` and the figures).
8. **The 251 v1 weaknesses still drive this revision:**
   - it was designed from ASCII previews;
   - there was no summary;
   - the window and overall were mixed;
   - agent-facing lists dominated;
   - there were two glossaries;
   - the tree was a narrow nested list;
   - the categories overlapped;
   - the status words misled;
   - the colour line contradicted itself;
   - the counts disagreed (33 against 34);
   - no visual test existed.

## 2. Assumptions

**Confirmed by direct read, command or measurement:**

- **The script and the policy:**
  - the slate page's pinned script and its policy (`slate_page.py:43`, SECURITY.md :175-182);
  - the standup page's "no script" text (SECURITY.md :206-213), which must change.
- **CI:**
  - the triggers are push to main, pull_request and workflow_dispatch;
  - Job 1 runs `check.py` only;
  - `server-smoke` is the separate-job precedent;
  - no test or lint pins `ci.yaml`;
  - CLAUDE.md :37 and :50 and README.md :480 describe CI.
- **Researched:** the Ubuntu 24.04 runner image 20261111 ships Google Chrome 157 and ChromeDriver
  (actions/runner-images, Ubuntu2404-Readme).
- **The local install:**
  - `claude plugin marketplace add --scope local` and `claude plugin install --scope local` exist
    on 2.1.326;
  - `.claude/settings.local.json` is gitignored (`*.local.json`);
  - the committed `.claude/settings.json` holds only the tamheed marketplace.
- **The skill repository:**
  - `main` is at `f2cc365` (2026-11-18 10:05Z), so it moves daily;
  - seven skills are under `./.claude/skills/`;
  - the core `search.py` and `core.py` make no network calls;
  - the `design` extra's `generate.py` loads `~/.claude/.env`.
- **`check.py`** lists its suites by name, so new test files must be added there.
- **The U10 counts** were measured (they sum to every live task). Jisr's window has 0 in
  progress, hence U3.
- **ADR numbers:** ADR-0001 to ADR-0004 exist. 0005 is free in the repo.

**Rejected:**

- "push a branch to prove CI";
- "a step in Job 1";
- "Chrome alone proves the layout".

**Still to verify (each has a step):**

- the plugin's installed commit and its cache path;
- Safari rendering (the operator's Mac);
- the measured row size;
- that the headless runs ignore local settings.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The page gains a script | **The slate's rules:**<br>• one inline script whose exact bytes are hashed into the policy;<br>• `base-uri 'none'` and `form-action 'none'`;<br>• no markup written;<br>• the stored colour accepted only as `auto`, `light` or `dark`, in try/catch.<br>ADR-0005 and SECURITY.md. **Tests:**<br>• the hash equals `sha256(standup.js)`;<br>• exactly one script block;<br>• no `on*=` attribute;<br>• hostile titles stay inert.<br>A security review before the 251 commit |
| Counts disagree | ONE `row_state()` (pure, in `standup_facts`) feeds the cards, the tree, the badges and the sections. A test runs a fixture holding every state and makes all views agree |
| The mock is rejected again | Three mock pages (the Jisr window, Jisr first, ACMP first), built under the real policy, in light and dark, at 1280 and 375 px. Iterate until the operator says yes. No engine work before |
| Safari breaks the layout | No grid on `<summary>` itself: a grid on an inner element, flexbox fallbacks, `:has()` used only for the colour switch. The operator opens the mock in Safari on the Mac, and that is part of the yes |
| The CI browser job is flaky | A separate job: setup-python, Node 22, build the fixture page, run the check, and fail when Chrome is missing. It is proved by `gh workflow run ci.yaml --ref <branch>` after pushing the branch, on the operator's word |
| The 250 separation is wrong | The method is in step A2. Proof: the 250-only diff is reviewed by hunk, both gates pass, and the 250 tests are red at HEAD and green after |
| The plugin is unpinned, or an extra fires | Record the installed commit. Use only `search.py` (read-only). Disable at the round's end (V5) |
| 6.7.0 cannot redraw new rows | The facts keep the 6.7.0 keys. The way-back test stays |
| Rows grow fast | V8: measured and shown with the mock. The operator decides on the facts |
| Field text in the public repo | Mocks and screenshots stay in the scratchpad and `.playwright-mcp/` (gitignored). Evidence holds counts only |

## 4. Changes made by this review, and why

| Change | Why |
|---|---|
| The CI proof uses `workflow_dispatch` on a pushed branch (on the operator's word), not a plain push | Weakness 1 |
| The browser check is a separate CI job, and D-U3, the CI comment, CLAUDE.md and the README text are amended | Weakness 2 |
| The marketplace is added with `--scope local` before the install | Weakness 3 |
| The Safari constraints, and a Safari read of the mock | Weakness 4 |
| ADR-0005 is taken here, and the parked plan's note moves its ADR to 0006 | Weakness 5 |
| The registration list for `standup.js` (step D) | Weakness 6 |
| A concrete separation method (step A2) | Weakness 7 |
| V9 and V10 (state words in the Status column, the state words in the glossary) | Consistency (request item 10) |

## 5. Refined execution plan

**A. Record and commit 250 (U19).**
1. **Plan 249:**
   - `plans/249-field-round-6.8.0.md` holds the rulings (provisional, V7), the defaults and the
     measured counts;
   - the plan rows;
   - a dated note in the parked plan (6.9.0, ADR-0006);
   - the round's memory entry.

   Output: one docs commit, on the operator's word.
2. **Separate 250:**
   1. Copy every changed and untracked file to `scratchpad/wip251/`.
   2. Restore every file to HEAD.
   3. Re-apply ONLY the 250 hunks with a script that reads the saved diff and keeps hunks by
      file and anchor:
      - `standup.py` (`_GIVEN`, `_kept`);
      - the server refusal (lines 2317-2319, line-neutral);
      - the eight texts and the stock-history key;
      - the session-handoff skill;
      - design-decisions;
      - the guide's `section.tools.upsert.2`;
      - the CHANGELOG `[Unreleased]` "Fixed" block;
      - `test_given_rulings_never_read_as_requests`;
      - `test_an_unknown_column_refusal_names_the_columns_the_item_takes`.
   4. Rebuild `index.html`.
   5. Both gates.
   6. Review the diff by hunk.
   7. Commit, on the operator's word.
   8. Copy `wip251/` back. Its diff against the new HEAD is then 251 only, which `git diff
      --stat` proves.

**B. The skill (U13).**
1. `claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill --scope local --json`.
2. `claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill --scope local --json`.
3. Check that only `.claude/settings.local.json` changed (`git status` clean).
4. Record the commit and the cache path.
5. Run the core `search.py`: `--design-system "delivery status report data-dense tree table"
   --density 8`, and `--domain ux` for dark mode, contrast, chips, tables, progressive disclosure
   and focus.
6. Output: a short "applied rules" note in the evidence.

**C. The mock (U20).** A throwaway script in the scratchpad.
1. It renders three pages (the Jisr window, Jisr first, ACMP first) from the copies' frozen
   facts, under the real policy with a pinned script. Each has every section, the tree table
   (U9), the states (U10, V1, V2, V9), the KPI cards, the chips and search working, one
   glossary, Record details, and the colour statement.
2. Screenshots: light and dark × 1280 and 375 px, plus a script-off view.
3. Measure the row size (V8).
4. **Validation:** the operator reads it, including on Safari. Iterate until they say yes.

**D. Build 251 v2 (after the yes).**
- **Engine:** `row_state()` (U10, V1 to V3); touched ids; Deferred; uncapped lists; the facts
  keep the 6.7.0 keys.
- **Page:** the mock's layout made real.
- **Script:** `standup.js`.
- **Policy:** with the hash. The slate's `script_hash` helper is reused.
- **Tool:** the budget, shrink and warning are removed; the shares are unchanged.
- **Skill** `standup`: section names, and the four questions mapped to the keys.
- **Registration of `standup.js`:**
  - CLAUDE.md layout;
  - the server README;
  - SECURITY.md;
  - ADR-0005;
  - `generated-structure.md` if it lists `reports/`;
  - the tests.
- **Docs:**
  - the CHANGELOG `[Unreleased]` is rewritten (limits removed, script added);
  - the EN and AR guide keys;
  - the ADR-0003 note;
  - D-U3 amended;
  - the CI comment, CLAUDE.md :37/:50 and README :480;
  - the contradiction sweep (1,400, 2,000, 2,700, 30 items, no script).
- **Python tests:**
  - the state table and the overlaps;
  - V1 to V3;
  - D-T1 (no next slice matches no "None");
  - the views agree;
  - sections and ids;
  - one glossary, with the state words;
  - Record details folded;
  - first report;
  - the colour statement;
  - the policy hash;
  - one script, no handlers;
  - the data attributes;
  - uncapped lists;
  - the way back;
  - hostile titles;
  - goldens with `--regen`.
- **Browser check:** `tests/standup_browser_page.py` (it builds the page in a temp folder),
  `tests/standup_browser_check.js` and `tests/run_standup_browser_check.mjs`. It checks:
  - the script ran, with no policy violation;
  - each chip and the search show the right rows;
  - expand and collapse all;
  - the switch, and that it is remembered;
  - contrast of at least 4.5:1 for the tag text and 3:1 for the bars, in both themes;
  - no overflow at 375 px;
  - print hides the controls;
  - screenshots on request.
- **CI:** a new `standup-browser` job.
- **Field replay** of the four pages, read by the operator.
- **Commit, on the operator's word:** a branch push, `gh workflow run` green, then main.

**E. Plan 252:** a headless `/tamheed:standup` on a seeded lab copy (a second report), cap
5 USD. It verifies that local settings are not loaded.

**F. Plan 253:** stamp 6.8.0, `refresh_lab_680.py`, CI green, tag, and two briefs (pinned and
rehearsed). Disable the plugin (V5).

## Verification

- `check.py` on 3.13 and 3.10. Each new test is red at the parent commit and green after.
- The browser check passes by hand and in CI (by `workflow_dispatch`).
- Screenshots of the mock and the final pages: light and dark, 1280 and 375 px, and Safari by
  the operator.
- The operator's yes on the mock (step C) and on the final pages (step D) before each commit.
- The field replays open clean, change no file under `data/`, and every count agrees.

## 6. Approval checkpoint

Approving approves:

- U1 to U20, V1 to V10, the kept rulings and the changes above;
- the order: A (249, 250) → B (the skill) → C (the mock, your yes) → D (251 v2) → E (252) →
  F (253);
- each commit, push and `workflow_dispatch` on your word;
- the round's memory updated right after this approval;
- about 15 USD of headless runs.

Nothing from the parked plan except its dated note.
