# Brief to ACMP — tamheed 5.8.0 (your FB-026 and FB-027 answered; no report unless a class fails)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.8.0.md` and execute it; write no
> report unless a class fails.* Everything below is a CLASS of result, never the field's counts.
> Where an id, a path or a number appears it is either a stable row of yours or the maintainer's
> own measurement on a read-only copy of the package taken by `git archive` at `d47d9938`,
> quoted so you can compare.
>
> **As the operator ruled for 5.7.0 (R53), this brief asks for no report.** You take the release
> at the start of your next ordinary session, check the classes, and write a feedback row only
> for a class that fails. Your mission queue is not held.
>
> **This brief prescribes two store writes and no other:** the two feedback rows it answers move
> to `Reported` and then to `Resolved` (§4). Both moves are bookkeeping inside the bound set and
> need no operator word; the maintainer rehearsed them on the copy with the exact rows below.
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only.
> Every absence claim below is a claim about tracked files. Your ignored folders were not read.

## 0. Errors owned

- **O18** The 5.7.0 brief's class 9 said the three descriptions show "after the reload". Your
  FB-026 measured that a session resumed after the update lists the text it recorded before it.
  The maintainer had never measured a resumed session, while the maintainer's own session held
  such a record. The condition is corrected beside the sentence, in the brief, the install
  guide, the design record and the changelog (§1).
- **O19** One cycle earlier the maintainer declined a design-record note on the review page's
  weight, on your `DEC-236` d4 ("not a cost today"). Your `DEF-224` measured the cost the next
  day. The cost was the maintainer's: the page's line structure (§1).
- **O20** The 5.7.0 brief's section 3, the check of your four generators, was optional. You did
  not run it, and it stays unverified. Nothing in 5.8.0 touches an `entity_export` file.

## 1. The upgrade, and what a session meets

1. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope
   user`, then your reload route.
2. **No migration.** No JSONL rewrite. `schema_version` stays 7. The canonical JSONL and the
   CSV keep their bytes.

**What changes.** Three things:

| Surface | Before | From 5.8.0 |
|---|---|---|
| `readiness_check("package")` | 22 advisories on your package | 23: **`handoff-repeated`**, emitted once the journal holds three handoffs. It names, by line number, the lines of the LATEST handoff that stood word for word (whitespace collapsed) through three handoffs in a row, with the handoff each first stood in. Headings (ending `:`) and lines under 20 characters are not read. No line's text reaches the output. Replayed over your 18 handoffs it names the 13-verdicts line at `PE-1506`, `PE-1519` and `PE-1542`, and the WBS-40.19/DEF-211/MTG-2026-061 line at `PE-1519` and `PE-1562`; on `PE-1577` it passes. It reads wording, never truth: a reworded line resets it |
| `review.html` | every table and both graphs on single lines (four lines of 840–912 KB) | **each table row and each graph element on its own line.** The rendered page is the same |
| The registered descriptions of `progress_update` and `audit_record` | "Each item is an object …" | "`entries` is a list; each entry …" / "`verdicts` is a list; each verdict …" — one of your calls had sent `items` |

**The corrected condition for a description (your FB-026).** A client shows a new description
in a context that loaded the tool AFTER the update: a new session, `/clear`, or a compaction. A
`--resume` keeps the text the session recorded. The maintainer measured it on 2,122 transcripts:
Claude Code writes a `deferred_tools_record` when a tool is first loaded; a loaded tool was
recorded again 936 times after a compaction and 5 times without one; 100 re-selects of an
already-recorded tool in the same context, 12 of them after a `--resume`, re-recorded it 0
times. The vendor's docs state nothing on this; a newer build than 2.1.283 may differ. The wire
(`tools/list`) and a fresh `claude -p` always show the server's current text, as your own
controls did.

> **Corrected 2026-10-01 (5.8.1, your FB-028): "or a compaction" was wrong.** A compaction
> re-records the listing the client process built when it started; `/reload-plugins` restarted
> the server and the hooks and left that listing (your session, 2.1.284 on the rows). The
> new text shows in a client process started after the update: a new session, or
> `claude --resume` from a fresh process followed by a compaction. The 5.8.1 brief states the
> route and the counts; `docs/install.md` carries the correction beside the 5.8.0 one.

**The page, and your history scan (your `DEF-224`, `ADR-0052`).** Each export used to add about
4 MB of patch text, because the lines that moved were the long ones; gitleaks reads `git log -p`.
From 5.8.0 the next export after a journal write adds kilobytes. Your past page versions stay in
history — 5.8.0 rewrites nothing — so `ADR-0052`'s skip of the page's past versions keeps its
reason for the history already written, and nothing in 5.8.0 asks you to change it. Tamheed
recommends no narrowing; the install guide reports your route as your decision.

## 2. The classes — hold, or a feedback row

| # | Probe | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `5.8.0` / `007_handoff.sql` / `7` | after the reload |
| 2 | `package_verify` before any write | `verified`, `review_current true`, `review_exported_by "5.7.0"` | no write since your last export |
| 3 | `readiness_check("package")` | `handoff-repeated` present, advisory. On `PE-1577` it PASSES with no entity. On a later handoff a fail names only lines that stood word for word through three handoffs, by line number, with the handoff each first stood in, and never a line's text | always |
| 4 | **the first `export_html`** | the page re-flows once: on the copy `git diff --numstat` read `26396 2006` and the patch 20.2 MB; `csv/` unchanged; `package_verify` then reads `review_current true`, `review_exported_by "5.8.0"`. Every `<tr id=` starts a line; no line holds two `</tr>` or two `<path` | the first export on 5.8.0 |
| 5 | the same store rendered by 5.7.0 and by 5.8.0, same date | equal once the newlines between tags are removed and the stamp replaced (the maintainer's `bytecheck.py`; also equal in a browser: elements, rows, paths, text, height, pixels) | always |
| 6 | the next export after a journal write | small: on the copy `20 17` lines and 34 KB after one note; `63 51` lines and 63 KB after the two feedback rows' four transitions and a note | the writes add no node and no edge to the connected graph; a write that does re-emits both graphs (every position moves), about 1.3 MB on your `3a6dd21b` |
| 7 | the three descriptions, read in a context that loaded the tools after the update (a new session, `/clear` or a compaction), or on the wire — **read false on 2026-09-30 after a reload and a compaction in one process (your FB-028); corrected 2026-10-01: a client process started after the update** | `entity_query` as 5.7.0 wrote it (387 characters); `progress_update` names `entries` (333); `audit_record` names `verdicts` (325) | a context that loaded the tools after the update |
| 8 | the first plain `handoff_emit` | writes nothing but the tool-owned artefacts, and the note changes in no string — on the copy the note differed in its path and its install-mode sentence only, because the copy runs outside the plugin | no string of the note changed |
| 9 | the first trace line of the session after the reload | it opens `<utc> version=5.8.0` | the process reloaded or started after the update |

The hook after a compaction printed 29 lines / 2,723 characters on an untouched copy, the trace
line opening `version=5.8.0 source=compact` and ending with the session id.

## 3. Not built, and said plainly

A carried count in the hook or the resume block. Any normalisation of the mark's wording. A
`newest` read. A smaller page or a stable graph geometry. `server_info` returning the
descriptions. Any change to `csv/` or the JSONL. Any migration. The valid set in `unknown
columns` (R52 stands; two more refusals since 5.7.0 were read). The other sixteen one-liners
(R55 stands; `handoff_emit`'s still reads "Emit handoff prompts" though since 3.0.0 it writes the
note, the package's prompt library and a standalone `.mcp.json`).

## 4. Your two feedback rows: the moves

The maintainer answered both. Each moves `Confirmed → Reported → Resolved` in one session, no
operator word, as PARTIAL rows carrying the NOT NULL columns (`id`, `kind`, `title`,
`lifecycle_status`). Rehearsed on the copy: both landed, four `transition` entries were
journalled, `feedback-unanswered` named neither afterwards, and `handoff-current` counted the
four — so your session's handoff comes AFTER them.

**First read the two rows back, then resend `kind` and `title` exactly as returned** — a
changed `kind` or `title` on a confirmed row is refused as drift, never dropped:

```
entity_query("feedback", ids=["FB-026", "FB-027"], columns=["kind", "title"])
```

Then, for `FB-026`, two `entity_upsert` items in turn — `kind` and `title` being the values
that read returned, not a placeholder:

```
{"type": "feedback", "id": "FB-026", "kind": ..., "title": ..., "lifecycle_status": "Reported"}
{"type": "feedback", "id": "FB-026", "kind": ..., "title": ..., "lifecycle_status": "Resolved",
 "resolved_in": "5.8.0", "upstream_ref": "tamheed plans 165-169"}
```

The same two items for `FB-027`. **The answers:**

- **FB-026** (should class 9 read "in a client that loaded the tools after the update"?): yes,
  and that is now the condition, with the measurement behind it (§1). No engine change: the
  record is the client's.
- **FB-027** (should a carried line name its source and date, and should something flag a line
  carried unchanged past N handoffs?): both. `handoff-repeated` is the flag (N = 3 handoffs,
  measured on your journal); `tamheed:session-handoff` now says a carried line names its source
  and the date last measured, that the mark lasts one handoff, and that a line the rule names is
  re-measured against its source and the rulings given since — never reworded to clear the rule.
  Your `LL-005` sweep stays the remedy the rule points at.

## 5. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
