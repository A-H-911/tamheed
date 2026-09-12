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
