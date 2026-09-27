# Lab continuation report — beat 25 (plan 139), 2026-09-27

Harness: `beat25.py` (scratchpad; in-process through the engine's tool functions — the same code path
the MCP tools call). Phase A on the FIXTURE `evals/sample-results/lab-tracker` (committed); phase B on
a SCRATCH copy (never committed). Every line below is quoted from the harness's `OBS` output
(`beat25.log`, second run — see "Owned" below).

## Phase A — the fixture (schema 7, tamheed 5.3.0)

| Observation | Value |
|---|---|
| `server_info` | `schema_version 7`, `migrations_head 007_handoff.sql`, `version 5.3.0` |
| `package_open` → `resume` | `handoff PE-047`, `handoff_behind 0`, `skill tamheed:package-writes` |
| `package_open` → `resume.lock` | `observed "alive"`, `evidence "held by this session"` |
| `server_info` → `resume.lock` | the same — the session's own lock is never probed |
| `handoff_emit(<target>, refresh_stock=true)` | `refreshed ["prompts/README.md"]`; `stock_merged []`, `oversized_prompts []`, `stale_references []`, `restated_content []`; no `skill` key |
| the fixture's guide after the refresh | reads `tamheed v5.3.0` and "every successful `entity_query` result names" |
| second emit | `CLAUDE.md` in `unchanged` |
| the note (`PE-048`), then the final handoff (`PE-049`, written LAST) | `handoff-current` → `pass` |
| `export_html` | `<section id="resume">` present; `Latest handoff: PE-049`; `promoted lessons` in the readiness table |
| `gate_run` | `ready true` |
| `package_verify` | `verified true`, `dirty []`, `foreign []`, `review_current true` |
| `package_close` | no `data/.lock` remains |

## Phase B — the scratch copy (nothing written to the fixture)

| Observation | Value |
|---|---|
| `package_open` on the copy → `resume.lock` | `observed "alive"`, `evidence "held by this session"` |
| `LL-002` approved unpinned → `next` | `… (the note is rebuilt by nothing else); it renders in the note only if pinned or among the 10 newest unpinned Approved rows - pin it to keep it visible` |
| `LL-006` approved pinned → `next` | `… (the note is rebuilt by nothing else); pinned rows always render` |
| the pointer-target emit | writes `package/CLAUDE.md` (the note the hook reads behind one `@` import) |
| the hook over `data/.lock` naming pid 2147483648 (`source: resume`) | exit 0; first line `tamheed resume — package \`package\` (schema 7) — lock file present (pid 2147483648 on Anas-PC since 2026-09-26T18:30:44+00:00; holder observed not-running — package_unlock(confirm=true) on the operator's word)`; the lock file still there |
| the hook with `TAMHEED_HOOK_LOG` naming a path that does not exist | exit 0; nothing created |
| the hook with `TAMHEED_HOOK_LOG` naming an existing empty file (`source: compact`) | one line `2026-09-27T01:02:56+00:00 source=compact lines=7 chars=1007 status=printed`; the counts equal the printed block's; the entry's text and the handoff id absent from the line; the block printed whole (7 lines, `unlocked`) |
| the hook with the variable unset | the log still holds one line |

The hook's output on the last run (the pointer root, after a compaction):

```
tamheed resume — package `package` (schema 7) — unlocked
Context was compacted mid-session: this is state re-injection, not a session start — resume from the handoff below; do not re-summarise it to the operator.
Handoff PE-049 (2026-09-27T01:02:55Z, agent:lab-beat-25); 0 work-done/transition entries since.
  Resume at: the next continuation beat (26). In flight: none - beat 25 closed. […] Do not carry: the scratch copy's lesson approvals and the dead-pid lock - never written to this package.
Latest journal: PE-051 (lesson-confirmed), PE-050 (lesson-confirmed), PE-049 (handoff)
Next: Read handoff PE-049 and its corrections first, then invoke tamheed:package-writes before your first write
Skill: tamheed:package-writes — invoke it by name before your first write.
```

(`PE-050`/`PE-051` are the copy's two approvals — `lesson-confirmed` rows the engine wrote on the
scratch copy, not counted by `handoff-current`, never in the fixture.)

## Owned

The first run's phase B ran the hook on a copy that had no `package/CLAUDE.md`: the note the hook
reads is written only by a pointer-target emit, which beat 24 had run and this harness had not. The
hook printed nothing (its guard), the harness stopped at the trace step, and phase A had already
written `PE-048`/`PE-049` to the fixture. The fixture was restored from git (`git checkout --
evals/sample-results/lab-tracker`), the harness gained the pointer emit before closing the copy, and
the whole beat was re-run: every class held on the second run. Lesson 3 of the 5.2.0 cycle again — a
beat that fails after phase A must be re-run from a restored fixture, never resumed.

## Evals

Re-aimed (F-6): `handoff=PE-049 behind=0`; the guide's `tamheed v5.3.0`; four handoffs. Added: the
note quotes `holder observed not-running`, `TAMHEED_HOOK_LOG`, `10 newest unpinned Approved rows`.
Fixture regolden by the beat's own writes (`data/`, `csv/`, `review.html`, the refreshed guide);
`python check.py` green after.
