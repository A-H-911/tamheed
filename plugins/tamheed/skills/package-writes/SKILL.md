---
name: package-writes
user-invocable: false
description: >-
  Use before any write to a Tamheed package (entity_upsert - full-row, substitute or retire items -
  progress_update, audit_record, work_bind, package_verify with record). Use before export_html or
  handoff_emit, which write package files. Use before any git operation that touches package data
  (commit, branch, checkout, reset, stash, merge, push). Use before writing a commit sha, a digest,
  or a claim that a row was written, into a row or a commit message.
---

# Package writes

**The package and git each know things the other cannot. Every rule here guards a crossing between
them, or a value crossing from your hand into a row.**

The obligations table in this project's `CLAUDE.md` note (the `tamheed:note` span) says WHAT to
record and when. This skill says HOW a write reaches the store without losing anything on the way.
None of these failures is caught by a gate. Every gate is row-level, none reads git, none knows what
a sha is, and none compares a field to the value you meant to send. A bad write reports `ok`, every
id resolves, and the damage stays until someone reads it.

---

## 1. Send rows the store can verify

- **Full rows, or at least every NOT NULL column.** An omitted column is preserved by the UPDATE.
  But the row you send must still satisfy the table's NOT NULL constraints, so a bare `{id, pinned}`
  on a lesson is refused on its title. "Omitted columns are preserved" is narrower than it reads.
- **`expect_unchanged: [cols]` names only columns you SEND.** A sent column that differs from the
  stored row refuses the write (a long-row status flip becomes self-verifying). Naming a column the
  item does not carry is refused: it could only pass, so it asserted nothing. Beside a `substitute`
  every column is carried, so name freely there.
- **`substitute` for one token, or a status flip on a long row.** `{type, id, substitute: {col: [old,
  new]}}` re-materialises the row server-side. The long columns never pass through your output. Named
  refusals guard it: a zero-occurrence needle, digit glue, a re-run (`new` contains `old` and `new` is
  already present), JSON inside `custom_attributes`. Bound a needle with its backticks. It cannot
  fill a NULL.
- **Read `changed_columns` after every write.** A length you did not intend is a lost paragraph.
  The cheapest correct status flip is `substitute` on `lifecycle_status`: zero transport, every guard.
  A move that must carry a column of its own is NOT that flip. A lesson's approval lands with its
  `confirmed_by`, and a substitute item carries no other column, so the approval is a full row.
- **Trace edges are keyed** `(from, to, relation)`. A wrong edge is retired (`retire: true`, journaled)
  and the correct one written in the same batch. A new relation never replaces an old one by itself.
- **Immutable-after-approval rows** (ADRs, approved acceptance criteria, approved lessons) are
  superseded, never edited. The trigger refuses the edit. The successor row is the change.

## 2. Move payloads by paste, never by hand, and verify every field the same way

- Paste a generated payload into the call. Do not re-type it. Where you must compose rather than paste,
  treat the composition as untrusted and make the verify step mandatory.
- Re-send a field only from a read taken FOR that send. Text that has passed through a display (a
  terminal print, a summary, a table, an excerpt) is unsafe whatever its origin.
- Hash the field before the write and compare after. Calibrate the check with a one-character
  corruption first. Assert the comparison. Never eyeball it. Length does not predict which field drifts.
- End any fix over more than one row with an independent re-read that re-derives each expected
  value from its own source. Save a pre-image first so the verifier has something to compare.
- *Why:* the hand is the transport, and care does not catch a transcription error. Only a verifier does.
- *Field evidence:* a probability typed as `medium` where the source said high. A title rebuilt from a
  truncated print that lost 1,697 of 2,097 characters on a write that returned `ok`.

## 3. Read the store through the tools, at any size

- `entity_query(type, id?, status?, columns?, limit?, after_id?, ids?, search?, context?)`: `limit`
  cuts rows, never fields. `total` is exact. Page with `after_id` (the result's `next_after`). Quote a
  known set verbatim with `ids`. Sweep by keyword with `search` (the result says which column
  `matched`). `search` + `context` returns true `occurrences`, the census instrument over the
  journal. A `columns` projection says what it `omitted_columns`.
- **Rows come in id order, by prefix and then by the id's first number, and `limit` cuts from the
  lowest.** A limited read returns the first ids of the family, never the newest rows. `after_id`
  returns the rows AFTER an id in that same order. Pass the result's `next_after`, or an id you type,
  which need not name a row. The cut excludes the id itself: to read from an entry on, type the
  id one below it. Only an id's FIRST number counts. What follows it orders as text, so under
  one leading number a dotted id's tenth part comes before its second. For recent state, what
  to read:
  - the newest journal entries: the `resume` block's `last_entries` (three) and `handoff_behind`
    (a count). `readiness_check`'s `handoff-current` names the work entries written after the
    latest handoff, up to its cap of 50. Read them with `ids`.
  - the verdicts: `gate_run`'s `audit_evidence` (three counts over each active criterion's latest
    verdict, with the narrated and the ungraded ids) and `readiness_check`'s `acs-met` list.
  No tool returns "the last ten rows" of a family.
  *Field evidence:* three teaching texts called a read limited to ten rows "the last recorded
  activity" for two months. On a journal of fifteen hundred entries it returned the first ten.
  Until v5.7 the order was the id's text order. A typed `after_id` returned entries hundreds of
  numbers older, and once it dropped three matching entries with no sign in the result.
- **The two journal tools take the keys they name, and refuse any other.** `progress_update`
  items: `entry` (required), `event_type`, `subject_id`, `actor`, `corrects`, `phase_id`,
  `slice_id`. `audit_record` items: `ac_id` and `verdict` (required), `evidence`, `verified_by`,
  `verification_method`, `against_commit`. The server assigns the id and the time. A key outside
  the list refuses the whole batch by name and writes nothing.
  *Field evidence:* until v5.7 such a key was dropped in silence. One journal write lost its
  attributes on a write that returned `ok`, and `summary` sent for `entry` came back as the
  database's own error.
- `trace_query(entity_id, direction, relation?)` for typed links. `server_info()` for the version, the
  root and the package header. `package_verify()` proves the on-disk store canonical (per-file
  byte-equality, foreign files, a citable digest). `record=true` (open package, passing verification)
  appends the server-witnessed `integrity-verified` row. Journal a verification when the operator
  wants the record, not as a reflex.
- A committed script that must QUOTE the store reads an `entity_export` file the tool wrote under
  `<package>/exports/`, never `data/*.jsonl`, never a pasted display. Export immediately before
  generating. A script over the package exists only as a confirmed `local-tool` feedback row.
- Never open `data/*.jsonl` to dodge a payload cap. The tools page.

## 4. Check the tree AT the branch operation, not from memory of having committed

- Immediately before `git checkout -b`, `git switch -c`, `git stash`, `git reset --hard` or
  `git checkout <ref>`, run `git status --porcelain -uall`. Non-empty output is a stop.
- Treat the tail of a recording batch as a write. Every store write (`entity_upsert`,
  `progress_update`, `audit_record`, `work_bind`, `package_verify(record=true)`, `package_close`)
  flushes `data/*.jsonl`. `export_html` / `handoff_emit` write package files beside it
  (`review.html`, `csv/`, `README.md`, the target's `CLAUDE.md`). `work_bind` records the commit and
  dirties the tree AFTER it. If anything ran since your last commit, the tree is dirty again.
- Prefer this order: code work on the branch → land it → commit package writes on the branch the
  package is tracked on. Then bind → commit the binding.
- **A review page you commit is exported before the commit that carries it.** Every store write
  makes the page stale (a closing entry, the handoff and a bind included), so `export_html` comes
  after the last of them. `package_verify` reads `review_current: true` right before that
  commit. After a bind the order is bind → export → commit both, and that last commit stays
  unbound. A bind names a commit, so binding it would stale the page again. `review_current` says
  the page's DATA is the store's. `review_exported_by` names the release that exported it. After
  an upgrade the first reads true over a page the older exporter wrote, and the first export
  rewrites the page with no data moved.
  *Field evidence:* a close-out committed its handoff beside a page exported before it. The
  page on the remote lacked that handoff until the next commit.
- If the check catches something, commit it on the branch you are on before switching.
- *Why:* the act of recording a commit dirties the tree, so the habit "commit before branching" can be
  followed and still be wrong. *Field evidence:* after a bind stamped a sha, six JSONL files rode onto
  a feature branch and cost a full CI cycle to recover.

## 5. Branch from what the remote has

- Before `git checkout -b`, run `git rev-list --left-right --count @{u}...HEAD` and require `0 0`.
  A clean `git status` cannot see committed-but-unpushed work.
- If the local branch is ahead of its upstream, push first (on the operator's say-so where the
  project requires it). Or branch from the remote branch explicitly.
- After a squash-merge, a `git pull` that will not fast-forward is the tell. Verify the package tree is
  identical at both shas and drop the local commits, never a merge commit.
- *Why:* a squash-merge carries every unpushed commit below the branch point into the pull request.
- A branch or an open pull request that the handoff does not explain is a stop: ask the operator. It
  is a state nothing in the record describes.

## 6. Write a sha into a row only once the commit is on the remote

- This covers a `work_bind` ref, an `against_commit`, a digest attributed to a commit, and a sha quoted
  in a progress entry. If the commit is not pushed, push first, or bind after history is settled.
- After any history operation, check each sha a row names: `git merge-base --is-ancestor <sha>
  <remote>/<main>` (or `git branch --contains <sha>`).
- A bind is not the closing ceremony of the work. It only feels like one.
- *Why:* a rebase, amend, squash-merge or `reset --hard` rewrites shas and never touches the row.
  *Field evidence:* thirteen rows bound to an unpushed sha. A correct rebase renamed it, and the
  progress entry pointed at nothing.

## 7. A commit message may claim only writes you have re-read

- Before committing prose that says a row was written, re-read the row.
- When a batch is uncertain, under-claim. Write what is verifiable, add rows afterwards.
- *Why:* no gate reads a commit message against the store, and a commit message reads as a receipt.
  Memory of an intention is indistinguishable from memory of an action.
- A shell chain fails CLOSED for the command that breaks and OPEN for a later command that reads a
  file the chain should have written. A commit took a stale message file from another session, with
  correct files and no error anywhere. Write the message to a unique path, remove it afterwards, and
  read the commit's subject back.
- A multi-line message or body reaches a command only from a file the editor wrote. The shell
  rewrites a stdin heredoc or an inline literal. A flag inside a quoted message can be read as
  the command's own. Write the file, pass its path, and read the subject back.

## 8. Set a scope change to `Merged` last

- Apply the delta to every row its `scope_adds` / `scope_modifies` / `scope_removes` / `amends` edges
  name. RE-READ those rows, then set the `SC-` to `Merged`. An `amends` target merges by full-row
  upsert of a decision or by supersession of an ADR.
- If it is already `Merged`, run `trace_query` on it and open each target. The edges are the checklist.
- A sentence in a target that the scope change discharges ("needs a scope change first") is part of the
  delta. Rewrite it too.
- *Why:* nothing couples `Merged` to its delta. The readiness rule stops looking once it says `Merged`.

## 9. Cross-check git against the package by classifying, never by counting

- A commit whose whole content is a package write cannot cite its own sha. Never report the raw
  "unreferenced commits" set.
- The close-out's last commit is one of them BY RULE. It carries a bind with the exported review
  page (§4), and it stays unbound. It is not drift, and no audit, loop or drift pass binds it.
- Match shas mechanically, not from commit messages. For each unreferenced commit, run `git show
  --name-only` and bucket by path. The buckets: the package directory (expected), docs, notes or
  other non-source files (out of scope), source or tests (a real candidate). Flag only the last
  bucket.
- State the discriminator even when the result is empty, so a clean result reads as a check that ran.
- Never invent a verdict for a flagged commit. Name it and let the operator decide.

## 10. The lock and the operator's word

- A refused `package_open` names the holder (pid, host, taken_at) and what the store observed about it
  (`not-running`, `reused`, `alive`, `unobservable`). `package_unlock(name)` reports it on demand.
  `package_unlock(name, confirm=true)` is the OPERATOR's word, never yours, and refuses on `alive` and
  `unobservable`. Never remove `data/.lock` on your own judgment. When the tool refuses, the manual
  removal is the operator's deliberate act. Interview them. It is never yours.
- Every `operator_confirm: true`, every `force: true`, every `go_no_go`, every waiver row is the
  operator's explicit words. They come from an interview in this session
  (`tamheed:operator-interview`). The JSON
  boolean is the word, never a value you supply because the ceremony expects it.

## 11. Never manufacture a status, and never trust a global rename

- **A status is written from evidence, never to turn a rule green.** A row becomes `Implemented`,
  `Met` or `Done` because the verdict, the binding or the operator's word exists. It never does
  because the readiness rule that lists it would pass once it did. A sweep flipped every work item
  in a family to `Implemented` on the assumption that the work "must be done by now". It was
  reverted as a defect: manufactured status, and the register could no longer tell finished from
  assumed.
  - *Tell:* the write you are about to make has no `audit_record`, no `work_bind` and no decision
    behind it, only a rule it silences.
- **An advisory failure is normal and is not a task. A BLOCKING failure names its row and is a real
  finding.** Ask the readiness check every time and expect neither answer. A line that said "expect
  not ready" stayed true for days after the row it rested on had closed. Never clear a blocking failure
  by softening a defect's severity or converting its kind. A close is an evidenced disposition, not a
  re-grading.
- **A liveness field that carries a due date goes red as dates pass, and that is the control
  working.** Check the row again and write the new date from that act. Clearing or moving a date to
  restore the amber re-blinds the control.
- **A global rename skips every record that quotes the text as written.** Renaming an id, a title
  or a term with a search-and-replace over the rows you know about leaves the quotations in other
  families untouched. Think of a decision clause that cites the old title. Think of a journal entry
  that names the old id in prose, or a prompt row that repeats it. Sweep with `search=` across every family for the
  OLD text after the rename, and read each hit (`tamheed:reading-the-record` step 3: two keys, not
  one). `prose-ids-resolve` and `prompt-ids-resolve` catch a dangling id, never a stale sentence.

## 12. Coupled rows move in one batch

Nothing in the store compares these pairs. Every one was found by a sweep, not by a rule.

- **Closing the last child readies nothing by itself.** The parent item and the slice have their own
  rules (re-run `readiness_check` on the slice), and the slice's `Implemented` is the operator's
  verdict. `Review` is the done-claim.
- **A requirement's status and its deferred-work row's are uncoupled columns.** A requirement
  labelled out of scope beside an Activated row for the same work is invisible to every rule. When you
  move one, check the other in the same breath. Measure the deferred set, never assume it only grows.
- **The item and its deferred-work row move together.** A deferred-work row never closes itself when
  its item ships. Close it in the done-claim batch. The omission recurred four times in one project.
- **A done-claimed item names the acceptance criteria it satisfies**, or records, citing the ruling,
  why it has none. Nothing enforces the amendment, and an item without it is permanently
  unreviewable.
- **A placeholder row says so.** A test row created to satisfy a trace gate says in its own text that
  it is planned and not written. It must never read as evidence that a test exists.
- **Run the gate. Never carry its count.** A pass count or a version floor written into a rule
  survives every upgrade that falsifies it.

---

## What this skill does NOT cover

- **What to record**: the obligations table in the note is authoritative. This file never restates it.
- **Where a session stopped**: `tamheed:session-handoff` (the `handoff` journal entry, written last).
- **Whether a record says what you think**: `tamheed:reading-the-record`.
- **Whether a test, a measurement or a CI run proves what you claim**: `tamheed:test-evidence`,
  `tamheed:measurement-evidence`, `tamheed:ci-evidence`.
- **How to put a decision in front of the operator**: `tamheed:operator-interview`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
