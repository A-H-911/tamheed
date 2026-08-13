<!-- ================= TAMHEED EVIDENCE ARCHIVE — C37 =================
Archived verbatim from c:\Users\ahammo\Repos\acmp\findings_16.md on 2026-08-14
(v3.2.1 acceptance close-out — NO plan, NO release; findings_9/11 precedent).
Steps 1–2 CLEAN: the per-file template-acceptance path (delete prompts/README.md
→ re-emit) worked in the field on its first real use, closing the loop
findings_14 asked for and findings_15 confirmed on paper; both README additions
render, the lock section judged faithful to the findings_13 method. ZERO
tamheed defects. The one ⚠ is a phrasing observation, DEFERRED to the next
release: the lock guidance should read "delete when EITHER discriminator proves
staleness; keep the lock only when both pass" (either failure suffices — an
identity failure means pid reuse, an ordering failure means the process cannot
be the holder); the current stricter wording errs toward NOT deleting, the safe
direction. §6 (drift): STILL OPEN, operator-owned methodology — the headless
acceptEdits run blocked the tool path, so the null cannot distinguish "chose
not to record" from "could not" ("a measurement that cannot tell the two
states apart is not a verdict" — worth keeping); INSTRUCTION TRANSFER is now
proven in a SECOND independent context (the fresh session paraphrased the
obligations table and surfaced the is-a-flaky-repair-a-defect ambiguity as an
explicit decision). The last instrument: an INTERACTIVE fresh session,
operator-side. DEF-061's PUT→POST correction is ACMP-side. Evidence is
superseded, never edited.
================================================================== -->
# findings_16 â€” Tamheed v3.2.1 acceptance pass

**Steps 1 and 2: clean.** The per-file template-acceptance path works in the field, and both
documented additions render.

**Step 3 is filed here because the drift verdict is still not settled** â€” and the reason is
methodological, mine, not the tool's.

---

## âœ… 1 â€” the per-file path, first real field use

`prompts/README.md` appeared in `diverged` (6 stock prompts, up from 5) because its template moved
on. Taken exactly as documented: **deleted that one file, re-emitted** â†’
`emitted: ["prompts/README.md"]`, the current guide came back, the five customised prompts stayed
untouched and still report `diverged`, warning count 6 â†’ 5.

That closes the loop findings_14 asked for and findings_15 could only confirm on paper.

## âœ… 2 â€” both additions render, and the lock section is faithful

Header carries `(tamheed v3.2.1)`. The closing row â€”
*"Something project-specific | any other `.md` here â€” project prompts are operator-authored,
purpose-named; read the folder"* â€” fixes findings_15's README negative: a table-scanner is now routed
to the three `project-*.md` prompts.

The **"One session at a time"** section encodes the findings_13 Â§1 method faithfully, both
discriminators: identity (*"plausibly IS an agent session"*) **and** ordering (*"a process younger
than the lock cannot hold it"*).

âš  Wording nit, not a defect: *"Only when both say stale, delete"* is stricter than the logic requires
â€” **either** discriminator failing already proves staleness (a `conhost.exe` that started after the
lock cannot be the holder, whatever the other check says). It errs toward **not** deleting, which is
the correct direction for a destructive action, so this is a phrasing observation only.

## âš  3 â€” the drift verdict: STILL OPEN, and my instrument confounded it

I ran a **genuinely fresh primary session** this time â€” `claude -p`, Claude Code v2.1.229, not a
delegated agent â€” on a small real task (the flaky agenda-publish race) whose prompt said nothing
about recording, packages, or Tamheed. I released the package lock first and captured a baseline so
any write would be provable by diff, not by self-report.

**Result: no package writes.** defects 64 â†’ 64, progress 311 â†’ 311, edges 1052 â†’ 1052.

**But that null is not evidence of a choice, because I blocked the path.** I ran with
`--permission-mode acceptEdits` (deliberately, since project rules forbid
`--dangerously-skip-permissions`). That mode accepts *file edits only*. The session reported that
`git checkout -b`, `git switch -c`, bare `git branch` and `tsc --noEmit` were **all rejected by the
permission layer**. An MCP `entity_upsert` would almost certainly have been rejected the same way â€”
and it never attempted one, so I have no evidence about whether the tools were even reachable.

**I cannot distinguish "it chose not to record" from "it could not."** Reporting the null as a
behavioural verdict would be exactly the error this series keeps catching: a measurement that cannot
tell the two states apart.

### What the run *does* prove

**Instruction transfer, in a second independent context.** Unprompted, it wrote:

> *"CLAUDE.md's recording table says a found defect gets a `DEF-` row before the fix, plus
> `progress_update`/`work_bind` on the commit. Does a flaky-spec repair cross that bar for you, or is
> it below the line? Your call â€” I didn't write to the package either way."*

It read the table, paraphrased it correctly, and **surfaced the obligation as an explicit decision
rather than silently skipping it** â€” including the genuinely ambiguous question of whether a
flaky-test repair is a "defect" at all. It also declined to commit to `main` when it could not branch,
and said so.

So across two independent contexts the note transfers **completely**. What remains unproven is only
autonomous *discharge*, and no headless run can prove it without a permission posture I am not willing
to use.

### How Â§6 could actually be closed

An **interactive** fresh session (a human pasting the task into a normal Claude Code window, where MCP
calls prompt and can be approved) is now the only instrument left. Everything cheaper is confounded:
a delegated agent defers to its parent (findings_15), and a headless run cannot reach the tools.

## Bonus â€” the fresh session corrected one of my own rows

`DEF-061` records the racing call as a **PUT**. It is a **POST**:
`POST /meetings/{id}/agenda/items/{topicId}/presenter` (`meetings.ts:264`, `MeetingsEndpoints.cs:96`).

It also established two things my row did not:

- **The UI cannot help.** `AgendaBuilder.tsx:216` enables Publish on `items.length` alone, so
  Playwright's auto-wait-for-enabled offers no protection â€” the barrier must be the response.
- **Root-cause sweep: one site only.** `scenario.ts` sets the presenter inside the same
  `addAgendaItem` POST body, so its later publish is atomic; `dnd-and-failures.spec.ts` only asserts
  the disabled state.

The fix is preserved on `fix/e2e-agenda-publish-race` (`2e91b9d`), and `DEF-061` has been corrected.
âš  That commit is **not type-checked or run** â€” the same permission layer blocked both â€” so it needs
verification before merge.

---

## Summary

| Step | Verdict |
|---|---|
| 1 Per-file template acceptance | âœ… works in the field, first real use |
| 2 Table row + lock section | âœ… both render; lock method faithful Â· âš  "both say stale" is stricter than needed |
| 3 Drift verdict | âš  **still open** â€” transfer proven twice; discharge unprovable by any instrument I can run |
| Bonus | `DEF-061` corrected (PUT â†’ POST) by the fresh session |
