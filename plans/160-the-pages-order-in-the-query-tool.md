# Plan 160: the query tool takes the page's order, and says so to the client

> Maintainer-executed, 2026-09-29. Batch map: [160-164-batch-findings-39.md](160-164-batch-findings-39.md).
> Field source: ACMP `findings_39.md` §3 (the typed `after_id` that dropped three rows),
> rulings R51 and R55.

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM - **DONE**

## What the field showed, and what the maintainer's review added

- **A typed `after_id` dropped rows in silence.** On 2026-09-11 a field session read the journal
  with a search, `after_id "PE-950"` and `limit 3`. It got `PE-954` and `PE-997`. Three matching
  entries with four-digit ids existed and were skipped, because the cut compared ids as text.
  The session drew no conclusion from the short result. Re-run over the field's journal with
  the engine's own statements, the read reproduces.
- **The review page has ordered ids by number since plan 057.** Its rule is prefix, then the
  id's first number, then the id. The query tool ordered the same families as text. One product
  held two orders.
- **v5.6.1 recorded number order in the tool as rejected,** for two reasons: a contract test
  pinned text order, and the cut and the order must share one collation. The first describes the
  old behaviour and argues nothing for it. The second is met by a cut written against the same
  rule as the order.
- **v5.6.1 put its rule where no client reads.** The server registers the second element of
  `TOOLS` as each tool's description. It has done so since its first commit. A docstring
  reaches no client. The sentence v5.6.1 added to `entity_query`'s docstring was called "the
  tool's description" in the changelog, the design record and the batch record. It reached no
  session. Its test pinned the docstring, so it passed while the claim was false.

## The rulings (R51, R55)

- `entity_query` sorts and cuts by the page's rule. R47 is superseded. R50 stands: no
  descending read is built.
- Three tools register a short contract. `entity_query` is the first; the two write tools
  follow in plan 161. The other sixteen one-line descriptions stay.

## What changed

| File | Before | After |
|---|---|---|
| `tamheed_server.py`, `_by_id` | lived in the viewer | lives in the server with `_id_prefix`, `_id_number` and `_after_id`; the viewer imports it |
| `tamheed_server.py`, `entity_query` | `ORDER BY id`; the cut `id > ?` | the page's order; the cut `_after_id()`, the typed id bound once per reference, its prefix and number computed by SQLite with the order's own expressions |
| the cursor's fallback, the `search` re-read | their own `ORDER BY id` | the same order as the main read |
| `matched`, `occurrences` | sorted as text | the returned rows' order |
| `TOOLS["entity_query"]` | "Query one entity family with targeted columns" | the contract: the order, what `limit` and `after_id` do, what `total` counts |
| `selftest()` | counted the tools the SDK registered | also compares each description the SDK lists with `TOOLS` and with the client's cap, and returns 1 on a difference |
| `export_html.py` | defined `_by_id` | imports it beside `ENTITY_TABLES`; its thirteen call sites are untouched |
| `entity_query`'s docstring | "the id's TEXT order" | the page's rule, and a sentence saying no client receives this text |

## The cut, as written

The order is `(prefix, number, id)`. The cut is that tuple's "greater than", written as three OR
branches and not as a row-value comparison:

```
(prefix > P) OR (prefix = P AND number > N) OR (prefix = P AND number = N AND id > ?)
```

`P` and `N` are computed by SQLite from the bound id, with the expressions the order uses. Python
computes no key. A second implementation could part from SQLite's `CAST` on a string no family
holds, and a cut that disagrees with its order drops or repeats rows.

## The ceiling, stated as the rule it is

Only an id's first number counts. What follows it orders as text, so `WBS-1.10` comes before
`WBS-1.2`. The page has always ordered them so. A store holds only ids its checks admit: a
prefix, a hyphen, a digit, then anything. A bound typed by a caller is any string.

## Not changed, on purpose

- The canonical JSONL order and the CSV order. Both are committed bytes and both keep the plain
  key.
- The eleven id lists the gates and the readiness rules return. Each names ids and none chooses
  rows.
- The descriptions of the other sixteen tools.
- A descending read.

## Tests (written first, each seen failing)

| Test | What it pins |
|---|---|
| `test_entity_query_keyset_paging_over_mixed_width_ids` | a walk at `limit=1` over ids of two widths is complete and in number order; the cursor at `limit=4` is `RISK-1000` |
| `test_entity_query_orders_and_cuts_by_the_pages_rule` | the viewer's `_by_id` is the server's; a bound that names no row returns the rows after it; the field's shape, a search with a typed bound and a limit; `matched` names the returned rows in their order, with `id` projected away too; the tool's order equals the page's over dotted ids |
| `test_the_cut_agrees_with_the_order_on_any_string` | over 28 strings on a scratch table, the rows after each position are exactly the rest of the order |
| `test_the_registered_description_is_what_the_client_receives` | the order's words stand in `TOOLS["entity_query"][1]`; every registered description is at most 2,048 characters |
| `test_selftest_compares_the_listed_descriptions` | the selftest reports the descriptions as listed; one made to differ, or one over the cap, returns 1 and is named |
| `test_entity_query_ids_search_and_refusals` | the docstring's own pin, kept |

## Validation

| Check | Result |
|---|---|
| The five new or changed tests before the engine moved | all five failed, each for its own reason: no `_by_id` in the server, text order returned, the one-line description, no line on descriptions in the selftest |
| The same after it | pass |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED; no fixture or golden touched |
| The operator's trace file over the run | 31 lines before and after |
| One description as the SDK lists it, beside its `TOOLS` entry | identical, 387 characters; all 19 identical. Seen on two versions of the SDK: 1.28.1 under `uv run`, 1.27.2 in this machine's plain Python |
| `uv run … --selftest` | 19 of 19 tools registered; 19 of 19 descriptions as listed; the longest 387 characters |
| The engine diff, read line by line | one line outside the plan: a comment's alignment at `_PROMPT_MAX_LINES` had lost a space. Restored |
| One page of 100 on the field's journal of 1,546 entries | 0.6 ms; it was 0.03 ms. A full walk at `limit=100`: 12 ms; it was 2 ms. A bound of a million characters: 2 ms |

## The two reviews

Two reviewer agents read the diff. Each finding was checked by reading before it was acted on.

| Review | Finding | Checked | Disposition |
|---|---|---|---|
| security | no caller string reaches the SQL text: `type` maps through a fixed table, `columns` are checked against the table's own, `limit` is coerced, the rest are bound | read at the lines it cites | no change |
| security | LOW, unmeasured: the cut evaluates its expressions on the bound value per row | measured, the last row of the table above | no change |
| python | the cut is the tuple's "greater than"; 11 binds; all four statements share one order; no off-by-one in the cursor | agrees with the tests | no change |
| python | MEDIUM: two docstrings said "every local gate" holds the description claim | half right. The suite runs the selftest, and this machine's Python has the SDK, so the real listing is compared locally. It holds only where the SDK is installed, and the docstrings did not say so | the condition is stated; the existing selftest test now asserts the real listing when the SDK is present |
| python | LOW: a lint marker on an import that is used | true | removed |
| python | LOW: the alignment change | true, found by my own read first | restored |
| python | LOW: the cap's assertion named no tool | true | it asserts every tool's name on the line |
