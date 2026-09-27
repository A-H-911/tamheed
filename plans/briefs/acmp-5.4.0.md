# Brief to ACMP — tamheed 5.4.0 (Interlude 12)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line: *read
> `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.4.0.md` and execute it; the report is
> `findings_36.md`.* Everything below is a CLASS of result, never the field's counts. A prediction
> names a role ("the latest handoff"), never a row that moves. Where an id or a number appears it is
> either a stable row of yours or the maintainer's own measurement on a read-only copy of the package
> taken from `3071f1f4`, quoted so you can compare, not so you can carry it.
>
> **Every recipe in §2 was executed on that copy before this file was written.** The 5.3.0 brief's
> trim recipe was not, and it could not run.

## 0. Errors owned

**The 5.3.0 brief's, as you found them.**

- **E1** "trim those thirteen lines, a `substitute` each": the nine lessons were Approved, and an
  approved lesson is immutable. Measured on the copy now: `substitute` on an Approved lesson's
  `statement` returns `approved/promoted lessons are immutable: supersede, never edit`.
- **E2** the brief named no live sentence a trim would falsify.
- **E3** Q1 cannot be measured where the note names the skills. Q1 is retired (§2.3).
- **E4** P8 named a handoff by id although the brief's own close-out order writes a new one first.

**The maintainer's own, which you did not report.**

- **E5** P3 said "a `substitute` status flip reads `pinned` from the stored row". A lesson cannot be
  approved by a `substitute` at all. Measured on the copy, both refused by name:
  - a substitute alone: `attribution lands WITH approval — confirmed_by can never be added later;
    set it on this write`;
  - a substitute with `confirmed_by` beside it: `a substitute item carries only type, id, substitute,
    operator_confirm and expect_unchanged`.

  The approval is a full row, which is the recipe you used in Interlude 10. `package-writes` §1 now
  says so.
- **D1** `install.md` and the 5.3.0 CHANGELOG entry said a reload had delivered the resume block on
  5.1.0. It was a Claude Code restart. The evidence, from your own session's transcript
  (`d37475be…`): the `/reload-plugins` row at `2026-09-26T11:29:18.881Z` carries build `2.1.282`;
  the `SessionStart:resume` attachment at `11:29:55.524Z` is that session's first row on `2.1.283`.
  **Asked of you:** confirm or refute it with your own transcript method, and if it holds record a
  dated correction beside `findings_33.md:85` and the lines of `findings_34.md` that lean on it.
- **D2** `install.md` told the reader that a trace line with no block in context means "fired, not
  delivered". It gave no way to know whose line it was. That sentence is what your `PE-1501` repeated.
- **Two counts in the maintainer's interview** were wrong: five headless sessions (six), four
  reloads (24 once every transcript was read). No ruling depended on either.

## 1. The upgrade (part A; no interview needed)

1. Baseline as before: commit the package; `package_close()`; keep `gate_run()`,
   `readiness_check("package")`, `package_verify()` and `server_info()` outputs.
2. **The trace stays as you have it** (`DEC-233` d4). Nothing to create. Note the time before and
   after each operator event, as you did.
3. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope user`,
   then your reload route. **Check the installed tree against the tag** with your own recipe: on
   LF-normalised bytes, run-time folders left out. It is in `install.md` now.
4. **No migration.** `server_info` reads `5.4.0`, `migrations_head 007_handoff.sql`,
   `schema_version 7`. No JSONL rewrite: the digest is unchanged across the upgrade.

### Predicted classes (each measured on the copy with the shipped engine)

| # | Probe | Class |
|---|---|---|
| P0 | `server_info` after the reload | `5.4.0` / `007_handoff.sql` / `7`; checked first |
| P1 | `package_open` → `resume` | the latest handoff, with the ids of its corrections listed; `handoff_behind 0` while nothing was journalled after it; `open_feedback []`; `skill tamheed:package-writes`; `lock` `observed "alive"`, `evidence "held by this session"`; `server_info` while open says the same |
| P2 | the reload and the hook | **no trace line carrying YOUR session's id inside the reload's window.** Any line there is another session's: a different id, or no `session=` tail at all if that session ran the 5.3.0 hook before the update landed. The maintainer measured 24 reloads in your transcripts, builds 2.1.261 to 2.1.283: none ran a `SessionStart` hook of any plugin; each of 19 compactions did |
| P3 | the hook after `/compact` | the latest handoff whole; one trace line whose `lines=`/`chars=` equal the block's and whose tail is ` session=<id>`, the id being the file name of your session's transcript. A headless session started in the window writes its own line with its own id |
| P4 | plain `handoff_emit` | every scan empty; no `skill` key; both `CLAUDE.md` files `unchanged` on the real package (the copy rebuilt the note once, a copy artefact: its path line differs); `diverged_stale_stock [{prompts/README.md, matches 5.3.0}]` and its STALE-STOCK warning |
| P5 | `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; the guide's title is its only changed line; the note NOT rebuilt |
| P6 | `readiness_check("package")` | the blocking classes of your baseline, unchanged. **`lessons-confirmed` fails (advisory) while a lesson is Proposed.** Your Interlude 11 baseline had none; you now have one. The upgrade does not cause it |
| P7 | any `entity_query` | `skill: "tamheed:reading-the-record"` on every successful result, `count: 0` included. An error result carries no `skill` key: measured on the copy with an unknown type |
| P8 | a lesson approval, if one is ruled | a full row; `changed_columns` are `lifecycle_status`, `confirmed_by`, `confirmed_at`; a `lesson_audit` journal id; `next` ends `; it renders in the note only if pinned or among the 10 newest unpinned Approved rows - pin it to keep it visible` for an unpinned row |
| P9 | `export_html`, `entity_export` | nothing new; `review.html` renders no lock, by design |
| P10 | the skills the cues load | from the `5.4.0` folder. `operator-interview` step 3 recommends by default and step 6 carries the standing-instruction rule; `measurement-evidence` §3 and §4 each end with a new bullet; `package-writes` §1 names the approval as a full row |

`DEC-233` d1 asks more than the skill does: your options are also checked with the advisor. That part
is your project's rule and stays yours.

### Feedback dispositions

None to move. No row was Reported this round.

## 2. Part B — ACMP-side, on the operator's word

1. **`LL-112`.** Its generic core is in `measurement-evidence` §4 now; the names of the tools that
   start headless sessions stay the project's. The options are the operator's, put your way:
   - approve it as written;
   - edit, then approve. While it is Proposed the text can still move. Measured on the copy: a
     `substitute` on `recommendation` succeeds and `changed_columns` names that column alone. Its
     first recommendation (attribute by transcript timestamps) has a shorter instrument now: read
     the line's `session=`. After approval the same edit is refused;
   - leave it Proposed.
2. **Live sentences the upgrade falsifies**, by path and line at `3071f1f4`. Fix the file, not the
   pointer (`written-claims` step 7):

   | Where | Sentence | Why it goes false |
   |---|---|---|
   | `.claude/memory/hook-trace.md:15` | "and **no session id**" | the line ends `session=<id>` |
   | `.claude/memory/hook-trace.md:18` | "every Claude Code session in EVERY project appends a line while tamheed 5.3.0+ is the user-scope install" | false today, before the upgrade: the plugin is disabled in the user settings and enabled by this project's `.claude/settings.json`. The maintainer ran a headless session in a folder that does not enable it; no line was written |
   | `.claude/memory/MEMORY.md:48` | the pointer line repeats both | the same |

   Still true, and now second to the tail: `hook-trace.md:25`, attribute by the transcripts. It
   stays the cross-check.
3. **Q1 is retired.** The latest handoff that carries the OWED line about a Q1 addendum (`PE-1506` at
   `3071f1f4`) can be corrected by a `correction` entry naming it, on the operator's word. Measured
   on the copy: `handoff-current` stays `pass`, and the resume block and the hook list the new
   correction's id beside the others.
4. **The thirteen index lines**: ruled KEEP. Nothing to do.
5. **The close-out order** stands: status moves → the handoff LAST → commit `data/` → `work_bind`
   that commit.

## 3. `findings_36` — what to measure

- The reload's window in the trace: is there a line with your session's id? (P2)
- The tail after `/compact`, and after a restart if one happens: is it the same id both times, and
  is it your transcript's file name?
- D1: your own reading of the 2026-09-26 11:29Z window.
- P8, on an approval made for the project's own reasons — not one made to see the hint.
- The hook after a process restart with a stale lock, if one occurs naturally.
- Any brief error, numbered E1… as before; any wrong class above is a finding, not a paraphrase.
