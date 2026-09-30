# Tamheed design decisions

The durable architectural decisions behind Tamheed, distilled for contributors. These are the choices a
maintainer needs to understand and preserve; the *process* history of how the capability was first built
(as Keystone) is not retained. Superseded decisions stay on record with a pointer to their successor —
supersede-don't-edit is the house rule here too. The enforceable contracts these decisions imply live in
[`../plugins/tamheed/references/extension.md`](../plugins/tamheed/references/extension.md) and
[`governance.md`](../plugins/tamheed/references/governance.md); the layering is in
[`architecture.md`](architecture.md).

## 1. The skill owns the capability; entry points are thin wrappers

All methodology — the 22 stages, intake, clarification, artifact selection, generation, quality gates, and
handoff — lives in the skill (`SKILL.md` + `references/`). Every entry point (a slash invocation, a CLI, an
HTTP API, an MCP server, a UI) only normalizes input to the skill's contract, invokes the skill, and routes
output; it carries no methodology or business logic. This keeps one authoritative implementation no matter
how Tamheed is invoked, and it is enforceable: gate **G-CMD-THIN** flags any entry point that smuggles
methodology in. (In the Claude Code plugin model, the skill itself is the entry point — there is no separate
command file — so the principle now governs *external* wrappers. The **MCP server is not an entry point**:
it is the capability's mechanical half — see decision 11.)

## 2. Markdown artifacts paired with JSON schemas *(superseded in v2 — see decisions 9–11)*

> **Superseded** by the relational package store (decision 9, D-STORE), the HTML-only review surface
> (decision 10, D-REVIEW), and MCP-only interaction (decision 11, D-MCP). Kept for the record: this
> dual-surface model is exactly what the v1 field evidence broke on — the human-editable Markdown and
> the machine-checked structure drifted apart, and derived documents froze on first generation.

Every artifact had a dual surface: human-readable **Markdown** (what people review and edit) and, where it
was structured, a machine-readable **JSON Schema** (`schemas/`) that the validator and state machine relied
on. This let humans work in prose while tools mechanically checked identifiers, statuses, and traceability.
The templates were the single source of truth for document shape; the schemas the single source of truth
for data shape. (The v1 schemas and templates survived in the bundle as the frozen migration contract
until they were **retired in v4.0.0** — the validator and schemas are gone; v1 packages take the two-step
escape route via tamheed 3.2.1.)

## 3. Provider-neutral repository bootstrap *(retired in v2 — ASM-B)*

v1 shipped a repository bootstrapper: local `git init` + scaffold, opt-in remote
creation. **Removed in v2**: a Tamheed package is data (`data/*.jsonl`) the operator commits to any
repository they choose, and storage initialization is the MCP server's `package_create` (see ADR-0001).
Provider neutrality survives where it matters — the plan couples to no repo host (safeguard 15,
G-COUPLING) — without Tamheed owning repository creation.

## 4. Derived traceability and persisted state *(state half superseded in v2 — decision 9)*

The traceability matrix (requirement → decision → task → test → risk → acceptance criterion) is a **derived**
artifact, regenerated rather than hand-edited, so it can never silently drift from the registers it links —
in v2 it is literally a query (`trace_query` / the matrix in `review.html`), never a stored snapshot. The v1
state file (`keystone-state.json`, machine-owned) is gone: **the package is the state** (decision 9) —
`resume`/`update` are `package_open` + `entity_query`, and there is no second store to reconcile.

## 5. Progressive-disclosure skill structure

The skill is a lean always-loaded `SKILL.md` front door plus a `references/` directory loaded only when the
work reaches the matching part. This keeps context usage low and the methodology navigable, and it sets the
extension pattern: add depth as a new reference file and register it, rather than bloating the front door.

## 6. Self-contained, single-unit packaging

Tamheed ships as one self-contained bundle (`plugins/tamheed/`) containing everything it reads or invokes
at runtime — references, section templates, the DDL + store, the MCP server, the artifact catalog, the
frozen v1 contract *(retired in v4.0.0 — the validator and schemas are gone; v1 packages take the
two-step escape route)*, and logos — with no outward references. This is required by Claude Code's plugin install semantics (the plugin directory is copied to a
cache, so files outside it would not travel) and it makes the bundle equally usable as a standalone Agent
Skill or a manual copy. It replaces the earlier "single source at repo root + vendor step" model, which had
no build and left runtime references dangling once installed.

## 7. The brief is untrusted data, not instructions

Tamheed ingests an external project brief and emits prompts another agent will act on — the canonical
prompt-injection shape (OWASP LLM01, direct and second-order). So the brief and any file content are treated
as **data to plan over, never commands**: verbatim brief text is quoted and provenance-labeled, an injected
directive is captured (and surfaced) rather than executed, and the assembled handoff is screened before emit
(gate `G-INJECT` in `handoff_emit`). v2 extends the same posture to **adopted repositories** (`package_adopt`
fences injection-shaped code content as data) and to the **review surface** (`export_html` escapes every
data-derived string; no data may become script). The contract lives in `SKILL.md` (operating principle 10),
`references/safeguards.md` (safeguard 18), and `references/handoff.md`; the overall posture is documented in
`SECURITY.md`.

## 8. Mechanical gates verify what is present *and* that what must be present is

The identifier/status/source/completeness/traceability gates check the internal consistency of whatever
artifacts exist. That left a gap: a package missing its core artifacts could pass, because each gate
SKIPped on the absent input. Gate **G-SET** closes it by requiring every **Always**-class artifact family
to be present or explicitly recorded as omitted *with a reason* — omission is a conscious, recorded act,
never a silent gap. In v1 the Always set was `required-artifacts.json` (retired with v1 ingestion in
v4, plan 031); since v2 it is the **`entity_types` registry** seeded into every package,
checked by the `g_set_failures` view and an `omissions` table whose reason column is NOT NULL. That
completeness discipline is what lets the "execution-ready" verdict be trusted. Deterministic checks stay
mechanical (schema + views + scans); judgment gates stay with the model and are recorded.

## 9. Relational package store: canonical text, SQLite runtime *(v2 — D-STORE, ADR-0001)*

A package is **one entity table per artifact family**, serialized as deterministic canonical JSONL
(`data/*.jsonl` — stable key order, PK-ordered rows, UTF-8, LF) that the operator commits to git, and
loaded into stdlib SQLite for every mutation. Field evidence from three real v1 deployments drove this:
registers rot, statuses stall, derived Markdown freezes on first generation, and every project hand-rolls
missing structure. In the store, statuses are three-axis (`lifecycle_status` / `verdict` / `disposition`),
derived views are queries that cannot go stale, approval-bearing rows are trigger-enforced
immutable-after-approval, and a single-writer lockfile makes concurrent writers fail loud. Full doctrine:
[`adr/adr-0001-v2-relational-package-store.md`](adr/adr-0001-v2-relational-package-store.md).

## 10. HTML is the only human review surface *(v2 — D-REVIEW)*

Humans never review raw JSONL, and v2 emits **no derived-Markdown snapshots** (they are exactly the
artifacts that froze in v1). `export_html` renders the whole package — gate chips, registers with
three-axis statuses and per-entity `last_referenced`, the traceability matrix, execution progress, and
gap/screening notes — as one self-contained static `review.html`: every data-derived string escaped, no
JavaScript, no data-derived links, a restrictive CSP, and **deterministic output** (same DB state ⇒
byte-identical file), so the export is committed alongside the data and its diffs are meaningful.
*(Since v4.12 the identity holds on one UTC date: the Readiness section states the date it was
evaluated on. See §19.)*

## 11. MCP-only interaction: the server is the capability's mechanical half *(v2 — D-MCP)*

Every write goes through the Tamheed MCP server (official Python SDK; launched via `uv`/PEP 723 with a
pip fallback) — `entity_upsert` batches are all-or-nothing with per-item verdicts, there is no raw-SQL
tool, and stored text is data, never instructions. The server is **not** an entry point under decision 1:
it is the successor of the v1 validator — the mechanical half of the capability, inside the boundary that
G-CMD-THIN protects. This is what moves the referential gates to write time (decision/gate mapping in
[`architecture.md`](architecture.md) §2) and gives the executing agent a governed write path for progress,
audit verdicts, and work bindings during execution.

## 12. D-V4 — the v4 entity-model re-baseline (2026-08-14)

v4.0.0 re-derived the entity model from first principles as one baseline schema — a systematic entity
study whose fifteen decisions (claimed-vs-verified `Review`, evidence-chained verdicts, waivers, typed
progress events, drift-delta scope changes, blocking G-REL, milestone demotion, and the rest) are recorded
in [`entities.md`](entities.md) §2. The full decision record is
[`adr/adr-0002-v4-entity-model-re-baseline.md`](adr/adr-0002-v4-entity-model-re-baseline.md). With it, the
v1 machinery (validator, importer, schemas) was retired; v1 packages take the two-step escape route via
tamheed 3.2.1.

## 13. D-RESUME — the resume surface rides on the journal, not on a state file (2026-09-26, v5.1)

The field's largest project carried "where the session stopped" in a 3,600-line kickoff prompt and
three hand-pointed journal ids, and its discipline skills never fired because a crowded host delivers
most skill descriptions name-only. v5.1 keeps the doctrine — the package IS the state — and gives that
state a typed home: a caller-written `handoff` journal entry (append-only; corrected, never edited),
returned by `package_open`/`server_info` as the `resume` block and printed by the plugin's
`SessionStart` hook as plain text (guarded, lockless, screened, capped, never able to fail the
session). The obligations table was NOT extended: the handoff duty is a sentence in the note and the
`handoff-current` advisory, so the note marker stays `v5` and every project's AGENTS copy stays
lint-identical. The discipline skills leave the `/` menu and the phase-start tool results name the
skill to invoke — a name works for the model even when its description did not arrive. The
alternatives rejected: a state file (the v1 mistake), an engine-managed live-state span in AGENTS.md
(a committed copy that goes stale between emits), a PreCompact hook (it cannot inject; exit 2 blocks
compaction), and JSON hook output (the plugin path's bug history). Record: plan
[`120-128-batch-findings-32.md`](../plans/120-128-batch-findings-32.md).

## 14. Four rulings from the first field round on the resume surface (2026-09-26, v5.2)

The field ran v5.1 for a day and returned three defects and a measurement. Each ruling below was
taken against evidence read at the path, not from the report.

- **D-STOCK-BODY — a `stock-merged X.Y.Z` marker claims the whole body of X.Y.Z.** The v5.1 check
  verified only the lines X.Y.Z added over the previous release, so a marker over a body three
  releases older passed as soon as the newest increment alone was merged (38 of 62 lines absent,
  `verified: true`). Every line of the declared body is required now, and each absent line is
  attributed to the release that introduced it. Rejected: "increments only, both counts shown"
  (never fails a partial merge) and "every increment from the first release" (demands lines a later
  release removed). The check stays report-only because a customisation that rewrites stock lines
  reads as absent — the marker states what the claim would need, not that the customisation is wrong.
- **D-STALE-HOME — the stale-warning block lives beside the note, never in a file the tool does not
  own.** In the pointer-import case v5.1 appended it to the root `CLAUDE.md` while the emission's own
  warning said the root was untouched; it goes into the package's `CLAUDE.md` now, the warning names
  the block's add/remove apart from the span, and removal is tail-aware so a stale → clean cycle is
  byte-neutral. The block's text names the scan's scope (agent-control, prompt and skill files).
- **D-CUES-2 — a tool result is the cue; the note is not.** Measured: no discipline skill loaded
  without a tool result naming it, and the always-loaded note naming all eight cued nothing. v5.1's
  "phase-start tools only" ruling was revisited on that evidence: every successful `entity_query` result names
  `reading-the-record` (the row arrives with its cue), and `handoff_emit` names `written-claims`
  exactly when a scan found something to fix; the `entity_export` file, a script's input, never
  carries a cue. Rejected: naming skills on write results (the cue arrives after the write) and
  leaving the two skills to the note alone (measured insufficient).
- **D-SKILL-GUARD — the engine witnesses a skill row's moves.** A retirement (Obsolete +
  `upstreamed_to`) was the one lifecycle move with no `system:` row; the field wrote its record by
  hand. Now a `transition` signed `system:skill-guard` records a status change or a pointer's
  arrival — never the insert (the promotion ceremony journals `lesson-promoted`), never an idle
  re-send — and it counts toward `handoff-current` like every transition, which is why the
  `session-handoff` skill orders the close-out: status moves, the handoff, the commit, the bind.

Also decided without a diagram: the AGENTS template points at the note's obligations table instead
of carrying a twin (one copy, no drift); the hook prints 25 lines / 4,000 characters of the entry
(= the resume block's own cap); `lessons-stranded` measures the Promoted lessons; the brief to a
field project is a committed file read by path, after paste damage in two consecutive cycles. Record:
plan [`129-135-batch-findings-33.md`](../plans/129-135-batch-findings-33.md).

## 15. Four rulings from the second field round on the resume surface (2026-09-27, v5.3)

The field's second day on the surface (ACMP `findings_34`) returned no defect: every predicted class
held, and what came back was seven brief errors, one contested docs claim, one friction and the
residue of the carried rules. The rulings (R15–R18):

- **D-LOCK-OBSERVED — the resume block says what the store observed about the holder.** After a
  Claude Code process restart the hook read "lock file present (pid …)" and the agent needed
  `package_unlock` to learn the pid was dead. The block now carries `observed` + `evidence` from the
  same seam `package_unlock` reads; the hook prints the observation and the operator's remedy. A lock
  held by the very session that asks reads `alive` / `held by this session` with no probe — three of
  the block's four callers hold the lock themselves. Nothing is removed by a read.
- **D-HOOK-LOG — an opt-in, counts-only trace.** The field could not tell "the hook did not fire on
  `/reload-plugins`" from "it fired and its output was not delivered" (one reload delivered the block
  on 5.1.0; two delivered nothing on 5.2.0; every restart and compaction delivered it). When
  `TAMHEED_HOOK_LOG` names a file the operator created, the hook appends one line per run — source,
  line and character counts, status — never the entry; a missing path gets nothing, because a
  project's settings `env` block could otherwise aim the hook at any writable file. The docs stop
  calling the reload a mechanism: a session restart is the route the block arrives by every time.
  > **Correction, 2026-09-27 (v5.4, §16 D-RELOAD-MEASURED).** "One reload delivered the block on
  > 5.1.0" is false: that delivery was a Claude Code restart across a build change, 37 seconds
  > after the reload. No reload has been observed to run the hook.
- **D-RENDER-HINT — binding is not rendering, and the write says so.** Thirteen unpinned approvals
  moved every lesson the note showed behind "19 more"; the approval's `next` had said "binds once the
  note is rebuilt" and nothing about the roster. The hint now names the rule (pinned always; unpinned
  only among the 10 newest Approved) — the roster rule itself is unchanged: pinning is the operator's
  curation tool.
  > **Correction, 2026-09-27 (v5.5, §17 D-TWO-WORDS).** The 5.3.0 hint named the roster and kept
  > its first clause, which still gated BINDING on the rebuild. Since 5.5.0 it reads that a lesson
  > binds from the write and is rendered only once the note is rebuilt.
- **D-RESIDUE — a partial rule's generic remainder enters the skill, one sentence each.** The field's
  re-read of the 113 carried rules (95 quotes verified) found 26 partial; twelve carry a stack-neutral
  remainder no skill stated, each re-read at the rule's own text. Thirteen sentences entered six
  discipline skills (plan 137); the other fourteen partials and the 34 project rules stay the field's.

Also decided without a diagram: `entity_query`'s cue rides every SUCCESSFUL result — a usage error is
the caller's misuse, and "no such record" is an empty success, which is where the cue matters; the
brief carries classes only, line counts included (its "21 lines" came from a copy; the field read 19);
the next Q1 is measured in the first normal-work session that has read no brief. Record: plan
[`136-140-batch-findings-34.md`](../plans/136-140-batch-findings-34.md).
> **Correction, 2026-09-27 (v5.4, §16 D-Q1-RETIRED).** That measurement cannot be made where the
> note names the skills, which is every project since 5.0.0. Q1 is retired.

## 16. Seven rulings from the third field round on the resume surface (2026-09-27, v5.4)

The field's day on 5.3.0 (ACMP `findings_35`) returned no defect and no feedback row. What came
back: a trace line nobody could attribute, four brief errors, the operator's standing rule on
recommendations, and a recipe caution. The rulings (R19–R26; R19 is the version):

- **D-TRACE-SESSION — the trace line names the session that wrote it.** A headless session another
  tool started in the project folder printed the same block, so its line equalled the operator
  session's replay to the character; a verdict about the operator's session was read from it and
  reached a journal entry, a report and a memory file. The remedy removes the condition rather
  than teaching around it: the line ends `session=<id>`, the event's own `session_id` and the
  transcript's file name. Measured before the edit: a headless run on 2.1.283 delivers
  `session_id` on `SessionStart`'s stdin, equal to the run's id. Not added: the working directory
  and the entrypoint — the transcript named by the id carries both, and the entrypoint variable is
  undocumented for hooks. Both stdin fields pass one token rule; anything else is written `-`.
- **D-HEADLESS-PRINT — the hook prints in every session.** Six headless sessions in two days each
  received the field's resume block. No documented field separates a summariser from a headless
  worker that needs the block (a request to document such a signal was closed as not planned), so
  the hook does not guess: it prints, and the docs say so. No opt-out variable either — it would
  work only if the tool that starts the session set it.
  > **Correction, 2026-09-27 (v5.5, §17 D-WHO-WRITES).** "Every session" is too wide. The hook
  > prints in every session that LOADED the plugin. Sessions a tool started through the Agent
  > SDK's Python entry loaded none on the measured machine, and a session started before an
  > upgrade keeps the hook it loaded until a reload or a restart.
- **D-RELOAD-MEASURED — a plugin reload runs no `SessionStart` hook.** 24 reloads on builds
  2.1.261–2.1.283, in three sessions of one project, and no `SessionStart` event of any plugin's
  hook after any of them; each of 19 compactions ran them. The one delivery this record carried
  (§15) was a restart: the reload's rows are on build 2.1.282, the `SessionStart:resume` 37 seconds
  later is the first row on 2.1.283. One separate observation, not a mechanism: the first
  `SessionStart` after the 5.3.0 reload ran the 5.3.0 hook with no restart between.
  > **Correction, 2026-09-27 (v5.5).** That observation is documented behaviour: Claude Code's
  > plugin loading reference says a reload switches hooks to the new version's path. That a
  > reload fires no `SessionStart` stays a measurement; no page states it.
- **D-Q1-RETIRED — "does a cue ALONE load a skill" is not a question a project can answer.** The
  note has named the discipline skills since 5.0.0 and the hook's last line names one; the note,
  the hook and the cue are designed to work together, and no project runs a cue without them.
- **D-RECOMMEND-DEFAULT — an option set carries one recommendation, marked as the agent's.** The
  operator sent bare options back twice asking for one and then made it standing; the rule it
  replaced had lived in memory and was cited to a decision whose text never stated it. The skill's
  default flips (the planning reference already offered a recommended default with each
  question); a recommendation is never a verdict or an approval; a standing instruction on how to
  ask is a decision row in the operator's words, and it is not a banked answer.
- **D-TREE-CHECK — the install check is a documented recipe.** On Windows the marketplace clone
  checks out with CRLF and a byte compare read every file different. The recipe compares through
  git or on LF-normalised bytes. Not built: a forced line ending for the bundle (a renormalisation
  of every clone) and a bundle digest in `server_info` (a new surface and a new release step for
  what one command does).
- **D-REVIEW-NO-LOCK — `review.html` renders no lock.** The lock's holder is run-time state; the
  export is deterministic from stored text and the date of the export, and it runs under the
  exporting session's own lock, so the line could only ever read "held by this session".

Two lessons of the round entered `measurement-evidence` (a match on value attributes nothing when
another producer can write the same value; every item differing is as suspect as none). Owned by
the maintainer: the brief's trim recipe could not run on Approved lessons and had never been run
on the copy; a prediction named a moving row. From this round a brief's every recipe runs on the
copy first, and a prediction names a role ("the latest handoff"), never an id. Record: plan
[`141-145-batch-findings-35.md`](../plans/141-145-batch-findings-35.md).

## 17. Nine rulings from the fourth field round (2026-09-27, v5.5)

The field's day on 5.4.0 (ACMP `findings_36`) returned no defect and no feedback row. Every
predicted class held, and the `session=` tail told two sessions apart that had printed one block 75
seconds apart. What came back: one false docs sentence, three brief errors, and two rounds lost to
the note's render rule. The maintainer's review of its own plan found a fourth thing the field had
not reported: the bundle defined "binds" two ways. The rulings (R27–R35; R27 is the version):

- **D-TWO-WORDS — the status binds; the note's roster is what is rendered.** `governance.md` said
  status is the single truth for what binds. `reading-the-record` (5.2.0) said the roster binds,
  "never a lesson's register status", a sentence absorbed from a field rule about an emit that ran
  two days late. The field followed the skill and recorded a lesson pushed out of the roster as one
  that "no longer binds", which the operator had never said. One word cannot carry both: a status
  the operator alone moves, and a roster an approval of another row changes. **Binds** is the
  status, from the write that approves it, retired only on the operator's word. **Rendered** is
  the roster: every pinned Approved row and the 10 highest-numbered unpinned ones, rebuilt only by
  the emit. A lesson outside the roster still binds and is read only by query. Three engine
  strings moved: the approval hint's first clause, the note's footer (the rows behind it "bind too
  and are not rendered here"), and the note-budget advisory. Lint 13 refuses a sentence that gates
  binding on the emit or the roster. Rejected: the roster binds — an eleventh unpinned approval
  would unbind the oldest with no word from the operator, against the 2026-09-21 ruling that what
  binds is retired on the operator's word.
- **D-NOTE-ROSTER-COLUMN — the review page marks what the next emit renders.** Its fold had listed
  every Approved lesson under "rendered into the CLAUDE.md note"; in the field 30 were listed and
  10 rendered. The server computes the roster with the helper the note itself uses and passes the
  ids; the page imports nothing. The column is computed from the store, so it says "at the next
  emit": the note on disk differs until an emit has run, and a blocked emit renders nothing. Not
  built: a read of the note on disk — the emit's target is the caller's, and the exporter does not
  know it.
- **D-WHO-WRITES — who writes a trace line is stated as a count.** The 5.4.0 guide said every
  session in an enabling project appends a line. Measured: every interactive and headless
  command-line session that loaded the plugin did; over six hundred sessions started through the
  Agent SDK's Python entry listed no plugin to their models and wrote none. Their transcripts hold
  no hook row of ANY event, so "ran no hook" cannot be read from them; the listing is the
  instrument that can. No cause is stated: whether an SDK session loads settings is its caller's
  choice. A hook run with no output leaves no transcript row.
- **D-RULE-FIRST — a lesson's statement opens with its rule.** The note prints the statement
  flattened, whole at 180 characters or fewer and cut to its first 177 above that. The field
  worked the cut out of the server's source twice. The two numbers are named constants now, and a
  test reads them back out of the shipped text.
- **D-APPROVAL-COST — an approval's cost is stated in the question.** Three cases: the
  highest-numbered unpinned approval pushes the lowest of the ten out; a pinned approval pushes
  nothing out; an unpinned approval numbered below the ten is never rendered.
- **D-DISCHARGE — an obligation is discharged in the family that made it.** The 5.4.0 brief
  retired a question by a correction on the handoff that named it. The recipe had run clean on a
  copy. The question also stood as a clause of an approved ruling, and the field wrote a new
  ruling. A dry-run proves a write lands; it cannot prove the write discharges what is owed.
- **D-NO-RESULT-KEY — no tool result gains a key.** Considered: a lesson write returning its note
  line, and an approval naming the row it pushes out. The second arrives after the operator has
  ruled. The rule is one sentence an agent can apply before the question, and the review page
  shows the outcome.

Owned by the maintainer: the roster sentence shipped in 5.2.0 against `governance.md`, with no
check to see it; the false trace sentence, written by the 5.4.0 sweep; the 5.4.0 brief's sweep of
the field's memory files only, which is how the question's second carrier was missed; and four
statements in this round's own plan that direct inspection overturned. Record: plan
[`146-150-batch-findings-36.md`](../plans/146-150-batch-findings-36.md).

## 18. Nine rulings from the fifth field round (2026-09-28, v5.6)

The field's day on 5.5.0 (ACMP `findings_37`) returned no defect and no feedback row. Every
predicted class it could exercise held. What came back: two brief errors, one question no
instrument could answer, and three practices of the field's own that the skills did not yet
state. The maintainer's review found a fourth thing the field had not reported: four step lists
export the review page before their last journal write. The rulings (R36–R45):

- **D-TRACE-VERSION — the trace line names the hook that wrote it.** The hook's two files are
  byte-identical at the 5.4.0 and 5.5.0 tags, and a running session keeps the hook it loaded, so
  the field could not say which hook had written a line. The line opens `<utc> version=<x>`, read
  from the bundle's manifest by the hook itself, before any note is looked for: the hook imports
  the server only once a note is found, and a silent line must carry the version too. The value
  passes the token rule the session id passes. **The placement departs from a common convention**
  for `key=value` lines, which appends a new key at the end: the tail is documented in two
  releases, pinned by four assertions, and taught to the field as its instrument. The cost is a
  reader that takes `source=` by position. Rejected: the version in the resume block — it would
  move every session's character count for a fact the agent reads from `server_info`.
- **D-EXPORTED-BY — the review page names the release that exported it.** `review_current`
  compares the digest stamped in the page with the store's. After the upgrade it read true over a
  page with no roster column. The export stamps `<meta name="tamheed-version">` beside the digest,
  through the same `replace`, so the page module still imports nothing from the server; the stamp
  is a constant of the release, no clock and no counter, so two exports stay byte-identical.
  `package_verify` reports it as `review_exported_by`, `None` with no stamp. Rejected:
  `review_current` going false on a page another release exported — thirteen lab lines and the
  contract test read it as "the page's data is current", and every upgrade would read stale.
  The key is not called "rendered by": v5.5 gave that word to the note's roster. A custom meta
  name is the HTML Standard's own allowance ("Anyone can create and use their own extensions to
  the predefined set of metadata names"), and it is read by an exact pattern.
- **D-EXPORT-BEFORE-COMMIT — the commit is the anchor, not the ceremony.** Any store write makes
  the page stale. `session-handoff` said to write the handoff after the export; `phase-close`
  exported before its closing entry, `release-close-out` before its bind, `skill-promote` before
  its closing note. The field's handoff commit carried a page without its handoff. One rule, in
  `package-writes`: the export precedes the commit that carries the page, and `package_verify`
  reads `review_current: true` right before it; after a bind the order is bind, export, commit
  both, and that commit stays unbound. Rejected: "no write follows the export" — a bind names a
  commit and must follow it. Not built: a lint that reads step order.
- **D-WORD-RULING — a ruling that changes a word is swept by the word.** The field covered
  fourteen dated rows with one reading rule in a decision row and reworded its live files. The
  maintainer's sweep for the brief had matched five phrasings: it passed a memory line that
  negated the verb and never opened the kickoff prompt. `written-claims` says: every form of the
  word, word-bounded, every hit read, in every file a session reads before acting.
- **D-CARRIED-LINE — a carried handoff line is re-measured or marked carried.** Two handoffs named
  a change request that had been closed and replaced. The skill's rule on live numbers covered
  figures, not a thing outside the store.
- **D-LINT-NEGATED — lint 13 refuses the negated shape.** A memory line of the field's negated
  the verb and gated it on the emit, and the v5.5 shapes passed it. The window stops at a full
  stop, a semicolon and a colon: its first form hit a correct sentence joined to a clause about
  the note. The lint refused this very entry in its first wording, which quoted the line.
- **Not absorbed (R40).** A clause on the provenance of a ruling that arrived in a document, and
  a clause that a failed prediction is reported as measured: each was one field instance, and
  `operator-interview` and `measurement-evidence` already carry most of it.
- **Not built.** A hook that walks up to find the note from a subfolder; a vocabulary scan at
  emit; a line-ending pin for the bundle — a pull rewrites only the files it changes, so an
  installed tree would hold mixed endings for a release.
- **Not studied this release (R42): the review page's weight.** The field's page is 14.5 MB,
  9.0 MB of it the registers. The ruling was given on the maintainer's sentence that the field
  had reported no cost. The sweep for the brief then found a field memory line of 2026-08-05
  that records pushes timing out and names the page, then 3 MB, as the cause. No findings file
  carried it, and the maintainer had not swept the field's memory before asking. The question
  was put again before the tag, with the line quoted and the moved premise named, and the
  operator answered "R42 stands, the brief asks ACMP to measure (Recommended)" (R45). The
  brief asks the field three questions, each with its instrument.

Owned by the maintainer: the 5.5.0 brief's sweep, which matched phrasings and read no prompt;
its ninth class, which the brief's own close-out order made impossible; a question asked before
its instrument was named; and, in this round's own plan, a rule that could not be satisfied, a
count that was wrong, a claim that a review tool was unavailable after one failed call, and an
option put to the operator on a premise the field's own memory contradicts.
Record: plan [`151-155-batch-findings-37.md`](../plans/151-155-batch-findings-37.md).

## 19. Five rulings from the sixth field round (2026-09-28, v5.6.1)

The field's day on 5.6.0 (ACMP `findings_38`) returned no defect and no feedback row. Every
predicted class held, and the field numbered no brief error. What came back was smaller than in
any earlier round: one condition the field added to a class of the brief, one misuse it classed
as its own, and two sentences its advisor corrected in a handoff draft. The maintainer's review
found the larger thing behind the misuse. The rulings (R46–R50):

- **D-LIMIT-ORDER — a limited read returns the lowest ids.** `entity_query` returns rows in the
  id's text order and `limit` cuts from the lowest. Three teaching texts had called a read
  limited to ten rows "the last recorded activity" since 2026-07-22. The field typed an id into
  `after_id` to mean "from this entry on", the same misreading. Run over the real journal ids,
  the engine's order returns the ten lowest on the lab and on the field. The rule now stands in
  the tool's description and in `package-writes`, with what to read instead: the resume block's
  last entries, the `handoff-current` list read with `ids`, `audit_evidence` and `acs-met`.
  Rejected: number order in `entity_query` — a contract test pins text order over ids of mixed
  width, and the cut and the order must share one collation for a paged walk to be complete.
  **Not built: a `newest` parameter.** No tool returns the last rows of a family, and the skill
  says so; a hand-made method would be misused as the old line was.
- **D-UNBOUND-BY-RULE — the close-out's last commit is no drift.** v5.6 anchored the export on
  the commit, which leaves one commit unbound at every close-out: the one that carries a bind
  with the exported page. Three audit lists called an unbound commit drift and carried no
  discriminator, and one of them runs unattended. They now point at the classifying rule of
  `package-writes`, which names that commit. Not built: a lint over the lists.
- **D-PAGE-DATE — the page's identity holds on one date.** Since v4.12 the Readiness section
  states the UTC date it was evaluated on, because two of its rules read the calendar. Four
  sentences went on promising the same bytes from the store's state alone, one of them "no wall
  clock". The field supplied the missing condition in its own prediction. The sentences are
  corrected, and a test pins that two dates over one store differ in the date and nowhere else.
  `review_current` compares the store's digest and is unaffected. Rejected: a date derived from
  the store's last write — the section would then disagree with `readiness_check` run today.
  The exporter already takes the date as an input, which is the practice the Reproducible
  Builds project describes for a build's clock.
- **D-HANDOFF-TENSE — a handoff says what is true when it is written.** Since v5.6 its commit,
  the bind and the export follow it. A draft in the field said a branch was pushed through
  commits that did not exist yet.
- **D-AUDIT-WRITES-NOTHING — the read-only audit exports outside the repository.** Its staleness
  step ran a bare export, which rewrites the package's committed page and `csv/`. The
  instrument is kept, the newest stored timestamp of every table, and the file goes to the
  system's temporary folder.

The release is a PATCH. The repo's texts name what a MINOR adds — an entity type, a template, a
gate, a profile, a diagram kind, an entry point — and this release adds none; Semantic
Versioning defines a patch as a change that "fixes incorrect behavior". The case against was
named at the approval: two of the sentences are new rules.

Owned by the maintainer: the three teaching lines, two months old; the four sentences on the
page's bytes; a class of the 5.6.0 brief with a condition missing; an absence claim that rested
on a copy blind to ignored files; the 5.6.0 order rule, shipped without a sweep of the lists
that read binds; and, in this round's own plan, a count that was too low, a test weaker than its
claim, a false "only", and a tool's result described as more than it returns.
Record: plan [`156-159-batch-findings-38.md`](../plans/156-159-batch-findings-38.md).

**A correction of §19, dated 2026-09-29.** D-LIMIT-ORDER says the rule "now stands in the
tool's description". It stood in `entity_query`'s docstring, which no client receives: the
server registers the second element of each `TOOLS` entry. The rule reached sessions through
`package-writes` and the other teaching texts, never through the tool. §20 records what changed.
The same entry lists number order in `entity_query` as rejected, for two reasons. §20 answers
both and reverses it.

## 20. Five rulings from the seventh field round, the closing one (2026-09-29, v5.7)

The field's session on 5.6.1 (ACMP `findings_39`) returned no defect, no feedback row and no
numbered brief error. Every class held. It reported one read worth more than the rest: a typed
`after_id` that had dropped three matching entries on 2026-09-11 with no sign in the result.
The maintainer's review added a census of the field's 5,226 tool calls and one error of its own,
the largest of the round. The rulings (R51–R55):

- **D-ONE-ID-ORDER — the query tool takes the review page's order.** The page has ordered ids
  by prefix, then the id's first number, then the id since plan 057. `entity_query` ordered the
  same families as text. It now orders and cuts by the page's rule, and one function serves
  both: it lives in the server and the page imports it. §19 rejected this for two reasons.
  *A contract test pins text order*: the test described the old behaviour and argued nothing
  for it. *The cut and the order must share one collation for a walk to be complete*: true, and
  met. The cut is the order's own comparison. It is written as three OR branches over the
  tuple (prefix, number, id) and not as a row-value comparison, so a reader finds no tuple in
  the statement. SQLite computes the bound's prefix and number with the order's expressions;
  Python computes no key, because a second implementation could part from SQLite's cast on a
  string no family holds. **The ceiling:** only an id's first number counts, and what follows
  it orders as text, so under one leading number a dotted id's tenth part precedes its second.
  The page has always ordered them so. Rejected: full natural order, which would move the
  committed page of every package that holds such ids. Not built: a descending read (R50
  stands). Unchanged: the canonical JSONL and the CSV, which are committed bytes, and the
  eleven id lists of the gates and the readiness rules, which choose no rows.
- **D-REFUSE-THE-UNKNOWN-KEY — a journal tool refuses what it does not take.**
  `progress_update` and `audit_record` read the keys they knew and dropped the rest. In the
  field one write lost its attributes on a result that said `ok`. An item that is no object,
  an item with a key outside the list, and an item without a key the store requires are now
  refused by name, before any insert. The refusal adds no rule of its own: an empty entry is
  a value, and a vocabulary is the store's check to refuse. A null optional key means an
  absent one. Rejected: a typed item schema, which would put the keys where the SDK refuses
  them. The contract suite runs without the SDK, so nothing in the gate would test that
  refusal. Not built: the valid set in the "unknown columns" message, whose last refusal in
  the field was on 2026-09-21.
- **D-DESCRIPTION-IS-REGISTERED — what a client reads is the registered text.** The server
  passes the second element of each `TOOLS` entry to the SDK as the tool's description. A
  docstring is the maintainers' text. Since v4.4 the changelog had credited docstrings with
  teaching sessions, and v5.6.1 shipped a rule in one and called it the description. Three
  tools now register a short contract: the order for `entity_query`, the item keys for the two
  journal tools, each built from the constant the refusal reads. The client's cap is 2,048
  characters, so the texts are short and lead with what matters. The selftest compares what
  the SDK lists with the registry, in CI and wherever the suite runs with the SDK present.
  Not built: contracts for the other sixteen tools, and server instructions, a field the
  server has never set. **Corrected 2026-09-30 (v5.8, the field's FB-026):** "what a client
  reads" is what the client RECORDED when it first loaded the tool. Claude Code keeps that
  record through a `--resume`; a new session, `/clear` or a compaction reads the server's
  current text. The 5.7.0 brief's class 9 said "after the reload" and read false in the
  field's resumed session (§21, D-RESUME-KEEPS-THE-RECORD).
- **D-REPORT-A-FAILURE — the field reports what fails, through the package.** Seven rounds
  asked the field for a report after each release. From this release a brief lists the
  classes with their conditions, the field checks them in an ordinary session, and a class
  that fails becomes a feedback row: written `Proposed`, confirmed on the operator's word.
  No report is asked when nothing fails.
- **D-CENSUS-HORIZON — a count over a pruned store names its horizon.** The harness sweeps
  old session records. Four counts of the same folders in two days read 685, 673, 667 and
  678, the third taken by the field and the first three with the same count of calls.
  `measurement-evidence` says what to state beside such a count. No number of days is taught:
  the vendor's own sentence on the sweep was not located, only reports in its tracker.

The release is a MINOR. A public result's order changes, two tools grow stricter and three
descriptions grow. None touches the store's shape, the identifier scheme or the handoff
contract, which are this repo's triggers for a MAJOR. The case against was named at the
approval: a caller that relied on text order, or that passed an ignored key, meets a change.
The repo's suites hold no such caller; the field held one such write.

Owned by the maintainer: the rule shipped in a docstring and called delivered; a census that
counted any read with `after_id` as safe and never looked inside the class; the recommendation
to leave `after_id` to teaching, one round before the field measured the drop; the 5.6.1
brief's row that left out `csv/`; a front door that named a key loosely; and, in this round's
own plans, the docstring error repeated, a pattern search called a census, and "no committed
byte moves" said of a release that reorders an exported file.
Record: plan [`160-164-batch-findings-39.md`](../plans/160-164-batch-findings-39.md).

## 21. Three rulings from the eighth field round, on two feedback rows (2026-09-30, v5.8)

The field ran 5.7.0 and, by D-REPORT-A-FAILURE, wrote no report: two feedback rows came
back, both questions on the operator's word (`FB-026`, `FB-027`), and one of its own defects
measured the review page's history as the whole cost of its secret scan. Three rulings
(R56–R58) on 2026-09-30; the record is `plans/165-169-batch-fb026-fb027.md`.

- **D-HANDOFF-REPEATED — the engine names the handoff lines carried unread.** FB-027: a line
  marked `carried, not re-measured` travelled eight handoffs after the operator had answered
  it, under a rule that was followed — the mark moved the re-measurement onto the next
  reader, who carried it again. Teaching alone had lost, so the ruling is a rule and the
  teaching: `readiness_check` names, by line number, the lines of the latest handoff that
  stood word for word through three handoffs in a row, with the handoff each first stood in;
  the skill says a carried line names its source and the date last measured, and that the
  mark lasts one handoff. Two constants from one project's 18 handoffs: three handoffs (both
  lost lines are named at the third, two days before the field's sweep) and twenty
  characters (keeps every awaiting item the field wrote, drops the headings, which end with
  `:`). The ceiling, said in the rule's note: it reads wording, never truth; a reworded line
  resets it — on the field's own case the verdicts line is named at three of its eight
  positions because its punctuation moved twice. It reads handoff entries and not their
  correction chain, so a retracted line that is still repeated counts. Why an advisory and
  not the hook: the field reads `readiness_check` at every close-out, before it writes the
  next handoff, which is the moment; the hook's caps and screen stay untouched. Why the name:
  `deferred-work-carried` already means a `carries` edge, and the rule reads repetition.
  Each entry is read to the resume block's own cap, so the journal's size bounds the cost.
- **D-ONE-ROW-PER-LINE — the review page is a diff-friendly file.** The field's `DEF-224`
  measured `review.html`'s history as the cost of a 15–32 minute secret scan (8m37s at two
  CPUs against 14.4 s without it) and, under `ADR-0052`, skips the page's past versions. The
  cause was the generator's: table rows and graph elements joined with no newline, so the
  page held four lines of 840–912 KB — both graphs and the journal table twice — each
  carrying a stamp or a count that moves on every export, about 4 MB of patch text each
  time; gitleaks reads `git log -p`, and a scanner that reads patches pays for every changed
  line's bytes. The fix is a newline between rows, between SVG siblings, after a fold's
  summary and after a section's freshness paragraph — nowhere inside an inline run, a cell,
  a `<text>` or the handoff's `<pre>`. Measured in git on a fresh field copy: the first
  export re-flows the page once (26,395 added, 2,005 removed, 20 MB); the next export after a
  journal write is 20 added, 17 removed, 34 KB. Proven the same page: equal bytes once the
  newlines between tags are removed, and in a browser equal elements, rows, paths, text,
  height and pixels. Not built: a smaller page (the journal renders twice by design,
  `DEC-236` d4's weight), a stable graph geometry (a new node moves its neighbours: 1.3 MB on
  the field's `3a6dd21b`), any change to `csv/` or the JSONL. Tamheed recommends no scan
  narrowing; the install guide reports the field's route as the field's own decision.
- **D-RESUME-KEEPS-THE-RECORD — a client shows the description it recorded.** FB-026: the
  5.7.0 brief's class 9 read false in a session resumed after the update — it listed the
  5.6.1 texts while the wire and a fresh client listed 5.7.0's. Measured on 2,122
  transcripts: Claude Code writes a `deferred_tools_record` when a tool is first loaded; a
  tool was recorded again 936 times after a compaction and 5 times without one; 100
  re-selects of an already-recorded tool in the same context, 12 after a `--resume`,
  re-recorded it 0 times. The vendor's docs state nothing on it. So the docs say "a context
  that loaded the tool after the update" and, by ruling R58, nothing in the engine changes:
  the record is the client's. Not built: `server_info` returning the descriptions.
- **The number.** A new advisory in `readiness_check`'s output and a new page layout, and
  two descriptions reworded to name their argument: MINOR. No store shape, identifier or
  handoff-contract change; no migration.

Owned by the maintainer: the 5.7.0 condition "after the reload", written without measuring
a resumed session while the maintainer's own session held such a record (O18); the decline
of a design-record note on the page's weight on the field's "not a cost today", one day
before the field measured the cost, which was the generator's (O19); the 5.7.0 brief's
optional generator check, never run (O20). Record: plan
[`165-169-batch-fb026-fb027.md`](../plans/165-169-batch-fb026-fb027.md).
