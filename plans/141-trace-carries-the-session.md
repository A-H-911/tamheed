# Plan 141: the trace carries the session

> Maintainer-executed, 2026-09-27. Batch map: [141-145-batch-findings-35.md](141-145-batch-findings-35.md).
> Field source: ACMP `findings_35.md` (A2, B4, `PE-1508`, `LL-112`), ruling R20.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

The 5.3.0 trace line carried counts and no identity. A headless session another plugin started in
the project folder printed the same resume block, so its line equalled the operator session's replay
to the character. The field read "the hook ran on the reload, not delivered" from that line and
wrote it into a work-done entry, its findings and a memory file. Its own `/compact` control exposed
the error; the verdict became "did not run".

## Step 0 — measured before any engine edit

One headless run (`claude -p`, build 2.1.283) in a scratch folder, with a probe hook passed through
`--settings` that writes its own stdin to a file. The probe file existing is the control that the
probe ran.

| Reading | Value |
|---|---|
| Keys of the SessionStart event | `cwd`, `hook_event_name`, `session_id`, `source`, `transcript_path` |
| `session_id` against the run's own id | equal |
| `session_id` against the transcript's file name | equal |
| `source` | `startup` |

Not used, recorded for the next reader: the hook's environment also carried a session-id variable
and an entrypoint variable reading `sdk-cli`. Both are undocumented for hooks.

A second reading from the same run: the installed plugin's hook wrote NO line to the operator's
trace file. The plugin is disabled in the user settings on this machine and enabled per project, so
the hook runs only where a project enables it. "Every session in every project writes a line" is
false here; the docs sweep (143) states the condition.

## What changed

- `resume_hook.py`: `read_event()` returns the event object (`{}` on any failure, a non-object
  included). `read_source()` stays as an alias for a caller written against 5.1–5.3: field scripts
  are not in git, so the consumer cannot be grepped. `main` takes `source` and `session_id` from one
  read.
- `_trace` appends ` session=<id>` AFTER `status=`, so every substring a field script matched stays
  true. `_token` keeps a value only when it is a string that fully matches `[A-Za-z0-9._-]{1,64}`;
  anything else is written `-`. The event arrives on stdin: a newline in it would forge a line.
- The same rule now covers `source`, which 5.3.0 wrote as it arrived.

## Tests

`tests/test_resume_hook.py`:

- `run_hook` removes `TAMHEED_HOOK_LOG` for the call, aims the hook at a file only through `trace=`,
  and restores the old value. A machine that traces its real sessions has the variable set; before
  this, every hook test appended to the operator's own file.
- `test_a_run_never_writes_the_operators_own_trace`: a decoy file named by the variable keeps its
  bytes through a run, and the variable is restored.
- `test_trace_line_names_the_session_that_wrote_it`: two ids in one folder give equal counts and
  different tails; a newline, a space, an empty string, 65 characters, a number, a list and null each
  give `session=-` and exactly one new line; a forged `source` gives `source=-`.
- `test_opt_in_trace_writes_counts_only_to_an_existing_file` uses `trace=` and asserts the tail
  `session=-` when no id is sent.
- `test_read_event_is_guarded` (renamed) adds a JSON list and a JSON string as events.

## Validation

| Check | Result |
|---|---|
| `python check.py`, the variable unset in the command | ALL CHECKS PASSED |
| The operator's trace file over the suite's window (04:25:49Z–04:27:07Z) | no line inside it; five lines before and after |
| The repo hook fed the captured real event, its trace aimed at a scratch file | one line ending `session=` with that run's id |
