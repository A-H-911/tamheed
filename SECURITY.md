# Security policy

Tamheed is a planning/handoff **skill** (Markdown methodology + a stdlib-only relational store and
MCP server). It has a small attack surface. But it (a) ingests an untrusted project brief and (b) emits
prompts that the agent acts on in the execution half. So prompt injection is its primary risk. This document states
the trust model and how to report a problem.

## Trust boundaries

1. **Untrusted brief → skill.** The project description and any file the skill reads are *data to plan over*,
   never instructions to obey (OWASP LLM01, direct injection).
2. **Skill → generated artifacts.** Artifacts may quote verbatim brief text. That text stays quoted and
   provenance-labeled, never rendered as a directive.
3. **Approved prompt rows → the execution half.** The highest-stakes boundary (OWASP LLM01, indirect /
   second-order injection): the agent in the target repository acts on the handoff. Since v6 the
   prompts are `prompt` rows the operator approves. `handoff_emit` refuses without an Approved kickoff
   and screens every Approved row (gate `G-INJECT`). A row approved after the last emit is read by its
   skill unscreened until the next emit, as a lesson is. The emitted note tells the agent to treat the
   package as untrusted too.
4. **Agent tool calls → MCP server → package store.** The only write path into a package: structured,
   checked arguments (no raw SQL, package names checked, single-writer lock). A constraint violation
   fails the call. (The v1 repository bootstrapper was removed in v2, ASM-B.)
5. **Journal → the next session's context (v5.1).** The plugin's `SessionStart` hook prints the
   package's resume block (the latest agent-authored `handoff` journal entry) into the model's context.
   It does so at every session start, resume, clear, compaction and fork. Agent-written prose entering an
   always-loaded surface is the same class as the note's lessons (boundary 3). It is screened before it
   is printed, capped, and read-only.

## Controls in place

- **The SessionStart hook is guarded, screened, capped and lockless** (plan 123). It prints
  nothing unless the project's `CLAUDE.md` (or ONE `@`-imported file) carries the tamheed note. It
  reads the store through the lockless loader and never takes the writer lock or writes a byte. The
  handoff text is withheld when the `G-INJECT` screen (`_INJECT_RE`) finds instruction-shaped text.
  The block is at most 40 lines and the entry at most 25 lines / 4,000 characters. That is the resume
  block's own cap since v5.2, where 5.1 printed 2,000. Any failure is one line and exit 0. Its output is plain
  text (never JSON hook output). Its lock line reports the store's OBSERVATION of the holder (v5.3)
  and removes nothing. `package_unlock(confirm=true)` stays the operator's word. Opt-in trace (v5.3,
  plan 136): `TAMHEED_HOOK_LOG` names a file the OPERATOR created. The hook appends one line of
  counts per run (source, line and character counts, status) and never the entry's text. A path
  that does not exist gets nothing (a project's settings `env` block could otherwise aim the hook
  at any writable file). The line ends `session=<id>` (v5.4, plan 141): the event's `session_id`,
  never the entry. That id is already the file name of that session's transcript on the same machine.
  The id and `source` arrive on stdin. So each is written only when it is a plain token
  (`[A-Za-z0-9._-]`, at most 64 characters), and `-` otherwise. A newline in either would forge a
  line. The line
  opens `<utc> version=<x>` (v5.6, plan 151): the hook's own release, read from the bundle's
  manifest, under the same token rule. The review page carries the same value as
  `<meta name="tamheed-version">`. It is written only when it is a plain token and read back by an
  exact pattern, because `package_verify` echoes it into a tool result. Every session that runs the
  plugin's hook in a project receives the resume block, a headless session another tool starts there
  included. A session runs the hook when it LOADED the plugin. One a tool starts with no settings
  loaded, as an Agent SDK caller may choose, loads none (v5.5, measured). Claude Code gives a hook no
  documented signal to tell them apart, and the block is text the project's own files already hold.
  Opt-out: disable the plugin for that project (`enabledPlugins`), the only per-plugin switch.
  `disableAllHooks` disables every hook of every tool in that project, and Claude Code has no
  per-hook switch.

- **Untrusted-content handling**: operating principle 10 in `plugins/tamheed/skills/tamheed/SKILL.md`,
  safeguard 18 in `plugins/tamheed/references/safeguards.md`, and the handoff screening step in
  `plugins/tamheed/references/handoff.md`. Brief text is fenced + provenance-labeled, never an imperative.
- **No VCS command execution.** The store and the package tools execute no VCS commands. The sole
  exception is adopt mode's read-only `git log` (list-argument subprocess, no shell,
  `plugins/tamheed/server/adopt.py`). `plugins/tamheed/scripts/scratch_diff.py` is a read-only diff
  tool, and nothing in the bundle invokes `gh` (CWE-78 surface: none).
- **No path traversal.** The MCP server checks package names as a single kebab-case segment
  (`^[a-z0-9][a-z0-9-]{0,63}$`) under the declared `--package-dir` (CWE-22). Every tool that resolves
  a name applies it (create, open, verify, migrate), and `.`/`..` are unrepresentable. A malicious name
  is rejected and writes nothing.
- **No CSV formula injection.** The `csv/<table>.csv` files `export_html` emits beside
  `review.html` are opened in spreadsheets. A text cell that a spreadsheet would evaluate as a
  formula is written quote-prefixed, the standard neutralization (CWE-1236, plan 050). Such a cell
  leads with `=`, `+`, `-`, `@`, tab or carriage return. The HTML surface renders the same cell
  unchanged. The guard lives in the CSV writer only.
- **The exporter removes only what it provably wrote.** `export_html` removes a stale
  `csv/<table>.csv` only when it is a regular file in the PACKAGE's own `csv/`. Its header must be
  the one the exporter writes for that table. An operator's file, anything in a caller-chosen
  `output` directory, and symlinks are reported, never touched (plan 065).
- **Lock observation reads process metadata and nothing else.** To tell a dead lock holder
  from a recycled pid the server queries process existence and start time. It uses Windows
  `OpenProcess`/`GetProcessTimes` with query-limited access, and Linux `/proc/<pid>/stat`. On macOS it uses `proc_pidinfo` through libproc (v6.5). It
  spawns no process and sends no signal (`os.kill(pid, 0)` never runs on Windows, where it
  terminates the target). A pid from the lock file is probed only if it is a real, bounded
  integer. The lock's strings are length-capped before they reach the journal (plans 063–064).
  Since v6.5 (plan 224) a lock also records the boot session. It is read on Linux from the
  kernel's boot id, and on macOS from the kernel's boot-session id. It is no hardware identifier: it changes at every boot and names no machine. A machine
  id is not read, because machines made from one image share it. A host-name mismatch is bridged
  only by an equal boot session. On Linux it also needs an equal, recorded pid namespace, because
  containers on one host share a boot. `package_unlock` refuses while a stopped migration's
  staging files remain. The stated limit: two machines restored from one memory snapshot share
  the boot id, as they share every pid. If one is renamed and its copy of the writer is killed,
  it reads a live writer on the other machine as gone. The operator's word is the guard for
  that case, as it already is when two such machines keep one host name.
- **One destructive lifecycle tool, operator-only.** `package_unlock(confirm=true)` removes
  `data/.lock` only for a holder OBSERVED dead (`not-running` / `reused`). It refuses on `alive`
  and `unobservable`, proves the store loads first, removes only the exact bytes it judged,
  and journals the removal. "Operator's words only" is a convention, as with `force`. Nothing
  mechanical tells an operator's word from an agent's (plan 064).
- **What binds every session is retired on the operator's word too.** On an Approved or
  Promoted lesson, any move off a binding status and any change to `superseded_by` is refused
  without `operator_confirm`. The engine retires a lesson only inside the write where the
  operator approves its successor, journaled. Two reviewers found the two ways an agent could
  have unbound a lesson unattended (`Proposed`, a pre-set pointer). Both are closed (plan 075).
  The by-hand exit is journaled by the engine (plan 086), and the engine's actor namespace is its
  own. A caller cannot write `system:<component>` on either journal path, so an audit row that
  says `operator_confirm attested` was written by the server or not at all.
- **A partial write inherits every guard.** The `substitute` item (v4.12) changes one token in one
  column by materializing the stored row and sending it down the ordinary full-row path. It has no
  guard of its own to have holes in. It refuses the journal, composite-key rows, `id`, and a match
  glued to a digit (`DEC-20` inside `DEC-208`). That last is the class the security review found. It
  refuses
  (v4.13) the re-run shape too. A replacement that contains the needle and is already present would
  compound on a second run. The field found it, and the guard now names it.
- **The go/no-go verdict is the operator's.** `entity_upsert(type="package")` refuses any item that
  NAMES `go_no_go` without `operator_confirm` (v4.13: presence-checked, so a refusal probe can fail).
  It journals a real move by `system:package-guard`, and writes no audit row for an attested re-send of
  the same verdict. Identity columns are frozen.
- **Every engine-written journal row is signed `system:<component>`.** `work_bind`'s was the one
  anonymous row (found in the field's journal, v4.13). A caller can never write a `system:` actor.
  v5.2 closes the last unwitnessed move. A skill row's status change and its retirement pointer
  are journalled by `system:skill-guard` (the field had written that record by hand).
- **A feedback row is journaled at every move.** Entering the bound set and leaving it on the
  operator's word (v4.11), and the bookkeeping moves within it (v4.13: `Confirmed → Reported`,
  `Reported → Resolved`). The row says which it was and never claims a word it did not get.
- **What leaves the package leaves on the operator's word.** A `feedback` row (v4.11) is the
  only sanctioned channel from a project to the plugin's maintainer. It leaves as an
  `entity_export` file inside the project's own findings, only once `Confirmed`
  (`operator_confirm` + `confirmed_by`). Its content cannot be rewritten underneath that
  confirmation. A local tool over the package exists only as a confirmed `local-tool` row (no
  draft stage). It writes nothing tool-owned, and if it reads the STORE, it reads `exports/` only.
  `handoff_emit` names unconfirmed rows every emission, ids only. **The operator's word is the JSON
  boolean `true`** on every guard. A truthy string never attests (v4.12). Two reviewers bypassed the
  first guard four ways before commit (a tool kind by update, born Reported, content under an old
  confirmation, an unjournaled withdrawal). All are closed (plan 087).
- **Approved-only lessons in the note.** The emitted `CLAUDE.md` note's Lessons section renders only
  operator-Approved `LL-` rows and is screened by the same G-INJECT patterns as the Approved prompt rows
  (blocking). The store refuses to land a lesson in Approved/Promoted without the operator's explicit
  `operator_confirm` on the write.
- **Skill files.** A promoted skill's `SKILL.md` body is operator-approved interview output, written
  by the agent on the operator's words and operator-owned from that moment. The server neither writes
  nor reads skill files (the package row holds metadata only). The promotion skill instructs a
  G-INJECT-style self-review of the draft before it is shown for approval. A skill is a standing
  instruction surface and is treated as one.
- **The plugin's own skills (v5).** The front door, nine discipline skills (v5.1, v5.9) and seventeen
  scenario skills under `plugins/tamheed/skills/` are static bundle text with no package-derived content.
  They reach a session through the plugin install, never through a package, and check.py's skills lint
  keeps them well-formed, stack-neutral and free of field identifiers. The scenarios carry
  `disable-model-invocation`: the operator invokes a ceremony, the model never starts one. The note
  `handoff_emit` writes names them by skill name only. No skill body ever enters the note, so the
  note's screens are unchanged. Removing a retired 4.x scenario file left under `<package>/prompts/` happens
  only with `refresh_stock=true`. It happens only when the file is byte-equal to a shipped release
  (the proof the overwrite has always relied on). A customised copy is never touched.
- **Server-witnessed journal facts cannot be narrated.** The four journal kinds the server appends
  (`forced-override`, `lesson-confirmed`, `lesson-promoted`, `integrity-verified`) are refused from
  `progress_update`. `package_verify` is read-only by default and journals a digest only on a passing
  round-trip. It is stated as evidence-of-verification, not tamper-evidence. There is no hash chain or
  signature, because a hand edit followed by a tool call is rewritten canonically. Git history is
  the tamper record.
- **Nothing leaves the store silently.** Entity rows are never removed (retired, superseded, or
  dispositioned). The one removal a caller can make is a trace EDGE via an explicit `retire: true`
  item (v4.6). The server journals it as a `correction` row in the same transaction and reports it
  per item. The relation rule is bypassed on retire (a mistyped edge is what is retired), and the
  gates re-evaluate on the next run. A retire that removes traceability shows up in G-TRACE.
- **The sanctioned read for scripts writes only a derived file.** `entity_export` (v4.7) runs a
  read-only tool (an allow-list, with `package_verify`'s `record` refused). It writes its whole result
  to a caller-named path outside `data/`, resolved before the check. An existing file is replaced
  only if it is itself a tamheed export. The file holds brief-derived text a script will RENDER.
  Consumers escape it, and the viewer's escape-first rule applies to them too. On the write side,
  `expect_unchanged` refuses a full-row write that alters columns the caller named as untouched. It
  refuses (v4.14) a write that names a column it does not carry, because that assertion could only pass.
- **The interview page runs one script, named by hash** (v6.5, plan 227). `slate_export` writes
  `<package>/slates/<name>.html` from a slate that an agent wrote and from rows of the store. Both
  are untrusted text. Every text passes the one escape function at render. The page carries ONE
  script, the bundled static file `slate.js`, the same for every slate. A content policy in the
  page names that script by its SHA-256 hash and allows nothing else: `default-src 'none'`,
  `base-uri 'none'`, `form-action 'none'`. So an inline handler, a second script block and a
  script added by a row's text do not run. The page loads nothing and sends nothing.
  The script reads ids from data attributes, sets values and classes, and writes no markup. A
  line of a round's points is copied from a template that the server rendered. The page
  holds no data block. Measured in Chrome 157 on a `file://` page: the hashed script runs,
  and each of the other three is blocked and reported. Limits, stated plainly. A policy in a meta
  tag cannot set `frame-ancestors` or `sandbox`. The answers stay in the browser's storage until
  the operator clears them, under a key that is the page's own address. So a shared browser
  profile shows them to its next user. Measured in Chrome: every local page shares one storage
  area, so another local page that is opened in that profile can read them.
- **A view of the interview page protects nothing** (v6.5, plan 227c). The page has a room view
  and a presenter view. The room view hides the operator's questions, attendance, closure and
  the recommendations, and it can show one round. All of that is the style's work, from a
  switch on the page. The hidden text is in the file, and anyone who holds the file can read
  it. Text that a reader must not see does not belong in a slate.
- **The hand-outs hold the room's questions only.** `slate_export` writes two Markdown sheets
  beside the page. They leave out every option, every recommendation, every question of the
  operator and every decided topic. Both tools refuse a slate folder or file that is a link or that leads outside
  the package. A hard link cannot be told from a file, and it is not caught. A page is bounded
  before it is built: a row is printed once per citation, and the quoted text is counted first.
  The review page is unchanged: it still runs no script.
- **An answers file is a record of a page, never the operator's word.** `slate_read` reads
  `<package>/slates/<name>.answers.json` and one `<name>.<round id>.answers.json` for each ready
  round. It builds those names from the record, the caller names no path, and it opens no
  other file. A file beside the page that it did not read is named, never opened. It refuses a
  file over its size cap, a key written twice and a head for another slate. It refuses an
  answer that the slate does not offer. It refuses a person, a point kind and a closure field
  that the slate did not declare. A round holds 200 points at most. Where two files disagree, the
  answer is listed and neither file is picked. A file from an earlier export of the slate is
  read. Each answer is compared with its question's digest, and a changed question is listed
  to be put again. Every digest is computed from content, and no stored field is trusted. A
  question may be marked as needing the operator's approval. The page holds no approval input,
  and the reader lists such answers for the session. Nothing proves who wrote the file, and the result says so (`provenance:
  unverified`). It WRITES NOTHING: no row, no journal entry, no stamp. Free text of the file is
  screened by the `G-INJECT` pattern, and a hit is named in `screened`, never removed and never
  obeyed. An approval, a waiver and a `force` are still spoken in the session
  (`tamheed:operator-interview`, step 7).
- **Safe-by-default store.** No raw-SQL tool. Batch mutations are transactional (all-or-nothing).
  Approval-bearing rows are immutable (supersede, never edit). One writer per package via a fail-loud
  lockfile. `handoff_emit` refuses emission when the injection screen finds instruction-shaped text.
- **Minimal supply chain.** Standard library only: no third-party dependencies, no network access in the
  tools, no code executed from package content. The loader and gates parse, and they never `eval`/`exec`
  input.

## Provenance fields and the content gate (plan 017)

`custom_attributes` columns preserve v1-package and repository text **verbatim** as
provenance. The G-COMPLETE placeholder scan exempts them. That exemption is *grading*
relief only (provenance is evidence, not authored content), **not** trust relief. The
untrusted-content posture still applies in full. Stored text is data, never instructions,
and the G-INJECT screen at `handoff_emit` scans everything that leaves the package,
provenance included.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainer
([github.com/A-H-911](https://github.com/A-H-911)). Open a **private** GitHub Security Advisory on the
repository, or a minimal issue that omits exploit detail and asks for a private channel. Do not open a public
issue containing a working exploit. We aim to acknowledge within a few business days.

When reporting, include: affected file/version, a minimal reproduction, the impact, and (if known) a
suggested fix. Thank you for helping keep Tamheed and its downstream packages safe.
