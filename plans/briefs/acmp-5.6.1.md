# Brief to ACMP — tamheed 5.6.1 (no interlude: it rides with your next ordinary session)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.6.1.md` and execute it; the report is
> `findings_39.md`.* Everything below is a CLASS of result, never the field's counts. A
> prediction names a role ("the latest handoff"), never a row that moves. Where an id, a path or
> a number appears it is either a stable row of yours or the maintainer's own measurement on a
> read-only copy of the package taken by `git archive` at `2cf7ab61`, quoted so you can compare.
>
> **The operator ruled how you take it** (the maintainer's interview, 2026-09-28): at the start
> of your next ordinary session, with FOUR reads and no pre-registration (§1). The report is one
> page. Your mission queue is not held for this release.
>
> **This brief prescribes no store write.** Part B names one sentence by path and line and
> leaves it to the operator's word.
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only.
> Every absence claim below is a claim about tracked files. Your ignored folders were not read.

## 0. Errors owned

**In the 5.6.0 brief, as your findings_38 showed them.** You numbered none. They are errors all
the same.

- **O1** P8 said the first export's diff is one line and a second export is byte-identical. Both
  hold on one UTC date only. You wrote the condition into your own prediction (C5, P8).
- **O3** §2.4 said no script on disk parses a trace line. That was true of the copy, which
  cannot see your ignored `.scratch/`. You found the one parser there (C10).
- **O4** P10 named a process nobody controlled, the maintainer's own session. Your control
  replaced it. Measured since on that session: before its restart it wrote a line with no
  `version=`; a new process in the same folder, 145 seconds earlier, wrote `version=5.6.0`;
  after the restart the same session id wrote `version=5.6.0`.
- **O5** P12 cited "step 5" of a skill whose steps are bold paragraphs. This brief cites a skill
  by its heading text.
- **O6** §0 said "the journal from `PE-1500` on" and named no method. You reached for
  `after_id`, which compares ids as text.

**In the plugin, which you did not report.**

- **O8** Three teaching texts called `entity_query("progress-entry", limit=10)` "the last
  recorded activity": the skill `orient-resume` ("Recent state"), the skill `loop-iteration`
  ("Orient") and the fresh-session paragraph of the follow-up template. `entity_query` returns
  rows in the id's text order and `limit` cuts from the lowest. On your journal that read
  returns the ten lowest ids of 1,540. The line was two months old. Your `after_id` note has
  the same root: the plugin taught that the family is read in number order.
- **O2** Four sentences of the plugin's docs promised the review page's bytes from the store's
  state alone, one of them "no wall clock". The Readiness section has stated its date since
  4.12.0.
- **O7** 5.6.0 made the close-out's last commit unbound by rule, and three skills went on
  calling an unbound commit drift: `integrity-check`, `loop-iteration`, `drift-register`. Your
  handoffs have said since 2026-09-26 that this commit "stays unbound by construction". The
  plugin now says it too.
- **O9** `integrity-check` ran a bare export inside a run that "changes nothing". A bare export
  rewrites the committed page and `csv/`.

## 1. The upgrade, and the four reads

1. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope
   user`, then your reload route.
2. **No migration.** No JSONL rewrite. No tool result gains or loses a key. No string of the
   note changed.

**The four reads**, taken as the session starts its own work:

| # | Read | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `5.6.1` / `007_handoff.sql` / `7` | after the reload |
| 2 | `package_verify` before any write | `verified`, `dirty []`, `review_current true`, `review_exported_by "5.6.0"` | no write since your last export, as at `2cf7ab61` |
| 3 | `git diff --numstat` on the page after the first export | `1 1`: the stamp's line, `5.6.0` to `5.6.1` | no write since the last export AND the same UTC date as that export |
| 3′ | the same | `2 2` | no write since, on a LATER UTC date: the line that holds the Readiness section moves with its date. Your last export was on 2026-09-28. More lines only if a rule that reads the calendar moved a row |
| 3″ | the same | the digest's line and the stamp's line, one freshness line per section, and what was written | a store write came before the export. A write moves the digest, and every section opens with the freshness line, the newest stored timestamp |
| 4 | the first trace line of the session after the reload | it opens `<utc> version=5.6.1` | the process reloaded or started after the update |

After the first export `review_exported_by` reads `5.6.1`.

**Measured on the copy with the shipped engine, for comparison:**

| Probe | Result on the copy |
|---|---|
| The first plain `handoff_emit` | one line of the note differs, in the path and in the clause on where the server is registered; a root `.mcp.json` is written. Both are copy artefacts. On your package the class is `written []` |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; the guide's diff is its title |
| The first export, on 2026-09-28 | `1 1`, the stamp's line; the digest unchanged; the page's size unchanged; 30 rows in the Approved fold, the ten marked equal the note's roster |
| A second export | byte-identical |
| `export_html(output=<a path outside the package>)` | the package's page unchanged |
| `entity_query("progress-entry", limit=10)` | the ten lowest ids in text order; none of them among the resume block's `last_entries` |
| The hook after a compaction | the latest handoff whole, WITH its `Corrections` line: your latest handoff carries one correction. A fresh handoff removes the line |
| `readiness_check("package")` | blocking `acs-met`, `adrs-approved`; `handoff-current` passes |

## 2. What changed in the skills you invoke

Cited by heading text. No step order changed.

| Skill | Where | Now says |
|---|---|---|
| `package-writes` | "Read the store through the tools, at any size" | rows come in the id's text order; `limit` cuts from the lowest; a typed `after_id` is compared as text; what to read instead |
| `package-writes` | "Cross-check git against the package by classifying, never by counting" | the close-out's last commit is unbound by rule |
| `session-handoff` | "The rules" | the handoff says what is true when it is written; its commit, the bind and the export are named as following |
| `orient-resume` | the step on lessons, feedback and recent state | the resume block's `last_entries`, `handoff-current`'s list read with `ids`, `audit_evidence` |
| `integrity-check` | "Check staleness" | the export goes to a path outside the repository |
| `integrity-check`, `loop-iteration`, `drift-register` | the git cross-check | unreferenced commits are classified; a package-write commit is not drift |

**What the tools do NOT give, said plainly.** No tool returns the newest rows of a family.
The resume block names the three newest journal entries. `handoff_behind` is a count.
`handoff-current` names the work entries after the latest handoff, up to 50. For the verdicts
there are `audit_evidence`'s three counts with the narrated and the ungraded ids, and
`acs-met`'s list. The operator ruled that no parameter is built for it this release. If you
need one, it is a feedback row.

## 3. Part B — one sentence, on the operator's word

The sweep read 102 tracked files a session reads before acting, and the decisions from
`DEC-230`, the journal from `PE-1500` (its ids read as numbers from the data file of the copy)
and the live lessons. Five words: a limited read, the newest rows, `after_id`, "unbound", the
page's bytes. 33 hits, every one read.

| Hits | Where | Disposition |
|---|---|---|
| 1 | `AGENTS.md:13`: "`gate_run()` + `readiness_check(scope)` + the latest `progress-entry` rows" | **the one sentence.** It names no method, so it is not false. It came from the plugin's template, which now names the block's `last_entries`. Whether it is reworded is the operator's |
| 4 | "the latest `handoff` journal entry (the `resume` block)" in two memory files and twice in your kickoff prompt | read and left: true |
| 3 | `after_id` in one memory file, the guide and one lesson | read and left: each says it pages, which it does |
| 5 | "unbound" in your handoff-last memory, `DEC-236` and two handoffs | read and left: each says the rule 5.6.1 now states |
| 19 | "byte-identical" and "wall clock" | read and left: none speaks of the review page |
| 1 | a decision's "last recorded recurrence" | read and left: not the journal |

## 4. `findings_39` — what to report, each with its instrument

| Question | Instrument |
|---|---|
| Did the four reads hold? | the four results, as read |
| Which shape did the first export's diff take? | `git diff --numstat` on the page, with the UTC date of your last export beside it |
| Did a session of yours ever read the lowest journal ids as recent state? | your transcripts' `entity_query` calls. The maintainer's count over the 673 transcript files of your project on this machine, 2026-08-29 to 2026-09-28, is 1,335 calls and none such. Older transcripts are not on disk |
| Do your ignored folders hold a script or a note that reads the journal by `limit`, or by a typed `after_id`? | a search of those folders. The maintainer could not read them |
| Any brief error, numbered E1… | any wrong class above is a finding, not a paraphrase |
