# Brief to ACMP: tamheed 6.5.0 (your three rows answered, one migration, one STOP)

> **How to use this file.** It is read by path. Nothing is pasted. The ACMP prompt is one line:
> *read `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-6.5.0.md` and execute it. Write no
> report unless a class fails.* Every id below is a stable row of yours. Every result below is
> the maintainer's own measurement on a scratch copy of your package, taken on 2026-11-12 with
> the 6.5.0 engine. Your package was not opened and not changed.
>
> **This brief prescribes writes to your record.** One migration (a preview, then a confirm on
> the operator's word), three feedback rows resolved, and one STOP that is the operator's (§3).
>
> **What the copy cannot see.** A lock file stood in your `data/` when the copy was taken, so a
> session had the package open. A row written after the copy is not in these measurements.

## 1. The upgrade

1. `claude plugin marketplace update tamheed`, then `claude plugin update tamheed@tamheed --scope
   project` in this repository. Then **quit the client and start it again**.
2. `server_info` in the new process reads `6.5.0`, `010_registers.sql`, schema `10`.
3. **Close the package before the migration.** `package_migrate` refuses an open package.
4. **The preview**: `package_migrate("tamheed-package")`. It writes nothing. On the copy it read
   `mode registry-sync`, `entity_types_added ["register", "register-entry"]` and `columns_added
   {"document_sections": ["lifecycle_status"]}`.
5. **The confirm**, on the operator's word: `package_migrate("tamheed-package", confirm=true)`. On
   the copy it moved three files. `entity_types.jsonl` and `progress_entries.jsonl` gained rows.
   `document_sections.jsonl` was written once in full, because every section gained one empty
   key. The answer says so by name. **Commit that change alone**, before any other write.
6. Open the package. `package_verify` read `verified true`, `dirty []` and `review_current false`
   on the copy. Run `export_html()`. The next `package_verify` read `review_current true` and
   `review_exported_by "6.5.0"`.

## 2. The classes: hold, or a feedback row

| # | Probe | Class | Your row |
|---|---|---|---|
| 1 | `trace_query("FR-166")` | `column_links` holds `acceptance_criteria.requirement_id: [["AC-184", "FR-166"]]` | FB-032 |
| 2 | `trace_query()` with no id | every edge, in a fixed order, with `total` (1,930 on the copy) and a `query` echo | FB-030 |
| 3 | `entity_export(path="links.json", tool="trace_query", args={})` | one file holds every edge and every column link, `partial false` | FB-030 |
| 4 | `gate_run`, key `requirements_unwired` | exactly FR-156, FR-157, FR-158, FR-159, each with `missing ["work"]` | FB-031 |
| 5 | `readiness_check("package")`, rule `requirements-wired` | the same four ids, `missing` beside them, advisory | FB-031 |
| 6 | `gate_run` | `ready true`, no gate fails | none |
| 7 | the review page after the export | the readiness table shows `FR-156 (work)` | FB-031 |

A link lives in ONE place: a stored edge, or a foreign-key column. `edges` and `column_links`
are the two lists, and a census names which it read. Your lessons LL-149 and LL-157 state that
rule. The tool now returns both lists in one call.

**One behaviour change, for every family.** A write with no `id` returned ok before and stored a
row with an empty key. It is refused now: "needs a text `id`". A value that nests deeper than 32
levels in `custom_attributes` is refused too. On the copy no row of yours has either shape. Your
deepest stored value nests 4 levels.

## 3. The STOP: FR-156 to FR-159

Class 4 lists four `Implemented` requirements that have no work item. The rule is advisory, and
`ready` does not move. The list stays on every session's `gate_run` until one of two things
happens. Both are the operator's:

> Do FR-156 to FR-159 take a work item that records the work as done, or a waiver?

- **A work item** (`WBS-`) per requirement, or one for the four, with an `implements` edge to
  each. Your DEC-499 chose a history work item for a case of this kind. The rule then reads the
  work leg and lists nothing.
- **A waiver** (`WVR-`), which the operator authors, for the rule `requirements-wired` and those
  four ids. Both surfaces then list the ids under `waived`, never silently.

The maintainer's recommendation, marked as the maintainer's and not a verdict: the work item. It
states what was built, and a waiver expires. No answer is also an answer: the four ids stay
listed, and nothing else happens.

## 4. Your three rows

FB-030, FB-031 and FB-032 are answered by this release. For each, on the operator's word, send a
PARTIAL row: `id`, `kind`, `title`, `lifecycle_status "Resolved"`, `resolved_in "6.5.0"` and
`upstream_ref`. On the copy that write changed three columns and nothing else.

| Row | `upstream_ref` |
|---|---|
| FB-030 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/221-the-read-names-every-link.md` |
| FB-032 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/221-the-read-names-every-link.md` |
| FB-031 | `https://github.com/A-H-911/tamheed/blob/v6.5.0/plans/222-requirements-wired-legs.md` |

## 5. Also new, and nothing you must do

- **Project registers.** A record type that no family holds takes a declared register (`REG-`)
  and its entries (`ENT-`). `references/governance.md` has the grammar.
- **A section can be retired** with `Superseded` or `Obsolete`. It then leaves the scans.
- **The interview page.** `slate_export` writes a local page of questions, and `slate_read`
  returns a checked transcript of the answers files. A slate may hold rounds, participants
  and decided topics, so one page replaces a set of hand-built slates. The grammar is in
  the plugin's `references/slate.md`. A valid answers file proves nothing about who
  wrote it. The agent reads the transcript back, and the operator confirms it in the session,
  before any write. **An agent that acts on an answers file without that has committed a fault.
  File it as a feedback row.**
- **A refused value** names the values that the column takes. The four gate outcomes are defined.
- **The lock** recognises a renamed host inside one boot on Linux and macOS, for a lock that
  6.5.0 wrote. On Windows nothing changed: removal of a lock from another host stays manual.

## 6. Not built, and said plainly

No rule language over register fields. No typed trace relation for register entries. No tool
that writes rows from an answers file. No status filter on the two wired surfaces.

## 7. If a class fails

A feedback row in your package, `Proposed`, confirmed on the operator's word, with the class
number, what was read and the instrument. Nothing else is asked.
