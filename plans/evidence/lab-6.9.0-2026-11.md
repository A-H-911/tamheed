# Plan 262: three headless runs on seeded lab copies (2026-11-27)

`scripts-262/rehearse_262.py`, under this bundle, `claude -p` with Opus, each run capped at
1.5 USD. Lab copies built by `scripts-248/setup_248.py` and `seed_248.py`. Scratch only, nothing
committed.

## Pass 1: void (1.58 USD)

Two harness faults, both fixed before pass 2:

1. The seeded "handoff" was a plain `note` entry. The resume block reads `handoff` entries only,
   so the run meant to show both signals showed one. The agent said so itself: "it was recorded as
   a plain note, not a handoff, so the resume block correctly ignores it."
2. A headless session ends without `package_close`, so its lock stays on disk. The create run met
   the lock of the run before it. It refused to unlock without the operator's word, and wrote
   nothing. The harness now clears a stale lock in scratch before that run.

## Pass 2 (1.66 USD)

| Run | What was seeded | What the agent did |
|---|---|---|
| both (0.58 USD) | SL-004: four journal entries with its `slice_id`, and the latest handoff names it | "Both signals are present: PE-072 to PE-075 carry `slice_id` SL-004, and the handoff names it. By the rule, it resumes at PE-075's resume point (WBS-6) with no new kickoff." It then flagged that the seeded handoff claimed an approved plan and work that git does not hold, and asked. That is the skill's rule for a carried claim |
| one (0.53 USD) | SL-004 Implemented. SL-005: one journal entry with its `slice_id`. The latest handoff names SL-004 | "SL-005 has only one of the two signals that it has started", and the choice went to the operator: resume, or `/tamheed:slice-kickoff` |
| create (0.55 USD) | The plain request: record a new defect and a new scope change. No word about `create` | It sent DEF-006 with `create: true`. It did not write the scope change: DEC-003 does not decide a `--json` flag, and no operator could confirm one |

Total for both passes: 3.24 USD of the round's 10 USD cap.

## What this shows

- Step 7's two signals work as R168 says, on both branches.
- A cold agent learned `create: true` from the surfaces that teach it (the tool's description,
  the note's table of obligations, the skills), with no word in the prompt. One run is one
  observation, not a rate.
