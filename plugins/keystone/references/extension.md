# Extension points

Keystone is designed to grow as new projects reveal new reusable patterns — **without editing core logic**.
Everything below is additive: register a new entry, drop in a file; don't fork the workflow.

## What you can extend

| Extension | How | Where |
|---|---|---|
| New artifact type | Add a template + a catalog row + (if structured) a schema; add a selection trigger. | `../templates/`, `artifact-catalog.md`, `../schemas/`, `artifact-rules.md` |
| New template | Add a `.template.md`; reference it from the catalog. | `../templates/` |
| New schema | Add a `*.schema.json`; reference from the artifact/state. | `../schemas/` |
| New quality gate | Add a gate row + (if mechanical) a check in the validator. | `quality-gates.md`, `../scripts/` |
| New project-type profile | Add a profile that biases selection + research depth. | `artifact-rules.md`, `research-depth.md` |
| New diagram kind | Add to the diagram set + a generation note. | `generated-structure.md` |
| New entry point | Build a thin wrapper that normalizes input and routes output to THIS skill. | a future CLI / API / MCP / UI wrapper (in Claude Code the skill itself is the entry point) |

## Entry-point contract

Any new entry point (another slash command, a CLI, an API endpoint, an MCP tool, a UI) MUST:

1. Accept user input + optional parameters and normalize them to the skill's input contract
   (`../schemas/project-input.schema.json` + a mode).
2. Invoke this skill — never re-implement intake, clarification, artifact selection, generation, gates, or
   handoff.
3. Route or link the skill's output back to the user.
4. Contain no methodology and no business logic. (Mirrors safeguard 12 / G-CMD-THIN.)

This is what "the skill owns the capability; the entry point only invokes it" means in practice. If you
find yourself adding decision logic to a wrapper, it belongs in the skill instead.

## Compatibility

Additive changes (new template/schema/gate/profile) are MINOR. Changing an existing schema's required
fields, an identifier scheme, or the handoff contract is MAJOR and needs a migration note (`governance.md`).
Keep older packages readable: the validator should degrade gracefully on a package authored under a prior
MINOR version.
