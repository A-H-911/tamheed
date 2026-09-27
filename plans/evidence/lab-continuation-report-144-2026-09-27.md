# Lab continuation report — beat 26 (plan 144), 2026-09-27

Harness: `beat26.py` (scratchpad; in-process through the engine's tool functions — the same code path
the MCP tools call; the hook itself runs as a subprocess through `uv run --no-project`, the way
`hooks.json` runs it). Phase B on a SCRATCH copy ran FIRST, with hard assertions; phase A then wrote
the FIXTURE `evals/sample-results/lab-tracker`. Every line below is quoted from the harness's `OBS`
output (`beat26.log`, first run; window 04:39:56Z–04:39:59Z).

The operator's own trace variable was removed from every hook run. The operator's trace file held
the same five lines before and after the beat, none inside the window.

## Phase B — the scratch copy (nothing written to the fixture)

| Observation | Value |
|---|---|
| `package_open` on the copy → `resume` | `handoff PE-049`, `handoff_behind 0` |
| the pointer-target emit | writes `package/CLAUDE.md` (the note the hook reads behind one `@` import); `refreshed ["prompts/README.md"]` |
| the hook, `source: startup`, first session id, trace on | `2026-09-27T04:39:58+00:00 source=startup lines=6 chars=830 status=printed session=4fe4a0dd-bf04-4c32-836d-94b34c81ca86` |
| the hook, `source: startup`, second session id, trace on | `2026-09-27T04:39:58+00:00 source=startup lines=6 chars=830 status=printed session=04caef30-7785-450e-ad15-edaa46800a0f` |
| the two runs compared | the same block printed (6 lines, 830 characters); equal counts; different tails; the handoff's id and the entry's text in neither line |
| `session_id` holding a newline | `status=printed session=-`, exactly one new line |
| `session_id` holding a space | `status=printed session=-`, exactly one new line |
| `session_id` a number | `status=printed session=-`, exactly one new line |
| `session_id` absent | `status=printed session=-`, exactly one new line |
| `source` holding a newline | ` source=- lines=6 chars=830 status=printed session=4fe4a0dd-bf04-4c32-836d-94b34c81ca86` |
| the hook with the variable unset | the log still holds seven lines; the block is printed |

The first session id is the one step 0 measured on a real `SessionStart` event (plan 141).

The hook's output on the last run (the pointer root, `source: compact`):

```
tamheed resume — package `package` (schema 7) — unlocked
Context was compacted mid-session: this is state re-injection, not a session start — resume from the handoff below; do not re-summarise it to the operator.
Handoff PE-049 (2026-09-27T01:02:55Z, agent:lab-beat-25); 0 work-done/transition entries since.
  Resume at: the next continuation beat (26). In flight: none - beat 25 closed. Awaiting the operator: nothing. Verified facts: gate_run ready and package_verify verified after this entry (both re-run after it); handoff-current pass; the resume block's lock reads alive / held by this session while the package is open. Do not carry: the scratch copy's lesson approvals and the dead-pid lock - never written to this package.
Latest journal: PE-049 (handoff), PE-048 (note), PE-047 (handoff)
Next: Read handoff PE-049 and its corrections first, then invoke tamheed:package-writes before your first write
Skill: tamheed:package-writes — invoke it by name before your first write.
```

## Phase A — the fixture (schema 7, tamheed 5.4.0)

| Observation | Value |
|---|---|
| `server_info` | `schema_version 7`, `migrations_head 007_handoff.sql`, `version 5.4.0` |
| `package_open` → `resume` | `handoff PE-049`, `handoff_behind 0`, `skill tamheed:package-writes` |
| `package_open` → `resume.lock` | `observed "alive"`, `evidence "held by this session"` |
| `handoff_emit(<target>, refresh_stock=true)` | `refreshed ["prompts/README.md"]`; `stock_merged []`, `oversized_prompts []`, `stale_references []`, `restated_content []`; no `skill` key |
| the fixture's guide after the refresh | reads `tamheed v5.4.0`; its only changed line is the title |
| second emit | `CLAUDE.md` in `unchanged` |
| the note (`PE-050`), then the final handoff (`PE-051`, written LAST) | `handoff-current` → `pass` |
| `export_html` | `<section id="resume">` present; `Latest handoff: PE-051` |
| `gate_run` | `ready true` |
| `package_verify` | `verified true`, `dirty []`, `foreign []`, `review_current true` |
| `package_close` | no `data/.lock` remains |

## Evals

Three assertions re-aimed (the resume block's handoff, the guide's version, the handoff count) and
two added, both `grep-present` over the journal: `each line ended session= followed by its own id`
and `written session=- on exactly one new line`. 112 deterministic assertions on the case.

## Owned

Nothing failed in this beat. The order changed from beat 25: the scratch phase runs first, so the
fixture's note quotes observations already made. Beat 25 wrote its note before its scratch phase
ran, and had to be re-run from a restored fixture when that phase stopped.
