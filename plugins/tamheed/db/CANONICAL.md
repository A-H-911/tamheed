# Canonical serialization — Tamheed v2 package data

The canonical form of a package's data is **one JSONL file per table** under the package's
`data/` directory, committed to git. SQLite is only the runtime (`store.py` loads text in,
enforces integrity, writes normalized text back after every mutation). This spec exists so git
diffs are minimal and merges are row-scoped (finding W-V2-5). `store.py` is the reference
implementation; on any disagreement, `store.py`'s output is canonical.

## File layout

- `data/<table>.jsonl` — exactly one file per **non-empty** table; a table with zero rows has
  **no file** (a stale file for a now-empty table is deleted on write-back).
- `entity_index` is derived (trigger-maintained) and is **never serialized**.
- File names are the table names from `schema.sql`, verbatim.

## Determinism rules

1. **Encoding:** UTF-8, no BOM. Line endings: **LF only**. The file ends with a trailing LF.
2. **One row per line:** a single JSON object, no pretty-printing.
3. **Key order:** the column order declared in `schema.sql` (`PRAGMA table_info` order) — never
   alphabetical, never insertion-dependent.
4. **All columns present:** SQL `NULL` serializes as JSON `null`; no key omission.
5. **Row order:** ascending by primary key, byte-lexicographic (SQLite BINARY collation).
   Composite keys (e.g. `trace_edges`) compare column by column in declared key order.
6. **Strings:** JSON with `ensure_ascii=False` (raw UTF-8), compact separators `","` / `":"`.
7. **Numbers:** integers only in schema-typed INTEGER columns; REAL columns are avoided by
   design — if one is ever added, its values serialize per Python `json` repr.

## Write-back

Every mutation cycle ends with a full rewrite of the affected table files from SQLite state
(normalize-on-write). Hand-edits to `data/*.jsonl` are legal *at rest* (that is the point of
text-canonical storage) but are validated on next load: unknown keys, FK violations, CHECK
violations, and bad JSON fail loud — nothing is silently repaired.

## Single-writer rule

One loader/writer per package, guarded by a lockfile:

- `data/.lock` is created with `O_CREAT | O_EXCL` on open-for-write; it contains the writer's
  PID for diagnostics.
- If `data/.lock` already exists, opening the store **fails loud** (`StoreLockedError`) — no
  waiting, no stealing. A crashed writer's stale lock is removed by the operator, deliberately.
- The lock is released (file removed) when the store closes, including on error exit.

## Byte-stability guarantee (field-proven, plan 019)

An idle `package_open` → `package_close` round-trip on a committed store produces **zero
git diff** — canonical text is byte-stable across open/close cycles (LF, no BOM, PK-ordered,
minimal separators, load+dump idempotent; `check.py`'s canonical gate enforces it on the
demo golden every run). Operators can and should lean on this: **"did anything change?" is a
`git status` question.** Verified in production during the ACMP migration (evidence C20).
