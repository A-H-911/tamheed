---
id: ADR-0001
title: Name the capability "Keystone"
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0001: Name the capability "Keystone"

Status: Accepted
Date: 2026-06-17

## Context

This skill needed a name. The capability is a reusable engine that takes a
project from inception through R&D planning, architecture governance,
execution handoff, and repository initialization, and is intended to grow into
broader project-management and engineering workflows. The naming criteria
(recorded in `../NAMING-OPTIONS.md`) were: short, memorable, vendor-neutral,
technology-neutral, easy to type as a slash command, valid as a GitHub repo
name, and broad enough to support future capabilities without becoming
misleading.

Seven candidates were scored 1–5 on clarity, memorability, extensibility, and
ambiguity (collision risk). On raw score, `Project Forge` (17) and `Groundwork`
(17) edged ahead of `Keystone` (16), mainly because Keystone carries a real
collision risk: **OpenStack Keystone** is a well-known identity service, and
"keystone" appears in other tools and brands. A purely analysis-driven pick
would have short-listed Project Forge (most brandable/extensible) or Groundwork
(cleanest, lowest collision).

## Decision

Name the capability **Keystone**. Identity as built:

- Skill name: `keystone`
- Slash command: `/keystone`
- GitHub repo: `keystone` (fallback slugs if taken: `keystone-inception`,
  `keystone-kit`)

A keystone is the wedge-shaped stone at the apex of an arch that locks every
other stone in place — nothing stands without it. That maps cleanly onto "the
planning foundation that makes execution hold together" and onto the
architecture-governance theme, and unlike "the beginning"-flavoured names it
does not feel narrow once the capability drives execution and ongoing
governance. It is a single, strong, memorable word that is trivial to type as a
command. The project owner selected it over the higher-scoring alternatives.

## Consequences

- A clear, evocative identity that scores top on memorability and
  extensibility and reinforces the product metaphor across docs.
- **Accepted trade-off — the OpenStack Keystone collision is real** for a
  technical audience. Mitigations, applied consistently:
  - Always frame the product as **"Keystone (project inception)"** in the
    README, the skill description, and first mentions in docs, so a reader
    coming from the OpenStack world is disambiguated immediately.
  - Do not assume the bare GitHub repo name `keystone` is available; plan for
    an owner/scope (`<owner>/keystone`) or a fallback slug
    (`keystone-inception`, `keystone-kit`) while keeping the command
    `/keystone` regardless.
  - Avoid positioning anywhere near identity/auth/IAM, where the collision
    would be most confusing.
- SEO/discoverability is weaker than a zero-collision name would give; accepted
  as the cost of the better metaphor and memorability.

## Alternatives considered and rejected

- **Project Forge** (score 17) — most extensible and brandable, the original
  working name. Rejected: two-word, hyphenated command (`/project-forge`) is
  longer to type, and "forge" overlaps code-forge tooling (SourceForge,
  Forgejo).
- **Groundwork** (score 17) — cleanest, lowest collision. Rejected: leans
  toward "the beginning" and risks feeling narrow once the capability drives
  execution and progress tracking.
- **Charter** (16) — professional, very typeable. Rejected: reads as "the
  charter document", narrower than the full inception→handoff scope; Charter
  Communications brand.
- **Blueprint** (16) — instantly communicates "the plan". Rejected: very common
  product/framework name, high collision.
- **Launchpad** (14) — readiness-to-launch framing. Rejected: Canonical
  Launchpad is a major existing platform, high collision.
- **Scaffold** (12) — Rejected: strongly implies code scaffolding/generators,
  which would mislead about Keystone's planning/governance focus.

See `../NAMING-OPTIONS.md` for the full scoring table and rationale.
