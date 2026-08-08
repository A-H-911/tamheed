<!-- Archived by the plan 025 acceptance close-out (field-evidence C32). Verbatim copy of
the eleventh ACMP operator field report (findings_11.md): C31 verification on v2.7.0 —
ALL FOUR §A defects closed and verified by running the tools (A1 with a text-order
control line; A2 both spellings; A3 rejected-vs-unchanged split; A4 append-only hint),
C1 stale-tree guard exercised deliberately (names the file, preserves disk, close never
traps) and D lock metadata verified across a real process boundary. C2 source-confirmed
only in the report — covered in-repo by test_work_bind_failure_leaves_no_pending_stamp.
§C's MCP-reconnect note is harness-side (byte-identical .mcp.json, clean --selftest),
not a plugin fault; the run verified tool functions + store in-process, not the MCP
transport. Second zero-actionable-findings report — no plan 026, no release.
Do not edit: evidence, not documentation. -->

# Tamheed 2.7.0 — field report: C31 verification, all four §A defects closed

**Context.** Tenth run, and the shortest. 2.7.0 is the C31 response to `findings_10.md`, and this run
is verification only — every §A repro from that report re-run against the installed build, plus the
§C1 and §D fixes exercised deliberately. `server_info` reports **2.7.0**; the source carries `C31`
markers keyed to my own section numbers (`# C31 (A1)`, `(A2)`, `(A3)`, `(A4)`, `(C1)`, `(C2)`, `(D)`),
so the release is traceable to the report line by line. Live-package writes this run: **zero** — the
only committed change is a one-line `review.html` regeneration. Gates 7/7 and audit 93/12, unchanged
by the upgrade. file:line refs are into the 2.7.0 plugin source. Every claim below was observed
directly unless marked unverified.

**Bottom line.** **All four §A defects are FIXED, and both §C/§D items with them.** Every fix was
verified by *running* the tool, not reading it — the standing lesson of findings_10 §A2. Nothing
regressed, the UNEXPECTED bucket is empty, and the two threads carried since `findings_4` are now
answered in-surface. One operational note that is **not** a Tamheed defect: the MCP server did not
reconnect after the upgrade (§C).

---

## A. §A verdict table — every item, with the tool's own output

### A1 — the id ceiling. **FIXED, verified.**

Scratch package seeded to 999 `progress_entries`, then `progress_update` twice through the real tool:

```
seeded rows: 999
max by TEXT order: PE-999          <- the old ORDER BY id DESC would still have said this
  progress_update #1: ok=True ids=['PE-1000']
  progress_update #2: ok=True ids=['PE-1001']
final count: 1001
```

`PE-1000` then `PE-1001` — no `IntegrityError`, no repeat. The `max by TEXT order` line is the control:
text order still reports `PE-999`, so the fix is genuinely in `_next_id`'s numeric `MAX` and not an
artifact of the fixture. Scratch deleted.

### A2 — the truthful refusal. **FIXED, verified.**

```
entity_query('trace-edge'): entity type 'trace-edge' is write-only (composite key, no id column)
                            — writable via entity_upsert; query edges via trace_query
entity_query('omission')  : (same write-only message)
entity_query('trace_edge'): unknown entity type 'trace_edge'
```

The message now names both the write path and the read path, and the underscore spelling is still
correctly unknown. This was the item with proven downstream cost — the old "unknown entity type" put
a false statement into this project's permanent record for three days. A reader hitting the new
message cannot make that mistake.

### A3 — writes vs attempts. **FIXED, verified.**

```
bogus relation:      {"ok": false, "applied": 0, "error": "batch rolled back — one or more items
                      violated constraints"}
   item: {"index": 0, "ok": false, "error": "row rejected by a constraint (CHECK/NOT NULL)
          — not written"}
real existing edge:  {"ok": true, "applied": 0}
   item: {"index": 0, "ok": true, "unchanged": true}
```

Both halves land: the constraint-violating row is now a loud per-item rejection instead of a silent
`applied: 1`, and the genuine idempotent re-write is `ok` with `unchanged: true, applied: 0`. `applied`
counts writes, not attempts. The distinction between "rejected" and "already correct" is exactly what
was missing.

### A4 — append-only enforced. **FIXED, verified.**

```
upsert onto PE-001: {"ok": false, "applied": 0}
   item: {"error": "UNIQUE constraint failed: progress_entries.id — append-only journal: append a
          new entry via progress_update / audit_record instead of editing history; corrections are
          recorded as new entries"}
   PE-001 untouched: True
```

The `ON CONFLICT … DO UPDATE` path is gone for the journal families, and the error teaches the right
move rather than just refusing. Every correction across the previous window was made by appending —
that was discipline; it is now enforcement.

## B. C1 and D — the two hazards, exercised deliberately

### C1 — the stale-tree guard. **FIXED, verified**, and it is the §B inverse now protected.

With the package open, a `data/*.jsonl` was modified externally (simulating a `git checkout` under a
live session — the exact shape that cost this project three package sessions):

```
write while stale: {"ok": false, "error": "data/ changed on disk since this session loaded it
                    (defects.jsonl) — refusing to overwrite — the batch was NOT applied; close the
                    package, reconcile data/ via git, then reopen and retry"}
disk content preserved: True
package_close:     {"ok": true, "flushed": false, "warning": "closed WITHOUT the final flush — …"}
after revert + reopen: {"ok": true, "ids": ["PE-184"]}
```

Four properties, all present: the refusal **names the changed file**, the incoming disk content is
**preserved** rather than clobbered, the batch is **not** applied, and `package_close` still succeeds
— a stale tree does not trap the session — while flagging `flushed: false` so the loss cannot be
silent. Normal writes resume after reconciling. This is the single most valuable fix in the release:
the failure it prevents destroys *committed* work, which the original direction did not.

### D — lock metadata. **FIXED, verified from a second process.**

```
.lock: {"pid": 153920, "host": "Anas-PC", "taken_at": "2026-08-08T19:37:20+00:00"}
contender: …\.lock exists — another writer owns this package (held by pid 162640 on Anas-PC
           since 2026-08-08T19:37:56+00:00; remove the stale lock deliberately if the writer crashed)
```

Tested across a genuine process boundary rather than in-process, because the in-process guard
("package is already open") short-circuits the lock path and would have proved nothing. The holder
and the since-when are both named, which is what makes a stale lock judgeable — the field case behind
this ask was a live PID that belonged to an unrelated program started hours *after* the lock.

**C2 (`work_bind` transactionality) is source-confirmed only** — `# C31 (C2): one transactional unit`
at `tamheed_server.py:531`. It was not in this run's repro set and is marked unverified rather than
claimed.

## C. Unexpected — one, and it is not a Tamheed defect

**The MCP server did not reconnect after the upgrade.** Following `/plugin` update + `/reload-plugins`,
every `mcp__…__tamheed` tool became unreachable, and a full session restart did not restore them.

Diagnosed before reporting, because "the new release broke the server" would have been the easy and
wrong conclusion — the same shape of error as findings_10 §B:

- `2.6.0/.mcp.json` and `2.7.0/.mcp.json` are **byte-identical**; the launcher did not change.
- `uv run …/2.7.0/server/tamheed_server.py --selftest` starts cleanly and lists **15 tools**.
- `server_info()` in-process reports **2.7.0**.

So the server binary is healthy and this is a harness-side reconnect failure, not a plugin fault. All
verification above was therefore run **in-process**, importing the module and calling the tool
functions directly — which is the plugin's own documented posture (*"Tool handlers are plain
functions (in-process testable, no transport needed)"*) and how its contract tests drive it. **Scope
of that caveat, stated plainly: this run verifies the tool functions and the store, not the MCP
transport layer.** Every C31 fix lives in those functions or in `store.py`, so the coverage is
right — but a transport-level regression would not have been caught here.

## D. Threads continued — both now answered in-surface

- **`gate_run` rows vs `review.html` criteria** (`findings_4`-era, restated in `findings_10`): the
  export now renders *"105 verdict row(s) over 86 criteria — verdict rows ≥ criteria because
  corrections and re-verdicts APPEND (gate_run counts rows; this table shows each criterion's
  latest)"*. Exactly one line of `review.html` changed. The reconcile that OQ-065/PE-167 had to work
  out by hand is now permanent, on the surface, where the next reader meets the discrepancy.
- **`v_backlog` / our DEF-012** (`findings_4 §D-11`, answered `findings_5` **"DISCLOSED, not fixed."**)
  remains as-is and remains correct for a docs importer. Not re-raised.
- **F6 (docs)** landed as an emitter change. The note is **append-once**, so an existing `CLAUDE.md`
  is not rewritten — correct behaviour, and worth stating because it means existing targets must add
  the line by hand. Done here.

## E. Positives worth keeping exactly as they are

- **Every ask was answered, and traceably.** Six §F asks plus both continued threads, each carrying a
  `C31 (§)` marker naming the finding it closes. The §D comment even preserves the field case that
  motivated it ("a dead writer's PID belonged to VS Code started hours later"). A reader of the source
  can reconstruct why each line exists.
- **The fixes teach.** A3 distinguishes rejected from already-correct; A4's error names the right move;
  C1 says which file changed and what to do about it. These are error messages written as part of the
  data contract — the closing ask of findings_10, taken seriously.
- **`schema.sql` is untouched** between 2.6.0 and 2.7.0. Every fix is in the server and store layers,
  so no package needs migrating to benefit.

## F. Verdict

Ten runs in, this is the first with nothing to ask for. All four §A defects closed, both hazards
closed, both long-running threads answered in-surface, and the one docs ask shipped as an emitter
change with the correct append-once semantics. The UNEXPECTED bucket is empty; the only note in §C is
a harness reconnect issue that the release did not cause and cannot fix.

The §A2 lesson held throughout and is worth restating as the method rather than the finding: every
verdict above came from running the call. Reading 2.7.0's source would have produced the same table
one step earlier and one confidence level lower — and this project has now twice paid for the
difference.
