# Tamheed v5.1.0 — the findings_32 batch: the resume surface, the menu contract, and the five notes

Status: **EXECUTING (started 2026-09-26)** — index section "Field cycle findings_32" in
[README.md](README.md). Execution order: 120 → 121 → 122 → 123 → 124 → 125 → 126 → 127 → 128
(120 and 125 have no dependency; 122/124 need 121; 123 needs 122; 126 needs 120–125; 127 needs 126).

§0 RESULT: see the measurements below (filled as they land).

Read-only evidence this record rests on: ACMP `findings_32.md` (b2f9fe30), the ACMP feedback export
(`FB-019`–`FB-022`), the journal through `PE-1449`, ACMP's root `CLAUDE.md` / `AGENTS.md` /
`tamheed-package/CLAUDE.md` / `prm-next.md` (3,594 lines), ACMP's ten project skills and 90 memory files
(the cited lines re-read at path), the engine at every line cited in the approved plan
(`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`, the authoritative design +
interview record), the official Claude Code docs (hooks, plugins manifest, skills, settings; fetched
2026-09-26), GitHub issues #16538 / #45438 / #28305, and the interview rulings R1–R6 (21 answers).

## 0. The first execution step: the loading test (STOP-or-fallback)

Measurements before any plan is dispatched:

| # | Measurement | Expected | Result |
|---|---|---|---|
| M1 | Plugin `SessionStart` plain-text stdout reaches the model (`--plugin-dir` probe with a stub hook; the probe line names `bash` or `powershell`) | quoted back | **PASS** 2026-09-26, Claude Code 2.1.283: the model quoted the line back as `SessionStart:startup hook success: …`; the `command` (bash) path fired, `source='startup'`, `CLAUDE_PROJECT_DIR` set with forward slashes, cwd = the project |
| M2 | `uv run --no-project` of a stdlib script | ≤ 200 ms | 115 ms first, 77 ms repeat, 99 ms with imports (uv 0.9.21) |
| M3 | Lockless `store.load` on a copy of ACMP's `data/` (4,246 ids) | < 1 s | 147 / 119 / 117 ms |
| M4 | Menu / model-listing counts after plan 120 | 18 / 9 | _pending_ |
| M5 | Dry-run of every new surface on a lab-tracker copy (§5.1.3 of the plan) | classes recorded | _pending_ |

Fallback if M1 fails: ship `resume_hook.py` anyway; document the `settings.json` hook snippet (the
#16538 workaround) in `docs/install.md`; the resume block still arrives through `package_open` /
`server_info`. Degraded, not a STOP.

## 1. Weaknesses — the 5.0.0 brief (eleven + E8/E9 + "five"), then this plan's first draft (W1–W11)

The brief: E1/E2 (span rebuilt on any rendering change), E3 (21 files), E4 (`project_prompts` 4),
E5/E10 (pre-sweep counts), E6 (flush sentence in `SKL-004`), E7 (paste truncation), E11 (AUTO-LOAD line
in the mechanics file), E12 (`/reload-plugins` loads skills), E13 (menu 24); E8 (marker never true), E9
(slice-review addition already in the skill); the shipped README says "five" discipline skills, lists
six, omits `written-claims`.

The first draft: W1 fixture refreshed before the stamp; W2 the CLAUDE/AGENTS scan already runs and never
strips the note span (a second-emit false positive); W3 a silent escalation (obligations-table row);
W4 the FB-020 pointer assumed an FK could name a plugin skill; W5 hook output shape unspecified against a
JSON-path bug history; W6 the hook's cost unmeasured; W7 the `audit_record` hint mapping undefined; W8
"anonymised" undefined against lint 12; W9 the `@`-import guard unspecified; W10 an over-specified `na`;
W11 the brief's truncation risk. All fixed in the approved plan.

## 2. Assumptions — confirmed, rejected, unresolved

Confirmed at path / by measurement, rejected (sub-agent claims), and unresolved (U1–U7): the approved
plan §2 is the record. Unresolved items are closed here as they resolve:

- U3 closed (M3): 117–147 ms.
- U1 (389/490) stays a prior-session measurement; U2 (`commandWindows` doc status) — the probe shows
  which path fires; U4 = M1; U5 (ACMP's `verification_method` strings) — the brief asks; U6 (`_INJECT_RE`
  on handoff prose) — beat 23; U7 (exact key-set asserts on `handoff_emit`) — grep at 125.

## 3. Risks and mitigations

The approved plan §3 (plugin stdout path; `skills.jsonl` churn; fixture-before-stamp; detector false
positives; `_INJECT_RE` withholding; Windows shell; hook cost; injection posture; `handoff-current` on
every existing package; lint 12 on adopted prose; brief truncation) — each with its mitigation.

## 4. Changes made and why

The approved plan §4: plain-text hook output in the proven shape; handoff duty as a note sentence +
advisory (note stays v5); stamp before the beat; note-span stripping + a two-emit test;
`lessons-stranded` through `ids()` and only when `skills` has rows; the anonymisation, `@`-import and
`audit_record` mapping rules; `resume_hook.py` argument-less and `source`-aware; §0 measurements.

## 5. The design, concretely

The approved plan §5.2, per plan 120–128, with expected outputs.

## 6. Refined execution plan

| # | Plan | Depends on | Status |
|---|---|---|---|
| 120 | [Menu contract, skill hints, note sentence, README wording](120-menu-contract-and-skill-hints.md) | — | PLANNED |
| 121 | [Migration 007: `handoff` kind + `skills.upstreamed_to`](121-migration-007-handoff-and-upstreamed-to.md) | — | PLANNED |
| 122 | [Resume block, `handoff-current`, `lessons-stranded`, Resume panel](122-resume-block-and-advisories.md) | 121 | PLANNED |
| 123 | [The SessionStart hook](123-session-start-hook.md) | 122 | PLANNED |
| 124 | [Skills and the AGENTS template](124-skills-and-agents-template.md) | 121 | PLANNED |
| 125 | [handoff_emit scans](125-handoff-emit-scans.md) | — | PLANNED |
| 126 | [Docs + diagrams sweep](126-docs-and-diagrams-sweep-findings-32.md) | 120–125 | PLANNED |
| 127 | [Version stamp, then lab beat 23 + evals](127-stamp-then-lab-beat-23.md) | 126 | PLANNED |
| 128 | [Tag v5.1.0, this repo, the ACMP brief, close-out](128-release-v510.md) | all | PLANNED |

Status values: PLANNED / IN PROGRESS / DONE.

## 7. Approval checkpoint

Approved by the operator on 2026-09-26 after the devil's-advocate revision (ExitPlanMode). Execution
begins with §0.
