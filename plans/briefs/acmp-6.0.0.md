# Brief to ACMP: tamheed 6.0.0 (prompts return to the store, no report unless a class fails)

> **How to use this file.** It is read by path. Nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-6.0.0.md` and execute it. Write no
> report unless a class fails.* Everything below is a CLASS of result, never the field's counts.
> Where an id, a path or a number appears, it is a stable row of yours or the maintainer's own
> measurement. The measurements come from a read-only copy of your package taken by `git archive`
> at `8b7d8bd1`, quoted so you can compare.
>
> **As the operator ruled for 5.7.0 (R53), this brief asks for no report.** You take the release
> at the start of your next ordinary session and check the classes. You write a feedback row only
> for a class that fails. Your mission queue is not held.
>
> **This brief prescribes writes to your record.** A MAJOR release with a migration:
> `package_migrate` (one preview, one confirm on your word) and the approval of your kickoff row.
> Both are yours. The brief ends with one STOP that is the operator's (§3).
>
> **The 5.9.0 brief is superseded by this one and is not executed.** Both releases shipped on
> 2026-10-04, and your copy shows the client you last ran was 5.8.1. Every "changed" claim below
> compares with 5.8.1, the state the copy measured. The 5.9.0 brief's class 4 emit is refused
> under 6.0.0 (§1.6). Its one STOP still stands and is yours: whether `/tamheed:ste-rewrite` runs
> on this record, batch by batch (`acmp-5.9.0.md` §3). This brief adds nothing to it.
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only. Your
> working tree held uncommitted changes to three JSONL files when the copy was taken, so your own
> first `package_verify` may differ from the copy's. Every absence claim below is a claim about
> tracked files.

## 0. Errors owned

- **O24** The 5.9.0 brief was superseded the day it was written, before you could read it. It made
  two promises in the language of files. Class 4 said the first emit refreshes `prompts/README.md`
  to the 5.9.0 body. §1.5 said the readiness rule reads "your prompt files". Both are void under
  6.0.0. The migrate removes that file and seeds the guide at the package root. The rule reads rows.
  The copy measured the state this brief starts from: `review_exported_by "5.8.1"`, the note
  `tamheed:note v5`.
- **O25** A 6.0 server on your package, before the migration, reads none of your four prompt
  files. `prose-plain-english` named 1,286 texts and no file. `prompt-ids-resolve` read
  `indeterminate` over zero rows. G-SET passed and said nothing, because your registry has no
  `prompt` type until the migrate adds it. Nothing warns. This brief is the warning.

## 1. The upgrade, and what a session meets

1. `claude plugin marketplace update tamheed`, then `claude plugin update tamheed@tamheed --scope
   user`. Then **quit the client and start it again**. `/reload-plugins` restarts the server and the
   hooks. It does not rebuild what the session lists (O21 and O22, carried).
2. **A migration, in two steps on your word.** The store gains the `prompts` table (migration
   `008_prompts.sql`, `schema_version` 8, applied at connect). Your package opens before the migrate.
   The emit does not run before it: `handoff_emit` requires an Approved kickoff row named by the
   header's `entry_point`, and your header names a file.
3. **`package_migrate` runs on a CLOSED package.** On an open package it answers "package
   'tamheed-package' is open — package_close it first". The lab's agent met that refusal when the
   maintainer's words had the order wrong.
4. **The preview** (`package_migrate("tamheed-package")`, no confirm) writes nothing. On the copy it
   named five files. `prompts/README.md`: remove, byte-equal to the shipped 5.8.1 stock.
   `prompts/prm-next.md`: convert to `PRT-001`, kind `kickoff`, because the header names it. The three
   `project-*.md` files: convert to `PRT-002`, `PRT-003`, `PRT-004`, kind `situational`. The
   `entry_point` line reads `prompts/prm-next.md -> PRT-001`. The folder line reads `remove`. The
   backup folder is `prompts-v5-backup/`. The registry gains `prompt`.
5. **The confirm** (`confirm=true`) on your word writes four Proposed rows with `converted_from` in
   their attributes, and the audit journal row. It sets the header's `entry_point` to `PRT-001`. It
   seeds the guide at `tamheed-package/README.md` (the 6.0.0 body). The four files move to `prompts-v5-backup/`, the
   stock guide is removed, and `prompts/` goes. On the copy fourteen paths changed.
6. **The STOP by design.** `handoff_emit` then refuses. Its message names the row and the word:
   PRT-001 is Proposed, not Approved, and the handoff carries only what the operator approved. It
   asks for the row to be approved in their words and the emit re-run. An Approved prompt row is edited in place, never
   superseded (R45, P11).
7. **The emit after your approval** rebuilds the note as `tamheed:note v7`. Its prompts section
   rosters the Approved rows, each with its kind and its skill. The guide at the root is reported
   `unchanged`, because the migrate seeded it. The stale scan names the file-era pointers (class 7).
8. **The rules read rows.** `prompt-ids-resolve` reads the four bodies. `prose-plain-english` counts
   their titles and bodies among its texts. `handoff_emit` screens the Approved rows (G-INJECT).
9. **The page.** `review.html` has twelve sections. The Prompts section lists the rows awaiting your
   approval first, then the Approved rows with the kickoff marked as the entry point.
10. **The wire.** Against the 5.8.1 client you last ran, 8 of the 19 descriptions changed: the
    5.9.0 plain-English rewrite, and `handoff_emit` once more in 6.0.0. `handoff_emit` opens "Wire a
    target project to the package: write the CLAUDE.md note and the stock README at the package
    root". It is 167 characters, 63 in 5.8.1. `entity_query("prompt", plugin_skill=...)` is new. Sixteen scenario skills read
    their bound rows at their first step. Every surface says "the planning half" and "the execution
    half", one agent in both.
11. **The hook** reads the v5, v6 and v7 sentences. On the copy, `startup` over the v5 note printed
    20 lines and 2,056 characters. Over the v7 note it printed 20 lines and 2,053 characters.

## 2. The classes: hold, or a feedback row

| # | Probe | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `6.0.0` / `008_prompts.sql` / `8` | in a client process started after the update |
| 2 | `package_verify` before any write | `verified`, `review_current true`, `review_exported_by "5.8.1"` | no write since your last export (the copy: `dirty []`) |
| 3 | `package_migrate("tamheed-package")` on the closed package | the plan of §1.4: five files, four rows, the kickoff `PRT-001`, the folder removed, nothing written | your `prompts/` holds the five tracked files and `prompts-v5-backup/` does not exist |
| 4 | `package_migrate("tamheed-package", confirm=true)` | `stage "migrated"`, `prompt_rows` four, `entry_point.to "PRT-001"`, `prompts_folder "remove"`, `README.md` at the package root | the preview matched §1.4 |
| 5 | `gate_run` after class 4 | `G-SET pass` and `G-IDS pass` | the four rows exist |
| 6 | `handoff_emit(refresh_stock=true)` before your approval | refused, the message of §1.6 | `PRT-001` is Proposed |
| 7 | `handoff_emit(refresh_stock=true)` after your approval (§3) | `tamheed:note v7`, the roster line `- **PRT-001** [kickoff, the entry point] Kickoff prompt — the durable one`, `prompt_library.unchanged ["README.md"]`. `stale_references` names `AGENTS.md:39` and `PRT-001.body:22`, both pointing at `tamheed-package/prompts/`. It is empty when you rewrote both first (§3) | on the copy the note grew 41 -> 53 lines (26 added, 14 removed) |
| 8 | the export after class 7 | the Prompts section (`section id="prompts"`), `csv/prompts.csv`, `review_exported_by "6.0.0"`. On the copy 397 lines were added and 12 removed | the rows' bodies are the new lines |
| 9 | `readiness_check("package")` after class 7 | `prompt-ids-resolve pass` over 4 rows. `prose-plain-english fail` with the 5.9.0 brief's counts back: 3,602 long sentences, 2,342 semicolons, 631 vocabulary hits, 1 marketing adjective. The texts are 1,294, up from 1,286 before the migrate. The eight are your four titles and bodies. `ready` on your open items alone | 24 advisories |
| 10 | the first trace line of a session started after the update | it opens `<utc> version=6.0.0`. The hook prints over the v5 note and the v7 note alike (§1.11) | the note has markers |
| 11 | the wire, `tools/list` | 19 descriptions. 8 differ from the 5.8.1 text. `handoff_emit` is 167 characters | a client process started after the update |

**One measurement that is not a class.** The repository's eval check `pkg_check.py ste-clean` read
73 hard findings over your 5.8.1 guide before the migrate and 0 over the root guide after it. Your
four project files were skipped by name before. After the migrate they are rows, and
`prose-plain-english` names them with the rest of your record.

## 3. The STOP: the kickoff, the bindings, the file-era sentences

The migration lands four Proposed rows and refuses the emit. The next three choices are the
operator's, and this brief puts them once:

> Do you approve `PRT-001` as the kickoff? Which rows bind to which scenario skill? Which file-era
> sentences do you rewrite?

What each means, from the engine:

- **The approval.** Read `PRT-001` whole: `entity_query("prompt", ids=["PRT-001"])`. Approve it in
  your words with a full-row `entity_upsert`, `lifecycle_status Approved`, `expect_unchanged` on
  every other column. On the copy that write changed one column. The emit then runs.
- **The bindings.** `plugin_skill` names the scenario skill that reads a row at its first step. The
  guard admits sixteen names and refuses any other (on the copy `design-review` was refused). Your
  invariant audit reads "alongside `/tamheed:integrity-check`": `PRT-004 -> integrity-check`. Your
  deferred-work cautions read "alongside `/tamheed:replan-deferred`": `PRT-002 -> replan-deferred`.
  Both bindings landed on the copy, and `entity_query("prompt", status="Approved",
  plugin_skill="integrity-check")` returned `PRT-004`. Your design review names no scenario skill
  that reads it. It stays a row you read yourself, Proposed or Approved as you choose.
- **The file-era sentences.** The emit names two: `AGENTS.md:39` ("START WITH
  `tamheed-package/prompts/prm-next.md`") and `PRT-001`'s body, line 22 (it sends the reader to
  `tamheed-package/prompts/README.md`). The emit cannot see
  `.claude/memory/prm-next-carried-rules.md:10`, which quotes the same path. Each row also carries a
  `converted_from` hint until you remove it from its attributes after review.
- **The backup folder.** `prompts-v5-backup/` holds your four files, byte for byte. Git holds them
  too. Keep it or remove it. The engine never reads it again.

The maintainer's recommendation, marked as the maintainer's and not a verdict. Approve `PRT-001`
after reading it as a row, in the same session as the confirm. Bind `PRT-004` and `PRT-002` as
above. Leave `PRT-003` Proposed until a reader exists. Rewrite `AGENTS.md:39` and the body's line 22
before the emit, so the stale scan reads empty (class 7 holds either way). Remove the backup folder once the migration is
committed. No answer is also an answer. The emit keeps refusing, and nothing else happens.

## 4. Not built, and said plainly

The migrate infers no kind beyond the kickoff: a file is situational unless its front matter says
otherwise. No row is approved by the engine. The migrate's result does not return the id of the
audit journal row it appends. A 5.9 server opens a 6.0 package, ignores `prompts.jsonl` and names
`prompt` in G-SET. A trace edge to a `PRT-` row makes that open fail (engine candidate E3).
`server_info` does not return the descriptions (R58 stands).

## 5. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class number,
what was read and the instrument. Nothing else is asked.
