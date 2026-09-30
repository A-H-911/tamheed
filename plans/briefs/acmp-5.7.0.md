# Brief to ACMP — tamheed 5.7.0 (no interlude, and no report unless a class fails)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.7.0.md` and execute it; write no
> report unless a class fails.* Everything below is a CLASS of result, never the field's counts.
> Where an id, a path or a number appears it is either a stable row of yours or the maintainer's
> own measurement on a read-only copy of the package taken by `git archive` at `24e59125`,
> quoted so you can compare.
>
> **The operator ruled how you take it, and that this is the last brief of its kind**
> (the maintainer's interview, 2026-09-28). You check the classes at the start of your next
> ordinary session. **You write no findings file.** If a class fails, the failure is a feedback
> row in your package (§5). Later releases reach you as ordinary updates with the changelog.
> Your mission queue is not held for this release.
>
> **This brief prescribes no store write.**
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only.
> Every absence claim below is a claim about tracked files. Your ignored folders were not read.

## 0. Errors owned

**In the 5.6.1 brief, as your findings_39 showed them.** You numbered none. They are errors all
the same.

- **O10** The row on `export_html(output=<a path outside the package>)` said the package's page
  stays unchanged and left out that a `csv/` folder is written beside the output. You noted it.

**In the plugin and in the maintainer's own work, which you did not report.**

- **O13** 5.6.1's changelog said its order rule stands "in the tool's description". It stood in
  `entity_query`'s docstring. The server registers a separate one-line text as each tool's
  description, and has since its first commit. **No client receives a docstring as a
  description.** Your 5.6.1 session met the rule through `package-writes` and the template,
  which is how `DEC-237` took its clause. It could have met the docstring only by opening the
  server's file, as one of your memory files once did.
- **O11** The maintainer's census for 5.6.1 counted any read that carried `after_id` as a safe
  read. Your census looked inside the class and found the read of 2026-09-11.
- **O12** 5.6.1 left `after_id` to teaching and recorded number order in the tool as rejected.
  One round later your census showed a read of 2026-09-11 that had dropped rows in silence.
  The review page had held the rule since
  4.8.0.
- **O14** The plugin's front door named the journal's keys as "event_type/subject/actor". The
  key is `subject_id`. Until 5.7.0 the engine dropped a key sent under a wrong name.
- **O16** In this round's own records the maintainer wrote that the docstring's sentence
  "reached no session". That is more than anyone can know. It was narrowed to what is shown:
  no client received it as a description.

## 1. The upgrade, and what a session meets

1. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope
   user`, then your reload route.
2. **No migration.** No JSONL rewrite. `schema_version` stays 7. The canonical JSONL, the CSV
   and the review page keep their order.

**What changes in a tool result.** Two things, and only these:

| Tool | Before | From 5.7.0 |
|---|---|---|
| `entity_query` | rows in the id's text order; `after_id` compared ids as text | rows by prefix, then by the id's first number, then by id: the review page's order. `after_id` returns the rows AFTER an id by that order. You may type the id, and it need not name a row. The cut excludes the id itself |
| `progress_update`, `audit_record` | a key outside the tool's list was dropped in silence; a missing `entry` came back as the database's raw text | the batch is refused by name, with the keys the tool takes, and nothing is written. A null optional key means an absent one |

**The ceiling, said plainly.** Only an id's FIRST number counts. What follows it orders as text.
Your work items are the one family this touches: 221 of 261 ids carry a dotted tail, and under
one leading number the tenth part still comes before the second. The page has always ordered
them so. `limit` still cuts from the lowest, so a limited read never returns the newest rows,
and the clause `DEC-237` put in `AGENTS.md:13` stays true.

**The classes:**

| # | Read | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `5.7.0` / `007_handoff.sql` / `7` | after the reload |
| 2 | `package_verify` before any write | `verified`, `dirty []`, `review_current true`, `review_exported_by "5.6.1"` | no write since your last export, as at `24e59125` |
| 3 | `git diff --numstat` on the page after the first export | `2 2`: the stamp's line and the line that holds the Readiness section, which moves with the date it states | no write since the last export, on a UTC date LATER than that export. Your last export was on 2026-09-28. That one line holds the whole section, so a rule that reads the calendar changes it in more than the date; the count stays `2 2` |
| 3′ | the same | `1 1` | no write since, on the SAME UTC date |
| 3″ | the same | the digest's line and the stamp's line, one freshness line per section, and what was written | a store write came before the export |
| 4 | any other line of the page | unchanged | always: the page held the id order already |
| 5 | an unlimited read of the journal | its last row carries the highest number | always. On 5.6.1 it ended at `PE-999` |
| 6 | `entity_query("progress-entry", limit=10)` | the ten lowest numbers | always |
| 7 | `entity_query` with a typed `after_id` | the rows after that id by number | always |
| 8 | `progress_update` with a key it does not take | `ok false`; the message names the key and the seven keys the tool takes; no row written | always |
| 9 | the descriptions of `entity_query`, `progress_update`, `audit_record` | each states its rule or names its keys | after the reload. **Instrument: the tool's description as your client lists it**, never the server's file |
| 9, corrected 2026-09-30 (v5.8.0, your FB-026) | the same three descriptions | the same | **in a context that loaded the tools after the update: a new session, `/clear` or a compaction.** A `--resume` keeps the text the session recorded before the update; the wire and a fresh client read the new text. Measured on 2,122 transcripts (`docs/install.md`, 5.8.0). The condition "after the reload" was the maintainer's error (O18); classes 1 and 10 are true as written |
| 10 | the first trace line of the session after the reload | it opens `<utc> version=5.7.0` | the process reloaded or started after the update |

**Measured on the copy with the shipped engine, for comparison:**

| Probe | Result on the copy |
|---|---|
| Your read of 2026-09-11, as you typed it (`search "handoff_emit"`, `after_id "PE-950"`, `limit 3`) | `PE-954`, `PE-997`, `PE-1033` |
| Every `after_id` call in your transcripts, 86 of them, run through the engine | each equals an independent cut by number, written in Python over the same filtered set |
| A full walk of the journal at `limit=100` | 1,546 rows in 16 pages, complete and in order. 6 ms; 1 ms on 5.6.1 |
| Families whose order differs from before | two of 27: the journal and the work items |
| The first plain `handoff_emit` | one line of the note differs, in the path; a root `.mcp.json` is written. Both are copy artefacts. On your package the class is `written []` |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; the guide's diff is its title |
| The first export, on 2026-09-29 | `2 2`; the date line changed in its stated date and nowhere else; the digest and the page's size unchanged; 29 CSV files unchanged; 30 rows in the Approved fold, the ten marked equal the note's roster |
| A second export | byte-identical |
| `export_html(output=<a path outside the package>)` | the page written there with `csv/` beside it, 29 files of the same names as the package's; the package's page unchanged |
| The hook after a compaction | the latest handoff whole, with NO `Corrections` line: your latest handoff carries no correction |
| `readiness_check("package")` | blocking `acs-met`, `adrs-approved`; `handoff-current` passes |

## 2. What changed in the skills you invoke

Cited by heading text. No step order changed.

| Skill | Where | Now says |
|---|---|---|
| `package-writes` | "Read the store through the tools, at any size" | rows come in id order by number; what `after_id` returns; the ceiling; the keys the two journal tools take, and that any other is refused |
| `orient-resume` | the step on lessons, feedback and recent state | "id order, and `limit` cuts from the lowest" in place of "the id's text order" |
| `integrity-check` | "Check staleness" | the export writes `csv/` beside the page at any `output` |
| `measurement-evidence` | "Is it the RIGHT subject?" | a census over a store that something else prunes names its horizon |
| the front door | "Update cycles" | the journal's keys by their exact names |

## 3. One dependency of yours the maintainer read in part

Three tracked generators read `entity_export` files through `scripts/lib/package-export.mjs`:
`scripts/gen-record-slate.mjs`, `scripts/gen-slice-review-slate.mjs` and
`scripts/gen-dw-disposition-slate.mjs`. The reader's own comment says four; three import it
at `24e59125`. An export of the
journal or of the work items taken on 5.7.0 lists its rows in the new order.

**What the maintainer read, and its limit.** The lines of those files that walk rows, found by
a search, not the files whole. By those lines the generators key rows by id and sort with their
own numeric comparator, and the one that walks in file order reads deferred work, whose order
does not move. No line indexes a row by position.

**Instrument, if you want the answer:** your own `scripts/test-gen-slice-review-slate.py`, and
the diff of a slate regenerated from a fresh export.

## 4. Part B — no sentence to reword

The sweep read 108 tracked files a session reads before acting, your generators and their
two library files among them, and the decisions from `DEC-230`, the journal from `PE-1500` and the live lessons. Five
words: text order, `after_id`, the journal's keys beside `progress_update`, the tool's
description or a docstring, a row read by position. Nine hits, every one read.

| Hits | Where | Disposition |
|---|---|---|
| 1 | `DEC-237`, its rationale: "the id's text order" | read and left: an Approved row's history, true when written. Its clause in `AGENTS.md:13` stays true |
| 1 | a memory file's quoted sentence on ids sorted as text | read and left: you marked it corrected on 2026-09-21 |
| 1 | "as text" in a memory file on minutes | read and left: not the store |
| 5 | `after_id` in a memory file, the guide, a lesson and twice in `PE-1541` | read and left: each says it pages, or records your census |
| 1 | a memory file that quotes a docstring of the server | read and left: it cites the server's file, which is what it read |

## 5. If a class fails

A wrong class above is a finding. Record it as the engine lets a feedback row be recorded:

1. Write the row `Proposed`, kind `defect` or `question`, naming the class by its number here,
   what you read, and the instrument.
2. It leaves the package only on the operator's word: `Confirmed`, with `operator_confirm` and
   `confirmed_by` on that write.
3. `Reported` when the operator hands it to the maintainer. `Resolved` when it is answered.

Nothing else is asked. If every class holds, this brief leaves no trace in your package.
