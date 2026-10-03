# Tamheed architecture

How Tamheed is *structured* so it can be invoked many ways without ever duplicating its logic. One principle
governs everything:

> **The skill owns the capability; every entry point is a thin wrapper.**

A slash invocation, a CLI, an HTTP API, a UI — each only normalizes input and routes output; none
re-implements the methodology. This is enforceable (gate **G-CMD-THIN**); the contract lives in
[`../plugins/tamheed/references/extension.md`](../plugins/tamheed/references/extension.md). See also
[`design-decisions.md`](design-decisions.md), [`methodology.md`](methodology.md) (what the capability is),
[`workflow.md`](workflow.md) (the staged process), and the in-bundle artifact catalog at
[`../plugins/tamheed/references/artifact-catalog.md`](../plugins/tamheed/references/artifact-catalog.md).

## 1. Layering

```
   ENTRY POINTS   slash · CLI · HTTP API · UI               (thin wrappers, NO methodology)
                        │  normalize to the input contract + a mode
                        ▼
   SKILL          the tamheed skill — THE CAPABILITY'S JUDGMENT HALF (single source of truth)
                  SKILL.md + references/ (workflow, governance, gates, intake, clarification,
                  artifact-rules, traceability, handoff, prompt-templates, state, extension…)
                        │  every write is an MCP tool call:
                        ▼
   MCP SERVER     the capability's MECHANICAL HALF (successor of the v1 validator)
                  entity_upsert · entity_query · trace_query · gate_run · handoff_emit ·
                  progress_update · audit_record · work_bind · package_migrate · package_adopt ·
                  export_html · package_verify · entity_export — the ONLY write path into a
                  package (and the read path: a committed script quotes an exports/ file)
                        │  loads / writes back
                        ▼
   PACKAGE STORE  SQLite runtime (schema-enforced) ⇄ canonical JSONL (data/*.jsonl, committed)
                        │
                        ▼
   OUTPUT         an execution-ready package + emitted handoff + review.html
```

The dependency arrow points one way: entry points depend on the skill; the skill depends only on the
server and templates bundled *with it*; nothing depends on a particular entry point. Add a wrapper and the
skill is untouched.

**The MCP server is not an entry point.** That distinction is doctrine (ADR-0001): the server is the
mechanical half of the capability itself — where the referential quality gates live as schema constraints —
exactly as `validate_package.py` was the mechanical half of v1. G-CMD-THIN governs *wrappers*; the server
is inside the capability boundary.

## 2. The three-tier gate mapping (ADR-0001)

v1 ran seven file-scanning gates after generation. v2 moves each gate to the earliest layer that can own
it (full table: [`../plugins/tamheed/references/quality-gates.md`](../plugins/tamheed/references/quality-gates.md)):

| Tier | Gates | Mechanism | When it fires |
|---|---|---|---|
| **Referential** | G-IDS, G-DEC-STATUS, G-REQ-SRC | FOREIGN KEYs + the `entity_index`; CHECK status enums; NOT NULL provenance | **At write time** — a violating `entity_upsert` fails with the constraint named; these defects are unrepresentable in a stored package |
| **Coverage** | G-TRACE, G-SET, G-PROGRESS, G-REL | SQL views (`g_trace_failures`, `g_set_failures`, `g_progress_failures`) + the `RELATION_RULES` edge-typing scan (G-REL — wrong edges are also rejected at write time) | On `gate_run` (stages 19/22, and any time) |
| **Content / judgment** | G-COMPLETE (mechanical scan), G-INJECT (emission screen), G-CONFLICT, G-EXEC, G-HANDOFF, G-OQ + the Warn gates | `gate_run`'s content scan; `handoff_emit`'s injection screen; recorded judgment | `gate_run` / `handoff_emit` / stages 19+22 |

The consequence: the strongest gates stopped being *checks* and became *properties*. There is no window
where a package can hold a dangling reference, a `Draft` decision, or an unsourced requirement — the write
that would create one fails, and the error message is the gate report.

Above the gates sits the **readiness layer**: `readiness_check(scope, id?)` answers "is this actually
done?" at a close boundary — `Review` counts as open (claimed is not verified), open critical/high defects
block while medium/low advise, and a stubborn failure passes only through an operator-approved `WVR-`
waiver (reported as `waived`, expiring, never silent); since v4.14 `ready` is false while any
blocking rule is `indeterminate` — the tool now agrees with its own review page, whose per-slice
panel had always called an empty slice "not ready" — and `indeterminate` names the rules.
Alongside the blocking rules run twenty
package-scope liveness advisories — from overdue open questions to `lessons-confirmed`, which nags while
any lesson recorded by the executing agent still awaits the operator's confirmation interview, and
`lessons-note-budget`, which names the lessons rendering past the always-loaded note's curation
ceiling as promotion candidates (pinning stays the operator's choice; its cost stops being invisible). The same
guarded-transition doctrine that reserves `force` for the operator's explicit words also guards lesson
binding: `entity_upsert` refuses any write landing a lesson in `Approved` or `Promoted` unless the item
carries `"operator_confirm": true` — operator-words-only, content byte-identical to the stored row,
attribution (`confirmed_by`) on the same write — and the server appends the typed
`lesson-confirmed`/`lesson-promoted` journal event itself. Promotion is where the package's memory turns
procedural: an operator interview distills Approved lessons into a **skill** (`SKL-` row + a written
`SKILL.md` the executing harness auto-loads), completing the episodic → declarative → procedural chain
(journal → lessons → skills).

The journal itself distinguishes what a caller reports from what the server witnessed: the four
server-appended kinds (`forced-override`, `lesson-confirmed`, `lesson-promoted`, `integrity-verified`)
are refused from `progress_update` (v4.5), so a narrated "confirmed" or "verified" can never be
journaled by hand. The caller-written `handoff` kind (v5.1) is the journal's newest use: where a
session stopped, returned as the `resume` block and printed by the SessionStart hook (§4 below), with
the `handoff-current` advisory naming a handoff the journal has moved past and `handoff-repeated` (v5.8)
naming the lines of the latest one carried word for word through three handoffs. And the store's byte-stability guarantee — an idle open→close is a zero-diff — is
exercised on demand by **`package_verify`**: the canonical round-trip reported per file, foreign files
in `data/` named, an unloadable store reported as a finding, memory compared to disk when the package
is open, and a sha256 digest of the canonical files that `record=true` journals as a citable fact
(tamper-evidence proper — a hash chain, signatures, an external anchor — is deliberately out of scope).
The read side matches: `entity_query` pages (`after_id`/`next_after`), fetches known sets (`ids`), and
sweeps by keyword (`search`), so a register of any size is reachable through the tool and the files
stay what they are — the canonical form, never the read path. Since v5.7 it orders ids by the
review page's rule — prefix, then the id's first number — and the two are one function. **What a
client knows of a tool is its registered description**, the second element of the server's `TOOLS`
entry; a docstring reaches no client, and the client caps a description at 2,048 characters. Three
tools register a contract there (`entity_query`, `progress_update`, `audit_record`), and the selftest
compares what the SDK lists with the registry. A committed script that must quote
the store byte-exact — a review slate, a docket — has the same rule and its own route (v4.7,
findings_24): **`entity_export`** writes a read tool's whole result to a deterministic,
digest-stamped JSON file under `<package>/exports/`, and the script quotes from that file; the
digest names the state the rows came from, so a slate's currency is one `package_verify` away.
The same file is how a project talks BACK to the plugin (v4.11): what the tools lack, and what
the project built instead, is an `FB-` row, confirmed by the operator, exported into the
project's findings, and collected by the maintainer — never a side utility over `data/`.

```mermaid
flowchart LR
    A["agent meets a missing function\nor would build a script"] -->|entity_upsert FB- Proposed| P[(package)]
    P -->|handoff_emit names it| O{operator}
    O -->|operator_confirm + confirmed_by| C[FB- Confirmed\njournaled system:feedback-guard]
    C -->|entity_export feedback.json| E[exports/feedback.json]
    E -->|inside findings_N.md| M[maintainer]
    P -->|feedback-unanswered + handoff_emit\nname it until resolved_in is set| M
    M -->|a plan, a release - a PARTIAL row:\nid, kind, title, status, resolved_in, upstream_ref| R[FB- Resolved\nresolved_in]
    O -.->|a local tool: confirmed before it exists,\nwrites nothing tool-owned; reads the store via exports/ only| T[scripts/gen-*.mjs]
```
On the write side, `expect_unchanged` lets a full-row status flip name the columns it did not
mean to change, and the store refuses transport drift (the field's LL-063: a paragraph lost
mid-paste with `ok: true`). The one departure from whole-row replacement (v4.12, the field's
FB-004) is the `substitute` item: one exact token in one column, which the server materializes
onto the stored row and then judges by the ORDINARY path — the same guards, triggers and
`changed_columns` — so there is no second write contract to guard. The header row (`title`,
`mode`, `iteration`, `entry_point`, `go_no_go`, `mvp_definition`) is written the same way,
`entity_upsert(type="package")`, with the go/no-go verdict on the operator's word (FB-001) —
presence-checked since v4.13: naming the verdict at all is the operator's act. Two things the
field found in v4.12's first week and v4.13 closes: a replacement that contains its needle is
refused when already present (a second run would compound), and `expect_unchanged` treats an
omitted column as what it is — preserved by the UPDATE, never drift — and (v4.14) refuses a named
column the item does not carry, the guard the field found could only pass.
On the read side, `search` with `context=N` is a census — the `occurrences` key, counts and
snippets per column (FB-003) — and `prompt-ids-resolve` scans the project's own prompt files for phantom ids
(FB-002), never a stock body.

## 3. The three actors

Three parties touch a package across its life, all through the same MCP boundary:

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Human operator
    participant Planner as Planning agent (tamheed skill)
    participant Server as Tamheed MCP server
    participant Executor as Executing agent (Claude Code)

    Operator->>Planner: project brief (untrusted data)
    Planner->>Operator: batched clarification questions
    Operator-->>Planner: answers + scope approval (gate)
    Planner->>Server: package_create · entity_upsert (registers, narratives, trace edges)
    Server-->>Planner: per-item verdicts (referential gates enforced at write time)
    Planner->>Server: gate_run
    Server-->>Planner: gate report (coverage views + content scan)
    Planner->>Operator: readiness verdict + open items (go/no-go gate)
    Operator-->>Planner: GO
    Planner->>Server: handoff_emit(target project)
    Server-->>Executor: executor-side .mcp.json + the CLAUDE.md note (v5: obligations + lessons, pointing at the plugin's skills) + the prompts guide
    Executor->>Server: progress_update · audit_record (evidence refs) · work_bind
    Note over Server: cascade-on-transition: all ACs of a requirement Met ⇒ requirement auto-advances
    Executor->>Server: entity_export(path, tool, args) — before a review slate is generated
    Server-->>Executor: exports/<file>.json (whole rows, digest-stamped) — a committed script quotes from it, never from data/
    Operator->>Server: export_html
    Server-->>Operator: review.html — the committed human review surface
    Operator->>Planner: scope change (update mode)
    Planner->>Server: decision + scope-change row FIRST, then mutations (iteration+1)
```

The operator never proofreads JSONL: human review happens through `review.html` — since v4.12 with a
Readiness section and a Feedback section beside the registers, and since v5.5 with each Approved
lesson marked `rendered` or `not rendered` in the note at the next emit (D-REVIEW — HTML is the
only human surface, deterministic and committed alongside the data). The executing agent never edits
package files: progress enters through `progress_update`/`audit_record`/`work_bind`, and status cascades
(AC verdicts → requirement lifecycle) fire inside the same transaction.

## 4. Distribution: a self-contained plugin

Tamheed is packaged as a **Claude Code plugin**, and the repository doubles as its own **marketplace**:

```
tamheed/
├── .claude-plugin/marketplace.json        # repo = marketplace; lists the one plugin
├── lab/                                   # the permanent execution lab (repo-side, not in the bundle)
└── plugins/tamheed/                       # THE PLUGIN — the self-contained skill bundle
    ├── .claude-plugin/plugin.json
    ├── .mcp.json                           # auto-starts the server when the plugin is enabled
    ├── skills/                             # v5: tamheed/SKILL.md (the front door, owns the capability) + 9 discipline + 17 scenario skills
    ├── references/                         # on-demand depth + artifact-catalog.md
    ├── templates/                          # surviving narrative section templates
    ├── scripts/                            # scratch_diff.py (package diff utility)
    ├── db/                                 # the store: schema.sql + migrations/ + store.py + CANONICAL.md
    ├── server/                             # Tamheed MCP server (only write path into a package)
    ├── prompts/                            # the operator guide (emitted into <package>/prompts/) + stock-history.json
    └── assets/                             # logos
```

### The instruction surfaces (v5)

Four surfaces instruct an executing session, each with one owner and one delivery path — the
always-loaded note stays small because everything that is HOW rather than WHAT moved to skills:

```mermaid
flowchart LR
    EMIT[handoff_emit] -->|rebuilds every emit| NOTE["CLAUDE.md note - tamheed:note v6<br/>AMBIENT: package pointer, the obligations table, Approved lessons, the skills line"]
    EMIT -->|refreshes the guide, retires stale leftovers| GUIDE["package/prompts/<br/>README.md (the one stock file) + project-authored prompts"]
    UPD[claude plugin update] -->|ships| DISC["9 discipline skills (v5.1, plain-english v5.9)<br/>MODEL-INVOKED, out of the / menu: package-writes, reading-the-record, operator-interview, written-claims, plain-english, test-evidence, measurement-evidence, ci-evidence, session-handoff (both routes)"]
    UPD -->|ships| SCEN["17 scenario skills<br/>OPERATOR-INVOKED /tamheed:name - description out of context"]
    UPD -->|ships| HOOK["hooks/hooks.json (v5.1)<br/>SessionStart: resume_hook.py prints the resume block - plain text, screened, capped"]
    PROMO["/tamheed:skill-promote"] -->|writes on the operator's word| PROJ[".claude/skills/name<br/>PROJECT: promoted lessons, operator-owned, SKL- rows"]
    NOTE -.->|names| DISC
    NOTE -.->|names| SCEN
    NOTE -.->|the skills line| PROJ
    RES["tool results (v5.1, v5.2)<br/>audit_record, readiness_check, progress_update, package_open/server_info,<br/>entity_query (every row), handoff_emit (any finding)"] -.->|"skill: tamheed:name"| DISC
```

In a crowded host most skill descriptions reach the model **name-only** (the field measured 389 of
490 with thirty-three plugins enabled), so "load on relevance" cannot carry the discipline alone:
since v5.1 the note names all eight skills and the phase-start tool results name the one to invoke
(`audit_record` → the evidence skill(s) by `verification_method`; `readiness_check` with a blocking
failure → `operator-interview`; `progress_update` of a handoff → `session-handoff`; the resume block
→ `package-writes`). A name works for the model even when its description did not arrive.

### The resume surface (v5.1)

After `/clear` or a compaction nothing used to reach the agent for free — the note is byte-stable
by design, and the MCP process with its lock survives a compaction (so `package_open` refuses; the
first call is `server_info`). Now the state a session stops in has a typed home in the journal, and
three surfaces return the same read of it:

```mermaid
sequenceDiagram
    participant A1 as session N (agent)
    participant S as tamheed MCP server
    participant P as package (journal)
    participant H as SessionStart hook
    participant A2 as session N+1 (agent)
    A1->>S: progress_update(event_type="handoff") - written LAST
    S->>P: PE- appended (corrected later via corrects, never edited)
    Note over A2: /clear, a compaction, a resume, a new session - never a plugin reload (v5.4, measured)
    H->>P: store.load (lockless, read-only)
    H-->>A2: the resume block - plain stdout, G-INJECT screened, 40 lines max;<br/>the lock line carries the store's OBSERVATION of a foreign holder (v5.3)
    Note over H: TAMHEED_HOOK_LOG (opt-in, v5.3): one counts-only line per run into a file the operator created;<br/>the line ends with the session's id (v5.4), so it names the session that wrote it,<br/>and opens with the hook's release (v5.6), so it names the hook that ran;<br/>only a session that loaded the plugin runs the hook (v5.5, measured)
    A2->>S: server_info (or package_open on a fresh session)
    Note over A2,S: server_info names the server that answers; the tool descriptions the session lists<br/>were fetched when its client process started - a plugin reload restarts the server, not that listing (v5.8.1, one field case)
    S->>P: _resume_block: latest handoff + corrections, handoff_behind,<br/>open feedback, open slices, lock holder + observed (own lock: alive, no probe)
    S-->>A2: resume: {...}, skill: tamheed:package-writes
    A2->>S: readiness_check("package")
    S-->>A2: handoff-current: the work entries no handoff covers;<br/>handoff-repeated (v5.8): the lines of the latest handoff carried through three handoffs, by number
    A2->>S: entity_query(type, id)
    S-->>A2: rows + skill: tamheed:reading-the-record (v5.2 - the row arrives with its cue)
    A2->>S: handoff_emit(target)
    S-->>A2: scans + skill: tamheed:written-claims (v5.2 - only when a scan found something)
    A2->>S: entity_upsert(skill row: Obsolete + upstreamed_to)
    S->>P: PE- transition signed system:skill-guard (v5.2)
```

The hook is guarded (silent without a tamheed note in `CLAUDE.md` or behind one `@` import),
lockless, screened, capped, and can never fail the session (one line, exit 0); its output is plain
text because the plugin JSON-output path has a bug history. The review surface renders the same block
as its Resume section. What v5.1 did NOT do: extend the obligations table (the handoff duty is a note
sentence plus the advisory, so the marker stays `v5`), add a tool (19), or add a state file. v5.2
(plans 129–135, the first field round on this surface) added two cues — every successful `entity_query` result
and any `handoff_emit` finding name their skill, since the field measured that nothing loads without
a result naming it — and the engine's `system:skill-guard` row on a skill row's lifecycle move; the
hook prints up to 4,000 characters of the entry (the block's own cap). v5.3 (plans 136–140, the
second field round) made the block say what the store OBSERVED about the lock's holder — after a
process restart the field's hook named a dead pid and the agent needed `package_unlock` to learn it
was dead — through the same seam `package_unlock` reads (a lock held by this very session reads
`alive` with no probe), and gave the hook an opt-in trace (`TAMHEED_HOOK_LOG`, counts only, an
existing file only) because the field could not tell "the hook did not fire on a plugin reload"
from "it fired and nothing was delivered"; the approval hint now says a lesson RENDERS only if pinned
or among the 10 newest unpinned Approved rows (thirteen unpinned approvals had hidden every rendered
lesson). v5.4 (plans 141–145, the third field round) put the session's id in the trace line: a
headless session another tool started in the project folder printed the same block, so its line
equalled the operator session's replay and a verdict was read from the wrong session. The same
round measured that a plugin reload runs no `SessionStart` hook at all (24 reloads, none; the one
delivery recorded earlier was a restart), so the routes in the diagram are a start, a resume, a
clear and a compaction — after a reload the block comes from `package_open` / `server_info`.
v5.5 (plans 146–150, the fourth field round) separated two words the bundle had used as one: a
lesson BINDS by its status, from the write that approves it, and is RENDERED when the note's
roster lists it. The field had recorded a lesson pushed out of the roster as no longer binding,
following a skill sentence that contradicted the governance reference. The approval hint, the
note's footer and the note-budget advisory say which word they mean, the review page marks the
roster, and a lint keeps the two apart. The same round corrected who writes a trace line: a
session that loaded the plugin, which sessions started through the Agent SDK's Python entry on
the measured machine had not.
v5.6 (plans 151–155, the fifth field round) named the release on two surfaces that could not say
it. The hook's two files were byte-identical at two tags, so a trace line of the old hook read as
a line of the new one: the line now opens with the hook's release, read from the bundle's
manifest. `review_current` compares a digest, so a page the older exporter wrote read current
after the upgrade: the export stamps its release beside the digest and `package_verify` reports
it as `review_exported_by`. The same round anchored the close-out on the commit: the export
precedes the commit that carries the page, after the handoff and after a bind, so the diagram's
"written LAST" names the last journal entry and the export follows it.

**Self-containment is a hard requirement, not a preference.** Claude Code copies the plugin directory to a
cache on install, so anything the skill reads or invokes at runtime must live inside `plugins/tamheed/` with
zero outward references. The same bundle is therefore also usable as a manual copy into a skills directory
or with any MCP-capable agent. Human-facing docs (`docs/`, this file) are *not* part of the bundle and may
link into it, but the bundle never links out.

## 5. The entry-point ↔ skill interface

A normalized request in, a routed package out. An entry point validates only invocation *syntax*; **content**
validation (is this a real, coherent project?) is the skill's job.

**Input contract** — whatever the user gave is mapped to one shape the skill understands: a description (or
brief path), an optional mode (`full | intake | plan | resume | stage:<id> | update | migrate | adopt`), an
optional `--profile` hint, and `--package-dir`. If the mode is omitted, the skill infers and
**confirms** it — never guesses silently
([`../plugins/tamheed/references/modes.md`](../plugins/tamheed/references/modes.md)).

**Output contract** — the skill returns either a completed package (whose gates pass, with the readiness
verdict) or a pause at a gate (clarification batch, or an approval gate: scope, decisions, roadmap, handoff,
final go/no-go). There is no separate state file: **the package is the state** — `resume`/`update` are
`package_open` + `entity_query`
([`../plugins/tamheed/references/state.md`](../plugins/tamheed/references/state.md)).

## 6. Error handling

Errors are handled at the layer that owns them. A **wrapper** fails *fast and loud* on bad invocation
(unknown flag, empty input → print help and stop); it never interprets project content. The **server**
fails *closed and named*: a constraint-violating write is rejected with the constraint in the error, batch
mutations are all-or-nothing, and a second concurrent writer fails loud on the lockfile. The **skill** fails
*safe and recorded* on process problems, via the workflow's per-stage failure conditions rather than by
crashing: empty input → ask; too-thin input → proceed under an `unknown` profile + raise an `OQ-`; unsourced
requirement → demote to an `ASM-` or raise an `OQ-` (never a silent requirement — and the store would
reject it anyway); unresolved hard contradiction → blocked from scope lock; user unavailable → proceed under
explicit recorded assumptions and mark the package *provisional*; critical gate failure → loop back, never
report "ready".

## 7. Versioning

Semver `MAJOR.MINOR.PATCH`, with the boundary defined by contract compatibility:

- **MINOR (additive):** new entity types (an `entity_types` registry row + an append-only DDL migration),
  section templates, optional columns, quality gates, profiles, diagram kinds, entry points. Existing
  packages keep working; a v4 package whose registry predates a newer family is taught it through
  `package_migrate`'s staged **registry-sync** mode (preview reports `entity_types_added`, confirm appends
  the registry rows — a pure registry append, no backup taken; `columns_added` names any files that re-serialize because their tables gained columns since the store was last written; since v4.5 the same staged sync also relocates a foreign `*.jsonl.converted` audit-trail file out of the canonical `data/` into `data-v3-backup/`). New trace relations and journal event kinds are MINOR too (a CHECK recreation on an empty-at-connect table — `004_amends_verify.sql`).
- **MAJOR (breaking):** a change to the DDL's existing required columns, the identifier scheme, or the
  MCP tool contract — ships with a migration note (see
  [`../plugins/tamheed/references/governance.md`](../plugins/tamheed/references/governance.md)).
- **PATCH:** fixes that change neither contracts nor user-visible behavior.

Immutable-after-approval rows (ADRs, approved acceptance criteria) are superseded, never rewritten — and
the schema enforces it with triggers. The plugin's own version lives in
`plugins/tamheed/.claude-plugin/plugin.json` and the marketplace entry; notable changes are recorded in
[`../CHANGELOG.md`](../CHANGELOG.md).

## 8. The single-writer lock, observed

One writer per package, guarded by `data/.lock` (`O_EXCL`). The lock records who took it — pid,
host, `taken_at`, and the writer's **process start identity** — so that the question "is the
holder still there?" is an observation, not a guess (plans 063–064, findings_25 §1). A bare pid
check is unsound: the OS recycles pids, and the field once found a dead writer's pid owned by an
editor started hours later.

```mermaid
stateDiagram-v2
    [*] --> Free
    Free --> Held : package_open or package_create takes the lock
    Held --> Free : package_close
    Held --> Orphaned : the writer dies - crash, closed terminal, process restart, plugin reload
    Orphaned --> Observed : any refusal reports the holder, package_unlock reports it on demand,<br/>the resume block and the hook's lock line carry it on the next session (v5.3)
    Observed --> Free : package_unlock confirm=true - holder not-running or reused - journaled
    Observed --> Orphaned : alive or unobservable - refused, manual removal stays deliberate
```

The observation has four outcomes. `not-running`: no such process. `reused`: the pid belongs to
a different process (its start identity differs from the one recorded; for an older lock that
recorded none, it started after the lock was taken). `alive`: the recorded process is running.
`unobservable`: another host or pid namespace, access denied, a legacy lock, or a platform that
cannot report a start time. `package_unlock(confirm=true)` — the operator's words, like `force` —
proceeds only on the first two; a lock the server could not see is not a lock it may remove.
The server reads process metadata to do this (Windows process query, Linux `/proc`); it spawns
nothing and signals nothing. Canonical JSONL reaches disk on **every write**, not at close:
`package_close` only releases the lock.
