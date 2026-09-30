# Brief to ACMP — tamheed 5.8.1 (your FB-028 answered; no report unless a class fails)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.8.1.md` and execute it; write no
> report unless a class fails.* Everything below is a CLASS of result, never the field's counts.
> Where an id, a path or a number appears it is either a stable row of yours or the maintainer's
> own measurement on a read-only copy of the package taken by `git archive` at `319d8c55`,
> quoted so you can compare.
>
> **As the operator ruled for 5.7.0 (R53), this brief asks for no report.** You take the release
> at the start of your next ordinary session, check the classes, and write a feedback row only
> for a class that fails. Your mission queue is not held.
>
> **This brief prescribes one row's remaining moves and no other write:** FB-028 to `Resolved`
> (§4), after you have read the row back — your handoff `PE-1584` says you set it `Reported`
> once it has left; only the transitions still ahead of it are yours. Bookkeeping inside the
> bound set; no operator word.
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only.
> Every absence claim below is a claim about tracked files. Your ignored folders were not read.

## 0. Errors owned

- **O21** The 5.8.0 brief's condition for a description named "a compaction" as a context that
  loads the tool. A compaction re-records the listing the client process built when it started;
  it loads nothing. The maintainer wrote that over a gap your FB-026 row had named as
  unmeasured, with an instrument (a census of re-records) that could not tell a listing from a
  server. Your FB-028 read it false; the maintainer replicated it the same day on a second
  process and a second project (§1).
- **O22** The 5.8.0 brief said "then your reload route" and left the route to you; the route you
  took — `claude plugin update`, `/reload-plugins`, `/compact`, one process — is the one that
  shows the old descriptions. This brief names the route (§1).

## 1. The upgrade, and what a session meets

1. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope
   user`, then **quit the client and start it again** (`claude --resume` from a fresh process is
   fine). `/reload-plugins` restarts the server and the hooks; it does not rebuild what the
   session lists (§1's route).
2. **No migration.** No JSONL rewrite. `schema_version` stays 7. **No engine change:** the
   server, the store, the CSV, the page and the note render as 5.8.0 did. 5.8.1 is docs and
   three skill sentences.

**The route, measured twice and a control (Claude Code 2.1.284 on your rows, 2.1.285 on the
maintainer's).** The descriptions and schemas a session lists for the tools were fetched when its
client process started. After `claude plugin update` in a running process, `/reload-plugins`
restarted the server (`server_info` answered the new version) and the hooks (the trace line
`version=5.8.0 source=compact`), and `/compact` re-recorded the listing that process had built —
the 5.7.0 texts. A client process started after the update lists the new text: fresh, at once;
by `claude --resume`, after its first compaction (one case, your `5bc5eab5`). The vendor's docs
state that a reload reconnects a server whose configuration changed and nothing on re-fetching
the definitions a session already lists; `/clear` was not measured.

**What the three skill sentences say (plans 170 and 174, rulings R59, R63, R64):**

| Skill | The sentence |
|---|---|
| `orient-resume` step 1 | the listing is the client process's; `server_info` names the server that answers; after an update only a client process started after it lists the new text — say so to the operator rather than read the listing as the server. **And:** a new client process is not a compaction — `claude --resume`, a `-p --resume` turn, a new terminal: the server restarted with it, the package is closed, a lock left on disk names a process that is gone; a session that ends with `package_close` leaves nothing to unlock |
| `slice-review` step 7, `phase-close` step 2 | a slice closes on at least one bound work item: with no `WBS-` row `wbs-done` reads indeterminate, and a recorded omission of the wbs family does not stand in for a row at slice or phase scope (the scoped rules measure rows — plans 049 and 077, the doctrine kept). The honest route is a work-item row for the verified work, bound to its commit, on the operator's word |

**Where the second sentence comes from.** The lab was driven end to end by a real agent, headless,
through the plugin's own path against this release (`plans/evidence/lab-acceptance-report-2026-09-30.md`):
a fresh run from the seed and four sessions on a copy of the fixture, 38 predicates, 17 engine
refusals all constraints or guards, no engine defect. A slice with every criterion Met and a
recorded wbs omission could not close without a work-item row; the agent's route was the honest
row on the operator's word, and the operator ruled to keep the doctrine and teach it.

**What the runs exercised, exactly.** The engine the runs, beat 32 and the copy's replay ran is
byte-identical to this release's `server/` and `db/` (`git diff` empty). The three skill
sentences above landed AFTER the runs, on the rulings the runs produced; no agent has met them
yet — you are the first.

## 2. The classes — hold, or a feedback row

| # | Probe | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `5.8.1` / `007_handoff.sql` / `7` | in a client process started after the update |
| 2 | `package_verify` before any write | `verified`, `review_current true`, `review_exported_by "5.8.0"` | no write since your last export (`319d8c55`) |
| 3 | `readiness_check("package")` | 23 advisories; `handoff-repeated` passes on `PE-1584` (on the copy: population 19, entities none); `feedback-unanswered` names no row | always |
| 4 | the export after §4's moves | small: on the copy `44 41` lines and 43 KB, longest added line 2,511; `csv/` two files; `review_current true`, `review_exported_by "5.8.1"` | the writes add no node and no edge |
| 5 | the first plain `handoff_emit` | writes nothing but the tool-owned artefacts, and the note changes in no string — on the copy it differed in its path only, because the copy runs outside the project (the feedback rows it names are in the tool's REPORT, not in the note) | no string of the note changed |
| 6 | the first trace line of a session started after the update | it opens `<utc> version=5.8.1` | the process started after the update |
| 7 | **the route test, with the texts you already hold:** quit the client, `claude --resume 5bc5eab5` — the FB-028 session, the one whose context holds the 5.7.0 record (a fresh session lists the new text at once and has nothing to compare) — from a fresh process, `/compact`, then read the first `deferred_tools_record` after the boundary in that session's transcript | `progress_update`'s description reads "`entries` is a list; each entry …" (5.8.0 and 5.8.1 carry the same text: 333 characters) | a client process started after the update, after its first compaction — **the maintainer's prediction from one case (your `5bc5eab5` on 5.7.0 → 5.8.0); a fail is a feedback row and the more valuable result** |

The hook after a compaction printed 24 lines / 2,474 characters on an untouched copy, the trace
line opening `version=5.8.1 source=compact` and ending with the session id. The wire (`tools/list`)
read 387 / 333 / 325 as before.

**Two sentences for your own sessions, measured in the lab and not classes:**
- A `claude -p --resume` turn (or any new client process) is a new MCP server: the package a
  previous turn left open is closed, `package_unlock` reports the holder `not-running`, and the
  removal is the operator's word, journaled. A session that ends with `package_close` leaves
  nothing to unlock (the lab's FB-003, answered by its own runs).
- On Claude Code 2.1.286 the client's first connection sends a `server/discover` request that the
  Python MCP SDK rejects with 31 validation errors on the server's stderr; the connection
  succeeds, later sessions skip the probe. Not a tamheed defect; the vendor's SDK.

## 3. Not built, and said plainly

`server_info` returning the descriptions (R58, re-put and kept by R59). Any engine change without a
lab finding — a recorded family omission read as a deliberate zero at slice or phase scope was put
to the operator and NOT built (R63: the doctrine kept, taught instead). A `/clear` measurement. Any
change to `csv/` or the JSONL. Any migration.

## 4. Your FB-028: the remaining moves

**First read the row back:**

```
entity_query("feedback", ids=["FB-028"], columns=["kind", "title", "lifecycle_status"])
```

Then, resending `kind` and `title` exactly as returned, only the transitions still ahead of
the row (`Confirmed → Reported → Resolved`; a `Reported` row needs the second item only):

```
{"type": "feedback", "id": "FB-028", "kind": ..., "title": ..., "lifecycle_status": "Reported"}
{"type": "feedback", "id": "FB-028", "kind": ..., "title": ..., "lifecycle_status": "Resolved",
 "resolved_in": "5.8.1", "upstream_ref": "tamheed plans 170-174"}
```

Rehearsed on the copy from `Confirmed`: both landed, two `transition` entries were journalled
(`PE-1585`, `PE-1586` on the copy), `feedback-unanswered` named nothing, `handoff-current` counted
the two — so your session's handoff comes AFTER them.

**The answer:** yes, the 5.8.0 condition was wrong in its last clause, and it is corrected on
every site with the date (`docs/install.md` upgrading section and its step 6's second correction,
`docs/design-decisions.md` §22 D-RELOAD-KEEPS-THE-LISTING, the changelog, the 5.8.0 brief); the
route is named above; no engine change, because the record is the client's.

## 5. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
