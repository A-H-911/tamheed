---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Package Manifest — <project-name>

<!-- The package manifest: which artifacts are present, their versions, and generation metadata. Emitted
     as manifest.json at the package root; this Markdown is the human-readable surface — keep the JSON-
     shaped block below authoritative. Generation class: Always. Lives at: manifest.json.
     Distinct from handoff-manifest (the executor contract): this inventories the WHOLE package. -->

## Manifest (mirror to manifest.json)

```json
{
  "schema_version": "<semver>",
  "package_version": "<semver>",
  "project": "<project-name>",
  "generated": "<YYYY-MM-DD>",
  "generator": "keystone",
  "project_profile": "<e.g. greenfield-library | service | tool | research>",
  "artifacts": [
    { "path": "00-charter.md", "role": "charter", "version": "<semver>", "generation_class": "always" },
    { "path": "01-executive-summary.md", "role": "executive-summary", "version": "<semver>", "generation_class": "always" },
    { "path": "requirements/functional.md", "role": "functional-requirements", "version": "<semver>", "generation_class": "always" },
    { "path": "requirements/non-functional.md", "role": "non-functional-requirements", "version": "<semver>", "generation_class": "always" },
    { "path": "validation/traceability-matrix.md", "role": "traceability", "version": "<semver>", "generation_class": "derived" }
  ],
  "omitted_artifacts": [
    { "artifact": "<name>", "reason": "<why omitted — e.g. no external dependencies>" }
  ],
  "counts": {
    "requirements": { "FR": 0, "NFR": 0 },
    "decisions": { "DEC": 0, "ADR": 0 },
    "risks": 0,
    "phases": 0
  },
  "readiness": "<ready | not-ready>"
}
```

## Notes

<!-- Generation metadata or caveats not captured structurally. -->
- Generated artifact set selected per `artifact-rules.md`; omissions recorded above with reasons.
- Derived artifacts are reproducible from state + sources; do not hand-edit them.
