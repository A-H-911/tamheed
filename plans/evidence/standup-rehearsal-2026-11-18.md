# Plan 252 — the headless `/tamheed:standup` rehearsal (2026-11-18)

**What ran.** `plans/evidence/scripts-252/rehearse_252.py` on a scratch copy of the lab fixture,
with this bundle (`5adc015`) loaded by `--plugin-dir`:

1. The workspace was built by `scripts-248/setup_248.py`, and the open slice SL-004 was added by
   `scripts-248/seed_248.py`, run A.
2. A first report was recorded in-process, signed `human:rehearsal-operator` (scratch only).
3. Work then moved in the window: WBS-5 was claimed done with a work-done line, WBS-6 was done,
   and AC-007 was met. The package-only commit leaves the store current.
4. One headless session ran: `claude -p "/tamheed:standup package"`, with `--setting-sources
   project`, `--permission-mode dontAsk`, no operator, the Opus model, and a 5 USD cap.

**Results (counts only):**

| Check | Result |
|---|---|
| Session | success, 21 turns, 0.78 USD, 66 s, 0 permission denials |
| The agent stated the slices | `slice_now` SL-004 (the suggestion), `slice_next` empty: SL-004 is the only open slice |
| Narrative keys | all ten, with `slice` at 58 words |
| Words per key against the shares | headline 26 (share 25), did 85 (150), challenges 104 (150), next 30 (100), plan 82 (125), slice 58 (100), colour_reason 22 (25) |
| Tool calls | 1 draft and 3 narrative attaches. The agent loaded `tamheed:plain-english` after the second attach. The likely cause is that the plain-English or id checks refused the first two drafts; the run's tool results were not read |
| Recorded by the agent | no: unattended, the skill does not record |
| The draft page | the nine sections in order (summary, needs, plan, did, now, next, challenges, glossary, record); exactly one script; the current slice marked "now"; both window states (done this window, claimed this window) present |
| The store after the run | RPT-001 Approved (the seeded first report), RPT-002 Draft; no lock left |
| Shell commands the agent ran | `git log --oneline -15` and `git status --porcelain -uall` only |
| ui-ux-pro-max (local scope in the tamheed repo) | not loaded. The debug log names its folder only in two cache-maintenance lines |

**Follow-up made.** An automated security review flagged the 248 allowlist: it allowed any
`git` and any `python` command. The script now allows `git log` and `git status` only, which is
everything the run used.
