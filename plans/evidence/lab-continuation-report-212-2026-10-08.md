# Lab continuation report — beat 35, wired at birth (plan 212, 2026-10-08)

> `lab/scenario.md` beat 35: a fresh repository with no `CLAUDE.md`, the package created by a real
> agent through the headless harness (`plans/evidence/scripts-fb028/labrun.py`, Opus 5.5,
> `--plugin-dir` on the working tree, `--setting-sources ""`, `--permission-mode dontAsk`, the base
> allow list, never bypassPermissions), three turns, each a new client process and a new MCP server.
> The scratch repository (`beat35_setup.py`: the lab seed's `tracker.py`, `test_tracker.py` and
> `brief.md`, one git commit, no `CLAUDE.md`, no `AGENTS.md`) lived outside the repository and was
> never committed. The run's outputs are beside this report under `scripts-ste/labrun-212/` (the
> turns file, three result files, three reports, the hook trace, the setup, the capture script).
> The bundle's manifest still read 6.1.0 (the stamp is plan 213's); the served server was the
> working tree's.

## What the beat measures

Before 6.2 nothing pointed a repository at its package until stage 20's `handoff_emit`: the
SessionStart hook finds a package only through the note span in the root `CLAUDE.md` or one `@`
import, so a planning half ran with no resume block. The beat asks three questions of the served
process: does `package_create` wire the repository (the root pointer stub, the planning note in the
package's own `CLAUDE.md`)? Does a new process's hook then print the resume block through the
pointer? Does the stage 20 emit replace the planning note and leave the root untouched?

## T1 — the birth (session `9157b48b-d875-4e06-bfea-5b979cea6a02`, 8 turns, $0.23, no denial)

The agent listed the root (`.git`, `brief.md`, `test_tracker.py`, `tracker.py`: no `CLAUDE.md`),
called `package_create("lab", "Lab tracker", "rnd", "full")` and quoted the result's wiring:

```json
"wiring": {"root": "created", "package_note": "planning"}
```

The root `CLAUDE.md` it read back, whole:

```
# Lab tracker

<!-- Created by tamheed at the package's birth. This file is yours: project rules go above this
     comment, or in `AGENTS.md`, imported with a line reading `@AGENTS.md`. The section below points
     at the tool-owned Tamheed note; keep it. -->

## Tamheed progress tracking

@lab/CLAUDE.md
```

`lab/CLAUDE.md`, whole (the file opens with a blank line, the emit's shape):

```

## Tamheed progress tracking
<!-- tamheed:note v7 -->
The Tamheed package for this project is `lab`. The planning half is in progress: resume with `package_open("lab")`, read the `resume` block (`server_info()` carries it), and continue from the stage the latest handoff names. The operating note, the recording obligations and the rosters arrive with `handoff_emit` at stage 20.
<!-- /tamheed:note -->
```

Then one `handoff` journal entry, `PE-001` (actor `agent:lab-beat-35`, "Resume at: stage 1 (intake).
The brief is brief.md at the workspace root; nothing of it is archived yet. Awaiting the operator:
the mode."), and `package_close`. Nothing refused. The hook's trace line for this process reads
`source=startup lines=0 status=silent`: at its start the repository had no `CLAUDE.md`.

## T2 — the hook in a new process (4 turns, $0.32 cumulative, no denial)

The trace line reads `source=resume lines=6 chars=654 status=printed`. The agent quoted the block
before any tool call:

```
tamheed resume — package `lab` (schema 8) — unlocked
Handoff PE-001 (2026-10-08T09:36:54Z, agent:lab-beat-35); 0 work-done/transition entries since.
  Resume at: stage 1 (intake). The brief is brief.md at the workspace root; nothing of it is archived yet. Awaiting the operator: the mode.
Latest journal: PE-001 (handoff)
Next: Read handoff PE-001 and its corrections, then continue the planning half with /tamheed:tamheed at the stage it names. Invoke tamheed:package-writes before your first write, and write a fresh handoff (tamheed:session-handoff) before the next compaction
Skill: tamheed:package-writes — invoke it by name before your first write.
```

`package_open("lab")` returned `wiring: {"root": "present", "package_note": "present"}` (idempotent),
`resume.half` `"planning"`, and `resume.next` word for word the hook's `Next:` line. The lock line
read "unlocked" because T1 closed the package. Nothing refused.

## T3 — the emit (19 turns, $0.70 cumulative, one denial: `git status` under dontAsk)

On the operator's word the agent wrote `PRT-001` (kickoff, Approved; it added `PE-002` holding the
approval words, since the prompt table has no approver column) and set `entry_point` to `PRT-001`.
`handoff_emit` on the workspace root returned, quoted from the result:

- `warnings[0]`: "the planning-era note in `<ws>/lab/CLAUDE.md` was replaced by the operating note"
- `warnings[1]`: "`<ws>/CLAUDE.md` imports the package note (@lab/CLAUDE.md) — the managed span lives
  at `<ws>/lab/CLAUDE.md` and was rebuilt there. The root file was left untouched"
- `written`: `.mcp.json` (a standalone install under `--plugin-dir`, as in every lab run) and
  `<ws>/lab/CLAUDE.md`; `unchanged`: `CLAUDE.md`.

After the emit `lab/CLAUDE.md` holds one span (`<!-- tamheed:note` once as an opening marker; the
maintainer's grep counts the closing marker too, two lines) and "planning half is in progress" zero
times; the root `CLAUDE.md` is byte-equal to T1's quote; `server_info().resume.half` reads
`"execution"`. The handoff `PE-003` was written last, then `package_close`. The plugin refused nothing.
The one denial was the agent's `git status` under the harness's permission mode, not a plugin call.

## Captures

The guide's figures this beat changed (the three effects canvases that gain a `CLAUDE.md` write and
the five gate figures whose labels carry server line numbers) were captured EN/AR, light/dark, by
`capture_212.py` through the Python Playwright runtime, under `plans/evidence/captures-212/`.

## What the beat did not measure

- The front door: the approved plan's run A said "the kickoff as the whole prompt"; the turns were
  the operator's words naming `package_create`, so `/tamheed:tamheed` was never invoked. The served
  process and the real agent are the same; the skill's own path to `package_create` is not measured
  here.

- `jisr` itself: the operator's repository is wired by its first `package_open` under 6.2.0, after
  plan 213's release; this beat measured the same path on a scratch repository.
- A root with an existing `AGENTS.md` (the stub's import line) and a root with an existing
  `CLAUDE.md` without a Tamheed section (the appended pointer): covered by the contract tests, not by
  an agent run.
