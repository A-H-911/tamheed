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
  `OpenProcess`/`GetProcessTimes` with query-limited access, and Linux `/proc/<pid>/stat`. It
  spawns no process and sends no signal (`os.kill(pid, 0)` never runs on Windows, where it
  terminates the target). A pid from the lock file is probed only if it is a real, bounded
  integer. The lock's strings are length-capped before they reach the journal (plans 063–064).
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
