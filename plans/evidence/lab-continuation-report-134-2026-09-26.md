# Lab continuation report — beat 24 (plan 134, the v5.2.0 continuation), 2026-09-26

Harness: `beat24.py` (scratchpad; in-process through the engine's tool functions, the same code
path the MCP tools call — the plugin's tools are not enabled in this repository's session).
Phase A ran on the FIXTURE (`evals/sample-results/lab-tracker`, committed); phase B on a scratch
COPY (never committed). The first run's phase B changed the lab skill's row AFTER the clean emit it
compared against, so "bytes restored" read false for the right reason (the span had changed) — the
fixture was restored from git and the whole beat re-run with the re-Approve before the clean emit;
the numbers below are the second run's. Every `OBS` line below is quoted from the log.

## Phase A — the fixture

| Observation | Value |
|---|---|
| `server_info` | `schema_version 7`, `migrations_head 007_handoff.sql`, `version 5.2.0` |
| `package_open` → `resume` | `handoff PE-044`, `behind 0`, `skill tamheed:package-writes` |
| `entity_query("skill", id="SKL-001")` | `skill: "tamheed:reading-the-record"`; the row `Approved`, `upstreamed_to null` |
| `lessons-stranded` before | `pass`, `population {table: lessons, rows: 1, unit: "promoted lessons"}` |
| `entity_upsert` (partial row: `Obsolete` + `upstreamed_to`) | `changed_columns` lifecycle_status, upstreamed_to; `skill_audit: PE-045` |
| `PE-045` | `transition`, actor `system:skill-guard`, subject `SKL-001`, `SKILL SKL-001 -> Obsolete (was Approved); upstreamed_to tamheed:reading-the-record` |
| `lessons-stranded` after | `pass`, entities `[]`, population unchanged |
| `handoff-current` after the guard's row | `fail`, entities `["PE-045"]`; `resume.handoff_behind 1` |
| an idle re-send of the row | no `skill_audit`; journal delta since the retirement = 1 (the guard's row only) |
| `handoff_emit(target, refresh_stock=true)` | `refreshed ["prompts/README.md"]`; `stock_merged [] oversized_prompts [] stale_references [] restated_content []`; no `skill` key |
| the guide | `tamheed v5.2.0` present; "every `entity_query` result names" present |
| the note | no stale-warning block; no skills line (no Approved skill remains) |
| second emit | `CLAUDE.md` unchanged |
| the close | note `PE-046`; final handoff `PE-047` written LAST; `handoff-current pass` |
| `export_html` | `<section id="resume">`, `Latest handoff: PE-047`, "promoted lessons" in the readiness table (U3: the panel renders population) |
| `gate_run` | `ready true` |
| `package_verify` | `verified true, dirty [], foreign [], review_current true`; no `data/.lock` after close |

## Phase B — the scratch copy

| Observation | Value |
|---|---|
| `entity_export` of the skill query | the file's `result` carries no `skill` |
| clean pointer emit (skill re-Approved, clean file) | package `CLAUDE.md` written; no `skill` key; root bytes constant |
| the guide = 5.0.0 body + 5.2.0's increment + marker 5.2.0 | `stock_merged [{declared 5.2.0, verified false, delta_missing "0/9", missing_by_release {"5.1.0": 11}, reason "11 of the 181 lines of 5.2.0 are absent (5.1.0: 11)"}]` |
| the skill file with the flush sentence | one `stale_references` entry (`skill:boundary-semantics (...)`, line 3); `skill: "tamheed:written-claims"` |
| the block | in the PACKAGE's `CLAUDE.md`; root bytes constant; warning `is current there; the stale-warning block was added there; the root file was left untouched` |
| second stale emit | `written []`; the package file's bytes unchanged |
| the guide restored + the sentence fixed | no findings; no `skill`; the package file byte-identical to the clean emit; root constant; warning `is current there; the stale-warning block was removed there; the root file was left untouched` |
| the hook (`source: compact`) over `PE-047` through the pointer | exit 0; 7 lines; the whole entry (`Do not carry:` present); no truncation marker |

## What this beat proves, and what it does not

Every mechanism of plans 129–132 fired under the engine's own tool functions with the predicted
class of result, on the recorded package and on a copy. It does not prove that a resuming MODEL acts
on the cue a result carries — findings_33 Q1 measured that in the field for the v5.1 cues (named →
invoked), and `findings_34` asks the same of the two new ones. The 4,000-character cap through
Claude Code itself is measurement M8 in the batch record.
