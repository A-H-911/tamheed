# Plan 037 (B33): findings_20 — the honest registry-sync report — v4.4.1

## Status

**DONE (2026-08-16)** — `python check.py` fully green, `--selftest` green. Version
stamped **v4.4.1** (PATCH — a false statement in tool output; no behaviour change
to the sync itself). *Release only on the maintainer's explicit words.*

## What this was

findings_20 (evidence **C41**) — the v4.4.0 acceptance, one finding: the
registry-sync note asserted "only the entity-type registry changes — pure append"
per-mode, while migration 003's new column re-serialized the populated
lessons.jsonl per-release — the operator's git diff contradicted the banner and
cost a hand-verification cycle. The report's forward-looking half: every future
registry-sync fronts the same static wording. Maintainer-locked: 4.4.1 PATCH,
enumerate + reword composed.

## What shipped

- **`columns_added`** in the sync report (both stages): per-table columns present
  in the live DDL but absent from the stored rows — the exact mechanical cause of
  re-serialization, named BEFORE the operator sees the diff. Sound because
  canonical JSONL serializes every column (CANONICAL.md rule 4 + store.py's dump,
  DA-verified at both levels; the field report's own observed `promoted_to: null`
  diff is the independent proof). Orphan files of dropped families skipped; the
  key omitted when empty.
- **The note reworded, computed per-run**: "registry rows + the audit journal row
  appended; no data transform, no backup taken" + the re-serialize clause only
  when columns_added is (the DA honesty upgrade: the old note was also silent
  about the system:migrate PE row modifying progress_entries.jsonl).
- The six "pure append" teaching surfaces swept; one new contract test (a
  stripped-column fixture → both report keys; the sibling no-lessons fixture
  proves the key's absence).
- C41 records the report's own model acceptance shape: two 4.4.0 fixes verified
  BY REPRODUCTION, §3 honestly left field-unverified, and the promotion ceremony
  run-and-DECLINED recorded as the prompt working.

## Verification

check.py green (110 contract tests; all lints — the roster lint confirms no
scenario prompt bodies changed); `--selftest`.
