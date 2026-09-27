# Brief to ACMP — tamheed 5.5.0 (Interlude 13)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line: *read
> `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.5.0.md` and execute it; the report is
> `findings_37.md`.* Everything below is a CLASS of result, never the field's counts. A prediction
> names a role ("the latest handoff"), never a row that moves. Where an id, a path or a number
> appears it is either a stable row of yours or the maintainer's own measurement on a read-only copy
> of the package taken by `git archive` at `27f63ae8`, quoted so you can compare.
>
> **Every recipe in §2 was executed on that copy before this file was written, and each names the
> record it discharges.** The 5.4.0 brief's Q1 recipe ran clean on the copy and still discharged
> nothing: a dry-run proves a write lands, not that it answers what is owed.

## 0. Errors owned

**The 5.4.0 brief's, as you found them.**

- **E1** the D1 list named two places to correct and omitted two that lean on the same error.
- **E3** Q1 "can be corrected by a `correction` entry". Q1 was also a clause of an approved
  decision. You wrote a new decision, which was the right write.
- **P4** said both `CLAUDE.md` files read `unchanged`. The result is one `unchanged` entry and a
  warning about the root file.

**The maintainer's own, which you did not report.**

- **The plugin defined "binds" two ways.** `governance.md` said status is the single truth for what
  binds. `reading-the-record` said the note's roster binds, "never a lesson's register status".
  That sentence shipped in 5.2.0, absorbed from your carried rule about an emit that ran in a later
  batch. Your handoff's "it no longer binds" followed the plugin's own skill. The error is the
  maintainer's. See §2.1.
- **"Every session in every project where the plugin is ENABLED appends a line"** (`install.md`,
  5.4.0): written as a rule, not a count. You measured it false.
- **The 5.4.0 brief's sweep read your memory files only**, never your decisions or journal. That is
  how Q1's second carrier was missed. This brief's sweep covered memory, decisions, the journal
  from the last interlude on, the live lessons and both `CLAUDE.md` files.
- **Four interview options of the maintainer's carried loose wording.** No ruling depended on one.

## 1. The upgrade (part A; no interview needed)

1. Baseline as before: commit the package; `package_close()`; keep `gate_run()`,
   `readiness_check("package")`, `package_verify()` and `server_info()` outputs.
2. The trace stays as you have it.
3. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed --scope user`,
   then your reload route. Check the installed tree against the tag with your own recipe.
4. **No migration.** `server_info` reads `5.5.0`, `migrations_head 007_handoff.sql`,
   `schema_version 7`. No JSONL rewrite: the digest is unchanged across the upgrade.

**Three strings an agent reads changed.** Anything of yours that quotes the old ones is a dated
record, not an error: the approval hint's first clause, the note's footer, the
`lessons-note-budget` advisory's last clause.

### Predicted classes (each measured on the copy with the shipped engine)

| # | Probe | Class |
|---|---|---|
| P0 | `server_info` after the reload | `5.5.0` / `007_handoff.sql` / `7`; checked first |
| P1 | `package_open` → `resume` | the latest handoff, with the ids of its corrections listed; `handoff_behind 0` while nothing was journalled after it; `open_feedback []`; `skill tamheed:package-writes`; `lock` `observed "alive"`, `evidence "held by this session"` |
| P2 | `package_verify` before any write | `verified`, `dirty []`, the digest of your baseline. **`review_current true`**: it compares the digest stamped in the page, so it stays true although the page is still the 5.4.0 render |
| P3 | the reload and the hook | no trace line carrying YOUR session's id inside the reload's window |
| P4 | the first plain `handoff_emit` | **`written` names the package's `CLAUDE.md`.** One line of it changes, the footer: `N more Approved lesson(s) bind too and are not rendered here: …`. The roster is unchanged. The root `CLAUDE.md` is one `unchanged` entry, with the warning that it imports the note, and a second warning says the note span was rebuilt. `diverged_stale_stock [{prompts/README.md, matches 5.4.0}]` with its STALE-STOCK warning; every scan empty; no `skill` key. A second emit writes nothing. On the copy the note's path line changed too, a copy artefact |
| P5 | `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`, `written []`. The guide's diff is its title and its lesson sentence: three lines out, five in. The note is not rebuilt |
| P6 | `readiness_check("package")` | the blocking classes of your baseline, unchanged. `lessons-confirmed` passes while no lesson is Proposed. `lessons-note-budget` passes; its new last clause prints only past the ceiling |
| P7 | any `entity_query` | `skill: "tamheed:reading-the-record"` on every successful result, `count: 0` included. An error result carries no `skill` key |
| P8 | the first `export_html` | **the page is rewritten although no data moved.** The Approved lessons fold gains the column `note (rendered at the next emit)`; its title names the roster's rule; the rows marked `rendered` are exactly the rows your note lists, and the rest read `not rendered`. The digest is unchanged and `review_current` reads true before and after |
| P9 | the hook after `/compact` | the latest handoff whole, with its `Corrections` line; one trace line whose counts equal the block's and whose tail is your session's id |
| P10 | a lesson approval, if one is ruled | `next` opens `this lesson binds from this write and is RENDERED only once the always-loaded note is rebuilt`; its cap phrase is unchanged. `changed_columns` names the columns the row SENT and changed: three when it sends `confirmed_at`, two when it does not. An approval that omits a stored column is refused as content drift: the stored content goes whole |
| P11 | the skills the cues load | from the `5.5.0` folder. `reading-the-record`'s paragraph on the note is rewritten; `register-liveness` step 14 asks for the row's note line and the approval's cost, three cases; `written-claims` step 5 ends with the discharge rule; every skill that writes a lesson says its statement opens with the rule |

### Feedback dispositions

None to move. No row was Reported this round.

## 2. Part B — ACMP-side, on the operator's word

1. **Two words.** The operator ruled this in the maintainer's interview, 2026-09-27: **binds** is
   the status, the operator's word, retired only on their word; **rendered** is the note's roster.
   A lesson pushed out of the roster still binds and is read only by query. It is tamheed's
   vocabulary now. Whether it becomes a decision row of your project is the operator's to say, put
   your way. The sentences it touches, by path and line at `27f63ae8`:

   | Where | Sentence | What the ruling makes of it |
   |---|---|---|
   | the latest handoff, its RULINGS GIVEN line | "it stays Approved; it no longer binds" | it stays Approved, so it binds; it is no longer rendered. **Recipe:** a `correction` entry naming the handoff. Measured on the copy: `handoff-current` stays `pass`, and the resume block and the hook list the new correction's id beside the earlier one. It discharges the handoff's line and nothing else |
   | `findings_36.md:204` | "the roster is what binds, so LL-102 stops binding" | a dated correction beside it, as you correct a finding |
   | `.claude/memory/prm-next-carried-rules.md:1333-1341` | "THE TOOL-OWNED NOTE IS THE ONLY ROSTER OF WHAT BINDS" | the rule's content stands in the other word: only the note says what is RENDERED, and an emit in a later batch leaves an approved lesson unrendered. The file holds a carried rule verbatim. Whether it gains a dated note is the operator's ruling. Fix the file, never the pointer |

   Read and left: `DEC-234` d2 says the pushed-out lesson "stays Approved", which is right under the
   ruling. `PE-1510` says a Proposed lesson "binds nothing", which is right.

   What the operator can do about a lesson that is no longer rendered is theirs alone: pin it,
   promote its theme into a skill, or leave it to the query. `review.html` now shows which rows
   those are.
2. **Your `hook-trace.md` rule on who writes a line** (`:21-25`, repeated at `MEMORY.md:48` and
   `findings_36.md:80`): "a session whose HARNESS RUNS SessionStart hooks", and SDK-Python
   sessions "ran no SessionStart hook at all". The instrument cannot say that. Measured by the
   maintainer over every transcript on the machine:

   | Reading | Result |
   |---|---|
   | SDK-Python transcripts holding a hook row of ANY event | none |
   | SDK-Python transcripts whose skill listing names any plugin | none of 640 |
   | Headless command-line transcripts whose listing names a plugin | every one |
   | `hook_success` rows with stdout and stderr both empty, any session | none |

   So those transcripts record no hook at all, and a missing row proves nothing. What is measured:
   those sessions loaded no plugin, and wrote no line. The rule that survives: a session writes a
   line when it LOADED the plugin. **Asked of you:** confirm or refute with your own method, by
   reading the listing attachment of one such transcript, and fix the file if it holds.
3. **The line you could not attribute** (03:22:45Z, 2026-09-27). Probable, for you to confirm or
   refute. Three controls: each time a `/compact` was typed, the summariser's `source=startup`
   line followed 2 to 3 seconds later (02:36:32 and 02:36:35; 17:56:52 and 17:56:55; and one in the
   maintainer's own session). In your session a `/compact` was typed at 03:22:42.572Z. No
   compaction row follows it in that transcript, and no summariser transcript persisted.
4. **The close-out order** stands: status moves → the handoff LAST → commit `data/` → `work_bind`
   that commit.

## 3. `findings_37` — what to measure

- P4: is the note's diff at the first emit exactly the footer line?
- P8: are the rows the page marks `rendered` exactly the rows your note lists? Does `review_current`
  read true before the first export?
- §2.2: the listing check on one SDK-Python transcript.
- §2.3: your own reading of the 03:22:42Z `/compact`.
- A session of yours that started before the upgrade: does it write a trace line only after a
  reload or a restart? The plugin loading reference says a running session keeps the version it
  loaded.
- P10, on an approval made for the project's own reasons — not one made to see the hint.
- Any brief error, numbered E1… as before; any wrong class above is a finding, not a paraphrase.
