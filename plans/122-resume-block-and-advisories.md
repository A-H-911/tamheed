# Plan 122: the resume block, `handoff-current`, `lessons-stranded`, the Resume panel

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW (one pure-SQL function reused by three
  surfaces; two advisory rules; one review.html section)

## Why this matters

After `/compact` or `/clear` the MCP process and the lock survive and the note is byte-stable, so
an agent got nothing for free (findings_32 note 4). `_resume_block(conn, name, data_dir)` — pure
SQL, no module globals, so the lockless hook (plan 123) can reuse it — returns the latest
`handoff` with its correction chain, `handoff_behind`, open feedback, active slices, the last three
journal ids, the lock holder, `next` and `skill`. `package_open` and `server_info` carry it; the
Resume panel renders it. `handoff-current` names the work no handoff covers; `lessons-stranded`
(FB-020) names Promoted lessons whose retired skill has no pointer.

## What changes

`tamheed_server.py`: `_resume_block`; `package_open` / `server_info` / `export_html` wiring; the two
rules after `lessons-note-budget` (package scope; `handoff-current` indeterminate before any work
is journalled; `lessons-stranded` only when `skills` has rows, through `ids()`). `export_html.py`:
`("resume", "Resume", _resume)` after `overview`, None-safe. `register-liveness` SKILL.md items 19–20;
the roster test; `quality-gates.md` (twenty-three, three conditional); `server/README.md` rows.
Tests: `test_resume_block_and_handoff_current`, `test_lessons_stranded_passes_once_the_pointer_exists`,
a Resume-section render test in `test_export_html.py`.

## Done criteria

- [ ] `python check.py` green
- [ ] `handoff-current` fails on every fixture (pre-registered) — the eval assertions still pass
- [ ] review.html of the demo carries `<section id="resume">`
