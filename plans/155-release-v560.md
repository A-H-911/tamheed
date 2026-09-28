# Plan 155: tag v5.6.0, the brief file, close-out

> Maintainer-executed, 2026-09-28. Batch map: [151-155-batch-findings-37.md](151-155-batch-findings-37.md).
> The brief: [briefs/acmp-5.6.0.md](briefs/acmp-5.6.0.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## 1. The replay on a fresh copy

The field package and the files a session reads before acting, taken by `git archive` at the
field's pushed head (`66ad54c4`, equal to its remote), with the final bundle over them
(`acmp_replay5.py`, committed beside the evidence). It ran once, 06:06:59Z to 06:07:08Z. Its raw
output quotes the field's own text and is not committed; the classes are here.

| Probe | Result on the copy |
|---|---|
| `server_info`, closed | 5.6.0 / `007_handoff.sql` / 7 |
| `package_verify` by name, package closed | `verified`, `dirty []`, `review_current` true, `review_exported_by` null |
| `package_open` → `resume` | the latest handoff, no correction listed; `handoff_behind` 0; `open_feedback []`; lock `alive` / `held by this session` |
| The first plain emit | `written`: the package's `CLAUDE.md` and a root `.mcp.json`; the root `CLAUDE.md` `unchanged`. One line of the note differs, in its path and in its clause on where the server is registered. Both are copy artefacts: the archive carries neither the field's path nor its plugin registration |
| The note's roster before and after | the same ten rows |
| The second emit | nothing written |
| `refresh_stock` | refreshed the guide; its diff is the title, one line out and one in |
| `readiness_check` | blocking `acs-met`, `adrs-approved`; `handoff-current`, `lessons-confirmed`, `lessons-note-budget` pass |
| `entity_query` | the cue on success, `count 0` included; none on an error |
| `package_verify` after the emits, before the export | `review_current` true, `review_exported_by` null, the digest unchanged |
| `export_html` | the page rewritten, 46 bytes longer, one line added: the version stamp, in the head. 30 rows in the Approved fold; the ten marked equal the note's roster |
| `package_verify` after the export | `review_current` true, `review_exported_by` `5.6.0`, the digest unchanged |
| A second export | byte-identical |
| A journal note after the export | `review_current` false, `review_exported_by` `5.6.0`; `handoff_behind` stays 0 |
| The export after that note | `review_current` true |
| The hook after a compaction | the latest handoff whole, no `Corrections` line; the trace line opens `version=5.6.0`, its counts equal the block's, and its tail is the session id sent |

## 2. No recipe

The brief prescribes no store write. Part B names files of the field's by path and line and
leaves each to the operator's word.

## 3. The sweep

By word, every hit read. Three words: the line's shape (`source=`, `status=printed`, `lines=N`),
`review_current`, and `export_html`. Over 102 live files (the memory files, the project skills,
the package's prompts, both `CLAUDE.md`, `AGENTS.md`) and three register families (the decisions
of the last two interludes, the journal from the last interlude on, the live lessons). 37 hits.

| Hits | Where | Disposition |
|---|---|---|
| 2 | the field's trace memory, the line's shape "(tamheed 5.4.0+)" | in the brief, §2.1 |
| 5 | the same file's dated measurements of single lines | read and left: dated records |
| 7 | journal entries and one lesson quoting a line as written | read and left: dated records |
| 2 | other files, the substring in an unrelated command and sentence | read and left: not the trace |
| 2 | the field's package-mechanics memory on `review_current` | one in the brief, §2.3: it cites a line of the plugin's README by number. The other read and left: true |
| 3 | three handoffs: `review_current` true "false again once this entry lands" | read and left: true, and the rule of plan 152 in the field's own words |
| 1 | the field's handoff-last memory: export, then the handoff | in the brief, §2.2 |
| 1 | the field's deployment memory, 2026-08-05: pushes time out, the page named as the cause | in the brief, §2.5. It contradicts a sentence the maintainer put to the operator |
| 14 | the other `export_html` hits | read and left: each exports after its last write, or states no order |

## 4. What the sweep found about the maintainer's own interview

The operator ruled that the page's weight is not studied this release (R42). The option read
"The field did not complain". The field's memory holds a line that records pushes timing out
and names the page. The maintainer had swept the field's findings file and its diff, and not its
memory, before asking. The question was put again before the tag, with the line quoted. The
operator's answer: "R42 stands, the brief asks ACMP to measure (Recommended)" (R45). The design
record says so, and the brief asks the field to measure with the instruments named.

## 5. Close-out

- The skills: no further edit.
- The batch record: EXECUTED, with W23 to W44 owned.
- Memory: the batch file and its index line.
- The advisor reviewed the brief and the record before the close-out commit. Its four points
  are in the batch record's execution note 7.
- Push; CI green on all nine jobs; the tag `v5.6.0` on the release commit; nothing after it.

## Validation

| Check | Result |
|---|---|
| `uv run … --selftest` on the final bundle | 19 of 19 tools registered |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| `git diff v5.6.0 HEAD -- plugins/tamheed` | empty |
| The operator's trace file over every suite, beat and replay window | no line inside any |
