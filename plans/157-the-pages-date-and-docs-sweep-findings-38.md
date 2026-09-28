# Plan 157: the page's date, and the docs sweep for v5.6.1

> Maintainer-executed, 2026-09-28. Batch map: [156-159-batch-findings-38.md](156-159-batch-findings-38.md).
> Field source: ACMP `findings_38.md` (§0.1 C5, §1 P8, §4, §7), ruling R48.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

- **The page has one clock.** The field read the exporter and wrote the condition into its own
  prediction: the first export's diff is one line "while the UTC date is still 2026-09-28". The
  Readiness section states the date it was evaluated on, because two of its rules read the
  calendar. The brief's class had no such condition.
- **A transcript row holds the hook's block three times.** The field's first reading of the
  post-compaction block took the wrapped copy and read as a mismatch.
- **A line with no `version=` comes from a process that has not reloaded.** The field showed it
  with a control. The maintainer's own session showed it again before and after its restart.

## What the sweep found

Ten sites speak of the page's clock or bytes. Every one was read.

| Site | Says | Disposition |
|---|---|---|
| `export_html.py:7-8` | same state, same bytes; "no wall clock" | reworded |
| `tamheed_server.py`, `export_html`'s docstring | same state, same file | reworded |
| `server/README.md`, the review surface section | same state, same output | reworded; the date and `review_current` named |
| `docs/design-decisions.md` §10 | same state, same file | a dated note added, pointing at §19 |
| `docs/design-decisions.md` §16, the no-lock entry | "deterministic from stored text" | "and the date of the export" added |
| `docs/install.md`, upgrade step 5 | a release's rendering change is "a one-time diff" | the date's line named |
| `docs/architecture.md`, `README.md`, `artifact-catalog.md`, `server/README.md` (the tool row) | the bare word "deterministic" | left: true of a function of the store and the date |
| `export_html.py` (`_freshness`, `_resume`), `server/README.md` (the freshness stamp) | no wall clock, of that function | left: true as written |

The engine's own comment at the export already said "evaluated as of today (two rules read the
calendar; the page says so)". The false sentences stood beside it.

## What changed

| File | Change |
|---|---|
| `tests/test_export_html.py` | `test_the_date_is_the_only_input_besides_the_store` |
| The six sites above | one sentence: the same store on the same UTC date gives the same bytes; on a later date the date moves, and a rule that reads the calendar may move its row; `review_current` is unaffected |
| `lab/scenario.md`, item 28 | "a second export is byte-identical" gains "on one UTC date" |
| `server/README.md` and `README.md`, the `entity_query` rows | the order sentence of plan 156 |
| `docs/install.md`, the trace | what `lines=` and `chars=` count; the three copies of the block in a transcript row; the line with no `version=` as measured on one session |
| `docs/design-decisions.md` §19 | five entries for the round's rulings, and what was not built. No paragraph on the page's weight (R48) |
| `CHANGELOG.md`, `plans/README.md`, the batch record | the round |

## Not changed, on purpose

- The engine. The exporter already takes the date as an input (`readiness["as_of"]`), so the
  test patches no clock.
- The date's source. A date derived from the store's last write would make the section
  disagree with `readiness_check` run today.
- No diagram. `docs/architecture.md`'s diagrams show neither the read's order nor the page's
  date; the sweep found no arrow made false.

## Tests

| Test | What it pins |
|---|---|
| `test_export_html.py::test_the_date_is_the_only_input_besides_the_store` | one store, one fixed report, two far-future dates: each date occurs once in its page; the pages differ; one page with its date replaced equals the other byte for byte |

The date sits on one line of several thousand characters that holds the whole section, so a
line diff would prove less than the sentence says. The substitution proves it.

## Validation

| Check | Result |
|---|---|
| The new test | passes; it fails by construction if the pages are equal or differ anywhere but the date |
| Clock and identity phrases over the bundle, `docs/`, `lab/` and the README, `stock-history.json` left out | every hit true as written |
| `git diff -- plugins/tamheed/server/*.py` | docstring lines only |
| `python check.py lint` | ALL CHECKS PASSED |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
