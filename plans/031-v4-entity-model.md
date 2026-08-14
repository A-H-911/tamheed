# Plan 031 (B27): the v4 entity-model redesign — deep study, re-baselined store, lab-proven

## Status

**DONE (2026-08-14)** — all ten phases complete, `python check.py` fully green
(8 suites incl. the new `test_migrate_v3to4.py` + the `V4EngineTest` battery, 8 lints,
canonical round-trip on the migrated v4 golden, THREE eval cases incl. the new
`lab-tracker` fixture with its 11 deterministic assertions — all green). Released as
**v4.0.0** on the maintainer's words.

**The lab acceptance run (P9) — a real agent, every mechanism fired.** The execution
agent (driving the handlers itself through a tool shim, actor `agent:lab-exec`, ~30
tool calls): registered defects BEFORE fixes with reasoned severities (high/low/low),
applied the flaky-test-is-a-defect doctrine (rewrote the clock test deterministically,
DEF-002 referenced — never deleted silently), recorded evidence-chained verdicts (3
evidenced / 0 narrated), claimed work as `Review` before verification, ran the full
drift lifecycle (SC-001 Proposed → STOP → operator words → Approved → rows applied +
`scope_adds` edges → Merged), had one slice close CLEAN through the guard and the
other REFUSED verbatim ("readiness: SL-002 cannot transition to Implemented —
acs-met: AC-003 …") then forced on operator words with the server's own typed
`forced-override` audit (PE-006), and honored the operator waiver (`defects-minor`
reported `waived` via WVR-001). Final state: `gate_run ready: true`;
`readiness_check(package) ready: false` on the deliberately-open AC-003 — the two
verdicts diverging by design (mechanical integrity vs lifecycle done-ness), which the
agent reported rather than "fixed".

**Lab findings (agent-reported), triaged:** (1) "unknown entity type" errors named no
valid types → FIXED in-release (the error now lists the roster); (2) trace-edge upsert
items return `"id": null` (correct — composite PK — but reads like a failure at a
glance) → recorded, cosmetic; (3) `force` placement (inside the row) is guessable-wrong
though the refusal text hints correctly → recorded, docs already teach it; (4) the
waiver/AC asymmetry (a waiver silences the defect rule, never `acs-met` for the same
underlying issue) → by design, kept: a Not-met AC must cost a deliberate act.

## What this is

The maintainer requested a v4 MAJOR built on a full study of every entity: columns,
relations, purpose, lifecycle position, CRUD semantics, cost of omission — backed by
deep external research, special care on relations + validations, an explicit migration
story, testing beyond test cases (a permanent agent-driven lab), and operator docs with
Mermaid diagrams recording the decisions (how/why/when) and the research sources.

Evidence base: three exhaustive code scans (DB / engine / methodology), three external
research reports (planning-entity practice; execution-entity practice incl. the
claimed-vs-verified consensus across spec-kit/Kiro/Taskmaster/Ralph/OpenSpec; a
dedicated DEC-vs-ADR study), **15 maintainer-locked decisions across five interview
rounds**, and a devil's-advocate round that re-verified every load-bearing sub-agent
claim against source (catching one: `required-artifacts.json` had a second reader —
`check.py:126` — the scan missed; the lint was retargeted, not deleted).

## The 15 locked decisions (full rationale: docs/entities.md)

1. v3→v4 migration = explicit tool + refusal at open (never silent).
2. v1 ingestion retired (two-step escape route via tamheed 3.2.1).
3. Schema re-baselined: schema.sql = the v4 DDL; migration chain reset.
4. DEC-/ADR- kept as two tiers; the one-way-door promotion rule made explicit +
   the `decisions-look-architectural` nag; ADR gains MADR's `confirmation`.
5. Claimed-vs-verified: `Review` state (wbs/slices) + evidence-chained verdicts
   (`verified_by`/`verification_method`/`against_commit`); readiness counts Review open.
6. Lightweight enrichment + liveness gates (never full 29148/PMI column sets).
7. Vocabulary normalized, domain sets kept; lifecycle column name unified
   (⚠ the round-2/3 collision on experiment verdicts resolved by the domain-sets
   principle: experiments/POCs = Validated/Invalidated/Inconclusive/Pending).
8. Milestones demoted to roadmap labels (no lifecycle; gates gate).
9. Gate hardening: severity-thresholded blocking + `WVR-` waivers + Go/Hold/Redirect/
   Kill outcomes.
10. Drift deltas: SC- lifecycle Proposed→Approved→Merged + typed scope_* edges;
    reconciliation checkable, never automatic.
11. Typed progress events + compensating corrections.
12. Deletions: `binds_to`, `entity_types.template_ref`, per-row
    `diagrams.generation_class`, the runtime-dead `schemas/`.
13. `[NEEDS-CLARIFICATION: OQ-NNN]` markers, G-COMPLETE-validated against live OQs.
14. Full relation coverage + the blocking G-REL gate (migrate cleans, adopt reports,
    writes reject).
15. Permanent agent-driven lab (eval-tier) + layered docs + single 4.0.0 release.

## What shipped (by phase)

- **P1** v4 DDL (38 tables, 12 views, 69 triggers, 5 indexes; latest-verdict
  auto-advance — the any-Met-ever trigger flaw finally dead), byte-twin 001, chain
  reset, CANONICAL.md v4 (incl. the findings_16 either-discriminator lock wording).
- **P2** `package_migrate` = staged in-place v3→v4 (preview report → backup →
  legacy-prompt conversion → transform → store-validated write-back); `package_open`
  version refusal; adopt runs the edge sweep; `migrate_v3to4.py` transform module.
- **P3** RELATION_RULES full coverage + G-REL blocking; readiness v4 (thresholds,
  waivers w/ expiry, Review-as-open, 9 new liveness advisories, marker counting);
  typed PE events; evidence-chained audit_record; gate outcomes; G-PROGRESS vacuous
  warning; `ready` gates surfaced; `supersedes` error parametrized.
- **P4** v1 retirement (validator, importer, goldens, mirror; `strip_code` inlined;
  `record.py` extracted for adopt; scratch_diff restored — the one scan miss);
  check.py rewired (Always-class↔catalog lint).
- **P5** catalog rewritten as v4; governance v4 tables; obligations table v3-span
  (template + emitted note, identical); all 14 prompts + README updated (agent-swept,
  spot-verified); ADR/naming/README templates fixed; SKILL/CLAUDE.md swept.
- **P6** viewer: typed journal, SC lifecycle, waivers fold, slice-readiness panel,
  gate outcomes incl. `ready`, G-REL chip.
- **P7** suites rewritten/extended (~150 tests incl. 11 migration + 8 V4Engine);
  golden + both eval fixtures migrated through the REAL tool; canonical gate green.
- **P8** README v4 sweeps (root + server, lint 8 green); `docs/entities.md` (the
  study: per-entity why/when/how, the 15-decision rationale table, Mermaid ER/state/
  lifecycle/sequence diagrams, the research source register) +
  `references/entity-guide.md` (in-bundle operator card).
- **P9** `lab/` (brief with seeded ambiguity/fork/bugs/drift + seed code + scenario);
  planning phases run through the handlers (all 8 gates green with the marker legally
  present); execution phases driven by a REAL agent through a tool shim; the package
  is the `lab-tracker` eval case (11 deterministic assertions pin every mechanism).
  **Honesty limit:** the lab proves mechanisms FIRE under a real agent; autonomous
  drift discharge remains provable only by an interactive fresh session
  (findings_15/16 instrument lesson).

## Verification

`python check.py` green at the P7/P8 boundaries (suites, lints, canonical, evals);
per-phase smoke scripts for P1–P3 (DDL constraints incl. the trigger regression,
migration end-to-end, engine mechanisms); the lab run as the behavioral proof.
Release ceremony: version 4.0.0 everywhere, three-README lint, migration named in
CHANGELOG, **push + GitHub release only on the maintainer's explicit words**, then the
ACMP migration + acceptance prompt (backup → preview → confirm → verify).

## Explicitly not done

- No auto-migration at open; no server-side SC- delta application; no session-identity
  self-certification; no DEC/ADR merge; no Mermaid in review.html (zero-JS);
  the `mcp.server.mcpserver` port stays deferred (pin lint-guarded).
