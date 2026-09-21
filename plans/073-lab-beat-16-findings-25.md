# Plan 073: Lab beat 16 — the findings_25 mechanisms, fired by a real agent

> **Executor instructions**: You are the lab's execution agent. Perform the beat below
> IN-PROCESS against the working-tree server, record every verbatim tool result and refusal
> text you observe, and follow the steps in order. Touch only the files listed as in scope. If a
> STOP condition occurs, stop and report — do not improvise. Commit in your worktree per the git
> workflow section; do NOT push, do NOT tag, and do NOT edit `plans/README.md` (the reviewer
> maintains the index). Report back: STATUS / STEPS (with the verbatim observations) / FILES
> CHANGED / NOTES.
>
> **Drift check (run first)**: `git log --oneline -1` must show `b18fcee` or a later commit that
> the reviewer named when dispatching you; `python plugins/tamheed/server/tamheed_server.py
> --selftest` must print `19/19 tools registered`.

## Status

- **Priority**: P1 — **Effort**: M — **Risk**: MEDIUM (it rewrites the recorded lab fixture)
- **Depends on**: 063–072 DONE + the acceptance pass (20/20 on the batch tree, 0/20 pre-batch)
- **Category**: lab / acceptance — **Planned at**: commit `b18fcee`, 2026-09-21

## Why this matters

The lab's claim is narrow and honest: *every mechanism fires under a real agent*. Beats 10–15
each exercised one release's mechanisms against the recorded package by continuation. Plans
063–071 shipped nine new behaviors; this beat fires the ones a lab can reach and pins them with
eval assertions, so the fixture that ships with v4.9.0 was produced by 4.9.0's own engine.

## Current state (what you need, inlined)

- Fixture: `evals/sample-results/lab-tracker/package` (eval-tier: validated by `gate_run` +
  `readiness_check` + the assertions, never byte-compared). Scenario: `lab/scenario.md` (beats
  listed in order; beat 15 is the last). Beat list prose: `lab/README.md`, section "How a
  release exercises the lab".
- Driver, exactly as beats 14–15 did it — small Python scripts, each opening and closing the
  package, run from the repo root:
  ```python
  import sys, pathlib, json
  sys.path.insert(0, "plugins/tamheed/server"); sys.path.insert(0, "plugins/tamheed/db")
  import store, tamheed_server as srv
  srv.PACKAGE_ROOT = pathlib.Path("evals/sample-results/lab-tracker").resolve()
  ```
  The package name is `package`. Print every result with `json.dumps(..., indent=1)`; your
  evidence report quotes them verbatim.
- `evals/evals.json`, case `lab-tracker`: `deterministic_assertions` is a list of
  `{"check": "...", "cmd": ["python", "evals/pkg_check.py", <subcommand>, ...], "expect_exit": 0}`.
  Primitives: `gates`, `count <pkg> <type> [--col K=V]... [--min N] [--max N]`, `nonempty`,
  `grep-present/absent <pkg> <needle> [--tables t1,t2]`, `grep-tree-present/absent <dir>
  <needle>`, `file-exists`, `grep-file <path> <needle>`, `verify`. `{case_dir}` expands to
  `evals/sample-results/lab-tracker`.
- Evidence report exemplar (mirror its shape):
  `plans/evidence/lab-continuation-report-059-2026-09-12.md`.
- The new behaviors (read each plan record under `plans/` if you need detail): 063 lock
  observation + lock-free migrate preview; 064 `package_unlock`; 065 `csv/` cleanup +
  `package_verify.foreign_csv`; 066 `server_info` package row + `detail=true`; 067 export
  envelope `partial` + `package_verify(expect=)`; 068 `omitted_columns` / `matched` / the lesson
  `next` hint; 069 rule `population`; 070 `prose-ids-resolve`; 071 stock prompts (five bodies
  changed: `README.md`, `integrity-check.md`, `replan-deferred.md`, `orient-resume.md`,
  `register-liveness.md`).

### Release discipline

No `plugin.json` bump; do not touch `CHANGELOG.md` (the reviewer writes the release entry), the
version stamps, `plugins/**`, or `tests/**`. The fixture changes ONLY through the tools, except
the lock files and the planted CSVs this beat writes and removes by hand, which the beat says so.

## Scope

**In scope**: `evals/sample-results/lab-tracker/package/**` (through the tools), `evals/evals.json`
(append assertions to the `lab-tracker` case only), `lab/scenario.md` (append beat 16),
`lab/README.md` (add beat 16 to the beats list), `evals/README.md` if it states an assertion
count for lab-tracker, `plans/evidence/lab-continuation-report-073-2026-09-21.md` (new).

**Out of scope**: everything else.

## Git workflow

One commit in your worktree:
`test(lab): beat 16 - the findings_25 mechanisms fired against the recorded package (plan 073)`.
Do not push, tag, or merge.

## The beat (append this to `lab/scenario.md` as item 16, then perform it)

> **16. The findings_25 continuation (v4.9.0).** A dead holder's lock: a child process writes
> `data/.lock` naming itself and exits; `package_open` refuses and SAYS what it observed
> (`not-running`); the read-only `package_migrate` preview answers anyway; `package_unlock`
> reports, then on the operator's word removes the lock and journals it. A LIVE holder's lock is
> refused. Then the legible reads: `server_info(detail=true)`, a projection that names what it
> omitted, a search that names where it matched, a readiness rule that reports its population;
> a phantom id in prose is caught by `prose-ids-resolve` and cleared by correcting the text; an
> export file that says it is partial and a digest that `package_verify(expect=)` confirms; a
> retired table's CSV removed while an operator's file survives; and `handoff_emit` with
> `refresh_stock` carrying the fixture's stock prompts to the 4.9.0 bodies.

## Steps

### Step 1: Baseline and backup

Copy the fixture's `package/` to a scratch directory outside the repo. Record `gate_run()`
(`ready`), `package_verify()` (`verified`, `digest`) and the `total` of `progress-entry` and
`defect`. Close the package.

### Step 2: The dead holder (plans 063–064)

1. With the package CLOSED, run a CHILD process (`subprocess.run([sys.executable, "-c", ...])`)
   that writes `evals/sample-results/lab-tracker/package/data/.lock` as JSON with `pid` =
   its own `os.getpid()`, `host` = `socket.gethostname()`, `taken_at` = now (UTC ISO),
   `started` = `store.process_start_time(os.getpid())[1]`, `identity` =
   `store.process_identity(os.getpid())`, and then exits. The pid is now dead.
2. `srv.package_open("package")` → expect a refusal. Quote it verbatim; it must contain
   `observed: not-running` and name `package_unlock`. (If the OS recycled the pid within that
   instant the outcome is `reused` — also acceptable; record which.)
3. `srv.package_migrate("package")` → expect the "nothing to migrate" answer containing
   `read while locked`. Quote it.
4. `srv.package_unlock("package")` → `stage: report`, `would_unlock: true`. Quote it. Confirm the
   lock file is byte-unchanged.
5. `srv.package_unlock("package", confirm=True)` — **the operator's word for this beat is given
   by this plan** → `stage: unlocked`, `journaled: true`, a `journal_id`. Quote it. Open the
   package and quote that `progress-entry` row (`event_type: forced-override`, actor
   `system:package-unlock`). Close.
6. The LIVE holder: write a lock naming THIS driver process (`os.getpid()`, this host, now,
   `started` and `identity` from the `store` functions). `srv.package_unlock("package",
   confirm=True)` → expect a refusal naming `alive`. Quote it. Then delete that planted lock by
   hand (you wrote it; say so in the report).

### Step 3: The legible reads (plans 066, 068, 069)

Open. Quote: `server_info()`'s `package` block; from `server_info(detail=True)` the count of
`entity_types`, the `defect` entry, and `relation_rules["mitigates"]`. Then
`entity_query("defect", columns=["id","title"], search=<a word you know occurs only in some
defect's `custom_attributes` or a non-projected column; if none exists, search a title word>)` —
quote `omitted_columns` and `matched`. Then `readiness_check("package")`: quote the
`population` of `defects-closed` and the status + population of `lessons-confirmed`.

### Step 4: The phantom id (plan 070)

Upsert a new defect (next free `DEF-` id, severity `low`) whose title is
`export header drifts after RISK-909 (see DEF-001)`. `readiness_check("package")` → quote the
`prose-ids-resolve` entry: it must name `<that id>.title -> RISK-909` and NOT `DEF-001`. Then
correct the row: same id, full row, title `export header drifts (see DEF-001)`. Quote the rule
again — it must pass. (Do not try to "fix" any other entity the rule may name; record it as a
finding instead.)

### Step 5: The export and the digest (plan 067)

`entity_export("beat16-defects.json", args={"type": "defect", "limit": 1})` → quote the tool
result, then read the FILE and quote its `tamheed_export` envelope: it must carry `count`,
`total` and `"partial": true`. Take `package_verify()`'s `digest`; `package_verify(expect=<it>)`
→ `matches_expected: true`. Quote both.

### Step 6: `csv/` (plan 065)

By hand, write `package/csv/prompts.csv` with the single header line
`id,prompt_kind,title,body,phase_id,custom_attributes,last_referenced` plus one data line, and
`package/csv/operator-notes.csv` with `my,own` / `1,2`. `package_verify()` → quote
`foreign_csv` (both names). `export_html()` → quote `csv.removed` (`csv/prompts.csv`) and
`csv.unowned` (`csv/operator-notes.csv`). Then delete `operator-notes.csv` by hand (you wrote
it; say so) and run `export_html()` once more → `removed: []`, `unowned: []`.

### Step 7: The stock prompts (plan 071)

`handoff_emit(target_dir=<a scratch directory outside the repo>, refresh_stock=True)` → quote
`prompt_library.refreshed` (expect the five changed bodies, as `prompts/<name>`) and any
`diverged`/`customized` list. No `force`.

### Step 8: Close the beat

`progress_update` ONE closing `note` entry (actor `agent:lab-beat-16`) that narrates the beat
and quotes, verbatim, the `observed: …` clause of the Step 2 refusal, the `alive` refusal, and
the `prose-ids-resolve` entity string. Then `package_verify(expect=<the Step 5 digest>)` →
`matches_expected: false` (any write moves the package digest — quote it; this is the lesson the
field learned the hard way). `export_html()`, `gate_run()` (must be `ready: true`),
`package_verify()` (must be `verified: true`, `foreign: []`, `foreign_csv: []`),
`package_close()`. Confirm no `data/.lock` remains.

### Step 9: Assertions (`evals/evals.json`, case `lab-tracker`, appended after the last one)

Add these (adapt a needle only if your verbatim text differs, and say so in the report):

```json
{"check": "A dead holder's lock was removed through the sanctioned tool and journaled (plan 064).",
 "cmd": ["python","evals/pkg_check.py","count","{case_dir}/package","progress-entry","--col","actor=system:package-unlock","--min","1"], "expect_exit": 0},
{"check": "The unlock journal row is a typed forced-override naming the observation (plans 063-064).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","FORCED lock removal","--tables","progress_entries"], "expect_exit": 0},
{"check": "The beat's note quotes what the store OBSERVED about the dead holder (plan 063).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","observed: ","--tables","progress_entries"], "expect_exit": 0},
{"check": "A live holder's lock was refused, and the note says so (plan 064).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","alive","--tables","progress_entries"], "expect_exit": 0},
{"check": "The phantom id was caught and then corrected out of the defect's prose (plan 070).",
 "cmd": ["python","evals/pkg_check.py","grep-absent","{case_dir}/package","RISK-909","--tables","defects"], "expect_exit": 0},
{"check": "The beat's note names the prose-ids-resolve finding (plan 070).",
 "cmd": ["python","evals/pkg_check.py","grep-present","{case_dir}/package","RISK-909","--tables","progress_entries"], "expect_exit": 0},
{"check": "The export FILE says it is partial (plan 067).",
 "cmd": ["python","evals/pkg_check.py","grep-file","{case_dir}/package/exports/beat16-defects.json","\"partial\": true"], "expect_exit": 0},
{"check": "The fixture's prompt guide carries the 4.9.0 stock body (plans 064, 071).",
 "cmd": ["python","evals/pkg_check.py","grep-file","{case_dir}/package/prompts/README.md","Show the record with its id"], "expect_exit": 0},
{"check": "No orphan CSV survives in the fixture (plan 065).",
 "cmd": ["python","evals/pkg_check.py","grep-tree-absent","{case_dir}/package/csv","prompt_kind"], "expect_exit": 0}
```

If `exports/` is ignored by the fixture's git rules so that `beat16-defects.json` cannot be
committed, replace that one assertion with a `grep-present` for the word `partial` in the closing
note and quote the envelope in the note instead; say so in the report.

### Step 10: Docs + evidence + gate

Append beat 16 to `lab/scenario.md` and to the beats list in `lab/README.md` (one clause, in the
list's own style). Write `plans/evidence/lab-continuation-report-073-2026-09-21.md` in the
exemplar's shape: a header quoting the context, a numbered tool-call log with verbatim results
and refusal texts, a table mapping each mechanism to `observed` / `not observed`, and the three
verification commands' results:
`python evals/pkg_check.py gates evals/sample-results/lab-tracker/package` → `ready=True`;
`python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → all pass;
`python check.py` → `ALL CHECKS PASSED` (over two minutes — background it and wait). Then commit.

## Done criteria

- [ ] `python evals/run_evals.py --results-dir evals/sample-results --case lab-tracker` → all pass
      (35 existing + the new assertions)
- [ ] `python check.py` → `ALL CHECKS PASSED`
- [ ] `git status --short` shows only in-scope paths; no `data/.lock`, no `operator-notes.csv`
- [ ] the evidence report exists and every mechanism row says `observed` or states why not

## STOP conditions

- The drift check fails, or `--selftest` does not print `19/19`.
- `gate_run()` is not `ready: true` at baseline, or `package_verify()` is not `verified`.
- Any tool result contradicts what this plan expects in a way you cannot explain from the plan
  records — quote it and stop; a surprising observation is a finding, not something to work around.
- A step would require editing anything under `plugins/` or `tests/`.
- `package_unlock(confirm=True)` refuses in Step 2.5 with an outcome other than the ones named.

## Maintenance notes

- The reviewer merges your commit, updates the index, then cuts v4.9.0 (plan 074); the release
  re-stamps `prompts/README.md`'s version line, so the fixture's copy will read as stale stock
  by one line afterwards — expected, as after every release.
