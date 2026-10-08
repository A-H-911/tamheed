# Implementation plans -- the Tamheed program index (through v5.x)

The authoritative index of every plan since the Track-B re-architecture began. One row
per plan; the plan files are close-out records (frozen once DONE except post-acceptance
addenda); `plans/evidence/` holds the verbatim field-report archives (C-series -- never
edited). The detailed cycle-by-cycle alignment records of the v2/v3 eras live in this
file's git history; the condensed chronicle below carries their substance.

**Lineage.** v1 (Keystone: markdown packages + a file-scanning validator) -> the v2
program (plans 005-016: the relational store, ADR-0001) -> field hardening against the
live ACMP deployment (017-026, evidence C11-C33) -> v3 (prompts-as-files + the
readiness engine, 027-030, C34-C37) -> **v4 (the entity-model re-baseline, ADR-0002;
031-, C38-)**. The Keystone repo stays archived at 1.0.x; v1 packages take the
two-step escape route (tamheed 3.2.1, then v3->v4 via `package_migrate`).

## The plans

### Foundation -- the v2 program (2026-07-11 -> 07-18)

| # | Title | Track | Priority | Size | Depends / evidence | Status |
|---|---|---|---|---|---|---|
| 005 | Bootstrap Tamheed repo (new repo, full history) | B1 | P1 | M | 001–004 committed | DONE |
| 006 | Deliverables review — **USER APPROVAL GATE** | B7 | P1 | M | 005 | DONE |
| 007 | Data model: ADR + DDL + canonical text | B2 | P1 | L | 006 — **unblocked**: `plans/deliverables-review.md` APPROVED 2026-07-17 | DONE |
| 008 | MCP server (official Python SDK) | B3 | P1 | L | 007 — SDK floor `>=3.10` verified 2026-07-17 (ASM-D: repo floor rises to 3.10) | DONE |
| 009 | Skill v2 rewrite + params + bootstrap removal | B4 | P1 | L | 008 | DONE |
| 010 | Migration v1 → v2 | B5 | P1 | L | 001–004, 009 | DONE |
| 011 | Adopt mode (brownfield onboarding) | B11 | P2 | L | 010 | DONE |
| 012 | HTML viewer (operator review surface) | B6 | P2 | M | 008 (010 preferred) | DONE |
| 013 | Eval runner + v2 CI + check.py | B10 | P2 | M | 010–012 | DONE |
| 014 | Docs + Mermaid diagrams + CHANGELOG 2.0.0 | B8 | P2 | M | 005–013 | DONE |
| 015 | Community extensibility + CONTRIBUTING | B9 | P3 | M | 007, 013, 014 | DONE |
| 016 | Keystone close-out: successor banner + freeze | B12 | P3 | S | 014 | DONE |

### Field hardening -- the ACMP cycles (2026-07-21 -> 08-08)

| # | Title | Track | Priority | Size | Depends / evidence | Status |
|---|---|---|---|---|---|---|
| 017 | Field-report hardening: core gates, shared pipeline, v1 dialect tolerance | B13 | P1 | L | 005–016 DONE, v2.0.0 tagged; evidence C11–C16 (ACMP run 2026-07-21) | DONE — v2.1.0; ACMP acceptance re-run SUCCEEDED 2026-07-21/22 (see plan 018 evidence) |
| 018 | Second field report: preview honesty, viewer scale, prompt library, cutover tooling | B14 | P1 | L | 017 DONE + the successful ACMP migration; evidence C17–C19 | DONE — v2.2.0; ACMP re-migration SUCCEEDED (zero repair loops — plan 019 evidence) |
| 019 | Third field report: managed emissions, ledger ergonomics, viewer consistency | B15 | P1 | L | 018 DONE + the v2.2.0 ACMP re-migration; evidence C20–C22 | DONE — v2.3.0; process-acceptance clean, but findings_4 §D retracted the data verdict → plan 020 |
| 020 | Fourth field report: DATA FIDELITY + viewer redesign + ACMP repair path | B16 | P1 | XL | 019 DONE + the retracted-verdict report; evidence C23–C25 | DONE — v2.4.0; §7 ACMP repair SUCCEEDED (zero blind repairs, v_phase_exit revived — plan 021 evidence) |
| 021 | Fifth field report: title resolution, escaped pipes, emit-scan closure | B17 | P2 | M | 020 DONE + the §7 repair run; evidence C26 | DONE — executed 2026-07-23, v2.5.0; acceptance = the findings_6 scratch-diff (empty UNEXPECTED bucket) |
| 022 | Sixth field report: DW prose carry, phase-regex fix, derived-artifact papercuts | B18 | P2 | S | 021 DONE + the scratch-diff regression run; evidence C27 | DONE — executed 2026-07-23, v2.5.1; acceptance = findings_7's §8 run (all four gaps closed) |
| 023 | Seventh field report: ledger honesty + upsert ergonomics | B19 | P3 | S | 022 DONE + the first official §8 run; evidence C28 | DONE — executed 2026-07-23, v2.5.2; acceptance = findings_8's blob-inclusive §8 run (empty UNEXPECTED) |
| 024 | Eighth field report: ship the §8 scratch-diff tool | B20 | P3 | S | 023 DONE + the blob-inclusive §8 run; evidence C29 | DONE — executed 2026-07-23, v2.6.0; acceptance SUCCEEDED (findings_9/C30: tool-vs-script 185=185, empty UNEXPECTED, scratchpad retired) |
| 025 | Tenth field report: EXECUTION hardening (allocator ceiling, truthful surfaces, stale guard) | B21 | P1 | M | findings_10 (first execution-shaped report); evidence C31 | DONE — executed 2026-08-08, v2.7.0; acceptance SUCCEEDED (findings_11/C32: all four §A defects verified FIXED by running the tools, C1/D exercised, zero asks) |
| 026 | Twelfth field report (INCIDENT): pin the MCP SDK, truthful startup diagnostics | B22 | P0 | S | findings_12 (SDK 2.0.0 broke every fresh resolve); evidence C33 | DONE — executed 2026-08-08, v2.7.1; acceptance = ACMP reconnects on a fresh resolve |

### v3 -- prompts-as-files + the readiness engine (2026-08-13 -> 08-14)

| # | Title | Track | Priority | Size | Depends / evidence | Status |
|---|---|---|---|---|---|---|
| 027 | Maintainer observations: prompts→files, readiness engine, typed relations, flow viewer, drift enforcement | B23 | P1 | XL | seven direct maintainer notes 2026-08-13 (no findings file); 3 exploration passes + devil's-advocate round + 2 interviews | DONE — executed 2026-08-13, **v3.0.0** (migrations 003+004); acceptance MET same day (findings_13/C34: conversion clean, readiness caught SL-004) |
| 028 | Thirteenth field report: prompt lifecycle signals, readiness discrimination, flow legibility, operator guide | B24 | P2 | M | findings_13 (the v3.0.0 acceptance) + the maintainer's prm-naming/overlap probe + user-guide ask; evidence C34 | DONE — executed 2026-08-13, v3.1.0; acceptance ran same-day (findings_14/C35: §2/§4/§5 all verified; two note/force defects → plan 029) |
| 029 | Fourteenth field report: tool-owned note span, honest force, indeterminate readiness | B25 | P2 | S | findings_14 (the v3.1.0 acceptance); evidence C35; all forks interview-locked | DONE — executed 2026-08-14, v3.2.0; acceptance ran same-day (findings_15/C36: all three fixes verified; curation done; instruction transfer PROVEN) |
| 030 | Fifteenth field report: README folder index + lock guidance; the README release contract (lint-enforced) | B26 | P3 | S | findings_15 (the v3.2.0 acceptance) + the maintainer's update-READMEs-each-release instruction; evidence C36 | DONE — executed 2026-08-14, v3.2.1; **acceptance MET (findings_16/C37: per-file path field-proven, both additions render; zero defects — no plan, no release)**; carried: the interactive fresh-session drift test (operator-side) + the either-discriminator lock rewording (next release) |

### v4 -- the entity-model re-baseline (2026-08-14 ->)

| # | Title | Track | Priority | Size | Depends / evidence | Status |
|---|---|---|---|---|---|---|
| 031 | The v4 entity-model redesign: full entity study + external research, re-baselined store, claimed-vs-verified Review, waivers, drift deltas, typed journal, blocking G-REL, v1 retirement, the lab | B27 | P1 | XL | maintainer v4 directive (study every entity, deep research, relations/validations, migration, lab testing, Mermaid docs); 15 decisions locked over five interview rounds + a devil's-advocate round | DONE — executed 2026-08-14, v4.0.0; docs/entities.md is the rationale record; the lab package is the lab-tracker eval case |
| 032 | The prompt-surface completion: stock-history classification + refresh_stock (findings_14 root fix), register-liveness playbook, expired-waiver sweeps, the templates' v4 sweep (a 4.0.0 miss), the teaching-surface lint | B28 | P2 | M | maintainer's prompt-impact question → verified assessment → three interview forks + DA round (content-not-hashes catch) | DONE — executed 2026-08-14, v4.1.0; lint 9 caught a live teaching defect on first run |
| 033 | findings_17 + the documentation reckoning: the OQ-rule discrimination fix, migration stash parity + letter scale, the entity-guide merge, schemas/ deletion completed, examples/ retired, four new/extended lints (dead-path, closed-triangle teaching, 5-file stamps, template-sync), the Mermaid delivery (7 entity + 3 workflow diagrams), ADR-0002, this index rewrite | B29 | P1 | L | findings_17 (C38) + the maintainer-ordered full documentation audit (three agents, 100+ files) → two interview rounds + DA round | DONE — executed 2026-08-15, v4.2.0 |
| 034 | findings_18: the risk-liveness hollow-pass guard (indeterminate when the scale is unpopulated — the only rule in the class, sweep-verified), customization-lag visibility (stock_last_changed + the honest-conditional warning), the repair doctrine's second and third halves (paste-don't-retype, independent post-repair verifier) | B30 | P2 | S | findings_18 (C39) → three interview forks + DA round (candidate-row scoping, consumer-list, risk_state NOT NULL catches) | DONE — executed 2026-08-15, v4.2.1 |
| 035 | The lessons-learned entity family: migration 002 (the v4 chain's first — LLIS-shaped `lessons` table, learned_from relation, column-selective immutability), the always-loaded note section (Approved-only, pinned-first, G-INJECT-screened), the lessons-confirmed advisory, staged registry-sync for existing v4 stores, the viewer Lessons section, the lab continuation beat | B31 | P1 | L | maintainer feature ask (no field report — 4.2.1 closed clean) → internet research (PMI/LLIS/Reflexion/AAR) + 2 explorers + 8 interview forks over 2 rounds + advisor + DA round | DONE — executed 2026-08-15, v4.3.0 |
| 036 | findings_19 + the confirm guard + lesson→skill promotion: the mechanical never-auto-confirm gate (operator_confirm, every landing path incl. birth — the DA bypass catch; closes §2's one-write-too-late gap), migration 003 (SKL- family, Promoted state, promoted_to), the skill-promote interview ceremony (level project\|user default project, full graduation), the pointer-pattern classifier fix (§1's destructive-advice hollow pass), FK message parity (§3) | B32 | P1 | L | findings_19 (C40) + the maintainer's capability ask → ECC/Voyager/Soar research + 2 interview rounds + a clarification + advisor + DA round | DONE — executed 2026-08-15, v4.4.0 |
| 038 | findings_21: the append-only gate trap — G-COMPLETE exempts the journal report columns (the C14 reasoning extended; the untested evidence twin test-pinned) + skips Superseded/Obsolete rows (the DA trap-class completion: supersession must actually repair), every failure names its `matched` token, and `corrects` gains its first consumer (the review.html corrected-entries fold) | B34 | P2 | S | findings_21 (C42, the program's reproduction-quality bar) → two interview forks + DA round | DONE — executed 2026-08-20, v4.4.2 |
| 037 | findings_20: the honest registry-sync report — `columns_added` computed per-run (stored-keys-vs-DDL, sound by CANONICAL rule 4) + the reworded note (incl. the audit-journal row the old note was silent about) + the six-surface "pure append" sweep | B33 | P3 | XS | findings_20 (C41) → one interview fork + DA round | DONE — executed 2026-08-16, v4.4.1 |
| 039 | findings_22 + the ACMP lessons: `entity_query` depth (`after_id` keyset, `ids`, `search` — the tool no longer pushes agents onto the files), the `amends` relation (migration 004) with Merged-last merge semantics, `package_verify` + the server-only `integrity-verified` event (and all four server-witnessed kinds refused from callers — the field data held five hand-written ones), `narrated_ids`, the `.converted` leftover relocated per file on BOTH migrate paths (the DA round's identical-copy catch; the advisor's v3-confirm catch), the `lessons-note-budget` advisory (57 note lines in the field), four doctrine lines from LL-061/042/040/004, the full documentation sweep, lab beat 12 | B35 | P1 | L | findings_22 (C43) + the 62-row ACMP lessons register → three interview rounds (10 forks) + advisor + DA round | DONE — executed 2026-09-06, v4.5.0 |
| 040 | findings_23: the edge retire (`retire: true` on the trace-edge item — the composite PK left `amends` sitting beside the `relates_to` it was meant to replace, and the G-REL note, the adopt note AND the maintainer's own 4.5.0 note named a "delete + re-add" the server could not perform; hard delete, journaled `correction` row, no operator gate — both DA forks on the maintainer's words), the honest audit split (each active AC's LATEST verdict in three buckets — the old all-rows count reported placeholders the package had replaced; the DA round corrected the plan's own "ungraded: 12" to the measured 142/0/0), the relocate wording (what was verified vs not; premise corrected — tamheed generates no gitignore), the remedy-must-exist doctrine, lab beat 13 | B36 | P2 | M | findings_23 (C44) → four interview forks + advisor + DA round (two more forks) | DONE — executed 2026-09-06, v4.6.0 |
| 041 | findings_24: the sanctioned read for committed scripts — `entity_export` (a read-only tool's WHOLE result to a digest-stamped, deterministic JSON file under `exports/`; the field's slate generators had no route under an MCP-exclusive read rule; the CLI and the lock-free open were offered, the tool chosen so the rule stays literally true), the `expect_unchanged` paste guard (the field's LL-063: a paragraph lost mid-paste with ok:true; opt-in self-verifying full-row writes for the trigger-less registers), the DA round's determinism/overwrite/partial/digest-of-memory catches, lab beat 14 | B37 | P2 | M | findings_24 (C45) → three interview forks + advisor + DA round | DONE — executed 2026-09-06, v4.7.0 |

Index note: plan 006's file points at `plans/deliverables-review.md` for the approved
artifact set -- that review is the v2 input contract and remains frozen alongside it.

### Advisor audit 2026-09-10 -- plans 042-053 (improve skill, deep; advisor, not maintainer)

Written against commit `7e3a92b` (v4.7.0) by the `/improve deep` audit: 8 read-only category
sweeps, every finding re-read or reproduced before it was planned. The plans follow the
improve template (self-contained; an executor with zero context runs them top to bottom)
rather than the findings-file/interview shape of 005-041. Recommended order = table order;
dependencies are hard where marked. Status values: TODO | IN PROGRESS | DONE | BLOCKED
(reason) | REJECTED (rationale). Executors update their row.

**Integration branch (2026-09-11):** all ten APPROVED branches below plus plan 042's line were
merged by an integration-only executor onto `worktree-agent-a9e0797e07858539d` (HEAD
`976ee6a`, descends from `7e3a92b`; `python check.py` → ALL CHECKS PASSED on the combined
state; the only edits beyond the union of the branch diffs are the CHANGELOG `[Unreleased]`
consolidation into one `### Fixed` + one `### Changed` and a `data/` prefix on plan 044's
stem-check message). Operator: `git merge --ff-only worktree-agent-a9e0797e07858539d`
on `main`, commit `plans/`, push; then `git worktree prune` after deleting the eleven
`.claude/worktrees/agent-*` directories and their branches.

| Plan | Title | Priority | Effort | Depends on | Status |
|---|---|---|---|---|---|
| 042 | [CI has never run](042-ci-has-never-run.md) -- 0 workflow runs on a public repo with two active workflows; add `workflow_dispatch`, investigate, get one green run | P1 | S | -- | DONE — 2026-09-11: first run ever, https://github.com/A-H-911/tamheed/actions/runs/34606957426, 7/7 jobs green (6 `check` legs + smoke). **Finding:** push events never trigger on this repo (the push of `c9ef603` registered `pushed_at` but fired nothing; `workflow_dispatch` ran immediately) — Actions is enabled, the repo is not a fork, no rulesets or protection, the push actor is the maintainer — every readable setting is normal, so the cause is unknown and GitHub-side (the v4.8.0 CHANGELOG's "account-side setting" wording overstated this; corrected here 2026-09-12, releases stay frozen). **Resolved 2026-09-12 (post-release review):** disable/enable both workflows → nothing; a throwaway branch with an unfiltered `on: push` probe fired in 6 s (run 34700651003) and a branch-filtered probe in 7 s (34700888409), so delivery works and only the two workflow objects registered at the first push were stale; renaming `ci.yml`→`ci.yaml` and `eval.yml`→`eval.yaml` (commit `7e07329`, names unchanged) re-registered them and the **first push-triggered CI run ever** followed 5 s later: https://github.com/A-H-911/tamheed/actions/runs/34701821873, 9/9 green. First eval-lint run (dispatch): 34700588616, `OK: 9 eval cases well-formed (71 live assertions)`. The probe workflow objects linger in the Actions list without a ref (GitHub-side GC); no Support ticket needed. `pull_request` delivery checked the same day on the maintainer's words: throwaway PR #1 fired CI in 7 s (run 34704852136, green), closed unmerged, branch deleted. The weekly schedule's first slot, Monday 2026-09-14 06:17 UTC, **fired on its own** (event `schedule`, run 34845915972, green; GitHub started it at 12:53 UTC, a platform delay) — every trigger kind is now verified on the re-registered workflows |
| 043 | [Stale-tree refusal must roll back](043-stale-tree-refusal-must-roll-back.md) -- `RELEASE batch` before `_commit()` committed the batch in memory; refused writes answered every later read (reproduced; one-line deletion, suite green on a scratch copy) | P1 | S | -- | DONE — APPROVED 2026-09-11, commit `8eef6e2` on branch `worktree-agent-a8e1a43b9c5cb62c6` (unmerged; operator merges) |
| 044 | [Package-name + output-path hygiene](044-package-name-and-output-path-hygiene.md) -- `_NAME_RE` applied only on create; open/verify/migrate resolve `PACKAGE_ROOT / name` raw (SECURITY.md claims otherwise); `export_html(output)` unguarded | P1 | S | -- | DONE — APPROVED 2026-09-11, commit `920c326` on branch `worktree-agent-aa9df8e9aa6b74a92` (unmerged; operator merges; `package_verify` validates the name before the already-open check — deliberate) |
| 045 | [`package_migrate` fail-atomic](045-package-migrate-fail-atomic.md) -- characterization tests first; parse before write, write-beside-then-swap (the v4 registry-sync path deleted before it copied, with no backup), restore-from-backup on any failure, corrupt `packages.jsonl` is an error not a traceback | P1 | M | (044 first if both) | DONE — APPROVED 2026-09-11 after one revision round (the plan's own swap sketch deleted the only copy on the v4 path; fixed + tested), commits `3037e57`/`e333b61`/`dd5a3e3` on branch `worktree-agent-a5276e0675981a0d6` (unmerged; operator merges) |
| 046 | [`_scan_markers` skips Superseded/Obsolete](046-scan-markers-skips-superseded-rows.md) -- parity with the placeholder scan (plan 038); a stale marker on an immutable superseded row was a permanent G-COMPLETE fail with an impossible remedy | P1 | S | -- | DONE — APPROVED 2026-09-11, commit `33e38ea` on branch `worktree-agent-a259d4a161f30b496` (unmerged; operator merges; the readiness advisory is named `clarifications-open`, not `open-markers`) |
| 047 | [`--selftest` registers with FastMCP](047-selftest-registers-with-fastmcp.md) -- the one step no check exercised (C33's class); 18/18 today, made a tripwire | P2 | S | -- | DONE — APPROVED 2026-09-11, commit `24ed879` on branch `worktree-agent-a56417be4cb278726` (unmerged; operator merges) |
| 048 | [Docs drift sweep](048-docs-drift-sweep.md) -- `--dry-run` removed from every surface (maintainer decision: docs, not code), v4 migrate example, `examples/`/`entity-guide.md`/`handoff/`/`sources=` ghosts, 15->16 prompts, SECURITY.md path + git-log wording, Keystone runbook says which steps run under 3.2.1 | P2 | S | (044 first) | DONE — APPROVED 2026-09-11, commit `207e085` on branch `worktree-agent-abc93ed074b21bb02` (unmerged; operator merges; cosmetic leftovers: `docs/methodology.md:273` "(v4.6) (safeguard 16)", and the "everything previewable" heading at :125) |
| 049 | [Scoped readiness indeterminate at zero](049-scoped-readiness-indeterminate-at-zero.md) -- `acs-met`/`wbs-done`/`slices-closed` passed silently for an empty phase/slice; C35/N3 doctrine applied (never blocks) | P2 | S | -- | DONE — APPROVED 2026-09-11, commit `06e4d83` on branch `worktree-agent-abe3772ef3f3535d6` (unmerged; operator merges) |
| 050 | [CSV formula-injection guard](050-csv-formula-injection-guard.md) -- CWE-1236 on the exported `csv/`; lab-tracker `csv/` goldens regenerated by tool | P2 | S | (044 first) | DONE — APPROVED 2026-09-11, commit `0987e73` on branch `worktree-agent-aecfa031d782d8870` (unmerged; operator merges; regeneration was a no-op — no fixture cell actually starts with a trigger character) |
| 051 | [Omission reason not silently dropped](051-omission-reason-is-not-silently-dropped.md) -- `INSERT OR IGNORE` reported a revised reason as `unchanged`; `scratch_diff` keyed omissions on the wrong tuple | P2 | S | 043 | DONE — APPROVED 2026-09-11, commit `d1ec480` on branch `worktree-agent-a24c2b4e5fced8269` (unmerged; operator merges) |
| 052 | [CI: real `uv` step, py3.13 leg, bounded `pip install`](052-ci-matrix-uv-step-and-bounded-pip-install.md) -- the documented fallback reproduced the C33 incident the pin prevents | P2 | S | 042, 047, (048 first) | DONE — APPROVED 2026-09-11 after one STOP (upstream publishes no floating `vN` tag past `v7`; pinned `astral-sh/setup-uv@v10.1.0` instead), commit `e2a8374`; CI https://github.com/A-H-911/tamheed/actions/runs/34609940476 — 9/9 green (8 `check` legs incl. py3.13 × 2 OS, smoke `18/18 tools registered`) |
| 053 | [Refuse phase/slice born Implemented](053-refuse-phase-or-slice-born-implemented.md) -- the guard measured an id with nothing bound and passed; `force` stays the route (maintainer decision 2026-09-10; tool-contract change) | P3 | S | 049, 043 | DONE — APPROVED 2026-09-11, commit `e3b44bc` on branch `worktree-agent-ae8c6bf7a6f44cd77` (unmerged; operator merges) |
| 054 | [Note: skills screened + marker literals defused](054-note-skills-screen-and-marker-defuse.md) -- `skills.name`/`level` rendered into the CLAUDE.md note without the `_INJECT_RE` screen; an HTML-comment literal inside rendered text could truncate the tool-owned span | P2 | S | -- | DONE — APPROVED 2026-09-12, commit `5a90707` on branch `worktree-agent-ae0def22b2ddc31ce` (merged via integration branch `df99524`, 2026-09-12) |
| 055 | [record/adopt debt](055-record-and-adopt-debt.md) -- silent `ImportError` fallback, dead v1 ledgers (`count_deltas` could never fire), adopt's hand-copied Always roster derived from the registry, 2 MB file cap with `scan.skipped_large`, post-flight `error` key (the "follows symlinks" claim was false -- `rglob` does not descend symlinked dirs) | P3 | S | -- | DONE — APPROVED 2026-09-12, commit `606715a` on branch `worktree-agent-a01926acc416d38bb` (merged via integration branch `df99524`, 2026-09-12) |
| 056 | [Test gaps](056-readiness-eval-and-lint-test-gaps.md) -- whole-rule waiver, `decisions-approved`, `decisions-look-architectural`; `pkg_check` lock leak + loud missing table + `grep-tree-*`; `injection-brief` assertion off the retired `prompts` table; `check.py` lints under their own suite | P2 | M | -- | DONE — APPROVED 2026-09-12, commits `d16488d`/`a3b7c88` on branch `worktree-agent-abfd9ac964dfa26db` (unmerged; integration pending; nine suites now) |
| 057 | [Numeric id ordering in the viewer](057-numeric-id-ordering-in-the-viewer.md) -- eleven string `ORDER BY id` sites in `export_html.py`; lexical version sort in `_emit_prompt_library` (`4.10.0` < `4.9.0`) | P3 | S | (054 first) | DONE — APPROVED 2026-09-12 after one revision (the Graph section's three Python-side id sorts — the executor found them), commits `5a6e935`/`e34d4dd` on branch `worktree-agent-aa04fac9fd4e29d5d` (merged via integration branch `df99524`, 2026-09-12) |

| 058 | [Release v4.8.0](058-release-v4-8-0.md) -- bump, dated CHANGELOG heading with the narrative lead-in, the five stamps, the README prompt body under `stock-history.json["README.md"]["4.8.0"]`; MINOR (053 is a contract change) | P1 | S | 042–057, 059 | DONE — 2026-09-12, release commit `96e4ed9`, tag `v4.8.0`, CI https://github.com/A-H-911/tamheed/actions/runs/34695497486 9/9 green |
| 059 | [Lab beat 15](059-lab-beat-15-advisor-audit.md) -- the advisor-audit continuation against the recorded lab package, agent-driven in-process through the working-tree server (the beat-14 procedure); nine new `evals.json` assertions; evidence report under `plans/evidence/` | P1 | M | 042–057 | DONE — 2026-09-12, commit `9759bce` (lab-tracker 26→35 assertions, ready, verified, 27 files; `plans/evidence/lab-continuation-report-059-2026-09-12.md`). Beat finding, recorded not fixed: a whole-rule waiver shadows a narrower per-entity waiver in the `waived` citation (`rule()` cites `whole_rule[0]` for every entity) — verdict unaffected, audit trail less specific |
| 060 | [Waiver citation prefers the specific waiver](060-waiver-citation-prefers-specific.md) -- `rule()` cites a per-entity `WVR-` before a whole-rule one (beat 15's observation); verdict unchanged, audit trail specific | P3 | XS | 056, 059 | DONE — 2026-09-12, commit `1d38a5f`, executed directly by the reviewer (maintainer-delegated); test RED→GREEN, `check.py` green, lab golden byte-identical on re-export |
| 061 | [Docs sweep for 042–060](061-docs-sweep-post-batch-042-060.md) -- the maintainer asked whether every doc surface followed the batch; a per-behavior grep found seven silent surfaces (CSV guard, note skills screen, scoped indeterminate, the ninth suite ×3, CI matrix, viewer order, waiver citation); no diagram affected | P2 | S | 042–060 | DONE — 2026-09-12, executed directly by the reviewer; seven files, lint green |
| 062 | [Release v4.8.1](062-release-v4-8-1.md) -- PATCH: the specific waiver (060), CI on push again (the rename), the docs sweep (061); plan-058 recipe | P1 | S | 060, 061 | DONE — 2026-09-12, tag `v4.8.1` (SHA in the tag), `check.py` green, CI green on push |

(Rows 054–057 added 2026-09-12: the maintainer asked for every audited finding to be planned
and executed before any release is cut. Rows 058–059 added the same day after the batch-2
acceptance: release on the maintainer's words, lab beat first so its fixture and assertions
land in the release commit as beats 10–14 did.)

**Batch 2 acceptance (2026-09-12):** integration branch `df99524` → `main` `c52ca04`; nine suites + `check.py` green (also under `PYTHONWARNINGS=error::DeprecationWarning`); a 37-check black-box acceptance run through the real tool handlers (one section per plan, each check shown to fail on the pre-fix code) 37/37; `uv run … --selftest` 18/18; CI https://github.com/A-H-911/tamheed/actions/runs/34669537392 9/9 green. All sixteen advisor plans (042–057) DONE; nothing released yet.

### Field cycle findings_25 -- plans 063-074 -> v4.9.0 (2026-09-21; reviewer-executed)

Master record: [063-074-batch-findings-25.md](063-074-batch-findings-25.md) (the approved plan; execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 063 | [The lock can be observed; the migrate preview runs without it](063-lock-observation-and-lock-free-preview.md) | findings_25 §1 | DONE — 2026-09-21, commit `79e8c5b`; reviewed by a security and a Python reviewer before commit; CI 9/9 on Ubuntu + Windows (run 35554874507) |
| 064 | [`package_unlock` — the sanctioned, journaled route out of a dead holder's lock](064-package-unlock.md) | 063 | DONE — 2026-09-21, commit `d54b989`; security + Python reviewers before commit (a racing-unlock CRITICAL closed by a byte-compare before removal); `--selftest` 19/19; CI 9/9 (run 35556634557) |
| 066 | [`server_info` package block + `detail=true` (entity types, relation rules)](066-server-info-package-row-and-detail.md) | findings_25 §3 | DONE — 2026-09-21, commit `6e319ed` |
| 067 | [Export envelope carries `partial`; `package_verify(expect=)`](067-export-self-describing-and-verify-expect.md) | ACMP export consumers | DONE — 2026-09-21, commit `3f53c0b` |
| 068 | [`entity_query` announces projections and search hits; lesson approval nudge](068-reads-announce-what-they-hid.md) | LL-077, LL-094, DEF-107 | DONE — 2026-09-21, commit `cf71a56` |
| 069 | [`population` on every readiness rule; `lessons-confirmed` indeterminate at zero](069-readiness-rules-report-their-population.md) | hollow-pass lessons | DONE — 2026-09-21, commit `f90d06b` |
| 070 | [`prose-ids-resolve` advisory (measured false-positive gate)](070-prose-ids-resolve-advisory.md) | 069; phantom DEF-082 | DONE — 2026-09-21, commit `0a27713`; measured first: both field phantoms found, ~1 false hit per 1,000 rows |
| 071 | [Stock prompts adopt the portable field rules (needle-pinned)](071-stock-prompts-adopt-field-rules.md) | 064, 066, 067 | DONE — 2026-09-21, commit `2e2d9e5`; two stale teachings removed from the prompt guide |
| 065 | [`csv/` equals what `export_html` emits; `package_verify.foreign_csv`](065-csv-dir-equals-what-was-emitted.md) | findings_25 §2 | DONE — 2026-09-21, commit `a5d08d8`; security + Python reviewers before commit; lab fixture byte-identical on re-export |
| 072 | [Docs + diagrams sweep after code lands](072-docs-and-diagrams-sweep.md) | 063–071 | DONE — 2026-09-21, commit `b18fcee`; one wrong sequence diagram corrected, a lock-lifecycle state diagram added |
| 073 | [Lab beat 16](073-lab-beat-16-findings-25.md) | 063–072 + acceptance | DONE — 2026-09-21, commit `234bd13` (agent-driven in-process, reviewed by rerunning its done criteria): lab-tracker 35→44 assertions, ready, verified; `plans/evidence/lab-continuation-report-073-2026-09-21.md`. Acceptance pass before it: a 20-check black-box script, 20/20 on the batch tree and 0/20 on the pre-batch tree, each failure for its own reason. Beat observation, recorded not fixed: a whole-rule waiver absorbed a defect written after it was approved |
| 074 | [Release v4.9.0](074-release-v4-9-0.md) | 073 | DONE — 2026-09-21, tag `v4.9.0`; `check.py` green; CI green on push |

### Field cycle findings_26 -- plans 075-084 -> v4.10.0 (2026-09-21; reviewer-executed)

Master record: [075-084-batch-findings-26.md](075-084-batch-findings-26.md) (the approved plan;
execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 075 | [Supersession completes itself; retiring a binding lesson needs the operator](075-lesson-supersession-completes-itself.md) | findings_26 §3 | DONE — 2026-09-21, commit `4c26224`; security + Python reviewers before commit (both found the same CRITICAL: `Proposed` unbound a lesson unattended; the security reviewer a second: an unguarded pointer); CI 9/9 (run 35615991440) |
| 077 | [No rule passes over nothing; a recorded omission reads `pass`](077-no-rule-passes-over-nothing.md) | maintainer ruling; plan 069 | DONE — 2026-09-21, commit `cedb443`; measured first (17 of 21 rules on a fresh package); none of the 18 existing `pass` assertions flipped |
| 076 | [Prose-id refinements: `in_code_spans`, `not_well_formed`, the list is a floor](076-prose-id-rule-says-what-it-skipped.md) | findings_26 §1–§2; 077 | DONE — 2026-09-21, commit `ea2a2cf`; measured on ACMP's exports: nothing fails, `DEC-208` visible under `in_code_spans`, the `ADR-2026` false positive gone |
| 079 | [`waivers-open-ended` advisory](079-waivers-open-ended-advisory.md) | beat 16's observation; 077 | DONE — 2026-09-21, commit `f82310a`; emitted only when the package has waivers (a recorded deviation); the lab's `WVR-002` is named |
| 080 | [Upsert results carry `changed_columns` with before/after lengths](080-a-write-says-what-it-changed.md) | the field's silent-loss lessons | DONE — 2026-09-21, commit `31637a8`; reviewed before commit, no critical or high finding; `if_match` dropped as speculative |
| 081 | [A digest stamp makes a stale review page detectable](081-a-stale-review-page-is-detectable.md) | the field's "git clean ≠ artifacts current" | DONE — 2026-09-21, commit `6d877cf` |
| 078 | [A completed hand-merge of a customised prompt is visible (declared marker)](078-a-completed-hand-merge-is-visible.md) | findings_26 | DONE `8cf9491` |
| 082 | [Docs + diagrams sweep after code lands](082-docs-and-diagrams-sweep-findings-26.md) | 075–081 | DONE |
| 083 | [Lab beat 17](083-lab-beat-17-findings-26.md) | 075–082 + acceptance (20/20 vs 0/20 on `v4.9.0`) | DONE `4a0bbb9` — 12 new assertions, each failing on the pre-beat fixture; finding F-1 |
| 084 | [Release v4.10.0](084-release-v4100.md) — plan-058 recipe + the fixture follows the stamp (F-1) | 083 | DONE — 2026-09-21, tag `v4.10.0` (SHA in the tag) |

### Field cycle findings_27 -- plans 085-090 -> v4.11.0 (2026-09-22; reviewer-executed)

Master record: [085-090-batch-findings-27.md](085-090-batch-findings-27.md) (the approved plan after a
devil's-advocate review; execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 085 | [findings_27 §1-§3: `_` is a word character; the classification order and `scoped` are stated; every list says when it is cut](085-prose-id-underscore-and-honest-lists.md) | findings_27 | DONE — 2026-09-22 |
| 086 | [findings_27 §4: the by-hand lesson retirement is journaled by the engine (`system:lesson-guard`)](086-by-hand-lesson-retirement-is-journaled.md) | findings_27; operator ruling | DONE — 2026-09-22; security review closed the `system:` actor forgery on the maintainer's ruling |
| 087 | [The `feedback` family (`FB-`, migration 005): upstream feedback and local tools on the operator's word; `handoff_emit` names what awaits](087-feedback-family-on-the-operators-word.md) | maintainer rulings 2026-09-22 | DONE — 2026-09-22; two reviewers, one CRITICAL and one MEDIUM-HIGH closed before commit |
| 088 | [Docs + diagrams sweep after code lands](088-docs-and-diagrams-sweep-findings-27.md) | 085-087 | DONE — 2026-09-22 |
| 089 | [Lab beat 18](089-lab-beat-18-findings-27.md) | 085-088 + full test (15/15 vs 0/15 on `v4.10.0`; 9 suites; selftest) | DONE `762b98b` — 9 new assertions, each failing on the pre-beat fixture; D-1 registry-sync unscripted, F-3 fixed |
| 090 | [Release v4.11.0](090-release-v4110.md) — plan-058 recipe + the fixture follows the stamp | 089 | DONE — 2026-09-22, tag `v4.11.0` (SHA in the tag) |

### Wired at birth -- plans 212-213 -> v6.2.0 (opened 2026-10-08; maintainer-executed)

The operator ran the planning half in a new repository with no `CLAUDE.md`; nothing pointed the
repository at its package before stage 20, so no session could resume through the hook. The engine now
writes the pointer pattern at the package's birth and at `package_open` on an unwired root (R67, R68).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 212 | [Wired at birth](212-wired-at-birth.md) -- `_wire_project` at create, adopt and open (served processes only, `_WIRE_ROOT`): the root `CLAUDE.md` stub or the three-line pointer section, the planning-era note in the package's own `CLAUDE.md`, the emit replacing it in silence, the note-only report, the resume block's `half`; nine contract tests and one hook test; the docs and the guide; lab beat 35 by a real agent | 211 | DONE -- 2026-10-08 (the commit this row lands in, after the operator's review) |
| 213 | Release 6.2.0 -- the stamp on every surface, the stock guide's history key, the lab fixture refreshed through the engine, push and tag on the operator's word | 212 | PLANNED |

### Field fixes after v6.1.0 (2026-10-08 ->; maintainer-executed)

Docs-only beats between releases, one ledger each, no version bump. Status values: DONE (the commit).

| # | Plan | Depends on | Status |
|---|---|---|---|
| 211 | [The per-project install refusal](211-install-scope-docs.md) -- `/plugin install` at project scope refuses "already installed globally" once a user-scope record exists; the route is `claude plugin enable --scope project` (measured: writes the project file, adds no record; the shell install also succeeds and adds a record); README, install page and the guide lead with it; the maintainer's stale 5.1.0 local record removed and the user copy lifted 5.8.1 -> 6.1.0 | 210 | DONE -- 2026-10-08 (the commit this row lands in, after the operator's review) |

### The user guide round 2 -- plans 201-210 -> v6.1.0 (released 2026-10-04 UTC; maintainer-executed)

Master record: [201-210-batch-guide-round-2.md](201-210-batch-guide-round-2.md) (the operator's
rulings G1-G13 and G16 of 2026-10-04, G17 from the plan 201 review). The generated user guide draws
the engine as it is after 6.0.0: one agent with two halves on D1 and D2, the chrome, the figures
folder, per-family, per-tool, per-gate and per-skill figures, the logo. Status values: PLANNED / IN
PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 201 | [D1 and D2 as one agent with two halves](201-d1-d2-two-halves.md) -- the frame primitive (G17) with its lint rule; the operator on top, the two lanes, the handoff, the server and the package; the README overview image re-exported | 200 | DONE -- 2026-10-04 (`ba9ac5f`) |
| 202 | [The chrome](202-chrome-nav-d3-d5-pager.md) -- numbered sections with chapter kickers, the two-level TOC that fits 1280 x 900 closed, D3's loop returns in channels, D5's row headers as boxes, the pager in rem identical in both languages | 201 | DONE -- 2026-10-04 (`dcb7dcd`) |
| 203 | [The figures folder on the twelve workflow swimlanes](203-figures-folder-workflow-swimlanes.md) -- sibling SVG files per language and theme, `<picture>` with the toggle swap, LF-pinned, the folder byte-twin; three-lane swimlanes on the frame primitive with the label-width rule | 202 | DONE -- 2026-10-04 (`a5aa642`) |
| 204 | [A relations figure per family](204-family-relations-figures.md) -- derived from the relation rules, one node per kind with the partner prefixes, the same-family node, 28 figures and 9 sentences, elbows ranked | 203 | DONE -- 2026-10-04 (`0fc8e07`) |
| 205 | [The flow figures per family](205-family-flow-figures.md) -- the Writes parser over workflow.md, a data path per family, a trace path for the 20 families a gate or rule reads (rules from a readiness run), STD8 drawn once | 204 | DONE -- 2026-10-04 (`0f6ddbe`) |
| 206 | [The tool figures](206-tool-figures.md) -- an effects canvas per tool with a server line per claim, a call-sequence strip per tool a recipe names, the step accented from its own label | 205 | DONE -- 2026-10-04 (`c01fab5`) |
| 207 | [The gate figures](207-gate-figures.md) -- the pipeline in the server's order, one figure per gate from the gate map, the Check clauses parsed and the definitions table read, one canvas helper | 206 | DONE -- 2026-10-05 (`3fc2798`) |
| 208 | [The skill figures](208-skill-figures.md) -- the skills' text read once, the citation matrix, the lifecycle map with only the stated moves, a strip per skill in a fold | 207 | DONE -- 2026-10-05 (`19dfdcc`) |
| 209 | [The logo, the icon and the tagline](209-logo-icon-tagline.md) -- the two-half paving mark with a return arc on the icon, the lockups and the favicon; the tagline reconsidered on every surface | 208 | DONE -- 2026-10-05 (`ee39799`) |
| 210 | [Release 6.1.0](210-release-6.1.0.md) -- the stamp on every surface, the stock guide's history key, the lab fixture refreshed through the engine, Lighthouse 100/100/100, push and tag on the operator's word | 209 | DONE -- 2026-10-04 UTC (`a48bd35`, tag `v6.1.0`, CI run 37243052723 green) |

### Prompts return to the store -- plans 192-200 -> v6.0.0 (released 2026-10-04; maintainer-executed)

Master record: [192-200-batch-prompts.md](192-200-batch-prompts.md) (the operator's rulings G1-G16 and
P1-P21 of 2026-10-04, after the user-guide review's interview and a devil's-advocate round). Project
prompts stop being files: a `prompts` family (`PRT-`) with a status, provenance and a binding to the
scenario skill that reads it; `handoff_emit` demands an Approved kickoff row; the stock operator guide
moves to `<package>/README.md`; `package_migrate` converts a package's prompt files on the operator's
word; the halves wording; the ACMP brief; the release. The user guide round 2 (plans 201-210) follows
the tag. Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 192 | [The `prompts` family](192-prompts-family.md) -- migration 008, the registry row, the `plugin_skill` write guard, the catalog and governance rows, the guide ids | 191 | DONE -- 2026-10-04 (`6d6c883`) |
| 193 | [The engine paths over prompt rows](193-engine-paths.md) -- the emit demands an Approved kickoff row named by `entry_point`, G-INJECT and the scans over the rows, the Prompts roster in the note (marker v7), `prompt-ids-resolve` and `prose-plain-english` over `prompts.title` / `body`, `entity_query(plugin_skill=)` | 192 | DONE -- 2026-10-04 (`8c5e3c2`) |
| 194 | [The stock operator guide at `<package>/README.md`](194-operator-guide-root.md) -- the managed emission targets the package root, a pre-v6 copy under `prompts/` is a leftover, the stock body speaks of rows, the note and the guide name the root, a stale pattern names the old paths | 193 | DONE -- 2026-10-04 (`4a19c47`) |
| 195 | [`package_migrate` converts prompt files to rows](195-migrate-prompt-files-to-rows.md) -- the staged plan (rows, the backup folder, the stock guide removed, `entry_point` on the kickoff, the folder gone), the v2 chain files-then-rows, replayed on ACMP's package copy | 194 | DONE -- 2026-10-04 (`ddfa49f`) |
| 196 | [The bundle's teaching surface](196-bundle-teaching-surface.md) -- prompt rows in the front door, workflow stage 20, handoff, the templates and the skills; sixteen scenario skills read their bound rows; "planning agent / executing agent" -> the two halves; the vocabulary's two terms | 195 | DONE -- 2026-10-04 (`f5347d2`) |
| 197 | [The docs, the README and the guide's prose](197-docs-readme-guide-prose.md) -- prompt rows and the two halves in methodology, README, architecture (the actors section), SECURITY boundary 3, the Keystone chain's 6.0 step, design-decisions §23 D-PROMPT-ROWS; 34 guide entries EN + AR | 196 | DONE -- 2026-10-04 (`f215fe6`) |
| 198 | [Stamp 6.0.0, the Always flip, the fixtures, the evals, lab beat 34](198-stamp-6.0.0-always-fixtures-evals.md) -- the MAJOR entry; `prompt` Always; P19 kickoff by file name; the Prompts section; the fixtures and the sample migrated by the engine; a real agent drove the migration in the lab | 197 | DONE -- 2026-10-04 (`4f3efec`) |
| 199 | [The ACMP brief 6.0.0](199-acmp-brief-6.0.0.md) -- every class replayed on a git-archive copy of the field package first (`acmp_replay11.py`); O24/O25 owned; the STOP (approve the kickoff, bind two rows, rewrite the file-era pointers) with the recommendation marked | 198 | DONE -- 2026-10-04 (`7b9a5c4`) |
| 200 | [Release 6.0.0](200-release-6.0.0.md) -- the batch record closed with SHAs, the index rows, the memory, check.py and the selftest green; the push on the operator's word, CI, the tag | 199 | DONE -- 2026-10-04 (the commit this row lands in; push and tag in the ledger) |

### The plain-English batch (ASD-STE100) -- plans 176-191 -> v5.9.0 (2026-10-03; maintainer-executed)

Master record: [176-191-batch-ste.md](176-191-batch-ste.md) (the approved plan, revision 2 after the
maintainer's own devil's-advocate pass, the operator's strict review and three advisor calls; 32
interview answers, rulings R1-R29 of the batch, R30-R48 from the wave and beat reviews). The upstream skill
[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (MIT) is ported, not
referenced: a bundle linter, a fourteenth lint with a roster that grows per wave, an advisory
readiness rule, two skills, four rewrite waves, lab beat 33, the ACMP brief, the release.
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 176 | [`handoff_emit` says what it writes](176-handoff-emit-description.md) -- the registered description named prompts the tool stopped writing in v3; README rows for plans 170-174 | -- | DONE -- 2026-10-03, `d7ca9f8` |
| 177 | [`_CONVERTED_HINTS` names live skills](177-converted-hints-name-live-skills.md) -- the hints named two files retired in 5.0.0; they name `/tamheed:<name>` skills, one sentence each | 176 | DONE -- 2026-10-03, `3e10ba1` |
| 178 | [`references/handoff.md` no longer claims the template twin](178-handoff-reference-template-twin.md) -- the reference contradicted the plan-132 test for seven releases | 176 | DONE -- 2026-10-03, `70e63d9` |
| 179 | [The vocabulary](179-vocabulary.md) -- a census of 16 synonym groups with name positions, one interview round (R30-R33), `references/vocabulary.md` frozen | 178 | DONE -- 2026-10-03, `74a6725` |
| 180 | [`server/ste_lint.py`, its suite, the third-party notice](180-ste-lint-module.md) -- the upstream linter ported with the paragraph join, the `ast` extractor, the vocabulary tables, Arabic and the allow marker; 21 tests, the twelfth suite | 179 | DONE -- 2026-10-03, `b0733b4` |
| 181 | [Lint 14, plain English, with a roster that grows per wave](181-lint-14-plain-english.md) -- one file rostered, 90 pending, a prose file in neither fails; six lint tests | 180 | DONE -- 2026-10-03, `dd1cc85` |
| 182 | [Readiness rule `prose-plain-english` (advisory)](182-readiness-prose-plain-english.md) -- register statements, prompt files and the latest handoff linted, `GT-` terms never a finding, counts per rule, the skill cue | 180 | DONE -- 2026-10-03, `8ec513b` |
| 183 | [Skills `plain-english` and `ste-rewrite`; every count surface](183-skills-plain-english-ste-rewrite.md) -- the discipline and the operator-run rewrite ceremony, the note's skills line, the stock README under 5.9.0, 1 / 17 / 9 | 182 | DONE -- 2026-10-03, `a537a1e` |
| 184 | [Wave 1: tool descriptions, server messages, note v6, the hook](184-wave-1-engine-strings.md) -- 207 hard findings to 0 on 16 rostered files, the note as v6 with the hook reading both, 16 pins re-aimed | 183 | DONE -- 2026-10-03 `883412b` |
| 185 | [Wave 2: the 27 skills](185-wave-2-skills.md) -- 818 hard findings to 0 on 27 skills, the glob rostered, triggers and 22 pins kept, two names-table rows, one allow marker in a lint-13 probe | 184 | DONE -- 2026-10-03 `8beaecd` |
| 186 | [Wave 3: references, templates, stock README, server README, CANONICAL](186-wave-3-references-templates.md) -- 1,010 hard findings to 0 on 37 files, six globs rostered, 41 pins kept, the stock body under its 5.9.0 key, `Validate:` → `Check:` in workflow.md | 185 | DONE -- 2026-10-03 `3f281eb` |
| 187 | [Wave 4a: human docs, root files, the lab and evals READMEs](187-wave-4a-human-docs.md) -- 1,262 hard findings to 0 on 13 files (flavored), seven globs rostered, 21 pins kept, both manifest descriptions name both halves, six stale counts corrected under R38 | 186 | DONE -- 2026-10-03 `f745edb` |
| 188 | [Wave 4b: the guide EN and AR, the Writing discipline section](188-wave-4b-guide.md) -- 1,495 hard findings to 0 over 1,284 bilingual entries, `content.py` rostered by import, pending empty, the vocabulary tables rendered from the file with Arabic twins (92 new ids), 14 pins kept | 187 | DONE -- 2026-10-04 `1d4408b` |
| 189 | [Stamp 5.9.0, the evals re-aimed, `ste-clean`, lab beat 33](189-stamp-evals-lab-beat-33.md) -- six surfaces stamped, the 5.9.0 CHANGELOG entry with the migration note, the stock body re-keyed, `ste-clean` + three eval re-aims + two rubric lines, beat 33 by a real agent on a scratch copy ($2.29, two turns, no refusal) then the fixture refreshed in-process; the agent found three skill gaps, closed in the skill | 188 | DONE -- 2026-10-04 `90947b8` |
| 190 | [The ACMP brief 5.9.0](190-acmp-brief-5.9.0.md) -- `plans/briefs/acmp-5.9.0.md` under the strict rules, rostered by path (lint 14 admits a rostered file under an exempt prefix), every class replayed on a `git archive` copy of the field at its head, the release recipe's ninth step | 189 | DONE -- 2026-10-04 `7f11e41` |
| 191 | [Release 5.9.0: the batch record, the README rows, push, tag](191-release-5.9.0.md) -- sections 2-5 closed, sixteen rows with SHAs, the push on the operator's word, CI on every job, the tag on the CI-green commit, the bundle diff against the tag empty | 190 | DONE -- 2026-10-04 (the release commit; the push and the tag recorded in the ledger) |

### Field cycle FB-028 -- plans 170-174 -> v5.8.1 (2026-09-30; maintainer-executed)

Master record: [170-174-batch-fb028.md](170-174-batch-fb028.md) (rulings R59-R64; the headless lab
harness recipe; released as a PATCH). Rows added 2026-10-03 (plan 176): the cycle shipped without them.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 170 | The correction of 5.8.0: a reload restarts the server, not what the session lists (FB-028) | -- | DONE -- 2026-09-30, `5a38184` |
| 171 | The 5.8.1 stamp with its history key; the reload replication (R62) | 170 | DONE -- 2026-09-30, `1c1b812` + `7acf957` |
| 172 | The lab driven by a real agent, headless, against the 5.8.1 working tree (R60/R61) | 171 | DONE -- 2026-09-30, `a24f67e` |
| 173 | Lab beat 32 on the fixture, the evals re-aimed, three corrections to the report | 172 | DONE -- 2026-09-30, `12f7a87` |
| 174 | Release v5.8.1, the brief `briefs/acmp-5.8.1.md`, close-out (R63, R64) | 173 | DONE -- 2026-09-30, `67889cc`, tag `v5.8.1` |

### The user guide, review round 1 -- plan 175 (2026-10-02; pair review, maintainer + reviewer)

| # | Plan | Depends on | Status |
|---|---|---|---|
| 175 | [The user guide, review round 1](175-guide-review-round-1.md) -- the rendered `index.html` walked section by section in interview style; every accuracy concern settled against the engine, every visualization defect named by geometry; ledger first, one fix batch at the end | the guide commits c3874e4 / 0b13ba7 / e818d5a | DONE -- 2026-10-03, `f59a72c` (+ one follow-up): 22 rounds walked, 60-odd ledger rows, the diagram engine gained a geometry lint, the guide and the bundle's self-description carry both halves |

### Field cycle FB-026 / FB-027 -- plans 165-169 -> v5.8.0 (2026-09-30; maintainer-executed)

Master record: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md) (the approved plan, revision
2 after the maintainer's own devil's-advocate pass, the operator's strict review and three advisor calls;
3 interview rulings R56–R58; execution order 165 → 166 → 167 → 168 → 169). By R53 the field wrote no
report: two feedback rows came back, both questions (a resumed session kept the old descriptions; a
handoff line carried eight handoffs past its answer), and the field's own secret-scan defect measured the
review page's history as its whole cost. The batch: `handoff-repeated`, an advisory that names the lines
of the latest handoff carried word for word through three handoffs; the review page one row per line
(about 4 MB of patch text per export before, kilobytes after); the docs corrected on what a resumed
session shows. No migration. Brief: [briefs/acmp-5.8.0.md](briefs/acmp-5.8.0.md).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 165 | [`handoff-repeated`, the advisory](165-handoff-repeated-the-advisory.md) | — | DONE — 2026-09-30 `248166f` |
| 166 | [The review page: one row per line](166-the-page-one-row-per-line.md) | 165 | DONE — 2026-09-30 `0c4917e` + `c9184c0` (one assertion corrected) |
| 167 | [Teaching, docs and the corrections of 5.7.0](167-teaching-docs-and-the-corrections-of-570.md) | 166 | DONE — 2026-09-30 `cbec045` |
| 168 | [The version stamp, then lab beat 31 + evals](168-stamp-then-lab-beat-31.md) | 167 + full gate (suites; 13 lints; canonical; evals 3/3 incl. 4 new assertions) | DONE — 2026-09-30 `2fe5289` (stamp before the beat; beat 31 held on its first run) |
| 169 | [Tag v5.8.0, the brief file, close-out](169-release-v580.md) | 168 | DONE — 2026-09-30, tag `v5.8.0` on the release commit (CI green); the field closes its two rows and checks the classes in an ordinary session |

### Field cycle findings_39 -- plans 160-164 -> v5.7.0 (2026-09-29; maintainer-executed) -- the closing round

Master record: [160-164-batch-findings-39.md](160-164-batch-findings-39.md) (the approved plan, revision
3 after two devil's-advocate reviews, 5 interview rulings R51–R55; execution order 160 → 161 → 162 → 163
→ 164). The field returned no defect, no feedback row and no numbered brief error. It reported one read
that had dropped rows in silence. The batch: `entity_query` takes the review page's id order, the two
journal tools refuse an item key they do not take, and three tools register a contract where a client
reads it. The round's largest finding is the maintainer's own: v5.6.1 shipped a rule in a docstring and
called it the tool's description; a docstring reaches no client. No migration. By R53 this is the last
round that asks the field for a report: [briefs/acmp-5.7.0.md](briefs/acmp-5.7.0.md).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 160 | [The query tool takes the page's order, and says so to the client](160-the-pages-order-in-the-query-tool.md) | — | DONE — 2026-09-29 `67a537d` |
| 161 | [Two write tools refuse an unknown key, and name their keys to the client](161-the-write-tools-refuse-an-unknown-key.md) | 160 | DONE — 2026-09-29 `2607652` |
| 162 | [Teaching, docs and the corrections of 5.6.1](162-teaching-docs-and-the-corrections-of-561.md) | 161 | DONE — 2026-09-29 `399d688` |
| 163 | [The version stamp, then lab beat 30 + evals](163-stamp-then-lab-beat-30.md) | 162 + full gate (suites; 13 lints; canonical; evals 3/3 incl. 3 new assertions) | DONE — 2026-09-29 (stamp before the beat; the beat held on its second run; `cbad9d6`) |
| 164 | [Tag v5.7.0, the brief file, close-out, housekeeping](164-release-v570.md) | 163 | DONE — 2026-09-29, tag `v5.7.0` on the release commit (CI green); the field checks the classes in an ordinary session and reports only a failure, as a feedback row |

### Field cycle findings_38 -- plans 156-159 -> v5.6.1 (2026-09-28; maintainer-executed)

Master record: [156-159-batch-findings-38.md](156-159-batch-findings-38.md) (the approved plan, revision
3 after a devil's-advocate review, 5 interview rulings R46–R50; execution order 156 → 157 → 158 → 159).
The field returned no defect, no feedback row and no numbered brief error; the batch is teaching and
docs the maintainer's own review corrected: a limited read returns the lowest ids and never the
newest rows, the close-out's last commit is unbound by rule, the review page's bytes hold on one UTC
date, and a handoff says what is true when it is written. No engine behaviour changes. The brief to
the field project is a committed file, read by path: [briefs/acmp-5.6.1.md](briefs/acmp-5.6.1.md).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 156 | [What a limited read returns, the unbound commit, three sentences](156-what-a-limited-read-returns-and-the-unbound-commit.md) | — | DONE — 2026-09-28 `1be1305` |
| 157 | [The page's date, and the docs sweep for v5.6.1](157-the-pages-date-and-docs-sweep-findings-38.md) | 156 | DONE — 2026-09-28 `1b3ce75` |
| 158 | [The version stamp, then lab beat 29 + evals](158-stamp-then-lab-beat-29.md) | 157 + full gate (suites; 13 lints; canonical; evals 3/3 incl. 3 new assertions) | DONE — 2026-09-28 (stamp before the beat; the scratch phase first; held on the first run) `e6fe055` |
| 159 | [Tag v5.6.1, the brief file, close-out](159-release-v561.md) | 158 | DONE — 2026-09-28, tag `v5.6.1` on the release commit (CI green); the brief rides with the field's next ordinary session: four reads, no pre-registration, no store write, one sentence for the operator's word |

### Field cycle findings_37 -- plans 151-155 -> v5.6.0 (2026-09-28; maintainer-executed)

Master record: [151-155-batch-findings-37.md](151-155-batch-findings-37.md) (the approved plan after a
devil's-advocate review, 9 interview rulings R36–R44; execution order 151 → 152 → 153 → 154 → 155). The
field returned no defect and no feedback row; the batch is the release named on two surfaces that
could not say it (the trace line, the review page), the export anchored on the commit in five step
lists, two sentences in the skills, and lint 13's negated shape. The brief to the field project is a
committed file, read by path: [briefs/acmp-5.6.0.md](briefs/acmp-5.6.0.md).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 151 | [The version in the trace line and on the review page](151-the-version-in-the-trace-and-on-the-page.md) | — | DONE — 2026-09-28 `e151e3d` |
| 152 | [The export before the commit, two sentences, lint 13's negated shape](152-the-export-before-the-commit-and-two-sentences.md) | 151 | DONE — 2026-09-28 `6bae045` |
| 153 | [Docs + diagrams sweep for v5.6.0](153-docs-and-diagrams-sweep-findings-37.md) | 151-152 | DONE — 2026-09-28 `9db4b7c` |
| 154 | [The version stamp, then lab beat 28 + evals](154-stamp-then-lab-beat-28.md) | 153 + full gate (suites; 13 lints; canonical; evals 3/3 incl. 4 new assertions) | DONE — 2026-09-28 (stamp before the beat; the scratch phase first; held on the first run) `21a25f5` |
| 155 | [Tag v5.6.0, the brief file, close-out](155-release-v560.md) | 154 | DONE — 2026-09-28, tag `v5.6.0` on the release commit (CI green); the brief prescribes no store write, names a condition for every class and an instrument for every question |

### Field cycle findings_36 -- plans 146-150 -> v5.5.0 (2026-09-27; maintainer-executed)

Master record: [146-150-batch-findings-36.md](146-150-batch-findings-36.md) (the approved plan after a
devil's-advocate review, 9 interview rulings R27–R35; execution order 146 → 147 → 148 → 149 → 150). The
field returned no defect and no feedback row; the batch is two words the bundle had used as one
(a lesson binds by its status, the note's roster is what is rendered), the roster on the review page,
three sentences in the skills, and the docs the maintainer's own measurement corrected. The brief to
the field project is a committed file, read by path: [briefs/acmp-5.5.0.md](briefs/acmp-5.5.0.md).
Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 146 | [Two words in the engine, and the roster on the review page](146-two-words-and-the-note-roster.md) | — | DONE — 2026-09-27 `de49286` |
| 147 | [The two words and three sentences in the skills](147-the-two-words-and-three-sentences.md) | 146 | DONE — 2026-09-27 `ac6c96b` |
| 148 | [Docs + diagrams sweep for v5.5.0](148-docs-and-diagrams-sweep-findings-36.md) | 146-147 | DONE — 2026-09-27 `837865c` |
| 149 | [The version stamp, then lab beat 27 + evals](149-stamp-then-lab-beat-27.md) | 148 + full gate (suites; 13 lints; canonical; evals 3/3 incl. 4 new assertions) | DONE — 2026-09-27 (stamp before the beat; the scratch phase first; held on the fourth run, the first three stopped before the fixture) `5f4ffbb` |
| 150 | [Tag v5.5.0, the brief file, close-out](150-release-v550.md) | 149 | DONE — 2026-09-27, tag `v5.5.0` on the release commit (CI green); the recipe of the brief ran on the copy first and names what it discharges |

### Field cycle findings_35 -- plans 141-145 -> v5.4.0 (2026-09-27; maintainer-executed)

Master record: [141-145-batch-findings-35.md](141-145-batch-findings-35.md) (the approved plan after a
devil's-advocate review, 8 interview rulings R19–R26; step 0, then 141 → 142 → 143 → 144 → 145). The
field returned no defect and no feedback row; the batch is one field in the trace line, two lessons,
the interview's default, and the docs the maintainer's own transcript measurement corrected. The
brief to the field project is a committed file, read by path:
[briefs/acmp-5.4.0.md](briefs/acmp-5.4.0.md). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 141 | [The trace carries the session](141-trace-carries-the-session.md) | step 0 (the real event measured) | DONE — 2026-09-27 `0be3a56` |
| 142 | [Two absorbed lessons and the interview's default](142-two-lessons-and-the-interview-default.md) | — | DONE — 2026-09-27 `983df9d` |
| 143 | [Docs + diagrams sweep for v5.4.0](143-docs-and-diagrams-sweep-findings-35.md) | 141-142 | DONE — 2026-09-27 `5037176` |
| 144 | [The version stamp, then lab beat 26 + evals](144-stamp-then-lab-beat-26.md) | 143 + full gate (suites; lints; canonical; evals 3/3 incl. 2 new assertions) | DONE — 2026-09-27 `85007b4` (stamp before the beat; the scratch phase first; held on the first run) |
| 145 | [Tag v5.4.0, the brief file, close-out](145-release-v540.md) | 144 | DONE — 2026-09-27, tag `v5.4.0` on the release commit (CI green); every recipe of the brief ran on the copy first |

### Field cycle findings_34 -- plans 136-140 -> v5.3.0 (2026-09-27; maintainer-executed)

Master record: [136-140-batch-findings-34.md](136-140-batch-findings-34.md) (the approved plan after a
devil's-advocate review, 4 interview rulings R15–R18; execution order 136 → 137 → 138 → 139 → 140). The
field returned no defect this round; the batch is two instruments, one hint, the carried rules' generic
residue, and the docs the field falsified. The brief to the field project is a committed file, read
by path: [briefs/acmp-5.3.0.md](briefs/acmp-5.3.0.md). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 136 | [The observed lock, the render hint, the hook trace](136-observed-lock-render-hint-hook-log.md) | — | DONE — 2026-09-27 `b8e1f7c` |
| 137 | [The residue: thirteen sentences from twelve partial rules, and E3](137-residue-sentences-and-e3.md) | — | DONE — 2026-09-27 `dbd81e1` |
| 138 | [Docs + diagrams sweep for v5.3.0](138-docs-and-diagrams-sweep-findings-34.md) | 136-137 | DONE — 2026-09-27 `5b9d2ec` |
| 139 | [The version stamp, then lab beat 25 + evals](139-stamp-then-lab-beat-25.md) | 138 + full gate (suites; lints; canonical; evals 3/3 incl. 3 new assertions) | DONE — 2026-09-27 `87bdb1d` (stamp before the beat; the ACMP replay on the final bundle held) |
| 140 | [Tag v5.3.0, the brief file, close-out](140-release-v530.md) | 139 | DONE — 2026-09-27, tag `v5.3.0` on the release commit (CI green); the brief is a committed file read by path |

### Field cycle findings_33 -- plans 129-135 -> v5.2.0 (2026-09-26; maintainer-executed)

Master record: [129-135-batch-findings-33.md](129-135-batch-findings-33.md) (the approved plan after a
devil's-advocate review, 8 interview rulings R7–R14; execution order 129 → 130 → 131 → 132 → 133 → 134
→ 135). The brief to the field project is a committed file, read by path:
[briefs/acmp-5.2.0.md](briefs/acmp-5.2.0.md). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 129 | [`stock_merged` verifies the whole declared release (FB-023)](129-stock-merged-whole-body.md) | — | DONE — 2026-09-26 `8a75914` |
| 130 | [The stale-warning block's home, text and removal (FB-024)](130-stale-block-home-text-removal.md) | — | DONE — 2026-09-26 `b72296e` |
| 131 | [Two more cues, the stranded rule's population, the skill guard](131-cues-populations-skill-guard.md) | — | DONE — 2026-09-26 `96506c3` |
| 132 | [The sixteen and the forty-four rules, the template's pointer, the hook's caps (FB-025)](132-skills-template-hook-caps.md) | 131 | DONE — 2026-09-26 `9424a12` |
| 133 | [Docs + diagrams sweep for v5.2.0](133-docs-and-diagrams-sweep-findings-33.md) | 129-132 | DONE — 2026-09-26 `8975009` |
| 134 | [The version stamp, then lab beat 24 + evals](134-stamp-then-lab-beat-24.md) | 133 + full gate (suites; lints; canonical; evals 3/3 incl. 5 new assertions) | DONE — 2026-09-26 `7107122` (stamp before the beat; M8 through Claude Code PASS) |
| 135 | [Tag v5.2.0, the brief file, close-out](135-release-v520.md) | 134 | DONE — 2026-09-26, tag `v5.2.0` on the release commit (CI green); the brief is a committed file read by path |

### Field cycle findings_32 -- plans 120-128 -> v5.1.0 (2026-09-26; maintainer-executed)

Master record: [120-128-batch-findings-32.md](120-128-batch-findings-32.md) (the approved plan after a
devil's-advocate review, 21 interview rulings; execution order 120 → 121 → 122 → 123 → 124 → 125 → 126
→ 127 → 128). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 120 | [The menu contract, the result skill hints, the note sentence](120-menu-contract-and-skill-hints.md) | — | DONE — 2026-09-26 `80d9779` |
| 121 | [Migration 007: the `handoff` journal kind + `skills.upstreamed_to`](121-migration-007-handoff-and-upstreamed-to.md) | — | DONE — 2026-09-26 `80d9779` |
| 122 | [The resume block, `handoff-current`, `lessons-stranded`, the Resume panel](122-resume-block-and-advisories.md) | 121 | DONE — 2026-09-26 `144074f` |
| 123 | [The SessionStart hook](123-session-start-hook.md) | 122 | DONE — 2026-09-26 `88cb788` (loading test M1 PASS) |
| 124 | [session-handoff, the resume step, five practices, two absorbed steps, the retirement doctrine, the AGENTS template](124-skills-and-agents-template.md) | 121 | DONE — 2026-09-26 `18d8ae8` |
| 125 | [handoff_emit scans: marker verified, oversized prompt, skill files, two detectors, the note span stripped](125-handoff-emit-scans.md) | — | DONE — 2026-09-26 `8dfb229` |
| 126 | [Docs + diagrams sweep for v5.1.0](126-docs-and-diagrams-sweep-findings-32.md) | 120-125 | DONE — 2026-09-26 `a2bd7b8` |
| 127 | [The version stamp, then lab beat 23 + evals](127-stamp-then-lab-beat-23.md) | 126 + full gate (suites; lints; canonical; evals 3/3 incl. 7 new assertions) | DONE — 2026-09-26 `519005d` (stamp before the beat; M4 = 9, M5 every class observed) |
| 128 | [Tag v5.1.0, this repo's local enable, the ACMP brief, close-out](128-release-v510.md) | 127 | DONE — 2026-09-26, tag `v5.1.0` on `519005d` (CI green); the brief delivered in two parts (transcript) |

### Field cycle findings_31 -- plans 112-119 -> v5.0.0 (2026-09-24; reviewer-executed)

Master record: [112-119-batch-findings-31.md](112-119-batch-findings-31.md) (the approved plan after a
devil's-advocate review; execution order 114 → 115 → 116 → 112 → 113 → 117 → 118 → 119 — the surfaces
112/113 edit are created by 114-116). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 112 | [The findings_31 doc cycle: FB-017's step 15, the NOT NULL clause, the paste verifier, the brief's five errors](112-findings-31-doc-cycle.md) | 116 | DONE — 2026-09-25 |
| 113 | [`carries` (wbs-item -> deferred-work) + the `deferred-work-carried` advisory, migration 006 (FB-018)](113-carries-relation-and-deferred-work-carried.md) | 116 | DONE — 2026-09-25 |
| 114 | [The front door moves into `skills/`; the skills lint](114-front-door-moves-into-skills.md) | §0 (passed) | DONE — 2026-09-24 `e7172c3` |
| 115 | [Seven discipline skills adopted from ACMP under tamheed names](115-seven-discipline-skills.md) | 114 | DONE — 2026-09-25 |
| 116 | [Sixteen scenario skills + engine v5: note v5, README-only library, leftovers retired on refresh](116-scenario-skills-and-engine-v5.md) | 114, 115 | DONE — 2026-09-25 |
| 117 | [Docs + diagrams sweep for v5.0.0](117-docs-and-diagrams-sweep-v5.md) | 112-116 | DONE — 2026-09-25 |
| 118 | [Lab beat 22](118-lab-beat-22-v5.md) | 112-117 + full test (9/9 vs 0/9 on `v4.14.0`; invariants 2/2; selftest 19/19; CI green) | DONE `80c7173` — one dispatch, 7/7 discriminate; F-10 (grep `tests/` too) recorded |
| 119 | [Release v5.0.0 + the ACMP brief](119-release-v500.md) | 118 | DONE — 2026-09-25, tag `v5.0.0` on `bbdeb4a`; the fixture's guide followed by tool |

### Field cycle findings_30 -- plans 106-111 -> v4.14.0 (2026-09-24; reviewer-executed)

Master record: [106-111-batch-findings-30.md](106-111-batch-findings-30.md) (the approved plan after a
devil's-advocate review; execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 106 | [`ready` follows its doctrine: false while a blocking rule is indeterminate, with the list (FB-016)](106-ready-follows-its-doctrine.md) | FB-016 | DONE — 2026-09-24 `6013cd6` |
| 107 | [Three honesty fixes: `deferred-work-reviewed` population, the pointer warning, the empty unanswered fold](107-three-honesty-fixes.md) | findings_30 §3.2-3.3 | DONE — 2026-09-24 |
| 108 | [`expect_unchanged` refuses the vacuous case; the sweep prompt's four gaps](108-expect-unchanged-refuses-the-vacuous-case.md) | findings_30 Q3, Q5 | DONE — 2026-09-24 |
| 109 | [Docs + diagrams sweep](109-docs-and-diagrams-sweep-findings-30.md) | 106-108 | DONE — 2026-09-24 |
| 110 | [Lab beat 21](110-lab-beat-21-findings-30.md) | 106-109 + full test (9/9 vs 0/9 on `v4.13.0`; selftest 19/19) | DONE `59fe5b5` — one dispatch, every mechanism fired; F-9 (the pointer import built the span inside the fixture) recorded |
| 111 | [Release v4.14.0](111-release-v4140.md) | 110 | DONE — 2026-09-24, tag `v4.14.0` on `83cfb12`, CI green; the fixture followed by `refresh_stock` (three guides) |

### Field cycle findings_29 -- plans 100-105 -> v4.13.0 (2026-09-23; reviewer-executed)

Master record: [100-105-batch-findings-29.md](100-105-batch-findings-29.md) (the approved plan after a
devil's-advocate review; execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 100 | [The feedback channel's middle: journaled bound-to-bound moves, `feedback-unanswered`, a third handoff warning, the fold split, the sweep prompt (FB-014)](100-the-feedback-channels-middle.md) | FB-014 | DONE — 2026-09-23 `ab0a981`; also repairs plan 093's missed `register-liveness.md` step |
| 101 | [The header read is a superset of the write (FB-015)](101-the-header-read-is-a-superset-of-the-write.md) | FB-015 | DONE — 2026-09-23 |
| 102 | [Three guard refinements: `go_no_go` presence-checked, the substitute re-run refusal, `expect_unchanged` honours omission](102-three-guard-refinements.md) | findings_29 §1, §3, §4 | DONE — 2026-09-23; security review: one HIGH (the check ran before the engine's own column writes) closed |
| 103 | [Docs + diagrams sweep](103-docs-and-diagrams-sweep-findings-29.md) | 100-102 | DONE — 2026-09-23 |
| 104 | [Lab beat 20](104-lab-beat-20-findings-29.md) | 100-103 + full test (11/11 vs 0/11 on `v4.12.0`; selftest 19/19) | DONE `faf4036` — first dispatch stopped correctly on the plan's own assertion collision (F-6); 8 new assertions, each failing on the pre-beat fixture |
| 105 | [Release v4.13.0](105-release-v4130.md) | 104 | DONE — 2026-09-23, tag `v4.13.0` on `91774b6`, CI green; the fixture followed by `refresh_stock` (two guides) |

### Field cycle findings_28 -- plans 091-099 -> v4.12.0 (2026-09-22; reviewer-executed)

Master record: [091-099-batch-findings-28.md](091-099-batch-findings-28.md) (the approved plan after a
devil's-advocate review; execution order is the row order below). Status values: PLANNED / IN PROGRESS / DONE.

| # | Plan | Depends on | Status |
|---|---|---|---|
| 091 | [The feedback teaching says what the code does (FB-013, findings_28 §3a-§3b; export wording; work_bind sentence)](091-feedback-teaching-says-what-the-code-does.md) | findings_28 | DONE — 2026-09-22 |
| 092 | [FB-003: `entity_query(search=…, context=N)` reports `occurrences`](092-search-with-context-is-a-census.md) | FB-003 | DONE — 2026-09-22 |
| 093 | [FB-002: advisory `prompt-ids-resolve` over the project's prompt files](093-prompt-ids-resolve.md) | FB-002 | DONE — 2026-09-22; no stock body change (the one 'bare' example was a wrapped code span) |
| 094 | [FB-001: `entity_upsert(type="package")` — the header on the operator's word](094-the-package-header-on-the-operators-word.md) | FB-001 | DONE — 2026-09-23; security review closed three items, incl. the operator's word = the boolean `true` everywhere |
| 095 | [FB-004: the `substitute` item on `entity_upsert`](095-the-substitute-write.md) | FB-004; 092-094 | DONE — 2026-09-23; two reviewers, one MEDIUM (a match glued to a digit) closed |
| 096 | [review.html follows plans 069-095 (Feedback + Readiness sections, the lesson tag, the waiver mark)](096-review-page-follows-the-batches.md) | maintainer ruling | DONE — 2026-09-23 |
| 097 | [Docs + diagrams sweep](097-docs-and-diagrams-sweep-findings-28.md) | 091-096 | DONE — 2026-09-23 |
| 098 | [Lab beat 19](098-lab-beat-19-findings-28.md) | 091-097 + full test (12/12 vs 0/12 on `v4.11.0`; 9 suites; selftest) | DONE `9a7aa34` — three dispatches: F-4 and F-5 (two engine crashes only the recorded fixture could show) fixed between them; 8 new assertions, each failing on the pre-beat fixture |
| 099 | [Release v4.12.0](099-release-v4120.md) — plan-058 recipe; the fixture followed by `refresh_stock` (stale-stock, no force) | 098 | DONE — 2026-09-23, tag `v4.12.0` (SHA in the tag) |

**Dependency notes (advisor plans).** 042 before 052 (a red matrix leg is unattributable
until CI has run once). 043 before 051/053 (they edit the same function; 043 settles its
transaction tail). 045's tests land before its refactor (same plan, red then green). 050 and
any later plan that changes emitted bytes share the "regenerate goldens by tool" step. 049
before 053: the first makes an empty scope visible, the second makes a brand-new row refusable
-- two questions, deliberately separate.

**Findings audited and NOT planned (still open, recorded so they are not re-audited from
scratch).** Inconsistent id ordering (`_emit_prompt_library` sorts version strings lexically
then numerically; `SUBSTR(id,4)` literals; `export_html._execution` orders the progress log by
string id) -- one helper, wrong order only past ID-010, LOW. Readiness/gate test gaps: the
whole-rule waiver branch is untested (the only WVR test's WVR-002 is expired),
`decisions-approved`/`decisions-look-architectural` have zero tests, `check.py` lints are
untested, eval `injection-brief` assertion 3 greps the `prompts` table retired in v3 (vacuous),
`evals/pkg_check.py` leaks the lock on exception. `skills.name` is rendered into the CLAUDE.md
note without the `_INJECT_RE` screen (the confirm-guard half relitigates migration 003 -- a
question). `adopt` rglob follows symlinks with no size cap. Small debt: `record.py:22-26`
`except ImportError` -> silent empty registry; `adopt.py:240-248` `ALWAYS_TYPES` hand-copied
with no sync lint; dead v1 scaffolding in `record.py:53-101`; `work_bind` journal insert
without `event_type`. Eval harness spawns a process per assertion (62% of `check.py` wall time)
and read-only assertions rewrite fixtures via `package_close`. LOW-confidence, investigate
before planning: the marker literal truncating the tool-owned note span; adopt post-flight
`ok` without an `error` key; `MigrateV3ToV4Test` shared fixture makes test order load-bearing;
string-compared dates in `_readiness_report`; PRAGMA introspection re-run per open.

**Direction (options, not defects).** The next release is another field-report cycle: adopt
mode is the least-exercised surface and its doc has drifted -- a one-day spike on one real
non-Tamheed repo, doc fixed to match. An eval rubric ledger (9 cases, 3 recorded, 6 skipped
every run -- make the gap visible in `evals/README.md`). Stages 9-13 (Explore) have no liveness
advisory the way registers do. README promises host-agnostic; the note is CLAUDE.md-only.

**Not audited.** `plans/evidence/`, `docs/history/`, bodies of `generated-samples/` and
`evals/sample-results/`, `lab/seed`, `__pycache__`. Coverage numbers were not measured.

## Program chronicle (the alignment records, condensed -- full text in git history)

- **2026-07-17** -- the v2 artifact set locked (`deliverables-review.md` APPROVED);
  registers become relational entities; ADR-0001 recorded.
- **2026-07-18** -- the program complete through plan 016; v2.0.0 released; the
  Keystone repo archived at 1.0.x.
- **2026-07-21 -> 07-23** -- the first ACMP field cycles (C11-C30): migration fidelity
  hardened release-by-release (plans 017-024); two zero-actionable acceptances (C30
  after 024, C32 after 025) set the no-plan/no-release close-out precedent.
- **2026-08-08** -- execution-shaped hardening (025, C31: stale-tree/session-trap
  lessons, the wbs-item guard exemption) and the SDK 2.0 incident (026, C33: the
  `mcp<2` pin, lint-guarded; the mcpserver port recorded as the only sanctioned
  unpin path).
- **2026-08-13** -- v3.0.0 (027): prompts leave the database; `readiness_check` + the
  guarded Implemented transition; RELATION_RULES; the note-span obligations table.
  Same-day acceptance (C34) -- the readiness engine caught a hollow slice on day one.
  v3.1.0 (028, C35): lifecycle signals + the operator guide.
- **2026-08-14** -- v3.2.0 (029, C36): the tool-owned note span, honest `force`,
  `indeterminate`. v3.2.1 (030): the README release contract, lint-enforced.
  findings_16 (C37) = the third zero-actionable acceptance. **v4.0.0 (031)**: the
  entity-model redesign -- 15 interview-locked decisions, the permanent lab, a real
  agent fired every mechanism (the lab acceptance report is the evidence). **v4.1.0
  (032)**: the prompt-surface completion -- stock-history classification + safe
  refresh (findings_14's root fix), register-liveness, the teaching lint.
- **2026-08-15** -- findings_17 (C38): the ACMP v3->v4.1.0 migration clean first-try,
  refresh field-proven, the liveness sweep to-spec; the maintainer-ordered
  **documentation audit** (three agents over 100+ files) -> **v4.2.0 (033)**: the
  OQ-rule discrimination fix, migration stash parity + the letter scale, the
  entity-guide merge, the `schemas/` deletion completed (the 4.0.0 execution miss,
  stated in the CHANGELOG), `examples/` retired, four new/extended lints, the Mermaid
  delivery, ADR-0002, this index rewrite. findings_18 (C39) same day — the ACMP 4.2.0
  run: all findings_17 repairs verified closed → **v4.2.1 (034)**: the risk-liveness
  hollow-pass guard (the rule's first real firing named six exposures),
  customization-lag visibility, the repair doctrine completed (paste-don't-retype +
  the independent verifier — the operator's own catch, adopted). Then **v4.3.0
  (035)**, the maintainer's feature ask: the lessons-learned entity family — the
  first new family since the v4 re-baseline (migration 002 validates the extension
  recipe in-tree), operator-confirmed lessons rendered into the always-loaded
  CLAUDE.md note, the staged registry-sync teaching existing v4 stores new types,
  and the lab's incremental continuation beat as the real-agent proof. findings_19
  (C40) same day — the first field lesson, and the report's headline was the tool's
  OWN hollow pass (a heading-matched classifier advising deletion of the import
  that delivers the note) → **v4.4.0 (036)**: the mechanical confirm guard (a
  lesson lands in Approved/Promoted only on the operator's flag, from any state
  including birth), lesson→skill promotion (the SKL- family + the skill-promote
  interview, full graduation into natively-loaded SKILL.md files), the
  pointer-pattern classifier, FK message parity — the three-generation memory
  (episodic journal → declarative lessons → procedural skills) complete.
- **2026-08-16** — findings_20 (C41): the model acceptance report — two fixes
  verified by REPRODUCTION, one honestly left unverified, the promotion ceremony
  run-and-declined recorded as the prompt working; one finding (the static
  registry-sync note vs the per-release DDL reality) → **v4.4.1 (037)**: the
  per-run `columns_added` report + the honest note.
- **2026-08-19/20** — findings_21 (C42): the sharpest shape yet — a content gate
  over an append-only journal with no repair path (the note about the rule became
  the only row breaking it) and `corrects` written-but-never-read → **v4.4.2
  (038)**: the journal exemption, the Superseded/Obsolete skip (the DA completing
  the trap-class), `matched` in every failure, and the corrected-entries fold —
  corrects' first consumer.
- **2026-09-06** — findings_22 (C43): an operator-commissioned integrity audit — the
  query surface had no depth, so agents read the files and a false sentence about
  why recruited every later session; plus `amends`-less scope changes, withheld
  narrated ids, a `.converted` leftover, and an uncitable byte-stability guarantee
  (which held over 488 commits). The maintainer also had the 62-row ACMP lessons
  register read for tamheed's own gaps → **v4.5.0 (039)**: `after_id`/`ids`/`search`,
  the `amends` relation (migration 004), `package_verify` + the server-only
  `integrity-verified` event (all four server-witnessed kinds now refused from
  callers), `narrated_ids`, per-file relocation of the leftover (the DA round caught
  the identical-copy collision and the registry-current no-op), the
  `lessons-note-budget` advisory, four doctrine lines from the field register, and
  a full documentation sweep.
- **2026-09-06 (later)** — findings_23 (C44), written from USING 4.5.0 for the
  close-out: every findings_22 section verified closed by observation, plus the gap
  `amends` created by arriving alone (no edge delete — and three notes, the
  maintainer's own included, naming one), the C7 counter pointed at every verdict
  row ever written, and an approval string naming the weaker safety net →
  **v4.6.0 (040)**: `retire: true` (hard delete, journaled, no gate), the
  three-bucket audit split over each active AC's latest verdict, the honest
  relocate wording, the remedy-must-exist doctrine below, lab beat 13.
- **2026-09-06 (third)** — findings_24 (C45): one GAP, no defect — under the field's
  MCP-exclusive read rule its committed slate generators (the scripts that quote every
  record the operator decides against, byte-exact) had no sanctioned route to the
  store, and the two ways out were hand-transport (their measured paragraph loss) or a
  re-implemented protocol per consumer → **v4.7.0 (041)**: `entity_export` (the tool
  writes the file the script quotes — the rule stays literally true), the
  `expect_unchanged` paste guard, a read-only CLI recorded as a future option.

## Dependency notes

- Everything mechanical routes through **`python check.py`** -- the suites, the lint
  battery (registry/DDL/catalog sync, version + CHANGELOG discipline, the teaching-
  surface vocabulary gate, dead references, template copies, stock-history currency),
  canonical form, and the eval fixtures. CI runs exactly that command.
- **Frozen surfaces:** released CHANGELOG entries; `plans/evidence/**` (verbatim);
  `docs/history/**`; DONE plan files (post-acceptance addenda only); shipped
  migrations (append-only). The v1 machinery is gone (validator + importer retired at
  v4.0.0; the `schemas/` deletion completed at v4.2.0) -- nothing v1 is "frozen-kept"
  anymore.
- **Actively maintained surfaces:** the bundle (`plugins/tamheed/**`, templates
  included -- swept each release), `docs/**`, and the five version-stamped files
  (root README, server README, prompts README, SKILL.md, artifact-catalog.md --
  lint 8).
- The live field deployment is **ACMP** (`../acmp`, package `tamheed-package`, on v4
  since findings_17). Its findings files drive the verify-then-plan cycle;
  zero-actionable findings close with evidence only.

## Locked decisions (maintainer, 2026-07-11 — recorded here so no executor relitigates)

D-NAME Tamheed · D-REPO-1 new repo carrying full history (push `--all`+`--tags`, NOT `--mirror` —
refs/pull are hidden refs; plans/ committed pre-push) · D-REPO-2 keystone end-state = frozen +
successor notice (plan 016) · D-REPO-3 Track B plans live in the tamheed repo · D-REPO-4
agent-facing migration runbook `docs/migrate-from-keystone.md` linked from both READMEs ·
D-REPO-5 **v1 stays fully working for its projects; migration is operator-initiated — Keystone
hints (once per session), never forces, and agents never auto-migrate** ·
D-STORE text-canonical JSONL + SQLite runtime, entity-level modeling ·
D-REVIEW HTML-only human surface · D-MCP official Python SDK (launch via uv/PEP 723, pip
fallback) · D-U1 DEC- statuses = 5 + Implemented · D-U3 CI checks stay stdlib · D-UPDATE update
mode = diff-aware re-derivation + progress sync + agile scope change · D-ADOPT brownfield adopt
mode · ASM-A v1 = migrate-only · ASM-B bootstrap deleted entirely · ASM-C the skill bundle stays
Markdown · ASM-D Python floor rises to the MCP SDK's (≥3.10).

> **Currency annotations (plan 033):** these decisions are the 2026-07-11 record, kept
> verbatim. Where a later maintainer-locked decision superseded one, the newer record
> governs: D-REPO-5's "v1 stays fully working / Keystone hints" clauses are superseded
> by the v4.0.0 v1-retirement (plan 031, ADR-0002) -- the two-step escape route via
> tamheed 3.2.1 is the surviving promise. Nothing else in this list has been superseded.

> **Doctrine added 2026-09-06 (plan 040, findings_23 §1):** a remedy named by a gate
> note, an advisory, a refusal text, or a release note must be an operation the server
> exposes; the lab beat performs every named remedy end to end. Recorded because the
> maintainer's own 4.5.0 upgrade note told the field to "delete + re-add" an edge the
> server could not delete — the findings_21 §1 shape, from the maintainer's hand.

## Findings considered and rejected (do not re-audit)

- `gate_set` re-reads `manifest.json` once after `load_package` — a single small-file re-read,
  below any optimization bar.
- `DOCUMENT_STATUSES` tolerating "Accepted" for ADR documents — common ADR convention
  (accepted≈approved); a laxness, not a break.
- `--owner` argument not regex-validated in the bootstrapper — no injection sink (list-argument
  subprocess, JSON-encoded output); moot anyway once plan 009 deletes the bootstrapper.
- `_guess_id_column` best-ratio-across-columns mis-pick on tables with NO recognized ID header —
  real but low-priority once plan 001 fixes the header path; the v2 DB makes it obsolete.
- Old plans "004 check-script", "006 manifest reconciliation", "007 state-schema enum" from the
  pre-scope-expansion batch: folded into 013, 010, and 010 respectively (the manifest/state
  quirks are now documented migration inputs, not things to fix in place).
- **In-place rename of this repo to Tamheed**: superseded by the new-repo strategy (user
  decision, 2026-07-11) — old plan 005 replaced by `005-b1-bootstrap-tamheed-repo.md`.

*Advisor audit 2026-09-10 (plans 042–053) — rejected:*

- **Whole-store rewrite per mutation** (`store.commit()` dumps every table on every commit;
  ~34% of suite time): sub-100 ms on real field packages (the C31 measurement: 29 files /
  3.1 MB ≈ 0.02 s per guard); an incremental dump is a MED-risk change to the byte-canonical
  invariant for no field-visible gain.
- **Parallel test suites / `check.py -j`**: the gate is ~seconds-to-a-minute; the eval
  harness's per-assertion process spawn is the real cost and is recorded above as open.
- **Bumping `actions/checkout@v4` / `setup-python@v5`**: current majors; a diff for its own sake.
- **SHA-pinning GitHub Actions**: read-only `permissions: contents: read`, no secrets, no
  publish step — the threat the pin defends against has no target here.
- **A `pyproject.toml`**: no build step, stdlib only, PEP 723 carries the one dependency
  (locked: D-U3, ASM-C).
- **`.vscode/` tracked in git**: false premise — `git ls-files .vscode` is empty.
- **`migrate-dialect-fixture` eval case "stale"**: documented HISTORICAL in `evals/README.md`.
- **Implementing `--dry-run`**: decided 2026-09-10 to remove the docs claim instead (plan 048);
  the wording is preserved in that commit's diff if it is ever built.
- **Raising the `mcp` floor above `>=1.2`** as part of plan 052: a floor change needs the lowest
  working version verified first; recorded as a future option, not bundled.
- **Eval harness: one process per assertion** (~60% of `check.py` wall time): a per-case
  process needs the runner to know the primitives' state, and the read-only assertions'
  `package_close` rewrites are byte-identical on canonical fixtures — cost is CI seconds,
  risk is a harness rewrite; not worth it. (2026-09-12)
- **`work_bind` journal row without `event_type`**: the DDL defaults `event_type` to `'note'`
  and names it "the deliberate escape hatch"; a shared insert helper for two INSERTs with
  different column sets is an abstraction with one and a half callers. (2026-09-12)
- **Memoizing PRAGMA introspection per open**: unmeasured; the open→close cycle is dominated
  by the canonical dump. (2026-09-12)
- **String-compared waiver `expires` dates**: the column is documented ISO (`YYYY-MM-DD`) and
  `_now()` writes ISO; string order is date order for that shape. (2026-09-12)
- **`MigrateV3ToV4Test` shared fixture order**: the one mutating test restores in `finally`;
  `MigrateFailurePathTest` (plan 045) is per-test. (2026-09-12)
- **adopt `rglob` follows symlinked directories**: false — `Path.rglob("*")` does not expand
  `**` through directory symlinks; symlinked *files* are covered by plan 055's size cap. (2026-09-12)

## Future options recorded (not planned)

- **A FOREIGN KEY failure raised by the index trigger is unnamed** (lab beat 18, F-2, 2026-09-22):
  `entity_upsert`'s FK handler names the offending reference only when it is a column of the row
  written; when the failing reference is `entity_index.entity_type` (a family missing from a stale
  registry), the error reads bare `FOREIGN KEY constraint failed`. The remedy is `package_migrate`
  (registry-sync); naming it in the error is a small legibility gain, revisit on the next field hit.

- **A read-only CLI on the server script** (findings_24 §1's alternative shape, declined
  2026-09-06 on the maintainer's words in favour of `entity_export`): `--read '<json>'`
  running a read tool over a lock-free `store.load()` snapshot, for consumers that run
  with NO agent session (CI, a cron). The export tool needs a session to write the
  file; the first field need for a session-less consumer reopens this.

- **An AC born on an already-Implemented slice** (lab beat 13's observation, 2026-09-06):
  no guard objects today. Recorded as a question, not a defect — a closed slice
  legitimately gains ACs through a scope change, so any guard would have to require the
  `SC-` linkage first. Revisit if the field reports one landing without a scope change.

- **`progress_redact`** (findings_21 remedy 3, deferred 2026-08-20 on the
  maintainer's words): a sanctioned, operator-guarded in-place journal rewrite for
  the general secret-pasted-into-the-journal case — the first-ever journal edit,
  doctrinally heavy, and the incident it serves also needs git-history surgery no
  tool alone provides. Revisit on the first field need.

- **Tamper-evidence for the store** (findings_22 §5's second half, deferred
  2026-09-06 on the maintainer's words): a row hash chain, signatures, or an
  external anchor so that a clean `package_verify` is durable evidence rather than
  a citable moment. The report itself states why the audit could not detect a
  determined tamper — a hand edit followed by any tool call is rewritten into
  perfect canonical form with a journal entry naming the row — and git history
  remains the tamper record. Revisit if a governance need for in-store
  tamper-evidence arrives.

- **A whole-rule waiver keeps absorbing new rows** (lab beat 16's observation, 2026-09-21): `WVR-002`
  (no `applies_to`) waived a defect written long after the operator approved it. Documented
  behavior, reported never silent; options if the field asks: an expiry by default, or a nudge
  when a whole-rule waiver absorbs a row newer than itself.

- **From the findings_25 batch, audited and not built** (2026-09-21, one reason each): a patch/append
  mode (**SUPERSEDED by plan 095's `substitute` write, 2026-09-23** — the field ranked it and showed it changed a decision) and an implicit `if_match` on every upsert (a write-contract redesign; `expect_unchanged` is
  the shipped answer); column-fidelity profiling in `package_verify`; flagging stale derived
  artifacts (it would mean rendering the review page on every gate run); `acs-met` respecting
  `Deferred` ACs (**RULED 2026-09-21, maintainer: keep as is** - a deferred criterion still counts;
  postponed work is closed by retiring the criterion through a scope change or by an operator
  waiver, both of which leave a record; do not re-raise); reading `diverged_customized` without an
  emit; a multi-family atomic export (the digest already detects a mixed snapshot); "zero rows
  in the family => indeterminate" for every rule (arguable doctrine; the `population` is visible
  either way); claim-versus-store checks on commit messages and prose (no mechanical subject).

- **Relativize `handoff_emit`'s emitted paths** (post-v4.8.0 review, 2026-09-12, on the
  maintainer's words: document, do not change): `.mcp.json` (standalone installs) and the
  `CLAUDE.md` note carry the resolved server script and package root as absolute paths —
  plan 041's stance, because the executor host must find the server without guessing. The
  cost is that an emitted target is a workspace, not a committable fixture (lab beats quote
  the note in their evidence report instead). Revisit if a field need for a portable emitted
  target arrives; the shape would be paths relative to the target plus a resolver at open.

- **D3 — GitHub Action / pre-commit hook** exposing package validation to end-user repos
  (post-v2: wrap `gate_run`).
- An extension/marketplace registry for community entity types (beyond plan 015's in-repo
  mechanism).
- ~~Retiring the frozen v1 contract (validator + schemas)~~ — DONE in plan 031 (v4.0.0): the
  two-step escape route via tamheed 3.2.1 replaces in-repo v1 ingestion.

*Advisor audit 2026-09-10 — recorded, not planned:*

- **`--dry-run` as a real SAVEPOINT-backed preview** (removed from the docs by plan 048 on the
  maintainer's 2026-09-10 decision): if built, it lives in `entity_upsert` beside plan 043's
  rollback test; the spec wording is in plan 048's diff.
- **A confirm guard on `skills.name` in the CLAUDE.md note** (the `_INJECT_RE` screen half is
  a small fix, unplanned; the guard half relitigates migration 003's "the interview IS the
  approval" — a maintainer question).
- **Raising the `mcp` floor** (PEP 723 `>=1.2`): verify the lowest working SDK version, then
  raise the floor and the seven `pip install` sites together (plan 052 bounds them at `<2` only).
- **Python 3.14 CI leg**: add once `python check.py` passes locally on 3.14 under
  `PYTHONWARNINGS=error::DeprecationWarning` (3.13 was verified that way on 2026-09-10).
- **An opt-in GitHub issues source for adopt mode** (`adopt.md` documented a `sources`
  parameter that never existed; plan 048 removes the claim): the first field need reopens it.
- **Eval rubric ledger + recording one more case per release** (direction finding; 9 cases,
  3 recorded).
- **An `experiments-settled`-style liveness advisory for stages 9–13** (direction finding).
