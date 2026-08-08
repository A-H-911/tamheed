<!-- Archived by plan 025 Phase 3 (field-evidence C31). Verbatim copy of the tenth ACMP
operator field report (findings_10.md): the FIRST execution-shaped report — a month of
PH-5 work (PE-131..182, AV 74..105, defects 13..27) against a live package. Four
confirmed defects (A1 _next_id text-sort 1000-row ceiling; A2 false "unknown entity
type" that wrote a wrong claim into the package's permanent record for three days; A3
INSERT OR IGNORE counting discarded rows as applied; A4 the append-only journal being
silently rewritable), two read-confirmed hazards (C1 stale-tree clobber on commit; C2
work_bind partial writes), the bare-PID lock gap (D), and the F6 docs omission (package
data = git working tree). §B is the operator's own retraction (git reset, not tamheed —
recorded as calibration); §E records positives to preserve (incl. do-NOT-optimize
dump()). Drove v2.7.0. Do not edit: evidence, not documentation. -->

# Tamheed 2.6.0 — field report: the first execution run, four confirmed defects, one retracted accusation

**Context.** Ninth run, and the first of a different kind. `findings.md`–`findings_9.md` were all
**migration/fixture** runs against the frozen Keystone v1 package; this is the first report from
**sustained execution use** — a month of PH-5 cloud-deployment work (2026-07-23 → 2026-08-08) driving
`progress_update` / `audit_record` / `work_bind` / `entity_upsert` many times a day against a live
package. Window fixed at `findings_9.md`'s mtime, 2026-07-23 11:15Z (that file is git-excluded, so
there is no adding commit to cite); progress entries **PE-131 … PE-182** are in-window. Growth over
the window: `progress_entries` 130→182, `audit_verdicts` 74→105, `defects` 13→27. Same **2.6.0**
plugin as `findings_9.md`, and the installed build at
`~/.claude/plugins/cache/tamheed/tamheed/2.6.0/` is **byte-identical to the repo source after
line-ending normalisation** — so nothing below is already fixed upstream. `findings_9.md` left **no
open asks**, so no regression table is owed. file:line refs are into the 2.6.0 plugin source. Gates
7/7 throughout; audit 93/12 at close. Every claim below was observed directly unless marked
unverified. Final state at close of this pass: PE-183 · AV-105 · DEF-027 · audit 93/12; all three
§A repros re-run against the installed 2.6.0 and reproducing verbatim.

**Bottom line.** Execution use surfaces a class the migration runs could not: four confirmed defects,
three of them **silent or actively misleading**, and two proven by running the tool rather than
reading it (§A1, §A3). The most expensive is not the most severe — §A2 is a **false error message**
that put a wrong statement about Tamheed into our package's permanent record, where it sat for three
days. §B retracts an accusation *I* made against the tool that turned out to be my own `git reset`;
it is first because it calibrates everything after it. The store itself never corrupted anything
under a month of abuse (§E).

---

## A. Confirmed defects

### A1. `_next_id` sorts ids as TEXT, so every unbounded table dies at 1000 rows

`tamheed_server.py:156-161`:

```python
row = _CURRENT.conn.execute(
    f"SELECT id FROM {table} WHERE id GLOB ? ORDER BY id DESC LIMIT 1", (prefix + "*",)
).fetchone()
n = int(row[0][len(prefix):]) + 1 if row else 1
return f"{prefix}{n:0{width}d}"
```

`ORDER BY id DESC` is a **lexicographic** sort on a semantically numeric value. Inside the
zero-padded width text order and numeric order agree, so this is correct for exactly the first 999
rows. At 1000 it stops being correct **permanently**, because `n:03d` widens rather than truncates
and `"PE-999" > "PE-1000"` as text.

**Reproduction** (stdlib, no package needed):

```python
import sqlite3
c = sqlite3.connect(":memory:"); c.execute("CREATE TABLE t (id TEXT PRIMARY KEY)")
c.executemany("INSERT INTO t VALUES (?)", [(f"PE-{n:03d}",) for n in range(1, 1000)])
def next_id(prefix="PE-", width=3):
    row = c.execute("SELECT id FROM t WHERE id GLOB ? ORDER BY id DESC LIMIT 1", (prefix+"*",)).fetchone()
    return f"{prefix}{(int(row[0][len(prefix):]) + 1 if row else 1):0{width}d}"
nid = next_id(); print(nid)                     # PE-1000
c.execute("INSERT INTO t VALUES (?)", (nid,))
print(next_id())                                # PE-1000  <-- again
print(next_id())                                # PE-1000  <-- forever
```

**Impact.** `id` is the primary key, so the second insert raises `IntegrityError`, the handler rolls
back and the tool returns an error. Loud, not silent — but **permanent and unrecoverable through the
MCP surface**: from row 1000 onward no progress entry and no audit verdict can ever be written to
that package again.

**Why nine prior runs never saw it, and why every execution run eventually will.** `_next_id` has
exactly three call sites, and all three are the **append-only, unbounded-growth** tables:

| Call site | Line | Table | Growth |
|---|---|---|---|
| `progress_update` | 415 | `progress_entries` | one row per narrative, forever |
| `audit_record` | 442 | `audit_verdicts` | one row per verdict; re-verdicts append |
| `work_bind` | 475 | `progress_entries` | one row per commit/PR binding, forever |

Every other id in the schema is **caller-supplied** (`FR-`, `AC-`, `DEC-`, `DEF-`…) and bounded by
the size of the plan. The ceiling is therefore invisible to planning-shaped and migration-shaped
workloads — the whole `findings.md`–`findings_9.md` corpus — and guaranteed for any package that is
*executed* long enough. This package reached PE-182 in three weeks of daily execution.

**Suggested fix:** order by value, and let `CAST` absorb a non-numeric suffix that slips past the
GLOB (which the current Python-side `int(...)` cannot survive either):

```python
row = _CURRENT.conn.execute(
    f"SELECT MAX(CAST(SUBSTR(id, ?) AS INTEGER)) FROM {table} WHERE id GLOB ?",
    (len(prefix) + 1, prefix + "*"),
).fetchone()
return f"{prefix}{(row[0] or 0) + 1:0{width}d}"
```

`MAX` also removes the empty-table branch. Regression test: seed 999 rows, allocate twice, assert the
ids differ.

### A2. `entity_query` reports a valid, writable entity type as "unknown" — and it corrupted our record

`tamheed_server.py:306`:

```python
if table is None or type in ("trace-edge", "omission"):
    return _err(f"unknown entity type {type!r}")
```

`trace-edge` **is** a registered entity type — `tamheed_server.py:77` reads
`"trace-edge": "trace_edges",   # composite PK; write surface for relations` — with its own
`entity_upsert` branch at `:263-265`, and it is documented as a write surface in the plugin's own
`server/README.md:68` and `SKILL.md:141`. Only the underscore spelling `trace_edge` is genuinely
unknown.

Both halves verified against the live package rather than reasoned:

```
entity_upsert(type="trace-edge", from_id="AC-001", to_id="FR-001", relation="verifies")
  -> {"ok": true, "applied": 1}
entity_query(type="trace-edge")
  -> {"ok": false, "error": "unknown entity type 'trace-edge'"}
```

The same string is simultaneously a working write surface and a nonexistent type. The read surface
reports **non-queryable as nonexistent**, and that is not a cosmetic distinction.

**This is the most expensive item in the report, though not the most severe.** On 2026-08-05 an
integrity audit of ours hit that message and concluded, in writing, that *"tamheed 2.6.0 exposes no
write path to trace_edges in any case (entity_upsert rejects both 'trace-edge' and 'trace_edge')"*.
That false statement was recorded into `OQ-065`, `PE-166`, `PE-167` and `PE-169` — our package's
permanent record — and sat there for three days until this run tested the call instead of believing
the error. A wrong
message does not merely waste a minute; it propagates into downstream records that outlive the
session. Corrected on our side 2026-08-08.

**Suggested fix:** distinguish the two conditions. `unknown entity type 'X'` when `X` is absent from
`ENTITY_TABLES`; something like `entity type 'X' is not queryable (composite key, no id column) —
it is writable via entity_upsert` when it is present but excluded here.

### A3. `INSERT OR IGNORE` discards invalid rows and reports them as applied

`tamheed_server.py:263-265`:

```python
if etype in ("trace-edge", "omission"):
    sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(names)})" ...)
```

SQLite's `IGNORE` resolution skips rows violating NOT NULL / CHECK / UNIQUE / PK **with no error**.
`trace_edges.relation` carries `CHECK (relation IN (...))` at `schema.sql:559`, so a typo'd relation
is dropped on the floor while `:277` still appends `{"ok": True}` and `:297` returns
`"applied": len(entities)` — a count of *attempts*, not writes.

**Verified live**, and the test is self-cleaning precisely because the bug discards the row:

```
entity_upsert(type="trace-edge", from_id="AC-001", to_id="FR-001",
              relation="bogus_relation_not_in_check_constraint")
  -> {"ok": true, "applied": 1}
trace_query("AC-001", direction="out")
  -> exactly one edge, relation "verifies"      # the bogus edge was never written
```

`trace_edges.jsonl` stayed at 1042 rows across both probes. **Symptom:** the caller believes the
traceability graph was written; `G-TRACE` then either fails with no explanation or passes because
the edge it would have checked never existed. This is the same silent-success family as A2, one
layer lower.

**Suggested fix:** `conn.execute(...).rowcount == 0` distinguishes skipped from written — report the
skipped rows in the per-item verdict rather than counting them as applied. (Note FK violations *do*
still raise, so this is not a total bypass.)

### A4. The append-only journal is silently rewritable, and nothing can be deleted

`audit-verdict` and `progress-entry` are both in `ENTITY_TABLES` (`tamheed_server.py:64-65`), so
`entity_upsert` takes the `ON CONFLICT(id) DO UPDATE SET` path at `:267-270` and will **rewrite a
recorded verdict or progress entry in place, leaving no trace** — despite `schema.sql:437`
describing an append-only journal. Conversely, no tool in `TOOLS` (`:872-888`) deletes a row, so a
mistyped entity is permanent. Both halves of the contract are inverted: the immutable thing mutates,
the mutable thing cannot be removed.

We did not hit this destructively — every correction in this window was made by **appending** a
retraction (PE-181, PE-182, AV-105) rather than editing history, which is the right practice
anyway. But that was discipline, not enforcement.

**Suggested fix:** if append-only is the intent, exclude those two families from the `DO UPDATE`
path and make a conflicting id an error. A `supersedes` column would then carry corrections
explicitly, the way `adrs` already does.

## B. Retraction — "Tamheed silently loses writes" was wrong, and the cause was mine

I recorded in this package, in a commit message and in a memory file that two package sessions had
silently lost every write and that ids were being reused to overwrite earlier rows. **That
diagnosis was wrong.** It was never carried in any prior findings file — the incorrect record was
PE-level plus a memory file, both since corrected (PE-181) — so there is no struck sentence to hunt
for in `findings.md`–`findings_9.md`.

What actually happened: `tamheed-package/data/*.jsonl` is **git-tracked** (29 files), and canonical
state is written there rather than to a private store. I was merging PRs throughout the run and ran
`git reset --hard origin/main` repeatedly. Any package write not yet git-committed was discarded
**by my own reset**. Checked before retracting: only two commits in the whole run ever carried
package data, `git reflog` shows the resets sitting between the writes and any commit, and
`git show <sha>:tamheed-package/data/audit_verdicts.jsonl` finds `AV-103` in none of the
intermediate commits.

Tamheed's behaviour was **correct at every step**: on each re-open it loaded canonical state as it
actually stood on disk and allocated the next free id from it. What I read as id reuse was the
allocator being right about state I had rewound underneath it.

Recorded prominently because a false "this tool loses data" report is expensive, and because the
same misreading nearly happened twice more this run: a suspected migration-fidelity defect in
`NFR-056`/`NFR-057` turned out to be **our own prose** (the package rows are faithful to the v1
source), and A2 above was believed for three days on the strength of an error message. **The
genuine lesson is the inverse of the one I first recorded** — a Tamheed package *is* a git working
tree, so `git reset --hard`, `git checkout` and `git stash` destroy uncommitted package writes
exactly as they destroy uncommitted source. §F6 asks for that to be written down. (Writing this
report cost one more demonstration of it: untracking *this file* and then running
`git reset --hard` deleted it outright, because reset applies the recorded deletion. It had to be
rewritten from scratch.)

## C. Hazards — mechanism confirmed by reading, not observed firing

### C1. `commit()` will clobber a `data/` that moved underneath it

`store.py:152-154` — `PackageStore.commit()` calls `dump()`, which **rewrites every table from
memory unconditionally**. There is no check that `data/` still matches what `load()` read. So the
mirror image of §B is a live data-loss path: package open → `git checkout` / `git pull` / a second
writer edits → any subsequent write tool calls `commit()` → **every incoming change is silently
overwritten** by the session's older in-memory copy, with no error.

§B is the reason to take this seriously rather than treat it as theoretical: the package lives in
git and branch operations during a working session are routine. §B fired in the harmless direction
(my writes lost, disk state intact); the same setup fires the other way just as easily, and that
direction destroys *committed* work. **Not observed firing this window.**

**Suggested fix:** fingerprint at load, verify before dump — `{name: sha256}` over `*.jsonl` only
(`.lock` is yours), recorded in `__enter__` after `load()`, recomputed in `commit()`, raising a
distinct `StoreStaleError` naming the changed files. Measured on this package: 29 files /
3,141,016 bytes, `load()` 0.058 s and a full serialize 0.021 s, so this costs nothing. Keep the
guard in `PackageStore.commit()` rather than in `dump()` so `migrate`/`adopt`, which legitimately
write fresh trees, are unaffected. For the close path, dumping in-memory state to a timestamped
sibling directory before releasing the lock would mean neither side's work is lost.

### C2. `work_bind` leaves partial writes pending on its unguarded failure paths

`tamheed_server.py:464-482`. The unknown-entity-id path *is* handled — `:469` calls
`conn.rollback()`. But `table = ENTITY_TABLES[row[0]]` at `:471` is a bare dict index that raises
`KeyError` for any `entity_index` type absent from the map, and the final `INSERT INTO
progress_entries` at `:476-481` is unguarded. In both cases the `last_referenced` UPDATEs already
applied for earlier ids are left pending on the connection, and whether they land depends on
whether the *next* tool call commits or rolls back.

This composes with A1: once a package passes 999 progress entries, that final INSERT raises
`IntegrityError` **after** the UPDATEs have been applied. `progress_update` and `audit_record` are
clean by comparison — their `_CURRENT.commit()` sits outside the `try`, which is correct placement.

**Suggested fix:** wrap the body in the same `SAVEPOINT`/rollback shape `entity_upsert` already uses
at `:246`.

## D. Lock diagnostics — the bare PID, with field frequency

`store.py:144` writes `str(os.getpid())` into `data/.lock`, and the `StoreLockedError` at `:140-143`
says only "remove the stale lock deliberately if the writer crashed". After a crash the operator
holds a bare number, and the obvious check — *is that PID alive?* — **is unsound**, because the OS
reuses PIDs.

This is not hypothetical here; it has field frequency. The server does not release its lock when it
dies or cycles, so `package_open` fails with a stale lock **recurrently** — twice in one session on
2026-08-04. That session is the worked example of why the check cannot be trusted: the lock named
PID **71948**, and PID 71948 **was alive** — but it belonged to **VS Code, started 10:18:56**, while
the lock's mtime was **01:51:50**, 8.5 hours *earlier*. Believing the liveness check would have
meant leaving a dead writer's lock in place indefinitely.

**Suggested fix:** write JSON (`pid`, `host`, `taken_at`) instead of a bare integer, and include it
in the error so the operator sees *who* holds it and *since when* without opening the file; parse
tolerantly so older bare-PID locks still describe themselves. I would **not** auto-reclaim on a
"dead" PID — that trades a visible annoyance for an invisible two-writer corruption, and PID reuse
is exactly why the check cannot carry that weight.

## E. Positives worth keeping exactly as they are

- **The store did not corrupt anything under a month of execution.** Gates stayed 7/7, FK
  enforcement and the immutability triggers never misfired, `export_html` stayed consistent with the
  JSONL, and — per §B — it recovered cleanly and correctly from a working tree I repeatedly rewound
  underneath it. The one behaviour I mistook for a bug was the tool being right.
- **The `entity_upsert` full-row contract made repair mechanical.** Correcting a defect's evidence
  text, retracting a false clause in a resolved open question, and re-applying a lost `work_bind`
  all went through the MCP surface with no hand-editing of canonical files.
- **Two earlier field frictions are already fixed in 2.6.0, with the evidence in the comments.**
  `tamheed_server.py:322-323` names the `limit=100` silent truncation that cost a caller a
  218-row family and now returns `total`; `:284-286` names the real cause on a NOT-NULL failure.
  Field reports visibly landing in the source is the reason these are worth writing.
- **`dump()` rewriting everything is fine at this size** — 29 files / 3.1 MB, 0.021 s to serialize.
  Recorded so it does not get optimised on suspicion.
- **The migration was faithful where I doubted it.** `NFR-056`/`NFR-057` looked swapped against our
  entire codebase; the package rows match the v1 source exactly, and the swap was in our prose.

## F. Asks, in priority order

1. **§A1 `_next_id`** — confirmed, reproduced, one-line fix, and it sets a silent expiry date on
   every executed package. This is the one that matters.
2. **§A2 the false "unknown entity type"** — cheapest fix here and the one with proven downstream
   cost: it wrote a wrong statement into another project's permanent record.
3. **§A3 `INSERT OR IGNORE` counting attempts as writes** — silent, and it undermines the
   traceability graph `G-TRACE` gates on.
4. **§C1 stale-overwrite guard** — real silent-data-loss path, made routine by packages living in git.
5. **§A4 append-only that is not** / **§C2 `work_bind` savepoint** / **§D lock metadata**.
6. **Docs** — state somewhere load-bearing that package writes are *working-tree* changes and must
   be committed before branch operations. `AGENTS.md`/`CLAUDE.md` say "never hand-edit" and
   "canonical JSONL is flushed on `package_close`", never that it lands where `git reset` can reach
   it. §B is what that omission cost one careful operator, twice.

**Threads continued, not re-raised.** `v_backlog` (`findings_4 §D-11`, answered `findings_5`
**"DISCLOSED, not fixed."**) is still our `DEF-012` and still the sole long-lived open defect — the
`execution_state_note` disclosure remains the right call for a docs importer. And `gate_run` counting
verdict **rows** while `review.html` counts **criteria** (our OQ-065/PE-167) is correct on both
sides — they differ by the number of supersessions — but it costs a reader time on every reconcile;
a one-line note in the export would end that permanently.

## G. Verdict

The first execution-shaped run finds what nine migration runs structurally could not: three of the
four confirmed defects are silent or actively misleading, and two of them (§A1, §A3) are invisible
until a package has been *used* rather than *produced*. None of them corrupted data here, and §A1
has not fired yet — but it will, on a schedule set by how much the package is used, and the fix is
one line.

The report's own history is the caveat worth keeping: of four things this project believed about
Tamheed this window, **one was my error (§B), one was our prose (§E), and one was the tool's error
message believed for three days (§A2)**. Only running the calls settled them. If there is a single
ask beyond the code, it is that error messages be treated as part of the data contract — §A2 shows
they end up in other people's records.
