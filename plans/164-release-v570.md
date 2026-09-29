# Plan 164: tag v5.7.0, the brief file, close-out, housekeeping

> Maintainer-executed, 2026-09-29. Batch map: [160-164-batch-findings-39.md](160-164-batch-findings-39.md).
> The brief: [briefs/acmp-5.7.0.md](briefs/acmp-5.7.0.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## 1. The replay on a fresh copy

The field package and the files a session reads before acting, taken by `git archive` at the
field's pushed head (`24e59125`, equal to its remote), with the final bundle over them
(`acmp_replay7.py`, committed beside the evidence). It ran once, 05:31:06Z to 05:31:17Z. Its raw
output quotes the field's own text and is not committed; the classes are here.

| Probe | Result on the copy |
|---|---|
| `server_info`, closed | 5.7.0 / `007_handoff.sql` / 7 |
| `package_verify` by name, package closed | `verified`, `dirty []`, `review_current` true, `review_exported_by` `5.6.1` |
| `package_open` → `resume` | the latest handoff, no correction listed; `handoff_behind` 0; `open_feedback []`; `last_entries` the three highest-numbered entries |
| Every family read through `entity_query` | 27 families, each in the independent order; two differ from their text order, the journal and the work items |
| `entity_query("progress-entry", limit=10)` | the ten lowest numbers of 1,546; none among `last_entries` |
| A full walk of the journal at `limit=100` | 1,546 rows in 16 pages, complete and in the order of the unlimited read |
| Every `after_id` call in the field's transcripts, 86 | each equals the independent cut: the engine's own read of the same search and status without the bound gives the set, and Python orders and cuts it with a key of its own |
| The field's read of 2026-09-11, as it typed it | `PE-954`, `PE-997`, `PE-1033` |
| `progress_update` with `summary`; `audit_record` with a key it does not take | refused by name with the keys the tool takes; no row written; the digest unchanged |
| `gate_run` | ready; `audit_evidence` 154 evidenced, 0 narrated, 1 ungraded |
| The first plain emit | `written`: the package's `CLAUDE.md` and a root `.mcp.json`; the root `CLAUDE.md` `unchanged`. One line of the note differs, in its path. Both are copy artefacts |
| The note's roster before and after | the same rows |
| The second emit | nothing written |
| `refresh_stock` | refreshed the guide; its diff is the title |
| `readiness_check` | blocking `acs-met`, `adrs-approved`; `handoff-current` passes |
| `export_html`, on a UTC date after the one the page carried | two lines out and two in: the stamp, and the line of the Readiness section, which changed in its stated date and nowhere else. The page's size unchanged. 29 CSV files unchanged. 30 rows in the Approved fold; the ten marked equal the note's roster |
| `package_verify` after the export | `review_current` true, `review_exported_by` `5.7.0`, the digest unchanged |
| A second export | byte-identical |
| `export_html(output=<a path outside the package>)` | the page there with `csv/` beside it, 29 files of the package's names; the package's page unchanged |
| A journal note after the export, then the next export | `review_current` false, then true |
| The hook after a compaction, on an untouched second copy | the latest handoff whole, no `Corrections` line; 19 lines, 3,189 characters; the trace line opens `version=5.7.0`, its counts equal the block's, and its tail is the session id sent |

**The walk's cost, through the real tool of each bundle on the same copy** (`walk_timing.py`,
best of 20): 6.0 ms on 5.7.0 and 0.9 ms on 5.6.1. An unlimited read of the journal ends at the
highest number on 5.7.0. On 5.6.1 it ended at `PE-999`.

## 2. The descriptions, as the SDK lists them

`uv run … --selftest` on the final bundle: 19 of 19 tools registered; 19 of 19 descriptions as
listed by the SDK; the longest 387 characters, under the cap of 2,048. The printout of the
registry is no evidence of this. The comparison reads the SDK's own listing.

## 3. The sweep

By word, every hit read. Five words: text order; `after_id`; the journal's keys beside
`progress_update`; the tool's description or a docstring; a row read by position. Over 108 live
files (the memory files, the project skills, the package's prompts, both `CLAUDE.md`,
`AGENTS.md`, the generators and their two library files) and three register families (the
decisions from `DEC-230`, the journal from `PE-1500`, the live lessons). Nine hits.

| Hits | Where | Disposition |
|---|---|---|
| 1 | `DEC-237`, its rationale | read and left: an Approved row's history |
| 1 | a memory file's quoted sentence on ids sorted as text | read and left: the field marked it corrected |
| 1 | "as text" in a memory file | read and left: not the store |
| 5 | `after_id` in a memory file, the guide, a lesson, twice in a journal entry | read and left: each says it pages, or records the field's census |
| 1 | a memory file that quotes a docstring of the server | read and left. It showed that a session can read a docstring from the file, which narrowed a sentence of the maintainer's (O16) |

**The sweep's limit.** A `git archive` copy holds tracked files. The field's ignored folders
were not read, and the brief says so.

## 4. The brief

- How the field takes the release, as the operator ruled (R53): the classes checked in an
  ordinary session, no findings file, a failure recorded as a feedback row.
- Errors owned, the plugin's and the maintainer's own among them.
- Every class with its condition. The first export's diff has three shapes.
- Every instrument named. The descriptions are read on the client's own tool listing.
- One dependency of the field read in part, said as such, with the field's own instrument.
- Part B: no sentence to reword.

## 5. Close-out

- The batch record: EXECUTED.
- Memory: the batch file, its index line, and lesson 2 of the 5.6.1 batch file rewritten.
- The advisor reviewed the brief and the record before the close-out commit.
- Push; CI green on every job; the tag `v5.7.0` on the release commit.

## 6. Housekeeping, after the tag (R54)

The state was read again before any removal. Three registered worktrees, each clean, unlocked,
with no branch on the remote, and `git cherry` printing `-` for each. Four more folders, empty.

```
git worktree remove .claude/worktrees/agent-a701f7e044476ffea
git worktree remove .claude/worktrees/agent-a7dd2ae7c975f513d
git worktree remove .claude/worktrees/agent-ac6565c644c37909f
git branch -D worktree-agent-a701f7e044476ffea worktree-agent-a7dd2ae7c975f513d worktree-agent-ac6565c644c37909f
rmdir .claude/worktrees/agent-a69a2c3405622e03c .claude/worktrees/agent-a81725e35e47fd82d
rmdir .claude/worktrees/agent-a92602e16cc5bba9b .claude/worktrees/agent-aa9df8e9aa6b74a92
git worktree prune
```

`-D` because the branches are no ancestors of main; main holds an equal patch for each. The
removal touches no tracked file, and its result is in the closing report, not in this commit.

## Validation

| Check | Result |
|---|---|
| `uv run … --selftest` on the final bundle | 19 of 19 tools registered; 19 of 19 descriptions as listed |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| `git diff v5.7.0 HEAD -- plugins/tamheed` | empty |
| The operator's trace file over the execution | 31 lines before the first run and after every run |
