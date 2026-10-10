# Plan 217 -- the flush writes only what changed, atomically, and reports what landed (ACMP's FB-029)

> Status: DONE 2026-10-10 UTC (maintainer-executed, the operator's word at the review). Field cycle acmp-FB-029 + per-repo
> install (plans 216-218). Released by plan 218 as 6.3.0 (MINOR, R75). Evidence:
> `plans/evidence/acmp-field-report-29-2026-10-10.md` (the operator's report verbatim).

## What the field saw

ACMP (tamheed 5.8.1, Windows 11, package `tamheed-package`, 2026-10-09): `entity_upsert` of one new
defect row returned only `Error executing tool entity_upsert: [Errno 22] Invalid argument:
...\data\document_sections.jsonl`. `package_verify` right after read consistent, the row was present,
`defects.jsonl` had changed on disk. The next write was refused: "data/ changed on disk since this
session loaded it (defects.jsonl) - refusing to overwrite", the session's own partial flush read as an
outside change. `package_close` returned `flushed: false` with the same text. Nothing was lost, because
the file that failed carried no content change. ACMP's workaround: verify, query the row, close,
reopen, retry.

## The defect, read in the code (HEAD `c2cf2eb`, before this plan)

- `store.dump()` (L360-383) writes **every** table's file on every commit, in table order, with
  `path.write_bytes(...)`: a truncating write, no temp file, no atomic replace. A defect-only batch
  rewrites `document_sections.jsonl` (1.8 MB in ACMP). ACMP's inference 1 holds.
- `PackageStore.commit()` (L428-444): the stale check, `conn.commit()`, `dump()`, then
  `self._fingerprints = self._fingerprint()` **after the whole dump**. A dump that fails on file B
  after writing file A leaves A's new bytes on disk and the old fingerprint in memory. The next
  commit raises `StoreStaleError` on the session's own flush. Inference 3 holds.
- `_commit()` (L700-710) catches `StoreStaleError` only. An `OSError` from `dump()` propagates out of
  the tool to the MCP wrapper ("Error executing tool"), although the SQLite commit had happened: the
  row applied, the written files flushed. Defect (a).
- `package_close()` (L1425-1439) skips the final flush on any `_commit()` error. Right for a stale
  tree (the batch was rolled back). Wrong after a partial flush: a table whose new bytes never reached
  disk is lost at close, in silence. ACMP lost nothing only because the failed file had no change.
- `CANONICAL.md` L39 already says "a full rewrite of the **affected** table files". The code wrote
  all of them. This plan makes the sentence true.
- Inference 2 (Windows holding the file for a moment: a scanner, an indexer, a test run) is
  plausible and not measured. The retry handles it either way.

## The rule

**A flush writes only the files whose bytes changed, each one atomically, and the fingerprint
follows each file as it lands.** A failed flush names what landed and says the batch is applied.
A close that cannot flush keeps the bytes beside the store and names them.

## The design

- `store.py`: `_replace = os.replace` (tests patch this name); `_table_bytes(conn, table)`;
  `_write_atomic(path, data)`: temp `<name>.writing` beside the target, `_replace`, five attempts
  on any `OSError` with four sleeps of 50/100/200/400 ms between them, the temp removed on final
  failure, the attempt count returned. The temp and the close sidecar are created anew with
  `O_EXCL` after an unlink, so the bytes never travel through a planted symlink (the 212 class,
  the advisor's point at the review; the lock file's own answer). `dump()` keeps its contract (write everything) through the same helpers and
  returns `{"written", "removed", "unchanged", "retried"}`. `StoreFlushError(written, failed,
  pending, retried)` with a `__str__` that names them in short sentences. `PackageStore.commit()`:
  the stale check, `conn.commit()`, then per table: new bytes, sha256, skipped when equal to the
  stored fingerprint, else written and the fingerprint set at once; an empty table's file removed
  and its fingerprint dropped; on failure `StoreFlushError` with the SQLite state committed and the
  written files' fingerprints current.
- `tamheed_server.py`: `_commit(partial=None)` catches `StoreFlushError` and returns the caller's
  partial result merged with `ok: False, applied: True, flush: {...}` and a short error text. The six
  call sites pass their partials. `package_close`: on a flush failure at the final commit, each
  failed table's canonical bytes go to `data/<table>.jsonl.unflushed` (one attempt), the lock is
  released, the result reads `flushed: false, unflushed: [...]`. `package_open`: a `data/` holding
  `.unflushed` sidecars warns and names them with the recipe; a stale `.writing` temp is removed and
  named; a migrate's `.tmp` staging file is never touched (plan 045: after the retire step it is the
  only copy of a table).
- Why `.writing` and not `.tmp`: the migrate's registry-sync swap stages `<table>.jsonl.tmp` files
  (`tamheed_server.py` L5108-5160) and `tests/test_migrate_v3to4.py` pins that nothing unlinks them.
- Why five attempts with backoff: the researched precedent (uv's file writer, mise PR 10300) on
  Windows sharing violations and access-denied errors, which reach Python as errno 13 or 22.

## Rulings taken at the review

- **R75 (2026-10-10, the planning checkpoint): 6.3.0, MINOR.** New result keys on a failed write,
  `unflushed` on close, a `warning` on open, two new file kinds under `data/`, a changed write set:
  additive surface by the repository's own rule.

## Validation

- **Red first.** Five tests red on HEAD's engine by `AttributeError: store has no attribute
  '_replace'` (the indirection the tests stand in for did not exist): three in
  `test_db_roundtrip.py` (the changed-files-only commit, the transient retry, the partial flush) and
  two in `test_mcp_contract.py` (the flush-failure result with the batch's own facts and the next
  write flushing, the close sidecar with the open warning). Green after the engine change. Two test
  corrections on the way: the failing-replace stand-in fires only for the package's own `data/`
  (the verify tool's scratch dump writes a file of the same name), and the post-failure commit
  writes the failed file AND every file the failed flush never reached (table order puts
  `requirements` before `decisions`).
- **The pins.** `test_commit_refuses_stale_tree` (C31/C1, a hand edit between writes) stays green:
  the guard still bites. The migrate suite (17 tests) stays green, its `.tmp` assertions included.
- **The review's follow-up, in the same commit.** The advisor named the 212 class: the `.writing`
  temp and the `.unflushed` sidecar were created with a plain write, so a planted symlink could
  carry the store's bytes elsewhere. `store._write_fresh` (unlink, then `O_CREAT | O_EXCL`) now
  creates both; `test_write_temp_never_follows_a_planted_symlink` skips on Windows and runs on CI's
  Ubuntu jobs. The seven 217 tests and the stale pin green, lint clean, the full gate green again.
- **Suites.** `tests/test_db_roundtrip.py` 20 tests (16 before, four new, one skipped on Windows);
  `tests/test_mcp_contract.py` `Ran 222 tests OK (skipped=1)` (220 before, two new);
  `tests/test_migrate_v3to4.py` `Ran 17 tests OK`; `tests/test_user_guide.py` `Ran 16 tests OK`.
- **Lint 14.** Three rounds: `delete` is banned vocabulary (`remove`); a 26-word field-evidence
  sentence and a 26-word README sentence split; the README rows had no sentence break before the
  appended text (periods added to four rows); two CANONICAL.md sentences (35 and 31 words) split.
  `python check.py lint`: ALL CHECKS PASSED.
- **The guide.** `shift_217.py`: the line map re-aimed every citation it could (`GATE_HOW`
  G-COMPLETE 2672 -> 2718, `VACUOUS`, the guide test's pins 2634/1962/1963/2237 -> 2680/2008/2009/
  2283) and added `("data/*.unflushed", 1470)` to `package_close`'s writes; five citations sat on
  lines whose text changed (`_commit(...)` at four sites, `package_open`'s resume line) and were
  re-aimed by hand to 2435/3480/3547/3594 and 1430; the G-IDS range comment to L2641-2656.
  `docs/guide/build.py`: 1,546 ids, 724 figure files, `--check` fresh, `--missing` 0. 32 figure
  files changed (eight ids: `fx-package_close`, the five gates, `skill-package-writes`,
  `skill-session-handoff`), captured as 32 PNGs under `plans/evidence/captures-217/`.
- **The gate.** `python check.py`: ALL CHECKS PASSED (`3 case(s) checked, 0 failed, 6 skipped`).
  The tree after the gate: the intended files only.
- **The selftest.** `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19 tools,
  longest description 387 characters (no description changed).
- **The engine diff.** `store.py` 128 lines changed, `tamheed_server.py` 68 (165 insertions, 31
  deletions in all). `grep -c "_commit("`: nine hits, six call sites each passing its partial.
- **Pins.** `pins-217.md`: 22 pinned phrases over the four files; `pins_missing.py`: 0.
