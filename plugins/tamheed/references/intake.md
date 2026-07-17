# Intake & normalization

## Accept

- **Long-form prose** — a pasted brief, doc, or transcript. Most common.
- **Structured input** — a file matching `../schemas/project-input.schema.json` (YAML/JSON).
- **Mixed / partial** — some fields plus prose. Treat the structured fields as authoritative and mine prose
  for the rest.

Keystone **must support incomplete input** and normalize progressively: capture what exists, mark gaps as
`OQ-`, and fill them through clarification rather than blocking.

## Provenance is mandatory

For every extracted item, record where it came from (a quoted span or the input section). Provenance is what
lets G-REQ-SRC pass and lets a reviewer audit "why is this here?". Never drop provenance to tidy the output.

## Normalization steps

1. **Segment** the input into statements.
2. **Classify** each statement: business objective, problem, functional requirement, non-functional
   requirement, constraint (technical/organizational/regulatory), preference, existing-system fact, risk,
   known decision, unknown, deliverable, stakeholder, resource/time/budget, out-of-scope.
3. **Extract verbatim**, then restate crisply in a `normalized` field while keeping the original.
4. **Split** compound statements into atomic items.
5. **Assign IDs** per `governance.md`.
6. **De-duplicate**; merge with a recorded `merged_from`.
7. **Separate requirement from preference** ("must/shall" vs "prefer/ideally/nice-to-have"); set priority.
8. **Detect premature solutions** (a named technology in a requirement) and lift them into candidate
   decisions, leaving the underlying need as the requirement.
9. **Record gaps** as `OQ-`; **record inferences** as `ASM-` with `risk_if_wrong` — never as requirements.

## Input field map

The input schema covers: business objectives, problem statement, functional & non-functional requirements,
technical/organizational/regulatory constraints, existing systems/environments, preferred & prohibited
technologies, known risks, known decisions, unknowns/ambiguities, expected deliverables, target users,
stakeholders, available infrastructure, execution-agent constraints, repository constraints, and
time/budget/resource constraints. Absent fields are normal — list them as `OQ-` if they matter for the
profile, otherwise leave unset.

## Output of intake

`keystone-state.json` populated with: raw input + provenance, `project_profile`, requirement registers
(Draft), and seeded `OQ-`/`ASM-`. This is the substrate every later stage reads and updates.
