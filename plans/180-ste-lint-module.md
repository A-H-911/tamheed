# Plan 180: `server/ste_lint.py`, its suite, the third-party notice

> Maintainer-executed, 2026-10-03. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R15, R17, R21, R25, R28, R29. Upstream: `scripts/ste-lint.py` of
> danyuchn/asd-ste100-skill at `7d4a135` (MIT, (c) 2026 Dustin Yuchen Teng).

## Status
- **Priority**: P1 - **Effort**: L - **Risk**: MEDIUM (every later beat calls this module) - **DONE** (2026-10-03)

## What this beat produces

- `plugins/tamheed/server/ste_lint.py`: stdlib, Python 3.10, the MIT notice in the header. Three
  extractors (Markdown prose with paragraph join, Python runtime literals through `ast`, plain text),
  the vocabulary parser for `references/vocabulary.md`, the rules, a CLI.
- `plugins/tamheed/THIRD-PARTY-NOTICES.md`: the MIT text verbatim, the upstream URL and commit.
- `tests/test_ste_lint.py`: the suite, registered in `check.py` `SUITES` (twelve suites).
- Count surfaces that say how many suites there are: `tests/README.md`, `evals/README.md:3`,
  `CONTRIBUTING.md:18`, the guide (`suite.test_ste_lint` EN+AR, `index.html` rebuilt).

## What the port changes against upstream

| upstream | this module | why |
|---|---|---|
| sentences split per line | paragraphs joined first | Tamheed hard-wraps Markdown near 100 columns, which hid 32% of skill sentences over 20 words |
| `SYNONYM_GROUPS`, per-file rotation | rejected words from `vocabulary.md`, names skipped | the upstream groups flag Tamheed's deliberate distinctions |
| `--baseline N` | none | R3: baseline 0 per rostered file, the roster lives in `check.py` |
| no frontmatter handling | `description` linted, other keys dropped | a skill's description is the text that picks the skill |
| no Python input | runtime literals through `ast`, docstrings and comments skipped | tool descriptions, refusals and rule notes are agent-facing (R17, R28) |
| no Arabic | `semicolon` matches `؛` too, `long-sentence` splits on `؟` | R25 |
| `--selftest` in the module | `tests/test_ste_lint.py` | the repo's suites are the selftest |
| no allow marker | `ste:allow <rule>: <reason>`, a reason mandatory | R29 |

Hard rules: `semicolon`, `long-sentence` (25 words), `dangling-conjunction`, `phrasal-verb`,
`marketing-adjective`, `nominalization`, `vocabulary` (hard under strict, advisory under flavored),
`allow-without-reason`. Advisory: `passive-voice`, `present-perfect`. Headings and table headers
are exempt from length. A sentence whose code-span or quoted tokens are at least half of its tokens
is exempt from length (a trigger list, an identifier list). Code-shaped and markup-shaped Python
strings are skipped by tag name, never by a bare angle bracket (`<package>` is prose).

## Validation
- Red: `tests/test_ste_lint.py` failed to import the module (ModuleNotFoundError), then 19/21 on the first module: a hand-built block lacked `bad_allow`, and an f-string's constant parts were read twice by `ast.walk`. Both fixed with the tests as the oracle.
- Green: 21/21; the module parses under the 3.10 grammar; `python check.py` ALL CHECKS PASSED with twelve suites; `index.html` rebuilt (1,280 ids).
