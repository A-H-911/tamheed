# Plan 156: what a limited read returns, the unbound commit, and three sentences

> Maintainer-executed, 2026-09-28. Batch map: [156-159-batch-findings-38.md](156-159-batch-findings-38.md).
> Field source: ACMP `findings_38.md` (§5 the `after_id` note, §6 the handoff draft, B3 the
> close-out), rulings R46, R47, R48, R50.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed, and what the maintainer's review added

- **The field typed an id into `after_id` to mean "from this entry on".** The cursor compares
  ids as text, and the read returned entries hundreds of numbers older. The field classed it as
  its own misuse and filed no feedback row.
- **The bundle taught the misreading.** `entity_query` returns rows in the id's text order and
  `limit` cuts from the lowest. Three teaching texts called a read limited to ten rows "the last
  recorded activity": `orient-resume` step 4, `loop-iteration` step 1 and the fresh-session
  paragraph of the follow-up template. The line dates from 2026-07-22. Run over the journal ids
  of the lab and of the field, the engine's own order returns the ten lowest ids on both.
- **Nobody was hurt, as far as the transcripts still on disk can say.** 685 transcript files of
  the field project, 1,335 `entity_query` calls from 2026-08-29 to 2026-09-28: none reads the
  journal or the verdicts with a bare `limit`. The resume block has carried the three newest
  journal entries since 5.1.
- **The field's handoff draft claimed the future twice,** and its advisor caught both. Since 5.6.0
  the commit, the bind and the export come after the handoff.
- **5.6.0 left one commit unbound at every close-out, and three lists called an unbound commit
  drift.** `orient-resume`, `package-writes` §9 and the follow-up template classify unreferenced
  commits by their paths. `integrity-check` step 6, `loop-iteration` step 1 and `drift-register`
  step 2 did not. `loop-iteration` runs unattended, and the drift steps bind "per orphan commit".
  The field did not hit it: its handoffs have said since 2026-09-26 that the final bind commit
  stays unbound by construction.
- **`integrity-check` step 5 exported the page inside a run that "changes nothing".** A bare
  export rewrites the package's committed page and `csv/`.

## The rulings (R46, R47, R48, R50)

- The three audit lists point at one rule, `package-writes` §9. No lint.
- `after_id` and the limited read: teaching only. The engine is unchanged, and no `newest`
  parameter is built.
- `session-handoff` gains the sentence on what follows the handoff.

Two changes go beyond the interview and were named at the approval: the sentence in
`entity_query`'s docstring, and `integrity-check`'s export to a path outside the repository.

## What changed

| File | Before | After |
|---|---|---|
| `tamheed_server.py`, `entity_query`'s docstring | byte order for `after_id`; nothing on what `limit` returns | one sentence: text order, `limit` cuts from the lowest, never the newest rows |
| `package-writes` §3 | "page with `after_id`" | the rule, what to read instead, and the field evidence |
| `package-writes` §9 | the classifying rule | the same, and the close-out's last commit named as unbound by rule |
| `orient-resume` step 4 | two reads limited to ten rows | the resume block's `last_entries`, the `handoff-current` list read with `ids`, `audit_evidence` |
| `loop-iteration` step 1 | a read limited to ten rows; "unbound package-relevant commits are drift" | the resume block; the classifying rule by pointer; a package-write commit is never bound there |
| `drift-register` step 2 | `git log` against the binds | the same, classified; a package-write commit is not an orphan |
| `integrity-check` step 5 | a bare `export_html()` | an export to a path outside the repository, the line read from the result's `path` |
| `integrity-check` step 6 | "package-relevant commits with no recorded binding" | the classifying rule by pointer; only source-touching commits are listed |
| `session-handoff`, the rules | — | the handoff says what is true when it is written |
| `follow-up-prompts.template.md`, `agent-control.template.md` | the limited read; "the latest `progress-entry` rows" | the resume block's entries |
| `references/prompt-templates.md` | the rows of `drift-register` and `integrity-check` | read against the new text and reworded |

## What the tools return, stated as it is

- The newest journal entries: `last_entries` holds three. `handoff_behind` is a count.
  `handoff-current` names the work entries written after the latest handoff, up to 50.
- The verdicts: `audit_evidence` holds three counts over each active criterion's latest verdict,
  with the ids of the narrated and the ungraded ones. `acs-met` lists the criteria whose latest
  verdict is not Met. A verdict write journals no row.
- **No tool returns the last ten rows of a family.** The skill says so. No hand-made method is
  taught in its place.

## Not changed, on purpose

- The engine's order. A contract test pins text order over ids of mixed width.
- The stock guide and `references/state.md`. Both teach paging and are true as far as they go.
- The eleven id lists the gates and the readiness rules return in text order. None chooses rows
  by that order, and no family but the journal has passed three digits.
- `integrity-check`'s instrument. The freshness line is still the newest stored timestamp of
  every table. The resume block's newest journal time costs no export and misses a register
  write that journals nothing.

## Tests (written first)

| Test | What it pins |
|---|---|
| `test_mcp_contract.py::test_entity_query_ids_search_and_refusals` | the docstring holds "never the newest rows"; a read of two rows returns the two lowest ids |

## Validation

| Check | Result |
|---|---|
| The new assertion before the edit | failed: the phrase was not in the docstring |
| `python check.py lint` after the edits | ALL CHECKS PASSED; 58 teaching files, 25 skills, lint 13 over 76 files |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| `limit=` with a number over the bundle, `docs/`, `lab/` and the README | 2 hits left, both reads of one row for `total` or for a paging walk |
| "last recorded activity" over the bundle | 3 hits, each naming what to read |
| `git log` over the bundle | 6 lists; each carries the classifying rule or a pointer to §9 |
| `git diff -- plugins/tamheed/server` | one file, docstring lines only |
