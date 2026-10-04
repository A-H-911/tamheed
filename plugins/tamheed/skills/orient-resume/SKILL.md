---
name: orient-resume
description: >-
  Invoke after a session clear, a compaction or a handover to re-orient on this project's Tamheed
  package before any new work. It covers the lock, the gate, lessons, feedback, the git-vs-package
  cross-check, the active slice. Read-only until the operator confirms.
disable-model-invocation: true
argument-hint: "[package]"
---

# Orient / resume: after a session clear, compaction, or handover

Invoke this (`/tamheed:orient-resume`) to re-orient an agent on the `<package>` Tamheed package before
any new work.

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Orient yourself on this project's Tamheed package before doing anything else:

0. **The resume block first.** The plugin's SessionStart hook prints it at every session
   start, clear and compaction. `package_open` and `server_info` return it as `resume`. Read
   the latest `handoff` entry WITH its corrections before anything else. It says where the
   last session stopped, what awaits the operator and what not to redo. `handoff_behind`
   counts the work-done/transition entries written after it. You orient on those from the
   journal (step 4). No handoff at all: the journal is the resume state, and you write one
   before this session ends (`tamheed:session-handoff`). When the hook already printed the
   block, do not re-read what it showed. Go to the steps it leaves open. A handoff line
   marked `carried, not re-measured` is a claim about the past, not a fact. Re-measure it at
   its source before you act on it or put it to the operator.
1. `server_info`: confirm the server version and the resolved package root. **After a
   compaction the package is still open** (the MCP process and the lock survive). This is
   the first call, and it carries the resume block. Skip step 2. **A new client process is
   not a compaction.** `claude --resume`, a `claude -p --resume` turn, a new terminal: the
   server restarted with it, and the package is closed. A lock left on disk names a
   process that is gone (lab measurement, 2026-09-30). Step 2's refusal reports it, and a
   session that ends with `package_close` leaves nothing to unlock. The descriptions and
   schemas this session lists for the tools were read when the client process started.
   `server_info` names the server that answers. After a plugin update, only a client process
   started after it lists the new text. A reload restarts the server, not the listing (field
   measurement, 2026-09-30). Say so to the operator rather than read the listing as the
   server.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="orient-resume")`. Each carries what is true of this project for this ceremony.
2. `package_open("<package>")`: take the single-writer lock. If it refuses, the refusal
   says what the store observed about the holder. `package_unlock("<package>")` reports
   it. Removing a dead holder's lock (`confirm=true`) is the OPERATOR's word, never yours.
   Its result carries the resume block too.
3. `gate_run()`: note the verdict, any failing gate, and any G-TRACE warning.
4. The lessons: `entity_query("lesson", status="Approved")`. Confirmed lessons
   bind this session too. A large register pages: pass the result's `next_after`
   back as `after_id`. Never read `data/*.jsonl` to dodge a payload cap.
   **Search finds candidates. An exact read decides.** `search` matches every text
   column (the result's `matched` says which). A `columns` projection hides the
   rest (`omitted_columns`). Project to enumerate, never to answer *what is the state
   of X*.
   The feedback: `entity_query("feedback")`. Rows still Proposed await the operator's
   word (interview, never decide). Confirmed rows not yet Reported are owed to upstream
   (`entity_export("feedback.json", args={"type": "feedback"})` into the findings).
   A function you find missing this session is a new `FB-` row, never a script.
   Recent state: what was the last recorded activity? The resume block's `last_entries`
   names the three newest journal entries. `readiness_check`'s `handoff-current` names the
   work entries written after the latest handoff. Read them with
   `entity_query("progress-entry", ids=[...])`. The verdicts: `audit_evidence` in step 3's
   `gate_run` result. Never a read cut by `limit`. Rows come in id order and `limit` cuts
   from the lowest, so it returns the OLDEST rows (`tamheed:package-writes` §3).
5. **Cross-check git against the package** (the package is the state, git is the
   evidence). Run `git log --oneline -15` and match each commit's short AND full sha
   against the recorded `work_bind` refs mechanically (`entity_query("progress-entry",
   search="<sha>")` and `last_referenced` stamps). Never judge from commit messages,
   which cite ids whether or not anything was bound. For every unreferenced commit
   run `git show --name-only` and bucket by path. Commits touching ONLY the package
   folder are self-referentially unbindable (a package-write commit cannot cite its
   own sha, so this bucket is expected clean). Docs/memory-only commits are out of scope.
   Anything under source or tests is the only real candidate. Flag that last bucket alone,
   and report the discriminator with the result. "None: every unreferenced commit
   is a package write" is a check. A bare "no findings" is indistinguishable from
   not having looked. Do NOT invent verdicts for them.
6. Identify the active slice/phase: `entity_query("slice")`, `entity_query("phase")`,
   and the roadmap order. State which slice you believe is in progress and why.
7. Report back in five lines: package state, gate verdict, last recorded activity,
   unrecorded-work findings, and the slice you propose to resume. STOP for
   confirmation before writing anything. Resuming work on an approved slice →
   `/tamheed:slice-kickoff`. A cold agent that has never seen this package →
   `/tamheed:package-onboarding`.
