# Plan 027 (B23): v3.0.0 — prompts leave the DB, readiness engine, typed relations, flow viewer

## Status

**DONE (2026-08-13)** — eight phases, `check.py` green at every boundary (~210 tests);
released as **v3.0.0** (MAJOR — the prompts table is dropped and the handoff contract
changes; migrations `003_drop_prompts.sql` + `004_readiness_views.sql`, both append-only,
tracked via the new `PRAGMA user_version` mechanism). Evidence: **seven direct maintainer
observations** after sustained ACMP usage — no findings file this cycle; every claim was
verified against source by three exploration passes before planning, the plan survived a
maintainer-requested devil's-advocate round (all sub-agent claims re-checked by direct
read) and two interview rounds. The full decision record (19 adversarial-review entries)
lives in the approved plan file; the load-bearing outcomes are below.

## What shipped (by maintainer note)

1. **Prompts out of the database** (note 1): migration 003 drops the table; prompts are
   `.md` files in `<package>/prompts/` — the operator reads the folder and picks.
   `package_open` converts a legacy `data/prompts.jsonl` ONCE (abort-on-anomaly, source
   renamed `.converted`, PRM- edges + registry/omission rows scrubbed, full report);
   `handoff_emit` becomes pure target wiring (no copies, `subdir` refused, G-INJECT and
   the C24/D-8 stale scan relocated to the package prompt files, ≥1 project-authored
   prompt required); `package_create` seeds the folder from birth; `migrate` lands v1
   prompt files verbatim with a deterministic provenance header (no timestamp — golden
   byte-reproducibility). Goldens + eval sample regenerated to the end state.
2. **Prompt library 5 → 14** (note 2): slice-kickoff, defect-triage, drift-register,
   replan-deferred, release-close-out, phase-close, package-onboarding (semi-auto) +
   loop-iteration/loop-guard (fully-auto, machine-parseable `ITERATION:` contract for
   both loop drivers — maintainer: "both/undecided").
3. **Drift enforcement on always-loaded surfaces** (note 3): the emitted CLAUDE.md note
   is marker-managed (`tamheed:note v2`) with a mandatory 7-row Recording-obligations
   table; the three Stage-20 templates drop v1 markdown-file instructions for the MCP
   tools; agent-control carries the identical table (drift between the two texts stays
   grep-detectable). v1 notes are warned, never machine-edited (no terminator).
4. **Typed relations** (note 4): `RELATION_RULES` hard-rejects mistyped edges on new
   writes (`relates_to` = untyped escape hatch; `binds_to` unpinned — zero documented
   usage); `gate_run`'s three referential gates VERIFY at gate time (the hardcoded
   "enforced at write time" pass literals are gone; whitespace-only provenance caught);
   advisory `relation_rules` sweep lists legacy mistypes (the golden's 2 PH- edges are
   its living test data — never "fix" them).
5. **Flow viewer + graph rework** (note 5, "both"): layered `#flow` section (labeled
   clickable nodes, arrowheads, CSS-only relation filters, zero JS) + connected-only
   circular overview (74% of the golden's nodes were isolated dots — now their own
   fold; degree-scaled radii; 12 hues + ring). Two stale five-section tests fixed to
   iterate SECTIONS.
6. **Test/infra enrichment** (note 6): `PRAGMA user_version` (Python-stamped; byte-twin
   lint untouched) + `tests/test_store_migrations.py`; three new lints (CHANGELOG
   newest-first, the `mcp<2` pin guarded, every migration named in the CHANGELOG); the
   first execution-phase eval case (`execution-loop`, recorded via the real handlers).
7. **Devil's-advocate discipline** (note 7): a verbatim adversarial round before
   approval re-verified every sub-agent claim by direct read and found a **new latent
   defect**: `export_html`'s latest-verdict used string `ORDER BY av.id DESC` — wrong
   past 1000 verdict rows post-025. Fixed via migration 004's numerically-ordered
   `v_latest_verdicts` (which also killed `v_phase_exit`'s any-Met-ever flaw).
8. **Readiness engine** (note 8, added at review): `readiness_check(scope, id?)` —
   blocking rules (pre-approval decisions/ADRs, ACs not latest-Met, open defects,
   undischarged risks — the last upgraded to blocking at interview round 2), advisory
   rules, `human_required` from declared `execution_gates` (prose never
   machine-evaluated). **The transition guard** (maintainer decision): phase/slice →
   `Implemented` is refused while blocking rules fail; item-level `"force": true` after
   the operator's explicit words proceeds AND the server appends the FORCED `PE-` audit
   row itself. Transition-edge detection (full-row re-upserts never re-fire);
   `wbs-item` writes and `package_close` exempt (session-trap avoidance, C31).
   export_html gained the per-phase readiness panel + human-gates fold.

## Verification

`check.py` green after every phase (suites, v1 goldens, 7 lints, canonical round-trip,
2 recorded eval fixtures). Live probes during execution: fresh migration → golden
byte-identity; converter on the eval sample; the execution-loop fixture built through
the real server handlers with gates ready. **Acceptance (maintainer): the next ACMP run
on 3.0.0** — the open-time conversion of the live package succeeds loudly, the flow
view answers real coverage questions, an execution session records defects/scope
changes unprompted, and `readiness_check` surfaces the true blockers at a close.

## Deferred / rejected (recorded, do not re-audit)

- `mcp.server.mcpserver` port — still deferred from plan 026; the pin never widens
  without it (now lint-guarded).
- Auto-upgrading v1 CLAUDE.md notes; server-side git-vs-work_bind checks; a
  weekly-health prompt; computed-HSL palette; per-relation arrowhead colors
  (`context-stroke` unportable); continuous gate-time G-INJECT file scanning; keeping
  the prompts table as a deprecated read surface; making readiness a G-* gate
  (scope-parameterized checks must not change `ready`'s meaning).
