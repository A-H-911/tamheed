---
name: ste-rewrite
description: >-
  Invoke to rewrite a package's existing prose into plain English, batch by batch. The readiness
  rule `prose-plain-english` names the texts. The agent proposes before and after, STOPs for your
  approval, writes Draft and Proposed rows in place and supersedes immutable rows.
disable-model-invocation: true
argument-hint: "[package]"
---

# Plain-English rewrite - the record's prose, batch by batch, on the operator's word

Invoke this (`/tamheed:ste-rewrite`) to rewrite the texts of `<package>` that the readiness rule
`prose-plain-english` names. The agent touches nothing the rule does not name. Every batch STOPs.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Rewrite the prose of the `<package>` Tamheed package into plain English:

1. `package_open("<package>")` if not already open, then `readiness_check("package")`. Read the
   `prose-plain-english` rule: its `entities` are the scope and its `counts` are the baseline.
   A text the rule does not name is never touched. A stock body in `prompts/` and the journal's
   history are outside the scope by construction.
2. Read every named row whole: `entity_query("<type>", ids=[...])` with the full columns, never
   a display (`tamheed:reading-the-record`). Read a named prompt file from disk.
3. Form a batch of at most ten texts. For each text, write a table row with four cells. The
   cells are the id and column (or the file and line), the text before, the text after, and the
   consequence of the write.
   - A Draft or Proposed row: rewritten in place.
   - An Approved row of a family with no supersession column: rewritten in place, and it stays
     Approved. Those families are requirements, constraints, assumptions, dependencies and
     decisions. This path holds only while the change is punctuation or a sentence split. A change of meaning is a new
     row through the `update` flow, never a rewrite.
   - An Approved or Implemented ADR, an Approved acceptance criterion, an Approved lesson: a
     superseding row, never an edit. An acceptance criterion with a Met verdict starts its
     successor unverified. `acs-met` reads the successor as open until a new verdict verifies
     it. A superseded Approved lesson leaves the note's roster at the next emit.
   - The latest handoff entry: never edited, because the journal is append-only. It leaves the
     rule when the session writes its own handoff in plain English.
   - DEFAULT: the agent lists an Approved acceptance criterion with a Met verdict, an Approved
     lesson and a Promoted lesson, and marks each "skipped by default". The operator opts in per
     row, in their words.
4. Write each "after" text under `tamheed:plain-english`: one instruction per sentence, the
   actor named, no semicolon, the vocabulary's verbs, every hedge kept. Never add a fact. When a
   rewrite keeps a compound tense or a hedge on purpose, add a `Kept as-is:` line and read it to
   the operator with the batch.
5. **STOP for operator approval** (`tamheed:operator-interview`): one decision per row. A word
   the operator calls the project's own becomes a `glossary-term` row (`GT-`), and the text keeps
   it. The rule stops naming it from that write on.
6. After approval, write (`tamheed:package-writes`):
   - a Draft or Proposed row, or an Approved row of a family with no supersession column: a
     full-row `entity_upsert`. Name every column you did not touch in `expect_unchanged`. The
     server then refuses a concurrent write instead of overwriting it.
   - an immutable row: the supersession path of the governance reference. Insert the successor
     first, Proposed, with the text rewritten and every other column carried. Then point the
     predecessor at it (`superseded_by`, or `promoted_to` where the family uses it) and set it
     Superseded. The operator approves the successor on their own word.
   - a prompt file: rewrite it in place, never a stock body, never a file the rule did not name.
7. One `progress_update` per batch (event_type `note`, actor `agent:<session>`). It names the
   rows written, the rows superseded, the files rewritten and the rows skipped by default.
8. `readiness_check("package")` again. Show the operator the rule's `counts` before and after.
   Then propose the next batch, or stop when the operator says stop.

You never author a `WVR-` row for this rule, and you never run a batch without the STOP.
