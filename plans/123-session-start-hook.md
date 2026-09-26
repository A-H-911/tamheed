# Plan 123: the SessionStart hook — the resume block for free

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (the plugin hook path has a bug history on
  JSON output — plain stdout is the measured-working path; loading test M1 PASS on 2.1.283)

## Why this matters

After `/compact` or `/clear` nothing reached the agent for free; the note is byte-stable by design.
The hook prints the resume block (plan 122) into context on every session start, resume, clear,
compaction and fork — guarded (silent without a tamheed note), lockless (`store.load`), screened
(`_INJECT_RE` withholds an instruction-shaped handoff), capped (40 lines), and never able to cost
the session (one line, exit 0, on any failure).

## What changes

- `plugins/tamheed/hooks/hooks.json`: one `SessionStart` entry, matcher
  `startup|resume|clear|compact|fork`, `command` = `uv run --no-project
  "${CLAUDE_PLUGIN_ROOT}/server/resume_hook.py"; exit 0`, a `commandWindows` PowerShell twin,
  `timeout: 10`, `statusMessage` — the shape measured injecting on this machine (ponytail's).
- `plugins/tamheed/server/resume_hook.py`: stdlib, no PEP 723 metadata (no MCP SDK resolve; uv
  77–115 ms measured); project dir from `CLAUDE_PROJECT_DIR` (argument or cwd as fallbacks); the
  note in `CLAUDE.md` or behind ONE `^@path` import line; package name from the note; pre-v4 →
  one line; `source` from stdin guarded (isatty/empty/malformed); a `compact` header says
  "re-injection, do not re-summarise"; the handoff entry ≤ 25 lines / 2,000 chars then a pointer
  to `entity_query`; corrections by id; open feedback; open slices; latest journal ids; `Next`;
  `Skill`. Any exception → `tamheed: resume unavailable (…)`, exit 0.
- `tests/test_resume_hook.py` (registered in `check.py` SUITES): silent without a note; the
  `@`-import case; inline note; missing data dir (one line); handoff + correction + lock line +
  compact header; withholding; line cap; failure posture; guarded stdin; `hooks.json` shape.
- `SECURITY.md`: the posture (agent-authored journal text enters context at session start:
  screened, capped, opt-out = `disableAllHooks` or disabling the plugin for the project).
- `docs/install.md`: the hook paragraph + the `settings.json` fallback snippet (the workaround
  from anthropics/claude-code #16538) for a host where plugin SessionStart output is dropped.

## Measured

- M1 (batch record §0): the stub hook's plain-text line was quoted back by the model in a
  `--plugin-dir` session on 2.1.283; the bash `command` path fired; `CLAUDE_PROJECT_DIR` set.
- Live smoke run of the real script on a scratch project with the note behind `@pkg/CLAUDE.md`
  and a copy of the lab-tracker package: header + compact line + "No handoff recorded; … uncovered:
  11" + latest journal + Next + Skill, exit 0; a project with no note printed nothing, exit 0.

## Done criteria

- [ ] `python check.py` green with the new suite
- [ ] the final-bundle `--plugin-dir` probe prints the real block (repeat of M1 with the script)
