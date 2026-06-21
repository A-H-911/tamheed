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

Promoted from `DEC-002`. The shortener stores a small, fixed record per link
(code, target URL, click count). Read and write volumes are modest for the MVP.

## Decision

Store links and their click counts in a single relational table keyed by the
short code. This satisfies `FR-001`, `FR-002`, and `FR-003` without a second
datastore.

## Consequences

Simple to operate and back up; one write path for counts. If hot-link
contention threatens `NFR-001`, revisit via `DEC-003` (a cache layer).

## Alternatives considered and rejected

A separate analytics store was rejected as premature for MVP scale.
