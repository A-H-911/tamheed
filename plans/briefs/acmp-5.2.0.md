# Brief to ACMP — tamheed 5.2.0 (Interlude 10)

> **How to use this file.** It is read by path — nothing is pasted (the 5.0.0 and 5.1.0 briefs were
> damaged in transit twice, even split in two). The ACMP prompt is one line: *read
> `C:\Users\ahammo\Repos\tamheed\plans\briefs\acmp-5.2.0.md` and execute it; the report is
> `findings_34.md`.* Everything below is a CLASS of result, never the field's counts; where a number
> appears it is the maintainer's own measurement on a read-only copy of the ACMP package taken
> 2026-09-26 (`30a33887`), quoted so you can compare, not so you can carry it.

## 0. The 5.1.0 brief's errors, owned

E1 the installed tree is marketplace HEAD, not the tag — this release tags the LAST commit, and §1
tells you how to check; E2 `skills.jsonl` rewrites on the first store WRITE, not the first close
(`store.dump` writes every table on every commit) — now in `install.md`; E3 `handoff-current`'s
population is every work entry, engine transitions included — the docs say so now; E4 the brief
predicted `stock_merged` false and it read true: that was the defect (FB-023), fixed; E5 the scans
run over every `prompts/*.md`; E6 paste damage — hence this file; E7 the diet was under-scoped and you
did it right; E8 eight twins, not seven; E9 no second copy of the handoff sentence — the AGENTS
template now points at the note's table instead of carrying one; E10 the Claude Code bug was already
sent; E11 the brief's order would have made a scan's silence vacuous (the skill-file scan reads
Approved rows only — it still does); E12 G-PROGRESS is a gate; E13 the root `CLAUDE.md` block: that
was FB-024, fixed; E14 `disableAllHooks` disables every hook — the docs now name disabling the
plugin as the only per-plugin opt-out.

## 1. The upgrade (part A; no interview needed)

1. Baseline as before: commit the package; `package_close()`; keep `gate_run()`,
   `readiness_check("package")`, `package_verify()` and `server_info()` outputs.
2. `claude plugin marketplace update tamheed`, `claude plugin update tamheed@tamheed`, then
   `/reload-plugins` and `/reload-skills` (your measured route; neither command is documented, the
   docs say restart). **Check the installed TREE against the tag, not the sha**: with the marketplace
   at HEAD, `git -C C:\Users\ahammo\Repos\tamheed diff v5.2.0 HEAD -- plugins/tamheed` must be empty
   (a docs-only commit landed after the tag — this brief's own correction — so `gitCommitSha` is
   HEAD's, while the plugin tree is the tag's; your 5.1.0 blob comparison is the same check).
3. **No migration.** `server_info` reads `5.2.0`, `migrations_head 007_handoff.sql`,
   `schema_version 7`. No JSONL rewrites on the first write. The hook fires on the reload as
   `SessionStart:resume` and prints `PE-1473` whole (it did on the copy: 21 lines, no marker).

### Predicted classes (measured on the copy with the shipped engine)

| # | Probe | Class |
|---|---|---|
| P1 | `package_open` → `resume` | unchanged: `handoff PE-1473`, `handoff_behind 0`, `skill tamheed:package-writes` |
| P2 | any `entity_query` | the result carries `skill: "tamheed:reading-the-record"` (every result, every family) |
| P3 | any `entity_export` | the file's `result` carries NO `skill` (a script's input never does); no churn in `exports/` |
| P4 | `handoff_emit` (plain) | `stale_references [] restated_content [] oversized_prompts [] stock_merged []` (you have no marker file any more), both `CLAUDE.md` files `unchanged`, NO `skill` key — the key appears only when a scan finds something to fix |
| P5 | `handoff_emit(refresh_stock=true)` | `refreshed: ["prompts/README.md"]` (the 5.2.0 guide names the `entity_query` cue and the marker's verification); the note is NOT rebuilt (its text did not change in 5.2.0) |
| P6 | `readiness_check("package")` | `lessons-stranded` pass with `population: {table: lessons, rows: <your Promoted count — 75 on the copy>, unit: "promoted lessons"}`; `handoff-current` pass, population every work entry (360 on the copy); the `skill` key `tamheed:operator-interview` while `ADR-0049`–`0051` / `AC-175`–`176` block |
| P7 | the FIRST `entity_upsert` of a skills row that changes `lifecycle_status` or sets `upstreamed_to`/`superseded_by` | the item returns `skill_audit: PE-N`; that entry is a `transition` signed `system:skill-guard` (`SKILL SKL-NNN -> <status> (was <status>)[; upstreamed_to …]`); **it counts toward `handoff-current`** — so write skill moves BEFORE the handoff (the `session-handoff` skill now says: status moves → handoff → commit → bind). An idle re-send journals nothing; an insert journals nothing |
| P8 | `export_html` | the readiness table shows `promoted lessons` in the `lessons-stranded` row |
| P9 | `AGENTS.md` | nothing to do: the template no longer carries the obligations table, and yours never did |
| P10 | the hook after `/compact` | the whole handoff up to 25 lines / 4,000 characters (5.1 cut at 2,000; measured through Claude Code: a 3,615-char entry came back whole) |

### Feedback dispositions (the partial-row recipe; the engine journals each move)

`FB-023` → Resolved, `resolved_in 5.2.0`, `upstream_ref "tamheed plan 129"` — `stock_merged` now
requires every line of the DECLARED release and attributes each absent line to the release that
introduced it (`missing_by_release`); replayed over your deleted `integrity-check.md` at
`c85e68d8`: `verified false`, 38 of 62, `{4.2.1: 2, 4.5.0: 18, 4.6.0: 18}` — the two 4.2.1 lines are
ones your copy rewrote, which is why the reason says "absent", never "never merged".
`FB-024` → Resolved, plan 130 — the block lives beside the note (the package's `CLAUDE.md` in the
pointer case), names agent-control/prompt/skill files, and a stale → clean cycle is byte-neutral; a
5.1-era block found in the root is stripped once and the warning says so (yours is already gone).
`FB-025` → Resolved, plan 132 — all sixteen, written from your retired files at `c85e68d8`, plus
the verified generic gaps below.

## 2. Part B — ACMP-side, on the operator's word

1. **`LL-099`–`LL-111` (the 113 carried rules).** A classifier placed every rule against the eight
   discipline skills: **44 generic candidates**, every one re-read at the file by the maintainer and
   **all 44 absorbed** in 5.2.0 (one only in part), condensed into about 30 sentences; the other 69 it
   placed as **36 already covered** by a twin and **33 project-specific** — those two classes were
   NOT re-read, so treat them as the classifier's verdict, not the maintainer's. Absorbed, by skill — `written-claims`: the whole PROSE-1 family (a status, a negative, a hedged count, an
   ordinal, a moving list, a restored table are a status with no timestamp: give the command), PROSE-2
   (a ruling falsifies prose that reasons from the old state: grep the id AND the advisory name, ship
   in the ruling's commit, every artefact in one batch), PROSE-3's attribution, code-comment judgement
   and regenerated-path rules; `ci-evidence`: CI-1 whole (every workflow, `cancelled`, attribute by
   signature, recording a red: new row vs appended occurrence, never re-run into silence, identical
   code disagreeing is a defect), CI-3's early-stopped job / checkout-vs-environment / one-at-a-time;
   `operator-interview`: the absent reason, per-item verdicts, re-put only on a moved premise;
   `measurement-evidence`: singular-over-plural (PKG-1's "every Approved slice"); `test-evidence`:
   coverage vs calls, the local race fix; `reading-the-record`: what binds is the note's roster;
   `package-writes` §12: parent/slice readiness, requirement ↔ deferred-work statuses, item + DW row
   together, ACs named on a done-claim, placeholder test rows, run the gate never carry its count,
   the unexplained branch, the shell chain that fails open. The operator's call, per lesson:
   confirm (it binds and renders in the note), trim its statement to the project-specific residue,
   or reject it as covered by the named twin. Suggested order: PROSE-1/2/3 and CI-1 first (largest
   overlap); TECH-* and the stack halves of CI-2/3 stay as project rules.
2. **The close-out order** from now on: feedback and skill status moves → the handoff LAST →
   commit `data/` → `work_bind` that commit (a bind is a `note`; the handoff stays current). Bind the
   commits Interlude 9 left unbound (`95841b0d`, `30a33887`) on the operator's word — or record
   why not.
3. **Nothing to do** on `prm-next.md` (57 lines), `AGENTS.md`, root `CLAUDE.md`, the memory files.

## 3. `findings_34` — what to measure

- Q1 again, for the two new cues: did `reading-the-record` load the first time an `entity_query`
  result named it, and did `written-claims` load if a `handoff_emit` ever carried the key (on a clean
  package it never will — say so rather than forcing a finding).
- The first skill-row write: the `skill_audit` id, the row's text, and `handoff-current` behind by
  one until the handoff.
- P3: an export file taken after the upgrade — no `skill` in `result`.
- P5: the guide refresh, the note NOT rebuilt.
- The hook after a `/compact` with a handoff longer than 2,000 characters: whole or cut.
- Any brief error, numbered E1… as before; any wrong class above is a finding, not a paraphrase.
