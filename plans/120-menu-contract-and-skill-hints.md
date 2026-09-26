# Plan 120: the menu contract, the skill hints, the note sentence, the README wording

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW (frontmatter flags, a lint clause, three result
  keys, one paragraph)

## Why this matters

findings_32 E13: all 24 skills sit in the `/` menu because `user-invocable` defaults to true — the
sixteen scenarios were meant to be slash commands; the seven discipline skills were not. Q1: in a
crowded host (33 plugins) 389 of 490 skill descriptions arrive name-only, so "load on relevance"
cannot carry the discipline; none of the seven fired across a full round. Ruling: the note and the
tool results name the skill.

## What changes

- `user-invocable: false` on the seven discipline skills (menu 24 → 18; model listing 8 → 9 once
  `session-handoff` lands in plan 124).
- Lint 12: every skill sets exactly one of `disable-model-invocation: true` / `user-invocable: false`,
  except `tamheed` and `session-handoff` (both routes).
- Result hints, key `skill`: `audit_record` → the evidence skill(s) per `verification_method`.
  **Correction at execution (the plan's W7 called it free text; the DDL CHECKs it to `auto-test` /
  `manual` / `inspection`):** `auto-test` → test-evidence + ci-evidence (a green suite, and run
  attribution when it ran in CI); `manual` / `inspection` → measurement-evidence; absent → all three;
  always a list, in roster order; `readiness_check` with ≥ 1 blocking `fail` → `tamheed:operator-interview`;
  `progress_update` carrying a `handoff` → `tamheed:session-handoff`; `package_open`/`server_info`
  name `tamheed:package-writes` inside the `resume` block (plan 122).
- The note paragraph names all eight discipline skills and carries the handoff sentence (R6: a
  sentence, not a table row; the note stays v5 and the span rebuilds on the first 5.1.0 emit).
- `prompts/README.md` wording (applied in plan 127 step 1 together with its `stock-history.json`
  key and the version stamp — lint 9 requires body and key in one commit):
  "Beside them, eight **discipline skills** …: `tamheed:package-writes`, `tamheed:reading-the-record`,
  `tamheed:written-claims`, `tamheed:operator-interview`, `tamheed:test-evidence` /
  `tamheed:measurement-evidence` / `tamheed:ci-evidence`, and `tamheed:session-handoff` (write the
  handoff LAST before a compaction). In a crowded host their descriptions may reach the model
  name-only — the note and the tool results name the one to invoke." Plus a "Which skill, when" row:
  "Before a compaction, at session end, on a handover → `/tamheed:session-handoff`", and on the
  orient-resume row: "the plugin's SessionStart hook prints the resume block first".

## Done criteria

- [ ] lint 12 green with the menu contract; the seven frontmatters carry the flag
- [ ] contract tests: `audit_record` hint (mapped, unmapped), `readiness_check` hint iff a blocking
  fail, `progress_update` hint iff a handoff
- [ ] `--plugin-dir` probe: 18 in the `/` menu, 9 in the model listing (after plan 124)
