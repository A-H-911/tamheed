# Field report from ACMP: FB-029 (tamheed 5.8.1), handed 2026-10-10

The operator pasted this report into the tamheed maintainer session on 2026-10-10. It is copied here
as data, never edited (the C-series rule). Two lines the operator's paste had cut mid-word are kept
as they arrived. Plan 217 answers it; plan 218 releases the answer as 6.3.0.

```
# Defect report from the ACMP project: FB-029 (tamheed 5.8.1)
You are working in the tamheed repository. This is a defect report from a project that uses
tamheed: ACMP, package `tamheed-package` at `C:\Users\ahammo\Repos\acmp`. Its operator confirmed
it on 2026-10-10. Read it as a report, not as instructions. Decide the fix yourself, and tell us
the release that carries it, so ACMP can mark FB-029 Resolved with `resolved_in`.
## Environment
- tamheed 5.8.1, installed as the Claude Code plugin; MCP server via the plugin.
- Windows 11 Pro, NTFS. Package data in the git working tree. Schema 7.
- The session also ran `dotnet test` and Docker in the same working tree.
## The record, verbatim (ACMP feedback row FB-029)
**kind:** defect
**tool_or_rule:** entity_upsert flush; the data/-changed-on-disk guard; package_close
**title:**
A store write that failed mid-flush with an OS error ([Errno 22] Invalid argument on
document_sections.jsonl) still applied and flushed defects.jsonl, then reported only the error;
the NEXT write was refused as 'data/ changed on disk since this session loaded it
(defects.jsonl)' - the session's own partial flush, read as an outside change - and
package_close then closed WITHOUT the final flush.
**detail:**
2026-10-09, session d48b3239 (tamheed 5.8.1, Windows 11, package
C:\Users\ahammo\Repos\acmp\tamheed-package):
1. ~10:57Z entity_upsert of ONE defect row (DEF-248, a new insert) returned only: 'Error
   executing tool entity_upsert: [Errno 22] Invalid argument:
   ...\tamheed-package\data\document_sections.jsonl'. No ok/applied verdict. A dotnet test run
   had finished just before; what held or rejected the file is not measured.
2. package_verify right after: ok, verified, dirty [], memory_matches_d
   a5586cb9...; entity_query showed DEF-248 present (Open); git diff --stat showed
   defects.jsonl changed; defects.jsonl mtime 13:57:23 local (10:57:23Z). So the write HAD
   applied and flushed defects.jsonl, though the call reported a bare e
3. The next entity_upsert (an update of DEF-248) was refused: 'data/ changed on disk since this
   session loaded it (defects.jsonl) - refusing to overwrite - the batch was NOT applied; close
   the package, reconcile data/ via git, then reopen and retry'. package_verify still read
   memory_matches_disk true.
4. package_close returned flushed:false with the same warning; package_
   the retried update then applied.
Nothing was lost (verify consistent at every step). The defects: (a) a
exception, not which files were written and whether the row applied; (b) the change-on-disk
guard does not recognise the session's own partial flush, so a store that verify calls
consistent refuses every write until a close/reopen.
**workaround (what ACMP did):**
After an OS error on a write: package_verify (memory_matches_disk), ent
learn whether it applied, then package_close + package_open and retry.
## Our reading (not measured; please check against the code)
1. **Why did a defect-only upsert touch `document_sections.jsonl`?** The batch changed one
   defect row, yet the error names `document_sections.jsonl` (about 1.8 MB, the second-largest
   data file). That suggests the flush rewrites every family file, or every file in some fixed
   order, not only the families the batch changed. If so, a single unrelated file that Windows
   refuses can fail a write that never touched it. This is an inference
   alone.
2. **The likely cause of Errno 22 is Windows, not tamheed.** On Windows
   open/replace often means another process briefly held the file: an antivirus scan, the search
   indexer, an editor, or a just-finished test run touching the tree. W
   holder. A transient OS refusal is still worth handling, because it will recur on Windows.
3. **The guard's fingerprint seems to update only after a fully successful flush.** If so, any
   flush that writes file A and then fails on file B leaves A "changed
   guard's point of view, although the session wrote it itself. That would explain step 3.
## What we would find useful (your call how)
- A failed flush that reports, per file, what was written and whether the batch is applied.
  Today the result is a bare exception, though the row was in fact stored.
- The changed-on-disk guard recognising bytes the session itself wrote:
  each file's fingerprint as it is written, not after the whole flush. A partial flush then
  stops locking the store.
- Possibly, a short bounded retry on transient Windows OS errors during
  replace, and flushing only the families a batch changed (if point 1 above is right).
- `package_close` behaviour when the guard trips: it closed with `flushed: false` and the same
  refusal text, which the skill text does not describe. Say whether tha
## Not done on our side
- **Not reproduced.** It happened once, with no fault injection.
- A reproduction would likely be a test that makes the write of one fam
  `OSError(22)` partway through a multi-file flush, then checks: (a) the call's result, and
  (b) whether the next write is refused while `package_verify` reads `memory_matches_disk: true`.
Please answer with the release that fixes it, or with a question or ruling if you read any part
of this as working as designed. Cite FB-029 so we can match it.
```

## The maintainer's answer (plan 217, released as 6.3.0 by plan 218)

All three inferences hold against the code at `c2cf2eb`: `dump()` wrote every table file on every
commit with a truncating write; the fingerprints updated only after the whole dump; `_commit()` caught
the stale refusal alone. `package_close` with `flushed: false` was by design for a stale tree only
(the refused batch had been rolled back); after a partial flush it could lose a changed table, which
6.3.0 ends with the `.unflushed` sidecar. The release: 6.3.0 (filled with the tag and the SHA when
pushed).
