# Plan 182: the readiness rule `prose-plain-english` (advisory)

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R13; the approval item on columns (every register family's statement columns, prompts
> and the latest handoff; not `document_sections.body`).

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: LOW (advisory: `ready` never moves) - **DONE** (2026-10-03)

## What this beat produces

A new advisory rule in `_readiness_report`, package scope, after `prompt-ids-resolve`:

- Reads the statement columns of the register families (requirements, constraints, invariants,
  assumptions, dependencies, open questions, decisions, ADRs, acceptance criteria, lessons), rows
  Superseded or Obsolete skipped; the latest `handoff` journal entry; the project's prompt files
  (`<package>/prompts/*.md` that are not a stock body, the same test `prompt-ids-resolve` uses).
- Lints each text with `ste_lint` under strict, English, with the bundle vocabulary extended by
  the package's `glossary_terms` rows: a `GT-` term is a project word, never a finding.
- `entities`: one line per text with hard findings, `FR-003.statement: semicolon x2,
  long-sentence x1`, `prompts/kickoff.md:14: vocabulary`, `PE-061.entry: semicolon x1`, cut at
  `_PROSE_ID_CAP` with the cut note. `counts`: findings per rule. `population`: texts scanned,
  set by hand; zero texts reads `indeterminate`.
- The note ends with the skill cue: `tamheed:plain-english` for new text, `/tamheed:ste-rewrite`
  for the operator who wants the existing text rewritten.
- The guide: `rule.prose-plain-english` EN+AR; `extract.py` counts 30 package rules;
  `register-liveness` names the rule in its amber list.

## Validation
- Red: `test_prose_plain_english_is_advisory_and_counts` (tmp package): rule present; a fresh
  package indeterminate; a requirement "The job runs; it waits." reads `fail` with
  `FR-001.statement: semicolon x1` and `ready` unchanged; a `GT-` row `validate` suppresses the
  vocabulary finding on "Validate the input."; `test_rule_extraction_matches_the_engine` red at 29.
- Red confirmed (the rule absent). Green: the new test, the register-liveness roster test with the rule added, `test_rule_extraction_matches_the_engine` at 30, `python check.py` ALL CHECKS PASSED, `index.html` rebuilt (1,282 ids).
- `_scan_prompt_ids` now reads the stock bodies through the factored `_stock_bodies(name)`; the bundle vocabulary is cached by the file's mtime; `GT-` terms enter as names in three forms (as typed, capitalized, lower).
- The register-liveness playbook gained item 22 for the rule.
