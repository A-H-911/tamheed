# Plan 025 (B21): Execution hardening

## Status

**DONE (2026-08-08)** — three phases, `check.py` green at every boundary; released as
**v2.7.0** (MINOR — write/read-surface behavior changes + a new store error; no schema
migration). Evidence: the tenth ACMP field report
(`evidence/acmp-field-report-10-2026-08-08.md`) — the FIRST execution-shaped report (a
month of PH-5 work driving the execution loop daily), finding what nine migration runs
structurally could not: four confirmed defects, three silent or actively misleading.
Cluster **C31**. Adversarial review round 9 corrected the draft's omissions PK
(entity_type alone), closed a refused-batch leak (rollback on StoreStaleError), retired
an F6 divergence-storm risk (the operating note is append-once by heading), and hardened
the lock parse for Windows.

## What shipped (per phase, one commit each)

1. **Server surface (C31 A1–A4, C2)** — `_next_id` orders by the parsed NUMBER
   (`MAX(CAST(SUBSTR))`) — the lexicographic sort permanently re-allocated PE-1000 once
   an executed package crossed 999 rows, ending all progress/audit writes forever;
   `entity_query` no longer calls the registered `trace-edge`/`omission` write surfaces
   "unknown" (the false message put a wrong claim in ACMP's permanent record for three
   days) — a write-only message names `entity_upsert`/`trace_query`; an
   `INSERT OR IGNORE` row dropped by a constraint is a per-item ERROR while an
   idempotent duplicate reports `unchanged`, and `applied` counts writes, not attempts;
   `progress-entry`/`audit-verdict` lose the ON CONFLICT path — the append-only journal
   is enforced with a targeted hint (append via `progress_update`/`audit_record`);
   `work_bind` is one transactional unit (failures roll back pending `last_referenced`
   stamps). Five tests, including the report's own 999-row repro shape.
2. **Store (C31 C1, D)** — `PackageStore` fingerprints `data/*.jsonl` at load and
   REFUSES to dump over a tree that moved underneath the session (`StoreStaleError`
   naming the changed files; ~0.02 s/commit at ACMP size); the server surfaces it as a
   loud "batch NOT applied" with the pending transaction rolled back, and
   `package_close` still releases the lock (flush skipped with a warning — a stale tree
   never traps the session; the suite caught the first cut doing exactly that). The
   lock records `{pid, host, taken_at}` JSON; `StoreLockedError` names who/since-when,
   tolerates legacy bare-PID and unreadable content; **no auto-reclaim** (PID reuse —
   the report's dead-writer PID belonged to VS Code). Four tests.
3. **Docs, evidence, release (C31 F6 + nits)** — the working-tree warning ("package
   data is destroyed by `git reset --hard` like any uncommitted change; commit before
   branch operations") in the emitted CLAUDE.md operating note, `references/handoff.md`,
   `references/migration-runbook.md`, and server/README; the viewer's execution section
   states verdict ROWS ≥ criteria (supersessions append — gate_run counts rows, the
   table shows latest-per-criterion); findings_10 archived (C31); plans/README row +
   alignment record; CHANGELOG `[2.7.0]` + plugin.json (version-sync lint); tag v2.7.0.

## Verification

`check.py` green throughout (~198 tests, 10 new). Golden delta N/A (migrate.py
untouched); canonical round-trip unaffected (fingerprinting is read-only).
**Acceptance MET (findings_11, evidence C32)**: all four §A defects verified FIXED by
running the tools (A1 with a text-order control; A2 both spellings; A3
rejected-vs-unchanged; A4 append-only hint), C1 exercised deliberately (file named, disk
preserved, close never traps), D verified across a real process boundary, F6's manual
line added on the ACMP side. C2 source-confirmed in the report; unit-verified in-repo.
Second zero-actionable-findings report — no plan 026 followed. The §C MCP-reconnect note
is harness-side (byte-identical launcher, clean selftest), not a plugin fault.

## Rejected / recorded-not-planned

- §B (silent write loss) — the operator's own `git reset`; tamheed was correct at every
  step; addressed by F6 docs + the C1 guard for the inverse direction.
- Auto-reclaiming "dead"-PID locks — PID reuse makes liveness unsound; metadata + a
  loud message instead.
- `supersedes` column for journal corrections — schema migration for a practice
  (append a retraction) that already works; revisit only if the field asks.
- Optimizing `dump()`'s full rewrite — §E explicitly asks it NOT be optimized on
  suspicion (0.021 s measured).
- Timestamped-sibling dump on stale close — refuse-and-guide is sufficient; a second
  escape hatch invites divergence.
