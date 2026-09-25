# Tamheed v5.0.0 — skills as the instruction surface, `carries`, and the findings_31 cycle

Status: **EXECUTED — v5.0.0 tagged on `bbdeb4a`, 2026-09-25 (revision 2 approved after the devil's-advocate review).** Index: [README.md](README.md) § Field cycle findings_31.
Execution order differs from the numbering: 114 → 115 → 116 → 112 → 113 → 117 → full test → 118 → 119, because the surfaces plans 112 and 113 edit (the scenario bodies, the write rules) are created by 114-116.
§0 RESULT (2026-09-24, before plan 114): `/tamheed:probe` → `PROBE-OK`; `/tamheed:tamheed` loaded with `Base directory … \skills\tamheed` and the `${CLAUDE_PLUGIN_ROOT}` sentence substituted to the bundle root; the skills list showed `tamheed:probe` and `tamheed:tamheed`. All three passed.
Read-only work only: `findings_31.md` in full; the eighteen `FB-` rows through ACMP's tool-written
`exports/feedback.json` (`count == total == 18`, `partial: false`; never `data/`); the journal through
`csv/progress_entries.csv` (PE-1381…1428); ACMP's diff since findings_30 by file name; its memory and
AGENTS.md rewrites (consistent with the store); **all ten ACMP project skills read in full**; every engine
claim verified at the line (`_note_lesson_rows` :3150, `RELATION_RULES` :144, the DDL `CHECK (relation
IN …)` :636, `_emit_prompt_library` :2955 and its four callers, `handoff_emit` :3232-3593, check.py
lints 8-11, `store.schema_version()` = PRAGMA, the tests that name prompt files, the evals' `prompts/`
greps, `lab/scenario.md:369`, `docs/install.md` in full). **The sub-agent's doc reading was re-checked
against the official pages myself** (`code.claude.com/docs/en/skills`, `/plugins-reference`): two of
its answers were incomplete and one changes the design (§1.6-1.8). **This session's own plugin loader
was probed**: invoking `tamheed` resolved to the ROOT `SKILL.md` in the 4.14.0 cache — the front door
loads today only because the bundle has no `skills/` directory. Three advisor passes. No web research
beyond the two doc pages (every other question is internal).

Interview rulings (2026-09-24), final: **plugin-shipped skills**; the note keeps **pointer +
obligations table + lessons**; the 16 stock prompts **become slash skills**; **5.0.0**; adopt **seven**
ACMP skills (four package-facing, three evidence-facing; the three engineering-only stay ACMP's) as
**procedure + anonymised field evidence**; **`carries`** as a new relation (advisor-confirmed; the edge
is the ONLY carrier); `refresh_stock` **deletes** stale-stock leftovers; the AGENTS.md template **keeps
the lint-identical table** (advisor-confirmed); the adopted skills are **renamed to tamheed vocabulary**
(advisor-confirmed); **I run the loading test** as the first execution step.

---

## 0. The first execution step: the loading test (STOP on failure)

On a scratchpad copy of the bundle laid out as plan 114 will lay it out (front door at
`skills/tamheed/SKILL.md`, a throwaway `skills/probe/SKILL.md`), from a scratch working directory,
with the nested-session guard lifted for that one process (`env -u CLAUDECODE`):

1. `claude --plugin-dir <copy> -p "/tamheed:probe"` → `PROBE-OK`.
2. `claude --plugin-dir <copy> -p "/tamheed:tamheed"` + "print the first line of the skill you loaded"
   → the `Base directory` line names `<copy>/skills/tamheed` and the body's `${CLAUDE_PLUGIN_ROOT}`
   sentence reads as an absolute path (the placeholder substitutes in skill content per the docs).
3. `claude --plugin-dir <copy> -p "list every skill by exact invocation name"` → both
   `tamheed:tamheed` and `tamheed:probe` present.

Any failure STOPS execution before plan 114 and comes back to you with the measured output.
Project-scope enablement (`enabledPlugins` in `.claude/settings.json`) is **docs-confirmed, not
measured**: `--plugin-dir` cannot probe it (it names installed `name@marketplace` plugins) and a real
probe would edit your settings. It is not a STOP condition; install.md states it as the docs do.

## 1. Weaknesses — my 4.14.0 brief, then this plan's first draft, then the engine

**The brief (owned in the next brief)**
1. `deferred-work-reviewed` "44 → 27": measured 44 → **19**. Activated was 25, not 17.
2. "`was rebuilt there`" on the first refresh: measured `is current there; nothing written` twice —
   the note carries no version and nothing it renders had changed. Both halves measured by ACMP.
3. "Both will appear again": half — the `system:work-bind` rows did; the `CLAUDE.md` diff did not.
4. "Your 29 legacy slices": **38** — I missed nine whose items are all Implemented but that have no
   slice-bound AC (`acs-met`).
5. "Rewrite the memory's `44 → 44` line": no such line exists in memory.

**This plan's first draft**
6. **It would have put a `skills/` directory beside the root `SKILL.md` and expected both to load.**
   The docs: *"If a plugin has no `skills/` directory and no `skills` manifest field, a `SKILL.md`
   at the plugin root is loaded as a single skill"* — so the first `skills/` directory silently
   retires the front door. The sub-agent reported "no mention"; the page says it. The front door
   moves to `skills/tamheed/SKILL.md` (name `tamheed` → `/tamheed:tamheed`, the invocation
   `docs/install.md:37` already documents). Every path that names the root file moves with it:
   check.py lints 8, 9 (teaching dict + blacklist scope) and 10 (`link_files`), `tests/test_check_lints.py:56`,
   `CLAUDE.md:67`, `CONTRIBUTING.md:40`, `docs/install.md:112`, `docs/methodology.md:27,76`,
   `README.md:18,374`, `SECURITY.md:24`. The body keeps its bundle-relative tokens (lint 10 already
   resolves `bundle / target`) and gains one sentence: paths are relative to the bundle root,
   `${CLAUDE_PLUGIN_ROOT}`, two directories above this skill's folder.
7. **It costed "≈ 23 descriptions" in every session.** The docs' table: `disable-model-invocation:
   true` → *"Description not in context, full skill loads when you invoke"*. The 16 scenario skills
   cost nothing ambient; only the seven discipline skills and the front door do (≈ 2.5 KB).
8. It wrote "`$ARGUMENTS` only, unverified". Confirmed: `$ARGUMENTS`, `$0…`, `arguments`,
   `argument-hint` all exist. Scenario skills use `argument-hint: [package]` + `$ARGUMENTS`.
9. It read "the plugin will install skills at project level" literally; no mechanism does that.
   "Project level" = `enabledPlugins` in `.claude/settings.json` (docs: user / project / local scopes).
10. It would have moved the obligations table into a skill. Interviewed; it stays ambient.
11. It called `carries` "no schema change". The DDL enforces the relation set: migration
    **`006_carries.sql`** (the 002/004 recreation). Operator cost: none — migrations apply at
    `connect()` on a fresh in-memory DB before the JSONL load; `schema_version` is a PRAGMA
    (`store.py:275`), so no JSONL changes on upgrade; lint 7 needs the CHANGELOG to name the file.
12. It gave the carried advisory two carrier definitions. One: the `carries` edge.
13. It forgot `package_create`, `package_migrate`, `package_adopt` seed the library (`:857`,
    `:3938`, `:4077`) — four callers.
14. It said "after `claude plugin update` the skills follow". The docs: updated skills in a copied
    marketplace plugin need a session restart (`/reload-plugins` covers hooks/MCP, not cached skills).
    The brief says restart.
15. It described the manual install route as "copy `skills/*` too". The docs: a skill folder that
    carries `.claude-plugin/plugin.json` loads as a plugin `tamheed@skills-dir`; whether its nested
    `skills/` is scanned is not stated. install.md states that, and names the marketplace route as
    the supported one.
16. **It let scenario skills cross-reference each other as `/tamheed:<name>`.** Under
    `disable-model-invocation: true` the docs table says "Claude can invoke: No" — a body telling the
    AGENT to read `loop-guard` first (loop-iteration ↔ loop-guard, register-liveness → skill-promote)
    would point at something it cannot invoke. Every cross-reference is classified: operator-next-step
    → `/tamheed:<name>`; agent-reads-now → a Read of `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`.
    Lint 10 skips any token containing `{`, so the new skills lint strips the placeholder and resolves
    the path against the bundle, or those references go unchecked.
17. **It let "stock" shrink to README.** The engine derives stock from the bundle's `prompts/` dir in
    three places (`:470` the prompt-ids-resolve project set, `:2975` the library, `:3259` the handoff
    project set). With README as the only file, the 16 leftovers would read as PROJECT prompts:
    satisfying the "no project prompts" refusal, scanned by `prompt-ids-resolve` (ACMP's population
    22, not 6, until the refresh) and by the restated-content scan. Fix: one `_stock_names()` =
    current stock ∪ history keys, used by all three.
18. **Its anonymisation lint was not stack-neutrality.** `trusting-a-green-test` step 5 names
    Kestrel/TestServer/InMemory/MediatR, step 6 fake timers, `ci-evidence` step 4 Dependabot; the grep
    passes all of it while SKILL.md principle 9 forbids coupling the teaching surface to one stack.
    Plan 115 rewrites those steps stack-neutral ("a test host that does not enforce the production
    server's request limit"; "a job with both `if:` and `needs:`" stays — CI-generic) and the lint
    carries a product/framework denylist with an explicit allowlist (git, CI, the tool names).
19. **Its `carries` roster was the plan's list, not the repo's.** `amends` (the last relation added)
    lives in ~30 files, including `check.py:314`'s hard-coded needles for `governance.template.md`,
    `references/traceability.md`, `modes.md`, `handoff.md`, `prompt-templates.md`, `workflow.md`,
    `follow-up-prompts.template.md`, `docs/workflow.md`, `evals/README.md`, `lab/README.md` and
    `tests/test_store_migrations.py` (005's landing test → a 006 twin). Plan 113's validation is that
    grep, file by file.
20. **install.md:74 says a MAJOR release makes `package_open` refuse until a staged migration runs.**
    5.0.0 does not: the store stays v4-shaped, `schema_version` 6, opens as before. CHANGELOG,
    install.md and the brief settle what "v4 store" means under tamheed 5.x, or ACMP will look for a
    v5 store.
21. **The fixture's README is refreshed by beat 22** while three eval assertions grep its body
    (`evals.json:1155` "Show the record with its id", `:1322` `tamheed:stock-merged`, `:1441`
    `local-tool`). The 5.0.0 README keeps those three needles, and the beat plan checks them before
    dispatch (F-6).
22. "lint 11 (new)" collides with the existing lint 11 (template copies). It is lint 12.
23. **(execution) The beat plan's F-6 grep did not cover `tests/`**: `test_pkg_check_grep_tree` used the
    fixture's prompts folder as a corpus for `gate_run`, a word that lived in the retired files; the
    agent left `tests/**` alone and reported it; the needle was re-aimed in the close-out (F-10).
24. **(execution) The beat plan expected `gate_run` ready on a bare scratch package** — G-SET fails
    there on the nine Always families a bare package never has; the plan's expectation, not the agent's.
25. **(execution) The beat refreshed the fixture's guide to an unreleased body** (the pre-release
    `5.0.0` history key), which left the history at the stamp — the fixture-follow proved
    byte-equality to that body and forced exactly that file (plan 119's note).
26. **(execution, the reviewer's find) The note's flush sentence, since plan 039, named
    `export_html`/`handoff_emit` as JSONL flushers** — only the store writes reach `_commit()`; the
    conclusion held, the mechanism was wrong; corrected in the v5 rebuild, the guide, the template,
    handoff.md and the `package-writes` skill; owned in the brief.

**The engine (findings_31, each verified)**
16. **`FB-017`** — step 15's mechanism is false (`_note_lesson_rows`: pinned + `unpinned[:10]`; any
    unpin of a pinned lesson removes exactly one line while ≥ 10 unpinned Approved remain; retiring
    an unpinned lesson removes nothing). The N-10 count is right.
17. **`FB-018`** — `implements` targets `_REQ_LIKE | _DECISION | {acceptance-criterion}`;
    deferred-work is a legal target of `scope_*` only; "its WBS rows carry it" is prose.
18. "Omitted columns are preserved" reads wider than it is: a partial row still carries every NOT
    NULL column. 19. §3.3: the promotion guard is a paste verifier — one sentence in `skill-promote`.
    §3.4: no ask; recorded as the reason Open rows stay listed.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed (the docs, quoted, or source)**
- Plugin skills: `<plugin>/skills/<name>/SKILL.md` → `/<plugin>:<name>`; the bare `/<name>` also
  works unless taken; a root `SKILL.md` loads ONLY when no `skills/` dir exists; `skills` manifest
  key adds to the default scan; `${CLAUDE_PLUGIN_ROOT}` substitutes anywhere in skill content;
  `disable-model-invocation: true` keeps the description out of context; `user-invocable: false`
  hides from the `/` menu; ≤ 500 lines; descriptions in context, bodies on invocation; invoked
  bodies persist across turns (write standing instructions, not one-shot steps); `enabledPlugins`
  at user / project / local scope; `--plugin-dir` is session-scoped; updated cached skills need a
  restart.
- The DDL enforces relations (006); `schema_version` is PRAGMA-derived; `export_html.py` never
  reads `prompts/`; evals' `prompts/` greps survive (dir, README, project-kickoff);
  `lab/scenario.md:369` names `prompts/orient-resume.md` (beat-22 re-aim); seven contract tests name
  stock files (`:373`, `:1611`, `:1645`, `:1675`, `:1695-1713`), `:1539` pins the cheat-sheet;
  lint 8 stamps `prompts/README.md` (survives); CI = `python check.py` + selftest.

**Rejected**
- "44 → 27"; "was rebuilt there" on an unchanged note; "29 slices"; a root `SKILL.md` beside
  `skills/`; "≈ 23 descriptions"; "no schema change"; two carriers; skills follow an update without a
  restart; skill copies emitted into the project.

**Unresolved — measured in execution**
- §0's four probes. Nested-`skills/` discovery under the manual route (documented as unverified).

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The moved front door does not load, or bundle-relative tokens misresolve from `skills/tamheed/` | §0 steps 2-3 before any skill is written; the `${CLAUDE_PLUGIN_ROOT}` sentence; lint 10's bundle fallback keeps every token checked |
| An agent never invokes `tamheed:package-writes` and writes carelessly | The obligations table stays ambient; the note's first paragraph names the skills and when they apply; descriptions are the trigger sentences ACMP's operator approved; the brief asks ACMP to report whether a skill fired |
| A loop harness pastes `loop-iteration.md` and finds no file | The retired-leftover warning names `/tamheed:loop-iteration`; `prompts/README.md` maps every situation; `-p "/tamheed:<name>"` verified in §0 |
| `refresh_stock` deleting files | Only files byte-equal to a shipped stock body after substitution (today's overwrite proof); reported `retired`; customised copies never touched (warned with the rename advice); tests for both branches; git keeps the deleted tracked file |
| The note v5 rebuild lands in every project at once | Marker `v5`; the pointer-import path rebuilds `<package>/CLAUDE.md` (measured shape); a v4 span is replaced wholesale, warned as today |
| Migration 006 | The 004 recreation pattern; test: a v4.14 fixture copy opens with `schema_version 6`, edges intact, `package_verify` unchanged; lint 7 |
| `deferred-work-carried` reads 25 amber rows at ACMP on day one | Doctrine-correct; the brief's edge recipe (the SC join finds eight, titles the rest) |
| ACMP's project skills duplicate the plugin's | The brief's retirement recipe: `Obsolete` + `custom_attributes.upstreamed_to` (the `superseded_by` FK cannot point upstream); the operator keeps any row whose ACMP instances they value |
| Anonymised evidence still identifies ACMP | Lint over `skills/`: `WBS-|DEF-|LL-|PE-|SC-|DEC-|AC-|#[0-9]|acmp|Keycloak|Webex|Playwright` |
| The teaching lint over 24 new files | `skills/**` joins the teaching dict with the `prompts` blacklist scope (their bodies came from prompts) |
| Docs edited unread | Transactional scripts, one match per edit |
| The lab fixture | Beat 22 retires the fixture's 16 stock files (its subject); `carries` on a temp package (the fixture has a recorded deferred-work omission) |

## 4. Changes made and why

1. The front door moves into `skills/` (docs-mandated; §1.6). 2. Cost statement corrected (§1.7).
3. `$ARGUMENTS` + `argument-hint` used (§1.8). 4. Delivery = plugin skills; "project level" =
enablement (§1.9). 5. Table stays ambient (§1.10). 6. `006_carries.sql` named; no operator step
(§1.11). 7. One carrier (§1.12). 8. Four callers (§1.13). 9. Restart after update (§1.14).
10. Manual route documented as unverified for nested skills (§1.15). 11. The routine cycle keeps its
own plans. 12. Plans renumbered: the front-door move is its own plan (114), gated by §0.
13. Scenario cross-references classified by who acts (§1.16). 14. One `_stock_names()` (§1.17).
15. Stack-neutral evidence skills + a denylist lint (§1.18). 16. The relation roster from the `amends`
grep (§1.19). 17. "v4 store under 5.x" said once (§1.20). 18. The README needles kept (§1.21).
19. Lint numbered 12 (§1.22); enablement scope docs-confirmed, not a STOP (§0).

## 5. The design, concretely

**`plugins/tamheed/skills/`** — 24 directories, each `SKILL.md` (frontmatter `name` == folder,
`description`, flags), ≤ 500 lines, no `{package}` literal, no ACMP identifier:

| Skill (`tamheed:`) | From | Flags | Body |
|---|---|---|---|
| `tamheed` | the root `SKILL.md`, moved | default | unchanged + the bundle-root sentence; the version line stays (lint 8) |
| `package-writes` | ACMP `writing-to-the-package` + the note's cheat-sheet rules | default | full rows / `expect_unchanged` / `substitute` / NOT NULL columns / exports-only reads / the flush rule / tree at the branch op / branch from the remote / sha once pushed / commit prose / SC Merged last / classify unreferenced commits; POINTS at the note's table, never restates it |
| `reading-the-record` | `before-you-cite-a-record` | default | the field not the search; closed rows + journal as decision store; id AND shape sweeps; absence claims; before calling stale |
| `operator-interview` | `interviewing-the-operator` | default | ask now; homework; one decision per question; quote with id; label own prose; never bank; the ceremonies' STOPs |
| `written-claims` | `keeping-written-claims-true` steps 1, 3, 5, 7 | default | the words around a number; hedges in done-claims; inventory as the sweep; retraction greps the shipped diff |
| `test-evidence` | `trusting-a-green-test` | default | the meaning of a Met verdict's `evidence`/`verification_method` |
| `measurement-evidence` | `trusting-a-measurement` steps 1-3, 5, 8 | default | subject, right subject, two sources, after the number |
| `ci-evidence` | `ci-evidence` steps 1, 5 | default | run id + event + tree; the gate list from the workflow — `against_commit` |
| 16 scenarios | the stock prompt bodies | `disable-model-invocation: true`, `argument-hint: [package]` | `{package}` → "the package named in this project's Tamheed note, or `$ARGUMENTS`"; cross-references classified (§1.16): operator-next-step → `/tamheed:<name>`, agent-reads-now → Read `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`; otherwise the current bodies (plan-108 text intact; FB-017's step 15 rewritten in `register-liveness`) |

The three evidence skills are rewritten **stack-neutral** (§1.18): no framework, product or vendor
name; the lint's denylist (`Kestrel|TestServer|MediatR|InMemory|Dependabot|Playwright|Keycloak|Webex|
acmp|WBS-|DEF-|LL-|PE-|SC-|DEC-|AC-|#[0-9]`) with an allowlist (`git`, `CI`, `gh`, the tamheed tool
and rule names).

Each adopted body ends "Field evidence: distilled from a production package's operator-confirmed
lessons (2026); instances anonymised." Standing instructions, not one-shot steps (bodies persist).

**The note v5** (`<!-- tamheed:note v5 -->`): paragraph 1 (package, root, record principle, server
line, `prompts/` = project prompts + README, review.html) + one sentence: "the tamheed plugin's
skills carry the how — `tamheed:package-writes` before any package write or git operation,
`tamheed:reading-the-record` before citing a row, `tamheed:operator-interview` at every STOP; the
scenarios are `/tamheed:<name>` (see `<package>/prompts/README.md`)" + the obligations table
(text unchanged → template unchanged, lint `:1011` untouched) + the STOP line + the lessons section
+ the skills line. The cheat-sheet is gone.

**`_stock_names()`** = the bundle's current `prompts/*.md` ∪ every `stock-history.json` key — the
one definition of "stock" for the prompt-ids-resolve project set (`:470`), the library (`:2975`) and
the handoff project set (`:3259`), so a leftover is never a project prompt (§1.17).

**`_emit_prompt_library`**: current stock = `README.md` only. Leftover pass:
for every history key not in stock that exists on disk: byte-equal to any historical body after
substitution → `leftover_stale_stock`; with `refresh_stock=True` deleted → `retired`; else
`leftover_customized` (rename advice). All four callers. `handoff_emit` warnings name both classes.

**`carries`** (`006_carries.sql`): `RELATION_RULES["carries"] = ({"wbs-item"}, {"deferred-work"})`.
Advisory `deferred-work-carried`: `Activated` rows with no `carries` edge from a WBS item whose
status is not in `('Implemented','Superseded','Obsolete','Rejected')`; note: "an Activated row is
work only while an open WBS item `carries` it (the edge is written with the WBS rows in the
activating batch); when every carrier is Implemented the row is Done — or bind a new carrier".
`replan-deferred` writes the edge in the same batch. Docs: governance relation list, catalog,
entities, quality-gates (twenty-one rules), architecture flowchart edge.

**`agent-control.template.md`**: table identical; "Operating conventions" → a pointer paragraph at
the skills; "Kickoff" → `/tamheed:package-onboarding` + the project prompt.

**`prompts/README.md`** (still emitted, substituted, 5.0.0 history key): project prompts live here;
the situation table maps to `/tamheed:<name>`; leftover semantics; the harness line.

**check.py**: lint 12 (new): every `skills/*/SKILL.md` has `name` == folder and a `description`;
≤ 500 lines; no `{package}`; the scenario set == history keys minus README; the stack-neutrality
denylist/allowlist; every `${CLAUDE_PLUGIN_ROOT}/...` token resolves against the bundle after the
placeholder is stripped; `skills/**` in the teaching lint with the `prompts` blacklist scope;
blacklist += `tamheed:note v4`; lint 9 asserts every retired name keeps its history; lints 8/10 and
the teaching dict point at `skills/tamheed/SKILL.md`; lint 11's governance-template needles +=
`carries`.

**"v4 store" under tamheed 5.x** (§1.20): the MAJOR is the handoff contract; the store keeps its v4
shape, `schema_version` reads 6, `package_open` behaves as before, `package_migrate` answers
"nothing to migrate". Said once in CHANGELOG, install.md (§74 rewritten), the brief.

## 6. Refined execution plan

Constraints: stdlib only; no new MCP tool (19); one migration; CHANGELOG `[Unreleased]` until 119;
released blocks frozen; every dry-run on a scratchpad copy; explicit staging beside the worktrees;
commits from message files; push separately; status every three minutes; §0 before 114.

| # | Plan | Validation → expected |
|---|---|---|
| 112 | **findings_31 doc cycle**: step 15 rewritten (true arithmetic + corollary); the NOT NULL clause (server README, governance, the write rule); the paste-verifier sentence; the five brief errors owned in the batch record | RED/GREEN on the prompt-teaching test; `check.py` |
| 113 | **`carries` + `deferred-work-carried`** (006; rules; advisory; replan prompt; docs across the whole relation roster — every non-fixture, non-plan file the repo-wide `amends` grep names, §1.19) | tests: edge accepted, reverse refused, advisory lists / drops / re-lists; `test_store_migrations` 006 twin of the 005 landing test; v4.14 fixture copy → `schema_version 6`, `package_verify` unchanged; `:4042` tuple += the rule; the `amends` grep re-run: every file also names `carries` or is a retired stock prompt; `check.py` |
| 114 | **The front door moves + `skills/` infrastructure** (after §0): `skills/tamheed/SKILL.md`; lints 8/9/10 + `test_check_lints`; lint 11; the eleven path references; the root file deleted | `check.py`; §0 steps 2-3 re-run on a copy of the REAL bundle |
| 115 | **Seven discipline skills**, stack-neutral rewrites of the three evidence skills (§1.18) | lint 12 clean; each ≤ 500 lines; denylist clean; a reviewer pass (security: standing-instruction surface; neutrality: principle 9) |
| 116 | **Sixteen scenario skills + engine v5**: note v5; README-only library + leftovers + `retired`; four callers; template; `prompts/README.md`; tests rewritten (`:1539` retired; `:1606-1713` re-aimed; new: customised leftover survives refresh, stale leftover deleted only with refresh; `:3205` names the skills) | RED/GREEN; dry-run on a fixture copy: 16 `retired`, README refreshed, `project-kickoff.md` untouched, note v5 in the workspace copy; `-p "/tamheed:slice-kickoff"` resolves; `check.py` |
| 117 | **Docs + diagrams**: README, server README, the moved front door, generated-structure (tree), handoff.md, governance, quality-gates, artifact-catalog, prompt-templates.md, extension.md (006 beside 005), install.md (plugin route; project enablement; restart after update; the manual route's unverified nesting), SECURITY.md (static bundle text; deletion proof; screens unchanged), architecture.md (sequence + an "instruction surfaces" diagram: ambient note / on-demand skills / operator slash skills / project skills), entities.md (skill section: plugin vs project; `carries`), methodology.md, CONTRIBUTING.md, CLAUDE.md layout, CHANGELOG 5.0.0 with the name mapping and `006_carries.sql` | per-behaviour grep ≥ 2 docs; `check.py` |
| — | **Full test**: `check.py`; `accept_v500.py` N/N vs 0/N on an extracted `v4.14.0`; selftest 19/19; §0 on the real bundle; CI | N/N vs 0/N |
| 118 | **Lab beat 22** (agent, opus, worktree; dry-run + F-6 grep first): the fixture's leftovers retired; the fixture README refreshed (its three eval needles — "Show the record with its id", `tamheed:stock-merged`, `local-tool` — kept in the 5.0.0 body, §1.21); the workspace note v5; `carries` + the advisory on a temp package; step 15's arithmetic; the customised-leftover branch on a copy; scenario.md's `prompts/orient-resume.md` sentence re-aimed | new assertions each failing on the pre-beat fixture; evidence report; scenario beat 22 |
| 119 | **Release 5.0.0** (recipe; README history key; stamps; tag; CI) + **the ACMP brief** (transcript-only): the five errors; restart after update; `/tamheed:tamheed`; leftovers → `refresh_stock=true` deletes 14, warns on `integrity-check.md`/`slice-review.md`; note v5 diff; `FB-017` → Resolved (112), `FB-018` → Resolved (113) by the recipe; the 25 `carries` edges; the name mapping + the `Obsolete` recipe for `SKL-001/002/003/004/005/008/010` (operator's choice); memory lines; findings_32 questions | tag; CI; ACMP's rows leave `Reported` |

**Considered and rejected:** keeping the root `SKILL.md` (never loads beside `skills/`; a stale copy);
`handoff_emit` copying skills into the project; widening `implements`; two carriers; the cheat-sheet
kept beside `package-writes`; an overlap release.

## 7. Approval checkpoint

Nothing has been executed. Approving authorizes plans 112–119, commits, pushes and the `v5.0.0` tag
on `main` under the standing git delegation, and the ACMP brief — with §0 run first and execution
stopping on its failure. Behaviour and doctrine changes:

1. **The front door moves** to `skills/tamheed/SKILL.md` (`/tamheed:tamheed`, unchanged invocation).
2. **The instruction surface moves**: 23 more plugin skills; the note v5 loses the cheat-sheet; the
   16 stock prompts are no longer emitted; `refresh_stock=true` deletes stale-stock leftovers.
3. **`carries`** with migration `006_carries.sql`; advisory `deferred-work-carried`.
4. **Seven ACMP skills adopted under tamheed names**, generic, anonymised evidence.
5. **Doc corrections**: step 15; the NOT NULL clause; the paste-verifier sentence.
6. **MAJOR 5.0.0** with lab beat 22.

Approve as written, or name which of the six to change.
