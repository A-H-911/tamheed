# Brief to ACMP — tamheed 5.3.0 (Interlude 11)

> **How to use this file.** It is read by path — nothing is pasted. The ACMP prompt is one line: *read
> `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.3.0.md` and execute it; the report is
> `findings_35.md`.* Everything below is a CLASS of result, never the field's counts — line counts
> included (the 5.2.0 brief's "21 lines" came from a copy; you read 19). Where a number appears it is the
> maintainer's own measurement on a read-only copy of the ACMP package taken 2026-09-27 (`e88b051b`),
> quoted so you can compare, not so you can carry it.

## 0. The 5.2.0 brief's errors, owned

E1 "nothing to do" on `prm-next.md` and the memory files — your rulings falsified four live sentences,
one of them a lesson status the file's own rule forbids; E2 "confirm (it binds and renders)" — the note
renders every pinned Approved lesson plus the 10 highest-numbered unpinned ones, so thirteen unpinned
approvals moved the sixteen it showed behind "19 more" (now the approval's `next` says which, §1 P3);
E3 "every result" — the `entity_query` cue rides every SUCCESSFUL result (an empty `count: 0`
included); a usage error carries none; E4 "21 lines" — a count from the maintainer's copy; E5 P4
omitted `diverged_stale_stock` and its STALE-STOCK warning; E6 "one partial" — two, and `CI-3 1860`'s
shell half is now in `package-writes` §7 (§2.1); E7 the classifier's 36 covered / 33 project-specific —
your re-read (11 / 26 / 32) was the measurement; twelve of the 26 partials carried a generic remainder
and entered the skills (§2.1). And the docs: `install.md` said `/reload-plugins` fires the hook — one
observation written as a mechanism; it now states both observations and names a restart as the route
the block arrives by every time.

## 1. The upgrade (part A; no interview needed)

1. Baseline as before: commit the package; `package_close()`; keep `gate_run()`,
   `readiness_check("package")`, `package_verify()` and `server_info()` outputs.
2. **Before the upgrade, create the trace file** (empty, outside any package — e.g.
   `C:\Users\ahammo\tamheed-hook.log`) and set `TAMHEED_HOOK_LOG` to its path in the environment
   Claude Code inherits (your shell before launching, or the `env` block of your USER settings — never
   a project's). The 5.3.0 hook appends one line per run there: `<utc> source=<startup|resume|clear|
   compact|fork> lines=N chars=N status=printed|silent|error:<Class>` — counts only, never the entry.
   A 5.2.0 hook writes nothing there, which is itself a reading.
3. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed`, then your
   reload route (`/reload-plugins` is documented now — "apply pending plugin changes to the running
   session without restarting it" — and the `/plugin` panel runs it when closed with pending changes;
   `/reload-skills` still is not documented). **Check the installed TREE against the tag**: with the
   marketplace at HEAD, `git -C C:\Users\ahammo\Repos\tamheed diff v5.3.0 HEAD -- plugins/tamheed` must be
   empty (your blob comparison is the same check). Then **read the trace file**: a line means the hook
   RAN on the reload; a line with no block in your context means it ran and nothing was delivered; no
   line means it did not run — **but read the reload's result only after a `/compact` has written a
   line** (delivery is known to work there): a compaction with the block in context and NO line means
   the variable never reached the hook subprocess, and the reload's "no line" was uninterpretable.
   Report which — that is the measurement 5.2.0 could not make.
4. **No migration.** `server_info` reads `5.3.0`, `migrations_head 007_handoff.sql`, `schema_version
   7`. No JSONL rewrites on the first write.

### Predicted classes (measured on the copy with the shipped engine)

| # | Probe | Class |
|---|---|---|
| P1 | `package_open` → `resume` | `handoff PE-1498`, `handoff_behind 0`, `open_feedback []`, `skill tamheed:package-writes`; **new:** `resume.lock` carries `observed: "alive"`, `evidence: "held by this session"` — the session's own lock is never probed; `server_info` while open says the same |
| P2 | the hook on a process restart with the previous server's lock left behind | the first line ends `holder observed not-running — package_unlock(confirm=true) on the operator's word` (the copy: your own pid 48276 read `not-running`); the lock file is still there — a read removes nothing; `package_unlock` remains the operator's act |
| P3 | the next lesson approval (`Approved`, any route) | `next` ends `; pinned rows always render` or `; it renders in the note only if pinned or among the 10 newest unpinned Approved rows - pin it to keep it visible`; a `substitute` status flip reads `pinned` from the stored row; a promotion carries no render clause |
| P4 | plain `handoff_emit` | every scan empty, no `skill` key, both `CLAUDE.md` files `unchanged` on a real package (the copy rebuilt the note once — a copy artefact: its path line differs), **plus** `diverged_stale_stock [{prompts/README.md, matches 5.2.0}]` and its STALE-STOCK warning (E5, listed this time) |
| P5 | `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]` (the 5.3.0 guide says "every successful `entity_query` result"); the note NOT rebuilt |
| P6 | `readiness_check("package")` | unchanged classes: `handoff-current` pass (every work entry), `lessons-stranded` pass over `promoted lessons`, `lessons-confirmed` and `feedback-unanswered` pass, `skill tamheed:operator-interview` while `ADR-0049`–`0051` / `AC-175`–`176` block |
| P7 | any `entity_query` | `skill: "tamheed:reading-the-record"` on every successful result; an error result none (E3) |
| P8 | the hook after `/compact` | `PE-1498` whole (the copy: 17 lines, no marker) and one line in the trace file with `source=compact`, whose `lines=`/`chars=` equal the printed block's, carrying none of the entry's text — the CONTROL for §1.3: this line proves the variable reaches the hook |
| P9 | `export_html`, `entity_export`, `AGENTS.md`, `prm-next.md`, the memory files | nothing new; every 5.2 class unchanged |

### Feedback dispositions

None to move: `FB-023`–`FB-025` are Resolved; no row was Reported this round. If findings_35 finds a
defect, file it as before (`kind`, the recipe, the numbers you measured).

## 2. Part B — ACMP-side, on the operator's word

1. **Twelve absorbed remainders, thirteen kept index lines** (plan 137; each re-read by the maintainer
   at the rule's own text, then written stack-neutral; 856 and 2649 are two index lines for one rule).
   The operator may now trim those thirteen lines, a `substitute` each, the Interlude 10 recipe — or
   keep them as the project's own wording; `CI-3 1860` is "trim or keep", since only its shell half
   was absorbed and its stack-specific half stays the project's:
   `LL-099` PROSE-1 1352 → `measurement-evidence` §3; `LL-101` PROSE-3 1128 → `measurement-evidence` §3;
   `LL-103` CI-2 1886 → `ci-evidence` step 1; `LL-104` CI-3 475 → `ci-evidence` step 4, CI-3 1860 (the
   shell half) → `package-writes` §7; `LL-106` TECH-2 1914 → `measurement-evidence` §2, TECH-2 856 and
   2649 → `reading-the-record` step 2; `LL-107` TECH-3 2453 → `test-evidence` §5; `LL-108` PKG-1 101 and
   1560 → `package-writes` §11; `LL-109` PKG-2 1542 → `measurement-evidence` §3; `LL-111` OPS-1 516 →
   `operator-interview` "What you cannot see". Verify each covering sentence in the installed 5.3.0
   copy before trimming (your `verify-quotes` recipe); a quote that fails is a finding. Not absorbed,
   on purpose: the fourteen project-only partials and the 34 project rules.
2. **Q1, measured properly this time.** This brief names the cues, so the session that runs it cannot
   measure whether a cue ALONE loads a skill. Measure Q1 in the first NORMAL-WORK session (DEF-218 on
   the operator's word) that has read no brief: on its first `entity_query`, did `reading-the-record`
   load, and on its first `package_open`, did `package-writes`? Record named → invoked / named → not
   invoked with the base dir. That session's `findings_35` addendum is the measurement.
3. **The close-out order** stands: status moves → the handoff LAST → commit `data/` → `work_bind`
   that commit.

## 3. `findings_35` — what to measure

- The trace file after the reload (§1.3): ran / ran-not-delivered / did not run.
- The hook after a process restart with a stale lock, if one occurs naturally: the observed line, and
  whether `package_unlock`'s report agrees with it (nothing manufactured).
- P3 on the next approval you make for the project's own reasons — not one made to see the hint.
- P8 after your first `/compact`: the block whole, the trace line's counts against the block.
- Q1 in the first brief-free session (§2.2).
- Any brief error, numbered E1… as before; any wrong class above is a finding, not a paraphrase.
