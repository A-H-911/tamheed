# Plan 159: tag v5.6.1, the brief file, close-out

> Maintainer-executed, 2026-09-28. Batch map: [156-159-batch-findings-38.md](156-159-batch-findings-38.md).
> The brief: [briefs/acmp-5.6.1.md](briefs/acmp-5.6.1.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## 1. The replay on a fresh copy

The field package and the files a session reads before acting, taken by `git archive` at the
field's pushed head (`2cf7ab61`, equal to its remote), with the final bundle over them
(`acmp_replay6.py`, committed beside the evidence). It ran once, 09:59:54Z to 10:00:04Z. Its raw
output quotes the field's own text and is not committed; the classes are here.

| Probe | Result on the copy |
|---|---|
| `server_info`, closed | 5.6.1 / `007_handoff.sql` / 7 |
| `package_verify` by name, package closed | `verified`, `dirty []`, `review_current` true, `review_exported_by` `5.6.0` |
| `package_open` → `resume` | the latest handoff with one correction listed; `handoff_behind` 0; `open_feedback []`; lock `alive` / `held by this session`; `last_entries` the three highest-numbered entries |
| `entity_query("progress-entry", limit=10)` | the ten lowest ids in text order, of 1,540; none of them among `last_entries` |
| `gate_run`'s `audit_evidence` | 154 evidenced, 0 narrated, 1 ungraded |
| The first plain emit | `written`: the package's `CLAUDE.md` and a root `.mcp.json`; the root `CLAUDE.md` `unchanged`. One line of the note differs, in its path and in its clause on where the server is registered. Both are copy artefacts |
| The note's roster before and after | the same ten rows |
| The second emit | nothing written |
| `refresh_stock` | refreshed the guide; its diff is the title, one line out and one in |
| `readiness_check` | blocking `acs-met`, `adrs-approved`; `handoff-current`, `lessons-confirmed`, `feedback-unanswered`, `lessons-note-budget` pass |
| `package_verify` after the emits, before the export | `review_current` true, `review_exported_by` `5.6.0`, the digest unchanged |
| `export_html`, on the UTC date the page carried | one line out and one in: the stamp, `5.6.0` to `5.6.1`. The page's size unchanged. 30 rows in the Approved fold; the ten marked equal the note's roster |
| `package_verify` after the export | `review_current` true, `review_exported_by` `5.6.1`, the digest unchanged |
| A second export | byte-identical |
| `export_html(output=<a path outside the package>)` | the package's page unchanged |
| A journal note after the export | `review_current` false; `handoff_behind` stays 0 |
| The export after that note | `review_current` true |
| The hook after a compaction, on an untouched second copy | the latest handoff whole, with its `Corrections` line; 20 lines, 3,451 characters; the trace line opens `version=5.6.1`, its counts equal the block's, and its tail is the session id sent |

**One reading the replay settled.** The field's own trace holds two lines of 19 lines and 3,295
characters at the same head. They are `source=resume` lines. A compaction's block opens with one
line more, the sentence that says context was compacted, 155 characters and its line feed: 20
and 3,451.

## 2. No recipe

The brief prescribes no store write. Part B names one sentence of the field's by path and line
and leaves it to the operator's word.

## 3. The sweep

By word, every hit read. Five words: a limited read (`limit=` with a number, "last recorded"),
the newest rows ("latest", "newest", "most recent" beside an entry, the journal or a verdict),
`after_id`, "unbound", the page's bytes ("byte-identical", "wall clock"). Over 102 live files
(the memory files, the project skills, the package's prompts, both `CLAUDE.md`, `AGENTS.md`) and
three register families (the decisions from `DEC-230`, the journal from `PE-1500`, the live
lessons). 33 hits. Two more words were swept after the run, "deterministic" beside the page
and the names of the four skills that changed: no hit to act on.

| Hits | Where | Disposition |
|---|---|---|
| 1 | `AGENTS.md:13`, "the latest `progress-entry` rows", no method named | in the brief, §3: the operator's word |
| 4 | "the latest `handoff` journal entry (the `resume` block)" | read and left: true |
| 3 | `after_id` in a memory file, the guide, a lesson | read and left: each says it pages |
| 5 | "unbound" in a memory file, a decision, two handoffs | read and left: the rule 5.6.1 states |
| 19 | "byte-identical", "wall clock" | read and left: none speaks of the review page |
| 1 | a decision's "last recorded recurrence" | read and left: not the journal |

**The sweep's limit.** A `git archive` copy holds tracked files. The field's ignored folders
were not read, and the brief says so and asks.

## 4. The brief

- How the field takes the release, as the operator ruled (R49): at the start of its next
  ordinary session, four reads, no pre-registration, a one-page report.
- Errors owned, O1 to O9, the plugin's own among them.
- Every class with its condition. The first export's diff has three shapes, each with the
  condition it holds under; the UTC date is one of them.
- Every question with its instrument, and what the maintainer's own instrument could not see.

## 5. Close-out

- The batch record: EXECUTED.
- Memory: the batch file and its index line.
- The advisor reviewed the brief and the record before the close-out commit.
- Push; CI green on all nine jobs; the tag `v5.6.1` on the release commit; nothing after it.

## Validation

| Check | Result |
|---|---|
| `uv run … --selftest` on the final bundle | 19 of 19 tools registered |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| `git diff v5.6.1 HEAD -- plugins/tamheed` | empty |
| The operator's trace file over the execution | 26 lines when the plan's review read it, before the approval, and 26 after the replay: no line was added. Its last line is at 09:15:15Z; the first full gate of this batch ended at 09:38:59Z |
