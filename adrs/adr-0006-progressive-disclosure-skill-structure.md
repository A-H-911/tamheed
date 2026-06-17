---
id: ADR-0006
title: Progressive-disclosure skill structure
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0006: Progressive-disclosure skill structure

Status: Accepted
Date: 2026-06-17

## Context

Keystone's methodology is large: a multi-stage workflow, governance rules,
artifact-selection logic, quality gates, safeguards, handoff and repo-init
procedures, and more. All of it must be available to the model, but not all of
it is needed at once — a given run touches intake, or planning, or handoff, not
every reference simultaneously. How the skill is structured directly affects
how much context each invocation consumes and how easy the methodology is to
maintain.

Putting everything in one giant prompt is the obvious approach and the wrong
one: it burns context on every call (most of it irrelevant to the current
stage), is hard to navigate and edit, and makes small changes risky because the
whole monolith reloads.

## Decision

Structure the skill for **progressive disclosure**: a lean `SKILL.md` that
states what Keystone does, when to use it, the high-level workflow, and pointers
to detail, plus a `references/` directory of focused files (governance,
workflow, artifact-rules, quality-gates, safeguards, traceability, state,
handoff, repo-init, modes, …) that are **loaded on demand** when a stage needs
them. The entry point stays thin (see ADR-0002), so the skill is the single
place this structure lives.

## Consequences

- Each invocation loads only what it needs; the always-on context stays small
  and cheap.
- The methodology is modular: each reference file has one responsibility, is
  easy to find, and can be edited in isolation without reloading everything.
- New methodology is added as a new reference file plus a pointer, rather than
  by growing a monolith.
- Cross-references between reference files (e.g. quality-gates → governance) are
  explicit and stay consistent because each topic has one home.
- **Cost:** a reader or the model must follow pointers to assemble the full
  picture, and the author must keep `SKILL.md` pointing at the right files.
  Accepted: the navigability and context savings far outweigh the indirection,
  and the lean top level is what makes the skill pleasant to use and maintain.

## Alternatives considered and rejected

- **One giant prompt / single SKILL.md with everything inline.** Rejected:
  wastes context on every call, is hard to navigate and edit, and makes every
  change high-risk because the whole thing reloads. Does not scale as the
  methodology grows.
- **Many tiny skills (one per stage).** Rejected: fragments a single coherent
  methodology into pieces that must be orchestrated and kept mutually
  consistent; the staged workflow is one capability and belongs in one skill
  with internal structure, not many skills.
- **External documentation site the skill links to.** Rejected: the methodology
  must travel with the skill and be available to the model offline/in-context;
  an external site is not loadable on demand into the run and adds a dependency.
  Repo-root specs (`METHODOLOGY.md`, `ARCHITECTURE.md`, …) complement the skill
  for human readers but are not the skill's runtime source.
