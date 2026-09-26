# Changelog

All notable changes to Tamheed are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Lineage.** Entries ≤ 1.0.x record this project under its former name, **Keystone**, in its
> original repository (<https://github.com/A-H-911/keystone>). Tamheed carries Keystone's full git
> history; the Keystone repository stays frozen at 1.0.x for existing v1 packages.

## [Unreleased]

### Fixed
- **`handoff_emit`'s `stock_merged` check verifies the whole declared release** (plan 129, the
  field's FB-023). The 5.1 check required only the lines the declared release ADDED over the
  previous one, so a `stock-merged 4.9.0` marker over a 4.2.1-era body read `verified: true, 0/9`
  with 38 of 4.9.0's 62 lines absent. Every non-blank line of the declared body is required now;
  each absent line is attributed to the release that introduced it (`missing_by_release`), the
  reason names the counts per release, and `delta_missing` stays beside it. Report-only, as before.
- **`handoff_emit`'s stale-warning block: its home, its text, its removal** (plan 130, the field's
  FB-024). In the pointer-import case the block was appended to the ROOT `CLAUDE.md` while the
  emission's own warning said the root was left untouched; it now lives beside the note in the
  package's `CLAUDE.md`, the warning names its add/remove separately from the span, and a 5.1-era
  block left in the root is stripped once and said so. The text names agent-control, prompt and
  skill files (the scan's scope), not "v1 references" and "the v1 tree". Removal is tail-aware:
  a stale → clean cycle leaves the file byte-identical (5.1 left two extra newlines).

### Added
- **Two more results name their discipline skill** (plan 131, findings_33 Q1 — measured: no
  discipline skill loaded without a tool result naming it, and the note naming all eight cued
  none). `entity_query` carries `skill: tamheed:reading-the-record` on every result — the row
  arrives with its cue; the `entity_export` file, a script's input, never carries it.
  `handoff_emit` carries `skill: tamheed:written-claims` exactly when a scan found something to
  fix (restated content, a stale reference, an oversized prompt, an unverified marker).
- **`system:skill-guard`** (plan 131, findings_33 §4): a skill row's `lifecycle_status` move, and
  the arrival of `upstreamed_to` or `superseded_by`, is journalled by the engine as a `transition`
  (result key `skill_audit`) — never on the row's insert, never on an idle re-send; an omitted
  `lifecycle_status` reads as unchanged. It counts toward `handoff-current` like every transition.

- **The discipline skills absorb the field's rules** (plan 132; the field's FB-025 and the
  forty-four generic gaps read out of a project's 113 carried rules, each verified at the file):
  `measurement-evidence` gains step 6 "Cause, control and classification" (eight rules: a positive
  control proves firing, not coupling; what you changed to observe it; one calibration per check;
  reproduction confirms, intervention explains; a root-path tool names a path; classify from source;
  a layer no test reaches; two instruments disagreeing) and the singular-over-plural subject;
  `written-claims` gains step 8 "A live surface carries the command, not the answer", step 9 "Read
  the predicate a scope claim describes", the build-time sweep by name, the ruling sweep, and
  attribution; `reading-the-record` gains the constraint-first shortlist, the bundled-property
  remedy, and "what binds is the note's roster"; `ci-evidence` gains every-workflow/`cancelled`,
  "Attribute a red by its signature", "Recording a red", the early-stopped job and one-at-a-time
  verification; `operator-interview` gains the absent reason, per-item verdicts and the
  moved-premise rule; `test-evidence` gains the local race fix and coverage-versus-calls;
  `package-writes` gains §12 "Coupled rows move in one batch", the unexplained branch and the
  shell chain that fails open.
- **The hook prints up to 4,000 characters of the handoff** (plan 132; = the resume block's own
  cap; 5.1 printed 2,000 — a 12-line field handoff was already 1,735). `session-handoff` says so
  ("under 25 lines and 4,000 characters") and teaches the close-out order: status moves, the
  handoff, the commit, the bind.

### Changed
- **`lessons-stranded` measures the Promoted lessons** (plan 131): its `population` is
  `{table: lessons, unit: "promoted lessons"}`, not the whole table the join reads.
- **The AGENTS template points at the note's obligations table** (plan 132): its own copy is gone —
  one copy, no drift; the handoff sentence stays. Nothing to do in a project whose AGENTS.md
  already has no table.

## [5.1.0] - 2026-09-26

**MINOR — the findings_32 batch: the resume surface, the menu contract, and the five notes (plans
120–128; field report findings_32, `FB-019`–`FB-022`).** The v5 premise — discipline skills load on
relevance — is broken in a crowded host: with thirty-three plugins enabled most skill descriptions
reach the model name-only, and none of the seven fired across a full field round. Now the note and the
tool results name the skill, the seven discipline skills leave the `/` menu, and the state a session
stops in has a typed home. Migration `007_handoff.sql` ships (applied at connect; `schema_version` 7;
`skills.jsonl` rewrites once on the first close because every column serialises). No new tool (19).

- **The `handoff` journal kind and the resume block (plans 121, 122).** `progress_update` accepts
  `event_type: "handoff"` — where a session stopped, written LAST. `package_open` and `server_info`
  return a `resume` block: the latest handoff with its `correction` chain, `handoff_behind`, the open
  feedback, the open slices, the last three journal ids, the lock holder, the next step and the skill to
  invoke. review.html gains a Resume section after the overview.
- **The SessionStart hook (plan 123).** `hooks/hooks.json` runs `server/resume_hook.py` on every
  session start, resume, clear, compaction and fork and prints the resume block into context: guarded
  (silent without a tamheed note in `CLAUDE.md` or behind one `@` import), lockless, screened by the
  injection gate, capped at 40 lines, one line and exit 0 on any failure. Plain stdout, never JSON.
- **Two advisories (plan 122).** `handoff-current` lists the work-done/transition entries no handoff
  covers (indeterminate before any work is journalled); `lessons-stranded` (only when the package has
  skill rows) lists Promoted lessons whose retired skill row has neither `superseded_by` nor the new
  `upstreamed_to` — the field's `FB-020`. Twenty-three package-scope advisories.
- **The menu contract and the result hints (plan 120).** The seven discipline skills carry
  `user-invocable: false` (menu 24 → 18; model listing 8 → 9 with `session-handoff`); lint 12 enforces
  exactly one flag per skill. `audit_record` names the evidence skill(s) by `verification_method`,
  `readiness_check` names `operator-interview` on a blocking failure, `progress_update` names
  `session-handoff` on a handoff. The note paragraph names all eight skills and carries the handoff
  sentence; the obligations table and the `v5` marker are unchanged (the span rebuilds once).
- **The skills (plan 124).** New `tamheed:session-handoff` (in the menu and model-invocable);
  `orient-resume` reads the resume block first and uses `server_info` after a compaction; five
  practices adopted (never manufacture a status, a rename skips quoted text, a carried premise is a
  claim, fix the file never the pointer, ask before anything destructive — the agent cannot see a
  permission prompt); `integrity-check` absorbs the `changed_columns` re-derivation and lessons
  liveness (`FB-019`); `skill-promote` states the correction and retirement doctrine (`FB-020`,
  `FB-021`). The AGENTS template keeps only `owner` in its frontmatter.
- **handoff_emit's scans (plan 125).** A declared `stock-merged X.Y.Z` marker is verified against
  the stock history (`stock_merged`); a project prompt over 300 lines or 24,576 bytes is named
  (`oversized_prompts`); every file the skills table points at is scanned for stale sentences,
  including the retired "export_html flushes" claim; the restated-content scan gains `status-claim`
  and `id-dense`; the tool-owned note span is stripped before every scan (a latent second-emit false
  positive on a target with the note inline), and the pointer case scans the package's `CLAUDE.md`.
- **Docs (plans 123, 126).** `docs/install.md` corrects project-only enablement (`FB-022`:
  `enabledPlugins` merges key by key; disable at user scope, then enable at project scope; the Claude
  Code bug reported) and documents the hook with a `settings.json` fallback; SECURITY.md gains trust
  boundary 5 and the hook control; `extension.md` describes scenario and discipline skills and hooks;
  the resume flow is diagrammed in `docs/entities.md` and `docs/architecture.md`.

## [5.0.0] - 2026-09-25

**MAJOR — the findings_31 batch: the instruction surface moves into plugin skills (plans 112–119;
field report findings_31, `FB-017`, `FB-018`).** The always-loaded note and sixteen stock prompt
files carried tamheed's execution discipline into every project and were refreshed one package at a
time; now the plugin ships it — seven discipline skills loaded on relevance, sixteen operator-invoked
`/tamheed:<name>` scenario skills, the front door at `skills/tamheed/SKILL.md` — updated by
`claude plugin update` alone. The handoff contract changes (what `handoff_emit` emits, what the
note holds, where the scenarios live), hence MAJOR; **the store stays v4-shaped** (`schema_version`
6 after `006_carries.sql`, applied at connect — no `package_migrate` step). One operator action per
project: `handoff_emit(<repo>, refresh_stock=true)` rebuilds the note as v5 and deletes the retired
stock files that are byte-equal to a shipped release. An acceptance script of nine discriminating
checks passes on this tree and fails, each for its own reason, on an extracted `v4.14.0`; the
front door and the slash skills were measured loading through `claude --plugin-dir`; lab beat 22
fired every mechanism against the recorded package after a dry-run on a copy and the F-6 grep.
No new tool (19). The stock library is `README.md` alone — the sixteen scenario files are retired from
the bundle (their bodies stay in the history for the leftover classifier) — and migration
`006_carries.sql` ships.

The findings_31 batch (plans 112-119; the master record is `plans/112-119-batch-findings-31.md`).
**MAJOR: the handoff contract changes** — the instruction surface moves from the always-loaded note
and sixteen stock prompt files into plugin-shipped skills. **The store stays v4-shaped**:
`schema_version` reads 6 after migration `006_carries.sql`, `package_open` behaves as before and
`package_migrate` answers "nothing to migrate" — no operator step. The one operator action is
`handoff_emit(<repo>, refresh_stock=true)` per project, which rebuilds the note as v5 and deletes
the retired stock prompt files that are byte-equal to a shipped release.

- **The front door lives at `skills/tamheed/SKILL.md` (plan 114).** A plugin with a `skills/`
  directory loads no root `SKILL.md` (Claude Code docs), so the front door moved first — its
  invocation stays `/tamheed:tamheed`. check.py lint 12 keeps every plugin skill well-formed
  (name == folder, a description, ≤ 500 lines, no `{package}` placeholder, `${CLAUDE_PLUGIN_ROOT}`
  paths resolve, stack-neutral, no field identifiers).
- **Seven discipline skills (plan 115)**: `tamheed:package-writes`, `reading-the-record`,
  `operator-interview`, `written-claims`, `test-evidence`, `measurement-evidence`, `ci-evidence` —
  generic procedure plus anonymised field evidence, adapted from a production package's
  operator-confirmed skills (`writing-to-the-package`, `before-you-cite-a-record`,
  `interviewing-the-operator`, `keeping-written-claims-true`, `trusting-a-green-test`,
  `trusting-a-measurement`, `ci-evidence`). Loaded on relevance wherever the plugin is enabled.
- **Sixteen scenario slash skills + engine v5 (plan 116).** `/tamheed:slice-kickoff`,
  `/tamheed:progress-sync`, `/tamheed:orient-resume`, … (`disable-model-invocation`: the operator
  invokes, as they pasted; `$ARGUMENTS` names another package). The stock library is
  `prompts/README.md` alone; a retired file left on disk is a `leftover_stale_stock` (deleted only
  with `refresh_stock=true`, reported `retired`) or a `leftover_customized` (kept, named). The note
  is v5: the obligations table, the lessons and the skills line stay; the tool cheat-sheet goes;
  the flush sentence names the store writes that flush JSONL (`export_html` and `handoff_emit`
  write other files — the mechanism the note had carried since plan 039 was wrong; the
  conclusion held). `agent-control.template.md`'s conventions point at the skills.
- **`carries` (wbs-item → deferred-work) and the `deferred-work-carried` advisory (ACMP's
  `FB-018`; plan 113; migration `006_carries.sql`, the 002/004 recreation).** "Its WBS rows
  carry it" is measurable now: the advisory lists Activated rows no OPEN item carries — every
  carrier Implemented means the row is Done. `replan-deferred` writes the edge in the batch.
- **findings_31 doc cycle (plan 112)**: `register-liveness` step 15 states the true note-budget
  mechanism (ACMP's `FB-017`); a partial row still carries every NOT NULL column; the promotion
  guard is the paste verifier.

## [4.14.0] - 2026-09-24

**MINOR — the findings_30 batch: `ready` follows its own doctrine, three honesty fixes, the sweep
prompt's four gaps (plans 106–110; field report findings_30 and `FB-016`).** ACMP's first day on
4.13.0 answered the last brief's questions on every value and filed one row: `readiness_check`
called a slice with no criteria and no work items ready while `quality-gates.md` said an empty
slice is not ready and the review page's own per-slice panel had always rendered it "not ready".
**Behaviour change, named first:** `ready` is now false while ANY blocking rule is `indeterminate`,
and the result carries `indeterminate: [rule names]`; a loop harness reading `ready=` at slice
scope halts on an empty slice, and `loop-iteration.md` says what that means. The `Implemented`
transition guard is unchanged. Three honest-reporting gaps closed: `deferred-work-reviewed` no
longer lists an Activated row forever, the pointer-import warning says what it did, and the review
page says when nothing awaits an answer. The guard that could only pass is refused:
`expect_unchanged` naming a column the item does not carry. The sweep prompt closes the four gaps
running it end to end exposed. An acceptance script of nine discriminating checks passes on this
tree and fails, each for its own reason, on an extracted `v4.13.0` tree; lab beat 21 fired every
mechanism against the recorded package after a dry-run on a copy and the F-6 grep of the eval case.
No migration; no new tool (19); three stock prompt bodies (`README.md`, `register-liveness.md`,
`loop-iteration.md`).

The findings_30 batch (plans 106-111; the master record is `plans/106-111-batch-findings-30.md`).
ACMP's first day on 4.13.0: every prediction held on its values, the channel worked end to end on
its first new row, and the round's one engine finding was a contradiction between the doctrine
and the tool. Additive, MINOR. **No migration.** **One behaviour change harnesses read, named first.**

- **`readiness_check().ready` follows its own doctrine (ACMP's `FB-016`; plan 106).**
  `quality-gates.md` said "an empty slice is not a ready slice" and the review page's per-slice
  panel had always rendered one as "not ready"; the tool said `ready: true`, because `ready`
  ignored `indeterminate` — 29 of the field's 44 slices read ready on a blocking rule that measured
  nothing. Now `ready` is false while ANY blocking rule is `indeterminate`, and the result carries
  `indeterminate: [rule names]`. **A loop harness reading `ready=` at slice scope halts on an empty
  slice** — `loop-iteration.md` says what that means (record the rows the slice lacks; it is not a
  failure). The `Implemented` transition guard is unchanged: `fail` only, so history's empty slices
  still close. A package that has recorded no defects records the family's omission, or every
  scope's `defects-closed` stays amber (plan 077, applied uniformly).
- **Three honesty fixes (findings_30 §3.2-3.3, Q1.4; plan 107).** `deferred-work-reviewed` lists
  Open and Scheduled rows only — an Activated row is work (its WBS rows carry it) and used to stay
  amber forever; the pointer-import warning says `was rebuilt there` only when the note changed;
  the review page says when the unanswered feedback fold is empty instead of omitting it.
- **`expect_unchanged` refuses a column the item does not carry (findings_30 Q3; plan 108).**
  Under 4.13.0 naming an omitted column passed and asserted nothing — a guard that can only pass.
  Beside a `substitute` every column is carried, so nothing changes there. `register-liveness.md`
  closes the four gaps running it end to end exposed: name only carried columns (step 7), search
  across families for an existing ruling before framing any interview (step 10), the rule's new
  population (step 11), the note's render arithmetic (step 15).
- **Documented from the field**: `substitute` on `lifecycle_status` is the cheapest correct status
  flip (25 moves in one round, zero transport). findings_19 §3 closes: a `substitute` FK failure
  names the column.

## [4.13.0] - 2026-09-23

**MINOR — the findings_29 batch: the feedback channel's middle, the header read, three guard
refinements (plans 100–104; field report findings_29 and the two `FB-` rows it carried).** ACMP's
first week on 4.12.0 answered the question the last release asked: the four capabilities worked on
real repairs, and the field found what only use finds. **`FB-014`**: a request that went upstream
had no liveness surface — `handoff_emit` named a row only while it awaited the operator or the
export, nothing journaled the move within the bound set, and the review page filed unanswered
reports under a closing heading; now the move is journaled as bookkeeping (the row never claims a
word it did not get), the `feedback-unanswered` advisory and a third warning name every reported
row until `resolved_in` is set, and the page splits unanswered from closed. **`FB-015`**:
`server_info().package` reads back all ten header columns, a superset of the write. **Three
guards**: `go_no_go` is presence-checked (the last brief's refusal probe re-sent the stored verdict
and could not fail); `substitute` refuses the re-run shape the field derived by reading (a
replacement that contains its needle, already present, would compound); `expect_unchanged` honours
omission — a sent column must match, an omitted one is preserved by the UPDATE — and, the security
review's finding, runs against the FINAL row, after the engine's own column writes. The disposition
recipe is now taught as a partial row, because "full rows, as stored" was the riskier instruction
on a bound row. `register-liveness.md` walks `feedback-unanswered` and the `prompt-ids-resolve`
step plan 093 had left out. An acceptance script of eleven discriminating checks passes on this
tree and fails, each for its own reason, on an extracted `v4.12.0` tree. Lab beat 20 fired every
mechanism against the recorded package after every new surface was dry-run on a copy of it first.
No migration; no new tool (19); two stock prompt bodies (`README.md`, `register-liveness.md`).

The findings_29 batch (plans 100-105; the master record is `plans/100-105-batch-findings-29.md`).
ACMP's first week on 4.12.0: the four answers worked; two new rows (`FB-014`, `FB-015`) and four
findings about the guards. Additive, MINOR. **No migration.**

- **The feedback channel's middle (ACMP's `FB-014`; plan 100).** A `Reported` row upstream never
  answered had no liveness surface. Now the move WITHIN the bound set (`Confirmed → Reported`,
  `Reported → Resolved`) is journaled as `transition` by `system:feedback-guard` with bookkeeping
  text — the row never claims a word it did not get; the advisory `feedback-unanswered` names every
  reported row with no `resolved_in` (registers excluded; emitted only when the package has feedback
  rows, the plan-079 posture); `handoff_emit` carries a third warning, ids only; the review page's
  middle fold splits into *Reported upstream, not yet answered* and *Resolved or rejected (kept as
  evidence)*; one predicate serves all three. The disposition recipe is taught as a PARTIAL row —
  `id`, `kind`, `title`, `lifecycle_status`, `resolved_in`, `upstream_ref` — because omitted columns
  are preserved and the drift guard is presence-checked (the 4.12.0 brief's "full rows, as stored"
  was the riskier instruction). `register-liveness.md` gains walk steps for `feedback-unanswered`
  and for `prompt-ids-resolve`, which plan 093 had left out of the sweep prompt.
- **The header read is a superset of the write (ACMP's `FB-015`; plan 101).** `server_info().package`
  reports all ten columns — `mvp_definition` and `created_at` were writable or stored and readable
  only through `review.html` — and, on a migrated package, `v1_manifest_derived` (the page's
  annotation, as data).
- **Three guard refinements (findings_29 §1, §3, §4; plan 102).** `go_no_go` is PRESENCE-checked:
  naming it without the operator's word is refused whatever the value (the brief's probe re-sent the
  stored verdict and could not fail); an attested re-send writes no audit row. `substitute` refuses
  the re-run shape — `new` contains `old` and already occurs — with the remedy in the message.
  `expect_unchanged` honours omission: a sent column must match, an omitted column is preserved by
  the UPDATE and never counts as drift (the retire path had said so since plan 040; this path said
  the opposite and refused a correct partial write). The JSON refusal is named for what it checks,
  `custom_attributes`. Both id rules say a green means every id RESOLVES, not that the sentence
  about it is true. Read off ACMP's journal while checking the feedback table: `work_bind`'s row
  was the one engine-written row with NO actor — it now signs `system:work-bind`.

## [4.12.0] - 2026-09-23

**MINOR — the findings_28 batch: the four capabilities the feedback channel asked for, the review
page's catch-up, and the channel's return half (plans 091–098; field report findings_28 and the
thirteen `FB-` rows it carried).** The channel worked on its first use: ACMP filed thirteen rows,
every one confirmed by an operator who refused to rubber-stamp them — one tool was deleted when
asked what it computed — and exported them as a digest-stamped file. This release answers the four
requests. **`FB-004`, a substitute write**: `{"type", "id", "substitute": {"<column>": ["<old>",
"<new>"]}}` changes one token in one column without the whole row passing through the agent's
output; the server materializes the stored row, replaces the exact text, and sends the result down
the ordinary full-row path, so every guard, trigger, `expect_unchanged` and `changed_columns` judge
it as a caller's row and there is no second guard to have holes in — the security reviewer's one
finding, a match glued to a digit (`DEC-20` inside `DEC-208`), is refused by name. Recorded twice
before as "not built"; the field showed it had changed a decision. **`FB-001`, a writable header**:
`entity_upsert(type="package")` writes `title`, `mode`, `iteration`, `mvp_definition`,
`entry_point` and `go_no_go` — the verdict only on the operator's word, journaled — special-cased
and never a family, so no package's review page or CSV set changes for it. **`FB-002`, the prompt
files** (the field ranked it first): `prompt-ids-resolve` scans the project's own prompt files for
phantom ids with the row rule's doctrine, never a stock body. **`FB-003`, a census**:
`entity_query(search=…, context=N)` reports `occurrences` — counts and snippets per column. The
review page renders `readiness_check` for the first time, evaluated as of its export date, and
gains a Feedback section, the supersession tag on Approved lessons and the open-ended waiver
mark. The feedback teaching now says what the code does (a local tool has no draft stage; the
two-clause rule; the kinds by name), and one convention tightened on every guard: the operator's
word is the JSON boolean `true` and nothing else. An acceptance script of twelve checks passes on
this tree and fails, each for its own reason, on an extracted `v4.11.0` tree. Lab beat 19 took
three dispatches: the first two stopped, correctly, on crashes the suite could never see — the
header write keyed by a directory name that the recorded fixture and the field's package both
differ from, and the page joining waived records as strings — each fixed and pinned before the
next run; the third fired every mechanism and all five refusals against the recorded package. No migration; no new tool (19); one stock
prompt body (`README.md`).

### Added

- **`entity_query(search=…, context=N)` is a census (ACMP's `FB-003`, plan 092).** The result
  carries `occurrences: {id: {column: {count, snippets}}}` — exact counts on the raw needle with
  `LIKE`'s ASCII case folding, snippets of N characters either side (capped at 5 per column, 50 per
  response; counts never capped). Absent without `context`; `matched` unchanged.
- **`prompt-ids-resolve` (ACMP's `FB-002`, ranked first; plan 093).** A new advisory scans the
  PROJECT's prompt files — every `<package>/prompts/*.md` that is not a stock body (current or any
  older release's) — for identifiers that resolve to no entity, with the same three lists, caps and
  doctrine as the row rule (backticks make a quotation inert; the list is a floor); entities read
  `prompts/<file>:<line> -> <id>`; `population` counts files (`unit: "files"`); zero project files
  reads `indeterminate`. In a prose file a code span may wrap a line, and the scan honours that.
  Measured: the stock prompts hold no bare phantom, so no package is amber by construction.
- **The package header is written on the operator's word (ACMP's `FB-001`, plan 094).**
  `entity_upsert(type="package")` writes the one header row of the open package — `title`, `mode`,
  `iteration`, `mvp_definition`, `entry_point`, `go_no_go` — special-cased, never a family (no
  register, no CSV, no registry row). Identity columns are frozen and refused by name. `go_no_go`,
  the governance verdict, changes only with `operator_confirm`, journaled by the engine
  (`system:package-guard`, returned as `package_audit`). The read stays `server_info().package`.
  Lab beat 19 caught the first draft keying the row by the package's DIRECTORY name — a stored
  name may differ (the lab fixture, the field's package) and every header write crashed there;
  fixed before release: the header is the one row, and a refusal is a verdict, never a crash.
  Its security review tightened one convention for every guard: **the operator's word is the JSON
  boolean `true` and nothing else** — a truthy string like `"false"` no longer attests on a lesson,
  a feedback row or the header.
- **The `substitute` write (ACMP's `FB-004`, plan 095).** `{"type", "id", "substitute":
  {"<column>": ["<old>", "<new>"]}}` changes one token in one column without the whole row passing
  through the agent's output: the server materializes the stored row, replaces the exact text, and
  sends the result down the ordinary full-row path — every guard, trigger, `expect_unchanged` and
  `changed_columns` judge it as they would a caller's row; the item reports `substituted` counts.
  Refused by name: a mixed item, the journal, composite-key rows, `id`, a non-TEXT column, zero
  occurrences, a JSON column that would stop parsing, and — the security review's finding — a match
  glued to a digit (`DEC-20` inside `DEC-208`). Recorded twice before as "not built"; the field
  ranked it second and showed it had changed a decision (a 24,117-character re-send deferred a repair).
- **The review page follows plans 069–095 (plan 096; maintainer ruling 2026-09-22).** `review.html`
  gains a **Feedback** section (awaiting the operator's word / confirmed, not yet reported /
  registered local tools / closed) and a **Readiness** section rendering `readiness_check`'s
  package-scope rules — status, severity, population, discriminating, omitted, waived — under an
  *Evaluated as of <date>* line, so the two calendar-reading rules move the page only when the
  calendar does. The Approved-lessons fold shows the plan-075 supersession tag; the waivers fold
  marks an open-ended whole-rule waiver. Every package's page changes bytes once on its next export.
  Lab beat 19 caught the first draft joining `waived` entries as strings (they are `{entity,
  waiver}` records), a crash on any package where a waived rule fires; fixed before release.
- **Docs sweep (plan 097).** Every behavior of this batch is documented outside its plan record:
  the server README rows, quality-gates (nineteen package-scope advisories), governance (a new
  "package header" section), `docs/architecture.md`, `docs/entities.md`, SECURITY.md.

### Fixed

- **The feedback teaching says what the code does (findings_28 §3a–§3c, `FB-013`; plan 091).** A
  `local-tool` row has no draft stage — the operator's word is a precondition of its insert (the
  `005_feedback.sql` header, frozen as shipped, overstates a Proposed stage). The four draftable
  kinds are named (`missing-capability`, `defect`, `doc-error`, `question`). The local-tool rule has
  two clauses — *writes nothing tool-owned; if it reads the STORE, it reads `exports/` only* — so a
  generator of project-owned files inside the package directory satisfies it. Feedback leaves a
  repo as the export's envelope and rows QUOTED in the findings (`exports/` may be untracked);
  `handoff_emit`'s warning says so. `work_bind`'s doc: bind a sha that is on origin.

## [4.11.0] - 2026-09-22

**MINOR — the findings_27 batch: the feedback channel on the operator's word, the journal that
covers the lesson lifecycle in both directions, and a prose-id scan that sees an underscore
(plans 085–089; field report findings_27 plus the maintainer's audit of the field's guidance and
tooling).** ACMP's upgrade to 4.10.0 came back with four findings, every one verified in source:
the id pattern could not see an underscore, so a formula's variable names read as five dropped
zeros; width was tested before the code span, so the two informational lists were not what their
names said; those lists were cut at 50 silently; and a lesson retired by hand — the very path the
new advisory recommends — was journaled by nobody, six times over on the field's package.
Alongside, the maintainer's audit found the field's guidance still carrying live instructions to
read the JSONL store and to delete the lock by hand, and four slate generators plus a folder of
scratch probes built because tamheed lacked four functions and nothing told upstream. **The
feedback family (migration `005_feedback.sql`)**: a function the tools lack, a defect, a doc
error, a question — or a local tool the project keeps — is an `FB-` row. It is born `Proposed`
and binds nothing; it becomes `Confirmed` only on `operator_confirm` + `confirmed_by`, journaled
by the engine; a `local-tool` kind arriving on any row needs the word and lands the row
Confirmed; while a row is Confirmed/Reported/Resolved its content changes only with the word,
and leaving that set is journaled. `handoff_emit` names the rows still awaiting the operator and
the confirmed rows not yet exported; `entity_export("feedback")` inside the project's findings is
how it reaches the maintainer. Two reviewers bypassed the first guard four ways before commit;
all closed. **The journal**: a by-hand lesson retirement is written by `system:lesson-guard`,
and — the security reviewer's finding — the engine's actor namespace is now its own: a caller
cannot write `system:<component>` on either journal path, so an audit row that says
`operator_confirm attested` was written by the server or not at all. **The scan**: `_` is a word
character; every cut list says so; the notes state the classification order and name `scoped` as
the tell between the two ambers. An acceptance script of fifteen checks passes on this tree and
fails, each for its own reason, on an extracted `v4.10.0` tree; lab beat 18 fired the mechanisms a lab can reach
against the recorded package (the cut-list clause and the feedback withdrawal are unit-tested,
not fired: a fixture this small cannot hold fifty phantoms, and the beat never withdraws). No new tool (19); one additive migration; two stock prompt bodies.

### Added

- **The `feedback` family — upstream feedback and local tools on the operator's word (plan 087,
  migration `005_feedback.sql`; maintainer rulings 2026-09-22).** The field had built four slate
  generators over `exports/`, a JSONL-reading id resolver and a folder of scratch probes because
  tamheed lacked four functions and nothing told upstream. A function the tools lack, a defect, a
  doc error, a question — or a local tool the project keeps over the package — is now an `FB-` row:
  `kind`, `detail`, `workaround` (what the agent did instead — the column that catches side tools),
  `tool_path`, `plugin_version`. A row is born `Proposed` (the agent's draft; it binds nothing and
  leaves the package nowhere) and becomes `Confirmed` only with `operator_confirm` + `confirmed_by`,
  journaled by the engine (`system:feedback-guard`); a `local-tool` row is refused at INSERT without
  the word and is born `Confirmed`; withdrawing a Confirmed row needs the word too. `handoff_emit`
  names the rows still awaiting the operator and the confirmed rows not yet exported —
  `entity_export("feedback.json", args={"type": "feedback"})` is how feedback reaches the maintainer,
  inside the project's findings; no row text reaches an emitted file. The family is `Continuous`
  (never a G-SET failure) and exempt from `prose-ids-resolve` (feedback quotes broken ids by nature).
  No new tool. A field package opens as is (migrations apply before the load) and gains the registry
  row through `package_migrate`'s registry-sync, a pure append. Taught by the always-loaded note's
  obligations table, SKILL.md, `references/state.md` (a hand-edit at rest is validated, not
  sanctioned), and the `README.md` and `orient-resume.md` stock prompts.

### Fixed

- **The id pattern treats `_` as a word character (findings_27 §2, plan 085).** `KPI-17_score` inside
  a formula yielded a `not_well_formed` hit on `KPI-17`; every such entry on the field's package was
  that one false positive. A token touching an underscore on either side is part of a longer
  identifier, as `-<digit>` already meant someone else's numbering. Measured on the field's nine
  exported families: four underscore-joined labels stop being scanned, no citation does.
- **Every cut list says so (findings_27 §3, plan 085).** `in_code_spans` and `not_well_formed` were
  capped at 50 silently; the "showing 50 of N" clause now covers all three lists. The note states the
  classification order (the lists are disjoint; width is tested first, so a narrow token inside a code
  span appears only under `not_well_formed`), and the whole-table `indeterminate` note names
  `scoped: false` as the tell between it and plan 049's scoped zero (findings_27 §1).
- **A by-hand lesson retirement is journaled by the engine (findings_27 §4, plan 086).** The store
  guarded the exit from a binding status on the way in and recorded nobody on the way out: the field's
  package held six retirements with no journal row. When an Approved/Promoted lesson moves off a
  binding status on the operator's word, the engine now writes one `transition` row by
  `system:lesson-guard` (naming the stored approver and any `superseded_by`) and returns it as
  `lesson_audit`; the automatic path keeps `system:lesson-supersession`, so the two routes stay
  distinguishable. A refused write journals nothing.
- **The engine's actor namespace is its own (security review of plan 086; maintainer ruling
  2026-09-22).** Any caller could forge an engine audit row — `actor: "system:lesson-guard"`, an
  entry claiming `operator_confirm attested` — through `progress_update` or a `progress-entry`
  upsert, without touching the guarded write; the upsert path did not even refuse the server-only
  event types. Both caller paths now refuse an actor starting with `system:` and the server-only
  events alike; a caller records as `human:<name>` or `agent:<session>`. Measured before the ruling:
  no eval, prompt, doc or field practice wrote a `system:` actor as a caller.
- **`confirmed_at` lands on a re-sent feedback row (lab beat 18, plan 089).** The stamp used
  `setdefault`, a no-op when the full row re-sent for confirmation carries the key as null - the
  ordinary path. Stamped whenever empty now.
- **Docs and diagrams sweep (plan 088).** Every behavior of this batch is documented outside its
  plan record: the server README rows, quality-gates, governance (a new "Feedback and local tools"
  section), extension.md (`005_feedback.sql` as the worked example), SECURITY.md, the root README,
  a feedback data-flow diagram in `docs/architecture.md` and the feedback lifecycle diagram in
  `docs/entities.md`.

## [4.10.0] - 2026-09-21

**MINOR — the findings_26 batch: a supersession that completes itself, rules that never pass
over nothing, writes that say what they changed (plans 075–083; field report findings_26 plus
three plans held for it).** ACMP's upgrade to 4.9.0 came back with a lesson that kept binding
every session after it had been "superseded". The batch plan's first answer — filter the note —
was wrong, and a devil's-advocate review said so before any code: the sanctioned exit
(`Approved → Superseded`) already worked; the field had set only the `superseded_by` pointer,
the engine had accepted that half-finished state silently, and no document said the STATUS must
change. **Lessons**: status stays the single truth for what binds. When the operator approves a
lesson, the engine retires every binding lesson that points at it, in the same write, journaled
and named in the result; the half-state gets a truthful hint, a tag in the always-loaded note
and an advisory. And a hole nobody had reported is closed: binding a lesson needed the
operator's word, unbinding one needed nothing. Now any move off a binding status, and any change
to the pointer, is refused without `operator_confirm` — two reviewers found the two unattended
routes (`Proposed`; a pre-set pointer) before commit. **Readiness**: by maintainer ruling no
query-built rule passes over zero rows — it reads `indeterminate` — except where the family's
omission is recorded, a deliberate zero that reads `pass` and says so; measured first at 17 of
21 rules on a fresh package, and `ready` never moves. `prose-ids-resolve` reports what it
skipped (`in_code_spans`) and what is not an id at all (`not_well_formed`) instead of going
quiet; `waivers-open-ended` names blanket waivers with no expiry. **Writes and pages**: an
update reports `changed_columns` with before/after text lengths, so a re-sent field that lost a
paragraph is a number on the screen; `export_html` stamps the digest of the state it rendered
and `package_verify` reports `review_current`. **Prompts**: a hand-merged customised prompt can
declare its merge (`<!-- tamheed:stock-merged X.Y.Z -->`), reported as a claim, and stops
lagging — the containment heuristic first designed was measured to fail on the field's own
merged file. Dropped as speculative after review: `if_match` and row hashes (the store has a
single-writer lock; there is no concurrent writer to be stale against). An acceptance script of
twenty checks passes on this tree and fails, each for its own reason, on an extracted `v4.9.0`
tree. Lab beat 17 fired the mechanisms against the recorded package, and every assertion it
added was shown to fail against the pre-beat fixture. No schema migration, no new event type,
19 tools.

### Added

- A lesson supersession completes itself (findings_26 §3, plan 075): when the operator approves
  or promotes a lesson, every binding lesson whose `superseded_by` names it becomes `Superseded`
  in the same write, with one `transition` journal row each and the ids returned as `superseded`.
  STATUS stays the single truth for what binds — the always-loaded note and
  `entity_query("lesson", status="Approved")` both read it; the field's lesson kept binding
  because only the pointer had been set, and nothing said so. New advisory
  `lessons-superseded-binding`; the note tags a still-binding row that points at a successor.

- A completed hand-merge of a customised prompt is visible (findings_26, plan 078): each
  `diverged_customized` entry reports `stock_merged` — `"declared X.Y.Z"` when the file carries
  `<!-- tamheed:stock-merged X.Y.Z -->`, the operator's claim, reported as a claim — and
  `contains_current_stock`. A file leaves the lag warning when either holds. Containment alone
  was measured to fail on the field's own merged file, whose customisation rewrites stock lines.
- A stale review page is detectable (plan 081): `export_html` stamps the package digest into
  `review.html`, and `package_verify` reports `review_current` — `true` / `false`, or `null`
  for a page with no stamp. The field's rule was "git clean ≠ package artifacts current", and a
  stale page once sat on origin unnoticed. Every tracked `review.html` changes by one line on
  its next export; two exports of one state stay byte-identical.
- A write says what it changed (plan 080): an UPDATE's per-item result carries
  `changed_columns`, each with `old_len` / `new_len` for text. Upserts replace whole rows, and
  the field once re-sent a 4,296-character field missing a paragraph and got `ok` back with
  nothing to reveal it; a length drop on the screen does. An insert carries no list, an
  identical re-send `[]`. JSON columns compare as parsed values, as `expect_unchanged` does.
- `waivers-open-ended`, a package advisory (lab beat 16's observation, plan 079): whole-rule
  waivers with no expiry, which keep waiving rows written long after the operator approved
  them. Emitted only when the package has waivers at all — "no waivers" is the healthy state,
  not a question. `register-liveness.md` teaches it.
- `prose-ids-resolve` says what it skipped (findings_26 §1–§2, plan 076). Two informational
  lists join the entity list: `in_code_spans` (a phantom cited only inside a code span — still
  not a failure, but now visible, so backticks cannot silence a broken citation and a clean
  result says which kind of clean it is) and `not_well_formed` (a token narrower than any id its
  family holds, like `SEC-8` against `SEC-001`… — reported, never dropped, because `DEF-82`
  typed for `DEF-082` lands there too). A token followed by `-<digit>` is not an id
  (`ADR-2026-001`). The note says the entity list is a floor, not a census.

### Changed

- **No readiness rule passes over nothing (maintainer ruling 2026-09-21, plan 077).** A
  query-built rule whose family holds zero rows reads `indeterminate` /
  `discriminating: false` instead of a silent `pass` — the field found two package rules and
  one slice rule passing over nothing, with `population` the only tell. Measured first: 17 of
  21 rules on a fresh package. The one deliberate zero is a RECORDED omission: the rule then
  reads `pass` and carries `omitted`, so a legitimately empty family never stays amber.
  `indeterminate` never blocks; `ready` does not move.
- **Contract tightening (maintainer ruling 2026-09-21):** what binds every session on the
  operator's word stops binding on it too. On an Approved or Promoted lesson, ANY move off a
  binding status, and any change to `superseded_by`, is refused without
  `"operator_confirm": true`. A Proposed lesson binds nothing and is still rejected freely; an
  upsert that omits those columns is never refused (plan 075).
- **Docs and diagrams sweep (plan 082).** Every behavior of this batch is documented outside
  its plan record: the server README rows, quality-gates, governance, handoff, SKILL,
  SECURITY, the prompt guide (the `stock-merged` marker), and a new lesson-lifecycle state
  diagram in `docs/entities.md` with the automatic supersession edge. Corrected: the advisory
  count (eighteen at package scope, not sixteen), and 4.9.0's description of `search` as an
  "exact substring" — it is SQLite's default `LIKE`, case-insensitive for ASCII.
- **The lab fixture follows the release stamp (finding F-1, plan 084).** A beat refreshes the
  fixture's prompt guide before the release moves that file's version line and re-sets its
  history key, which left the fixture holding a body NO key records — classified `customised`,
  so `refresh_stock` would never touch it again. Lab-only (a field package refreshes after a
  release). The release recipe now re-emits the fixture's guide by tool after the stamp,
  refusing unless it is the only diverged file and differs by the version line alone.

## [4.9.0] - 2026-09-21

**MINOR — the findings_25 batch: the observed lock, the legible reads, the honest denominators
(plans 063–073; field report findings_25 + the field's lessons register).** ACMP's upgrade to
4.8.1 came back clean with three narrow findings, and its lessons register held rules that are
true of any package. Twelve plans followed, executed directly by the reviewer under the
maintainer's delegation after a devil's-advocate review of the batch plan; the three that touch
the lock or delete files (063, 064, 065) went through a security and a Python reviewer before
commit. **The
lock**: every refusal now reports what the store OBSERVED about the holder — `not-running`,
`reused`, `alive`, `unobservable` — decided by the process start identity the lock records,
never by a bare pid check; the read-only migrate preview no longer needs the lock; and
`package_unlock` is the one sanctioned, journaled way to remove a dead holder's lock, on the
operator's word, refusing anything it could not see (19 tools). A probe taken before the design
found that on Windows an exited process still opens while anyone holds a handle to it — the
naive check would have called a dead holder alive. **The reads**: `server_info` carries the
stored package row and, on request, the vocabulary; a projection names what it omitted and a
search names where it matched; an export file says when it is short; `package_verify(expect=)`
turns "is this slate current" into a boolean. **The denominators**: every readiness rule reports
the population it measured, `lessons-confirmed` no longer passes hollow, and `prose-ids-resolve`
names identifiers written in prose that resolve to nothing — measured before it was built, it
found both phantoms the field had found by hand, at about one false hit per thousand rows.
`export_html` leaves no orphan in `csv/`. Five stock prompts adopt the field's portable rules
and drop two stale teachings, one of which — that a query round-trip truncates fields — had
cost a field repo three weeks. `docs/workflow.md`'s sequence diagram was wrong about when data
reaches disk and is corrected; `docs/architecture.md` gains the lock's state diagram. An
acceptance script of twenty checks passes on this tree and fails, each for its own reason, on
the pre-batch tree. Lab beat 16 fired the mechanisms against the recorded package. No schema
migration.

### Added

- The store OBSERVES a lock's holder and reports it (findings_25 s1, plan 063): every
  lock refusal ends `observed: not-running | reused | alive | unobservable` with the
  evidence. The lock records the writer's process start time, so a recycled pid is decided
  by identity, not by a bare liveness check; another host, a legacy lock or a process that
  cannot be inspected is `unobservable`, never assumed dead. Stdlib only; the server
  spawns nothing and signals nothing.
- `package_unlock(name, confirm=false)` - the sanctioned route out of a dead holder's lock
  (findings_25 s1, plan 064; 19 tools). The default call reports the lock and the
  observation. `confirm=true` is operator-words-only, like `force`: it proceeds only when
  the holder was observed `not-running` or `reused`, refuses on `alive` and `unobservable`,
  proves the store loads first, removes only the exact lock it judged, and appends one
  `forced-override` journal row. Lock refusals name the tool. The doctrine moves from "the
  store never removes a lock" to "it observes, reports, and removes one only on the
  operator's word, journaled".
- `server_info()` carries `package`, the stored package row (name, version, iteration,
  go/no-go ...), which no tool could read before; `server_info(detail=true)` adds
  `entity_types` (type, table, id prefix) and `relation_rules` (allowed endpoint types), so
  neither has to be learned from a refusal (findings_25 s3, plan 066).
- An export FILE says whether it is short: the `tamheed_export` envelope carries `count`,
  `total` and `partial` for row results (it was on the tool's return only, so every reader
  re-derived it); still deterministic. `package_verify(expect=<digest>)` returns
  `matches_expected`, so "is this slate still current" is a boolean, not two hex strings
  compared by eye - a mismatch means stale, not damaged (plan 067).
- Reads announce what they hid (plan 068): `entity_query` with `columns` returns
  `omitted_columns`, and with `search` returns `matched` (which TEXT column matched, per
  row - `search` is an exact substring over every TEXT column incl. `custom_attributes`, so
  a hit in an unprojected column used to read as a fuzzy match). A lesson landing
  `Approved`/`Promoted` carries a `next` hint: the always-loaded note is rebuilt only by
  `handoff_emit`. Top-level keys only; row dicts are unchanged.
- Every readiness rule built from a query reports the `population` it measured (family,
  rows, and whether the count is scoped to the phase/slice) - a verdict without its
  denominator cannot be told from a rule that had no subject (plan 069).
- `prose-ids-resolve`, a package-scope advisory (plan 070): identifiers written in PROSE
  that resolve to no entity. `G-IDS` checks foreign keys and the index, never a sentence -
  the field carried a phantom `DEF-082` cited by three rows for weeks. Measured before it
  was built: it found both phantoms the field had documented by hand, at about one false
  hit per 1,000 rows. Code spans, JSON keys, Superseded/Obsolete rows and the append-only
  journal are not scanned. `register-liveness.md` teaches it (step 16).

### Fixed

- `export_html` leaves no orphan in `csv/` (findings_25 s2, plan 065): a CSV for a table
  that became empty, or that a migration retired (the field carried `csv/prompts.csv` for
  two months), is removed and reported under `csv.removed`. Only a regular file in the
  PACKAGE's own `csv/` whose header proves the exporter wrote it is removed; anything else -
  an operator's file, any file in a caller-chosen `output` directory, a symlink - is
  reported under `csv.unowned` and never touched. `package_verify` gains `foreign_csv`.
- A flaky assertion in `test_note_pointer_pattern_recognized`: it refused the substring `v1`
  anywhere in a warning that prints full paths, so a random temp directory named
  `tmpv174recz` failed one CI leg on a docs-only commit. It now refuses the v1 warning's own
  wording (`v1-era`), which a temp name cannot contain.

### Changed

- Docs and diagrams follow the batch (plan 072): `docs/workflow.md`'s sequence diagram no
  longer draws canonical JSONL being written back at `package_close` (every write flushes;
  close releases the lock); `docs/architecture.md` gains section 8 and a state diagram for
  the observed single-writer lock; the server README lists 19 tools; SECURITY.md states the
  new process-metadata capability, the exporter's deletion rule and the operator-only unlock;
  the install guide's Upgrading section gains the dead-holder branch and "reload or restart".
- Stock prompts adopt portable field rules and drop two stale teachings (plan 071):
  `prompts/README.md` teaches the lock observation and `package_unlock` instead of a
  hand-deleted lock, gains **Asking the operator** (homework first, one decision per
  question, show the record with its id, ask every time), and no longer says to repair from
  `data/*.jsonl` because a query round-trip "truncates" - no field is ever truncated, and
  that claim cost a field repo three weeks on the JSONL. `integrity-check.md` says what a
  green run does not prove (every gate is row-level; read `population`);
  `replan-deferred.md` asks which words of a trigger fired; `orient-resume.md` teaches
  "search finds candidates, an exact read decides". Needle-pinned; `4.9.0` history keys.
- `lessons-confirmed` reads `indeterminate` (never a hollow pass) on a package that holds no
  lesson at all: a session that learned nothing and one that recorded nothing looked the
  same. Advisory, so `ready` is unchanged (plan 069).
- `package_migrate`'s read-only preview no longer takes the writer lock: it diagnoses
  before it refuses, and says when it read under a held lock; `confirm=true` still needs
  the lock (findings_25 s1, plan 063).
- `docs/install.md` gains an **Upgrading** section: the marketplace refresh does not update the
  installed plugin (`claude plugin update tamheed@tamheed` + restart does), and the sequence
  around an upgrade in a repo that carries a package — close the lock holder, baseline, preview,
  `handoff_emit(refresh_stock=true)`, the one-time churn to expect in tracked derived files
  (written while preparing the ACMP 4.7.0 → 4.8.1 upgrade, 2026-09-20).

## [4.8.1] - 2026-09-12

**PATCH — the post-release review: the specific waiver, CI on push, the docs sweep (plans
060–061).** A devil's-advocate review of the v4.8.0 loose ends, executed directly by the
reviewer under the maintainer's delegation. One engine fix: a whole-rule waiver no longer
shadows a per-entity one in the readiness citation (060; verdicts unchanged; test written RED
first). The CI mystery closed: the two workflow objects registered at the repository's first
push never delivered `push`, `schedule` or `pull_request` events — probes on a throwaway branch
fired within seconds — and renaming the files re-registered them; the first push-triggered run
in the repository's history followed 5 s later, and a throwaway PR fired CI in 7 s. The
"account-side setting" wording in 4.8.0 was unsupported and is corrected here. A documentation
sweep closed seven surfaces that had stayed silent on behavior the advisor batch shipped (061).
No schema change; the lab fixture is byte-identical on re-export.

### Fixed

- `readiness_check` cites the **most specific** waiver: when a per-entity `WVR-` row and a
  whole-rule `WVR-` row both cover a rule, each waived entity now cites its own waiver and
  the whole-rule one is the fallback (previously the whole-rule waiver shadowed every
  citation — verdict unaffected, audit trail less specific; lab beat 15's observation,
  plan 060).
- CI fires on push again: the two workflow objects registered at the repository's first
  push never delivered `push` or `schedule` events (4.8.0's "account-side setting" was an
  overstatement — every setting was normal; probes on a throwaway branch fired within
  seconds). Renaming the files to `ci.yaml` / `eval.yaml` re-registered them; the first
  push-triggered run followed 5 s later (post-release review, 2026-09-12).

### Changed

- Documentation sweep for the advisor batch (plan 061): SECURITY.md records the CSV
  formula-injection guard (050); `handoff.md` the note's skill screen and marker defusing
  (054); `quality-gates.md` scoped readiness at zero rows (049); CONTRIBUTING, the README
  tree and `tests/README.md` the ninth suite (056) and the CI matrix (052); the server README
  the viewer's numeric id order (057) and the waiver citation rule (060).

## [4.8.0] - 2026-09-12

**MINOR — the advisor audit: sixteen plans, the lab beat, the first CI runs (plans
042–059; `/improve deep`, 2026-09-10).** An external advisor audit of v4.7.0 — eight
read-only sweeps, every finding re-read or reproduced before it was planned — produced
sixteen self-contained plans, each executed by an isolated executor, reviewed against its
own done criteria, and integrated on one branch before merge. Two findings were
silent-corruption class: `entity_upsert` released its savepoint before the stale-tree
check, so a refused write stayed applied in memory (043); and `package_migrate` deleted
`data/` before it copied, on the registry-sync path that has no backup (045). One is a
tool-contract change: a phase or slice can no longer be created already `Implemented`
without `force` (053). The rest are hygiene the engine's own doctrine already implied
(name validation on every tool, the marker scan's history filter, hollow scoped readiness,
CSV defusing, the note's skill screen, numeric id order). CI, which had never run on this
repository, ran for the first time on 2026-09-11 (manual dispatch; push events still do
not fire — an account-side setting) and is green on eight legs plus the smoke job. Lab
beat 15 exercised the mechanisms a lab can reach and pinned them with nine assertions.
No schema migration.

### Fixed

- The review surface orders ids by (prefix, number) instead of as strings (`PH-10` sorted
  before `PH-2`, `PE-1000` before `PE-999`), and the prompt library's stale-stock
  classification compares release versions numerically (advisor plan 057).
- `entity_upsert` released its `batch` savepoint before the stale-tree check, so a refused
  write (data/ moved underneath the session) stayed applied in memory and answered every
  later read in that session; the refusal now rolls the batch back as its message always
  claimed (advisor plan 043).
- G-COMPLETE's `[NEEDS-CLARIFICATION]` marker scan now skips `Superseded`/`Obsolete` rows,
  matching the placeholder scan (plan 038): a stale marker on an immutable, superseded row
  was a permanent blocking failure whose only named remedy — edit the row — the store
  forbids (advisor plan 046).
- Phase/slice readiness: `acs-met`, `wbs-done` and `slices-closed` now report
  `indeterminate` (discriminating: false) when the scope holds no candidate rows, instead
  of a silent pass — the C35/N3 hollow-pass doctrine applied to the rules that carry the
  transition; `ready` and the transition guard are unchanged (indeterminate never blocks)
  (advisor plan 049).
- `export_html`'s per-table CSVs prefix cells beginning with `=`, `+`, `-`, `@`, tab or CR
  with a quote so a spreadsheet never evaluates stored text as a formula (CWE-1236); the
  lab-tracker fixture's `csv/` goldens were regenerated by the tool (advisor plan 050).
- `entity_upsert` on an `omission` whose `reason` changed now updates the row; it used to
  `INSERT OR IGNORE` and report `ok: true, unchanged: true` with the old reason left on disk.
  `scripts/scratch_diff.py` keys omissions by `entity_type` (the table's primary key), so a
  reason change diffs as a change (advisor plan 051).
- Package names are validated on `package_open`, `package_verify` and `package_migrate`,
  not only on `package_create` — SECURITY.md's traversal claim is now true of every tool
  that resolves a name; `export_html(output=…)` refuses to overwrite a file it did not emit
  and requires a `.html` path (advisor plan 044).
- `package_migrate(confirm=true)` is fail-safe: inputs are parsed before anything is
  written, new files land beside the old ones and are swapped in last (the registry-sync
  path had no backup and deleted before it copied), and any failure restores `data/` from
  `data-v3-backup/` and removes it so the retry is not refused; a corrupt
  `data/packages.jsonl` is an error naming the file, not a traceback (advisor plan 045).
- The CLAUDE.md note's "Skills distilled from lessons" line is screened by `_INJECT_RE`
  like the lessons are, and HTML-comment delimiters inside rendered lesson/skill text are
  defused so a marker literal can no longer truncate the tool-owned span (advisor plan 054).

### Changed

- `--selftest` now registers the whole tool surface with FastMCP when the SDK is present
  and exits 1 if any tool fails to register — the one step no check exercised (C33's
  class); SDK-free runs stay informational (advisor plan 047).
- `entity_upsert` refuses a phase or slice created directly as `Implemented` — the
  transition guard ran readiness for an id with nothing bound and passed vacuously;
  `"force": true` (operator-confirmed, journaled as `forced-override`) remains the route
  for done-on-arrival rows (advisor plan 053; maintainer decision 2026-09-10).
- Docs: removed the `--dry-run` flag from every surface that described it (never implemented;
  decided 2026-09-10 to drop rather than build); README's migrate example now shows the v4
  `package_migrate(name)` preview/confirm flow; `CLAUDE.md` no longer names `examples/` or
  `references/entity-guide.md`; stage 20 no longer claims a `handoff/` directory; the stock
  prompt count is 16; `SECURITY.md` names adopt's read-only `git log` and the bundled
  `scripts/scratch_diff.py` path; `adopt.md` no longer documents a `sources` parameter; the
  Keystone runbook says which steps run under tamheed 3.2.1 (advisor plan 048).
- CI: the MCP server smoke job installs `uv` with `astral-sh/setup-uv` and fails on a failed
  `--selftest` (it used to skip); Python 3.13 joins the matrix. Docs and the server's error
  text now say `pip install "mcp<2"` — the unbounded fallback reproduced the C33 incident the
  PEP 723 pin prevents (advisor plan 052).
- Adopt/record hygiene: the registry import is no longer wrapped in a silent fallback,
  the v1 migration ledgers nothing populated are gone, adopt derives its Always roster from
  the registry instead of a hand copy, files over 2 MB are skipped and listed under
  `scan.skipped_large`, and a failed post-flight now carries an `error` (advisor plan 055).
- Tests: whole-rule waivers, `decisions-approved` and `decisions-look-architectural` are
  covered; `check.py`'s lints run under their own suite against a repo copy (pass, version
  mismatch, dead path, widened pin); `evals/pkg_check.py` releases the package lock on any
  exception, refuses a named table that has no file (exit 2), and gains
  `grep-tree-present/absent` for file trees — the `injection-brief` prompt assertion, which
  grepped the table retired in v3 and could never fail, now reads `prompts/` (advisor plan 056).

## [4.7.0] - 2026-09-07

**MINOR — the sanctioned read for committed scripts and the paste guard (plan 041,
findings_24/C45).** findings_24 reported one GAP and no defect: the tool-owned note says
all package reads go through the MCP tools, the field project made that unconditional,
and its four committed slate generators — the scripts that discharge its rule that
every record the operator decides against is quoted byte-exact from the store — then
had no sanctioned route to whole canonical rows. Both ways out were bad: the agent
hand-transports rows (their measured loss: a 4,296-character field dropped a paragraph
mid-paste with `ok: true`), or every consumer re-implements the JSON-RPC handshake and
the lock dance. The report also verified `entity_query` truncates nothing — correcting
a pinned lesson of its own — and that `retire` caught a mis-typed `amends` within an
hour of the rule that catches it being written. No schema migration.

### Added

- **`entity_export(path, tool?, args?)`** — 18 tools. Runs one read-only tool
  (`entity_query` by default; `trace_query`, `gate_run`, `readiness_check`,
  `package_verify` with `record` refused, `server_info` — an allow-list) and writes its
  WHOLE result to `<package>/exports/<path>` (absolute paths allowed; refused under
  `data/`, resolved first so no traversal escapes; an existing file is replaced only if
  it is itself a tamheed export — a caller-named path must never clobber a project
  file). The envelope stamps the `digest` of the OPEN connection's canonical form — the
  state the rows came from — beside `memory_matches_disk`; the file is deterministic
  (no timestamp: same state + same args = the same bytes, the `export_html` doctrine);
  the result carries metadata only (`count`, `total`, `partial`) so a short export is
  loud, and the docstring says what findings_22 made true: the file has no client
  payload cap — pass a `limit` above `total` to export a whole family. A committed
  script quotes from the file; "all reads go through the tools" stays literally true
  because the tool wrote it. The read-only CLI shape was offered and declined on the
  maintainer's words (it would have covered session-less consumers; recorded as a
  future option).
- **`expect_unchanged: [cols]`** on an `entity_upsert` item (the field's `LL-063`): a
  full-row write that only means to flip a status names the columns it did NOT mean to
  change, and the store refuses the item naming any that differ from the stored row —
  an omitted named column counts as changed; JSON columns compare as parsed values;
  id-keyed rows only, never the append-only journal. The immutability trigger's
  self-verifying property, opt-in, for the long-text registers that have no trigger.
  It proves the write alters nothing named, not that the caller saw the row correctly.

### Changed

- The note span's read rule now draws the line: `data/` is tool-owned; a committed
  script that must quote the store reads an `exports/` file the tool wrote — never
  `data/*.jsonl`, never a pasted display. Cheat-sheet lines for both additions.
- Teaching: server README (the row, two rules), SKILL.md, both READMEs (+ the mermaid
  tool node and the package layout in `generated-structure.md`: `exports/`),
  docs/architecture (the ASCII list, the three-actor sequence diagram, the read-side
  paragraph), CANONICAL.md, SECURITY.md (the export writes only a derived file; consumers
  escape what they render), governance + template (lint-11 needle `expect_unchanged`),
  state.md; five stock prompts with roster appends — `slice-review` (the verdict is taken
  against an export made immediately before the review; cite its digest),
  `progress-sync` and `register-liveness` (`expect_unchanged` on long-row flips),
  `package-onboarding`, and the prompts README (the export rule, the guard, and
  `LL-063`'s producer-source rule: before recording a premise as untestable, list the
  instruments — the source that produces an output is one).
- Lab beat 14 (a real agent): the export, a committed stdlib generator in the lab
  workspace with a calibrated verifier, the partial/whole-family pair, both refusals,
  the guard refusing a one-word drift on a defect title; four new lab assertions.
- `package_verify` shares `_canonical_digest` and `_dump_open_connection` with the new
  tool (refactor, no behaviour change).

### Not changed, stated

- A generator run with no agent session (CI, a cron) still has no route; the CLI shape
  would cover it and waits for the first field need.

## [4.6.0] - 2026-09-06

**MINOR — the edge retire, the honest audit split, and the relocate wording (plan
040, findings_23/C44).** findings_23 came out of USING 4.5.0 for the close-out and
verified every findings_22 section closed by observation ("four for four, and the
two fixes I cared most about landed better than I asked"). It also found one gap
the new `amends` relation created by arriving alone, one honesty counter pointed
at the wrong population, and one approval string naming the weaker of two safety
nets. Nothing here is a regression. No schema migration.

### Added

- **Edge retire** (§1): trace edges are keyed `(from_id, to_id, relation)`, so
  writing `amends` beside an old `relates_to` never replaced it — and the server
  exposed no way to remove an edge while the G-REL note, the adopt note, **and the
  maintainer's own 4.5.0 upgrade note** told callers to "delete + re-add"
  (findings_21 §1's shape: a remedy the server cannot perform). `entity_upsert` now
  takes `{"type": "trace-edge", "from_id", "to_id", "relation", "retire": true}` —
  exactly those keys: the triple is DELETED (the relation rule is not consulted — a
  mistyped edge is exactly what gets retired), the server appends a `correction`
  journal row naming it (actor `system:edge-retire`) in the same transaction, an
  absent triple is an error (an attempt is not a write), and the batch stays
  all-or-nothing. Retype in ONE batch: the retire item plus the corrected edge. The
  first agent-initiated removal of store content — on the maintainer's words: a hard
  delete (the `retired_in` tombstone was declined — a migration plus a filter in
  every edge consumer), no operator gate (the journal row, the per-item report, and
  the gates' re-evaluation are the controls), and the doctrine line: retire a WRONG
  edge only, never to make a gate pass. Both notes now name the real operation.
- **`audit_evidence.ungraded` + `ungraded_ids`** (§2): the counter now reads each
  ACTIVE AC's LATEST verdict — the `acs-met` population — in three buckets:
  `evidenced`, `narrated` (a graded verdict with no evidence — the graded party
  grading itself, C7), `ungraded` (a Pending placeholder nobody graded). The old
  predicate ran over every verdict row ever appended, so it counted superseded
  history and untouched placeholders as self-grades and could only grow. `evidenced`
  changes meaning with it (the field package: 225 → 142). review.html prints all
  three and labels a Pending latest verdict `ungraded`; `pkg_check gates` prints the
  split.

### Changed

- **The relocate action text** (§3) states what the server verified (the
  byte-identical copy in `data-v3-backup/`) and what it did NOT (that directory's
  durability — operators commonly gitignore it; if `data/` is git-tracked the file
  also lives in history; check `git log -- data/<file>` before confirming). Premise
  corrected in the record: tamheed generates no `.gitignore` — the field
  repository's ignore rule and its comment are its own; the server never calls git.
- Teaching: the G-REL and adopt notes, the note span's cheat-sheet line, the
  governance/traceability/quality-gates/catalog references, the governance template
  (lint-11 needle `retire`), SECURITY.md's trust model (nothing leaves the store
  silently), both READMEs, SKILL.md, docs/entities + methodology, and four stock
  prompts: `integrity-check` (the three buckets by id; the retype remedy as a
  recommendation; a positive control chosen from OUTSIDE the swept set — the field
  register's `LL-053`), `progress-sync`, `register-liveness`, and the prompts README
  (the retire rule + the remedy-must-exist rule). Roster appends for all four.
- Doctrine (plans/README): a remedy named by a gate note, an advisory, a refusal
  text, or a release note must be an operation the server exposes; the lab beat
  performs every named remedy end to end.
- Lab beat 13 (a real agent): the residue written and retired, both refusals
  verbatim, the G-REL note read, the placeholder verdict counted `ungraded` (the
  bucket keys on the verdict, not on empty columns), the fixture re-recorded; three
  new lab assertions. Tests: the retire battery, the three-bucket split (superseded
  history and retired ACs excluded), the relocate strings, the export label, and
  the findings_19 §3 culprit text now pinned for a trace-edge item (the field had
  carried that verification unverified for four releases).

### Not changed, stated

- The field register's `LL-025` (a plan row faithfully quoting a clause a ruling
  superseded) was measured: zero live hits on the field package — every such edge
  belongs to a Merged scope change — and the lesson itself says nothing mechanical
  can see it. No advisory (a zero-hit rule is the hollow-pass class).

## [4.5.0] - 2026-09-06

**MINOR — the query surface with depth, `amends`, `package_verify`, and the note
budget (plan 039, findings_22/C43 + the ACMP lessons register).** An
operator-commissioned integrity audit — begun after the operator caught an agent
reading `data/*.jsonl` instead of using the tools — found one design gap that had
caused an incident (a query surface with no paging pushed agents onto the files,
and a false sentence about the cause then recruited every later session), two
smaller gaps, one migration leftover, and a strong positive: the byte-stability
guarantee held over all 29 files, 40 tables, 7,819 rows, and 488 commits of
history ("survived a deliberate attempt to falsify it"). Reading the field
register's 62 operator-confirmed lessons alongside the report turned six of them
into engine and doctrine changes.

### Added

- **`entity_query` gains depth** (findings_22 §1): `after_id` (keyset paging — the
  cut and the order share one byte collation, so a walk is complete over
  mixed-width ids; the result's `next_after` is the cursor, exact via a one-row
  look-ahead, null on the last page; `total` counts the filtered set and stays
  constant across the walk), `ids` (a known set in one call, in id order — the
  slate-generator shape the register's `LL-011` demands: full text of every cited
  record), and `search` (case-insensitive substring over the family's TEXT
  columns, `%`/`_` escaped — the keyword sweep `LL-008` requires, now possible
  under MCP-exclusive access). The docstring now says what its silence used to
  hide: `limit` cuts ROWS, never fields; there is no field truncation in the
  query path; a payload cap is the client's.
- **`amends`** — a new typed relation, scope-change → decision | adr (§2), via
  **migration `004_amends_verify.sql`** (the 002/003 recreation pattern). A scope
  change that carves an exception out of a ruling no longer collapses into
  `relates_to` (the field package carried three such edges). Merge semantics
  taught everywhere the delta lifecycle is: a `DEC-` target merges by full-row
  upsert, an `ADR-` target by supersession; `Merged` is the LAST step, after every
  target row is applied and re-read (`LL-042`: nothing mechanical checks the
  assertion `Merged` makes).
- **`package_verify(name?, record?)`** — the integrity instrument as a tool (§5):
  the canonical round-trip reported per file (`dirty`), foreign files in `data/`
  listed, an unloadable store reported as a finding (with file:line — `store.load`
  now locates bad JSON), memory-vs-disk compared when the package is open (a
  refused flush is exactly when a disk-only round-trip would lie), and a sha256
  `digest` over the canonical files. `record=true` appends ONE typed
  **`integrity-verified`** journal row (actor `system:package-verify`; only on a
  passing verification) naming the digest — a citable fact; the entry states that
  recording rewrites the journal file, so the next digest differs by construction.
  Read-only by default: no lock, nothing written. 17 tools.
- **`audit_evidence.narrated_ids`** (§3): the count told you a C7 problem existed
  and refused to say where — findings_21 §3's shape again; the ids are now named.
- **`lessons-note-budget`** package advisory: the field register renders 57
  lesson lines into the always-loaded note (48 pinned, 0 promoted). Pinning
  bypasses the cap by design, so its cost is made visible instead — past the
  curation ceiling (20 rendered lines) the rule names the rows rendering beyond it
  in the note's own order: a deterministic promotion-candidate list, pointing at
  `skill-promote.md` or unpinning. The note and the rule share one row helper.
- **Server-only journal events are refused from `progress_update`**
  (`forced-override`, `lesson-confirmed`, `lesson-promoted`, `integrity-verified`):
  the field data held five agent-written `lesson-confirmed` rows beside the 58
  server-appended ones — a vocabulary that never refused a server-only type let a
  narrated "confirmed" be journaled by hand. The refusal names the appending tool;
  existing rows are untouched (data is never rewritten).

### Changed

- **The `.jsonl.converted` leftover leaves the canonical directory** (§4): the v3
  prompt converter no longer renames its source into `data/` (the backup copy
  `package_migrate` takes moments earlier is the audit trail — `source_kept`), and
  `package_migrate` on a v4 store gains a third staged-sync reason: a foreign
  `*.jsonl.converted` in `data/` is previewed as `relocate` and, on confirm, moved
  into `data-v3-backup/` — or REMOVED when the backup already holds a byte-identical
  copy (the field package's exact case: the v4 migrate had copied every `data/`
  file there), or REFUSED naming both paths when they differ. The
  "registry current — nothing to migrate" refusal fires only when there is also
  nothing to relocate (the remedy would otherwise have been a no-op — the
  hollow-pass class). The v3→v4 confirm path removes a stale `.converted` in the
  same run (its backup copy is taken first) — one migration, never two.
- **The note's C31 sentence carries `LL-061`**: `work_bind`, the closing
  `progress_update`, `export_html` and `handoff_emit` all FLUSH `data/*.jsonl`
  AFTER the commit they record — `git status --porcelain -uall` immediately before
  any branch operation, never a memory of having committed. The cheat-sheet teaches
  the widened `entity_query` and `package_verify`; the SC obligation row teaches
  `amends` + re-read-then-Merged; the agent-control template mirrors all of it.
- Stock prompts (six, roster-appended under 4.5.0): `orient-resume` classifies
  unreferenced commits by `git show --name-only` — package-only writes are
  self-referentially unbindable (`LL-004`: the old wording invited 18 false alarms
  per window); `register-liveness` step 8 (Merged last, `amends`) + a new
  note-budget step; `defect-triage` — a ruling made while closing a defect is a
  `DEC-` row, never prose inside the Fixed row (`LL-040`), and closed rows are
  re-read on status flips; `integrity-check` opens with `package_verify`, reads
  `narrated_ids`, sweeps closed rows for buried rulings, and verifies repairs
  through `ids=` instead of the files; `package-onboarding`/`slice-kickoff` teach
  paging and `ids`; the prompts README's standing rules gain all of it.
- References/docs swept for the new relation, event, tool, and paging surface
  (governance, traceability, artifact catalog incl. the entity map, handoff, state,
  workflow, quality-gates, extension — migration 004 as the second worked example
  — CANONICAL.md's verify section, both READMEs, SKILL.md, docs/architecture,
  docs/entities, docs/methodology, the lab scenario's beat 12, the eval fixture).

### Fixed

- `store.load()` names the file and line of unparseable JSON (a bare decoder
  message located nothing).

### Deferred (recorded)

- Tamper-evidence proper (a row hash chain, signatures, an external anchor —
  findings_22 §5's second half) — a future option in plans/README; a clean
  `package_verify` is a citable fact, not durable evidence against a determined
  hand-edit-then-tool-call rewrite.

## [4.4.2] - 2026-08-20

**PATCH — the journal exemption + `corrects`' first consumer (plan 038,
findings_21/C42).** The sharpest field shape yet: a content gate over an
append-only journal had no repair path — the operator's note explaining which
tokens G-COMPLETE screens became the only row breaking it, permanently ("the note
about the rule became the only row breaking it"), and the suggested correction
path turned out to be inert ("a correction is a comment, not a correction" —
`corrects` was written and displayed but never read by anything).

### Fixed

- **G-COMPLETE's placeholder scan exempts the append-only report columns**
  (`progress_entries.entry`, `audit_verdicts.evidence`) — the C14 reasoning
  extended: a journal entry is a REPORT of what happened and cannot be
  "unfinished"; grading it fails the package for being accurate about its own
  tooling, and an append-only row that failed a content gate could never be
  repaired. Both twins covered (the evidence twin was identified but untested in
  the field — now test-pinned). Entity prose stays fully screened; G-INJECT is
  untouched.
- **The trap-class completed (the DA catch)**: the scan also skips
  Superseded/Obsolete rows — immutable-after-approval content (lessons, ADRs,
  approved ACs) was the trap's third instance, where supersession, the sanctioned
  repair, left the OLD row failing forever. Superseded content is history, not
  the plan. Live rows of every family stay fully screened.
- **`corrects` gains its first consumer** (findings_21 §2): review.html's
  execution timeline moves a corrected entry into a collapsed "Corrected entries
  (superseded)" fold annotated with its corrector — no longer an equal peer to
  the entry that replaced it. Correction chains compose per-row.
- **Every placeholder failure names the `matched` token** (findings_21 §3 — the
  first field incident's initial hypothesis was wrong because the output named
  WHERE but not WHAT), and the screen is now documented where an agent meets it:
  the `entity_upsert` docstring (with the backtick escape), the
  `progress_update`/`audit_record` docstrings (the exemption), the G-COMPLETE
  teaching row, and the prompts README standing rules.
- **Deferred, recorded**: a sanctioned redaction tool (`progress_redact`) — the
  only general fix for a secret pasted into the journal — waits for the first
  field need (the incident response needs git-history surgery the tool alone
  cannot do). Recorded in plans/README future options.

The ACMP package's permanently-red gate goes green on upgrade with ZERO data
changes — PE-469 is exempt, and PE-470's correction now visibly collapses it.

## [4.4.1] - 2026-08-16

**PATCH — the honest registry-sync report (plan 037, findings_20/C41).** One
finding: the sync's note ("only the entity-type registry changes — pure append")
was asserted per-mode while reality varies per-release — migration 003 added a
column to a populated table, `lessons.jsonl` re-serialized, and the operator's
git diff contradicted the banner, costing a hand-verification cycle.

### Fixed

- **The registry-sync report is computed per-run, never asserted per-mode**: the
  preview (and confirm) now carry **`columns_added`** — per-table columns present
  in the live DDL but absent from the stored rows (diffed mechanically; sound
  because canonical JSONL serializes every column, CANONICAL.md rule 4) — naming
  exactly which files will re-serialize and why, before the operator sees the git
  diff. The note is reworded: "registry rows + the audit journal row appended; no
  data transform, no backup taken" with the re-serialize clause present only when
  columns_added is (the old note was also silent about the `system:migrate` PE
  row modifying progress_entries.jsonl). The six teaching surfaces carrying "pure
  append" swept to match.
- findings_20 also field-verified two 4.4.0 fixes by reproduction (the §1 pointer
  pattern by re-running the original misfire; the §2 guard "more completely than
  I proposed") and honestly recorded §3 (FK naming) as field-unverified — the
  contract test remains its pin. The promotion ceremony was run and DECLINED
  (the prompt stopped at the cluster pick with the pinned-lesson warning given —
  declining is a stated outcome; the ceremony held).

## [4.4.0] - 2026-08-15

**MINOR — the confirm guard + lesson→skill promotion + the findings_19 fixes
(plan 036, evidence C40).** Adds migration `003_skills.sql`. Two capabilities the
maintainer ordered after the lesson feature's first field use, plus the three
findings_19 items — one of which ("the tool's own hollow pass": a success-shaped
no-op with destructive advice) is the report's headline.

### Added

- **Never-auto-confirm, mechanically**: `entity_upsert` now REFUSES any write that
  lands a lesson in Approved or Promoted from a different state — **including a
  brand-new row born there** (without covering fresh inserts, the gate would be
  trivially bypassable by inserting-as-Approved) — unless the item carries
  `"operator_confirm": true` (operator-words-only, the `force` doctrine). The
  transition write must keep every content column byte-identical to the stored row
  (**this closes findings_19 §2** — the immutability trigger fired one write too
  late, leaving the approval write itself unguarded; now approval/promotion is
  mechanically NOT an edit, drift refused naming the columns); approval requires
  `confirmed_by` ON that write (attribution can never be added later — previously
  readable only out of the DDL, now enforced and stated in the refusal); the server
  appends the typed `lesson-confirmed`/`lesson-promoted` journal event itself.
  Loops never carry the flag — Proposed lessons accumulate, and the ITERATION
  contract line gains a trailing `lessons_pending=<n>` field.
- **Lesson→skill promotion** (migration `003_skills.sql`): the `skill` family
  (SKL-, On-request) — metadata only (kebab `name`, `description` = the trigger,
  `level` project|user **default project**, `target_path`, born Approved out of the
  operator interview, `superseded_by` for re-distillations); the BODY lives solely
  in the written `SKILL.md` (project: `.claude/skills/<name>/` in the target repo;
  user: `~/.claude/skills/<name>/`), operator-owned after creation — the server
  never writes or reads skill files (the v3 files-doctrine). `lessons.promoted_to`
  = FK → skills (the DEC→ADR promotion idiom; many lessons → one skill); the
  lesson lifecycle gains **Promoted** (Approved → Promoted only, guard-covered;
  content AND `promoted_to` frozen — the immutability trigger's WHEN extends so
  promotion cannot re-open the class §2 taught). **Full graduation**
  (maintainer-locked): Promoted lessons leave the CLAUDE.md note; the note keeps
  one line naming each promoted skill with its level. The new stock prompt
  **`skill-promote.md`** (17th file) runs the interactive ceremony: cluster
  candidates (the ECC continuous-learning idea) → the operator interview
  (name, trigger, edge cases, THE LEVEL — asked every time, default project;
  pinned candidates warned they will leave the note) → operator approves the
  content → the agent writes the file → the SKL- row + guarded Promoted flips.
  Lineage: Voyager's skill library; Soar's chunking (episodic PE- journal →
  declarative LL- lessons → procedural skills); Claude Code native skill
  discovery; ECC's promote-with-human-confirmation — tamheed's deliberate
  difference: operator confirmation at entry replaces numeric confidence/decay.

### Fixed

- **The v1-note classifier no longer gives destructive advice** (findings_19 §1):
  classification is marker-based, never heading-only; a heading plus an
  `@<package>/CLAUDE.md` import line is the RECOGNIZED POINTER PATTERN — the
  managed span is written and rebuilt in the PACKAGE's own CLAUDE.md, the root
  file stays untouched, and the warning names both full paths (the old classifier
  advised deleting the very section that carried the import, severing the
  always-loaded note — and reported the un-updated file as "unchanged", a
  success-shaped no-op). Every note-related warning now names the full path; the
  stale "the v2 note" wording is gone.
- **FK failures get NOT-NULL parity** (findings_19 §3): "FOREIGN KEY constraint
  failed" now names the offending column, the value, and the referenced table —
  "free text is never legal here" — instead of leaving the caller to try synonyms.

### Changed

- register-liveness step 14 teaches the enforced flag flow; loop-guard carries the
  standing never-carry-the-flag rule; the viewer's Lessons section gains the
  Promoted-into-skills subsection and the skills register; governance records the
  lesson/skill status sets and the promotion doctrine.
- **The lab caught the eval spec again — second release running**: beat 11's
  graduation made the 4.3.0 "≥1 operator-Approved lesson" assertion impossible on
  a conformant fixture (the only Approved lesson correctly became Promoted).
  `pkg_check` gains the **`nonempty-any`** primitive (≥1 row carries the column —
  evidence that survives lifecycle graduation), and the assertion now checks
  `confirmed_by` presence instead of current state, with both catches recorded in
  its check text.

**MINOR — the lessons-learned entity family (plan 035).** Execution agents make
mistakes and learn; the lessons now live IN the package, are confirmed by the
operator, and bind every future session. The first new entity family since the v4
re-baseline — it validates the extension recipe in-tree and ships the registry-row
write path extension.md promised. Grounded in PMI lessons-register practice, NASA
LLIS (approval-before-entry), agent-memory research (Reflexion: the failure mode is
persisting a WRONG lesson — hence the operator gate), and US Army AAR doctrine
(both polarities). All eight design forks maintainer-locked across two interviews.

### Added

- **Migration `002_lessons.sql`** — the v4 chain's first real migration
  (`schema.sql` stays the frozen 001 byte-twin). The `lessons` table: the full
  LLIS shape — `statement` (the lesson), `context` (the driving event),
  `recommendation`, `rationale`, `kind` (improve|sustain), `category`, both
  impact columns, `recorded_at`, `confirmed_by`/`confirmed_at` (operator
  attribution, never back-filled), `pinned`, `superseded_by`. Lifecycle:
  Proposed → Approved / Rejected / Superseded → Obsolete — no Draft (born
  Proposed, the decisions pattern) and no Deferred (an undecided lesson keeps
  nagging by design). Approved CONTENT is immutable via a column-selective
  trigger (the ADR shape) — `pinned`, the lifecycle transition, and
  `superseded_by` stay operator-mutable; revise by supersession. The migration
  also recreates `trace_edges` with the new **`learned_from`** relation
  (lesson → defect | decision | risk | slice | wbs-item | progress-entry,
  G-REL-enforced; safe because migrations apply before the JSONL load, so the
  table is empty at 002 time).
- **The always-loaded surface**: the CLAUDE.md note span (marker bumped
  `tamheed:note v4`) gains a **Lessons section** — its first data-derived
  content. ONLY operator-Approved lessons render, pinned lessons always, the
  newest (numeric id order) filling a cap of 10 unpinned, one count line naming
  the rest (`entity_query("lesson")`). Zero approved lessons = no section (the
  note stays byte-identical for lesson-less packages). **Injection posture**:
  the confirmation interview is the first screen; the same G-INJECT patterns
  that screen every emitted prompt run over each raw statement and BLOCK the
  emission naming the LL- row. The obligations table gains the lesson-capture
  row — in the note AND `agent-control.template.md`, whose sync is now
  test-enforced for the first time.
- **`lessons-confirmed`** — the 14th package-scope readiness advisory: Proposed
  lessons awaiting the operator's interview (inherits waiver support; fires on
  existence, so no hollow-pass class).
- **Registry-sync in `package_migrate`** (the blocker fix): a v4 store created
  before a new baseline entity type cannot write rows of that type (registry FK,
  fail-closed by design). `package_migrate` on such a store now offers a staged
  **registry-sync**: preview reports `mode: "registry-sync"` +
  `entity_types_added`; confirm appends the registry rows + a typed PE- note —
  a pure append, no backup taken, and an existing `data-v3-backup/` never blocks
  it. An up-to-date v4 store still refuses.
- **The viewer**: a dedicated **Lessons** section in review.html — the operator's
  confirmation queue first (Proposed rows), then Approved (pinned flagged, both
  impacts, attribution), then closed rows folded as evidence; the traceability
  flow lanes place lessons beside risks; registers fold/CSV/graph pick the
  family up automatically. Zero-JS doctrine untouched.
- **The lab**: `lab/scenario.md` gains the lessons continuation beat (run as an
  INCREMENTAL session against the recorded package — the only real-agent path
  that exercises registry-sync); three new eval assertions (≥2 lessons, ≥1
  operator-APPROVED, the review surface renders the section); the fixture
  regenerated by a real agent driving the beat end-to-end. **The lab caught a
  bug in this release's own eval spec on first run**: the original assertion
  (`nonempty lesson confirmed_by`) could never pass against a
  scenario-conformant fixture — the deliberately-Proposed remainder has an
  empty `confirmed_by` by design — and was replaced with the count-on-Approved
  form, with the catch recorded in the assertion text.
- Teaching surfaces: the catalog family row + entity-map/lifecycle diagram
  updates, governance (LL- identifier row, the lesson status set, learned_from),
  seven stock prompts teach capture (drift-register taxonomy, progress-sync,
  slice-review, defect-triage), reading (package-onboarding, orient-resume), and
  the operator interview (register-liveness step 14, incl. the pin decision and
  the full-row re-read-then-resend rule); docs/entities.md gains the full family
  study with the research sources.

### Changed

- `check.py`: lint 11 gains the `learned_from` needle; lint 9 blacklists
  `tamheed:note v3` (historical-exemption pattern); the templates' relation
  lists and the naming-conventions identifier table carry the new family
  (lint-forced).

## [4.2.1] - 2026-08-15

**PATCH — findings_18 (plan 034, evidence C39).** The hollow-pass fix and
customization-lag visibility. No schema change, no migration.

### Fixed

- **`risk-liveness` can no longer pass hollow** (findings_18 §3): with
  `probability`/`impact` unpopulated on every open/materialized risk the high-risk
  predicate could never fire, and an empty result read as a clean `pass` — "a rule
  that cannot discriminate is not a green light, and its green is the most misleading
  state it has." The rule now reports `indeterminate` with a note naming the
  unpopulated scale (the C35 doctrine, extended to this rule's load-bearing columns);
  the population check is scoped to the rule's candidate rows, so retired risks
  carrying a scale cannot mask a hollow pass over the live ones. A sweep of every
  readiness rule confirmed this was the only rule in the hollow-pass class.

### Changed

- **Customized stock prompts now show how far the stock has moved under them**
  (findings_18 §2): customizing a stock prompt opts it out of every future
  `refresh_stock` — silently and permanently. Each `diverged_customized` entry in the
  `handoff_emit` report now carries `stock_last_changed` (the newest release in the
  bundled history whose stock body differs from all earlier ones; `null` when no
  history exists), and the CUSTOMISED warning names the moved files with the honest
  conditional — *when* the operator customized is unknowable by design (memoryless
  emission), so the warning states the stock's last change, never the customization's
  staleness. The reconcile path is a hand-merge; `prompts/README.md` now says so
  explicitly, and `stock-history.json` carries every release's body to diff against.
- **The repair doctrine gained its second and third halves** (findings_18 §1, the
  operator's own catch): a generated repair payload is PASTED, never re-typed — the
  hand is the untrusted transport — and every multi-row repair ends with an
  independent verifier that re-reads the JSONL and re-derives each expected value
  from its source. Taught in the artifact catalog, the prompts README standing rules,
  and a new `integrity-check.md` repair-verification step; `register-liveness.md`
  now names the scale prerequisite for `risk-liveness`.

## [4.2.0] - 2026-08-15

**MINOR — findings_17 + the documentation reckoning (plan 033).** The ACMP v4-migration
acceptance's two behavior fixes, and the maintainer-ordered full documentation audit:
every markdown file at every level reviewed, the stale/overlapping/dead surfaces fixed
or removed, and four lints added so the class stays closed. No schema change.

### Fixed

- **`open-questions-resolved` discriminates** (findings_17 B1, evidence C38): the amber
  now counts a row only when it has neither a non-empty `resolution` nor a
  `resolved_by` AND its lifecycle status is non-terminal (Deferred/Rejected/Superseded/
  Obsolete are excluded); the can't-discriminate note fires only when neither column is
  populated anywhere. On the ACMP data the amber drops 72 → 1 (the one genuinely open
  question). `resolved_by` is never back-filled — attribution is a fact about a person.
- **Milestone stash parity in `package_migrate`** (findings_17 A5): the v3 milestone
  columns dropped by the v4 demotion (`lifecycle_status`, `disposition`,
  `disposition_reason_ref`) are now stashed into `custom_attributes` as `v3_*` — the
  same pattern the risks got — instead of silently discarded; the preview report rows
  gain `stashed_as`. (ACMP's six dropped statuses remain recoverable from its
  `data-v3-backup/`.)
- **Bare-letter risk scales map** (findings_17 C3): `H`/`M`/`L` (any case) normalize to
  `high`/`medium`/`low` during migration, reported under `risk_scale_normalized`,
  instead of falling through to the stash path. Scale semantics (probability = judged
  likelihood of materializing; impact = severity if it does; the enum IS the scale) are
  now documented in `references/governance.md`.
- **Three sequence diagrams in `docs/entities.md`** carried `;` inside message/Note
  text — a mermaid lexer break; all sequence text now holds to the conservative subset
  (no `;`, no `#`).

### Removed

- **`plugins/tamheed/schemas/` — actually deleted this time.** The 4.0.0 entry recorded
  this removal as part of the v1 retirement, but the execution missed it: the directory
  (21 files) stayed on disk for two releases while the CHANGELOG, CLAUDE.md, and
  docs/entities.md all claimed it gone. The 4.0.0 entry is append-only and stands
  uncorrected; this entry states the miss plainly. The documentation audit caught it.
- `references/migration-runbook.md` — wholly about the retired v1→v2 path; its one
  living section (`scratch_diff`) folded into `server/README.md`.
- `examples/` (41 files) — a v1-era generated package masquerading as teaching
  material; the lab package + the demo package are the living examples.
- `references/entity-guide.md` — overlapped the artifact catalog wholesale (the
  maintainer's audit trigger); merged into `references/artifact-catalog.md`, which now
  carries the per-family rules, the four operating rules (claimed-vs-verified, drift,
  waivers, markers), the repair doctrine (repair from `data/*.jsonl`, never from
  `entity_query` output — findings_17 C1), the entity-map and lifecycle diagrams, and
  a version stamp.

### Added

- **The Mermaid delivery** (a v4.0.0 acceptance item the maintainer could not find):
  `docs/entities.md`'s seven diagrams are now linked from README, CLAUDE.md, and the
  docs siblings; `docs/workflow.md` gains the 22-stage phase-grouped flowchart + the
  human-gate sequence; `docs/methodology.md` gains the HYP→EXP/POC→DEC→ADR chain;
  `docs/migrate-from-keystone.md` gains the migration-path diagram; the artifact
  catalog carries the entity-map + standard-lifecycle diagrams in the bundle.
- **ADR-0002** (`docs/adr/adr-0002-v4-entity-model-re-baseline.md`) — the v4 re-baseline
  finally has its ADR, recorded retrospectively at the audit; partially supersedes
  ADR-0001 (the store doctrine survives; the prompts-table, milestone-lifecycle, and
  frozen-v1 clauses do not). ADR-0001 received only its status pointer.
- **Four lints** (the audit's root-cause fix — the unlinted zone is gone):
  - lint 9 extended to ALL teaching surfaces (prompts + templates + references +
    SKILL.md) with a **closed-triangle gate roster**: every gate name a surface may
    teach must sit in exactly one tier (engine / judgment / warn) synced both
    directions against `quality-gates.md`;
  - lint 10 **dead-path**: every markdown link and backticked repo path in
    references/, SKILL.md, server/README, and db/CANONICAL must resolve — relative to
    the file, the repo root, or the bundle root (bundle-relative references are legal
    in-bundle). templates/, prompts/, and `references/generated-structure.md` are
    excluded: their paths describe the generated package;
  - lint 8 extended to **five version-stamped surfaces** (root README, server README,
    prompts README, SKILL.md, artifact-catalog.md);
  - lint 11 **template-sync**: the governance/naming-conventions templates' copied
    tables must match `references/governance.md` (the necessary-copy doctrine).
- An ACMP-shaped OQ fixture and migration-stash/letter-map tests pin the findings_17
  fixes; evidence **C38** archived
  (`plans/evidence/acmp-field-report-17-2026-08-15.md`).

### Changed

- The documentation sweep: SKILL.md teaches the real v4 `package_migrate` UX (staged
  preview, report keys, `confirm`); `references/quality-gates.md` gains G-REL (blocking
  since v4.0.0) and the explicit Warn-tier (prose-only) label; `templates/
  package-readme.template.md` rewritten for a v4 package; ~30 stale claims across
  references/, templates/, docs/, and the root files corrected per the audit's
  line-numbered lists; `plans/README.md` rewritten as the era-grouped program index
  (alignment history condensed into a chronicle — full text in git history; evidence
  files untouched).

## [4.1.0] - 2026-08-14

**MINOR — the prompt-surface completion (plan 032).** Closes the v4.0.0 teaching gaps
found by the maintainer-requested prompt assessment, and fixes the diverged-wave
problem at its root. No schema change, no migration.

### Added

- **Stock-history classification + safe refresh**: the bundle ships
  `prompts/stock-history.json` — every stock prompt body ever released
  (v3.0.0→v4.1.0, deduped, `{package}` placeholder intact). Every `diverged` stock
  file is now classified: **`stale-stock`** (byte-equal to an older release's stock
  after the substitution — the operator never customised it; reported with the release
  it matches) vs **`customized`** (equals none). `handoff_emit(refresh_stock=true)`
  safely overwrites ONLY stale-stock files (before the injection/stale screens);
  customized files are never touched by refresh; `force` still overwrites ALL
  diverged. This resolves the findings_14 "indistinguishable without history" gap at
  its cause — the v3.2 warning now names each class and its safe path. Missing
  history degrades to `customized` for everything (never a false stale-stock).
- **`register-liveness.md`** — the 15th stock scenario: the playbook for the readiness
  engine's amber list, walking all thirteen package-scope advisories (markers, overdue
  and unresolved OQs, decaying assumptions, unowned high risks, unmeasurable
  hypotheses, unpromoted architectural DECs, unmerged scope changes, unbound ACs,
  minor defects, deferred-work triggers, unapproved plans, unwired requirements) with
  operator STOPs for promotions, waivers, plan approvals, and activations.
- **Teaching-surface lint (check.py lint 9)**: prompts + prompt templates may only
  teach vocabulary the engine has — G-* gate names (mechanical roster imported from
  the server + the judgment tier synced against `quality-gates.md`), `event_type`
  values, relation kinds — with a retired-name blacklist (`binds_to`,
  `milestones-reached`, the old `"status"` column key, `PRM-`, uppercase `PASS/FAIL`
  verdict teaching); plus a stock-history currency check — a release that changes a
  stock prompt without appending its body cannot ship. `GATE_NAMES` and
  `PE_EVENT_TYPES` are tied to gate_run's real report keys and the DDL CHECK by
  contract tests.

### Fixed

- **The three prompt-pattern templates were never swept for v4** (a 4.0.0 miss):
  `initial-prompt`, `follow-up-prompts`, and `review-prompts` templates now teach the
  v4 recording contract — the `Review` claim, the full evidence chain on
  `audit_record`, the `[NEEDS-CLARIFICATION: OQ-NNN]` marker rule, the operator-only
  `WVR-` waiver route, the SC- drift lifecycle with delta edges — and orient via
  `entity_query`, not retired v1 file paths.
- `defect-triage.md` taught the retired `"status"` column key in its upsert example
  (the engine rejects it; now `lifecycle_status` — the class of bug lint 9 exists to
  prevent).
- `release-close-out.md` and `phase-close.md` now sweep `expired_waivers` (resolve the
  underlying item, or fresh operator words — never a silent carry-over).

## [4.0.0] - 2026-08-14

**MAJOR — the entity-model redesign (plan 031/B27).** Built on a full study of every
entity family (three exhaustive code scans + three external best-practice research
reports incl. a dedicated DEC-vs-ADR study; 15 maintainer-locked decisions across five
interview rounds — the rationale record is `docs/entities.md`). A v3 package is NOT
opened by this release: back it up, then run `package_migrate(name)` (preview) and
`package_migrate(name, confirm=true)` — the old files are kept in `data-v3-backup/`.

### Changed — the store (re-baselined schema)

- **The schema chain was re-baselined**: `schema.sql` is the full v4 DDL and the new
  `migrations/001_init.sql` byte-twin; the v2/v3 migrations (002_example_glossary,
  003_drop_prompts, 004_readiness_views) were retired — their end-state is folded into
  the baseline (glossary_terms is a baseline table; the prompts table no longer exists
  anywhere; the latest-verdict views ship in the DDL) and the v2/v3→v4 lineage lives in
  the migrate tool, not stacked ALTERs.
- **Claimed vs verified done**: `Review` (done-claimed) joins the wbs-item/slice
  lifecycle, distinct from `Implemented` (done-verified); every readiness closed-set
  counts Review as OPEN. Audit verdicts carry their evidence chain: `verified_by`
  (human/agent/ci), `verification_method` (auto-test/manual/inspection),
  `against_commit`. The requirement auto-advance trigger now uses LATEST-verdict
  semantics (the any-Met-ever flaw migration 004 fixed in the views was still live in
  the trigger through v3).
- **Lifecycle column unified**: `defects.status` and `deferred_work.status` are
  `lifecycle_status` (vocabularies unchanged) — one column name for the lifecycle axis
  (ADR-0001's three-axis doctrine).
- **Verdict vocabularies normalized, domain sets kept**: experiments/POCs conclude
  `Validated/Invalidated/Inconclusive/Pending` (a hypothesis verdict, not a test
  verdict — was PASS/FAIL); tests keep Pass/Fail/Pending; audits keep
  Met/Partial/Not-met/Pending.
- **Milestones demoted to roadmap labels**: no lifecycle, no disposition, never gate —
  a milestone that gates is an execution gate. Gates gained `outcome`
  (Go/Hold/Redirect/Kill, stage-gate practice).
- **Scope changes got a drift-delta lifecycle**: Proposed → Approved → **Merged**, with
  typed delta edges (`scope_adds`/`scope_modifies`/`scope_removes`) naming the affected
  rows; the `scope-changes-merged` advisory flags Approved-never-Merged.
- **The progress journal is typed**: `event_type` (work-done/verdict-recorded/
  transition/forced-override/gate-decision/escalation/correction/note) + `subject_id` +
  `actor` + `corrects` (compensating events — journals are never edited).
- **Lightweight enrichment, gate-checkable only**: requirements gained `rationale` +
  `verification_method` (Test/Demonstration/Inspection/Analysis); risks gained
  `owner` + `response_strategy` + high/medium/low enums on probability/impact; OQs
  gained `owner` + `due_by`; assumptions gained `validation_date`; hypotheses gained
  `metric` + `threshold`; ADRs gained `confirmation` (MADR 4.x — how compliance is
  verified; part of the immutable content).
- Stakeholders' label column is `title` (was `name`); a provenance `source_span` now
  REQUIRES a `source_kind`; `packages.mode` is CHECK-constrained; five indexes back the
  hot view scans; `binds_to` (zero usage ever), `entity_types.template_ref` (never
  read), and per-row `diagrams.generation_class` were deleted.

### Added

- **`WVR-` waivers**: an operator-approved row (rule + entity + justification +
  approver + expiry) satisfies a named readiness rule for a named entity — reported as
  `waived`, never silent; expired waivers are surfaced and ignored. The alternative to
  a waiver path is informal bypass.
- **Severity-thresholded blocking**: open critical/high defects block phase/slice/
  package readiness; medium/low surface as the `defects-minor` advisory.
- **`[NEEDS-CLARIFICATION: OQ-NNN]` markers** (spec-kit's forbidden-to-assume idea,
  tamheed-native): legal in any prose field while the cited OQ is live; a marker with
  no id, a dangling id, or a resolved cite fails G-COMPLETE; the `clarifications-open`
  advisory counts live markers.
- **Blocking G-REL gate**: stored trace edges must satisfy the endpoint-type rules
  (safe because the migrate tool retypes violating edges to `relates_to` at conversion,
  adopt reports them, and writes reject them). RELATION_RULES cover the scope-delta
  kinds; kinds with no evidenced edge semantics are deliberately relates_to-only.
- **Liveness advisories** (registers stay alive because the engine nags, not because
  columns exist): `decisions-look-architectural` (the DEC→ADR one-way-door nag),
  `open-questions-overdue`, `risk-liveness`, `assumptions-current`,
  `hypotheses-measurable`, `acs-slice-bound`, `clarifications-open`,
  `scope-changes-merged`, `defects-minor`. G-PROGRESS warns on its vacuous pass;
  `human_required` now surfaces `ready` (DoR) gates and gate outcomes.
- **`package_migrate` is the in-place v2/v3→v4 converter**: staged (preview = the full
  rewrite report, nothing written; confirm = backup to `data-v3-backup/`, legacy
  prompt conversion, transform, store-validated canonical write-back, a
  `system:migrate` audit event). `package_open` refuses pre-v4 stores by version.
  `package_adopt` runs the edge-rule sweep at adoption. Migration suite:
  `tests/test_migrate_v3to4.py` (incl. byte-determinism).

### Removed

- **v1 ingestion is retired**: the frozen v1 validator, the markdown importer, the v1
  goldens/fixtures, `required-artifacts.json`, and the `schemas/` directory (runtime-
  dead; the DDL is the single source of data shape). Escape route for a v1 Keystone
  package: migrate under tamheed 3.2.1, then v3→v4 here
  (`docs/migrate-from-keystone.md`). The shared recording pipeline adopt used moved to
  `server/record.py`; check.py's catalog-sync lint retargeted to the live registry's
  Always class.

### Documentation

- `references/artifact-catalog.md` rewritten as the v4 catalog (lint-synced to the
  registry); `references/governance.md` carries the full v4 identifier/status/vocabulary
  tables incl. the DEC-vs-ADR one-way-door promotion rule; the recording-obligations
  table (agent-control template + the emitted CLAUDE.md note, now `tamheed:note v3`)
  teaches Review, waivers, markers, delta edges, and the evidence chain; all 14 stock
  prompts + the prompts README updated (incl. the findings_16 either-discriminator
  stale-lock wording); `docs/entities.md` is the full per-entity study with the
  decision rationale and source register.

## [3.2.1] - 2026-08-14

Documentation release from the fifteenth ACMP field report — the v3.2.0 acceptance
(evidence **C36**, archived at `plans/evidence/acmp-field-report-15-2026-08-14.md`):
all three findings_14 negatives verified fixed, the prompt curation completed, and the
obligations note's **instruction transfer proven** in a controlled probe (autonomous
discharge awaits a genuinely fresh session). **No schema migration, no code-behavior
change.**

### Fixed
- **`prompts/README.md` indexes the folder, not just the library** (C36): a closing
  table row points table-scanners at project prompts ("any other `.md` here —
  operator-authored, purpose-named"), and a new **"One session at a time"** section
  teaches the single-writer lock and the field-validated stale-lock discipline (two
  discriminators: a live pid that plausibly IS an agent session AND that started
  before the lock's `taken_at`; never auto-clear).

### Changed
- **The documentation READMEs are updated with every release — lint-enforced**
  (maintainer contract): check.py lint #8 requires the root README, the server
  README, and the prompts operator guide to carry the current version string; a
  release that skips one fails the gate. The root README received its full v3 content
  sweep (11 verified-stale spots: version badge, prompts-as-files + the 15-file
  library, the note-span/force contract, the transition guard + typed relations,
  `readiness_check` in the tools table, the flow view + hover-isolate + readiness
  panel, the mermaid handoff node, the repo tree's missing `prompts/` +
  `db/migrations/`, ten suites, Maturity v3.x). The versioned operator guide
  deliberately diverges package copies each release — that IS the guide-update
  delivery signal via the documented delete+re-emit path.

## [3.2.0] - 2026-08-14

Fix release from the fourteenth ACMP field report — the v3.1.0 acceptance run
(evidence **C35**, archived at `plans/evidence/acmp-field-report-14-2026-08-14.md`):
every findings_13 recommendation verified working, plus two real defects the run
caught in the note/force machinery. **No schema migration — existing 3.x packages
unaffected.**

### Fixed
- **The CLAUDE.md note now actually self-updates** (C35/N1 — the code refused
  divergent updates while its own warning text promised "self-updates thereafter";
  the operator quoted the code back). The `<!-- tamheed:note v2 -->` span is
  **tool-owned** and rebuilt on every `handoff_emit` — no `force`, no `diverged`
  bookkeeping; a hand edit inside the markers is overwritten WITH a warning ("keep
  operator content OUTSIDE the markers"); content outside the markers is never
  touched.
- **`force` no longer couples the note to prompt clobbering** (C35/N2): with the note
  self-updating, `force` means exactly one thing — overwrite ALL diverged stock
  prompt files (+ `.mcp.json`). A new guidance warning states that the two divergence
  kinds (your customisation vs a template that moved on) are indistinguishable
  without history, and names the zero-machinery per-file acceptance path: **delete
  the file and re-emit**.

### Changed
- **`indeterminate` readiness status** (C35/N3): a rule with `discriminating: false`
  whose query found nothing reads `indeterminate`, never `pass` — "cannot measure" is
  not "verified clean". `ready` and the `Implemented` transition guard trip only on
  real `fail` (non-blocking, maintainer-locked); the loud all-null-fail case
  (`risks-discharged` firing on every risk) stays `fail`.

## [3.1.0] - 2026-08-13

Follow-up release from the thirteenth ACMP field report — the v3.0.0 acceptance run
(evidence **C34**, archived at `plans/evidence/acmp-field-report-13-2026-08-13.md`):
"the MAJOR landed clean", and `readiness_check` caught a prematurely-closed slice that
seven passing gates structurally could not see. This release answers its findings plus
the maintainer's converted-prompt questions. **No schema migration — existing 3.x
packages unaffected.**

### Added
- **`prompts/README.md` operator guide** ships inside the stock library (14 → 15
  files, managed like the rest): which prompt for which situation, the semi-auto day
  loop, the fully-auto loop-iteration/loop-guard pairing with the `ITERATION:`
  contract, and project-prompt naming/curation rules. The CLAUDE.md note points at it.
- **Converted-prompt curation hints**: files converted from the legacy prompts table
  (provenance header) get a standing per-KIND hint in every `handoff_emit`
  (`converted_prompts`) naming their stock counterparts — self-clearing when the
  operator removes the header line (reviewed) or the file; the same hints ship at
  conversion time (`curation` in the open report). The tool never deletes or renames
  converted files: they interleave restated generic workflow with unique project
  knowledge that exists nowhere else (preserve-and-signal, measured on the field data).
- **`requirements_unwired` advisory on both surfaces** (gate_run + the
  `requirements-wired` package readiness rule): execution-created requirements with
  zero trace edges — invisible to G-TRACE (mvp-matrix only) until now;
  drift-register/progress-sync prompts gain the wire-in-the-same-session step.
- **Hover-isolate in both graph views**: hovering a node dims every edge except its
  own — pure CSS (`:has()` + hidden incident-edge copies), zero JS, graceful
  degradation on older browsers.

### Changed
- **Leftover `handoff/prm-*.md` warnings are per-file verdicts** by content compare:
  "copy of prompts/<name> — safe to delete" vs "NOT a copy — MOVE it into
  <package>/prompts/" (the blanket "delete" would have destroyed a live project
  prompt; the operator had to do this compare by hand in findings_13 §2).
- **Readiness rules say when they cannot discriminate**: a rule keyed on a column that
  is NULL for every row of its type carries `discriminating: false` and a "0 of N rows
  have <column> set" note — severity unchanged (an unpopulated column is itself a
  package deficiency); slice/phase `defects-closed` also counts open defects with no
  `found_in` ("invisible to this scope").
- **The isolated fold breaks down per family**, isolated requirements sort first with
  a ⚠ prefix, and the flow lead names how many requirements the view cannot draw —
  the unverified requirements were exactly the ones the picture hid.
- The C22 restated-state detectors now cover package prompt files (advisory): a
  hard-coded audit tally inside a prompt drifts exactly like one in AGENTS.md.

## [3.0.0] - 2026-08-13

Major release from seven direct maintainer observations after sustained ACMP usage
(plan 027/B23 — no findings file; the observations, verification, and two interview
rounds are recorded in `plans/027-v3-prompts-files-readiness.md`). Prompts leave the
database, execution agents are bound to record drift, relations get typed rules, phase/
slice closes get a deep readiness engine with a hard transition guard, and the review
surface gains a layered traceability-flow view.

> **Migration note (v2 → v3).** Two append-only schema migrations ship:
> `003_drop_prompts.sql` (the prompts table is gone) and `004_readiness_views.sql`
> (latest-verdict views); the store now tracks the applied head via
> `PRAGMA user_version` (the full shipped set: `001_init.sql` = the schema itself,
> `002_example_glossary.sql` = plan 015's extension worked example, 003, 004). Opening a v2 package converts `data/prompts.jsonl` to
> `<package>/prompts/*.md` ONCE — loudly, abort-on-anomaly; the source is kept as
> `data/prompts.jsonl.converted`, PRM- trace edges and the `prompt` registry/omission
> rows are scrubbed, and the full report lands in the `package_open` result.
> `handoff_emit` no longer copies prompts into the target and its `subdir` parameter is
> refused: delete any leftover `handoff/prm-*.md` copies, delete the v1
> `## Tamheed progress tracking` section from the target's CLAUDE.md, and re-run
> `handoff_emit` for the marker-managed v2 note.

### Changed (BREAKING)
- **Prompts are `.md` files in `<package>/prompts/`, never database rows** (maintainer
  note 1): migration `003_drop_prompts.sql` drops the table; the `prompt` entity type
  is gone; `package_open` converts legacy packages once (see the migration note);
  Stage 20 authors prompt FILES; `package_create` seeds the folder from birth;
  `migrate` lands v1 prompt files as package files verbatim. G-INJECT and the C24/D-8
  stale scan now run over the package prompt files at `handoff_emit`.
- **`handoff_emit` is pure target wiring**: `.mcp.json` + the CLAUDE.md operating note;
  no prompt copies; `subdir` refused; leftover v2 copies warned.
- **Typed relations enforce endpoint types** (note 4): `RELATION_RULES` hard-rejects a
  mistyped edge on new writes (e.g. `TEST —mitigates→ FR`) naming both types and the
  `relates_to` escape hatch; stored legacy edges are untouched and reported by an
  advisory `relation_rules` sweep in `gate_run` (never blocks).
- **`gate_run` verifies at gate time**: G-IDS runs `PRAGMA foreign_key_check` +
  entity_index consistency, G-DEC-STATUS/G-REQ-SRC run real SELECTs (whitespace-only
  provenance is now caught) — the three hardcoded "enforced at write time" pass
  literals are gone.
- **Phase/slice → `Implemented` is guarded** (note 8, maintainer interview): the
  blocking readiness rules refuse the transition; `"force": true` (operator-confirmed
  only) proceeds and the server itself appends a `FORCED transition` progress entry.
  Full-row re-upserts of already-Implemented rows never re-fire; `wbs-item` writes and
  `package_close` are never guarded.

### Added
- **`readiness_check(scope, id?)`** — deep lifecycle-state validation at close
  boundaries: blocking rules (decisions/ADRs pre-approval, ACs not latest-Met, open
  defects, undischarged risks) + advisory rules (deferred work, open questions,
  unapproved execution plans) + `human_required` (declared `execution_gates` rows —
  prose definitions surfaced for human confirmation, never machine-evaluated).
- **Migration `004_readiness_views.sql`** — `v_latest_verdicts` with NUMERIC journal
  ordering, `v_phase_exit` rebuilt on it, new `v_slice_exit`. Fixes two latent
  defects: the any-Met-ever phase-exit count (verdicts append; an old Met survived a
  newer Not-met) and the string `ORDER BY id` latest-verdict (wrong past 1000 rows).
- **Traceability flow view** (note 5): a layered left-to-right `#flow` section (Needs →
  Decisions → Work → Verification → Risks), connected nodes only, labeled and
  clickable, arrowheads, per-relation colors with CSS-only filter radios — zero JS.
  The circular graph draws connected nodes only (74% of the golden's nodes were
  isolated dots — now their own fold), with degree-scaled radii and a 12-hue palette.
- **Recording obligations on every always-loaded surface** (note 3): the emitted
  CLAUDE.md note is marker-managed (`tamheed:note v2`) and carries a mandatory 7-row
  obligations table (defect → `DEF-` first; out-of-scope → `DW-` with trigger;
  deviation → `SC-` FIRST; progress/audit/bind per unit; `readiness_check` before
  declaring done); the three Stage-20 templates instruct the MCP tools instead of v1
  markdown files; agent-control carries the same table verbatim.
- **Scenario prompt library 5 → 14** (note 2): slice-kickoff, defect-triage,
  drift-register, replan-deferred, release-close-out, phase-close, package-onboarding
  (semi-auto) and loop-iteration + loop-guard (fully-auto, machine-parseable
  `ITERATION:` contract for in-session /loop or external harnesses).
- **`PRAGMA user_version` migration tracking** in the store (stamped from Python;
  `server_info` reports `schema_version`) + a dedicated migration-mechanics suite.
- **Three new lints** (note 6): CHANGELOG releases strictly newest-first; the PEP 723
  `mcp<2` pin present and bounded (guards C33); every shipped migration named in this
  file. Plus an `execution-loop` eval case exercising the record-as-you-execute shape.

## [2.7.1] - 2026-08-08

Incident release from the twelfth ACMP field report (evidence **C33**, archived at
`plans/evidence/acmp-field-report-12-2026-08-08.md`): **MCP SDK 2.0.0 removed
`mcp.server.fastmcp`**, and the plugin's unbounded PEP 723 dependency made every freshly
resolved environment unable to start the MCP server — across all plugin versions; cached
`uv` environments masked it. **No schema migration — existing 2.x packages unaffected.**

### Fixed
- **The `mcp` dependency is bounded**: `dependencies = ["mcp>=1.2,<2"]` — verified
  end-to-end (a fresh `uv` resolve serves on mcp 1.28.1). Porting `serve()` to the SDK's
  successor module is deferred, deliberate work; the pin is never widened without it.
- **The startup guard tells the truth**: the ImportError path prints the caught
  exception and distinguishes *absent* (install guidance + the real error) from
  *incompatible* (`mcp <version> is installed but does not provide mcp.server.fastmcp —
  this build requires mcp<2`) — the old hint advised installing the package that was
  already present and was the cause.

### Added
- **`--selftest` reports SDK serving status** (`mcp sdk: ok (<version>)` /
  `UNAVAILABLE for serving (<error>)`) — informational, never failing, so a passing
  selftest can no longer be mistaken for a serving server (the broken import was the one
  path no health check touched).

## [2.7.0] - 2026-08-08

Execution-hardening release from the tenth ACMP field report — the first from
**sustained execution use** (a month of daily `progress_update`/`audit_record`/
`work_bind`/`entity_upsert` against a live package), which surfaced defect classes nine
migration runs structurally could not (evidence **C31**, archived at
`plans/evidence/acmp-field-report-10-2026-08-08.md`). **No schema migration — existing
2.x packages unaffected.**

### Fixed
- **The 1000-row id ceiling is gone**: `_next_id` orders by the parsed number
  (`MAX(CAST(SUBSTR))`) instead of lexicographic `ORDER BY id DESC` — text order agrees
  with numeric order only below 1000, so an executed package permanently re-allocated
  `PE-1000` and could never again write a progress entry or audit verdict.
- **`entity_query` tells the truth about write-only types**: `trace-edge`/`omission` are
  no longer reported as "unknown entity type" (that false message put a wrong statement
  into a package's permanent record for three days) — the refusal now names
  `entity_upsert` and `trace_query`.
- **Writes are counted, attempts are not**: an `INSERT OR IGNORE` row dropped by a
  constraint is a per-item error (batch fails), an idempotent duplicate reports
  `unchanged`, and `applied` counts actual writes.
- **The append-only journal is enforced**: `progress-entry`/`audit-verdict` rows can no
  longer be silently rewritten via `entity_upsert` — a conflicting id errors with a
  targeted hint (append via `progress_update`/`audit_record`; corrections are new
  entries).
- **`work_bind` is one transactional unit**: failures roll back pending
  `last_referenced` stamps instead of leaving them to ride the next tool call's commit.

### Added
- **Stale-tree guard**: the store fingerprints `data/*.jsonl` at load and refuses to
  dump over a tree that moved underneath the session (`git checkout`/`pull`, a second
  writer) — new `StoreStaleError` names the changed files; write tools return a loud
  "batch NOT applied" with recovery guidance, and `package_close` still releases the
  lock (flush skipped, with a warning) so a stale tree never traps the session.
- **Lock metadata**: `data/.lock` records `{pid, host, taken_at}`; a lock conflict names
  who holds it and since when (legacy bare-PID locks still described). Deliberately no
  auto-reclaim: PID reuse makes a liveness check unsound.
- **The working-tree warning, where it's load-bearing**: package `data/` lives in the
  git working tree — uncommitted package writes are destroyed by `git reset --hard` /
  `checkout` / `stash` like any uncommitted change. Stated in the emitted CLAUDE.md
  operating note (new emits), `references/handoff.md`, the migration runbook, and the
  server README.
- The review surface's execution section states **verdict rows ≥ criteria**
  (supersessions append; `gate_run` counts rows, the table shows each criterion's
  latest) — ending a recurring reconcile cost.

## [2.6.0] - 2026-07-23

Feature release from the eighth ACMP field report — a full-green acceptance (empty
UNEXPECTED bucket including JSON blobs; FR-100/107 provenance byte-equal; evidence
**C29**, archived at `plans/evidence/acmp-field-report-8-2026-07-23.md`). **No schema
migration — existing 2.x packages unaffected.**

### Added
- **`scripts/scratch_diff.py` — the runbook §8 diff, shipped in the bundle** (stdlib
  only): field-level comparison of two canonical-JSONL package `data/` dirs with correct
  per-table keying baked in (`trace_edges` on from/to/relation, `entity_types` on
  `type_id`, `omissions` on entity_type/reason, `packages` as a singleton field-compare)
  and the union of columns **including JSON blobs** — the exact mis-keyings that cost the
  field run ~1,000 DUP-KEY noise lines are now impossible. Duplicates are reported, never
  clobbered; human + `--json` output; exit 1 (differences) is the normal mid-life outcome
  — bucketing into VANISHED/REMAINED/UNEXPECTED stays operator judgment. Runbook §8 (and
  the docs mirror) now invoke it.

### Changed
- **`references/handoff.md` names the scan detectors' limits**: the audit-tally pattern
  requires the word `Met` (a rewritten "73 evidenced / 1 narrated" tally cannot
  re-trigger it) and the restated-block pattern needs ≥3 consecutive id-led lines — a
  clean scan is evidence of no drift, not proof.

## [2.5.2] - 2026-07-23

Patch release from the seventh ACMP field report — the first official runbook-§8 run: all
four findings_6 gaps verified closed empirically, and the empty-UNEXPECTED criterion caught
a **live-data blemish two prior audits had missed** (FR-100/107's stale pipe-shear
provenance in `custom_attributes`; evidence **C28**, archived at
`plans/evidence/acmp-field-report-7-2026-07-23.md`). **No schema migration — existing 2.x
packages unaffected.**

### Fixed
- **The `In progress → Activated` carry is noted**: it moved out of the silent exact map
  into a semantic-alias step (+ `In-progress` variant) with a ledger note like the prose
  carries — the report caught the C27 honesty-symmetry comment being untrue while the
  alias carried silently.
- **Per-entry coercion basis**: every `status_coerced` entry now records which branch
  fired (`status_map` | `semantic-default` | `default`) and the top-level
  `status_coerced_basis` is derived from the entries — `mixed` when a supplied map covered
  only some coerced words. A replayed map no longer takes credit for semantic-default
  coercions.
- **`entity_upsert` accepts JSON objects/arrays**: dict/list values serialize at binding —
  a raw dict `custom_attributes` used to fail the whole batch with sqlite's opaque
  "type 'dict' is not supported" (tripped in the field by the FR-100/107 provenance
  repair).

### Added
- **Runbook §8 diff-method line**: the field diff must enumerate the union of columns
  **including JSON blobs** (`custom_attributes`) — the exact blind spot that let the
  FR-100/107 staleness survive two audits. Mirrored in `docs/migrate-from-keystone.md`.

## [2.5.1] - 2026-07-23

Patch release from the sixth ACMP field report — the first with an **empty UNEXPECTED
bucket**: a scratch migration under 2.5.0 diffed field-by-field against the live package
verified every 2.5.0 fix byte-exact on real data (evidence **C27**, archived at
`plans/evidence/acmp-field-report-6-2026-07-23.md`). **No schema migration — existing 2.x
packages unaffected.**

### Fixed
- **Deferred-work prose statuses carry**: a status cell that fails exact enum matching
  carries the enum word as a prefix after leading punctuation/emoji (`**✅ Done <date>
  (<slice>)** — narrative` → `Done`), with a preview note per prose carry; `In progress`
  maps to `Activated`. Takes the ACMP register from 18/23 to 23/23.
- **The phase prose-status matcher actually fires**: the 020 pattern matched zero times on
  the fixture that motivated it — now unanchored (status sentences ending
  `- **Exit gate.** …` bullets match) with a word-boundary guard (`ExitStatus:` never
  matches), and a parenthetical qualifier terminates the capture
  (`Status: complete (delivered …)` carries `complete`).
- **No more doubled H1s in emitted prompts**: a PRM body opening with its own H1 identical
  to the title has that line stripped at emit time (a *different* in-body H1 is preserved) —
  the `# {title}` composition rule is invisible to prompt authors.
- **Diverged CSVs are recoverable**: `export_html` CSVs emit forced — they are derived
  outputs regenerated from the DB, like `review.html` itself; a hand-edited CSV is
  overwritten (reported `emitted`), while authored emissions (`handoff_emit`) keep the
  refusal path.

### Added
- **Runbook §8 — the scratch-diff regression measurement** (institutionalizing the report's
  method): scratch-migrate the frozen v1 source with the replayed `status_map`,
  field-level-diff against the live package, bucket into VANISHED / REMAINED / UNEXPECTED —
  **empty UNEXPECTED is the pass criterion**; delete the scratch. Mirrored in
  `docs/migrate-from-keystone.md`.

## [2.5.0] - 2026-07-23

Polish release from the fifth ACMP field report — the calmest of the cycle: the §7
re-populate+swap on v2.4.0 needed **zero blind repairs** and revived `v_phase_exit`
(evidence **C26**, archived at `plans/evidence/acmp-field-report-5-2026-07-23.md`). **No
schema migration — existing 2.x packages unaffected.**

### Fixed
- **Two-pass title resolution**: an exact `Title`/`Name` column wins outright — an `EPIC`
  crosswalk cell can no longer out-rank the real Title column via column-order alias
  scanning; long-form text resolves independently of the title column; id-shaped titles
  trigger the degenerate rescue.
- **Escaped in-cell pipes** (`\|`) parse as literal pipes inside one cell — rows no longer
  shear at the escape (sentinel substitution around the frozen parser).
- **Deferred-work `Status` carries** onto the DW enum — the recurring Done/Activated
  truth-up after re-migration is gone.
- Phase prose-status sections match by heading id **or phase title** (real-world headings
  carry titles).
- A **refused (diverged) prompt write no longer suppresses the stale scan**: the PRM rows'
  would-be bodies are scanned and reported marked "(not emitted: diverged)" — the signal
  the runbook promised now always fires.
- **Relations graph: fit-all by default + zoom controls** — the SVG scales to its
  container (every node visible on open) and CSS-only radio controls (Fit/2×/4×/8×, zero
  JS) zoom into the pannable frame.

### Added
- **`references/migration-runbook.md` ships in the bundle** — the operator procedure
  including the §7 re-populate + swap mechanics (populate refuses an existing `data/`;
  `package_open` keys on the directory; `packages.name` is cosmetic; swap = close, rename,
  reopen) and the after-swap note: force-re-emit the prompt library once (its content
  embeds the package name). Fixes the standing self-containment violation (the mapping
  contract pointed at a repo-only doc plugin installs never receive).

## [2.4.0] - 2026-07-23

**Data-fidelity release** (plan 020; evidence **C23–C25** from the fourth ACMP field report —
the one that *retracted its own verdict* after a post-cutover column-level diff found twelve
degradation classes that row-level checks certified as clean; archived WITH the retraction at
`plans/evidence/acmp-field-report-4-2026-07-22.md`). **No schema migration — existing 2.x
packages unaffected; ALREADY-MIGRATED packages should be re-populated per
`docs/migrate-from-keystone.md` §7 to repair the damage the old parser caused.**

### Fixed (migration data integrity — the ship-blockers)
- Title cleaning strips markdown **positionally** — the old character class deleted every
  ASCII hyphen, mangling governed ids (`FR-001`→`FR 001`) and severing cross-references; one
  200-char cap replaces the hidden second 120 cap.
- A fallback title **never becomes the statement**: long-form columns always take the raw
  cell. Weak-definition rows (previously the only rows with NO provenance bag — genuinely
  unrecoverable) now preserve their raw defining line in `custom_attributes.v1.raw_line`.
- `D-nn`→`DW-` keys on the **parsed number**, never row position (an unsorted register once
  silently shifted five ids); duplicate guard + full crosswalk in the preview.
- Imported acceptance criteria land **`Proposed`**, never Approved — the immutability trigger
  freezes `slice_id` at Approved and v1 has no slices; `v_phase_exit` stays completable.
- Five typed-column starvation aliases (tests.kind `Type`, deferred `Trigger to activate`,
  KPI `Measurement`/`Cadence`, bare phase numbers, stakeholder `role`); risks map their v1
  status into `risk_state` too; row-bearing files also emit their narrative document;
  sections split on the shallowest heading level; narrow phase prose-status parse;
  `Living`/`Complete` join the semantic status map; degenerate-title guard.

### Added
- **Fidelity ledgers** — the report's central ask (*"every ledger so far reports choices;
  none reports fidelity"*): post-flight `truncations` (length-histogram mass at exactly a
  cap), `column_starvation` (typed column NULL while the attribute bag holds the value),
  `field_mapping`, and an execution-state note. `title_fallbacks` reclassified as a
  **data-loss warning**. Emitted prompt bodies join the stale-reference scan (v1-protocol
  instructions + dead relative links; reported, never rewritten). Migrate leaves the package
  open so `handoff_emit` follows directly.
- **Viewer redesign** (maintainer requirements): dark **maximalist** identity (validated
  8-hue family palette, glow accents, gradient headers, print falls back to light); sections
  ordered State→Relations→Data; the **relations graph** — every entity a clickable node
  jumping to its anchored register row, trace edges as a deterministic chord diagram, zero
  JS, family-aggregate above 4,000 nodes; **per-table CSV downloads** (deterministic
  `csv/<table>.csv`, managed emissions); long text wraps in place (supersedes the 2.3.0
  horizontal-scroll behavior).
- Runbook §7: re-populating an already-migrated package after a parser upgrade (the
  no-revert repair path, including the PRM prompt refresh).

## [2.3.0] - 2026-07-22

Third field-report hardening (plan 019; evidence **C20–C22** from the v2.2.0 ACMP
re-migration — a clean regression pass: zero repair loops, verdict "Ship it"; archived at
`plans/evidence/acmp-field-report-3-2026-07-22.md`). **No schema migration — existing 2.x
packages are unaffected.**

### Added
- **Managed emissions (C20):** every file `handoff_emit` writes (handoff prompts, the
  scenario prompt library, `.mcp.json`) reports as `written`/`unchanged`/`diverged` — a
  hand-edited file is refused, never silently clobbered; `force=true` replaces it
  deliberately. The stale-v1 warning now lives in a `<!-- tamheed:stale-warning -->` marker
  block that **retracts itself** once the scan is clean — re-running `handoff_emit` is the
  standing "is the cutover done?" verifier. (Note: warnings emitted by pre-2.3.0 versions
  lack markers — hand-remove those once.)
- **Restated-content tripwire (C22):** register content copied into `CLAUDE.md`/`AGENTS.md`
  (≥3 consecutive id-led bullets/table rows, or a hard-coded audit tally) is reported as
  `restated_content` — `unlabeled` copies get a suggested reference rewrite; blocks that
  already cite `entity_query`/`review.html`/`gate_run` are classified `labeled-snapshot`
  and asked only to verify currency. Single ids in prose and product-domain words never
  fire. Doctrine documented: reference, don't restate; state each fact once.
- **Grouped migration ledgers (C21):** `status_coerced_groups` and grouped
  `title_fallbacks` (the operator decision unit is the group — 21 coercions ≈ 6 decisions);
  `status_defaulted` ledger for registers with no status column; `status_coerced_basis`
  annotation (defaults vs supplied `status_map`).
- The three-prompt-surface sync model documented (`references/handoff.md`); the canonical
  byte-stability guarantee stated as contract (`db/CANONICAL.md`).

### Changed
- Migration: registers with **no status column** default their rows to `Approved` (parity
  with weak-definition synthesis; decisions stay `Proposed`) — reported per (file, family)
  in `status_defaulted`. Compound literals documented as valid `status_map` keys; v1
  progress logs documented as narrative-only mapping.
- Viewer: **every table folds closed** behind `<details>` with the count in the summary —
  one consistent affordance replaces the 50-row threshold. Sole exception: gap/screening
  warning cards stay visible (they exist to be seen).
- All emitted/reported paths use forward slashes on every platform.

## [2.2.0] - 2026-07-22

Second field-report hardening (plan 018; evidence **C17–C19** from the first *successful*
production migration — the ACMP run under v2.1.0, verdict "production-quality"; archived at
`plans/evidence/acmp-field-report-2-2026-07-22.md`). **No schema migration — existing 2.x
packages are unaffected.**

### Added
- **Preview honesty ledgers (C17):** `status_coerced` — every v1 status word outside the
  lifecycle vocabulary is reported with its proposed mapping (semantic defaults:
  `Resolved→Implemented`, `Open`/`Monitoring`/`Active`→`Approved`, `Closed→Obsolete`); the
  operator confirms or overrides via `package_migrate(..., status_map={...})`. Plus
  `title_fallbacks`, per-file `partial_files` row counts, and the frozen validator's
  sha256+size in the pre-flight result.
- **Scenario prompt library (C19):** five ready-to-paste prompts (orient-resume with a
  git-history cross-check, progress-sync, integrity-check, generate-report, slice-review)
  ship in the bundle and are emitted into `<package>/prompts/` by migrate, adopt, and
  `handoff_emit`.
- **Cutover tooling (C19):** `handoff_emit(target_dir, subdir=…)`; a full operating-context
  `CLAUDE.md` note with an MCP tool cheat-sheet; a `stale_references` report (v1-flow
  pointers in `CLAUDE.md`/`AGENTS.md` as file:line + suggested replacement — the bare word
  "Keystone" is never flagged).
- **Viewer navigation & scale (C18):** sticky zero-JS section TOC; register families over 50
  rows and the raw trace-edge dump fold behind `<details>`; wide tables now actually scroll
  horizontally; migrated package metadata labeled `(v1-manifest-derived)`.
- `entity_query` returns `total` beside the LIMIT'd rows.

### Changed
- Migration: ADR/experiment/POC parse failures and unknown diagram stems now fall through to
  the narrative catch-all (preserved as documents, still listed in `unmapped`); narrative
  documents keep their full v1 front matter in `custom_attributes`; title aliases never
  resolve to the id column.
- Viewer freshness: a package with no recorded v2 activity says so ("package record dated …;
  no v2 activity recorded yet") instead of presenting the v1 manifest date as activity.
- `handoff_emit` on plugin-hosted servers no longer writes a project `.mcp.json` entry (the
  installed plugin already registers the server; the old emit hard-coded a machine- and
  version-specific plugin-cache path).
- Operator-facing tool descriptions de-jargoned.

## [2.1.0] - 2026-07-21

Field-report hardening (plan 017; evidence **C11–C16** from the first production v1→v2
migration — the ACMP run, archived at `plans/evidence/acmp-field-report-2026-07-21.md`).
**No schema migration — existing 2.x packages are unaffected by upgrade**; every fix is
code-level and applies the moment a package is opened.

### Added
- `server_info` tool: plugin version (single source: the bundled `plugin.json`), resolved
  package root, open package, migrations head — makes startup diagnosable (C11/C16).
- `package_migrate(allow_zero=[...], patch=<file>)`: the family-zero tripwire (a family
  parsing to zero against a nonzero manifest count blocks populate until acknowledged) and
  the blessed parse→patch→populate repair path (D1), both echoed in the preview.
- Preview parity (C13): parsed-vs-manifest `count_deltas`, `zero_families`, and the
  `partial_files`/`skipped_files` loss ledgers are computed **before** the operator confirm.
- v1 dialect tolerance (C12): MADR ADRs without front matter (heading id + `- Status:`
  bullet; "Decision Outcome" preferred over "Drivers"); `Given / When / Then`/`Criterion`
  AC aliases with uncapped statements; `Test ref` audit-evidence alias + verdict
  provenance; MoSCoW `M`/`Must` → `mvp=1`; `D-nn` deferred-work rows → governed `DW-`;
  catch-all `doc_kind='other'` narrative for zero-row unmatched files; `generated`
  manifest spelling; raw profile preserved; stale omissions dropped.
- Adopt fidelity (C13): `Cargo.toml` dependencies parsed; every extraction cap reported in
  the gap report; successful migrate/adopt results end with the cutover pointer (C15), and
  `handoff_emit` flags stale Keystone references in the target's CLAUDE.md.
- Tests: the v1-green **dialect-package** golden (the ACMP quirk profile) + a conservation
  meta-test that catches the next unknown parser fall-through; 25 new tests; a 7th eval
  scenario (`migrate-dialect-fixture`); a version-sync lint in `check.py`.

### Changed
- **Gate-behavior relaxations** (outcomes may change on existing packages, both toward
  honesty): `G-COMPLETE` strips code spans before the placeholder scan (parity with the
  frozen v1 gate) and exempts `custom_attributes` (provenance, not authored content —
  G-INJECT still screens it at emission); `gate_run` attaches an explicit warning when
  `G-TRACE` passes vacuously over zero MVP requirements (D-017-1).
- Package-root resolution is layered — explicit `--package-dir` > `CLAUDE_PROJECT_DIR` >
  cwd — the bundled `.mcp.json` passes `${CLAUDE_PROJECT_DIR}`, and every `package_*`
  result echoes the resolved absolute root (C11: a stdio server's cwd is not guaranteed).

### Fixed
- Windows MCP deadlock (C11): pre-flight runs the frozen v1 validator **in-process**
  (no subprocess from the stdio server) with crash isolation; adopt's git spawn gets
  `stdin=DEVNULL`.
- `promoted_to` FK crash (C12): only `ADR-*` tokens qualify; mixed-token cells store NULL
  plus an unmapped note instead of killing the whole populate.
- Populate failures name the exact table/row/constraint and remove the created `data/`
  dir so retries are never blocked by a poison directory.
- `entity_upsert` documents the full-row requirement and names the actual cause when a
  partial update of an existing row fails NOT NULL.
- The plugin manifest version skew (installs self-identified as 1.0.0 since the v2.0.0
  release) — `plugin.json` now reads 2.1.0 and the sync is lint-enforced.

## [2.0.0] - 2026-07-18

The v2 re-architecture (MAJOR — the storage, interaction, and review contracts all changed; see
**Migration** below). Program record: `plans/`.

### Changed
- **Repository split (D-REPO-1..4):** this repository is **Tamheed** (`A-H-911/tamheed`), the
  successor of Keystone, carrying Keystone's full git history. The plugin bundle moved to
  `plugins/tamheed/` and the plugin/marketplace/skill identifiers renamed to `tamheed`. Install:
  `/plugin marketplace add A-H-911/tamheed` then `/plugin install tamheed@tamheed`; invoke as
  `/tamheed:tamheed`. The old install commands (`marketplace add A-H-911/keystone`) remain valid
  only for **Keystone 1.0.x** at the old repository, which is frozen for existing v1 packages.
- **Storage contract (D-STORE, ADR-0001):** a package is no longer loose Markdown + a state file —
  it is a **relational store**: one SQLite-enforced entity table per artifact family, serialized as
  deterministic canonical JSONL (`data/*.jsonl`, spec in `plugins/tamheed/db/CANONICAL.md`) that the
  operator commits to git. Statuses are three-axis (`lifecycle_status`/`verdict`/`disposition`);
  approval-bearing rows are trigger-enforced immutable-after-approval; derived artifacts are SQL
  views, never stored snapshots; a single-writer lockfile makes concurrent writers fail loud.
- **Interaction contract (D-MCP):** every write goes through the **Tamheed MCP server**
  (`plugins/tamheed/server/`, official Python SDK, launched via `uv`/PEP 723 or `pip install mcp`) —
  the only write path into a package and the successor of the v1 validator: referential gates
  (G-IDS, G-DEC-STATUS, G-REQ-SRC) are schema constraints enforced at write time, coverage gates
  (G-TRACE, G-SET, G-PROGRESS) are SQL views run by `gate_run`, and `handoff_emit` injection-screens
  every emission. Batch mutations are all-or-nothing with per-item verdicts; there is no raw-SQL tool.
- **Review contract (D-REVIEW):** the human review surface is **HTML only** — `export_html` renders
  the package (gate chips, registers, traceability, execution progress, gap/screening notes) as one
  self-contained, escaped, script-free, deterministic `review.html`, committed alongside the data.
  Derived-Markdown snapshots are gone (they are exactly what froze and misled in v1 field use).
- **Update mode is the agile heart (D-UPDATE):** diff-aware re-derivation (`trace_query` the impact
  set, regenerate only dependents), execution-progress sync (`progress_update`, `audit_record` with
  evidence refs, `work_bind` stamping `last_referenced`), and **typed scope changes**
  (defer/reschedule/reclassify/cancel/expand) — the `scope-change` row is written before any
  mutation, and iteration bumps track `introduced_in`/`retired_in`.
- **Python floor raised to 3.10** (ASM-D): the MCP server depends on the official `mcp` SDK
  (`requires-python >= 3.10`); the CI matrix drops 3.9 (now 3.10–3.12 × ubuntu/windows). The frozen
  v1 validator itself still runs on 3.9, but this repository gates on 3.10+.
- **CI rebuilt around one command** (B10): CI job 1 runs exactly `python check.py` — the seven test
  suites, the v1 goldens (0/0/1/1), structure lint (tracked JSON, registry↔DDL sync, v1
  Always-mirror↔catalog sync), a canonical-form round-trip of the committed v2 demo, and the
  deterministic eval runner on its sample fixture. A second ubuntu-only job smokes the uv/PEP 723
  server launch (skips visibly if uv is unavailable). The behavioral eval spec gained *executable*
  deterministic assertions run by `evals/run_evals.py`; assertions with no v2 mechanical equivalent
  are recorded as `retired`, never silently dropped.

### Added
- **`migrate` mode** (`package_migrate`, B5): staged, operator-initiated import of a conformant v1
  Keystone package — pre-flight against the frozen v1 validator, dry parse report, one-transaction
  populate, post-flight fidelity check. Runbook: `docs/migrate-from-keystone.md`; mapping contract:
  `plugins/tamheed/references/migration-v1.md`. A migrated golden ships at
  `generated-samples/support-triage-agent-v2/`.
- **`adopt` mode** (`package_adopt`, B11): staged brownfield onboarding for projects that never used
  Tamheed — nothing inferred is ever Approved, provenance is code-shaped (`source_kind='code'` with
  file:line spans), injection-shaped repo content is fenced as data, and the gap report (what code
  cannot reveal) is a first-class output.
- **Execution-tracking surface:** slices under phases, acceptance-criteria audit verdicts with an
  evidenced-vs-narrated split, defect and deferred-work registers, execution gates, per-slice
  execution plans, durable conventions, progress journal, work bindings (`work_bind`) stamping
  per-entity `last_referenced`, and cascade-on-transition (all ACs of a requirement Met ⇒ the
  requirement auto-advances, in the same transaction).

### Removed
- **The repository bootstrapper** (`init_skill_repo.*`, ASM-B) and with it the `--no-repo` flag:
  a package is data the operator commits to whichever repository they choose; storage
  initialization is the server's `package_create`. Provider neutrality survives in the plan itself
  (safeguard 15).
- **The v1 state file** (`keystone-state.json`): the package *is* the state — `resume`/`update` are
  `package_open` + targeted queries.
- **The chat-only generation path:** environments without an MCP host can hold the planning
  conversation but cannot create or mutate a v2 package.
- **Derived document snapshots** (traceability matrix, status report, readiness report, backlog,
  handoff manifest as files): all are views/queries now, rendered in `review.html`.

### Migration
- v1 packages are **not** read by v2 tools directly. Migration is **operator-initiated, staged, and
  gated** (D-REPO-5): Keystone hints once per session, never forces, and agents never auto-migrate.
  Run `package_migrate(source_dir)` for the preview, then `confirm=True` to populate; the frozen v1
  contract (validator, JSON schemas, templates) stays in this repository as read-only migration
  inputs. Full runbook: `docs/migrate-from-keystone.md`.
- Identifiers survive migration unchanged (`FR-001` stays `FR-001`); v1 document content lands as
  narrative documents + sections; register rows land in their entity tables with provenance intact.
- Anything a v1 package recorded that v2 models differently (e.g. handoff-manifest fields) is
  absorbed into the package row or entity columns — the migration report itemizes every mapping.

## [1.0.0] - 2026-06-22

First stable release. The methodology, schemas, identifiers, and handoff contract are now stable; future
changes ship with a migration note per the versioning rules in `references/governance.md`.

### Changed
- **Downstream executor is now Claude Code (no longer agent-neutral).** Keystone targets **Claude Code**
  (CLI/IDE; cloud coworker acknowledged) as the agent that implements the plans it produces, because
  Keystone is itself a Claude Code plugin. The handoff layer leans into Claude Code: the **agent-control
  surface** is now `CLAUDE.md` **importing** `AGENTS.md` (the file Claude Code auto-loads — Anthropic's
  documented idiom) instead of the prior "AGENTS.md-canonical + CLAUDE.md-shim" pair; the initial /
  follow-up / review prompt templates reference plan mode, TodoWrite, subagents, and a code-review pass
  where useful (named as capabilities, never hard-depended on). Safeguard 13 ("coupling to one agent")
  and the Warn gate `G-COUPLING` are reframed: coupling to Claude Code is now an intentional *harness*
  choice. Updated `SKILL.md`, `README.md`, `plugin.json`/`marketplace.json`,
  `references/{safeguards,quality-gates,handoff,prompt-templates,workflow,artifact-catalog,artifact-rules}.md`,
  `docs/{methodology,workflow}.md`, the handoff templates, and `init_skill_repo.py`.
- **The produced plan stays portable.** Requirements, architecture, and ADRs remain vendor-, provider-,
  and stack-neutral (safeguard 15); the bootstrap stays repo-provider-neutral (safeguard 14). The
  coupling is at the harness layer only, never the architecture.

### Migration
- Packages generated under ≤0.2.0 (AGENTS.md-canonical, agent-neutral handoff) remain valid — no schema,
  identifier, required-artifact, or handoff-manifest-shape change, so the validator accepts them
  unchanged. New packages emit a root `CLAUDE.md` containing `@AGENTS.md` as the loaded standing-context
  entry, plus Claude-Code-targeted handoff prompts. To bring an existing package forward, add a root
  `CLAUDE.md` whose body is `@AGENTS.md`.

## [0.2.0] - 2026-06-22

### Added
- **Execution-tracking layer (Tarseem-inspired).** New mechanical gate **`G-PROGRESS`** in
  `validate_package.py` (acceptance-audit coverage: when an audit is present, every `AC-` carries a verdict
  from {Met, Partial, Not-met, Pending}; SKIPs when no audit exists). New **acceptance audit**
  (`templates/acceptance-audit.template.md` — a derived close-out: criterion → verdict × evidence) and a new
  **agent-control surface** (`templates/agent-control.template.md` → package-root `AGENTS.md` + a `CLAUDE.md`
  shim, also emitted by `init_skill_repo.py`): the agent-neutral, ambient standing context (invariants +
  violation⇒ADR, hard constraints, conventions, and the tracking protocol). Evidence columns added to
  work-breakdown / status-report / acceptance-criteria; optional `evidence` on
  `acceptance-criterion.schema.json` and `acceptance_refs` on `execution-phase.schema.json`. Initial +
  follow-up handoff prompts gained the AC-first/test-first loop, the track-as-you-go cadence, and new
  situational prompts (phase-exit summary, acceptance audit, spike/experiment report, defect log). README
  flow diagram + `CLAUDE.md` + `quality-gates.md` updated (6 → 7 gates). (additive / MINOR)
- **Gate `G-SET`** in `validate_package.py`: every "Always" artifact must be present on disk or recorded in
  `manifest.json` `omitted_artifacts[]` with a reason; the manifest must exist; nothing it declares present
  may be missing. This closes the gap where a hollow package (charter + README only) passed validation
  because every other gate SKIPped on the absent input. Backed by the new
  `references/required-artifacts.json` (machine mirror of the Always class) and a new
  `tests/fixtures/incomplete-package/` regression fixture. (audit AUDIT.md F-01/F-05)
- **Continuous integration** (`.github/workflows/ci.yml`): runs the validator test suite and validates the
  golden packages (valid, invalid, incomplete, demo) on every push/PR across Linux + Windows × Python
  3.9–3.12. (audit F-02)
- **Behavioral eval harness** (`evals/evals.json`, `evals/README.md`, `.github/workflows/eval.yml`): five
  with-skill/without-skill scenarios including a prompt-injection case, plus a scheduled, non-blocking
  eval-spec lint. (audit F-03)
- **`SECURITY.md`**: trust model, untrusted-content posture, and vulnerability reporting. (audit F-04)
- **`init_skill_repo.py --layout plugin|classic`** (default `plugin`): scaffolds a self-contained plugin
  bundle (`marketplace.json` + `plugin.json` + `plugins/<name>/SKILL.md`) that installs as a Claude Code
  plugin with no restructuring; `classic` keeps the older `skill/` + `commands/` layout. (audit F-08)
- `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/install.md`, and `docs/design-decisions.md`.

### Security
- Treat the project brief and any file content as **untrusted data, not instructions** (OWASP LLM01): new
  operating principle 10 in `SKILL.md`, safeguard 18 in `references/safeguards.md`, and a handoff-screening
  step (`references/handoff.md`, gate `G-INJECT`). (audit F-04)
- `init_skill_repo.py` validates `--repo-name` as a single safe path segment and asserts the resolved target
  stays inside `--target-dir`, blocking path traversal (CWE-22). (audit F-09)

### Changed
- Repackaged Keystone as a self-contained **Claude Code plugin**. The skill and everything it reads or
  invokes at runtime (templates, schemas, scripts, the artifact catalog, logos) now live in one bundle at
  `plugins/keystone/`, and the repository is its own plugin marketplace (`.claude-plugin/marketplace.json`).
- Install is now one step in Claude Code (`/plugin marketplace add` → `/plugin install`); the bundle is also
  portable as a standalone Agent Skill.
- Reframed the "thin wrapper" principle for the plugin model (the skill is the entry point inside Claude
  Code; the principle still governs external CLI/API/MCP/UI entry points).
- `quality-gates.md`: added the `G-SET` row and corrected mechanization labels — `G-TRACE` is now "Partly"
  (its behavior-bearing → `AC-` clause is judgment, not mechanized) and `G-COMPLETE` no longer claims to
  verify required-set membership (that is `G-SET`). (audit F-05)
- `SKILL.md`: dropped the non-recognized `compatibility:` frontmatter key (its content moved to a body
  **Requirements** line) and fixed the "GitHub CLT" → "GitHub CLI" typo. (audit F-07/F-11)
- `references/extension.md`: refreshed the stale `commands/` entry-point reference. (audit F-10)
- **Migration (MINOR):** `schemas/package-manifest.schema.json` `generation.mode` now matches the skill's
  invocation modes (`full | intake | plan | resume | update | stage:<id>`) instead of the divergent
  `quick/standard/deep/research/update/resume` enum. A manifest that recorded a removed value
  (`quick`/`standard`/`deep`/`research`) must switch to a real mode; manifests that omit `mode` are
  unaffected. (audit F-06)

### Fixed
- Self-containment: removed dangling runtime references to repo-root docs and the obsolete "vendor step";
  corrected a stale traceability-schema filename reference.
- `init_skill_repo.py` no longer crashes with `UnicodeEncodeError` on Windows consoles using a legacy code
  page — stdout/stderr are reconfigured to UTF-8 at startup.

### Removed
- Build-history documents from the initial side-task context (`adrs/`, `IMPLEMENTATION-PLAN.md`,
  `NAMING-OPTIONS.md`, `CRITICAL-REVIEW.md`, `ROADMAP.md`, `ACCEPTANCE-CRITERIA.md`) and the redundant
  standalone `commands/keystone.md` wrapper. Durable design rationale was distilled into
  `docs/design-decisions.md`.

## [0.1.0] - 2026-06-18

### Added
- Initial Keystone capability: the methodology, skill specification (`SKILL.md` + references), governance
  model, artifact templates, JSON schemas, the repository-bootstrap script, the package validator with its
  self-test, worked examples, and a demonstration generated package.
