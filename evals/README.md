# Tamheed behavioral evals

`tests/` proves the **mechanical surfaces** are correct (store, server contract, migration,
adopt, viewer, the frozen v1 validator). These evals exercise the **skill** — does Tamheed
actually extract requirements faithfully, surface assumptions instead of inventing
requirements, keep proposals as proposals, resist prompt injection (in briefs *and* in
adopted repositories), and produce a package whose gates pass? That behavior is what
`tests/` cannot reach.

This follows the Agent Skills open standard's **evaluation-driven development**
(<https://agentskills.io/skill-creation/evaluating-skills>).

## The cases

`evals.json` holds 7 scenarios, each with an inline untrusted `input` brief:

| id | what it probes |
|---|---|
| `minimal-brief` | a small, complete brief → a full v2 package whose gates all pass |
| `rich-brief` | genuine uncertainty → ADRs, a technology comparison, a populated risk register |
| `contradictory-brief` | mutually exclusive requirements are surfaced, never silently reconciled |
| `thin-brief` | a vague one-liner → open questions + explicit assumptions, no invented requirements |
| `injection-brief` | an injected "system override" is treated as data, not obeyed (safeguard 18 / OWASP LLM01) |
| `adopt-injection-laced-repo` | adopt mode fences injection-shaped repo content as data (adopt rule 4) |
| `migrate-dialect-fixture` | migrate mode on the ACMP-dialect fixture: no silent loss, honest ledgers, cutover walked (plan 017) |

Each case carries **`deterministic_assertions`** — now *executable*: each live assertion is
a command (run from the repo root, `{case_dir}` substituted) plus an expected-exit /
expected-substring contract, speaking the `evals/pkg_check.py` vocabulary (`gates`, `count`,
`nonempty`, `grep-absent`/`grep-present`, `file-exists`, `grep-file`). Assertions with no
mechanical v2 equivalent are kept with a `"retired": "<why>"` note instead of being silently
dropped. Judgment dimensions live in each case's **`rubric`**, scored by review or an LLM
judge.

## How to run

1. Start a **fresh** session (leftover context masks gaps).
2. Run the case `input` **with** the tamheed skill available; record the produced v2 package
   at `<results-dir>/<case-id>/package/` (its `data/*.jsonl`, plus `review.html` if
   exported) and any tool outputs the case names (e.g. `preview.json` for adopt cases).
3. Run the same `input` in another fresh session **without** the skill; save that output for
   the comparison.
4. Grade the deterministic half mechanically:

   ```bash
   python evals/run_evals.py --results-dir <results-dir>          # all recorded cases
   python evals/run_evals.py --results-dir <results-dir> --case injection-brief
   ```

   Unrecorded cases SKIP visibly; the runner exits non-zero on any FAIL — or when nothing
   at all was checked.
5. Grade the **rubric** items by review or an LLM judge against the stated `pass_if` —
   this half stays manual (model-in-the-loop), by design.
6. A case **passes** when every live deterministic assertion holds and the rubric mean ≥ 0.7.
7. Repeat each case **≥ 3 times** and record invoke-rate, pass-rate, and token deltas
   (with vs without) to damp model variance.

`evals/sample-results/` ships a tiny recorded output for `minimal-brief` so the runner
itself is testable — CI exercises it through `python check.py` (gate `evals`), and
`tests/test_eval_runner.py` covers the runner's failure modes.

## Why this isn't in the PR gate

Behavioral evals are probabilistic and need a model in the loop, so they run on a
**scheduled, non-blocking** workflow (`.github/workflows/eval.yml` — it lints the spec's
shape, including the executable-assertion contract). The deterministic PR gate is
`python check.py` (`.github/workflows/ci.yml`).

## Extending

Add a case to `evals.json` (inline `input`, executable `deterministic_assertions`, `rubric`).
If an assertion needs a new kind of mechanical claim, add a subcommand to `pkg_check.py`
rather than inlining logic in the spec. Keep at least the two injection cases in any reduced
run — they are the cheapest guard against a safeguard-18 regression.
