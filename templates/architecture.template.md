---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Architecture — <project-name>

<!-- The recommended architecture: context, component model, the contracts between components, and the
     decisions that shaped it. Reference ADR-/DEC- rather than re-arguing them here.
     Generation class: Conditional (architecturally significant decisions). Lives at:
     architecture/architecture.md. Keep diagrams in architecture/diagrams/ and embed/link them. -->

## Context

<!-- The system in its environment: who/what it interacts with, the boundary, key external actors and
     systems. A context diagram belongs here. Stay vendor/provider-neutral unless a CON- mandates one. -->
<context-overview>

<!-- Optional: ![Context diagram](diagrams/context.svg) -->

## Quality attributes driving the design

<!-- The NFR- that most shape the architecture, and the tension between them. -->
- `NFR-001` <attribute> → drives <structural choice>.
- `NFR-00x` <attribute> → drives <choice>.

## Components

<!-- The major components/modules: responsibility, what it owns, what it must NOT do. One row each;
     expand below if needed. A component diagram belongs in diagrams/. -->

| Component | Responsibility | Owns | Must not |
|---|---|---|---|
| <component-A> | <single responsibility> | <data/behavior it owns> | <boundary it must not cross> |
| <component-B> | <responsibility> | <owns> | <must not> |

## Contracts / interfaces

<!-- The agreements between components and at the system boundary: the stable seams. Describe shape and
     guarantees, not implementation. These are where invariants (INV-) are often enforced. -->

| Contract | Between | Shape (inputs → outputs) | Guarantees / invariants |
|---|---|---|---|
| <contract-1> | <A → B> | <input> → <output> | <e.g. deterministic; honors INV-001> |
| <contract-2> | <boundary> | <request> → <response> | <validation; versioning policy> |

## Data / control flow

<!-- The important flows (request path, data pipeline). Reference a data-flow diagram if one adds
     understanding a paragraph cannot. -->
<flow-description>

## Decisions referenced

<!-- The decisions that define this architecture. Link, don't restate. -->
- `ADR-0001` <title> — <one-line what it settled>.
- `DEC-00x` <title> — <one-line>.

## Cross-cutting concerns

<!-- Where each is handled in the architecture. -->
- Error handling / failure modes: <approach>
- Observability: <logging/metrics/tracing approach>
- Security: <where enforced; links NFR-/CON->
- Extensibility: <how new <component types> are added — e.g. via a registry, honoring INV-002>

## Open architectural questions

- `OQ-00x` <unresolved architectural question and what it blocks>.
