# Lab continuation report — beat 23 (plan 127, tamheed v5.1.0), 2026-09-26

**Instrument.** The beat was fired in-process through the engine's tool functions
(`tamheed_server.package_open`, `progress_update`, `audit_record`, `readiness_check`, `handoff_emit`,
`export_html`, `package_verify`, `package_close`) — the same code path the MCP tools call — from a
throwaway script in the session scratchpad, on the working tree at the 5.1.0 stamp (plugin
`5.1.0`, `007_handoff.sql`, the guide's `5.1.0` history key already appended). Not over MCP stdio:
tamheed's tools are not enabled in this repository's session until plan 128's local enable takes
effect after a restart. The hook was run as a real subprocess (`uv run --no-project
server/resume_hook.py`) against the scratch project. Every line below is the script's printed
observation, not a memory of it.

## Phase A — the fixture (committed)

| Observation | Value |
|---|---|
| `server_info` | `schema_version: 7`, `migrations_head: "007_handoff.sql"`, `version: "5.1.0"` |
| `package_open` → `resume` | `handoff: null`, `handoff_behind: 11`, `skill: "tamheed:package-writes"` |
| `handoff-current` before | `fail`, 11 entities, `population: {table: progress_entries, rows: 11, scoped: false, unit: "work entries"}` |
| `lessons-stranded` before | `pass`, `entities: []` (emitted: the package has skill rows; the Obsolete `SKL-002` carries no Promoted lesson) |
| `readiness_check` hint | `skill: "tamheed:operator-interview"` (the scenario's deliberately-open blocking items) |
| `audit_record` (`AC-001`, `auto-test`) hint | `skill: ["tamheed:test-evidence", "tamheed:ci-evidence"]` |
| first handoff | `PE-040`, result `skill: "tamheed:session-handoff"`; `handoff-current` → `pass` |
| one `work-done` after it (`PE-041`) | `handoff-current` → `fail`, `entities: ["PE-041"]` |
| a `correction` of `PE-040` (`PE-042`) | `resume`: `handoff: PE-040`, `handoff_behind: 1`, `corrections: ["PE-042"]`, `next` opens "Read handoff PE-040 and its corrections, then note that 1 work-done/transition entries followed it — orient from the journal…" |
| `handoff_emit(<scratch target>, refresh_stock=true)` | `refreshed: ["prompts/README.md"]`; `stock_merged: []`; `oversized_prompts: []`; no `stale_references` from the skill file the skills table points at; `restated_content: []` |
| the emitted note | opens `<!-- tamheed:note v5 -->`; names `tamheed:session-handoff` and `tamheed:written-claims`; carries "write a `handoff` journal entry LAST" |
| the fixture's guide after refresh | contains "eight **discipline skills**" (the 5.1.0 body) |
| second emit | `CLAUDE.md` `unchanged`; nothing restated from the note (`[]`) |
| the beat's note | `PE-043` |
| final handoff, written LAST | `PE-044`; `handoff-current` → `pass` |
| `export_html` | review.html carries `<section id="resume">` and `Latest handoff: PE-044` |
| `gate_run` | `ready: true` |
| `package_verify()` | `verified: true`, `dirty: []`, `foreign: []`, `review_current: true` |
| `package_close` | no `data/.lock` remains |

Fixture files changed: `data/progress_entries.jsonl` (+5: `PE-040`…`PE-044`),
`data/audit_verdicts.jsonl` (+1), `prompts/README.md` (refreshed to the 5.1.0 stock body),
`review.html`, `csv/audit_verdicts.csv`, `csv/progress_entries.csv`, `csv/skills.csv` (the
`upstreamed_to` column). `data/skills.jsonl` was regenerated at plan 121 (the one-time
`"upstreamed_to": null` key).

## Phase B — a scratch copy of the package (never committed)

| Observation | Value |
|---|---|
| `SKL-001` set `Obsolete`, no pointer | `lessons-stranded` → `fail`, `entities: ["LL-001"]` |
| `entity_upsert` skill with `upstreamed_to: "tamheed:reading-the-record"` | `ok`, `changed_columns: [{column: "upstreamed_to", old_len: 0, new_len: 26}]` → `lessons-stranded` → `pass` |
| a 302-line `prm-next.md` | `oversized_prompts: [{file: "prompts/prm-next.md", lines: 302, bytes: 2911}]`; warning "prompts/prm-next.md is 302 lines / 2911 bytes — a prompt this size carries state; state belongs in a `handoff`…" |
| the previous release's guide body + `<!-- tamheed:stock-merged 5.1.0 -->` | `stock_merged: [{file: "prompts/README.md", declared: "5.1.0", verified: false, delta_missing: "14/14", reason: "14 of the 14 lines 5.1.0 added are absent"}]`; warning "…declares `stock-merged 5.1.0` but 14 of the 14 lines 5.1.0 added are absent — the marker is a claim…" |
| scratch `AGENTS.md` ("SL-001–SL-003 is COMPLETE; SL-003 is DEFERRED…", six `FB-` ids in one paragraph) | `restated_content`: `("id-dense", line 5, "feedback", count 6)`, `("status-claim", line 3, "slice", 1)` |
| second emit on the scratch target | nothing restated from the note it wrote (`[]`) |
| the hook, `source: "compact"`, `CLAUDE_PROJECT_DIR` = the scratch project | exit 0, seven lines (below) |

The hook's output, verbatim:

```
tamheed resume — package `package` (schema 7) — unlocked
Context was compacted mid-session: this is state re-injection, not a session start — resume from the handoff below; do not re-summarise it to the operator.
Handoff PE-044 (2026-09-26T10:17:45Z, agent:lab-beat-23); 0 work-done/transition entries since.
  Resume at: the next continuation beat (24). In flight: none - beat 23 closed. Awaiting the operator: nothing. Verified facts: gate_run ready and package_verify verified after this entry (both re-run after it); handoff-current pass. Do not carry: the first handoff of this beat (PE-040) and its correction are history.
Latest journal: PE-044 (handoff), PE-043 (note), PE-042 (correction)
Next: Read handoff PE-044 and its corrections first, then invoke tamheed:package-writes before your first write
Skill: tamheed:package-writes — invoke it by name before your first write.
```

## The emitted note (scratch target, head — the span is machine-path-specific and never committed)

```
<!-- tamheed:note v5 -->

This project executes Tamheed package `package` (under `C:\Users\ahammo\Repos\tamheed\evals\sample-results\lab-tracker`). **The package is the record — when code and package disagree, fix the code or record a scope change; never let them drift.** …
```

## Deviations from the pre-registered classes (batch record §0, M5)

None. Every class predicted in the approved plan's §5.1.3 was observed: `handoff-current` fail
then pass then fail (one entity) then pass; the correction chain in the block; `oversized`;
`stock_merged.verified false` with a `delta_missing` count; both detectors on the scratch
`AGENTS.md`; nothing from the note on the second emit; `lessons-stranded` fail then pass on the
pointer; the hook's block after a compaction, exit 0.

## The honesty limit

In-process, not over MCP stdio (the transport is covered by `--selftest`, 19/19). The Windows
`commandWindows` path of the hook was not exercised: the loading test (M1) and this run both used
the bash `command`. The `_INJECT_RE` false-positive rate on real handoff prose is one data point
(two handoffs, both printed).
