# Plan 032 (B28): the prompt-surface completion — v4 teaching gaps + the diverged-wave root fix

## Status

**DONE (2026-08-14)** — all five phases executed, `python check.py` fully green
(9 suites' worth of coverage: ~100 contract tests incl. the new classification/
refresh/tie-test/needle batteries; 9 lints incl. the new teaching-surface +
stock-history-currency lint; canonical; 3 eval cases), `--selftest` green (the
`refresh_stock` signature registers). Released as **v4.1.0** (MINOR — new tool
capability + a new stock prompt; no schema change, no migration) on the maintainer's
words.

## What this was

The maintainer asked "is there any impact or room for enhancement for prompts?" after
v4.0.0; the verified assessment found one genuine release miss and four enhancements;
the maintainer locked **all five into one 4.1.0** (three interview forks, then the
devil's-advocate template).

## What shipped

1. **The stock-history roster + classification + safe refresh** (the findings_14 root
   fix): `prompts/stock-history.json` — every stock body ever released
   (v3.0.0→v4.1.0, deduped, `{package}` intact, ~78 KB). Diverged stock is classified
   `stale-stock` (byte-equal to an older release after substitution; release named)
   vs `customized`; `handoff_emit(refresh_stock=true)` overwrites ONLY stale-stock,
   before the screens; `force` keeps covering the customized remainder; missing
   history degrades to customized (never a false stale-stock). The v3.2
   "indistinguishable without history" warning now names each class and its path.
   **⚠ Storage format = content, not hashes** (devil's-advocate catch: emitted files
   carry the `{package}` substitution, which hashing cannot cancel; reverse
   substitution would risk silently clobbering customization — recorded in the plan,
   flagged to the maintainer). The sidecar alternative was considered and DECLINED
   (reverses the C20 memoryless-emission doctrine).
2. **`register-liveness.md`** — the amber-list playbook, all THIRTEEN package-scope
   advisories enumerated from `_readiness_report` source (the recalled count was
   nine — the source-enumeration pin earned its keep), with operator STOPs.
3. **Expired-waiver sweeps** in release-close-out + phase-close.
4. **The templates sweep** (the 4.0.0 miss): initial/follow-up/review prompt templates
   teach Review, the evidence chain, markers, the waiver route, SC- deltas — and
   orient via `entity_query`, not v1 file paths (a second latent v1-path miss found
   and fixed in passing).
5. **The teaching-surface lint** (check.py lint 9): engine-vocabulary-only prompts
   (G-* incl. the judgment tier synced against quality-gates.md, event types,
   relations, retired-name blacklist) + stock-history currency. `GATE_NAMES` /
   `PE_EVENT_TYPES` constants tied to reality by contract tests. The lint caught a
   real defect on its FIRST run in-plan: `defect-triage.md` shipped 4.0.0 teaching
   the retired `"status"` column key — the engine rejects that upsert verbatim.

## Execution notes (defects found in-flight)

- **The backfill's first pass stored mojibake**: `subprocess(text=True)` decoded git's
  UTF-8 output as cp1252 — self-consistent under tests but the roster would never
  have matched real field files (fail-safe, feature dead on arrival). Caught by a
  changed-files sanity check, regenerated with explicit UTF-8, and pinned by the
  assertion that untouched prompts match their history verbatim.
- `defect-triage.md` "status" key (above) — fixed + blacklisted.
- Templates still taught v1 orientation paths — fixed in the sweep.

## Verification

check.py green at every phase boundary; the classification/refresh/precedence/
degradation battery; the roster-currency and teaching lints red-tested in-flight
(the judgment-gate roster round-trip); selftest. Acceptance (maintainer): the ACMP
migration lands directly on 4.1.0 — one diverge wave, then
`handoff_emit(refresh_stock=true)` should refresh every never-customised stock file
and leave the three project prompts + any customised stock untouched.
