# Plan 162: teaching, docs and the corrections of 5.6.1

> Maintainer-executed, 2026-09-29. Batch map: [160-164-batch-findings-39.md](160-164-batch-findings-39.md).
> Follows plans 160 and 161. Rulings R51 to R55.

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW - **DONE**

## What this plan carries

Plans 160 and 161 changed the engine. This plan makes every text that speaks of the order, of
the two journal tools' keys, or of what a client reads, say what is now true. It also corrects
one sentence v5.6.1 shipped that was false when it shipped.

## The sites, as measured

A search by path over the bundle, `docs/`, `lab/` and the README, `.claude/` excluded, for
`after_id`, `next_after` and the words on id order: 28 hits, every one read.

| Disposition | Sites |
|---|---|
| Reworded: the order | `entity_query`'s docstring (plan 160); `package-writes`, "Read the store through the tools, at any size"; `orient-resume`, the step on recent state; `follow-up-prompts.template.md`, the fresh-session paragraph; `README.md`, the row of `entity_query`; `server/README.md`, the row of `entity_query` |
| Read and left, true | eleven sites that say `after_id` pages: the stock guide, `references/state.md`, `package-onboarding`, `slice-kickoff`, `integrity-check`, the front door, `docs/architecture.md`, `lab/scenario.md` item 2, and three more rows |
| Read and left, holds no claim on the order | `loop-iteration`, `agent-control.template.md`, `references/prompt-templates.md`. Revision 1 of the plan had listed them from memory |
| A dated note, never an edit | `docs/design-decisions.md` §19 |

## What changed

| File | Change |
|---|---|
| `skills/package-writes/SKILL.md` | the order by number, what `after_id` returns, the ceiling; a new entry on the two journal tools' keys, with the field evidence |
| `skills/orient-resume/SKILL.md`, `templates/follow-up-prompts.template.md` | "the id's text order" gives way to "id order, and `limit` cuts from the lowest" |
| `skills/tamheed/SKILL.md` | the journal's keys by their exact names |
| `skills/integrity-check/SKILL.md` | the staleness step says `csv/` lands beside the page at any `output` |
| `skills/measurement-evidence/SKILL.md` | one entry: a census over a pruned store names its horizon |
| `tamheed_server.py`, `export_html`'s docstring | `csv/` beside the page at any `output`; nothing removed in a caller's folder |
| `server/README.md` | the rows of `entity_query`, `progress_update`, `audit_record` and `export_html`; a paragraph at the selftest on which text a client receives |
| `README.md` | the rows of `entity_query` and of the execution-tracking tools |
| `docs/architecture.md` | the read side: one id order, and which text a client receives |
| `docs/install.md` | step 6 of the upgrade: what a session meets at 5.7.0 |
| `docs/design-decisions.md` | the dated correction of §19; §20, five rulings |
| `CHANGELOG.md` | the 5.7.0 entry, with the correction of 5.6.1 named by its line |
| `plans/156-159-batch-findings-38.md` | a dated correction beside the false row |
| `lab/scenario.md` | item 30 |
| `plans/README.md` | the findings_39 section |

## The correction of 5.6.1

v5.6.1 wrote that the order rule "now stands in the tool's description". Three shipped texts
said it: the changelog, the design record §19 and the batch record. The rule stood in a
docstring. Each text now carries a dated correction beside the sentence. None was rewritten.

## The lint caught two of my sentences

Lint 12 holds the skills free of field identifiers. My first wording of the order in
`package-writes` gave an id as an example of a typed bound, and then a pair of dotted ids as an
example of the ceiling. Both were refused. The entry says both without an id.

## Not changed, on purpose

- The stock guide's body. It says `after_id` pages, which holds. It changes in its title
  only, at the stamp.
- The diagrams. Nine diagram lines in three documents name the tools. None shows an order, a
  description or an item key.
- `SECURITY.md`. The three descriptions are built from constants of the code.

## Validation

| Check | Result |
|---|---|
| `python check.py lint` after the skills | refused twice on a field identifier, then ALL CHECKS PASSED |
| The words on text order, over the bundle, `docs/`, `lab/` and the README | see the batch record |
| "the tool's description", "every client", over the changelog, `docs/` and the last batch record | each hit carries its correction or is the correction |
| The loose key names | no hit left |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
