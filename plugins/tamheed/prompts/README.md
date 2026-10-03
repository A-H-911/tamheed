# How to use this folder — the `{package}` prompt guide (tamheed v5.8.1)

This folder holds the **project's own prompts** for the `{package}` Tamheed package, plus
this guide. Since v5.0.0 the stock scenarios are no longer files here. They are the tamheed
plugin's **slash skills**, `/tamheed:<name>`, updated with the plugin and never refreshed
per project. Two kinds of thing live in this folder:

- **This guide** (`README.md`), shipped by tamheed and refreshed on upgrade. `handoff_emit`
  with `refresh_stock=true` updates it when it is byte-equal to an older release's copy. A
  hand-edited copy is `customized` and never touched by refresh. ⚠ Customising it opts it
  out of every future refresh. The emission warning names how far the stock has since
  moved (`stock_last_changed`). To carry a release's improvements into a customised copy,
  hand-merge from the bundled `stock-history.json` and say so IN the file with a line
  `<!-- tamheed:stock-merged X.Y.Z -->`. The line is verified against the bundled history. Every
  line of release X.Y.Z must be present, and the emission names the releases whose lines are
  absent.
- **Your project prompts**, any other filename. They are operator-owned, and tamheed never
  touches them. Name them by purpose, kebab-case (`kickoff.md`, `phase3-resume.md`). The
  `prompt-ids-resolve` readiness rule scans them (never a stock body): every id written in
  them must resolve. Files named `prm-NNN-<kind>.md` with a `<!-- converted … -->` header
  are legacy prompts converted from the old database. They are audit names, not a pattern to copy.

**Leftovers from before v5.0.0.** A package created under 4.x still holds the sixteen
retired stock files (`slice-kickoff.md`, `progress-sync.md`, …). `handoff_emit` names each.
One byte-equal to a shipped release's stock is a `leftover_stale_stock`, and
`refresh_stock=true` removes it (reported as `retired`). That is the same proof today's refresh
relies on: you never customised it. A `leftover_customized` copy is never removed. Keep it
as a project prompt under a new name (the stock name is retired), or remove it yourself.

## Which skill, when

| Situation | Invoke |
|---|---|
| A brand-new agent has never seen this package | `/tamheed:package-onboarding` |
| Resuming after a session clear / compaction | `/tamheed:orient-resume` — the SessionStart hook has already printed the resume block. The skill reads the handoff first |
| Before a compaction, at session end, on a handover | `/tamheed:session-handoff` — the `handoff` journal entry, written LAST |
| Starting the next slice of work | `/tamheed:slice-kickoff` |
| Work is done, package not yet updated | `/tamheed:progress-sync` |
| A bug was found or reported | `/tamheed:defect-triage` |
| Work happened without recording (any session) | `/tamheed:drift-register` |
| A slice is believed complete | `/tamheed:slice-review` |
| A phase is believed complete | `/tamheed:phase-close` |
| Closing out a release | `/tamheed:release-close-out` |
| Deferred-work triggers may have fired | `/tamheed:replan-deferred` |
| Readiness advisories piling up (the amber list) | `/tamheed:register-liveness` — run it on a cadence, not only at close |
| Distilling confirmed lessons into a reusable skill | `/tamheed:skill-promote` — the operator-interview ceremony (project or user level) |
| Read-only trust audit of the package | `/tamheed:integrity-check` |
| Refresh + read the human report | `/tamheed:generate-report` |
| Unattended execution — the repeated prompt | `/tamheed:loop-iteration` |
| Unattended execution — the brake (read FIRST) | `/tamheed:loop-guard` |
| The record's prose breaks the plain-English rules (`prose-plain-english` names the texts) | `/tamheed:ste-rewrite` |
| Something project-specific | any other `.md` here — project prompts are operator-authored, purpose-named. Read the folder |

Every scenario skill is **operator-invoked** (`disable-model-invocation`). The agent never
starts a ceremony on its own, exactly as it never pasted one. Each works in the package this
project's `CLAUDE.md` note names, and an argument names another (`/tamheed:slice-kickoff other`).
Beside them, nine **discipline skills** are model-invoked (out of the `/` menu since v5.1)
in every session where the plugin is enabled. They are `tamheed:package-writes` (every write,
read and git crossing), `tamheed:reading-the-record` (before citing a row), and
`tamheed:written-claims` (before prose that states a mechanism or a count). Then
`tamheed:plain-english` (before any English a reader cannot question, v5.9) and
`tamheed:operator-interview` (at every STOP). Then `tamheed:test-evidence` /
`tamheed:measurement-evidence` / `tamheed:ci-evidence` (what a verdict's evidence must survive).
And `tamheed:session-handoff` (write the handoff LAST before a compaction, at session end or on
a handover). It also answers to `/tamheed:session-handoff`.
In a crowded host their descriptions may reach the model name-only. The tool results name the
one to invoke, so invoke it by name. `package_open`/`server_info` name `tamheed:package-writes`.
Every successful `entity_query` result names `tamheed:reading-the-record`. `readiness_check` names
`tamheed:operator-interview` on a blocking failure. `audit_record` names the evidence skill for
the verdict's method. A handoff write names `tamheed:session-handoff`. `handoff_emit` names
`tamheed:written-claims` whenever a scan found something to fix (v5.2). The plugin's SessionStart
hook prints the package's resume block (the latest handoff and what followed it) into every new
session, clear and compaction. `package_open` and `server_info` return the same block.

## Semi-auto style (you drive)

The typical loop: `/tamheed:orient-resume` → `/tamheed:slice-kickoff` → the agent works →
`/tamheed:progress-sync` → `/tamheed:slice-review` → next slice. Phase exits go via
`/tamheed:phase-close`, releases via `/tamheed:release-close-out`. Every **STOP for
approval** in these skills is real. The agent waits for your words. Three things are
always yours alone. **Scope changes**: the `SC-` row needs your approval before its changes
are applied and it is set Merged. **Waivers**: a `WVR-` row satisfying one named readiness
rule for one named entity. The agent may ask for one, never author one. **`force`**:
overriding a whole blocked `Implemented` transition past failing readiness rules.

## Fully-auto style (unattended)

Pair `/tamheed:loop-iteration` (the skill a loop repeats) with `/tamheed:loop-guard` (the
stop conditions, read it before starting any loop). Drive it either way:

- an **in-session loop** (for example Claude Code `/loop`) re-invoking `/tamheed:loop-iteration`.
- an **external harness** starting a fresh session per iteration
  (`claude -p "/tamheed:loop-iteration"`). It parses the final
  `ITERATION: wbs=… slice=… acs_moved=… gate=… ready=… stop=… lessons_pending=…`
  line to decide continue/stop, and watches the operator-interview queue grow.

The loop stops itself on any guard condition, and never restarts itself. The conditions are a
degraded gate, non-convergence, a needed scope change, or a blocking readiness failure at a
close. Also a defect spike, empty iterations, or any store error. You resolve, you restart.

## One session at a time

The package has a **single-writer lock** (`data/.lock`). Two sessions invoking skills
concurrently will collide. The second `package_open` refuses, naming the holder (pid,
host, taken_at) **and what the store observed about it**. The observation is `not-running`,
`reused` (the pid now belongs to another process), `alive`, or `unobservable`. After a crash or
a plugin reload the holder is usually gone. `package_unlock("{package}")` reports the
lock and the observation. `confirm=true` removes it and journals the removal,
**on the operator's words only**, and only for a holder observed dead. It refuses on
`alive` and on `unobservable` (another host, a container, access denied). Removing
`data/.lock` by hand stays the deliberate path for what this host cannot see.
Never auto-clear. When unsure, ask the other session's operator.

## Asking the operator

When a decision is the operator's (a verdict, a waiver, `force`, `package_unlock`, a
scope change, a lesson), START THE INTERVIEW. Do not report a blocker and wait
(`tamheed:operator-interview` is the full procedure).

1. **Do the homework first.** Never ask what the package or the repository already
   answers. The operator should be deciding, not researching.
2. **One decision per question**, in plain words, with a concrete example of what each
   option means in practice.
3. **Show the record with its id.** Quote what the row says (its text, severity,
   status) beside its identifier. An id alone makes them read the record. Content
   alone makes the claim uncheckable. Every family: `DEF-`, `DEC-`, `ADR-`, `AC-`, `DW-`…
4. **Ask every time.** An earlier answer is evidence about then, never consent for now.

## The standing rules

The **Recording obligations** table in this project's `CLAUDE.md` note binds every
session, prompted or not. Defects, deferred work, and scope changes are registered
BEFORE moving on. Verdicts carry evidence and its chain (`verified_by`,
`verification_method`, `against_commit`). Done-claimed is `Review`, verified is
`Implemented`. `readiness_check` runs before anything is declared done. The HOW is the
`tamheed:package-writes` skill. The rules it carries, in short, follow.

**Fixing a damaged field.** Build the payload from a read made FOR transmission: `entity_export`
to a file, or an `entity_query` result taken whole. No field is ever truncated: `total` tells you
about rows, `omitted_columns` about a projection. Never build it from a display, an excerpt or a
summary. Text that passed through a display is suspect wherever it came from. PASTE a generated
fix payload, never re-type it (the hand is the untrusted transport). End every multi-row fix with
an independent verifier: re-read through the tools and re-derive each expected value from its
source before calling the fix done.

**Lessons.** When execution teaches something durable, record a `lesson` row (`LL-`, born
Proposed). Its statement opens with the rule, because the note prints a statement's opening
only. Only lessons the OPERATOR approves bind future sessions. The CLAUDE.md note renders
the pinned ones and the 10 highest-numbered unpinned ones. The rest bind too and are read by
query. The agent never approves its own lesson. The store REFUSES an approving or promoting
upsert without `"operator_confirm": true`, your words, in every mode. Approved lessons with a
shared theme can be distilled into a SKILL (`/tamheed:skill-promote`) that Claude Code loads
natively. Promoted lessons graduate out of the note, and the skill file carries them. Past the
note's curation ceiling the `lessons-note-budget` advisory names the promotion candidates.

**Placeholders and the journal.** Entity prose is screened for placeholder tokens (G-COMPLETE).
To QUOTE a token like `TODO` in prose, wrap it in backticks. Journal text (progress entries,
verdict evidence) is exempt, because reports are never "unfinished". A `correction` entry
collapses its target under itself in review.html when it names one. The server's own
edge-retire `correction` row names no entry and folds nothing. The journal's server-appended
kinds (`forced-override`, `lesson-confirmed`, `lesson-promoted`, `integrity-verified`) are
REFUSED from `progress_update`. The server records those facts itself.

**Reading registers.** Registers are read THROUGH the tools, whatever their size.
`entity_query` cuts rows never fields, `total` is exact, and `after_id` pages (the result's
`next_after`). `ids=[...]` quotes a known set verbatim, and `search=` sweeps by keyword.
Reading `data/*.jsonl` to dodge a payload cap is drift. A committed script that must QUOTE the
store (a review slate, a docket, an evidence page) reads an `entity_export` file. The tool wrote
it under `exports/`, and the file is whole rows, digest-stamped, deterministic. Export immediately
before generating and cite the digest. Never reuse an export across sessions, and never
hand-paste rows into a script's input (the hand is the untrusted transport). A full-row update
that only flips a status names the columns it did not mean to change (`expect_unchanged`). So
the store refuses transport drift. A partial row still carries every NOT NULL column (a bare
`{id, pinned}` on a lesson is refused on its title).

**Feedback.** **A function the tools lack is a `feedback` row (`FB-`) first, never a script**
(v4.11). Record what you needed and what you did instead, born Proposed (`kind`:
`missing-capability`, `defect`, `doc-error` or `question`). The operator confirms it, then
`entity_export("feedback.json", args={"type": "feedback"})` carries it into the project's
findings. QUOTE the file's envelope and rows there (exports are point-in-time and may be
untracked in your git). A script the project keeps over the package is a `local-tool` row that
cannot be a draft. Interview the operator BEFORE the insert, because the word is its
precondition. The rule has two clauses: it writes nothing tool-owned, and if it reads the
STORE, it reads `exports/` only. `handoff_emit` names every row still awaiting the operator or
the export, and every reported row until it is answered. The `feedback-unanswered` advisory
lists the same rows. When the maintainer ships or answers it, set the row `Resolved` as a
PARTIAL row. Set `resolved_in` (the release, or the response to a question) and `upstream_ref`.
The partial row is id, kind, title and those three. Omitted columns are preserved, and their
absence from `changed_columns` proves it. The recipe needs no `expect_unchanged`, because naming
a column the row does not carry is refused, and the engine journals the move. A local-tool row
is a register: it never resolves.

**Fidelity and edges.** Apply `expect_unchanged` to every long row regardless of size.
Transcription fidelity does not degrade with length. Before recording a premise as untestable,
list the instruments. The SOURCE that generates an output is one, and an output-versus-output
frame hides it. A scope change that touches a RULING carries an `amends` edge (DEC-: merged by
full-row upsert, ADR-: by supersession). `Merged` is set LAST, after every delta row is applied
and re-read. Trace edges are keyed (from, to, relation), so a new relation never replaces an old
one. A WRONG edge is retired (`retire: true` on the trace-edge item, and the server journals it)
and the correct edge written in the same batch. Retire a wrong edge only, never to make a gate
pass. A remedy a tool's note or a release note names is always an operation the server exposes.
If you cannot find it, report that as a finding rather than improvising.

**The store on disk.** `package_verify()` proves the on-disk store is canonical (per-file
byte-equality, foreign files, a citable digest). `record=true` appends the server-witnessed
`integrity-verified` row, so journal a verification when the operator wants the record. Every
store write FLUSHES `data/*.jsonl`, and `export_html` / `handoff_emit` write package files
beside it. The store writes are `entity_upsert`, `progress_update`, `audit_record`, `work_bind`,
`package_verify(record=true)` and `package_close`. `work_bind` records a commit and
dirties the tree AFTER it. Run `git status --porcelain -uall` before any branch operation,
never a memory of having committed. The package is the record. When code and package disagree,
fix the code or record the change. Never let them drift.
