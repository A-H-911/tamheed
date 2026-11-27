# PARKED: the loop findings, the requirement cascade and the contradictions

> **Dated note, 2026-11-18 (the 6.8.0 round, plans 249-253).** That round takes 6.8.0, the plan numbers
> 249-253 and ADR-0005. This plan therefore moves to **6.9.0**, takes new plan numbers at its return, and its
> ADR becomes **ADR-0006**. The round changes `standup_facts.py`, `standup_page.py`, the standup tool, the
> skills `standup`, `session-handoff` and `package-writes` (section 1), and adds `standup.js`: the Return
> checklist's `git diff 7d5a028..HEAD` will show them.

> **Dated note, 2026-11-27 (the 6.9.0 round, plans 256-263).** That round takes 6.9.0 and the plan
> numbers 256-263, and its ADR is **ADR-0007** (R163). This plan therefore moves to **6.10.0**. It keeps
> migration 013 and **ADR-0006** (R145). The round changes `tamheed_server.py` (entity_upsert, the
> readiness rules), the slate files, and the skills `package-writes`, `orient-resume`, `slice-kickoff`
> and `operator-interview`: the Return checklist's `git diff 7d5a028..HEAD` will show them.

> **THIS EXIT FROM PLAN MODE APPROVES THE PARKING STEPS ONLY — NOTHING FROM THE PLAN BELOW.**
> The parking steps (operator's choices, 2026-11-17):
> 1. Copy this file, verbatim, to
>    `plans/PARKED-2026-11-17-loop-findings-and-requirement-cascade.md` in the tamheed repo. Leave
>    it UNCOMMITTED until the operator says. It is untracked, so `git clean` would remove it.
> 2. A memory entry plus its `MEMORY.md` line: the path, the base `7d5a028`, "unapproved,
>    re-verify first", and "remind the operator at every session start".
> 3. Fix the stale plan 248 memory: it is committed `7d5a028`, pushed, CI 44067156789 green, and
>    its findings went to this parked plan.
> 4. A session-only daily reminder (CronCreate). It lives only while this session is open, and
>    expires after 7 days.
>
> No engine, text, test, rehearsal, commit or push from the plan below.

> **PARKED 2026-11-17 — NEVER APPROVED. Do not execute.** The operator parked it for other work
> that may change it. R9 is still open. The plan numbers 249–257 and the release "6.8.0" are
> PROVISIONAL: the other work may take them. On return, run the **Return checklist** below
> FIRST, put every ruling whose premise moved back to the operator, check with the advisor, and
> resubmit in the six-section form before any ExitPlanMode.

## Base (measured 2026-11-17, at parking)

| Item | Value |
|---|---|
| HEAD (main) | `7d5a0280f0f04fd8348317232488051e421606c9` (plan 248 record, CI 44067156789 green) |
| Newest tag | `v6.7.0` |
| plugin.json | `6.7.0` |
| Migration head | `012_standup_withdraw.sql` (schema 12) |
| Claude Code | 2.1.326 |
| Working tree | clean |

## Return checklist (run before anything else)

1. **The drift.** Run `git log --oneline 7d5a028..HEAD` and `git diff --stat 7d5a028..HEAD`. For
   every changed file this plan cites, re-read each cited file:line. List each claim that moved.
2. **Shape changers.** Check each of these:
   - a new migration (is 013 taken? does any migration add a column?);
   - a new tag, which changes the old arm `v6.7.0`;
   - the counts this plan pins: 28 skills (1 front door, 18 scenario, 9 discipline), 17 bindable,
     9 eval cases, the 7 schema pins, and lab-tracker's 136 assertions.
3. **Re-measure, each with its expected result:**

   | Measurement | Expected |
   |---|---|
   | F9 replay in memory (Met then Not-met, stored `Approved`, load) | reads `Implemented` |
   | The 4 shipped packages | load with no requirement status change |
   | The evals step | ≈20 s for ≈180 assertions |
   | One recorded package | ≈165 KB |
   | `store.py` fingerprints | taken from disk bytes before the replay |
   | The CHANGELOG pre-stamp heading | `## [Unreleased]` |
   | `blocks-lifted` | lists open rows with every blocker settled, uncapped |

4. **Every SUB-AGENT claim marked [S] below is re-verified** before it shapes a step.
5. **Rulings whose premise moved go back to the operator** (`tamheed:operator-interview`), then
   the advisor, then the six-section devil's-advocate form, then ExitPlanMode.
6. **Field state.** Whether ACMP or Jisr has started running the loop (R3), and fresh exports
   for plan 256.

## Context

Plan 248 (`7d5a028`, CI 44067156789 green on 11 jobs) ran `/tamheed:loop-iteration` end to end for
the first time and recorded F1–F8. The operator asked for:

- a deep study, with the impact radius on every capability;
- full tests, and deep rehearsals of all capabilities and of the loop in many scenarios;
- documents and diagrams, and contradictions detected and resolved;
- research on loop practice (Ralph and others);
- an interview per aspect, and no over-engineering.

**What the study found beyond F1–F8:**

- **F9, an engine defect.** `store.load` replays verdicts with `trg_requirement_auto_advance` live.
  A requirement set back to `Approved` after a regression reads `Implemented` after a reopen, and
  the first write of that session rewrites `requirements.jsonl`. Disk fingerprints are taken
  before the replay (`store.py:635-657`), so the flush sees a difference. It was measured in
  memory; it is latent in all 4 shipped packages.
- **F4 is wider.** The first verdict of ANY package fails G-PROGRESS for every other criterion.
- **The loop's brakes had no baseline.** Conditions 1, 5 and 6 compare with "the previous pass",
  which a fresh session never saw. Every 248 pass declared "brakes clear" without one; its
  journal rows hold neither the gate result nor the line.
- **17 contradictions** (table C), and **three wrong claims** in the committed 248 record.

**Sources:** three explorations, two design passes, three advisor reviews, nine interview rounds
and two devil's-advocate reviews (this is the second).

**Outcome:** 6.8.0 MINOR:
- one migration (013) and ADR-0005;
- a cascade in `audit_record`;
- a review-page change;
- text fixes across the bundle and the docs;
- a rehearsal recorded as two eval cases that `check.py` guards from now on.

## Rulings (operator, 2026-11-17)

| # | Ruling |
|---|---|
| R1 | Scope: everything found |
| R2 | The 248 record gets a dated corrections section; the original text is kept |
| R3 | Neither field runs the loop today |
| R4 | F1: pick the first `Approved` work item by phase `sort_order`, slice `sort_order`, then the id's number. `Review` is never re-picked; a human returns reworked work to `Approved` |
| R5 | F2: skip a blocked item (a `blocked_by` far end not settled). `stop=blocked` only when every remaining `Approved` item is blocked |
| R6 | F2: `stop=` is one of nine words, owned by loop-guard: `gate-degraded`, `not-converging`, `scope-needed`, `readiness-blocked`, `defect-spike`, `no-progress`, `store-error`, `backlog-empty`, `blocked`. The line's fields and order are unchanged |
| R7 | F3: every pass ends with one package-only commit of `data/` |
| R20 | Except a `store-error` stop, which commits nothing |
| R23 | A pass that starts with only package `data/` dirty commits it package-only first. Dirty source or tests at the start is `stop=store-error` |
| R22 | Condition 6 becomes "two consecutive passes made no code commit and moved no work item's status" |
| R25 (corrected) | Every pass ends its journal with ONE row written after its last `gate_run`: the escalation row on a stop, otherwise a `note` row. That row carries the ITERATION line and the open-defect count. Step 2 reads the newest such row as "the previous pass" for conditions 1, 5 and 6 |
| R8 | F9: migration 013 drops the trigger. The cascade moves into `audit_record` (same transaction). Each move writes a journal row |
| R9 | The advance's verifier set is DEFERRED to after the field replay (plan 256). Until then any latest `Met` advances. The rule lives in one function |
| R10+R21+R24 | Move-back: an `Implemented` requirement returns to `Approved` when a live criterion's newest RECORDED verdict is `Not-met` or `Partial`, or a `Pending` regrade. A placeholder and a missing verdict never move it back. A missing verdict still blocks the advance |
| R11 | F4: texts teach the Pending placeholder (at the first verdict, and for every later criterion). `audit_record`'s result lists live criteria with no verdict (`no_verdict`) |
| R12 | Work-item guard: fix the TEXT. Only phase and slice are readiness-guarded |
| R13 | The review page shows "no verdict" (class `missing`) apart from a stored `Pending` (`ungraded`) |
| R14 | Migration 013 recreates `v_backlog` in the R4 order (same columns and rows) |
| R15 | Waiver texts follow the engine |
| R16 | 6.8.0 MINOR. Both fields replayed on copies before the tag. Two pinned, rehearsed briefs |
| R17 | The loop matrix with old-text controls, AND a headless beat for all 28 skills |
| R18 (confirmed with costs) | Everything recorded as eval cases. Measured: about 40 packages (165 KB each, about 6.6 MB), about 150 assertions (the evals step 20 s → about 37 s on all 11 CI jobs), and a refresh over all of them at any migration that adds a column. Raw transcripts are never committed |
| R19 | Rehearsal cap 150 USD, ledger-enforced. A failed or VOID item may be re-run once |

## 1. Weaknesses of the previous plan (found by this review)

1. **R25's mechanics were impossible as written.** The work-done row is written at step 5,
   before step 6's `gate_run`, so it cannot carry `gate=`. Corrected: one last row after the last
   `gate_run`.
2. **The CHANGELOG step would have failed lint 4 on every commit before the stamp.** An undated
   `[6.8.0]` heading would make lint 4 compare plugin.json 6.7.0 with "6.8.0". Plan 246 used
   `## [Unreleased]`; this round does too.
3. **The F9 red test was mis-specified.** A pure close/open byte compare may pass at HEAD. The
   test must read after the reopen (`Implemented` at HEAD), then write once, then byte-compare.
4. **`no_verdict` was unbounded.** After a field's first verdict it could list every criterion on
   every call. It now takes the existing id cap plus a total.
5. **L06 (fresh package) would have lacked the project note.** `package_create` in-process does
   not wire the root CLAUDE.md (`_WIRE_ROOT` is false), so the build calls `handoff_emit` as
   `setup_248.py` did.
6. **The briefs missed a field-visible effect.** A reworded note makes `handoff_emit` warn "the
   tamheed:note span … was rebuilt", which reads like a hand-edit alarm.
7. **The brief rehearsals had no budget.** They are now inside the 150 USD reserve.
8. **Two interpretations rode as rulings.** R24's "regrade" and the retire case are now named
   defaults (D10, D11).
9. **The eval cost was stated as an estimate.** It is now measured and confirmed (R18).

## 2. Assumptions

**Confirmed by direct read or measurement:**
- **The loop path:**
  - the tag `v6.7.0` exists;
  - `audit_record` is the only live verdict writer; `record.py:121` iterates `plan.audits`,
    which nothing fills;
  - no view depends on `v_backlog`; only `record.py:232` and `standup_facts.py:286` read it;
  - work items carry `phase_id`;
  - `entity_query` takes `search` and `after_id`.
- **`blocks-lifted`** lists open rows whose every blocker is settled. Its `lifted` map names the
  settled blockers, and `rule()` does not cap entities. So the picker's blocked test is sound
  (D3).
- **The note:**
  - `_apply_note` rebuilds the span on any difference, with a warning, so no marker bump is needed;
  - the pinned phrases are `test_mcp_contract.py:3409-3416` (incl. "**Review** (done-claimed)",
    "`scope-change` row (`SC-`) FIRST", "verified_by") and the "Never Met without proof" check
    at `:3460`.
- **The guide's extractor** keys each `INSERT` to its enclosing top-level `def`
  (`extract.py:448-461`), so the journal insert stays inline in `audit_record`.
- **Tests and lints:**
  - `test_db_roundtrip.py:169-178` is the raw-insert cascade test, and it gets inverted;
  - the eval-spec lint requires `id`, `intent`, `input`, `deterministic_assertions` and `rubric`;
  - the schema pins are `test_mcp_contract.py:244, 4571-4572, 7226-7227` and
    `test_resume_hook.py:100, 145, 483`.
- **Measured costs:** the evals step takes 20 s; one recorded package is 165 KB.
- **The username** already appears in 51 committed files. The e-mail and organization id appear in
  none, and must never.
- **All earlier confirmations stand:**
  - F9's replay;
  - the trigger is the only cross-table writer;
  - `verified_by` is unread;
  - only phase and slice are guarded;
  - G-PROGRESS semantics;
  - the Pending placeholder concept;
  - frozen DDL;
  - `handoff-current` counts `work-done` and `transition`;
  - the standup's `system:work-bind` by name;
  - `lab-tracker` pins the stock body and the review page.

**Rejected:**
- the old F5 and F8 claims;
- "`v_backlog` drives the loop";
- "a note rewording needs a marker bump";
- "an undated `[6.8.0]` heading is safe";
- "a close/open byte compare proves F9".

**Unresolved (each has a step):**
- R9's verifier set (256, then a ruling);
- whether `C:\tamheed-reh` is writable (the B0 smoke; fallback D6);
- the loop's behaviour in L05, L08 and L13;
- the invoke rate of the 8 model-only skills at n=1.

**Research, kept apart from my reasoning:**
- **Sources:** Huntley and the Ralph Playbook, snarktank/ralph, Anthropic's ralph-loop plugin,
  Claude Code `/loop`, ralphctl, Codex `/goal`, continuous-claude, Aider, SWE-agent, and the ECC
  loop skills.
- **Closed terminal statuses** (ralphctl, SWE-agent, Codex). ralphctl forbids parsing the reason
  string, and the ralph-loop README admits one string cannot tell SUCCESS from BLOCKED.
- **Claimed apart from verified** (ralphctl, ECC).
- **A dirty tree after a run is corruption** (ralphctl).
- **Hard caps everywhere,** and no-progress breakers.
- **Not covered:** OpenHands, Goose and Cline/Roo.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The cascade change moves field requirements | 256 replays both fields on copies under the post-013 engine and counts each set before R9 is ruled and before the release |
| A raw SQL insert no longer cascades | Intended. The roundtrip test is inverted. `record.py`'s verdict path is dead |
| The new journal rows ripple | The cascade's `transition` rows make `handoff-current` name an earlier handoff (intended). R25's last row is `note` or `escalation`, not counted. The standup's lists ignore `system:requirement-advance`; "Requirements done" follows status both ways. A ripple test in 250 |
| Journal ids shift | Full suite per plan. Evals use `--min` counts |
| `no_verdict` floods a large field | The existing id cap, plus `no_verdict_total`. 256 measures each field's G-PROGRESS failures |
| The guide's pins and figures drift | Each server plan restores `diagrams.py` and `test_user_guide.py` from HEAD, runs `shift_221.py` once, hand-edits `TOOL_EFFECTS["audit_record"]`, rebuilds |
| Lint 4, 7, 12 or 14 refuses | CHANGELOG under `## [Unreleased]` until the stamp. The migration is named there (lint 7). Sentences ≤25 words, no semicolons, no rejected words, no id-shaped tokens in skills |
| The fixture follows the stamp | `refresh_lab_680.py` carries `lab-tracker` to the 6.8.0 stock body and review page |
| The note rewording reaches fields | Both briefs quote the "span was rebuilt" warning as expected |
| Rehearsal nondeterminism and n=1 | n and arm beside every claim. Old/new controls. The reserve allows n=2 on headline claims |
| The old arm runs the old engine too | Claims tagged [T] text or [E] engine. [E] proven in-process for free. Arm proof from `debug.log`; VOID on mismatch |
| Cost overrun or uncharged voids | One ledger. A void with no reported cost is charged its session cap. Batch caps total 91; the reserve of 59 includes the brief rehearsals (about 6) |
| Private data in committed evidence | A neutral root. The recorder reads the forbidden strings (home path, account name, e-mail, organization id) from an uncommitted local file, refuses on a hit, and the committed scripts hold none. A `grep-tree-absent AppData` assertion |
| Windows locks after a timeout | Kill the process tree. The L14 holder closes on stdin. A live lock stops the batch |
| 40 snapshots go stale | `reh.py refresh` (migrate + verify) whenever a migration adds a column |

## 4. Changes made by this review, and why

| Change | Why |
|---|---|
| R25's last row comes after the last `gate_run` | So it can carry `gate=` (operator confirmed) |
| `## [Unreleased]` until the stamp | Lint 4 |
| The F9 red test reads, writes, then compares | The fingerprints come from disk before the replay |
| `no_verdict` capped, plus a total | Field size |
| L06 calls `handoff_emit` | The note is wired only by a served process |
| The briefs name the rebuild warning, the result keys, the review-page change and the `handoff-current` effect | Field-visible effects |
| The brief rehearsals sit inside the reserve | Budget completeness |
| D10, D11 and D12 added as defaults | They were interpretations riding as rulings |
| R18 confirmed with measured costs; D6 confirmed | The operator's word |

## C. The contradictions and their resolutions

| Id | Where | Resolution | Plan |
|---|---|---|---|
| C-a | The guide's ITERATION line (`render.py:739`) has drifted from `loop-iteration/SKILL.md:55` | The guide reads it from the skill (`extract.facts()["iteration_line"]`); a test pins them equal | 252 |
| C-b | "Phase/slice order" vs id-order tools | R4 in the skill; `v_backlog` mirrors it (R14) | 250, 252 |
| C-c | The close-outs commit `data/`, but drift-register reminds the operator | The end commit (R7, R20); `package-writes` §4/§9; `drift-register:60` "in a loop the end commit covers it" | 252 |
| C-d | The page shows "Pending" for none and for stored | R13 | 251 |
| C-e | The note says work items are guarded | R12 text | 253 |
| C-f | What `Implemented` means for a requirement (`governance.md:92`, `entities.md:60/244…700`, `handoff.md:89-92`, `README.md:203`, `skills/tamheed:220`, `architecture.md:181`, `workflow.md:206`) | `audit_record` moves it both ways (R8–R10), journaled; the verifier set follows R9 | 254 |
| C-g | The glossary (`content.py:1716`) | Requirements take plain writes too, and `audit_record` moves them | 250 |
| C-h | Label C4 vs C5 | "The advance (C5) cascades in the same transaction (C4)" | 250 |
| C-i | `prompts/README.md:126` "a verdict" is the operator's | "a review verdict" | 252 |
| C-j | "Views cannot drift" | True again after F9; name the one write | 254 |
| C-k | Waiver scope and expiry | R15 | 252, 254 |
| C-l | "Narrated" = without four fields | = empty `evidence` | 254 |
| C-m | A void disposition vs `retired_in` | A cancel sets both | 254 |
| C-n | `ste-rewrite:38-40` "starts unverified" | It starts with a placeholder | 253 |
| C-o | `progress-sync:35` omits Pending | Add it | 253 |
| C-p | `slice-review`: who finishes a requirement | Recording your verdict moves it; the verifier words follow R9 | 253 |
| C-q | `package-writes` §11 (no rule-silencing write) vs a placeholder | §12: the placeholder's `evidence` says so; it shows as "ungraded" | 253 |

## L. The loop matrix (plan 255)

The new arm runs first; the old arm runs only where the new result is valid.

**The base:** `lab-tracker` plus the 248 code (6 tests green), the setup commit bound, and the
note wired by `handoff_emit`. Seeds go through the tools in `modes.md` §3 order, signed
`human:rehearsal-operator`, and end with a package-only commit.

**Every new-arm pass is checked for:**
- the stop word is one of the nine;
- a clean tree at the end;
- zero mixed commits;
- no `force`/`operator_confirm` in any tool input;
- no lock left;
- its last journal row carries the line (R25).

| # | Scenario [T/E] | Seed | Expected under the new text | Arms, n |
|---|---|---|---|---|
| L01 | Backlog empty + the end commit [T] | The base | `backlog-empty`; the escalation row carries the line; a package-only commit; clean tree. The old arm leaves it dirty | both, 1 |
| L02 | Picker gauntlet [T] | PH-3 (sort 2): SL-010 (sort 4), SL-005 (sort 5). PH-2 (sort 3): SL-004. In SL-010: WBS-9 at Review (faded behind 4 newer rows), WBS-10 blocked by OQ-001, WBS-100 and WBS-12 Approved. WBS-11 in SL-005; WBS-5 in SL-004 | Only **WBS-12**. Each wrong pick names its broken rule | new 2, old 1 |
| L03 | Skip blocked, then `blocked` [T] | WBS-5 blocked by OQ-001, WBS-6 Approved | p1 WBS-6 to Review; p2 `blocked` | both, 1 (2 passes) |
| L04 | Readiness blocked + the cascade [T+E] | WBS-5/6 at Review, WBS-7 Approved; AC-009 the only criterion of a new FR-008 | `readiness-blocked`; FR-008 as R9 rules | both, 1 |
| L05 | Regression moves back [E] | FR-009 Implemented on human Mets, then a human Not-met | New: `Approved` plus a journal row. Old: stays. The pass: `backlog-empty` (D5) | both, 1 |
| L06 | Fresh package, first verdict [E+T] | `package_create` + `handoff_emit`, zero verdicts, 2 Approved items | Placeholders recorded; `gate=pass`. Old: `gate=fail` | both, 1 |
| L07 | Drift registered first [T] | A driver commit implementing WBS-5, unrecorded | Bound before new work; then WBS-6 | both, 1 |
| L08 | Dirty start, data only [T] | An uncommitted escalation row | R23: a package-only commit first | both, 1 |
| L15 | Dirty start, source [T] | An uncommitted `tracker.py` edit | `store-error`; nothing touched; no commit | both, 1 |
| L09 | Gate degraded [T] | A previous-pass row with `gate=pass` (R25 format), then an MVP FR with no edges | `gate-degraded` | both, 1 |
| L10 | Not converging [T] | Two agent Not-met verdicts in a row on the next pick's criterion | `not-converging` | both, 1 |
| L11 | Scope needed [T] | An item contradicting Met AC-002 | `scope-needed`; SC count unchanged | both, 1 |
| L12 | Defect spike [T] | A previous-pass row with its open-defect count, then 3 new defects | `defect-spike` | both, 1 |
| L13 | No progress [T] | Two previous-pass rows, no commit and no status move between them | `no-progress` | both, 1 |
| L14 | Store error [T] | A live lock holder | `store-error`; zero writes; no unlock; no commit | both, 1 |

## S. The 28 skill beats (plan 255)

- **Turns.** Turn 1 is the slash command alone, or a plain request for a model-only skill.
  Later turns use `--resume` with neutral fixed words.
- **Observation.** A slash skill shows as its `<command-name>` tag. A model-only skill shows as a
  `Skill` call or a Read of its file; a miss at n=1 is an invoke-rate finding.

**The 7 touched skills, both arms, fresh workspaces:** slice-kickoff, progress-sync,
drift-register, slice-review, release-close-out, ste-rewrite, package-writes.

**The other 21, new arm, grouped:**

| Group | Skills |
|---|---|
| G1 read-only | orient-resume, package-onboarding, integrity-check, loop-guard, reading-the-record, measurement-evidence, ci-evidence, generate-report |
| G2 SL-004 | defect-triage, test-evidence, plain-english, written-claims, operator-interview, session-handoff |
| G3 lifecycle | phase-close, replan-deferred, register-liveness, skill-promote, standup |
| G4 empty repo | `tamheed` (the minimal-brief input) |
| — | loop-iteration is the matrix |

**Expected spend:** about 68 USD; batch caps total 91; reserve 59.

## 5. Execution plan

One commit per plan, each on the operator's word. Each runs `python check.py` green on 3.13 and
3.10.

**249: the round record (docs).**
- `plans/249-field-round-6.8.0.md`: rulings, research with citations, tables C/L/S, defaults.
- The 248 record gets §8 "Corrections (2026-11-17)": F1's proposal, F5, F8's work-item line, and
  the "brakes clear" claims, each with the measured fact.
- Plan rows 249–257. **Output:** docs only.

**250: the engine, red tests first.**
- **Red tests** (each fails at HEAD):
  - `test_raw_verdict_insert_does_not_cascade`;
  - `test_backlog_orders_by_phase_then_slice_then_number`;
  - `test_a_requirement_set_back_stays_set_back_across_reopen`: Met → set back → close/open →
    read `Approved` → one write → `requirements.jsonl` still says `Approved`;
  - `test_audit_record_moves_a_requirement_both_ways_and_journals_each`: a Met advances. A
    Not-met, a Partial and a Pending regrade move it back. A placeholder, a missing verdict and a
    Pending after only a Pending do not. A `transition` row with actor
    `system:requirement-advance`;
  - `test_audit_record_names_live_criteria_with_no_verdict`, with the cap and the total;
  - `test_the_advance_rule_is_one_function`;
  - the ripple test (`handoff-current`, the standup lists).
- **Engine:**
  - `013_requirement_advance.sql`: drop the trigger; recreate `v_backlog`; a header correcting
    `schema.sql:577` and `:805`.
  - `audit_record`:
    - `_requirement_advances`;
    - the move-back;
    - the inline journal INSERT;
    - result keys `requirements_moved`, `no_verdict` and `no_verdict_total`, present only when
      non-empty;
    - `_AUDIT_RECORD_DESC`.
- **Docs and pins:**
  - ADR-0005, which supersedes ADR-0001's trigger clause; ADR-0001 gains the pointer only.
  - The 7 schema pins, 12→13.
  - `CHANGELOG.md` under `## [Unreleased]`, naming `013_requirement_advance.sql`.
  - `tests/README.md:15`.
  - Guide (EN and AR): delete `trigger.trg_requirement_auto_advance`. Rewrite `block.LIFE`,
    `col.acceptance_criteria.requirement_id`, `.retired_in`, `status.Implemented`,
    `glossary.implemented.def`, `suite.test_db_roundtrip.py` and `view.v_backlog`.
    `TOOL_EFFECTS["audit_record"]` by hand.
- **Validation:** each red test red at the parent commit and green after; `check.py`; the
  selftest.

**256: the field replay (a measurement, then the R9 ruling).**
- **Step 0:** a fresh Jisr export and the ACMP path, from the operator. Copies only, `python -I`.
- **`replay_256.py`** prints counts only:
  - R9-all and R9-any;
  - NULL `verified_by`;
  - the move-back sets by cause;
  - advance-pending;
  - G-PROGRESS failures (which size `no_verdict`);
  - open, verify, no file moved.
- **Then the operator rules R9.** An exclusion is a one-line change plus its test (250b).

**251: the review page (R13).** `export_html.py:929-934` and `:175-179`; test
`test_export_html.py:420`.

**252: the loop texts (R4–R7, R20, R22, R23, R25; C-a, C-b, C-c, C-i, C-k part).**
- **loop-guard:**
  - it owns the nine words, and condition 6 is reworded;
  - conditions 1, 5 and 6 read the newest line-carrying row, from the resume block or by
    `search="ITERATION:"` paged to the newest;
  - "On stop": the escalation row with the line → `package_close()` → the package-only commit
    (not on `store-error`) → the line.
- **loop-iteration:**
  - step 1: the dirty-start rule;
  - step 3: `entity_query("wbs-item", status="Approved")` paged by `after_id`. Order by phase and
    slice `sort_order`, then id number (D1). A blocked item is free when `blocks-lifted` names it
    (D3);
  - step 6: a last `note` row after `gate_run`, carrying the line and the open-defect count, then
    the end commit;
  - the ITERATION line stays byte-identical.
- **Also:** `package-writes` §4/§9; `drift-register:60`; `prompts/README.md` (the nine words,
  C-i, C-k), whose body goes into `stock-history.json`.
- **Guide:** `iteration_line` read from the skill; prose `section.skills.styles.2/3`,
  `workflow.fully-auto.s1/s2/s4`, `dia.wf.fully-auto.s4`, `skill.loop-iteration`.
- **Tests:** `test_iteration_line_is_the_skills` and `test_stop_words_agree`. The existing pins
  at `test_mcp_contract.py:6065-6071, 278-281` still pass.

**253: placeholders, the note, slice-review (R11, R12; C-e, C-n to C-q).**
- **The placeholder sentence goes wherever a criterion is created:**
  - `modes.md` §3 step 4;
  - `package-writes` §1/§12;
  - `progress-sync:35`;
  - `slice-kickoff` step 5;
  - `ste-rewrite:38-40`;
  - `register-liveness` (supersede);
  - `drift-register`;
  - the two prompt templates;
  - `workflow.md:207`;
  - `README.md:200-204`;
  - `artifact-catalog.md:203-207`;
  - `entities.md:940-948`;
  - `content.py:268`;
  - the note's scope-change row.
- **The note's Review row:** C-e, with the pinned phrases kept.
- **Guide:** `section.modes.update.progress`, `workflow.update.s3`, `stage.21`.

**254: the remaining contradictions (C-f, C-j, C-k rest, C-l, C-m).** Text follows the engine.

**255: the rehearsal and the two eval cases (R17–R19).**
- **The harness**, `plans/evidence/scripts-255/`:
  - `reh.py` with `bundles`, `build`, `run`, `hold`, `record`, `refresh` and `ledger`;
  - `scenarios.py` and `seeds.py`;
  - reused 248 parts;
  - arms: `git archive v6.7.0` and HEAD, each building and reading under its own engine in a
    subprocess.
- **Batches**, with an operator checkpoint after each: B0 smoke (cap 12; the root's writability is
  checked here), B1 L02–L04/L06–L08/L15 (20), B2 L05/L09–L14 (12), B3 the 7 touched skills (25), B4
  the other 21 (22), reserve 59.
- **Stop when:**
  - the arm proof, the parse or the privacy scan fails;
  - the new arm fails a headline claim;
  - two VOIDs share a cause;
  - the client version changes;
  - spend exceeds 1.3× a batch's expected cost.
- **Record:**
  - `evals/sample-results/loop-rehearsal/<scenario>/<arm-n>/` and `skill-beats/<beat>/<arm>/`,
    each `package/data` + `obs.txt`;
  - existing `pkg_check` vocabulary only;
  - `evals.json` +2 cases; `evals/README.md` 9→11.
- **Optional, operator by hand:** `/loop /tamheed:loop-iteration package` on a new-bundle copy.

**257: acceptance, stamp, release, briefs.**
- `check.py` on 3.13 and 3.10; the selftest.
- `refresh_lab_680.py`.
- Six version surfaces; the three READMEs swept for content. `[Unreleased]` becomes
  `[6.8.0] - <date>`. `stock-history.json`; `index.html` rebuilt.
- CI on main green; tag `v6.8.0`.
- **Two briefs**, pinned by sha and sha256, rehearsed headless with the restart. They carry:
  - the replay counts;
  - the advance and move-back rules;
  - who records the finishing verdict;
  - the result keys;
  - the review-page change;
  - the note-rebuild warning;
  - the `handoff-current` effect;
  - the way back;
  - that a 6.7.0 reopen re-advances.

**Not done here:**
- a guard on work-item `Implemented`;
- an `entity_query` ordering option;
- edits to frozen DDL comments;
- OpenHands, Goose and Cline research.

## Verification

- **Each plan:** `check.py` on 3.13 and 3.10; red tests red at the parent commit, green after.
- **Engine:** F9 read-write-compare; the cascade both ways, journaled; the `no_verdict` cap;
  `v_backlog`; the ripple.
- **Loop:** `test_stop_words_agree`, `test_iteration_line_is_the_skills`, and the per-pass checks
  of table L.
- **Rehearsal:** both eval cases pass in `check.py`; n and arm beside every claim; the ledger at
  150 USD or less; the privacy scan clean.
- **Fields:** both replays open clean and move no file; both briefs rehearsed.
- **CI** green on main before the tag.

## 6. Approval checkpoint

Approving approves rulings R1–R25 as written, the order 249 → 250 → 256 (the R9 ruling) → 251 →
252 → 253 → 254 → 255 → 257, a commit only on your word for each plan, and rehearsal spend of
150 USD or less (brief rehearsals included). It also approves these **defaults**:

| # | Default |
|---|---|
| D1 | Equal `sort_order` values fall back to the phase or slice id number |
| D2 | A requirement with zero live criteria never advances (the old trigger could) |
| D3 | The picker's blocked test is `blocks-lifted`'s list (verified sound) |
| D4 | Cascade rows: `transition`, actor `system:requirement-advance`. `handoff-current` then names an earlier handoff |
| D5 | L05: a regression with no open work item ends the pass `backlog-empty` |
| D6 | Scratch root `C:\tamheed-reh`; the scratchpad if C:\ is not writable (operator confirmed) |
| D7 | A supersession that swaps the only Met criterion for a placeholder leaves the requirement `Implemented` |
| D8 | ADR-0005 records the move out of the trigger |
| D10 | A "Pending regrade" means the criterion had an earlier GRADED verdict (Met, Partial or Not-met). A Pending after only a Pending is a placeholder |
| D11 | Retiring a criterion does not run the cascade. The requirement moves at the next verdict that touches it (as today live) |
| D12 | `no_verdict` lists up to the existing id cap, plus `no_verdict_total` |

---

## Appendix A — Provenance: claims taken from a sub-agent [S], to re-verify on return

**Read by me:** the F9 replay; the load order (3 vs 23); the 4 shipped packages; the trigger
census; `verified_by` unread; the guard at `:2344`; `entity_query`/`v_backlog` order;
`blocks-lifted` and `rule()`; `_apply_note`; the fingerprints; the extractor; the roundtrip test;
the eval-spec keys; `record.py` audits; the CHANGELOG `[Unreleased]` precedent; the pins listed.

**[S], not yet re-verified:**
- **Code paths:**
  - the cross-engine open refusal (`tamheed_server.py:1577-1589`);
  - the guide key lines in `content.py` (the line numbers in plans 250–254);
  - `TOOL_EFFECTS` (`diagrams.py:1003-1006`);
  - `test_export_html.py:420/430`;
  - `standup_facts.py:120-124` (`requirements_done`);
  - `export_html.py:516-525` (design-ahead);
  - `_requirement_legs` (`:3264-3281`).
- **Docs:** every file:line in table C's "Where" column except C-a/C-b/C-e; the C4/C5
  provenance (plan 008:55, plan 007:91, ADR-0001:95).
- **Rehearsal estimates:** the per-beat costs (0.4–6 USD) and the 4 h wall time.
- **The research** quotes and URLs (Appendix B).

## Appendix B — Research citations (agent-gathered, 2026-11-17)

- **Ralph:** ghuntley.com/ralph; claytonfarr.github.io/ralph-playbook; humanlayer.dev/blog/brief-history-of-ralph.
- **snarktank/ralph:** `ralph.sh`, `CLAUDE.md`, `prompt.md`.
  - The pick is "highest priority … `passes: false`".
  - Done is the `<promise>COMPLETE</promise>` string.
  - `MAX_ITERATIONS=10`.
- **Anthropic ralph-loop plugin** (local:
  `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop`):
  - the stop hook feeds back the SAME prompt in one session;
  - the README:134 admits one string cannot tell SUCCESS from BLOCKED.
- **Claude Code docs** (`code.claude.com/docs/en/scheduled-tasks`, `/headless`):
  - `/loop` is session-scoped and expires after 7 days;
  - `--permission-mode dontAsk`.
- **ralphctl** (github.com/lukas-grigis/ralphctl):
  - topological pick;
  - `task-complete` only after `task-verified`;
  - a closed `blockCause` enum, with no reason-string parsing;
  - a dirty tree is called "silent corruption".
- **Codex `/goal`** (developers.openai.com cookbook): states active, paused, complete or
  budget-limited; no tool call means no continuation.
- **continuous-claude** (AnandChowdhary): a completion signal ×3; max runs, cost and duration
  caps; an error threshold.
- **Aider:** `max_reflections = 3`.
- **SWE-agent:** a closed set of `exit_*` statuses; the patch is captured on any exit.
- **ECC** (local): `loop-design-check` (a human flips done; an independent judge);
  `agents/loop-operator.md`.
- **Not covered:** OpenHands, Goose, Cline/Roo.

## Appendix C — Engine sketches (from the design pass; re-derive on return)

**`013_requirement_advance.sql`:**
- `DROP TRIGGER trg_requirement_auto_advance`.
- `DROP VIEW v_backlog`, then `CREATE VIEW v_backlog`:
  - the same columns;
  - `LEFT JOIN slices s ON s.id = w.slice_id`;
  - `LEFT JOIN phases p ON p.id = COALESCE(w.phase_id, s.phase_id)`;
  - the same `WHERE`;
  - `ORDER BY p.id IS NULL, p.sort_order, CAST(SUBSTR(p.id,4) AS INTEGER), s.id IS NULL, s.sort_order, CAST(SUBSTR(s.id,4) AS INTEGER), CAST(SUBSTR(w.id,5) AS INTEGER), w.id`.
- A header that corrects the frozen comments: C5 versus C4, and that `waivers.expires` NULL never
  expires.

**The cascade in `audit_record`,** after the inserts and before the commit:
- **Per requirement** of a touched criterion:
  - read the newest verdict, `verified_by` and history of each live criterion;
  - `_requirement_advances(pairs)` is `bool(pairs) and all(v == "Met" ...)`;
  - the move-back fires when the status is `Implemented` and some criterion's newest RECORDED
    verdict is `Not-met`, `Partial`, or a `Pending` with an earlier graded verdict (D10).
- **Each move** is an `UPDATE`, plus an INLINE `INSERT INTO progress_entries` (`transition`,
  `system:requirement-advance`, `subject_id` = the requirement).
- **The result:** `requirements_moved` [{id, from, to, audit}]; `no_verdict` (capped) and
  `no_verdict_total`, from `g_progress_failures` after the commit.

## Appendix D — Rehearsal mechanics (from the design pass)

- **Arms:**
  - `reh.py bundles` makes `git archive v6.7.0` (old) and HEAD (new) under
    `<root>/bundles/{old,new}`;
  - each `build`/`read` runs in a subprocess with that arm's `server`/`db` on `sys.path`;
  - the arm proof is that `debug.log` names `bundles/<arm>` only.
- **VOID** (re-run once, cost stays charged):
  - a timeout (kill the tree with `taskkill /T /F`);
  - a non-success subtype, or a turn or budget cap hit;
  - no JSON;
  - a denied test run;
  - a wrong arm proof;
  - a model id change;
  - a resume turn with the wrong session id;
  - a tamheed repo change during a run (stop the batch);
  - a live lock after a session (stop the batch).
  A wrong stop word or a wrong pick is a RESULT, not a VOID.
- **The ledger:**
  - per-session caps of 3 USD (10 for the tamheed planning turns);
  - a void with no reported cost is charged its cap;
  - pre-flight: refuse a session when the ledger plus its cap would cross a cap.
- **`obs.txt`:** facts outside the package. Absence is written as a value (`mixed_commits=0`).
  Old-arm statuses are read by the old engine at record time.
- **The privacy scan:** the forbidden strings come from an UNCOMMITTED local file (home path,
  account name, e-mail, org id, in slash, backslash and JSON-escaped forms). The recorder refuses
  on a hit.
