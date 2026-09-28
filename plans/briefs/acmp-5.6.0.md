# Brief to ACMP — tamheed 5.6.0 (Interlude 14)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line: *read
> `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.6.0.md` and execute it; the report is
> `findings_38.md`.* Everything below is a CLASS of result, never the field's counts. A prediction
> names a role ("the latest handoff"), never a row that moves. Where an id, a path or a number
> appears it is either a stable row of yours or the maintainer's own measurement on a read-only copy
> of the package taken by `git archive` at `66ad54c4`, quoted so you can compare.
>
> **Every class below that depends on your state names its condition.** The 5.5.0 brief's ninth
> class did not, and its own close-out order made it impossible. **Every question names the
> instrument that can answer it.** The 5.5.0 brief asked one that no instrument could.
>
> **This brief prescribes no store write.** Part B names files by path and line and leaves each to
> the operator's word.

## 0. Errors owned

**The 5.5.0 brief's, as you found them.**

- **E1** the sweep missed two live sentences in the old sense. It had two causes. It matched five
  phrasings instead of the word, so a memory line that negated the verb passed. And its families
  were memory, decisions, journal, lessons and both `CLAUDE.md`, so the kickoff prompt was never
  opened. This brief's sweep is by word, every hit read, over 102 files a session reads before
  acting — your memory files, your project skills, the package's prompts, both `CLAUDE.md`,
  `AGENTS.md` — and over the decisions, the journal from `PE-1500` on and the live lessons.
- **E2** P9 promised the hook block "with its `Corrections` line". §2.4 of the same brief writes a
  fresh handoff before the compaction. You predicted the opposite and it held.
- **The §3 question** asked whether a session started before the upgrade writes a line only after
  a reload. The hook had not changed between the tags and the line named no version. 5.6.0 builds
  the instrument (§1).
- **Your fourth control** for the 03:22:45Z line is the one whose counts equal it. The brief held
  three.

**The maintainer's own, which you did not report.**

- **Four of the plugin's step lists exported the review page before their last journal write.**
  `session-handoff` said to write the handoff after `export_html`. `phase-close`,
  `release-close-out` and `skill-promote` each exported before a closing write. Your own
  `write-the-handoff-last.md:22` carries the same order, and your practice has already left it:
  your page is refreshed after the binds. See §2.2.
- **"The field did not complain" about the page's weight.** The maintainer put that sentence to the
  operator in an option, and the operator ruled that the weight is not studied this release. Your
  `ph5-aws-deployment.md:42` records pushes timing out and names the page as the cause, at 3 MB.
  The maintainer had not swept your memory before asking. The question was put again with your
  line quoted, and the operator ruled that the ruling stands for 5.6.0 and that you are asked to
  measure. See §2.5.
- **"The advisor is unavailable in this session"**, written into the maintainer's plan after one
  failed call. A second call answered.

## 1. The upgrade (part A; no interview needed)

1. Baseline as before: commit the package; `package_close()`; keep `gate_run()`,
   `readiness_check("package")`, `package_verify()` and `server_info()` outputs.
2. The trace stays as you have it.
3. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope user`,
   then your reload route. Check the installed tree against the tag with your own recipe.
4. **No migration.** `server_info` reads `5.6.0`, `migrations_head 007_handoff.sql`,
   `schema_version 7`. No JSONL rewrite: the digest is unchanged across the upgrade.

**What a reader of a log line or a tool result sees change.** Anything of yours that quotes the
old form is a dated record, not an error.

| Surface | Before | After |
|---|---|---|
| The trace line | `<utc> source=… lines=N chars=N status=… session=<id>` | `<utc> version=<x> source=… lines=N chars=N status=… session=<id>` |
| `package_verify` | `review_current` | the same, plus `review_exported_by` |
| The review page's head | the digest stamp | the same, then `<meta name="tamheed-version" content="<x>">` |
| Three ceremonies' step order | the export before the last write | the export after it (§2.2) |

The version sits after the timestamp and not at the end, where a new key usually goes. The tail
is the instrument your memory teaches, so it was kept. A script that takes `source=` by position
breaks; one that reads by key does not.

### Predicted classes (each measured on the copy with the shipped engine)

| # | Probe | Class | Holds when |
|---|---|---|---|
| P0 | `server_info` after the reload | `5.6.0` / `007_handoff.sql` / `7`; checked first | always |
| P1 | `package_open` → `resume` | the latest handoff; `handoff_behind 0`; `open_feedback []`; `skill tamheed:package-writes`; `lock` `observed "alive"`, `evidence "held by this session"` | nothing work-done or transition was journalled after the handoff. Its corrections are listed only if one was written; at `66ad54c4` there is none |
| P2 | `package_verify` before any write | `verified`, `dirty []`, the digest of your baseline, `review_current true`, **`review_exported_by null`** | the page was exported after the last write, as it was at `66ad54c4` |
| P3 | the reload and the hook | no trace line carrying YOUR session's id inside the reload's window | always, on the builds measured |
| P4 | the first plain `handoff_emit` | **`written []`.** No string of the note changed in 5.6.0. `diverged_stale_stock [{prompts/README.md, matches 5.5.0}]` with its STALE-STOCK warning; every scan empty; no `skill` key | the note on disk is the one 5.5.0 emitted. On the copy the emit wrote the note and a `.mcp.json`: one line differed, in the path and in the clause on where the server is registered, both copy artefacts |
| P5 | `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`, `written []`. The guide's diff is one line out and one in: its title | the guide was never customised |
| P6 | `readiness_check("package")` | the blocking classes of your baseline, unchanged | always |
| P7 | any `entity_query` | `skill: "tamheed:reading-the-record"` on every successful result, `count: 0` included. An error result carries no `skill` key | always |
| P8 | the first `export_html` | **the page is rewritten although no data moved.** Its diff is one line added, the version stamp. The digest is unchanged. `review_exported_by` reads `5.6.0`; `review_current` reads true before and after. A second export is byte-identical | no write happened since the last export. After a write the diff also carries that write |
| P9 | the hook after `/compact` | the latest handoff whole; one trace line whose counts equal the block and whose tail is your session's id. **The line opens `<utc> version=5.6.0`** | the session reloaded or restarted after the update. A `Corrections` line prints only when the latest handoff has a correction |
| P10 | a trace line with no `version=` | it was written by a hook older than 5.6.0. Both shapes are correct | a session that has not reloaded since the update wrote it. One such process was observed on the machine in Interlude 13: the maintainer's own session, which you did not reload |
| P11 | any journal write after an export | `review_current false`, `review_exported_by` unchanged; the next export turns the first true | always |
| P12 | the skills the cues load | from the `5.6.0` folder: `package-writes` §4 has the bullet on the review page; `session-handoff` exports after the bind and has the carried-line bullet; `phase-close` step 7, `release-close-out` steps 6 to 8 and `skill-promote` steps 6 to 7 export after their last write; `progress-sync` step 8 points at the rule; `written-claims` step 5 has the bullet on a ruling that changes a word | always |
| P13 | a lesson approval | the 5.5.0 hint, unchanged | only when a lesson is ruled for the project's own reasons. Two rounds say none will be |

### Feedback dispositions

None to move. No row was Reported this round.

## 2. Part B — ACMP-side, on the operator's word

1. **Your `hook-trace.md:14-15`** states the line's shape "(tamheed 5.4.0+)". From 5.6.0 the line
   opens `<utc> version=<x>`. The dated measurements at `:55-58` and `:71` quote lines as they were
   written and stand.
2. **The export and the commit.** The operator ruled this in the maintainer's interview,
   2026-09-28: the export precedes the commit that carries the page, and `package_verify` reads
   `review_current: true` right before that commit. After a bind the order is bind, export,
   commit both, and that last commit stays unbound.

   | Where | Sentence | What the ruling makes of it |
   |---|---|---|
   | `.claude/memory/write-the-handoff-last.md:22` | "final verdicts → `gate_run` → `export_html` → **then** the handoff → commit everything together" | the handoff is a write, so a page exported before it lacks it. The file speaks of `handoff/RESUME-*.md` files, which the journal entry replaced. Whether it is reworded or retired is the operator's |
   | `.claude/memory/tamheed-package-mechanics.md:115` | "last write → `export_html()` → `package_verify()` → `package_close()`" | stands |
   | `.claude/memory/prm-next-carried-rules.md:1135`, `AGENTS.md:29` | `work_bind`, then `gate_run()` and `export_html()` | stand |
   | your close-out in Interlude 13 | handoff, commit, binds, export, commit | it already follows the ruling |

3. **`tamheed-package-mechanics.md:109`** cites `server/README.md:90`. That row moves with every
   release. Cite it by the row's name, `package_verify`.
4. **How your scripts read a trace line.** By key or by position? The instrument is the scripts
   themselves. The maintainer found none on disk that parses a line.
5. **The review page's weight.** Measured on the copy: 14,525,561 bytes, of which the registers
   section is 9.0 MB and the execution section 3.3 MB. Your `ph5-aws-deployment.md:42`, dated
   2026-08-05, says a push timed out and names the page, then 3 MB. **Asked of you, each with its
   instrument:**

   | Question | Instrument |
   |---|---|
   | How long does a push take for a commit that carries the page, and for one that does not? | the wall clock of two `git push` runs in one session |
   | How much of the repository is the page's history? | `git count-objects -vH`, and `git rev-list --objects --all` filtered on the page's path with `git cat-file --batch-check` |
   | Does the operator open the page, and which sections? | the operator's word |

   Whether it is a cost is the operator's to say. If it is, it is a feedback row.
6. **The close-out order**, in full: status moves → the handoff → commit `data/` → `work_bind`
   that commit → `export_html` → commit the bind with the page.

## 3. `findings_38` — what to measure

| Question | Instrument |
|---|---|
| P4: does the first plain emit write nothing? | the emit's `written` list, and `git diff --numstat` on the note |
| P8: is the page's diff at the first export exactly the stamp? | `git diff --numstat` on the page, taken with no write since the last export |
| P9, P10: which hook wrote each line of the interlude? | the line's `version=` field, beside its `session=` tail |
| Does a session that started before the update write a line with no `version=` until it reloads? | the trace, for a process you did not reload |
| Did a session started in a subfolder load the plugin? | its transcript's skill listing |
| §2.4 and §2.5 | as named there |
| Any brief error, numbered E1… as before | any wrong class above is a finding, not a paraphrase |
