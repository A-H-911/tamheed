# Plan 150: tag v5.5.0, the brief file, close-out

> Maintainer-executed, 2026-09-27. Batch map: [146-150-batch-findings-36.md](146-150-batch-findings-36.md).
> The brief: [briefs/acmp-5.5.0.md](briefs/acmp-5.5.0.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## 1. The replay on a fresh copy

The field package and its control files, taken by `git archive` at the field's pushed head
(`27f63ae8`), with the final bundle over them (`acmp_replay4.py`, committed beside the evidence).
The first run stopped in its sweep, before the package was opened: the script printed a character
the console's code page cannot encode. The second run, with UTF-8 output, ran on the same
untouched copy.

| Probe | Result on the copy |
|---|---|
| `server_info`, closed | 5.5.0 / `007_handoff.sql` / 7 |
| `package_open` → `resume` | the latest handoff with one correction listed; `handoff_behind` 0; `open_feedback []`; lock `alive` / `held by this session` |
| `package_verify` before any write | `verified`, `dirty []`, `review_current` true |
| The first plain emit | `written`: the package's `CLAUDE.md` and a root `.mcp.json`; the root `CLAUDE.md` `unchanged`. Two lines of the note differ: the footer, and the path line. The path line and the `.mcp.json` are copy artefacts: the archive carried neither the field's path nor its `.mcp.json` |
| The note's roster before and after | the same ten rows |
| The second emit | nothing written |
| `refresh_stock` | refreshed the guide; its diff is the title and the lesson sentence, three lines out and five in |
| `readiness_check` | blocking `acs-met`, `adrs-approved`; `lessons-confirmed` pass; `lessons-note-budget` pass |
| `entity_query` | the cue on success; none on an error |
| `package_verify` after the emits, before the export | `review_current` true, the digest unchanged |
| `export_html` | the page rewritten, 927 bytes longer; 30 rows in the Approved fold; the ten marked equal the note's roster; the old page had no such column |
| `package_verify` after the export | `review_current` true, the digest unchanged |
| The hook after a compaction | the latest handoff whole with its corrections line; the trace line's counts equal the block's and its tail is the session id sent |

## 2. The recipe, and what it discharges

| Recipe | Result on the copy | It discharges |
|---|---|---|
| A `correction` entry naming the latest handoff | ok; `handoff-current` stays `pass`; the resume block and the hook list both corrections | the handoff's one line, and nothing else |

The other two places the ruling touches are files of the field's. They are named by path and line
and left to the operator's word. No recipe is prescribed for them.

## 3. The sweep

Four families on the copy: the memory files and both `CLAUDE.md` files; the decisions of the last
two interludes; the journal from the last interlude on; the live lessons. Eight hits.

| Hits | Where | Disposition |
|---|---|---|
| 2 | the field's trace memory file, one sentence on SDK-Python sessions | in the brief, §2.2 |
| 2 | the carried rule on what binds, its heading and its body | in the brief, §2.1 |
| 1 | the latest handoff, "it no longer binds" | in the brief, §2.1, with the recipe |
| 2 | the interlude's work-done entry: a reload "ran no SessionStart hook in this session", and SDK-Python sessions "wrote no line" | read and left: both true as written |
| 1 | an earlier correction: a Proposed lesson "binds nothing" | read and left: true |

The sweep does not read the field's findings files; they are not in the four families. Two lines
of `findings_36.md` were found by a separate grep. One is in the brief, the sentence that a
pushed-out lesson stops binding. The other quotes the 5.4.0 approval hint verbatim as a
measurement of that release; it is a dated record and stands.

## 4. Close-out

- `package-writes` and the other skills: no further edit.
- The batch record: EXECUTED, with W8 to W22 owned.
- Memory: the batch file and its index line.
- The advisor reviewed the brief and the record before the close-out commit.
- Push; CI green on all nine jobs; the tag `v5.5.0` on the release commit; nothing after it.

## Validation

| Check | Result |
|---|---|
| `uv run … --selftest` on the final bundle | 19 of 19 tools registered |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| `git diff v5.5.0 HEAD -- plugins/tamheed` | empty |
| The operator's trace file over every suite, beat and replay window | no line inside any |
