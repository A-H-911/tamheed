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
4. **Operator CLI args → `init_skill_repo.py` → git/gh/filesystem.** Operator-controlled, but still validated.

## Controls in place

- **Untrusted-content handling** — operating principle 10 in `plugins/keystone/SKILL.md`, safeguard 18 in
  `plugins/keystone/references/safeguards.md`, and the handoff screening step in
  `plugins/keystone/references/handoff.md`. Brief text is fenced + provenance-labeled, never an imperative.
- **No shell injection** — both Python tools invoke `git`/`gh` with **argument lists** (`subprocess.run([...])`),
  never `shell=True` and never string-interpolated commands (CWE-78).
- **No path traversal** — `init_skill_repo.py` validates `--repo-name` as a single safe path segment
  (`^[A-Za-z0-9._-]+$`, `.`/`..` rejected) and asserts the resolved target stays inside `--target-dir`
  (CWE-22). A malicious name exits non-zero and writes nothing.
- **Safe-by-default scaffolding** — the bootstrapper is dry-run-capable, idempotent, never overwrites without
  `--force`, refuses a dirty/non-empty target, and writes a `.gitignore` that excludes `.env` and caches so
  generated repos do not commit secrets. Remote creation/push is opt-in (`--create-remote`).
- **Minimal supply chain** — standard library only: no third-party dependencies, no network access in the
  tools, no code executed from package content (the validator parses, it never `eval`/`exec`s input).

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainer
([github.com/A-H-911](https://github.com/A-H-911)) — open a **private** GitHub Security Advisory on the
repository, or a minimal issue that omits exploit detail and asks for a private channel. Do not open a public
issue containing a working exploit. We aim to acknowledge within a few business days.

When reporting, include: affected file/version, a minimal reproduction, the impact, and (if known) a
suggested fix. Thank you for helping keep Keystone and its downstream packages safe.
