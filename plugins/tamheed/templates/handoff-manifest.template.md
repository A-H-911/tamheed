---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Handoff Manifest — <project-name>

<!-- The machine-readable handoff contract. It MIRRORS schemas/handoff-package.schema.json and is
     emitted as handoff/handoff-manifest.(yaml|json); this Markdown is the human-readable surface /
     fillable form. Keep the YAML block below as the source of truth for the structured fields.
     Generation class: Always. Lives at: handoff/handoff-manifest.(yaml|json).
     G-HANDOFF: every referenced artifact path must EXIST in the package. -->

## Structured manifest (mirror to handoff-package.schema.json)

```yaml
schema_version: <semver>          # version of handoff-package.schema.json this conforms to
package_version: <semver>         # version of this generated package
project: <project-name>
generated: <YYYY-MM-DD>
generator: keystone               # tech-neutral; the producing skill

# What the executor is being handed
mvp_definition: >
  <one paragraph: the minimal viable product — what PH-1 must deliver to count as MVP>

invariants:                        # the non-negotiables, listed up front (INV-)
  - id: INV-001
    statement: <invariant>
  - id: INV-002
    statement: <invariant>

entry_points:                      # where the executor starts reading / running
  initial_prompt: handoff/initial-prompt.md
  follow_up_prompts: handoff/follow-up-prompts.md
  review_prompts: handoff/review-prompts.md
  readiness_report: handoff/execution-readiness-report.md
  package_readme: README.md
  repo_bootstrap: scripts/init_repo.*   # optional; omit if not generated

prerequisites:
  runtimes:
    - name: <runtime>
      version: <pinned version>
  tooling:
    - name: <build/test tool>
      version: <pinned version>
  accounts_access:
    - <required access, or "none">

artifacts:                         # every artifact present, with its version + role
  - path: 00-charter.md
    version: <semver>
    role: charter
  - path: requirements/functional.md
    version: <semver>
    role: functional-requirements
  - path: requirements/non-functional.md
    version: <semver>
    role: non-functional-requirements
  - path: architecture/architecture.md
    version: <semver>
    role: architecture
  - path: planning/roadmap.md
    version: <semver>
    role: roadmap
  - path: validation/acceptance-criteria.md
    version: <semver>
    role: acceptance-criteria
  - path: validation/traceability-matrix.md
    version: <semver>
    role: traceability
  # ... one entry per artifact actually present in the package

phases:                            # from the roadmap (PH-)
  - id: PH-1
    goal: <goal>
    exit_criteria: <one line>
  - id: PH-2
    goal: <goal>
    exit_criteria: <one line>

omitted_artifacts:                 # anything in the catalog deliberately NOT generated, with reason
  - artifact: <name>
    reason: <why omitted, e.g. "no external dependencies">

readiness: <ready | not-ready>     # mirror the readiness report's verdict
```

## Notes for the human reviewer

<!-- Anything a reviewer should know that is not captured structurally above. -->
- <note: assumptions the executor inherits, accepted-open questions, etc.>
