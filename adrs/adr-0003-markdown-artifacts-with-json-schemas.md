---
id: ADR-0003
title: Human-readable Markdown artifacts plus machine-readable JSON
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0003: Human-readable Markdown artifacts plus machine-readable JSON

Status: Accepted
Date: 2026-06-17

## Context

A Keystone package serves two very different audiences. Humans read it to
understand and approve the plan — they want prose, tables, and headings they
can scan and comment on. Tooling consumes it to resume work, re-derive the
traceability matrix, validate quality gates, and hand off to an execution agent
— it wants typed, schema-validated structure that does not depend on parsing
free text.

A single-format approach forces a bad trade. Markdown-only means every tool has
to scrape prose, which is brittle and lossy. JSON/YAML-only means the artifacts
a human must read and approve become machine files, which kills reviewability
and invites rubber-stamping. We needed both surfaces without letting them
drift apart.

## Decision

Keep **Markdown as the human-readable surface** for every artifact, and mirror
the structured fields a schema defines in **machine-readable JSON** (with JSON
Schemas in `schemas/` describing the shapes). Specifically:

- Narrative and registers are authored as Markdown (tables for registers).
- Normalized state (`keystone-state.json`) and the handoff manifest are JSON
  conforming to their schemas; they are machine-owned.
- Where a register needs both, Markdown is the readable surface and the
  structured fields the schema defines are mirrored alongside.
- Derived artifacts (the traceability matrix, readiness report, roadmap
  rollups) are regenerated from the structured sources, never hand-edited.

## Consequences

- Humans review and approve the prose surface; tools act on the structured
  surface; neither audience is shortchanged.
- The validator (`tests/validate_package.py`) can check both surfaces and
  cross-check them, catching divergence between what is rendered and what state
  records.
- Portability: Markdown with relative links renders anywhere (GitHub, editors),
  and JSON parses anywhere with stdlib.
- **Cost — two surfaces can drift.** Mitigated by making the machine surface
  authoritative for derived data and regenerating rather than hand-editing
  derived artifacts, and by the consistency invariant that state and rendered
  artifacts must agree after any operation (a mismatch is a bug to repair).
- Some duplication of the same fact in prose and in JSON; accepted as the price
  of serving both audiences, and bounded by deriving wherever possible.

## Alternatives considered and rejected

- **Markdown only.** Rejected: every consumer must scrape prose; identifiers,
  statuses, and links cannot be validated or re-derived reliably; resume/update
  cycles have no normalized state to reconcile against.
- **JSON/YAML only.** Rejected: the artifacts humans must read and approve
  become machine files; reviewability collapses and approval becomes a
  rubber stamp; the whole point of a readable, auditable package is lost.
- **A bespoke single format (one custom DSL serving both).** Rejected: invents
  a parser and a learning curve, loses the free rendering and tooling that
  Markdown and JSON already have, and still has to choose which audience it
  optimizes for.
- **Embed structured data only inside Markdown front-matter.** Rejected as
  insufficient for large registers and cross-artifact state; front-matter is
  used for per-document metadata (status/version/updated), but the normalized
  state and manifest need standalone JSON.
