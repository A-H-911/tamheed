# Tamheed v4.14.0 — the findings_30 batch: `ready` follows its own doctrine, three honesty fixes, the sweep prompt's four gaps

Status: **APPROVED 2026-09-24 (revision 2, after the devil's-advocate review) — IN PROGRESS.** Index: [README.md](README.md) § Field cycle findings_30.
Read-only work only: `findings_30.md` in full; the sixteen `FB-` rows through ACMP's tool-written
`exports/feedback.json` (`count == total == 16`, `partial: false`; never `data/`); the journal
through `csv/progress_entries.csv` (1,380 rows; seven `system:` actors, all the engine's;
`PE-1362/1363/1378` bookkeeping, `PE-1376` attested, `PE-1365` `system:work-bind`); ACMP's diff
since findings_29 by file name; its memory/AGENTS.md rewrites checked (the four invalidated lines
replaced correctly; no contradiction); **every engine claim verified at the line**; the blast radius
of the `ready` change measured (tests, prompts, evals, fixture — every scope of a fixture COPY and
`make_complete_package` run through `readiness_check` today). One advisor pass; the second review
read the page renderer, the gate view, the fixture's omissions and the loop prompt the first draft
had only grepped. **No web
research**: every question is internal. Interview rulings (2026-09-24): **FB-016** `ready` = no
blocking fail AND no blocking indeterminate, with an `indeterminate` list, the transition guard
fail-only; **`expect_unchanged`** refuses a named column the final row does not carry (outside
`substitute`); **`deferred-work-reviewed`** lists Open + Scheduled only. No new tool (19); no
migration; MINOR, v4.14.0 — but the `ready` change is a behaviour change harnesses read, named first.

---

## 1. Weaknesses — my 4.13.0 brief, then this plan's first draft, then the engine

**The brief (owned in the next brief)**
1. **"A THIRD feedback warning"** — a run emits one line per state that has rows; ACMP saw exactly one.
   I counted warning kinds in code, not warnings a run emits — the same shape as "none should remain".
2. **§6's diff list omitted `tamheed-package/CLAUDE.md`** (the refresh rebuilds the note) **and the
   `system:work-bind` row §5 itself promised.**
3. **"3,259 bytes"** — characters (3,281 bytes).
4. **"The middle fold is now two"** implied both render; an empty fold is omitted (§1.10).
5. **findings_19 §3 was carried once more** — ACMP closed it: a `substitute` FK failure names the column.

**This plan's first draft**
6. It would have re-raised the transition guard: `quality-gates.md:72` already rules it trips on
   `fail` only. Not re-raised.
7. It treated FB-016 as an open design question. It is a doc-vs-code contradiction: `quality-gates.md:70-72`
   says "an empty slice is not a ready slice"; `tamheed_server.py:2715` says `ready: true`; and
   `tests/test_mcp_contract.py:655-658` pins the code ("indeterminate never blocks: ready reflects only
   the real failures") — two rulings in tension, now settled by interview.
8. It would have excluded `Activated` rows without checking what the state means: `docs/entities.md:190`
   ("`Activated` = the activation trigger fired") and `replan-deferred.md:24-27` (the WBS rows are
   created in the same scope change) — so the work is tracked as work; excluding is safe.
9. **It planned a `DW-` activation on the lab fixture, which has a RECORDED OMISSION for deferred-work**
   ("The lab tracker defers no work") and no `deferred_work.jsonl`. Creating a row there contradicts
   the record. Beat 21 verifies the rule's new population on a temp package (the contract test) and,
   on the fixture, only that `deferred-work-reviewed` still reads `pass` with `omitted`.
10. **It said the fixture's `SL-003` would carry `indeterminate: ["wbs-done"]`; measured on a copy it
    is `["acs-met", "wbs-done"]`** — the slice has neither ACs nor work items. The beat flips it with
    one `WBS-` row AND one AC with a Met verdict, or records why it stays.
11. **It did not know the review page already disagrees with the tool**: `export_html.py:771-785`
    renders a slice with zero ACs as "not ready" in the per-phase/slice panel while
    `readiness_check` says `ready: true`. The ruling makes the tool agree with its own page.
12. **It left `loop-iteration.md` "if needed"**: read, it says a blocking FAILURE is the stop and the
    harness line carries `ready=<true|false|n/a>`. An empty scope will now read `false` with no
    failure — the prompt needs one clause (a `4.14.0` key), and `loop-guard.md:16` stays as written
    (it names a failure).

**The engine (findings_30, each verified)**
13. `FB-016`: `ready = not any(blocking and fail)` (`:2715`); an `indeterminate` blocking rule leaves
   `ready: true`. The lab fixture's `SL-003` (Implemented, zero work items) reads the same.
14. `deferred-work-reviewed` lists `Open`, `Activated`, `Scheduled` (`:2407-2409`): permanent amber.
15. The pointer warning says "was updated there" unconditionally (`:3544`), even when `written: []`.
16. The unanswered fold is omitted when empty (`export_html._feedback:570-574`, `if rows:` for every
    fold), so "nothing outstanding" and "no such section" look alike.
17. `expect_unchanged` naming an unsent column passes and asserts nothing (findings_30 Q3) — last
    round's ruling, now vacuous in that case.
18. `register-liveness.md`: step 11 cannot discharge its rule; step 10 does not say "search across
    families for an existing ruling before framing the interview"; step 15 omits the render
    arithmetic (`_NOTE_LESSONS_CAP = 10` unpinned fill beside ALL pinned); step 7's `expect_unchanged`
    sentence is vacuous for a partial row.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by source or measurement**
- Every findings_30 citation (`:2715`, `:2407`, `:3544`, `:3120`, `export_html:570`).
- ACMP's package diff is the predicted set (feedback, progress_entries, the two prompts, CLAUDE.md,
  review.html, CSVs) plus the sweep's own writes (decisions, defects, deferred_work, scope_changes,
  trace_edges, wbs_items); nine `system:edge-retire` rows for `DEF-123`'s retirements.
- Blast radius of the `ready` change: tests at `:522/539/580/658/747/1821/2084/3065/3096` assert
  `ready` (658 computes from fails and must change; the plan-049 test's docstring says "`ready` is
  untouched" and must change); the `ITERATION: … ready=<true|false|n/a>` line in `loop-iteration.md`
  is parsed by harnesses (prose only — the value now means what the doc says; the body may not need
  to change); every `ready=True` in `evals.json` is `gate_run`'s, not readiness; the fixture's
  `SL-003` has zero work items (beat 21's subject); `slice-review.md`/`phase-close.md` read the rules,
  not `ready` alone.
- `_NOTE_LESSONS_CAP = 10` (`:3120`): all pinned + the 10 highest-numbered unpinned.

**Rejected**
- "a third warning" as a count of lines; "3,259 bytes"; "findings_19 §3 still open"; "excluding
  Activated goes dark".

- **Measured today on a fixture copy**: package `ready: false` already (`acs-met` fails); `PH-1`
  false already; `SL-001` true (stays); `SL-002` false already; **`SL-003` true → false** with
  `indeterminate: ["acs-met", "wbs-done"]`. `make_complete_package` at package scope is already
  `false` (two fails) with two blocking indeterminates (`adrs-approved`, `defects-closed`) — no test
  flips there; the acceptance check builds an empty slice instead (old tree `true`, new `false`).
- Every `ready=True` in `evals.json` is `gate_run`'s; the plan-049 eval greps the journal for
  "indeterminate" — unaffected. No test pins `deferred-work-reviewed`'s population or the pointer
  warning's text (only the rule-name tuple at `:3965`).
- The page's package-scope "Readiness: READY/NOT READY" (`export_html.py:627`) follows `ready`; the
  fixture is already NOT READY there, so its page bytes do not move for that reason.

**Unresolved — settled in execution**
- Whether `SL-003` should be made ready in the beat (one `WBS-` row Implemented + one AC with a Met
  verdict) or left `false` with the note recording why: the beat plan says try the first; if any
  guard refuses, record and keep the second — both are valid outcomes, the assertion is on the note.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The `ready` flip halts unattended loops on empty scopes | Doctrine-correct; named FIRST in the CHANGELOG lead and the brief as a behaviour change; `indeterminate: [...]` in the result says why; `loop-iteration.md` gains the clause "`ready: false` with no blocking failure means a blocking rule could not discriminate — `indeterminate` names it; record the rows it lacks, never report it as a failure" (+ key); the remedy is in the rule notes already |
| ACMP's 29 legacy slices read `ready: false` | They are Implemented history; `readiness_check` is a report and the transition guard is fail-only; the brief warns and gives the falsifiable probe (`SL-007` → `false`, `indeterminate: ["wbs-done"]`) |
| A fresh package reads `ready: false` at package scope | Only until omissions are recorded — the plan-077 doctrine; tests pin both readings |
| Refusing an unsent `expect_unchanged` column breaks the disposition recipe | The recipe never carried `expect_unchanged`; README/governance say "the recipe needs none — `changed_columns` is the proof"; the refusal names the remedy; engine-populated columns are in the final row and count as sent (the batch-29 security fix's position is kept) |
| Excluding `Activated` hides a fired row that never became work | `replan-deferred.md` creates the WBS rows in the same SC; the rule note names each state's discharge; the contract test fires an activation on a temp package and shows the row leaving the list; the fixture keeps its recorded omission untouched |
| The pointer warning's two texts | Tested both: first emission ("rebuilt there") and idle re-emission ("is current there; nothing written") |
| Stock bodies change (`register-liveness.md`; maybe `loop-iteration.md`) | `4.14.0` keys in the same commit; `refresh_stock` at release; `:3800` tuple unaffected (no rule renamed) |
| The fixture dirtied by a dry-run | Every dry-run on a scratchpad copy |
| An existing eval assertion falsified by the beat (F-6) | Before dispatch: grep `evals.json` for `ready`, `Activated`, `deferred-work-reviewed`, `Reported`, `SL-003` and re-aim in the plan |
| Docs edited unread | Transactional script, one match per edit; the readiness prose at `quality-gates.md:64-78` re-read today |

## 4. Changes made and why

1. FB-016 is executed as the doctrine already written, not as a new design (§1.7); the test at `:658`
   and plan 049's docstring are rewritten to say so.
2. `expect_unchanged` refuses the vacuous case only; the recipe is untouched (ruling).
3. `Activated` leaves `deferred-work-reviewed` (ruling), with the discharge of each state in the note.
4. Two presentation fixes with tests, no interview (obvious).
5. The `substitute`-as-status-flip use ACMP found (25 moves, zero transport) is documented as the
   cheapest correct status flip — no engine change.
6. Five brief errors owned; findings_19 §3 closed.

## 5. Refined execution plan

Constraints: stdlib only; no migration; no new tool; CHANGELOG under `[Unreleased]` until 111; stock
edits carry `4.14.0` keys; released blocks frozen. Per plan: record → RED → GREEN → `python check.py` →
reviewers where listed → dry-run on a fixture copy → commit from a message file (explicit staging) →
push → CI. Status every three minutes.

| # | Plan | Validation → expected |
|---|---|---|
| 106 | **`ready` follows its doctrine (FB-016).** `_readiness_report`: `ready = no blocking fail AND no blocking indeterminate`; result gains `indeterminate: [rule names]` (blocking only, rule order; `[]` when none); the transition guard at `:1439` unchanged. Tests: `:658` and the plan-049 test rewritten (an empty slice → `ready: false`, `indeterminate: ["acs-met", "wbs-done"]`; a `WBS-` row + an AC with a Met verdict → `true`, `[]`); `make_complete_package` at package scope pinned as it reads today (`false`, two fails, two indeterminates). Docs: `quality-gates.md:67-72` (the sentence now true, and "`ready` is false while any blocking rule is indeterminate"), server README `readiness_check` row, `docs/architecture.md`, **`loop-iteration.md` clause (+ `4.14.0` key)**; `loop-guard.md`, `slice-review.md`, `phase-close.md` read failures, unchanged (read, not grepped) | RED/GREEN; `check.py`; dry-run on a copy: `SL-003` → `false`, `["acs-met", "wbs-done"]`; `SL-001` stays `true`; the page's per-slice panel and the tool now agree |
| 107 | **Three honesty fixes.** (a) `deferred-work-reviewed` = `Open`, `Scheduled`; note: "Open: a human judges whether the trigger fired; Scheduled: whether the date came; Activated is work (its WBS rows), Done/Won't-do closed". (b) Pointer warning: "rebuilt there" when `pkg_content != pkg_existing`, else "is current there; nothing written". (c) `_feedback`: when the package has feedback rows and the unanswered fold is empty, render `<p class="empty" id="feedback-reported">No reported feedback awaits an answer.</p>` (other folds unchanged) | tests for each; export test extended; `check.py` |
| 108 | **`expect_unchanged` refuses the vacuous case; the sweep prompt's four gaps.** Engine: outside `substitute`, a named column not in the final `cols` → refusal "not sent: an omitted column is preserved by the UPDATE, naming it asserts nothing — drop it, or send it"; beside `substitute` unchanged; the batch-29 security PoC stays (engine-populated `lifecycle_status` counts as sent). `register-liveness.md`: step 7 clause; step 10 "before framing any interview, `entity_query(search=<id>)` across families for an existing ruling (a decision, an AC, a scope change)"; step 11 rewritten to the new population; step 15 the arithmetic (`_NOTE_LESSONS_CAP`); + `4.14.0` key. README/governance: the recipe needs no `expect_unchanged` | RED/GREEN incl. the refusal text; `:3800` tuple unchanged; `check.py` |
| 109 | **Docs + diagrams sweep** (transactional script): the `substitute` status-flip sentence beside the recipe (server README, SKILL.md); `docs/entities.md` deferred-work lifecycle row (what discharges the advisory) and the readiness prose; `docs/architecture.md` readiness paragraph (`ready` + `indeterminate`); SECURITY.md (the `expect_unchanged` vacuity closed); CHANGELOG `[Unreleased]` with the `ready` change first | per-behaviour grep ≥ 2 docs; `check.py` |
| — | **Full test**: `check.py`; `accept_v4140.py` N/N vs 0/N on an extracted `v4.13.0`; selftest 19/19; CI | N/N vs 0/N |
| 110 | **Lab beat 21** (agent, opus, worktree; dry-run on a copy AND the F-6 grep first, both cited in the plan file): `SL-003` reads `ready: false, indeterminate: ["acs-met", "wbs-done"]`; one `WBS-` row (Implemented) + one AC with a Met verdict flip it to `true` — or the note records the refusal that stopped it; `deferred-work-reviewed` reads `pass` with `omitted` on the fixture (no `DW-` row is created: the omission is recorded); the pointer warning's two texts on a scratch target; the empty-fold line on the page; `expect_unchanged` on an unsent column refused, quoted; the refreshed sweep prompt walked once | new assertions each failing on the pre-beat fixture (needles specific to this beat, never "indeterminate" alone — beat 14's note has it); evidence report; scenario beat 21 |
| 111 | **Release v4.14.0** (recipe; `refresh_stock` for the changed guides; stamps; tag; CI) | tag; CI |
| — | **The ACMP brief**, transcript-only: the five errors owned; findings_19 §3 closed; the `ready` change as the headline with the falsifiable probe on `SL-007` and the warning about loop harnesses; `FB-016` → Resolved (plan 106) by the recipe; the memory lines invalidated (`expect_unchanged` "asserts nothing" → refused; `deferred-work-reviewed` 44; `ready` semantics in `tamheed-package-mechanics.md`); `findings_31.md` questions | ACMP's row leaves `Reported` |

**Considered and rejected:** `ready: null` (a tri-state breaks boolean readers); making the
transition guard trip on indeterminate (ruled in the doc; would refuse every legacy empty slice);
excluding rows with no trigger; a `reported_at` column.

## 6. Approval checkpoint (approved 2026-09-24)

Approval authorized plans 106–111, commits, pushes and the `v4.14.0` tag
on `main` under the standing git delegation, and the ACMP brief. Behaviour and doctrine changes:

1. **`readiness_check().ready` is false when a blocking rule is indeterminate**, with an
   `indeterminate` list — every empty scope flips; loop harnesses reading `ready=` halt on an empty
   slice. The Implemented guard is unchanged.
2. **`expect_unchanged` refuses a named column the row does not carry** (outside `substitute`).
3. **`deferred-work-reviewed` no longer lists `Activated` rows.**
4. **The pointer warning tells the truth about writes; the empty unanswered fold renders a line.**
5. **Two stock prompt bodies change** (`register-liveness.md`, `loop-iteration.md`).
6. **Doctrine wording**: the recipe needs no `expect_unchanged`; `substitute` is the cheapest status
   flip; findings_19 §3 closed.
7. **MINOR release v4.14.0** with lab beat 21.

Approve as written, or name which of the seven to change.

## Execution notes (2026-09-24)

- Plan 106 exposed a second consequence of the doctrine: a package with NO defects and no `defect`
  omission reads `defects-closed` indeterminate at every scope, so no scope is ready until the
  omission is recorded — plan 077 applied uniformly; pinned by the test and said in quality-gates.
- Beat 21's F-9: a root `CLAUDE.md` importing `@package/CLAUDE.md` makes the FIXTURE the emission site;
  the next beat that exercises the pointer warning imports a scratch package name, never the fixture's.
- Beat 21's N-4: `lab/scenario.md`'s Pass bar described `SL-003` as deliberately empty by design; the
  beat that populates it must re-aim that sentence — the F-6 grep now covers `lab/scenario.md` too.
