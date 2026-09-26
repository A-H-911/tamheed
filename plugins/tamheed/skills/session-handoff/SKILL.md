---
name: session-handoff
description: >-
  Use BEFORE a context compaction, at the end of a session, and when handing the package to another
  agent or session: write the `handoff` journal entry that says where this session stopped — the
  resume point, the in-flight ids, what awaits the operator, the verified facts with the query that
  measured each, and what NOT to carry. Also whenever the resume block or the `handoff-current`
  advisory says the latest handoff is behind the journal.
---

# Session handoff

**The package is the state; the handoff is the one journal entry that says where a session stopped
in it. A resuming agent reads it first — through the `resume` block of `package_open` /
`server_info`, and from the plugin's SessionStart hook after a clear or a compaction.**

What a compaction summary loses first is exactly what the next turn needs: which row was mid-write,
which question is still open, which figure was measured and which was assumed. A `handoff` entry
(`progress_update`, `event_type: "handoff"`) keeps that in the record, typed, where the
`handoff-current` advisory can see when it falls behind.

---

## When

- **Before a compaction** you can see coming (a long session, a large tool result ahead). The
  SessionStart hook re-injects the latest handoff after `/compact`; it cannot re-inject what was
  never written.
- **At the end of a session**, after the last write of the close-out.
- **On a handover** to another agent, model or operator session.
- **When the resume block reports `handoff_behind > 0`** or `handoff-current` fails — the record
  moved past the last handoff.

## The shape — five short sections, ids not rows

Write ONE entry, under 25 lines and 4,000 characters — the SessionStart hook prints exactly that
much of it, and the `resume` block carries the same; past either cap the next session sees a
truncation marker and has to query for the rest — in this order:

1. **Resume at.** The next action, concretely: the slice or work item, the step of the ceremony, the
   exact tool call if one is half-done. One or two lines.
2. **In flight.** The ids touched this session whose state is not yet settled — rows in `Review`,
   an open scope change, a verdict recorded but not bound, a branch not yet merged. Ids only; the
   rows are the record.
3. **Awaiting the operator.** Every question put and not yet answered, verbatim with its options
   (`tamheed:operator-interview`): the next session must re-put it, not reconstruct it. State
   explicitly which rulings were GIVEN this session, by decision id, so nobody re-asks them.
4. **Verified facts.** Each fact with the query or command that measured it (`gate_run` verdict,
   the `readiness_check` blocking list, `git status --porcelain -uall` empty, a CI run id). A fact
   without its instrument is a memory of a fact — leave it out or mark it unverified.
5. **Do not carry.** What is history and must not be re-done: closed rows, questions already ruled,
   the branch already merged. A handoff that dispatches someone to redo finished work is worse than
   no handoff.

## The rules

- **Write it LAST.** After the session's final package write, `gate_run` and `export_html` — never
  from a snapshot taken earlier in the session. A handoff written before the last verdict landed
  went to the remote claiming criteria still open that were already Met, and sent the next session
  to close them again.
- **Quote live numbers from a query made after the last write**, never from memory of earlier in
  the session (`tamheed:measurement-evidence`).
- **Ids, never pasted rows.** The rows are live; a copy rots. Name them and say what to read.
- **A stale handoff is corrected, never edited.** The journal is append-only: `progress_update`
  with `event_type: "correction"` and `corrects: "<the handoff's PE-id>"`; the resume block returns
  the handoff WITH its correction chain, so the correction is read beside the sentence it retracts.
  When a whole new handoff replaces an old one, the newer entry is simply the latest — no marker on
  the old one is needed; its id no longer comes back.
- **Nothing instruction-shaped.** The entry is printed into the next session's context by the hook
  and screened by the injection gate; an entry the screen withholds reaches nobody. Write state, not
  commands to a reader.
- **Status moves first, the handoff, then the commit, then the bind.** A feedback row's or a
  skill row's status move is journalled by the engine as a `transition` and counts against
  `handoff-current` exactly like your own work-done entries — write those BEFORE the handoff.
  After it: commit the package `data/` with the rest of the close-out (`tamheed:package-writes`;
  an uncommitted handoff is destroyed by the next `git checkout`), then `work_bind` that commit —
  a bind is journalled as a `note`, so the handoff stays current and the commit stays bound. A
  field close-out that skipped the bind left its own handoff commit unrecorded.

## What this skill does NOT cover

- **Re-orienting when you arrive** — `/tamheed:orient-resume` (which reads the latest handoff first).
- **What else to record before you stop** — the obligations table in this project's `CLAUDE.md`
  note (work-done entries, verdicts, bindings).
- **The closing ceremonies** — `/tamheed:progress-sync`, `/tamheed:slice-review`,
  `/tamheed:release-close-out`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
