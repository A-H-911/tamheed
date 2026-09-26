---
name: package-writes
user-invocable: false
description: >-
  Use before any write to a Tamheed package (entity_upsert - full-row, substitute or retire items -
  progress_update, audit_record, work_bind, package_verify with record); before export_html or
  handoff_emit, which write package files; before any git operation that touches package data
  (commit, branch, checkout, reset, stash, merge, push); and before writing a commit sha, a digest,
  or a claim that a row was written, into a row or a commit message.
---

# Package writes

**The package and git each know things the other cannot. Every rule here guards a crossing between
them, or a value crossing from your hand into a row.**

The obligations table in this project's `CLAUDE.md` note (the `tamheed:note` span) says WHAT to
record and when. This skill says HOW a write reaches the store without losing anything on the way.
None of these failures is caught by a gate: every gate is row-level, none reads git, none knows what
a sha is, and none compares a field to the value you meant to send. A bad write reports `ok`, every
id resolves, and the damage stays until someone reads it.

---

## 1. Send rows the store can verify

- **Full rows, or at least every NOT NULL column.** An omitted column is preserved by the UPDATE —
  but the row you send must still satisfy the table's NOT NULL constraints, so a bare `{id, pinned}`
  on a lesson is refused on its title. "Omitted columns are preserved" is narrower than it reads.
- **`expect_unchanged: [cols]` names only columns you SEND.** A sent column that differs from the
  stored row refuses the write (a long-row status flip becomes self-verifying). Naming a column the
  item does not carry is refused: it could only pass, so it asserted nothing. Beside a `substitute`
  every column is carried, so name freely there.
- **`substitute` for one token, or a status flip on a long row.** `{type, id, substitute: {col: [old,
  new]}}` re-materialises the row server-side; the long columns never pass through your output. Named
  refusals guard it (a zero-occurrence needle, digit glue, a re-run - `new` contains `old` and `new` is
  already present - JSON inside `custom_attributes`); bound a needle with its backticks. It cannot
  fill a NULL.
- **Read `changed_columns` after every write.** A length you did not intend is a lost paragraph.
  The cheapest correct status flip is `substitute` on `lifecycle_status` — zero transport, every guard.
- **Trace edges are keyed** `(from, to, relation)`. A wrong edge is retired (`retire: true`, journaled)
  and the correct one written in the same batch; a new relation never replaces an old one by itself.
- **Immutable-after-approval rows** (ADRs, approved acceptance criteria, approved lessons) are
  superseded, never edited — the trigger refuses the edit; the successor row is the change.

## 2. Move payloads by paste, never by hand — and verify every field the same way

- Paste a generated payload into the call. Do not re-type it. Where you must compose rather than paste,
  treat the composition as untrusted and make the verify step mandatory.
- Re-send a field only from a read taken FOR that send. Text that has passed through a display — a
  terminal print, a summary, a table, an excerpt — is unsafe whatever its origin.
- Hash the field before the write and compare after. Calibrate the check with a one-character
  corruption first. Assert the comparison; never eyeball it. Length does not predict which field drifts.
- End any repair over more than one row with an independent re-read that re-derives each expected
  value from its own source. Save a pre-image first so the verifier has something to compare.
- *Why:* the hand is the transport, and care does not catch a transcription error — only a verifier does.
- *Field evidence:* a probability typed as `medium` where the source said high; a title rebuilt from a
  truncated print that lost 1,697 of 2,097 characters on a write that returned `ok`.

## 3. Read the store through the tools, at any size

- `entity_query(type, id?, status?, columns?, limit?, after_id?, ids?, search?, context?)`: `limit`
  cuts rows, never fields; `total` is exact; page with `after_id` (the result's `next_after`); quote a
  known set verbatim with `ids`; sweep by keyword with `search` (the result says which column
  `matched`, and `search` + `context` returns true `occurrences` — the census instrument over the
  journal); a `columns` projection says what it `omitted_columns`.
- `trace_query(entity_id, direction, relation?)` for typed links; `server_info()` for the version, the
  root and the package header; `package_verify()` proves the on-disk store canonical (per-file
  byte-equality, foreign files, a citable digest); `record=true` (open package, passing verification)
  appends the server-witnessed `integrity-verified` row — journal a verification when the operator
  wants the record, not as a reflex.
- A committed script that must QUOTE the store reads an `entity_export` file the tool wrote under
  `<package>/exports/` — never `data/*.jsonl`, never a pasted display; export immediately before
  generating. A script over the package exists only as a confirmed `local-tool` feedback row.
- Never open `data/*.jsonl` to dodge a payload cap; the tools page.

## 4. Check the tree AT the branch operation, not from memory of having committed

- Immediately before `git checkout -b`, `git switch -c`, `git stash`, `git reset --hard` or
  `git checkout <ref>`, run `git status --porcelain -uall`. Non-empty output is a stop.
- Treat the tail of a recording batch as a write: every store write (`entity_upsert`,
  `progress_update`, `audit_record`, `work_bind`, `package_verify(record=true)`, `package_close`)
  flushes `data/*.jsonl`, and `export_html` / `handoff_emit` write package files beside it
  (`review.html`, `csv/`, `prompts/`, the target's `CLAUDE.md`). `work_bind` records the commit and
  dirties the tree AFTER it; if anything ran since your last commit, the tree is dirty again.
- Prefer this order: code work on the branch → land it → commit package writes on the branch the
  package is tracked on → bind → commit the binding.
- If the check catches something, commit it on the branch you are on before switching.
- *Why:* the act of recording a commit dirties the tree, so the habit "commit before branching" can be
  followed and still be wrong. *Field evidence:* after a bind stamped a sha, six JSONL files rode onto
  a feature branch and cost a full CI cycle to recover.

## 5. Branch from what the remote has

- Before `git checkout -b`, run `git rev-list --left-right --count @{u}...HEAD` and require `0 0`.
  A clean `git status` cannot see committed-but-unpushed work.
- If the local branch is ahead of its upstream, push first (on the operator's say-so where the
  project requires it), or branch from the remote branch explicitly.
- After a squash-merge, a `git pull` that will not fast-forward is the tell: verify the package tree is
  identical at both shas and drop the local commits — never a merge commit.
- *Why:* a squash-merge carries every unpushed commit below the branch point into the pull request.

## 6. Write a sha into a row only once the commit is on the remote

- This covers a `work_bind` ref, an `against_commit`, a digest attributed to a commit, and a sha quoted
  in a progress entry. If the commit is not pushed, push first, or bind after history is settled.
- After any history operation, check each sha a row names: `git merge-base --is-ancestor <sha>
  <remote>/<main>` (or `git branch --contains <sha>`).
- A bind is not the closing ceremony of the work. It only feels like one.
- *Why:* a rebase, amend, squash-merge or `reset --hard` rewrites shas and never touches the row.
  *Field evidence:* thirteen rows bound to an unpushed sha; a correct rebase renamed it, and the
  progress entry pointed at nothing.

## 7. A commit message may claim only writes you have re-read

- Before committing prose that says a row was written, re-read the row.
- When a batch is uncertain, under-claim: write what is verifiable, add rows afterwards.
- *Why:* no gate reads a commit message against the store, and a commit message reads as a receipt.
  Memory of an intention is indistinguishable from memory of an action.

## 8. Set a scope change to `Merged` last

- Apply the delta to every row its `scope_adds` / `scope_modifies` / `scope_removes` / `amends` edges
  name, RE-READ those rows, then set the `SC-` to `Merged`. An `amends` target merges by full-row
  upsert of a decision or by supersession of an ADR.
- If it is already `Merged`, run `trace_query` on it and open each target — the edges are the checklist.
- A sentence in a target that the scope change discharges ("needs a scope change first") is part of the
  delta. Rewrite it too.
- *Why:* nothing couples `Merged` to its delta; the readiness rule stops looking once it says `Merged`.

## 9. Cross-check git against the package by classifying, never by counting

- A commit whose whole content is a package write cannot cite its own sha. Never report the raw
  "unreferenced commits" set.
- Match shas mechanically, not from commit messages: for each unreferenced commit, `git show
  --name-only` and bucket by path — the package directory (expected), docs, notes or other
  non-source files (out of scope), source or tests (a real candidate). Flag only the last bucket.
- State the discriminator even when the result is empty, so a clean result reads as a check that ran.
- Never invent a verdict for a flagged commit: name it and let the operator decide.

## 10. The lock and the operator's word

- A refused `package_open` names the holder (pid, host, taken_at) and what the store observed about it
  (`not-running`, `reused`, `alive`, `unobservable`). `package_unlock(name)` reports it on demand;
  `package_unlock(name, confirm=true)` is the OPERATOR's word — never yours — and refuses on `alive` and
  `unobservable`. Never remove `data/.lock` on your own judgment: when the tool refuses, the manual
  removal is the operator's deliberate act — interview them; it is never yours.
- Every `operator_confirm: true`, every `force: true`, every `go_no_go`, every waiver row is the
  operator's explicit words from an interview in this session (`tamheed:operator-interview`); the JSON
  boolean is the word, never a value you supply because the ceremony expects it.

---

## What this skill does NOT cover

- **What to record** — the obligations table in the note is authoritative; this file never restates it.
- **Whether a record says what you think** — `tamheed:reading-the-record`.
- **Whether a test, a measurement or a CI run proves what you claim** — `tamheed:test-evidence`,
  `tamheed:measurement-evidence`, `tamheed:ci-evidence`.
- **How to put a decision in front of the operator** — `tamheed:operator-interview`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
