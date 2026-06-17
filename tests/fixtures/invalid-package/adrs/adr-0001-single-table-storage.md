---
id: ADR-0001
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0001: Single-table storage for links and counts

Status: Accepted
Date: 2026-06-17

## Context

Promoted from `DEC-002`. A small, fixed record per link with modest volumes.

## Decision

Store links and click counts in a single relational table keyed by the short
code, satisfying `FR-001`, `FR-002`, and `FR-003`.

## Consequences

Simple to operate; one write path for counts. Revisit via `DEC-003` if
`NFR-001` is threatened.

## Alternatives considered and rejected

A separate analytics store was rejected as premature for MVP scale.
