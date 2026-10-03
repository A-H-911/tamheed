---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# <project-name> — the Tamheed package

<!-- The front door of a generated package. A v4 package is a RELATIONAL STORE
     (data/*.jsonl, canonical serialization) + a prompt folder + a generated review
     surface — never a tree of Markdown registers. Generation class: Always.
     Stored as a narrative-document (doc_kind: readme); the on-disk README.md of the
     package directory is generated from it. -->

## What this is

The execution-ready planning and handoff package for **<project-name>**, written by Tamheed. It holds
requirements, constraints, invariants, assumptions, open questions, decisions and ADRs, risks, a
phased roadmap with slices, acceptance criteria, and full typed traceability. Every entity is a row,
and every write goes through the Tamheed MCP tools.

## Status snapshot

| Phase | Scope | Status |
|---|---|---|
| `PH-1` | <one line> | <from `readiness_check("phase", "PH-1")`> |

<!-- The snapshot is a courtesy copy — the LIVE answer is always a query. -->

## How to read this package

1. **The human surface**: open `review.html` (regenerate with `export_html`). The verdict
   and identity come first, then the traceability flow, the registers, execution progress.
2. **The data**: `data/*.jsonl`, one file per entity family, canonical and
   diff-friendly. Commit it with your code. Never hand-edit while a session is open.
3. **The queries**: `entity_query("requirement", status="Approved")`,
   `entity_query("invariant")`, `trace_query("<id>")`, `gate_run()`,
   `readiness_check(scope)`. The store is the record, and prose copies drift.

## How an execution agent consumes this

Start from the prompts folder: **`prompts/README.md`** is the operator guide (which
`/tamheed:<name>` skill for which situation, semi-auto vs fully-auto, the single-writer lock).
The project-authored kickoff prompt lives beside it, and the scenarios are the plugin's skills. The
target repo's `CLAUDE.md` carries the recording-obligations table (emitted by `handoff_emit`).
The package is the record, and unrecorded work is drift.

## Conventions

- Identifiers, statuses, and cross-references: this package follows Tamheed governance. See the
  generated `governance`/`naming` documents if present. Else the identifier prefixes are
  self-describing: `FR-`, `AC-`, `SL-`, `DEC-`, `ADR-`, and the rest.
- Approved ADRs and acceptance criteria are immutable: superseded, never edited.
- One session at a time: `data/.lock` is the single-writer guard.

## Package metadata

- Package: `<package-name>` · store version: <from `server_info`>
- Created: <date> · profile: <profile> · MVP: <one line or "see charter">
