# Plan 017 (B13): Field-report hardening — core gates, shared pipeline, v1 dialect tolerance

## Status

**DONE (2026-07-21)** — all six phases executed and committed with `check.py` green at every
boundary; released as **v2.1.0**. One deviation, better than planned: the catch-all narrative
uses the existing `doc_kind='other'` enum value (no DDL, no registry change needed). The
golden-regeneration review found and repaired pre-existing B4-class loss in the committed
golden itself (AC titles were literally "PH-1"). **Outstanding: the manual ACMP acceptance
run** (maintainer, needs the ACMP repo — see Done criteria).
Decisions locked at the 2026-07-21 approval checkpoint (were honored in execution):

- **D-017-1** Vacuous G-TRACE is reported as a **warning only** — `ready` semantics unchanged
  (adopt-mode packages are all-`mvp=0` by design and must keep working).
- **D-017-2** **One plan, phase gates**: all six phases in this plan; `python check.py` fully
  green at every phase boundary; one release (v2.1.0) at the end.
- **D-017-3** **Unified versioning**: `plugin.json` tracks the product version (2.1.0 at this
  release), enforced by a new `check.py` lint item.
- **D-017-4** The v2 content scan reuses the frozen validator's `strip_code` semantics — no
  second placeholder-scan implementation is ever written.

All line numbers below refer to the `v2.0.0` tree.

## Why this matters

The first real-world v1→v2 migration (ACMP: 218 requirements, 74 ACs, 33 ADRs, 1,032 trace
edges; v1-validator 7/7 green) **could not succeed vanilla**: a Windows subprocess deadlock
(A1), a whole-populate FK crash (A2), and silent data loss across five register families
(B1–B6) had to be worked around outside the MCP transport. Worse, two gates went **falsely
green** (C1 vacuous G-TRACE, C2 placeholder false-positives) — the system converted data loss
into confidence. Root-cause analysis (this plan's payload) shows most findings are **not
migration bugs**: they live in `gate_run`, `entity_upsert`, `PACKAGE_ROOT` resolution, the
shared `populate` pipeline, and `adopt.py` — every entry path is affected. ACMP is one of the
three C10 validation-corpus repos (plan 010); this report is that corpus doing its designed job.

## Evidence (C11–C16, continuing the C-series)

Source: the ACMP field report (`findings.md` in the ACMP repo, ACMP PR #151; archived into
`plans/evidence/acmp-field-report-2026-07-21.md` by Phase 5). Cite these ids in code comments.

| Id | Cluster | Report items |
|----|---------|--------------|
| C11 | Transport/environment: subprocess-from-server, cwd-relative roots, poison dirs | A1, A3, D3 |
| C12 | v1 dialect tolerance: same-author drift breaks allowlist parsing | B1, B4, B5, B6, A2, D4 |
| C13 | Loss visibility: id-granular accounting hides file/family-level loss | B2, B3, B6, C3 |
| C14 | Gate integrity: vacuous pass + false positive; provenance graded as authorship | C1, C2 |
| C15 | Cutover routing: migration moves the source of truth, pointers to it go stale | (AGENTS/CLAUDE gap) |
| C16 | Version skew: plugin manifest not bumped at v2.0.0 (installs self-identify as 1.0.0) | (env line of report) |

## Root causes (fix the class, not the instance)

1. **RC1 — allowlist parsing with silent fall-through** (aliases `migrate.py:170`,
   `NARRATIVE_KINDS:40`, `OMISSION_KEYWORDS:30`, adopt's config branches `adopt.py:104-125`).
2. **RC2 — loss accounting is id-granular only**; whole files and whole families vanish with no
   line item (`plan.unmapped` design).
3. **RC3 — the operator confirms on less information than the tool has** (deltas post-populate
   only, `migrate.py:556`; bare IntegrityError from the insert loop, `migrate.py:512-536`).
4. **RC4 — environment assumptions**: children inherit the MCP stdio transport; `PACKAGE_ROOT =
   Path(".")` (`tamheed_server.py:31`) resolves all fourteen tools against an unguaranteed cwd
   (Claude Code docs: cwd not guaranteed; `CLAUDE_PROJECT_DIR` is expanded in plugin `.mcp.json`
   args **and** exported to the server's environment).

## Deliverables

1. **Phase 1 — Core & blockers** (`tamheed_server.py`, `migrate.py`, `adopt.py`, `store.py`).
2. **Phase 2 — Migrate fidelity** (`migrate.py` + `references/migration-v1.md` in lockstep).
3. **Phase 3 — Adopt fidelity** (`adopt.py` + `references/adopt.md`).
4. **Phase 4 — Golden regeneration** (one dedicated commit; three consuming surfaces).
5. **Phase 5 — Docs & evidence archive** (`docs/`, `plans/evidence/`, references, SECURITY.md).
6. **Phase 6 — Release engineering** (plugin.json 2.1.0, version-sync lint, CHANGELOG, tag).

## Commands you will need

```bash
python check.py                                   # full gate; green at EVERY phase boundary
python check.py suites                            # fast loop while editing
python plugins/tamheed/scripts/validate_package.py tests/fixtures/dialect-package   # must exit 0
uv run plugins/tamheed/server/tamheed_server.py --selftest
```

## Scope

**IN:** everything under Deliverables. Zero DDL — every fix is code-level so existing 2.x
packages upgrade with no migration.

**OUT (considered and rejected — do not re-audit):**
- **Slice synthesis from roadmap prose** — v1 had no governed slice concept; inventing rows is
  guesswork. The catch-all narrative preserves the text; manual backfill is documented (B2).
- **`entity_patch` tool / fetch-and-merge upsert** — interacts with immutability triggers and
  batch savepoints; the observed need is met by a docstring + clearer error (D2).
- **Property-based fuzzing, coverage thresholds, test frameworks** — the stdlib seeded-fixture
  pattern extends instead.
- **Auto-editing target-repo agent-control files** beyond `handoff_emit`'s existing append —
  D-REPO-5 (operator-initiated, never forced) governs.
- **Windows deadlock root-cause confirmation** — stdin-inheritance is a plausible hypothesis;
  the fix removes the subprocess, making the question moot for migrate and defended-against
  for adopt.

## Steps

### Phase 1 — Core & blockers (C11, C14, A2-reporting)

1. **In-process preflight** (`migrate.py:142-159`): replace `subprocess.run` with
   `vp.run_gates(source)` + `vp.build_summary(...)` (`validate_package.py:1027/1034` —
   `{"ok": not critical_failures, ...}` is a superset of what preflight parses today). Wrap in
   `try/except`: the subprocess previously isolated validator crashes; surface a distinct
   "preflight crashed" error with traceback. The frozen validator is *called*, never edited.
2. **Spawn policy**: adopt's git call (`adopt.py:192`) gains `stdin=subprocess.DEVNULL`
   (children must never inherit the MCP stdio transport); timeout already present.
3. **`promoted_to` filter** (`migrate.py:207`): accept only `ADR-*` tokens; anything else →
   `NULL` + an `unmapped` note (kills the whole-populate FK crash for this column).
4. **Per-row populate error context** (`migrate.py:512-536`): report `table / row id /
   constraint` before re-raising — mirror `entity_upsert`'s per-item verdict pattern
   (`tamheed_server.py:258-266`). Atomicity unchanged.
5. **Poison-dir cleanup**: a failed populate removes the `data/` dir it created
   (`store.py:135` mkdirs on `__enter__`; `migrate.py:493-495` then refuses retries).
6. **Root resolution** (RC4): bundled `.mcp.json` args use `${CLAUDE_PROJECT_DIR}` (NOT
   `${CLAUDE_PLUGIN_ROOT}` — packages belong in the project); in code, resolution is layered:
   explicit `--package-dir` > `CLAUDE_PROJECT_DIR` env > cwd. Every
   `package_create/open/migrate/adopt` result echoes the resolved **absolute** root. New
   `server_info` tool: plugin version (read from bundled `plugin.json` — single source),
   resolved root, migration head.
7. **Vacuous-G-TRACE warning** (D-017-1): `gate_run` adds a prominent warning when
   `requirements` has zero `mvp=1` rows; `ready` unchanged.
8. **G-COMPLETE parity with the frozen contract** (D-017-4): the v2 placeholder scan
   (`tamheed_server.py:344-354`) exempts `custom_attributes` (provenance, not authored
   content — the `_INJECT_RE` untrusted-content screen still applies) and applies
   `vp.strip_code` before matching (the frozen validator already does: `validate_package.py:714`).
9. **`entity_upsert` docstring + error**: partial rows fail NOT NULL on the INSERT half before
   conflict resolution (`tamheed_server.py:253-257`) — document "send full rows"; error message
   names the cause.

**Validate:** all existing suites green; a new unit test per item; `check.py` green.

### Phase 2 — Migrate fidelity (C12, C13) — every parser change amends `references/migration-v1.md` in the same commit

10. **ADR fallback parser** (`migrate.py:287-299`): when front-matter has no id, parse the
    MADR shape Keystone itself emitted — id from `^# (ADR-\d+)` heading, status from a
    `- Status:` bullet. Fix the section trap: prefer "decision outcome", exclude "drivers" (D4).
11. **AC aliases** (`migrate.py:170-173, 247-253`): add `given / when / then` and `criterion`;
    `statement` takes the raw cell (never the `_clean_line` 120-char cap); `title` stays capped.
12. **Audit aliases** (`migrate.py:367-374, 521-525`): accept `test ref` as evidence; carry the
    remaining audit columns in `custom_attributes` (column exists — `schema.sql:431`).
13. **B6 batch**: raw profile preserved in `custom_attributes`; accept `generated` alongside
    `generated_at`; add `research` to `OMISSION_KEYWORDS`; suppress an omission when the same
    family also migrated rows.
14. **MoSCoW mapping**: `M`/`Must` in Priority/Scope → `mvp=1` (belt to Phase 1's suspenders).
15. **Catch-all narrative** (RC1 class fix): unmatched `.md` files migrate as
    `doc_kind="uncategorized"` narrative documents. Rules: applies only to files that produced
    **zero rows**; `SKIP_FILES` still skipped; row-bearing files are listed in the preview as
    "tables migrated; surrounding prose not". Register the new doc_kind via
    `references/extension.md`. **Depends on Phase 1 item 8** (the scan-surface expansion is
    only safe once `strip_code` parity has landed).
16. **Deferred-work rows**: recognize `execution/deferred-work-register.md`; map `| D-nn |`
    rows to `DW-` ids in `deferred_work` (table already in `INSERT_ORDER:479-483`; nothing
    feeds it today).
17. **Family-zero tripwire** (RC2): manifest count > 0 but parsed count == 0 → populate refuses
    unless the family is named in a new `allow_zero: [...]` parameter; preview lists
    `zero_families`.
18. **Preview parity** (RC3): compute count deltas (reuse `fidelity()`'s code,
    `migrate.py:556-564`) and a "files not migrated" section **in the preview** — the stage-3
    confirm happens on full information.
19. **Patch hook** (D1): `package_migrate(..., patch=<file>)` — merge-by-id row overrides
    applied to the parsed plan **pre-populate only**, echoed in the preview. Post-hoc mutation
    stays impossible; documented in `migration-v1.md` as the official repair path.
20. **Migrate/adopt results end with the cutover pointer** (C15): "next: run `handoff_emit`" —
    the mechanism already exists (`tamheed_server.py:472-497` writes `.mcp.json` + appends the
    CLAUDE.md tracking note); this closes the routing gap, building nothing new.

**Validate:** dialect-fixture assertions (Phase 4's fixture, built in parallel) + the
conservation meta-test.

### Phase 3 — Adopt fidelity (RC1/RC2 in adopt)

21. `Cargo.toml`: parse `[dependencies]` into DEP rows, or remove it from the scan allowlist —
    never scanned-but-silently-unparsed (`adopt.py:55` vs `104-125`).
22. Report every hit cap in the gap report (`[:1]` README, `[:20]` FRs, `[:40]` test files,
    `[:200]` code files, `[:30]` deps) — "no silent caps".
23. `handoff_emit`'s CLAUDE.md note gains one line flagging stale v1 workflow references
    (mention of `validate_package.py`/`docs/` registers) when detected in the existing file.

### Phase 4 — Tests + golden regeneration

24. **Dialect fixture** `tests/fixtures/dialect-package/`: a v1 package that is
    **v1-validator-green by construction** (ACMP proves the combination exists) while seeding
    every C12 quirk: MADR ADRs without front-matter, GWT AC column with >120-char statements,
    "Test ref" audit column, MoSCoW priorities, `D-nn` register, `generated` manifest key,
    parenthetical profile, roadmap prose, `{{…}}` and a code-span `TODO` inside narrative
    files, promoted-to cell mixing DEC/ADR tokens. Register in `check.py` `SUITES` (new
    `tests/test_migration_dialect.py`) **and** as a fifth `V1_GOLDENS` entry (expected exit 0).
    One assertion per seeded quirk: preserved by the right mapping.
25. **Conservation meta-test**: every source `.md` either produced rows/narrative or appears in
    files-not-migrated — catches the *next* unknown fall-through.
26. **Gate falsifiability tests, both directions**: zero-`mvp` warning present; `{{…}}` in
    `custom_attributes`/code spans passes; genuine `<placeholder>` in a title fails; the
    "requirement legitimately containing `TODO` in a code span" case passes.
27. **Failure-path tests**: seeded FK violation → error names table+id; retry after failed
    populate succeeds (no poison dir); both via migrate *and* adopt (shared pipeline).
    Read-only-source byte-digest assertion extended to adopt.
28. **Spawn-policy test**: monkeypatch `subprocess.run` to raise → preflight still completes
    (proves in-process).
29. **Golden regeneration (dedicated commit):** write the expected-delta list *first* (new
    DOC/SEC rows from catch-all, alias-widened fields), regenerate
    `generated-samples/support-triage-agent-v2`, review the diff against the list, and land
    with all three consuming surfaces green: `test_migration_golden.py` digests/counts,
    `check.py gate_canonical` byte round-trip, `test_export_html.py` render fixture.

### Phase 5 — Docs & evidence

30. Archive the ACMP report verbatim (with a provenance header) as
    `plans/evidence/acmp-field-report-2026-07-21.md`; add a 2026-07-21 alignment-record entry
    to `plans/README.md`.
31. `docs/migrate-from-keystone.md`: a "Cutover" section — `handoff_emit` is the cutover step;
    the operator updates AGENTS.md/CLAUDE.md pointers and freezes the v1 `docs/` tree; the
    two-sources-of-truth window is named explicitly.
32. `SECURITY.md`: one paragraph — the `custom_attributes` gate exemption is *grading* relief
    only; the untrusted-content screen still applies to provenance fields.
33. Reference updates not already shipped with their code: `references/quality-gates.md`
    (warning semantics, strip_code parity), `references/adopt.md` (cap reporting under rule 3).
34. One eval scenario (`evals/`): migrate the dialect package end-to-end; assert the cutover
    pointer appears in the result.

### Phase 6 — Release engineering (C16)

35. `plugin.json` version → `2.1.0` (fixes the live 1.0.0 skew; D-017-3).
36. `check.py gate_lint` item 4: `plugin.json` version == newest `CHANGELOG.md` release
    heading (stdlib, per D-U3).
37. `CHANGELOG.md` `[2.1.0]`: no schema migration — existing packages unaffected; the two
    gate-behavior relaxations (G-COMPLETE strip_code/provenance exemption, vacuous-G-TRACE
    warning) listed explicitly; MINOR per `references/extension.md`.
38. Tag `v2.1.0`.

## Done criteria

- `python check.py` fully green, including the dialect suite, the fifth golden, and the
  version-sync lint item.
- Every C12 quirk has a passing preservation assertion; conservation meta-test green.
- **Manual acceptance (maintainer, requires the ACMP repo):** vanilla re-migration of ACMP
  through the real MCP transport on Windows into a **scratch destination** — zero out-of-band
  workarounds, `ready: true` with a *non-vacuous* G-TRACE and evidenced audit verdicts; diff
  against the existing hand-repaired `tamheed-package/` shows only the hand-fixes' provenance.
- `plugin.json` == CHANGELOG heading == git tag `v2.1.0`.

## STOP conditions

- Any fix requires editing a frozen v1 surface (`validate_package.py`, JSON schemas,
  templates, the v1 demo) — stop; the validator is called as a library only.
- Any item turns out to need DDL or a migration file — stop (this plan is zero-DDL by design).
- A golden diff in Phase 4 not on the expected-delta list — stop; do not regenerate around it.
- Any gate-semantics change beyond the two approved relaxations — stop.
- `CLAUDE_PROJECT_DIR` behavior contradicts the documented contract at runtime — ship the
  echo-only part of item 6 and stop for a maintainer decision.

## Maintenance notes

- Migrations (if ever added later) stay idempotent — `store.py` applies `002+` on every connect.
- Future field reports: archive under `plans/evidence/`, continue the C-series, fold in via a
  dated alignment-record entry — this plan is the template.
- ACMP's own AGENTS.md/CLAUDE.md cutover is **ACMP-repo work**, out of scope here (tracked for
  the maintainer in the plan-017 review conversation).
