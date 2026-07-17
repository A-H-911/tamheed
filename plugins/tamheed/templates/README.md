# Tamheed section templates (v2)

Blank, fillable forms for the **narrative documents** of a v2 package. In v2 (ADR-0001) the
register families — requirements, decisions, risks, phases, acceptance criteria, and the rest —
are **relational entities** written through the MCP server (`entity_upsert`); their shape lives
in the `entity_types` registry + `../db/schema.sql`, not in a template. What remains here are
the **section templates** for `narrative_documents` prose and the handoff prompts.

Each template keeps YAML front-matter (`status`, `version`, `updated`, `owner`), section
headings, `<placeholder>` markers, and `<!-- guidance -->` comments. Fill from package state,
remove the guidance comments; blank forms only — filled content lives in the package (as
`document_sections` rows and emitted handoff files).

**Conventions:** identifiers, statuses, versioning, cross-references: `../references/governance.md`.

## Index (survivors of the plan-006 deliverables review)

| Template | Produces | Class |
|---|---|---|
| `project-charter.template.md` | Charter sections (problem, goals/non-goals, scope, KPIs, stakeholders) | Always |
| `executive-summary.template.md` | One-page summary + recommendation | Always |
| `architecture.template.md` | Architecture narrative (context, components, contracts) | Conditional |
| `adr.template.md` | ADR prose shape (context/decision/consequences → `adrs` row columns) | Conditional |
| `technology-comparison.template.md` | Weighted comparison matrix narrative (keep losers) | Conditional |
| `research-plan.template.md` | Research plan narrative (absorbs the v1 R&D backlog) | Conditional |
| `initial-prompt.template.md` | First execution-agent prompt (orient → 1 task → stop) → `prompts` row | Always |
| `follow-up-prompts.template.md` | Per-phase + situational prompts → `prompts` rows | Conditional |
| `review-prompts.template.md` | Audit / readiness / PR-review prompts → `prompts` rows | Conditional |
| `package-readme.template.md` | README of the generated package (reading order) | Always |
| `agent-control.template.md` | `CLAUDE.md` + `AGENTS.md` executor control surface | Derived |
| `naming-conventions.template.md` | Package naming/identifier conventions | Conditional |
| `contributing.template.md` | How to change the package without breaking governance | Conditional |
| `governance.template.md` | Package rules of record (ids, statuses, versioning) | Conditional |

## Where the v1 templates went (plan 009 dispositions)

- **Retired to entity types** (shape now = `entity_types` registry + DDL): the register
  templates — requirements (FR/NFR), constraint/invariant/assumption/dependency/open-question/
  open-decision registers, risk register, hypothesis/experiment/POC plans, roadmap,
  work-breakdown, test strategy, acceptance criteria/audit, progress log, deferred-work
  register, package manifest.
- **Dropped with their artifacts** (plan-006 review): milestones file, DoR/DoD (→ execution
  gates), stakeholder register, R&D backlog (→ research plan), handoff manifest (→ package
  manifest), traceability matrix + status report + execution-readiness report (derived views,
  rendered not templated).
