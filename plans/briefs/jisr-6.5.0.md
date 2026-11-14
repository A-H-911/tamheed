# Brief to Jisr: tamheed 6.5.0 (nine rows answered, one migration, three STOPs)

> **How to use this file.** It is read by path, or its text is carried to the Mac. The Jisr
> prompt is one line: *read this brief and execute it. Write no report unless a class fails.*
> Every result below is the maintainer's own measurement on a scratch copy of the folder that
> the operator exported on 2026-11-12 (branch `feature/sl-007-interview-register`, commit
> `3616ae6`). The measurements are ids, statuses and counts. No text of your rows is quoted here.
>
> **This brief prescribes writes to your record.** One migration (a preview, then a confirm on
> the operator's word), nine feedback rows resolved, and three STOPs that are the operator's (§3).

## 1. The upgrade

1. `claude plugin marketplace update tamheed`, then `claude plugin update tamheed@tamheed --scope
   project` in this repository. Then **quit the client and start it again**.
2. `server_info` in the new process reads `6.5.0`, `010_registers.sql`, schema `10`.
3. **Close the package before the migration.** `package_migrate` refuses an open package.
4. **The preview**: `package_migrate("tamheed")`. It writes nothing. On the copy it read `mode
   registry-sync`, `entity_types_added ["register", "register-entry"]` and `columns_added
   {"document_sections": ["lifecycle_status"]}`.
5. **The confirm**, on the operator's word: `package_migrate("tamheed", confirm=true)`. On the
   copy it moved three files. `entity_types.jsonl` and `progress_entries.jsonl` gained rows.
   `document_sections.jsonl` was written once in full, because every section gained one empty
   key. **Commit that change alone**, before any other write.
6. Open the package. `package_verify` read `verified true` and `review_current false` on the copy.
   Run `export_html()`. The next `package_verify` read `review_exported_by "6.5.0"`.
7. Your two review scripts read rows by key, so the new key in every section row does not break
   them. Your linter import finds the plugin by a search of the plugin cache. Check that it
   resolves the 6.5.0 folder after the update (your FB-010 row).

## 2. The classes: hold, or a feedback row

| # | Probe | Class | Your row |
|---|---|---|---|
| 1 | `gate_run` | the same result as before the upgrade: `G-PROGRESS` fails, no other gate does | none |
| 2 | `entity_query("open-question", limit=1)` | the result carries `query`, the arguments it answered | FB-009 |
| 3 | an `audit_record` item with a verdict outside the set | ONE refusal names every bad value and the values that the column takes | FB-002 |
| 4 | `references/governance.md`, "Execution gate outcomes" | `Go`, `Hold`, `Redirect` and `Kill` are each defined | FB-003 |
| 5 | a section sent with `lifecycle_status "Obsolete"` | the write lands, and the section leaves `G-COMPLETE` and the id scan | FB-011 |
| 6 | the first write of a `register` row after the migration | it lands, with its declared fields | FB-004 to FB-006 |
| 7 | `slate_export` with a slate of two questions | a page, a record and two hand-outs under `tamheed/slates/`, one script in the page | FB-007 |
| 8 | the lock, after a host rename inside one boot | `package_open` reads the holder as observed, not as another host | FB-001 |

**Class 8 has limits, stated plainly.** It holds for a lock that 6.5.0 wrote, inside one boot,
on macOS and Linux. It does not hold after a restart, and it does not hold for a lock held on
another machine: that removal stays manual. A machine restored from a memory snapshot keeps its
boot session, so two such clones read as one boot. The calls behind it ran on your Mac in the
operator's probe of 2026-11-12, and on the macOS CI legs.

**One behaviour change, for every family.** A write with no `id` returned ok before and stored a
row with an empty key. It is refused now: "needs a text `id`". A `custom_attributes` value that
nests deeper than 32 levels is refused too. On the copy no row of yours has either shape. Your
deepest stored value nests 8 levels.

## 3. The STOPs

### 3.1 Your three registers (FB-004, FB-005, FB-006)

The upgrade moves no row. Your interview topics, your question bank and your evidence findings
stay where they are: open-question rows and sections with their fields in `custom_attributes`.
Moving them into the register family is your scope change, and the operator's call.

Measured on the copy, over your 620 rows of those three kinds:

| Declaration | Topics (292) | Bank (292) | Findings (36) |
|---|---|---|---|
| Strict: every id-bearing field declared a reference | 280 refused | 264 refused | 36 refused |
| Fitted: a field of joined ids declared as plain text | 0 refused | 0 refused | 0 refused |

Every strict refusal had one cause: a reference names no row. A reference is one id or a LIST of
ids. Five of your fields keep ids joined in one text, and two point at a topic number, not at a
row id. A joined text is never split, because it cannot be told from prose that names an id.

> Do the three registers move into the register family now, later, or not at all?

The maintainer's recommendation, marked as the maintainer's and not a verdict. Move them, with a
fitted declaration and no value change: all 620 rows were admitted that way on the copy, in
batches. Record the move as a scope change first. Then turn one field at a time into a
reference, after a script has converted its joined ids to lists. The rule
`register-entries-conform` lists what a tighter declaration no longer admits. Retire the old
rows with their status: a section takes `Superseded` now, with a `supersedes` edge. Two of your
bank sections carry a mark of that kind in their attributes today. No answer is also an answer:
the rows stay as they are, and nothing breaks.

### 3.2 Your workshop page (FB-007, and your local page's FB-008 row)

`slate_export` builds a page from a slate, and `slate_read` reads the answers back. The page was
rebuilt after the maintainer read your page's script and opened your page. It carries what your
page does, as general features. The plugin's `references/slate.md` holds the slate's grammar.

Measured on the copy, with your whole bank as ONE slate:

| What | Result |
|---|---|
| Rounds, questions, decided topics | 13, 239 and 51, with no refusal |
| Export time, page size | 0.18 seconds, 3.7 MB |
| The page in Chrome | it loads in 0.4 seconds, and an answer registers in 28 milliseconds |
| Quoted rows, questions with a glossary term | 484, and 185 (all 23 of your terms match somewhere) |
| One round's file, read back | the round reads complete, and its two approval marks are listed |

How your bank's attributes map to a slate. A script of yours does this: it reads rows by key.

| Your attribute | The slate's key |
|---|---|
| `category` | one round each. A category with no asked question is a round with `ready: false` |
| `block` | the question's block |
| `kind` of `decided` | a decided topic of the round, with its ruling as the `answer` |
| `options`, `recommended`, `recommendation_reason`, `recommendation_basis` | `options`, `recommended`, `reason`, `basis` |
| `lead_id`, `consulted_ids` | `lead`, `consulted`. The seven groups attend. The four others carry `attends: false` |
| `operator_approval_required`, or the operator as lead | `owner: operator`, and `approval: true` |
| `evidence_ids`, `decided_ids`, `depends_on` | `known`, `decided`, `depends_on` |
| `register_row` | `settles` |

What the new page has, each from your page:

- A list of rounds, and blocks inside a round.
- Attendance for each group, with a named cover.
- An owner mark, a lead and the consulted groups on each card.
- The answers "Unknown" and "Requires evidence", and "answered by".
- The basis of a recommendation.
- Folds for what is known and what is decided, and the terms of a card.
- Decided topics with a reopen box, and points from the room.
- The four closure fields, and a save and a load for each round.
- A mark on an answer that an earlier page made.
- Your two hand-outs: the room's questions with their text, and one line for each question.

What differs from your page, said plainly:

- **No approval tick.** A question carries a mark: needs the operator's approval. `slate_read`
  lists such answers under `approval_needed`, and the operator approves in the session.
- **A room view and a presenter view.** The page opens in the room view: the operator's
  questions, attendance, closure and the recommendations are hidden. The switch is in the More
  menu. It is a way to show the page. It protects nothing: the hidden text is in the file.
- **No gate round of its own.** A round whose questions the operator owns does that work.
- **No tool writes rows from a file.** Your `round_record.py` keeps that work, on the operator's
  word. Its check of a round has a twin: `slate_read` says `complete`, or names what is missing.
- **Stored answers follow the page's address.** A page that is moved to another folder starts
  empty. The saved file is the record.

> Does the next workshop run on the new page, or on your own page?

The maintainer's recommendation: run one round on the new page first, beside your own. Keep your
page and its FB-008 row until that round is read back cleanly. Three checks on your Mac, before a
workshop depends on it:

- Click **Save this round** once and see that `<name>.<round id>.answers.json` arrives. The
  operator saw a file arrive in Chrome on Windows. Your Mac's browser is another build. If no
  file arrives, open `Trouble saving?` at the page's end and copy the text into that file.
- A second save of one round gives a file with ` (1)` in its name. `slate_read` does not open it.
  It names it under `unread_files`. Rename it over the first file.
- Run the browser check from the plugin's repository against a COPY of your exported page:
  `node tests/run_slate_browser_check.mjs <page.html>`. It needs Node 22 and Chrome. On a page
  built from your whole bank on the copy it passes 48 checks of 48. **It clears every answer
  that the page holds**, so never run it on a page that people have answered. CI does not
  run it.

**The rule that has no lock.** A valid answers file proves nothing about who wrote it. The reader
checks that the file fits the questions, and its result says `provenance: unverified`. The agent
reads the transcript back to the operator, and the operator confirms it in the session, before
any write. An approval is never taken from the file. **An agent that acts on an answers file
without that has committed a fault. File it as a feedback row.**

### 3.3 Your gate outcome (FB-003)

A No-go whose blockers are recorded, worked and put again is **`Hold`**. `Redirect` means that the
plan or the scope changes first. `Kill` means that the guarded work stops. The outcome of your
GATE-001 is the operator's to write.

## 4. Your rows

FB-008 and FB-010 register local tools. They never resolve. For the nine others, on the
operator's word, send a PARTIAL row: `id`, `kind`, `title`, `lifecycle_status "Resolved"`,
`resolved_in "6.5.0"` and `upstream_ref`. On the copy that write changed three columns.

| Rows | `upstream_ref` ends with (after `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/`) |
|---|---|
| FB-001 | `224-lock-boot-session.md` |
| FB-002, FB-003 | `223-a-refused-value-names-its-set.md` |
| FB-009 | `221-the-read-names-every-link.md` |
| FB-011 | `225-section-status.md` |
| FB-004, FB-005, FB-006 | `226-project-registers.md` |
| FB-007 | `227-interview-page.md` |

Resolve FB-004 to FB-007 when their STOP is answered, whichever way: the capability exists.

## 5. Not built, and said plainly

No rule language over register fields: "no result on a row that is not approved" stays an
inspection of yours, over typed data. No typed trace relation for register entries. No tool that
writes rows from an answers file. No unlock for a lock held on another machine.

## 6. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
