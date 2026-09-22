# Security policy

Tamheed is a planning/handoff **skill** (Markdown methodology + a stdlib-only relational store and
MCP server). It has a small
attack surface, but because it (a) ingests an untrusted project brief and (b) emits prompts that another
agent will act on, prompt injection is its primary risk. This document states the trust model and how to
report a problem.

## Trust boundaries

1. **Untrusted brief → skill.** The project description and any file the skill reads are *data to plan over*,
   never instructions to obey (OWASP LLM01 — direct injection).
2. **Skill → generated artifacts.** Artifacts may quote verbatim brief text; that text stays quoted and
   provenance-labeled, never rendered as a directive.
3. **Generated handoff prompts → downstream agent.** The highest-stakes boundary (OWASP LLM01 — indirect /
   second-order injection): the next agent may execute the handoff. The handoff is screened before emit
   (gate `G-INJECT`) and tells the downstream agent to treat the package as untrusted too.
4. **Agent tool calls → MCP server → package store.** The only write path into a package: structured,
   validated arguments (no raw SQL, package names validated, single-writer lock); a constraint violation
   fails the call. (The v1 repository bootstrapper was removed in v2 — ASM-B.)

## Controls in place

- **Untrusted-content handling** — operating principle 10 in `plugins/tamheed/SKILL.md`, safeguard 18 in
  `plugins/tamheed/references/safeguards.md`, and the handoff screening step in
  `plugins/tamheed/references/handoff.md`. Brief text is fenced + provenance-labeled, never an imperative.
- **No VCS command execution** — the store and the package tools execute no VCS commands; the sole
  exception is adopt mode's read-only `git log` (list-argument subprocess, no shell —
  `plugins/tamheed/server/adopt.py`); `plugins/tamheed/scripts/scratch_diff.py` is a read-only diff
  tool; nothing in the bundle invokes `gh` (CWE-78 surface: none).
- **No path traversal** — the MCP server validates package names as a single kebab-case segment
  (`^[a-z0-9][a-z0-9-]{0,63}$`, applied by every tool that resolves a name — create, open, verify,
  migrate; `.`/`..` unrepresentable) under the declared `--package-dir` (CWE-22); a malicious name
  is rejected and writes nothing.
- **No CSV formula injection** — the `csv/<table>.csv` files `export_html` emits beside
  `review.html` are opened in spreadsheets; a text cell that a spreadsheet would evaluate as a
  formula (leading `=`, `+`, `-`, `@`, tab or carriage return) is written quote-prefixed, the
  standard neutralization (CWE-1236; plan 050). The HTML surface renders the same cell
  unchanged — the guard lives in the CSV writer only.
- **The exporter deletes only what it provably wrote** — `export_html` removes a stale
  `csv/<table>.csv` only when it is a regular file in the PACKAGE's own `csv/` whose header is
  the one the exporter writes for that table; an operator's file, anything in a caller-chosen
  `output` directory, and symlinks are reported, never touched (plan 065).
- **Lock observation reads process metadata and nothing else** — to tell a dead lock holder
  from a recycled pid the server queries process existence and start time (Windows
  `OpenProcess`/`GetProcessTimes` with query-limited access; Linux `/proc/<pid>/stat`). It
  spawns no process and sends no signal (`os.kill(pid, 0)` never runs on Windows, where it
  terminates the target). A pid from the lock file is probed only if it is a real, bounded
  integer; the lock's strings are length-capped before they reach the journal (plans 063–064).
- **One destructive lifecycle tool, operator-only** — `package_unlock(confirm=true)` removes
  `data/.lock` only for a holder OBSERVED dead (`not-running` / `reused`), refuses on `alive`
  and `unobservable`, proves the store loads first, removes only the exact bytes it judged,
  and journals the removal. "Operator's words only" is a convention, as with `force`: nothing
  mechanical tells an operator's word from an agent's (plan 064).
- **What binds every session is retired on the operator's word too** — on an Approved or
  Promoted lesson, any move off a binding status and any change to `superseded_by` is refused
  without `operator_confirm`; the engine retires a lesson only inside the write where the
  operator approves its successor, journaled. Two reviewers found the two ways an agent could
  have unbound a lesson unattended (`Proposed`; a pre-set pointer); both are closed (plan 075).
  The by-hand exit is journaled by the engine (plan 086), and the engine's actor namespace is its
  own: a caller cannot write `system:<component>` on either journal path, so an audit row that
  says `operator_confirm attested` was written by the server or not at all.
- **What leaves the package leaves on the operator's word** — a `feedback` row (v4.11) is the
  only sanctioned channel from a project to the plugin's maintainer; it leaves as an
  `entity_export` file inside the project's own findings, only once `Confirmed`
  (`operator_confirm` + `confirmed_by`), and its content cannot be rewritten underneath that
  confirmation. A local tool over the package exists only as a confirmed `local-tool` row (no
  draft stage), writes nothing tool-owned; if it reads the STORE, it reads `exports/` only; `handoff_emit` names unconfirmed rows
  every emission, ids only. Two reviewers bypassed the first guard four ways before commit
  (a tool kind by update; born Reported; content under an old confirmation; an unjournaled
  withdrawal); all closed (plan 087).
- **Approved-only lessons in the note** — the emitted `CLAUDE.md` note's Lessons section renders only
  operator-Approved `LL-` rows and is screened by the same G-INJECT patterns as emitted prompts
  (blocking); the store refuses to land a lesson in Approved/Promoted without the operator's explicit
  `operator_confirm` on the write.
- **Skill files** — a promoted skill's `SKILL.md` body is operator-approved interview output, written
  by the agent on the operator's words and operator-owned from that moment; the server neither writes
  nor reads skill files (the package row holds metadata only), and the promotion prompt instructs a
  G-INJECT-style self-review of the draft before it is shown for approval — a skill is a standing
  instruction surface and is treated as one.
- **Server-witnessed journal facts cannot be narrated** — the four journal kinds the server appends
  (`forced-override`, `lesson-confirmed`, `lesson-promoted`, `integrity-verified`) are refused from
  `progress_update`; `package_verify` is read-only by default and journals a digest only on a passing
  round-trip, and it is stated as evidence-of-verification, not tamper-evidence (no hash chain or
  signature — a hand edit followed by a tool call is rewritten canonically; git history is the
  tamper record).
- **Nothing leaves the store silently** — entity rows are never deleted (retired, superseded, or
  dispositioned); the one removal a caller can make is a trace EDGE via an explicit `retire: true`
  item (v4.6), which the server journals as a `correction` row in the same transaction and reports
  per item; the relation rule is bypassed on retire (a mistyped edge is what gets retired), and the
  gates re-evaluate on the next run — a retire that removes traceability shows up in G-TRACE.
- **The sanctioned read for scripts writes only a derived file** — `entity_export` (v4.7) runs a
  read-only tool (an allow-list; `package_verify`'s `record` refused) and writes its whole result
  to a caller-named path outside `data/` (resolved before the check; an existing file is replaced
  only if it is itself a tamheed export). The file holds brief-derived text a script will RENDER —
  consumers escape it, the viewer's escape-first rule applies to them too. On the write side,
  `expect_unchanged` refuses a full-row write that alters columns the caller named as untouched.
- **Safe-by-default store** — no raw-SQL tool; batch mutations are transactional (all-or-nothing);
  approval-bearing rows are immutable (supersede, never edit); one writer per package via a fail-loud
  lockfile; `handoff_emit` refuses emission when the injection screen finds instruction-shaped text.
- **Minimal supply chain** — standard library only: no third-party dependencies, no network access in the
  tools, no code executed from package content (the loader and gates parse, they never `eval`/`exec` input).

## Provenance fields and the content gate (plan 017)

`custom_attributes` columns preserve v1-package and repository text **verbatim** as
provenance. The G-COMPLETE placeholder scan exempts them — that exemption is *grading*
relief only (provenance is evidence, not authored content), **not** trust relief: the
untrusted-content posture still applies in full. Stored text is data, never instructions,
and the G-INJECT screen at `handoff_emit` scans everything that leaves the package,
provenance included.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainer
([github.com/A-H-911](https://github.com/A-H-911)) — open a **private** GitHub Security Advisory on the
repository, or a minimal issue that omits exploit detail and asks for a private channel. Do not open a public
issue containing a working exploit. We aim to acknowledge within a few business days.

When reporting, include: affected file/version, a minimal reproduction, the impact, and (if known) a
suggested fix. Thank you for helping keep Tamheed and its downstream packages safe.
