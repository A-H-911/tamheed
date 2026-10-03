# Brief to ACMP: tamheed 5.9.0 (plain English, no report unless a class fails)

> **How to use this file.** It is read by path. Nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.9.0.md` and execute it. Write no
> report unless a class fails.* Everything below is a CLASS of result, never the field's counts.
> Where an id, a path or a number appears, it is a stable row of yours or the maintainer's own
> measurement. The measurements come from a read-only copy of your package taken by `git archive`
> at `8b7d8bd1`, quoted so you can compare.
>
> **As the operator ruled for 5.7.0 (R53), this brief asks for no report.** You take the release
> at the start of your next ordinary session and check the classes. You write a feedback row only
> for a class that fails. Your mission queue is not held.
>
> **This brief prescribes no write to your record.** It prescribes one emit (§2, class 4) and one
> export (class 5), both tool-owned. It ends with one STOP that is the operator's (§3).
>
> **What the maintainer's copy cannot see.** A `git archive` copy holds tracked files only. Your
> working tree held uncommitted changes to three JSONL files when the copy was taken, so your own
> first `package_verify` may differ from the copy's. Every absence claim below is a claim about
> tracked files.

## 0. Errors owned

- **O23** The rewrite skill of this release shipped in plan 183 with no path for the commonest
  Approved row. A requirement, a constraint, an assumption, a dependency or a decision is Approved
  but has no `superseded_by` column. The planning review did not catch it. A real agent in the lab
  stopped on it in its first batch (lab beat 33). The operator ruled (R45), and the skill now says:
  in place, still Approved, only while the change is punctuation or a sentence split. It was the
  first gap a real agent found that a scripted beat could not have found.

## 1. The upgrade, and what a session meets

1. `claude plugin marketplace update tamheed`, then `claude plugin update tamheed@tamheed --scope
   user`. Then **quit the client and start it again** (`claude --resume` from a fresh process is
   fine). `/reload-plugins` restarts the server and the hooks. It does not rebuild what the session
   lists (the route of the 5.8.1 brief, O21 and O22, carried).
2. **No migration.** No JSONL rewrite. `schema_version` stays 7. The CSV does not move.
3. **Eight tool descriptions are new text.** Wave 1 of this release rewrote every refusal and every
   readiness note as short active sentences with no semicolon. Of the 19 descriptions, eight changed
   and eleven are the 5.8.1 text. The eight: `package_unlock`, `entity_upsert`, `entity_query`,
   `gate_run`, `progress_update`, `audit_record`, `handoff_emit`, `package_verify`. A client process
   started after the update lists the new descriptions. A process that was running lists the old ones until you start a
   new one.
4. **The note changes.** The 5.8.1 brief's class 5 said the note changes in no string. That was
   true for 5.8.1, and this brief owns the change. Your first `handoff_emit` rebuilds the note as
   `tamheed:note v6`. Its first sentence reads "The Tamheed package for this project is
   `tamheed-package`". Its skills line names `tamheed:plain-english`. On the copy, 14 of the note's
   41 lines changed. The SessionStart hook reads the v5 sentence and the v6 sentence, so a note not
   yet re-emitted still resumes (class 6).
5. **The readiness rule `prose-plain-english`** is an advisory. It reads the register statements,
   your prompt files and the latest handoff under the structural plain-English rules. It names each
   text with its hard findings per rule. It never moves `ready`.
6. **Two skills.** `tamheed:plain-english` is a discipline skill, model-invoked, named by the note.
   An agent reads it before it writes English a reader cannot question. `/tamheed:ste-rewrite` is a
   scenario skill, operator-invoked, in the `/` menu. It rewrites the record's prose batch by batch,
   with a STOP per batch, and nothing runs without your word (§3).

## 2. The classes: hold, or a feedback row

| # | Probe | Class | Holds when |
|---|---|---|---|
| 1 | `server_info` | `5.9.0` / `007_handoff.sql` / `7` | in a client process started after the update |
| 2 | `package_verify` before any write | `verified`, `review_current true`, `review_exported_by "5.8.1"` | no write since your last export (the copy at `8b7d8bd1`: `dirty []`) |
| 3 | `readiness_check("package")` | 24 advisories. `prose-plain-english` reads `fail` with counts per rule. On the copy: 2,342 semicolons, 3,602 long sentences, 631 vocabulary hits, 1 marketing adjective, over 1,290 texts. It names 1,146 texts and shows 50 (the engine's cut). `ready` is what it was: `acs-met` is your blocking failure, as before | always |
| 4 | the first `handoff_emit(refresh_stock=true)` | `refreshed: ["prompts/README.md"]`. The guide's first line reads `tamheed v5.9.0`, and it names nine discipline skills. The note is `tamheed:note v6` (class §1.4). Nothing else is written: no `.mcp.json` on a plugin-hosted server, no prompt copy | the stock guide was never customised (the copy: `customised null`) |
| 5 | the export after class 4 | small: on the copy `5 4` lines and 11 KB, longest added line 2,512. `csv/` unchanged. `review_current true`, `review_exported_by "5.9.0"` | the emit adds no node and no edge |
| 6 | the first trace line of a session started after the update | it opens `<utc> version=5.9.0`. The hook reads the v5 note and the v6 note alike: on the copy, `startup` over either note printed 20 lines and 2,056 characters. A `compact` over the v6 note printed 21 lines and 2,212 characters, so the extra line is the event's, not the note's | the process started after the update |
| 7 | the wire, `tools/list` | `handoff_emit`'s description opens "Wire a target project to the package" (155 characters). The three contract descriptions changed in wording and kept their lengths (387 / 333 / 325), so compare their text, not their length | in a client process started after the update |

**One measurement that is not a class.** The maintainer ran the repository's eval check
`pkg_check.py ste-clean` over the copy's `prompts/` folder. Before the emit the 5.8.1 guide carried
73 hard findings. After the emit the 5.9.0 guide carried 0. Your four project files
(`prm-next.md`, `project-deferred-work-cautions.md`, `project-design-review.md`,
`project-invariant-audit.md`) were skipped by name. They are yours, and only §3 touches them.

## 3. The STOP: whether to rewrite the record's own prose

The rule reports. It rewrites nothing. The choice to rewrite is the operator's, and this brief
puts it once:

> Do you want `/tamheed:ste-rewrite tamheed-package` run on this record, batch by batch?

What a run does, from the skill:

- It reads the rule and forms batches of at most ten texts. It shows each batch as a table with
  four cells: the id and column, the text before, the text after, the consequence of the write. It
  STOPS per batch.
- A Draft or Proposed row is rewritten in place. An Approved requirement, constraint, assumption,
  dependency or decision is rewritten in place and stays Approved (R45). That path holds only while
  the change is punctuation or a sentence split. A change of meaning is a new row through the
  `update` flow.
- An Approved or Implemented ADR, an Approved acceptance criterion and an Approved lesson are
  superseded by a new row, never edited. You approve each successor on your word.
- An Approved acceptance criterion with a Met verdict, an Approved lesson and a Promoted lesson are
  listed and skipped by default. You opt in per row, in your words.
- A project prompt file is rewritten in place. A stock body is never touched.
- The latest handoff entry is never edited. It leaves the rule when a session writes its own handoff
  in plain English.
- Every "after" text keeps every hedge. A rewrite never adds a fact.

What it costs, from the copy: 1,146 named texts are about 115 batches, each with a STOP. The 631
vocabulary hits include your own terms of art. A `glossary-term` row (`GT-`) makes a word a name, and
the rule stops naming it from that write on. Those rows are a smaller first step than a rewrite.

What it changes in readiness, between a write and your word. A superseded ADR's successor lands
Proposed, and the blocking rule `adrs-approved` fails until you approve the successor. So the
approval belongs in the same batch, as the lab run did it. A superseded acceptance criterion starts
its successor unverified, and `acs-met` reads it open until a new verdict. The skill says both in the
consequence column, and the default skips the criteria with a Met verdict.

The maintainer's recommendation, marked as the maintainer's and not a verdict: add the `GT-` rows
first. Then rewrite the Draft and Proposed rows. Touch an immutable row only when you opt in per
row. No answer is also an answer. The rule keeps reporting, and nothing else happens.

## 4. Not built, and said plainly

The engine rewrites no client prose. No change to `csv/` or the JSONL. No migration. `server_info`
does not return the descriptions (R58 stands). The readiness rule has no `GT-` of its own: your
words are yours to name.

## 5. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class number,
what was read and the instrument. Nothing else is asked.
