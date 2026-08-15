# Implementation plans -- the Tamheed program index (through v4.x)

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

Index note: plan 006's file points at `plans/deliverables-review.md` for the approved
artifact set -- that review is the v2 input contract and remains frozen alongside it.

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
  delivery, ADR-0002, this index rewrite.

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

## Future options recorded (not planned)

- **D3 — GitHub Action / pre-commit hook** exposing package validation to end-user repos
  (post-v2: wrap `gate_run`).
- An extension/marketplace registry for community entity types (beyond plan 015's in-repo
  mechanism).
- ~~Retiring the frozen v1 contract (validator + schemas)~~ — DONE in plan 031 (v4.0.0): the
  two-step escape route via tamheed 3.2.1 replaces in-repo v1 ingestion.
