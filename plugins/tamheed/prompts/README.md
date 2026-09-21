# How to use this folder — the `{package}` prompt guide (tamheed v4.10.0)

This folder is the **single prompt surface** for the `{package}` Tamheed package. Every
file is a paste-ready prompt for a Claude Code session. Two kinds live here:

- **Stock scenarios** (this file and the 16 named below) — shipped by tamheed, refreshed
  on upgrade; if you hand-edit one, later refreshes report it `diverged` and never
  overwrite without `force`. Since v4.1 the tool tells the two divergence kinds
  apart against its shipped stock history: a file byte-equal to an OLDER release's
  stock is `stale-stock` (you never customised it) — `handoff_emit` with
  `refresh_stock=true` updates ONLY those; a `customized` file is never touched by
  refresh (per-file acceptance stays delete + re-emit; `force` still overwrites
  ALL diverged). ⚠ Customizing a stock prompt therefore opts it out of every future
  refresh, silently and permanently — the emission warning names how far the stock
  has since moved (`stock_last_changed`); to carry a release's improvements into a
  customized copy, hand-merge: the bundled `stock-history.json` holds every
  release's body, so extract the current one and diff against your copy. When the merge
  is done, say so IN the file — a line `<!-- tamheed:stock-merged X.Y.Z -->` naming the
  release you merged — and the lag warning stops for that file (reported as your
  declaration, never verified).
- **Your project prompts** — any other filename. Operator-owned; tamheed never touches
  them. Name them by purpose, kebab-case (`kickoff.md`, `phase3-resume.md`). Files named
  `prm-NNN-<kind>.md` with a `<!-- converted … -->` header are legacy prompts converted
  from the old database — audit names, not a pattern to copy; review each (keep the
  project-specific parts, drop what the stock library now covers) and remove the header
  line when done.

## Which prompt, when

| Situation | Paste |
|---|---|
| A brand-new agent has never seen this package | `package-onboarding.md` |
| Resuming after a session clear / compaction | `orient-resume.md` |
| Starting the next slice of work | `slice-kickoff.md` |
| Work is done, package not yet updated | `progress-sync.md` |
| A bug was found or reported | `defect-triage.md` |
| Work happened without recording (any session) | `drift-register.md` |
| A slice is believed complete | `slice-review.md` |
| A phase is believed complete | `phase-close.md` |
| Closing out a release | `release-close-out.md` |
| Deferred-work triggers may have fired | `replan-deferred.md` |
| Readiness advisories piling up (the amber list) | `register-liveness.md` — run it on a cadence, not only at close |
| Distilling confirmed lessons into a reusable skill | `skill-promote.md` — the operator-interview ceremony (project or user level) |
| Read-only trust audit of the package | `integrity-check.md` |
| Refresh + read the human report | `generate-report.md` |
| Unattended execution — the repeated prompt | `loop-iteration.md` |
| Unattended execution — the brake (read FIRST) | `loop-guard.md` |
| Something project-specific | any other `.md` here — project prompts are operator-authored, purpose-named; read the folder |

## Semi-auto style (you drive)

The typical loop: `orient-resume` → `slice-kickoff` → the agent works → `progress-sync`
→ `slice-review` → next slice (phase exits via `phase-close`, releases via
`release-close-out`). Every **STOP for approval** in these prompts is real — the agent
waits for your words. Three things are always yours alone: **scope changes** (the
`SC-` row needs your approval before its changes are applied and it is set Merged),
**waivers** (a `WVR-` row satisfying one named readiness rule for one named entity —
the agent may ask for one, never author one), and **`force`** (overriding a whole
blocked `Implemented` transition past failing readiness rules).

## Fully-auto style (unattended)

Pair `loop-iteration.md` (the prompt a loop repeats) with `loop-guard.md` (the stop
conditions — read it before starting any loop). Drive it either way:

- an **in-session loop** (e.g. Claude Code `/loop`) re-pasting loop-iteration;
- an **external harness** starting a fresh session per iteration and parsing the final
  `ITERATION: wbs=… slice=… acs_moved=… gate=… ready=… stop=… lessons_pending=…`
  line to decide continue/stop (and to watch the operator-interview queue grow).

The loop halts itself — never restarts itself — on any guard condition: a degraded gate,
non-convergence, a needed scope change, a blocking readiness failure at a close, a
defect spike, empty iterations, or any store error. You resolve, you restart.

## One session at a time

The package has a **single-writer lock** (`data/.lock`). Two sessions pasting prompts
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
scope change, a lesson — START THE INTERVIEW; do not report a blocker and wait.

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
`Implemented`; `readiness_check` runs before anything is declared done. Repairing a damaged
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
with a shared theme can be distilled into a SKILL (`skill-promote.md`) that Claude Code
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
mean to change (`expect_unchanged`) so the store refuses transport drift; apply it to
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
files, a citable digest; `record=true` journals it on the operator's words). Recording
FLUSHES `data/*.jsonl` after the commit it records (`work_bind`, the closing
`progress_update`, `export_html`, `handoff_emit`) — `git status --porcelain -uall`
before any branch operation, never a memory of having committed. The package is the
record — when code and package disagree, fix the code or record the change; never let
them drift.
