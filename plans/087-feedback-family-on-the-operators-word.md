# Plan 087: The `feedback` family — upstream feedback and local tools on the operator's word

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [085-090-batch-findings-27.md](085-090-batch-findings-27.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a new family + migration 005; guards on a
  write path; Python + security reviewers) - **Category**: field feedback channel
- **Planned at**: commit `97827e3`

## Why this matters

Measured in ACMP before this plan: four committed slate generators and a shared reader over
`exports/*.json` (compliant, built for LL-011 - the operator refused id-only slates), one JSONL-reading
id resolver (`count-prompt-ids.py`, already flagged non-compliant by ACMP), and a `.scratch/` of probes
over `exports/`. Behind them, four unmet needs nobody told upstream: a writable package header
(`go_no_go` is readable and writable by no tool), id resolution over prompt FILES, a per-field token
census with context, and a patch/substitute write. The maintainer's rulings: a capability tamheed
lacks is recorded IN the package first, on the operator's word; a local tool exists only as an
operator-confirmed register row; `exports/` is the one seam local tooling may read.

## What changed

- **Migration `005_feedback.sql`**: table `feedback` (`FB-`), `kind` in
  `missing-capability | defect | doc-error | question | local-tool`, `lifecycle_status` in
  `Proposed | Confirmed | Reported | Resolved | Rejected`, `workaround` (what was built instead),
  `tool_path` (required for `local-tool` by CHECK), `tool_or_rule`, `plugin_version`,
  `confirmed_by/at`, `resolved_in`, `upstream_ref`; `entity_index` triggers as `003`.
- **Registry**: `ENTITY_TABLES["feedback"]`, `BASELINE_ENTITY_TYPES` row (`Continuous` - never a
  G-SET failure), `_PROSE_ID_EXEMPT_TABLES` (feedback quotes broken ids by nature).
- **Guards in `entity_upsert`** (the lessons pattern): `Proposed -> Confirmed` refused without
  `operator_confirm` (sets `confirmed_at`, requires `confirmed_by`, journals one `transition` row by
  `system:feedback-guard`, returned as `feedback_audit`); a `local-tool` row refused at INSERT without
  `operator_confirm` and born `Confirmed`; leaving `Confirmed`/`Reported` needs the word too; a
  `Proposed` draft may be rejected freely.
- **`handoff_emit`** warns: `N feedback row(s) await the operator (FB-…)` and
  `M confirmed feedback row(s) not yet exported — entity_export("feedback") …`. Ids only; no row
  text enters the emitted files.
- **Teaching**: the note's recording-obligations table gains one row (a function tamheed lacks, or a
  tool you would build -> an `FB-` row FIRST, on the operator's word; local tooling reads `exports/`
  only and writes nowhere tool-owned); SKILL.md, `references/state.md` (a hand-edit at rest is no
  longer called legal), `prompts/README.md` and `orient-resume.md` say the same (history keys `4.11.0`).
- **Migration test** `test_migration_005_feedback_lands`; the 004 test's exact-head assertion relaxed
  to `>= 4`, matching its 003 sibling.

Upgrade path for a field package: `package_open` accepts the store as is (migrations apply at
`connect()` before the load; a missing `feedback.jsonl` is skipped); `package_migrate` reports
`registry-sync` for the one new registry row (pure append, no backup).

## Security review, and what it changed

The first draft's guard was a pairwise `(was, now)` check keyed on the literal `Confirmed` and on
"row absent = insert". The reviewer bypassed it three ways, empirically, on a scratch package: a
`local-tool` kind arriving by UPDATE on a free `question` row; a row born `Reported`/`Resolved`
without the word; and - the sharpest - a Confirmed row's `kind`/`tool_path`/`detail` rewritten in a
later write that merely repeats `Confirmed`, leaving the original `confirmed_by` attached to a tool
the operator never saw. Rewritten around a bound set (`Confirmed`, `Reported`, `Resolved`): entered
from outside only as `Confirmed`, with the word and an attribution; left only with the word; and
while bound, any change to `_FEEDBACK_CONTENT_COLS` (`kind`, `title`, `detail`, `workaround`,
`tool_path`, `tool_or_rule`, `confirmed_by`) is refused without the word - the lesson block's
drift rule. A `local-tool` kind arriving on any row, by insert or update, needs the word.
`Confirmed -> Reported -> Resolved` (bookkeeping of what left and what answered) stays free.
Also from the review: the exemption comment no longer claims feedback is append-only; the handoff
warnings never reach an emitted file (ids only, in the tool result) - stated in the code.
The Python reviewer found the way OUT unjournaled - the very gap plan 086 closed for lessons -
so an operator-confirmed withdrawal now journals its `transition` row too. Both reviewers
verified `cols` is a local copy (no caller-dict mutation) and `changed_columns` reports the
confirmation columns.

**Beat 18's F-3 (fixed before release):** `confirmed_at` was stamped with `setdefault`, a no-op when a
re-sent full row carries the key as null - the ordinary confirmation path. Now stamped whenever empty;
the test confirms a draft re-sent with `confirmed_at: null`. The fixture's `FB-001` keeps its null (the
fixture is what the engine produced at the time).

## Not built (recorded)

Mechanical detection of a tool's USE (tamheed cannot see a `node` process - doctrine and the
handoff warning carry it); a `feedback-unreported` advisory; `FEEDBACK.md` in the target repo;
absorbing slate generation upstream.

## Tests

`test_feedback_and_local_tools_exist_on_the_operators_word` (contract): draft free; unattended
Confirm refused; unattended tool refused and NOT inserted; the two handoff warnings; export total 2;
audit id; leaving Confirmed refused; a draft rejected freely; `server_info(detail)` lists the family;
`DEC-208` in a feedback row trips no rule; the three review bypasses refused; bookkeeping transitions free; a re-confirmed change allowed. `test_migration_005_feedback_lands` (store).

## Done criteria

- [x] contract + migration suites OK (165 / 8)
- [x] Python + security reviewers: one CRITICAL (three bypasses) and one MEDIUM-HIGH (unjournaled withdrawal) found and closed before commit
- [x] `python check.py` -> `ALL CHECKS PASSED` (registry/catalog/DDL sync lints, migration named)
- [ ] CI green

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]` naming `005_feedback.sql` (check.py lint 7);
stock prompt bodies re-set under `4.11.0` in the same commit.
