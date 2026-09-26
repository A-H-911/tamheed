# Tamheed v5.2.0 — the findings_33 batch: the two field defects, the sixteen (and forty-four) rules, the cues that never fired

Status: **EXECUTED — v5.2.0 tagged on the release commit (this record's commit; CI green),
2026-09-26** — index section "Field cycle findings_33" in [README.md](README.md). Commits: 129
`8a75914`, 130 `b72296e`, 131 `96506c3`, 132 `9424a12`, 133 `8975009`, 134 `7107122`; 135 = the
close-out commit that carries this record, the brief and the index — the tag sits on it. Execution
order 129 → 130 → 131 → 132 → 133 → 134 → 135 (129/130/131 have no dependency; 132 needs 131's wording;
133 needs 129–132; 134 needs 133; 135 needs all).

Read-only evidence this record rests on: ACMP `findings_33.md` (`b1a1c666` → `30a33887`), the feedback
rows `FB-023`–`FB-025`, the journal `PE-1450`..`PE-1473`, `skills.jsonl` / `lessons.jsonl`, the three
control files, `prompts/prm-next.md` (57 lines), `.claude/memory/prm-next-carried-rules.md` (113 rules,
every candidate re-read), the retired skill files at `c85e68d8`; the engine at every line cited in the
approved plan (`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`, the design +
interview record); the official Claude Code docs (hooks guide, plugin manifest; 2026-09-26 — silent on
a hook-output size cap and on `/reload-plugins`); the interview rulings R7–R14.

## 0. Measurements (the plan's §5.1)

The replay harness: `acmp_replay.py` over a read-only COPY of ACMP's package + control files + skills
(scratchpad), the engine in-process (the same code path the MCP tools call). Two artefacts of the copy,
not of the engine: the note's path line differs from the original (so the first emit rebuilds the span
once), and the server is not plugin-hosted in-process (so `.mcp.json` is written once).

| # | Measurement | Before (5.1.0 engine) | After (129–131) |
|---|---|---|---|
| M1 | `_stock_merged_check` over ACMP's deleted `integrity-check.md` (`c85e68d8`), marker 4.9.0 | `verified true, delta_missing 0/9` | `verified false, 0/9, missing_by_release {4.2.1: 2, 4.5.0: 18, 4.6.0: 18}`, reason "38 of the 62 lines of 4.9.0 are absent (…)" — the field's 38/62 |
| M2 | `handoff_emit` on the copy (no stale hit, no marker) | `stale_references [] restated_content [] oversized_prompts [] stock_merged []`, root `unchanged` | identical; no `skill` key (no finding); package `CLAUDE.md` `unchanged` on the second emit |
| M3 | `readiness_check` — `lessons-stranded` population | `{table: lessons, rows: 111}` (the whole table) | `{table: lessons, rows: 75, unit: "promoted lessons"}` (the 75 Promoted rows, measured on `lessons.jsonl`) |
| M4 | `handoff-current` on the copy | pass, population 360 work entries | pass, 360 |
| M5 | `entity_query` result keys | `count, next_after, ok, rows, total` | + `skill` |
| M6 | The hook (script) over the copied `PE-1473` (1,735 chars, 12 lines) | the whole entry, 21 lines, no marker | same (cap 4,000 after 132) |
| M7 | Byte-identity cycle (stale → stale → clean), non-pointer and pointer | — (5.1: two extra newlines; root written in the pointer case) | pinned by two contract tests: bytes identical; root constant; second stale emit `unchanged` |
| M8 | The 4,000-char entry through Claude Code (`--plugin-dir`, the M6 recipe of 5.1) | — | **PASS** 2026-09-26: a 3,615-char, 16-line handoff (`PE-048` on a scratch copy) written into a scratch project; `claude --plugin-dir plugins/tamheed -p …` quoted the block's first line and the entry's LAST line (`Line 15 …`) verbatim and answered "no" to a `for the rest` marker — Claude Code did not cut a block that size (U1 settled; the docs are silent on a cap) |
| M9 | Lab beat 24 (plan 134) | — | every class held on the second run; the first run's phase B compared bytes across a legitimate span change (owned in plan 134); evidence `evidence/lab-continuation-report-134-2026-09-26.md` |

Skill file sizes after 132 (lines): measurement-evidence 165, written-claims 136, reading-the-record 141,
ci-evidence 114, operator-interview 138, test-evidence 132, package-writes 208, session-handoff 91;
lint 12 green over all 25 skills.

## 1. Weaknesses owned (the 5.1.0 brief's fourteen, and this plan's own)

The brief: E1 tag ≠ marketplace HEAD; E2 "first close" (dump writes every table on every commit); E3
`handoff-current`'s population wording; E4 `stock_merged` predicted false, read true (the defect);
E5 the scans' scope; E6 paste damage despite the split; E7 an under-scoped diet; E8 seven twins
(eight); E9 a second copy of the handoff sentence; E10 a bug already sent; E11 an order that made a
scan's silence vacuous (Approved rows only); E12 a wrong claim about G-PROGRESS; E13 the root
`CLAUDE.md` block (the defect); E14 `disableAllHooks` disables every hook. This plan's own, found by
the review before execution: W1–W14 in the plan file (the two-skill cue count; the legacy-root block;
the span-vs-block warning; the export leak; the template test; the strip's ceiling; the "never
merged" wording; the scan scope; the missing cap test; the prediction method; the FB fragments; the
tag ordering; the README history key; the sub-agent's list).

## 2. Rulings (R7–R14, binding)

| # | Ruling |
|---|---|
| R7 | `stock_merged.verified` = every non-blank line of the DECLARED release's body; `missing_by_release`; `delta_missing` kept; report-only. |
| R8 | `entity_query` → `tamheed:reading-the-record` on every result; `handoff_emit` → `tamheed:written-claims` on any finding (R4 revisited on Q1's evidence). |
| R9 | The brief is a committed file read by path (R5 revisited: paste damage twice). |
| R10 | The AGENTS template points at the note's obligations table. |
| R11 | The hook prints 25 lines / 4,000 chars (= the resume block's cap); the skill says so. |
| R12 | `handoff-current` keeps counting engine transitions; the skill teaches status moves → handoff → commit → bind. |
| R13 | `system:skill-guard` journalling on a skill row's status move or pointer arrival. |
| R14 | FB-025's 16 plus every verified generic gap, one sentence each. |

## 3. Execution

| # | Plan | Status |
|---|---|---|
| 129 | [`stock_merged` verifies the whole declared release](129-stock-merged-whole-body.md) | DONE `8a75914` |
| 130 | [The stale-warning block's home, text and removal](130-stale-block-home-text-removal.md) | DONE `b72296e` |
| 131 | [Two more cues, the stranded rule's population, the skill guard](131-cues-populations-skill-guard.md) | DONE `96506c3` |
| 132 | [The sixteen and the forty-four rules, the template's pointer, the hook's caps](132-skills-template-hook-caps.md) | DONE `9424a12` |
| 133 | [Docs + diagrams sweep](133-docs-and-diagrams-sweep-findings-33.md) | DONE `8975009` |
| 134 | [The version stamp, then lab beat 24 + evals](134-stamp-then-lab-beat-24.md) | DONE `7107122` |
| 135 | [Tag v5.2.0, the brief file, close-out](135-release-v520.md) | DONE — the release commit; tag `v5.2.0` |

Post-tag docs commit, owned: the advisor's review after the tag found the brief's carried-rules sum
wrong (36 + 30 + 33 ≠ 113 — all 44 generic candidates entered the skills as ~30 sentences; the 36
"covered" and 33 "project-specific" are the classifier's classes, not re-read). The fix is docs-only
and lands AFTER the tag, deviating from plan 135's "nothing after the tag": the plugin tree is
byte-identical to the tag, so the brief's install check became tree equality (`git diff v5.2.0
HEAD -- plugins/tamheed` empty) instead of sha equality. The plan file's "dropped CI-3 475" was a
phantom drop (the classifier had listed it as covered).

Execution notes (owned as they land): (1) plan 129's `prompts/README.md` wording was reverted before
its commit — the guide is a stock body with history and lint 9 requires it to equal its newest key,
so the text lands with the `5.2.0` key in 134 (the plan file had it in 129); (2) plan 130's first test
run failed on CRLF: the test wrote the root with platform newlines and compared LF bytes — the test
writes LF and the block regex became CRLF-tolerant; (3) plan 132's cap test asserted the OLD handoff id
absent from the output, but it legitimately appears in the "Latest journal" line — re-aimed.
