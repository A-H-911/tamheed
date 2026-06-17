---
description: Turn a project description into a validated, execution-ready planning & handoff package (invokes the Keystone skill).
argument-hint: "<project description | path/to/brief> [--mode full|intake|plan|resume|update|stage:<id>] [--profile <type>] [--package-dir <dir>] [--no-repo] [--owner <o>] [--visibility private|public] [--license <id>] [--dry-run]"
---

# /keystone — thin entry point

You are the **entry point** for the Keystone capability. You do not contain the methodology. Your only job
is to normalize the invocation and hand off to the **`keystone` skill**, which owns all logic.

Do exactly this:

1. **Gather input.** Take everything in `$ARGUMENTS` as the project description. If it is a file path (or
   `@file`), treat its contents as the brief. If it is empty, show the help block below and stop.

2. **Validate invocation syntax only.** Check that recognized flags have valid values
   (`--mode` ∈ full|intake|plan|resume|update|stage:<id>; `--visibility` ∈ private|public). On a bad flag,
   print the help block and stop. Do **not** validate the project content — that is the skill's job.

3. **Normalize** into the skill's input contract: `{ description | brief_path, mode?, profile?, package_dir?,
   repo: { create?, owner?, visibility?, license?, default_branch? }, flags: { dry_run?, no_repo? } }`.
   If `--mode` is omitted, leave it unset so the skill infers and confirms it.

4. **Invoke the `keystone` skill** with the normalized request. Load and follow `skill/SKILL.md`. Pass the
   mode through; do not pre-empt the skill's clarification, artifact-selection, or approval gates.

5. **Route output.** When the skill finishes (or pauses at a gate), surface what it produced — link the
   generated package directory and the key artifacts (charter, readiness report, handoff initial prompt) —
   and relay any questions or gate decisions it is waiting on.

Never duplicate or summarize the methodology here, and never make planning decisions in this wrapper. If you
feel the urge to add logic, it belongs in the skill (see `skill/references/extension.md`).

## Help

```
/keystone <project description | path/to/brief> [options]

Transforms a project description into a validated, traceable, execution-ready
planning + handoff package for another agent to implement.

Options:
  --mode <m>          full (default) | intake | plan | resume | update | stage:<id>
  --profile <type>    hint the project type (e.g. enterprise, rnd, legacy, ai-agentic)
  --package-dir <dir> where to write the generated package
  --no-repo           plan only; do not initialize a repository
  --owner <o>         repo owner/org (repo init)
  --visibility        private | public (repo init)
  --license <id>      SPDX id for the generated repo (e.g. MIT, Apache-2.0)
  --dry-run           show what would be created without writing a repository

Examples:
  /keystone @briefs/new-platform.md --mode full --profile enterprise
  /keystone "Build a CLI that syncs Notion to Markdown" --mode plan
  /keystone --mode resume --package-dir ./packages/new-platform
```
