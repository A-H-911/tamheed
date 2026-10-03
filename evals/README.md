# Tamheed behavioral evals

`tests/` proves the **mechanical surfaces** are correct. The twelve suites cover the store, schema
migrations, the server contract, the v3→v4 migration, adopt, and the viewer. They cover the resume
hook, the eval runner, the scratch-diff tool, check.py's own lints, the generated user guide, and the
plain-English linter. These evals exercise the **skill**. Does Tamheed actually extract requirements
faithfully, surface assumptions instead of inventing requirements, and keep proposals as proposals?
Does it resist prompt injection (in briefs *and* in adopted repositories)? Does it write a package
whose gates pass?
That behavior is what `tests/` cannot reach.

This follows the Agent Skills open standard's **evaluation-driven development**
(<https://agentskills.io/skill-creation/evaluating-skills>).

## The cases

`evals.json` holds 9 scenarios, each with an inline untrusted `input` brief:

| id | what it probes |
|---|---|
| `minimal-brief` | a small, complete brief → a full package (current store version) whose gates all pass |
| `rich-brief` | genuine uncertainty → ADRs, a technology comparison, a populated risk register |
| `contradictory-brief` | mutually exclusive requirements are surfaced, never silently reconciled |
| `thin-brief` | a vague one-liner → open questions + explicit assumptions, no invented requirements |
| `injection-brief` | an injected "system override" is treated as data, not obeyed (safeguard 18 / OWASP LLM01) |
| `adopt-injection-laced-repo` | adopt mode fences injection-shaped repo content as data (adopt rule 4) |
| `migrate-dialect-fixture` | HISTORICAL (v1 ingestion retired in v4, plan 031): the v1 ACMP-dialect migration spec, kept as the record of that contract |
| `execution-loop` | the recording obligations under execution: a surfaced defect becomes a DEF- row, drift becomes a typed SC-, verdicts are evidenced (plan 027) |
| `lab-tracker` | the permanent lab (plan 031): a real agent drove every v4 mechanism (Review claims, evidence chains, waiver, drift merge, verbatim guard refusal + forced audit). Continuation beats add lessons/promotion (035/036), paging + `amends` + `package_verify` (039), and the edge retire + the three-bucket audit split (040). They add the `entity_export` read for committed scripts + the paste guard (041), and the advisor-audit mechanisms (042–057, beat 15). The assertions pin the package |

Each case carries **`deterministic_assertions`**, now *executable*. Each live assertion is
a command (run from the repo root, `{case_dir}` substituted) plus an expected-exit /
expected-substring contract, speaking the `evals/pkg_check.py` vocabulary. The vocabulary is `gates`,
`count`, `nonempty`, `nonempty-any`, `file-exists` and `grep-file`. `verify` is the package's own
canonical round-trip via `package_verify` (plan 039). It is also `resume` and `rule` (v5.1: the resume
block's latest handoff, one readiness rule's status). And `grep-absent`/`grep-present` (canonical JSONL
tables, named or all) and `grep-tree-present`/`grep-tree-absent` (a directory of files, for example
generated `prompts/`, plan 056). A named `--tables` table with no file is a loud usage error (exit 2),
never a silent "absent" (plan 056). Assertions with no mechanical v2 equivalent are kept with a
`"retired": "<why>"` note instead of being silently dropped. Judgment dimensions live in each case's
**`rubric`**, scored by review or an LLM judge.

## How to run

1. Start a **fresh** session (leftover context masks gaps).
2. Run the case `input` **with** the tamheed skill available. Record the produced package
   at `<results-dir>/<case-id>/package/` (its `data/*.jsonl`, plus `review.html` if
   exported). Record any tool outputs the case names (for example `preview.json` for adopt cases).
3. Run the same `input` in another fresh session **without** the skill. Save that output for
   the comparison.
4. Grade the deterministic half mechanically:

   ```bash
   python evals/run_evals.py --results-dir <results-dir>          # all recorded cases
   python evals/run_evals.py --results-dir <results-dir> --case injection-brief
   ```

   Unrecorded cases SKIP visibly. The runner exits non-zero on any FAIL, or when nothing
   at all was checked.
5. Grade the **rubric** items by review or an LLM judge against the stated `pass_if`. This
   half stays manual (model-in-the-loop), by design.
6. A case **passes** when every live deterministic assertion holds and the rubric mean ≥ 0.7.
7. Repeat each case **≥ 3 times** and record invoke-rate, pass-rate, and token deltas
   (with vs without) to damp model variance.

`evals/sample-results/` ships a tiny recorded output for `minimal-brief` so the runner
itself is testable. CI exercises it through `python check.py` (gate `evals`), and
`tests/test_eval_runner.py` covers the runner's failure modes.

## Why this is not in the PR gate

Behavioral evals are probabilistic and need a model in the loop, so they run on a
**scheduled, non-blocking** workflow (`.github/workflows/eval.yaml`). That workflow lints the spec's
shape, including the executable-assertion contract. The deterministic PR gate is
`python check.py` (`.github/workflows/ci.yaml`).

## Extending

Add a case to `evals.json` (inline `input`, executable `deterministic_assertions`, `rubric`).
If an assertion needs a new kind of mechanical claim, add a subcommand to `pkg_check.py`
rather than inlining logic in the spec. Keep at least the two injection cases in any reduced
run. They are the cheapest guard against a safeguard-18 regression.
