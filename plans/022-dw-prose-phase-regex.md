# Plan 022 (B18): DW prose carry, phase-regex fix, derived-artifact papercuts

## Status

**DONE (2026-07-23)** — three phases, `check.py` green at every boundary; released as
**v2.5.1** (PATCH — pure fixes + a runbook section, no new surfaces). Evidence: the sixth
ACMP field report (`evidence/acmp-field-report-6-2026-07-23.md`) — the first **empty
UNEXPECTED bucket**: the scratch-diff regression method proved every 2.5.0 fix byte-exact
on real data (epic titles, escaped pipes, DW enum carry, B4's un-suppressed scan with 46
marked findings). Cluster **C27**. This report is also plan 021's acceptance evidence.

Adversarial review round 6 refinements (pre-approval): prose prefix-carries emit a
visibility note (never the one silent judgment call in the DW mapping — honesty symmetry);
`\bStatus\b` word-boundary guard (unanchored, `ExitStatus:` would have matched); `In
progress` in the exact map, not the prefix regex. The sharpest finding was B2: the 020
phase prose-status regex **fired zero times on the very fixture that motivated it**
(line-anchored while ACMP's status sentences end `- **Exit gate.** …` bullets;
parenthetical qualifiers outside the capture class).

## What shipped (per phase, one commit each)

1. **Migrate fixes (C27/B1/B2)** — deferred-work status cells that fail exact enum
   matching carry the enum word as a PREFIX after leading punctuation/emoji
   (`**✅ Done <date> (<slice>)** — narrative` → `Done`, noted per carry); `In progress`
   → `Activated` (exact map); the phase `Status:` matcher unanchored with a `\b` guard
   and `(` joining the capture terminators (`Status: complete (delivered …)` →
   `complete`). Quirk 20 in migration-v1.md; 2 tests; golden delta empty (fixture carry
   target 23/23; PH-0/PH-1 move to the VANISHED bucket on the next measurement).
2. **Derived-artifact papercuts (C27/D1/D2)** — a PRM body opening with its own H1
   identical to the title is stripped at emit time (a DIFFERENT in-body H1 is preserved);
   `export_html` CSVs emit `force=True` — derived outputs like `review.html` itself,
   never operator files (a diverged CSV was unrecoverable in-tool); authored emissions
   keep the refusal path. Doc lines in `references/handoff.md` + server/README; 2 tests.
3. **Docs, evidence, release** — runbook **§8** (the scratch-diff regression measurement:
   scratch-migrate → field-level diff vs live → VANISHED/REMAINED/UNEXPECTED buckets,
   empty UNEXPECTED = pass, delete the scratch) + docs mirror; findings_6 archived (C27);
   plans/README row + alignment record; CHANGELOG `[2.5.1]` + plugin.json (version-sync
   lint); tag v2.5.1.

## Verification

`check.py` green throughout (~176 tests, 4 new). Golden delta script empty after Phase 1
(STOP rule satisfied without regen). **Acceptance (maintainer): the §8 measurement on the
next upgrade** — DW carry 23/23, PH-0/PH-1 in the VANISHED bucket, no doubled H1s, no
stuck CSVs.

## Rejected / recorded-not-planned

- D3 (graph node-count): no doc claims a number; `entity_index` IS the graph's honest
  domain (1,686 on ACMP; the "~2,400" estimate counted non-indexed rows).
- Warn-instead-of-strip for D1 (strip-if-identical is deterministic and safe).
- Broader DW fuzzy matching beyond prefix-after-punctuation (prefix + `In progress`
  reaches 23/23 on the only real fixture; more is speculation).
