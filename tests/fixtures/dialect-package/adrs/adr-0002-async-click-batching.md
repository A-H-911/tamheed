# ADR-0002: Async click batching

- Status: Accepted
- Date: 2026-06-17
- Deciders: engineering

## Context

Promoted from `DEC-004`. Click-count writes contend with redirect reads under load;
`NFR-001` sets the latency budget. This file deliberately carries **no YAML front
matter** — the MADR shape Keystone v1 emitted in production packages (field-evidence C12).

## Decision Drivers

- Redirect latency must not pay for counter writes.
- Operational simplicity from ADR-0001's single table is worth keeping.

## Decision Outcome

Batch click increments in memory and flush them hourly to the single table.

## Consequences

Counts lag by up to an hour; `DEC-003`'s cache option becomes unnecessary. Flush
failures retry with backoff and are logged.
