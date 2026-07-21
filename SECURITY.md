# Security policy

Keystone is a planning/handoff **skill** (mostly Markdown + two stdlib-only Python tools). It has a small
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
- **No shell injection** — both Python tools invoke `git`/`gh` with **argument lists** (`subprocess.run([...])`),
  never `shell=True` and never string-interpolated commands (CWE-78).
- **No path traversal** — the MCP server validates package names as a single kebab-case segment
  (`^[a-z0-9][a-z0-9-]*$`, `.`/`..` unrepresentable) under the declared `--package-dir` (CWE-22);
  a malicious name is rejected and writes nothing.
- **Safe-by-default store** — no raw-SQL tool; batch mutations are transactional (all-or-nothing);
  approval-bearing rows are immutable (supersede, never edit); one writer per package via a fail-loud
  lockfile; `handoff_emit` refuses emission when the injection screen finds instruction-shaped text.
- **Minimal supply chain** — standard library only: no third-party dependencies, no network access in the
  tools, no code executed from package content (the validator parses, it never `eval`/`exec`s input).

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
suggested fix. Thank you for helping keep Keystone and its downstream packages safe.
