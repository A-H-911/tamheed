# How to use this folder — the `{package}` prompt guide (tamheed v4.14.0)

This folder holds the **project's own prompts** for the `{package}` Tamheed package — plus
this guide. Since v5.0.0 the stock scenarios are no longer files here: they are the tamheed
plugin's **slash skills**, `/tamheed:<name>`, updated with the plugin and never refreshed
per project. Two kinds of thing live in this folder:

- **This guide** (`README.md`) — shipped by tamheed and refreshed on upgrade (`handoff_emit`
  with `refresh_stock=true` updates it when it is byte-equal to an older release's copy; a
  hand-edited copy is `customized` and never touched by refresh). ⚠ Customising it opts it
  out of every future refresh — the emission warning names how far the stock has since
  moved (`stock_last_changed`); to carry a release's improvements into a customised copy,
  hand-merge from the bundled `stock-history.json` and say so IN the file with a line
  `<!-- tamheed:stock-merged X.Y.Z -->` (reported as your declaration, never verified).
- **Your project prompts** — any other filename. Operator-owned; tamheed never touches
  them. Name them by purpose, kebab-case (`kickoff.md`, `phase3-resume.md`). The
  `prompt-ids-resolve` readiness rule scans them (never a stock body): every id written in
  them must resolve. Files named `prm-NNN-<kind>.md` with a `<!-- converted … -->` header
  are legacy prompts converted from the old database — audit names, not a pattern to copy.

**Leftovers from before v5.0.0.** A package created under 4.x still holds the sixteen
retired stock files (`slice-kickoff.md`, `progress-sync.md`, …). `handoff_emit` names each:
one byte-equal to a shipped release's stock is a `leftover_stale_stock` and
`refresh_stock=true` deletes it (reported as `retired` — the same proof today's refresh
relies on: you never customised it); a `leftover_customized` copy is never deleted — keep it
as a project prompt under a new name (the stock name is retired), or delete it yourself.

## Which skill, when

| Situation | Invoke |
|---|---|
| A brand-new agent has never seen this package | `/tamheed:package-onboarding` |
| Resuming after a session clear / compaction | `/tamheed:orient-resume` |
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
| Something project-specific | any other `.md` here — project prompts are operator-authored, purpose-named; read the folder |

Every scenario skill is **operator-invoked** (`disable-model-invocation`): the agent never
starts a ceremony on its own, exactly as it never pasted one. Each works in the package this
project's `CLAUDE.md` note names; an argument names another (`/tamheed:slice-kickoff other`).
Beside them, five **discipline skills** load on relevance in every session where the plugin
is enabled: `tamheed:package-writes` (every write, read and git crossing),
`tamheed:reading-the-record` (before citing a row), `tamheed:operator-interview` (at every
STOP), and `tamheed:test-evidence` / `tamheed:measurement-evidence` / `tamheed:ci-evidence`
(what a verdict's evidence must survive).

## Semi-auto style (you drive)

The typical loop: `/tamheed:orient-resume` → `/tamheed:slice-kickoff` → the agent works →
`/tamheed:progress-sync` → `/tamheed:slice-review` → next slice (phase exits via
`/tamheed:phase-close`, releases via `/tamheed:release-close-out`). Every **STOP for
approval** in these skills is real — the agent waits for your words. Three things are
always yours alone: **scope changes** (the `SC-` row needs your approval before its changes
are applied and it is set Merged), **waivers** (a `WVR-` row satisfying one named readiness
rule for one named entity — the agent may ask for one, never author one), and **`force`**
(overriding a whole blocked `Implemented` transition past failing readiness rules).

## Fully-auto style (unattended)

Pair `/tamheed:loop-iteration` (the skill a loop repeats) with `/tamheed:loop-guard` (the
stop conditions — read it before starting any loop). Drive it either way:

- an **in-session loop** (e.g. Claude Code `/loop`) re-invoking `/tamheed:loop-iteration`;
- an **external harness** starting a fresh session per iteration
  (`claude -p "/tamheed:loop-iteration"`) and parsing the final
  `ITERATION: wbs=… slice=… acs_moved=… gate=… ready=… stop=… lessons_pending=…`
  line to decide continue/stop (and to watch the operator-interview queue grow).

The loop halts itself — never restarts itself — on any guard condition: a degraded gate,
non-convergence, a needed scope change, a blocking readiness failure at a close, a
defect spike, empty iterations, or any store error. You resolve, you restart.

## One session at a time

The package has a **single-writer lock** (`data/.lock`). Two sessions invoking skills
concurrently will collide: the second `package_open` refuses, naming the holder (pid,
host, taken_at) **and what the store observed about it** — `not-running`, `reused`
(the pid now belongs to another process), `alive`, or `unobservable`. After a crash or
a plugin reload the holder is usually gone: `package_unlock("{package}")` reports the
lock and the observation, and `confirm=true` removes it and journals the removal —
**on the operator's words only**, and only for a holder observed dead. It refuses on
`alive` and on `unobservable` (another host, a container, access denied): deleting
`data/.lock` by hand stays the deliberate path for what this host cannot see.
Never auto-clear; when unsure, ask the other session's operator.

## Asking the operator

When a decision is the operator's — a verdict, a waiver, `force`, `package_unlock`, a
scope change, a lesson — START THE INTERVIEW; do not report a blocker and wait
(`tamheed:operator-interview` is the full procedure).

1. **Do the homework first.** Never ask what the package or the repository already
   answers: the operator should be deciding, not researching.
2. **One decision per question**, in plain words, with a concrete example of what each
   option means in practice.
3. **Show the record with its id.** Quote what the row says — its text, severity,
   status — beside its identifier. An id alone makes them fetch the record; content
   alone makes the claim uncheckable. Every family: `DEF-`, `DEC-`, `ADR-`, `AC-`, `DW-`…
4. **Ask every time.** An earlier answer is evidence about then, never consent for now.

## The standing rules

The **Recording obligations** table in this project's `CLAUDE.md` note binds every
session, prompted or not: defects, deferred work, and scope changes are registered
BEFORE moving on; verdicts carry evidence and its chain (`verified_by`,
`verification_method`, `against_commit`); done-claimed is `Review`, verified is
`Implemented`; `readiness_check` runs before anything is declared done. The HOW is the
`tamheed:package-writes` skill; the rules it carries, in short: repairing a damaged
field? Build the payload from a read made FOR transmission — `entity_export` to a file,
or an `entity_query` result taken whole (no field is ever truncated: `total` tells you
about rows, `omitted_columns` about a projection) — never from a display, an excerpt or
a summary: text that passed through a display is suspect wherever it came from. PASTE a
generated repair payload, never re-type it (the hand is the untrusted transport), and end
every multi-row repair with an independent verifier: re-read through the tools and re-derive each
expected value from its source before calling the repair done. When execution teaches
something durable, record a `lesson` row (`LL-`, born Proposed) — only lessons the
OPERATOR approves bind future sessions (rendered into the CLAUDE.md note, pinned first);
the agent never approves its own lesson — the store REFUSES an approving or promoting
upsert without `"operator_confirm": true`, your words, in every mode. Entity prose is
screened for placeholder tokens (G-COMPLETE): to QUOTE a token like `TODO` in prose,
wrap it in backticks; journal text (progress entries, verdict evidence) is exempt —
reports are never "unfinished" — and a `correction` entry collapses its target under
itself in review.html when it names one (the server's own edge-retire `correction` row
names no entry and folds nothing). The journal's server-appended kinds (`forced-override`,
`lesson-confirmed`, `lesson-promoted`, `integrity-verified`) are REFUSED from
`progress_update` — the server records those facts itself. Approved lessons
with a shared theme can be distilled into a SKILL (`/tamheed:skill-promote`) that Claude Code
loads natively — promoted lessons graduate out of the note, the skill file carries them;
past the note's curation ceiling the `lessons-note-budget` advisory names the
promotion candidates. Registers are read THROUGH the tools, whatever their size:
`entity_query` cuts rows never fields, `total` is exact, `after_id` pages (the result's
`next_after`), `ids=[...]` quotes a known set verbatim, `search=` sweeps by keyword —
reading `data/*.jsonl` to dodge a payload cap is drift. A committed script that must
QUOTE the store (a review slate, a docket, an evidence page) reads an `entity_export`
file the tool wrote under `exports/` — whole rows, digest-stamped, deterministic; export
immediately before generating and cite the digest, never reuse an export across
sessions, never hand-paste rows into a script's input (the hand is the untrusted
transport). A full-row update that only flips a status names the columns it did not
mean to change (`expect_unchanged`) so the store refuses transport drift — and a partial
row still carries every NOT NULL column (a bare `{id, pinned}` on a lesson is refused on
its title). **A function the tools lack is a `feedback` row (`FB-`) first, never a script**
(v4.11): what you needed, what you did instead, born Proposed (`kind`:
`missing-capability`, `defect`, `doc-error` or `question`) — the operator confirms it, then
`entity_export("feedback.json", args={"type": "feedback"})` carries it into the
project's findings: QUOTE the file's envelope and rows there (exports are point-in-time
and may be untracked in your git). A script the project keeps over the package is a
`local-tool` row that cannot be a draft — interview the operator BEFORE the insert; the
word is its precondition. The rule has two clauses: it writes nothing tool-owned; if it reads the STORE, it reads `exports/` only.
`handoff_emit` names every row still awaiting the operator or the export, and every reported
row until it is answered (the `feedback-unanswered` advisory lists the same rows). When the
maintainer ships or answers it, set the row `Resolved` with `resolved_in` (the release, or the
response to a question) and `upstream_ref` as a PARTIAL row — id, kind, title and those three:
omitted columns are preserved, their absence from `changed_columns` proves it (the recipe
needs no `expect_unchanged` — naming a column the row does not carry is refused), and the engine
journals the move. A local-tool row is a register: it never resolves.
Apply `expect_unchanged` to
every long row regardless of size — transcription fidelity does not degrade with
length. Before recording a premise as untestable, list the instruments: the SOURCE that
produces an output is one, and an output-versus-output frame hides it. A scope change that touches a
RULING carries an `amends` edge (DEC-: merged by full-row upsert; ADR-: by
supersession); `Merged` is set LAST, after every delta row is applied and re-read.
Trace edges are keyed (from, to, relation), so a new relation never replaces an old
one — a WRONG edge is retired (`retire: true` on the trace-edge item; the server
journals it) and the correct edge written in the same batch; retire a wrong edge
only, never to make a gate pass. A remedy a tool's note or a release note names is
always an operation the server exposes — if you cannot find it, report that as a
finding rather than improvising.
`package_verify()` proves the on-disk store is canonical (per-file byte-equality, foreign
files, a citable digest; `record=true` appends the server-witnessed `integrity-verified` row —
journal a verification when the operator wants the record). Every store write (`entity_upsert`,
`progress_update`, `audit_record`, `work_bind`, `package_verify(record=true)`, `package_close`)
FLUSHES `data/*.jsonl`, and `export_html` / `handoff_emit` write package files beside it —
`work_bind` records a commit and dirties the tree AFTER it: `git status --porcelain -uall`
before any branch operation, never a memory of having committed. The package is the
record — when code and package disagree, fix the code or record the change; never let
them drift.
