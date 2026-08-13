# Generated package structure (v3)

The layout Tamheed produces **for a target project** (distinct from the Tamheed repo itself). A
package is a data directory plus the prompts folder plus emitted review surfaces — not a tree of
Markdown registers.

```
<project-package>/
├── data/                          # THE package: canonical JSONL, one file per non-empty table
│   ├── packages.jsonl             # the package row (name, profile, mode, iteration, versions)
│   ├── entity_types.jsonl         # the artifact-family registry (G-SET reads classes from here)
│   ├── requirements.jsonl         # FR-/NFR- …and one file per populated family:
│   ├── decisions.jsonl            # constraints, invariants, assumptions, dependencies,
│   ├── adrs.jsonl                 # open_questions, risks, hypotheses, experiments, pocs, tests,
│   ├── phases.jsonl               # kpis, stakeholders, milestones, slices, wbs_items,
│   ├── acceptance_criteria.jsonl  # audit_verdicts, progress_entries, defects, deferred_work,
│   ├── trace_edges.jsonl          # execution_gates, execution_plans, conventions, scope_changes,
│   ├── narrative_documents.jsonl  # document_sections, diagrams, omissions
│   ├── …
│   └── .lock                      # single-writer lock (transient; never committed)
├── prompts/                       # v3 (plan 027): ALL prompts, plain .md — read the folder, pick
│   ├── <kickoff>.md               # project-authored (Stage 20; any non-stock filename)
│   └── <14 stock scenarios>.md    # the bundled library ({package} substituted), seeded at create
├── review.html (+ csv/)           # the human review surface, exported on demand
└── (target project root)          # handoff_emit writes there (wiring only, no prompt copies):
    ├── .mcp.json                  #   executor-side MCP config → the tamheed server
    └── CLAUDE.md                  #   the marker-managed operating note (obligations table)
```

The operator commits `<project-package>/data/` to whichever repository they choose — the package
travels as data. Human review happens through rendered surfaces (the HTML viewer, plan 012), never by
reading raw JSONL.

## What replaced the v1 tree

| v1 (Markdown tree) | v2 |
|---|---|
| `requirements/*.md`, `decisions/*.md`, `risks/`, `planning/`, `validation/*.md` registers | Rows in the corresponding tables |
| `00-charter.md`, `01-executive-summary.md`, `architecture/`, `research/` narratives | `narrative_documents` + `document_sections` rows |
| `architecture/diagrams/*` | `diagrams` rows (kind + source in `body`) |
| `validation/traceability-matrix.md`, `progress/status-report.md`, `execution/backlog.md`, readiness report | **Views** — queries, rendered on demand, never stored |
| `handoff/handoff-manifest.*`, `manifest.json` | The `packages` row + `omissions` + `v_artifact_membership` |
| `keystone-state.json` | The store itself (see `state.md`) |
| `scripts/init_repo.*` | Removed (ASM-B) — no repository scaffolding in v2 |

## Distinctions to preserve

- **Tamheed source** (the `plugins/tamheed/` bundle) vs **generated output** (a package's `data/`).
  Never write generated output into the source tree except under `generated-samples/`.
- **Section templates** (`../templates/`, blank narrative forms) vs **filled sections**
  (`document_sections` rows).
- **Entities** (rows, written via tools) vs **renders** (HTML/exported files, always regenerable).

## Minimal vs maximal

A tiny project may populate only: the package row, requirements, decisions, open questions,
assumptions, risks, one phase + one slice, acceptance criteria, a charter narrative, and the initial
prompt — with `omission` rows for the rest of the Always set. The selection rules decide
(`artifact-rules.md`); never emit empty ceremonial rows.
