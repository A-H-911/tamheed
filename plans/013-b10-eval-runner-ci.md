# Plan 013 (B10): Eval runner + the v2 CI pipeline

> **Executor instructions**: Build plan. Deliverables = a stdlib eval-assertion runner, rewritten
> v2 eval cases, the rebuilt CI, and a one-command local check. STOP conditions are binding.
>
> **Drift check (run first)**: plans 008–012 landed (server, migration, adopt, viewer — CI smokes
> them). Missing pieces → implement CI for what exists and mark the remaining smokes as
> commented-out TODO steps referencing the pending plan numbers.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW
- **Depends on**: plans/010, 011, 012 (smoke targets); useful after 008
- **Category**: tests / dx
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Two standing weaknesses converge here. (1) The behavioral eval spec (`evals/evals.json`) has
machine-checkable `deterministic_assertions` that **nothing executes** — CI only lints the spec's
shape (weekly, `eval.yml`), and after the v2 re-architecture the cases assert v1 paths that no
longer exist (adversarial finding W-V2-11). (2) v1's CI gates a world that v2 replaced; the new
mechanical surfaces (DDL, canonical text, server contract, migration fidelity, HTML export,
registry↔DDL sync) need deterministic gates, and contributors need ONE command that reproduces CI
locally — v1 never had that ("passes locally ≠ passes CI").

## Current state

- `evals/evals.json` — 5 cases (incl. the mandatory `injection-brief`); assertions reference
  v1 paths (e.g. `plugins/keystone/scripts/validate_package.py`) and v1 md-package expectations.
- `.github/workflows/eval.yml` — weekly; asserts spec shape + `injection-brief` presence (keep both).
- `.github/workflows/ci.yml` — matrix py3.9–3.12 × ubuntu/windows; runs the v1 suite + 4 golden
  validator runs. v1 goldens STAY (the frozen v1 validator is the migration contract), but the
  Python floor changes per ASM-D (SDK floor, ≥3.10) — drop 3.9 from the matrix and note it in
  CHANGELOG. This CI rebuild applies to the **tamheed repository only** — the old keystone repo's
  CI stays exactly as-is, guarding the frozen 1.0.x line.
- Test suites that exist by now: `test_validate_package.py`, `test_db_roundtrip.py`,
  `test_mcp_contract.py`, `test_migration_golden.py`, `test_adopt_sample.py`,
  `test_export_html.py`.
- Constraint (maintainer decision D-U3): **CI checks themselves are stdlib** — no third-party
  packages in workflow steps beyond what the server itself needs (`mcp` via `uv run` only in the
  server-smoke step).

## Deliverables

1. **`check.py`** (repo root, stdlib): runs, in order, every deterministic gate below and stops
   at first failure with the failing command echoed. CI calls THIS script so local and CI cannot
   drift. Gates: all six test suites → v1 goldens (0/0/1/1) → structure lint (parse every tracked
   `*.json` with `json.load`; verify `entity_types` registry rows ↔ DDL tables sync; verify the
   Always registry ↔ artifact catalog sync while v1 artifacts remain) → canonical-form check
   (load+dump the committed v2 demo package → byte-identical).
2. **Rebuilt `ci.yml`**: matrix per ASM-D floor; job 1 = `python check.py`; job 2 (ubuntu only) =
   server smoke via `uv run plugins/tamheed/server/tamheed_server.py --selftest`; migration
   golden + export smoke are inside the suites `check.py` already runs.
3. **Eval runner** — `evals/run_evals.py` (stdlib): for each case, execute its
   `deterministic_assertions` (each assertion = a command + expected-exit/expected-substring
   contract — normalize the case format so assertions are executable, not prose) against a
   recorded output directory the operator supplies (`--results-dir`); print per-case PASS/FAIL and
   exit non-zero on FAIL. Model-in-the-loop grading stays manual per `evals/README.md` — this
   runner executes only the deterministic half.
4. **Rewritten `evals/evals.json`** for v2: ≥5 cases — minimal brief, rich brief, contradictory
   brief, `injection-brief` (KEEP the id verbatim — eval.yml asserts it), plus the adopt-mode
   injection case added by plan 011; assertions now target v2 surfaces (gate_run verdicts, entity
   counts via `entity_query`, viewer export exists). Update `eval.yml`'s shape-lint if the case
   format gained the executable-assertion fields.
5. **`evals/README.md`** updated: how to run the runner; what stays manual.

## Commands

| Purpose | Command | Expected |
|---|---|---|
| The one command | `python check.py` | exit 0, ordered gate log |
| Eval spec lint | the `eval.yml` inline python | OK |
| Eval runner (self-test) | `python evals/run_evals.py --results-dir evals/sample-results` | exit 0 on the shipped sample |

Ship a tiny `evals/sample-results/` fixture so the runner itself is testable in CI.

## Scope

**In scope**: the five deliverables + `plans/README.md`. **Out of scope**: new eval *content*
beyond the case list above; the GitHub Action for end-users (recorded future option D3);
`eval.yml` schedule/cadence.

## Steps

1. `check.py` wrapping the existing suites + goldens; wire `ci.yml` job 1 to it; matrix floor per
   ASM-D. Verify green locally.
2. Structure-lint + canonical-form gates into `check.py`.
3. Normalize the eval case format (executable assertions); rewrite the 5+ cases; update the
   shape-lint.
4. `run_evals.py` + sample-results fixture.
5. Server-smoke CI job (uv path; job must SKIP gracefully with a visible notice if `uv`
   is unavailable on the runner — do not fail the pipeline on infra).

**Verify** per Commands after each step.

## Done criteria

- [ ] `python check.py` exit 0 and is the ONLY test entry point `ci.yml` job 1 uses
- [ ] Matrix floor matches ASM-D; CHANGELOG notes the floor change
- [ ] `run_evals.py` exit 0 on sample fixture; non-zero on a deliberately broken sample (test it)
- [ ] `injection-brief` case id preserved; eval.yml lint green
- [ ] `plans/README.md` updated

## STOP conditions

- A deterministic assertion in the old cases has no v2 equivalent — record it in the case as
  `"retired": "<why>"` and report; don't silently drop coverage.
- `check.py` and `ci.yml` would diverge (someone asks for a CI-only step) — resist; anything
  deterministic goes into `check.py`.

## Maintenance notes

- Every new plan/feature adds its suite to `check.py`, nowhere else.
- Reviewer scrutiny: the canonical-form gate (it's the guard against W-V2-5 git churn); the
  graceful-skip logic on the uv smoke.
