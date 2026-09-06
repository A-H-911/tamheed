# Canonical serialization — Tamheed v4 package data

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
- Nothing else lives in `data/` but the lock (`.lock`, transient). Audit-trail copies of
  converted or migrated sources live in `data-v3-backup/` — the v3 prompt converter used to
  leave a `prompts.jsonl.converted` beside the canonical files (findings_22 §4: the one object
  the engine did not own, weakening "`git status` on `data/` is the integrity question");
  since v4.5 it never does, and `package_migrate` relocates an old one (staged, per file).
  `package_verify` reports any remaining foreign file by name.

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

- `data/.lock` is created with `O_CREAT | O_EXCL` on open-for-write; it contains a JSON
  object `{pid, host, taken_at}` for diagnostics (legacy bare-integer locks are tolerated
  when read).
- If `data/.lock` already exists, opening the store **fails loud** (`StoreLockedError`) — no
  waiting, no stealing. A crashed writer's stale lock is removed by the operator, deliberately
  (delete it when EITHER staleness discriminator proves the holder cannot be live: the pid is
  not a plausible agent session, or the process started after `taken_at`).
- The lock is released (file removed) when the store closes, including on error exit.

## Byte-stability guarantee (field-proven, plan 019)

An idle `package_open` → `package_close` round-trip on a committed store produces **zero
git diff** — canonical text is byte-stable across open/close cycles (LF, no BOM, PK-ordered,
minimal separators, load+dump idempotent; `check.py`'s canonical gate enforces it on the
demo golden every run). Operators can and should lean on this: **"did anything change?" is a
`git status` question.** Verified in production during the ACMP migration (evidence C20), and
again by the operator-commissioned integrity audit of 2026-09-06 (evidence C43): `load()` →
`dump()` reproduced all 29 register files byte-identically — 40 tables, 7,819 rows — after a
deliberate attempt to falsify it.

## Verifying on demand — `package_verify` (v4.5)

The guarantee above used to be a property you had to know to exercise. `package_verify(name?,
record?)` exercises it and reports:

- **`dirty`** — every canonical file whose committed bytes differ from its own `load()` →
  `dump()` form (a hand edit that is semantically equal but not canonical lands here);
- **`foreign`** — files in `data/` that are neither canonical `*.jsonl` nor `.lock`;
- **`loadable`** — an FK/CHECK/JSON failure is reported as a finding with the file and line,
  never raised;
- **`memory_matches_disk`** — when the package is open, the open connection's dump compared
  to disk (a refused flush — the stale-tree case — is exactly when the two diverge);
- **`digest`** — sha256 over the sorted `(file name, sha256(bytes))` pairs of the canonical
  files: a fingerprint of the state as committed.

Read-only by default (no lock taken, nothing written). `record=true`, on an open package and
only when the verification passed, appends ONE `integrity-verified` journal row (actor
`system:package-verify`) naming the digest — a citable fact. **That row rewrites
`progress_entries.jsonl`, so the recorded digest describes the state BEFORE the row, and the
next verify's digest differs by construction**; the entry says so. This is evidence that a
state WAS verified, not tamper-evidence: a hand edit followed by any tool call is rewritten
into perfect canonical form with a journal entry naming the row, and nothing here (no hash
chain, no signature, no external anchor) would show it — that remains git's job.
