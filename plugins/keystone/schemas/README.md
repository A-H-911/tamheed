# Keystone schemas

Machine-readable **JSON Schema (draft 2020-12)** definitions for every structured artifact Keystone
produces or consumes. They are the contract between the skill's stages, the persisted state, and the
generated handoff package. Identifiers, statuses, and lifecycle rules here mirror
[`../references/governance.md`](../references/governance.md) — when in doubt, governance.md wins.

All schemas declare:
- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: `https://keystone.dev/schemas/<name>.schema.json`
- A `title`, `description`, `type`, `properties`, `required`, and `enum`s for statuses.
- `additionalProperties: false` on closed objects (the open intake schema and a few free-form maps are
  deliberately open).

Instances live elsewhere (the generated package's `keystone-state.json`, `manifest.json`,
`handoff/handoff-manifest.*`); these files describe their shape, they are not instances.

## How they relate

```
project-input.schema.json ───────────────┐  (raw intake; tolerant of incomplete input)
                                          │  $ref'd as raw_input
                                          ▼
                          keystone-state.schema.json  ◄── the master, machine-owned state
                                          │
   the `registers` object's arrays $ref one item schema ─┐
   per entity below (no `registers`/`requirements`        │
   umbrella schema exists — each entity is its own file): │
                                                          │
   requirement · constraint · invariant · assumption ·    │
   dependency · open-question · decision · adr-metadata ·  │  one schema per entity family
   risk · hypothesis · experiment · comparison-criteria ·  │
   acceptance-criterion · execution-phase                ─┘
                                          │
   traceability[]  $ref → traceability-row.schema.json
   progress[]      $ref → progress-update.schema.json
                                          │
                                          ▼
   handoff-package.schema.json   ◄── derived execution contract (artifacts, invariants, readiness)
   package-manifest.schema.json  ◄── derived inventory (present + omitted artifacts, generation meta)
```

`keystone-state.schema.json` is the hub. It uses **relative `$ref`** to the sibling files
(e.g. `"$ref": "requirement.schema.json"`), so the directory is self-contained and portable. Tooling
that loads the schemas should register each file under both its `$id` and its relative filename so the
sibling references resolve (the validation harness in this repo does exactly that).

## Files

### Intake
| File | Entity / purpose | ID pattern |
|---|---|---|
| `project-input.schema.json` | Comprehensive structured intake. Every field optional except a floor of `title`, `description`, **or** `meta` (`anyOf`), so partial input validates. Fields accept strings *or* partial objects and are normalized into the item schemas during intake. | — |

### Entity item schemas (register members)
| File | Entity | ID pattern |
|---|---|---|
| `requirement.schema.json` | Functional / non-functional requirement | `FR-NNN` / `NFR-NNN` |
| `constraint.schema.json` | Constraint | `CON-NNN` |
| `invariant.schema.json` | Invariant (non-negotiable) | `INV-NNN` |
| `assumption.schema.json` | Assumption (+ `risk_if_wrong`, `revisit_if`) | `ASM-NNN` |
| `dependency.schema.json` | Dependency | `DEP-NNN` |
| `open-question.schema.json` | Open question (+ `blocking`, `resolution`) | `OQ-NNN` |
| `decision.schema.json` | Lightweight decision (+ `options`, `recommendation`, `supersedes`/`superseded_by`, `promoted_to_adr`) | `DEC-NNN` |
| `adr-metadata.schema.json` | Architecture Decision Record metadata (+ `context`, `decision`, `consequences`, `alternatives`) | `ADR-NNNN` |
| `risk.schema.json` | Risk (`impact` · `likelihood` · `exposure` · `mitigation` · `owner` · `scope` · `trigger`) | `RISK-NNN` |
| `hypothesis.schema.json` | Hypothesis | `HYP-NNN` |
| `experiment.schema.json` | Experiment / POC (`method`, `pass_criteria`, `fail_criteria`, `timebox`, `result`) | `EXP-NNN` / `POC-NNN` |
| `comparison-criteria.schema.json` | Weighted comparison matrix (`criteria[]` with `weight`, per-option `scores`, `fit`) | — |
| `acceptance-criterion.schema.json` | Acceptance criterion (`statement`, `verification`, `scope`) | `AC-NNN` |
| `execution-phase.schema.json` | Roadmap phase (`goal`, `scope`, `deliverables`, `validation`, `risks`, `exit_criteria`) | `PH-N` |

### Derived / aggregate schemas
| File | Purpose | References |
|---|---|---|
| `traceability-row.schema.json` | One matrix row: requirement → decisions/work_items/tests/risks/acceptance + `coverage` (`full`/`partial`/`gap`) | — |
| `progress-update.schema.json` | One update-cycle entry (`date`, `summary`, `decisions_changed[]`, `items_completed[]`, `blockers[]`) | — |
| `handoff-package.schema.json` | Execution handoff contract (`artifacts[]`, `entry_points[]`, `invariants[]`, `mvp_definition`, `prerequisites[]`, `readiness` with `gate_results[]`) | — |
| `keystone-state.schema.json` | **Master state.** `schema_version`, `skill_version`, `project_profile`, `raw_input`, `provenance`, `registers`, `scope`, `selected_artifacts[]`, `stages[]`, `last_completed_stage`, `traceability[]`, `change_log[]` | `$ref`s **all** item schemas + `project-input` + `traceability-row` + `progress-update` |
| `package-manifest.schema.json` | Package inventory: artifacts present (path/version/status), generation metadata, and **omitted artifacts with reasons** | — |

## Status enums (from governance.md)

- **Decisions** (`decision.schema.json`) are **exactly**: `Proposed`, `Approved`, `Rejected`,
  `Superseded`, `Deferred`. A Proposed decision must never be rendered as Approved — this is a core
  safeguard, enforced by the closed enum.
- **ADRs** add `Implemented` and `Obsolete` to the decision set (realized / retired records).
- **Documents and most register items** use the full lifecycle:
  `Draft`, `Proposed`, `Approved`, `Rejected`, `Deferred`, `Superseded`, `Implemented`, `Obsolete`.
- **Open questions** use their own lifecycle (`Open`, `Answered`, `Deferred`, `Obsolete`).
- **Stages** (in `keystone-state`) and **phases** use `not-started`, `in-progress`, `blocked`, `done`.
- **Coverage** (traceability) is `full` / `partial` / `gap`; a `gap` on an MVP requirement fails
  `G-TRACE`.

## Conventions & invariants encoded here

- **Provenance is first-class:** item schemas carry a `source` field; `keystone-state` carries a
  `provenance[]` array. Required by `G-REQ-SRC` (see `intake.md`).
- **Typed cross-references:** items link to other entities through a `links` object with typed fields
  (`derives_from`, `verifies`, `mitigates`, `threatens`, `supersedes`/`superseded_by`, …) using the ID
  patterns above — not only in prose (see `governance.md`).
- **Supersession:** `supersedes` / `superseded_by` appear on decisions, ADRs, and acceptance criteria so
  history survives; the old item stays with status `Superseded`.
- **Tolerant intake:** `project-input` is deliberately permissive (`additionalProperties: true`, string-or-object
  fields, minimal floor) so incomplete briefs validate and gaps become `OQ-`/`ASM-` downstream.
- **Derived artifacts are reproducible:** `traceability[]`, `package-manifest`, and `handoff-package` are
  regenerated from state + sources, never hand-edited.

## Validating

Every file is valid JSON and a valid draft 2020-12 schema. To re-check (and exercise the cross-file
`$ref`s in `keystone-state`):

```bash
# parse-only
python -c "import json,glob;[json.load(open(f, encoding='utf-8')) for f in glob.glob('*.json')]; print('all parse')"

# full meta-schema validation (needs: pip install 'jsonschema>=4.18')
python - <<'PY'
import json, glob
from jsonschema import Draft202012Validator
for f in sorted(glob.glob('*.json')):
    Draft202012Validator.check_schema(json.load(open(f, encoding='utf-8')))
    print('OK', f)
PY
```

When resolving `keystone-state.schema.json`, register each sibling schema under its relative filename (the
`$ref` form used there) as well as its `$id`.
