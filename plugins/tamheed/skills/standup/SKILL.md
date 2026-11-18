---
name: standup
description: >-
  Invoke to draft a standup report for the window since the last one. It says what we did, the
  challenges and decisions, and what comes next. The operator records it.
disable-model-invocation: true
argument-hint: "[package] [since: a date or a report id]"
---

# Standup report: what we did, the challenges and decisions, what comes next

Invoke this (`/tamheed:standup`) to write a standup report for the `<package>` package. The
operator, the team and a manager read it in 5 to 10 minutes.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). A second argument, a date (`2026-11-10`) or a
> recorded report id, starts the window earlier: that report is an override. Recording
> obligations: the note's table.

The window runs from the end of the latest recorded daily report to now. The first report
covers the package from its start, and it can run long. The engine finds what changed: new
rows, status moves and edits. It never sees work that nobody recorded. So bring the store up to
date first.

1. `package_open("<package>")` if it is not open. Then read the prompt rows bound to this skill:
   `entity_query("prompt", status="Approved", plugin_skill="standup")`. Each carries what is
   true of this project for this ceremony. Read the `resume` block of the open result.
2. **Is the store behind?** It is behind when `resume.handoff_behind` is above zero, or when a
   commit in `git log --oneline -15` names no bind (`entity_query("progress-entry",
   search="<sha>")` finds none). Then ask the operator (`tamheed:operator-interview`): run
   `/tamheed:progress-sync` first, or report what the store holds now. Never sync without
   their yes.
3. **Take the facts.** Call `standup_report()`. Add `start="<date or report id>"` when the
   operator named one. On the package's first report the tool asks for the operator's UTC
   offset: ask them (for example `+03:00`), then call `standup_report(utc_offset="+03:00")`.
   The result holds the facts, the rule colour with its reasons, and the word shares. It also
   writes `reports/draft.html`. The list of blocked work names a slice or a WBS item only
   while its blocker is not settled. A met dependency at `Implemented` blocks nothing.
   `plan_summary` sums up the plan tree that the page shows. It names each open slice with
   its counts and its open tasks. `plan_summary.suggest` names the first open slice in plan
   order and the one after it.
   - A refusal names its cause and writes nothing. Fix the cause, then call again.
   - A draft exists already: a new call replaces it, with the same id.
4. **Write the narrative** under `tamheed:plain-english`: short sentences, plain words, real
   ids in brackets. Keys:
   - `headline`: the bottom line in one or two sentences, about 25 words.
   - `did`, `challenges`, `next`: one summary for each question, about 150, 150 and 100 words.
   - `plan`: what you expect to do next, about 125 words. The page labels it as a plan, not
     a record.
   - `slice_now` and `slice_next`: the current slice and the next one, while an open slice
     exists. Read the record, and take the suggestion unless the work shows another slice.
     Then say why in `slice`. With one open slice, `slice_next` stays empty.
   - `slice`: what the current slice is for, what is done in it since it started, and what
     remains, about 100 words.
   - `colour` and `colour_reason`: see step 5.

   Say what changed and why it matters to the reader. Do not repeat the lists: the page
   prints them. Write for a manager who does not know the engine's words. Keep each key short,
   clear and to the point. The keys fill the page's sections: `headline` the summary, `did`
   "What we did", `slice` "What we are working on now", `next` and `plan` "What we expect
   next", and `challenges` "Challenges and decisions". Cite a row by its
   id: the page prints its title beside the id at the first mention.
5. **Propose the colour** by the default rule, which the facts call computes:
   - red: an open critical or high defect.
   - amber: an open high risk, or an open question past its date.
   - green: otherwise.

   The release rules that fail (under "Not ready to close yet") do not move the colour: they
   fail during normal work. You may propose another colour. Then give the reason in `colour_reason`. A colour that
   is not green needs `colour_reason` with the road to green: what turns it green, and when.
   The page shows the rule's colour beside the confirmed one when they differ.
6. **Attach the words:** `standup_report(narrative={...})`. The tool refuses an id that names
   no row, a plain-English hard finding, and text shaped as an instruction. A summary over its
   share of words is a warning only. Shorten it when you can.
7. **Show the operator the draft.** In the chat, give the headline, the proposed colour with
   its reason, and the "Needs from you" items. Give the absolute path of `reports/draft.html`.
   Open it in the browser: `start "" "<path>"` on Windows, `open "<path>"` on macOS,
   `xdg-open "<path>"` on Linux. Without a display (a headless run), give the path only.
8. **Ask the operator** (`tamheed:operator-interview`): record, revise, or discard. Ask which
   colour they confirm, and which slices are the current and the next one.
   - Revise: change the words and attach them again (step 6).
   - Discard: `standup_report(action="discard")`.
   - Record: `standup_report(action="record", confirm={"operator_confirm": true, "by":
     "human:<name>", "words": "<what they said>", "colour": "<their colour>", "slice_now":
     "<the current slice>", "slice_next": "<the next slice>"})`. The two slices are the ones
     your words state. When the operator names others, revise the words first. Quote their
     words. Never record without them, and never in unattended mode. The words stay in the row.
     The journal note and the pages leave them out, but `data/` is committed.
9. **After the record:** call `export_html()`, because the new row makes the review page stale.
   Then propose one commit: `reports/RPT-NNN.html`, `review.html` and `data/`. Run it on the
   operator's yes (`tamheed:package-writes`).
10. `package_close()`.

## A correction

A recorded report is never edited. To redo its words, call `standup_report(supersede="RPT-NNN")`.
The draft copies the window, the changes and the facts of that report. The result carries the
old words for reference. Attach new words and record them on the operator's word, as in steps 6
to 8. The old report moves to Superseded. A correction cannot change the facts.

## Withdraw a report

The newest daily report, or an override report, can be withdrawn on the operator's word.
When it is a correction, the reports it corrects go with it. A report that another row
names stays. Discard any draft first. Call `standup_report(action="withdraw", report="RPT-NNN", confirm={"operator_confirm":
true, "by": "human:<name>", "words": "<what they said>"})`. The row leaves the store, and
its page is removed. A journal note names the report, who and when. The words are not stored.
The id is never used again. Git history keeps the removed row, so this is no erasure. Prose
that cites the id keeps it, and the advisory `prose-ids-resolve` then lists it. Export
`review.html`, then commit on the operator's yes.

## Fresh lists, and the page alone

A correction and a regenerate keep the frozen facts. Only the newest daily report can take
fresh lists: withdraw it, then draft again. To start the chain again, withdraw the newest
report each time until none is left: the next draft is a first report, computed from
today. An older window cannot be counted again, because
the store keeps current state only. `standup_report(action="regenerate")` rebuilds the
pages of recorded reports from their rows, for a lost page or a page of an older release.
It changes no row.

## An open that fails on `standup_reports.jsonl`

A git merge of two branches can leave two drafts, or two recorded reports at one place in the
chain. `package_open` then refuses and names the file and line. Fix the file by hand, with the
operator:

- **Two draft lines:** remove one line. A draft is only a working copy.
- **Two recorded reports at one place** (the same `seq`): keep the report whose page is
  committed. In the other line, set `lifecycle_status` to `Superseded`. Then open the package
  and run `package_verify`.

When a later report finds that the stored reports stopped matching, it keeps the full state,
and its page says so. Record it as usual. The chain is whole again from that report.
