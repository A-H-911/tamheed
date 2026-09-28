# Plan 151: the version in the trace line and on the review page

> Maintainer-executed, 2026-09-28. Batch map: [151-155-batch-findings-37.md](151-155-batch-findings-37.md).
> Field source: ACMP `findings_37.md` (§0.2 C2, §1 the instrument note, P2, P8), rulings R36, R37,
> R44.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

The 5.5.0 brief asked whether a session started before the upgrade writes a trace line only after
a reload. The field could not answer. The hook's two files are byte-identical at the two tags, and
the line names no version, so a line of the old hook reads exactly as a line of the new one.

The review page has the same gap. `review_current` compares the digest stamped in the page with
the store's. After the upgrade it read true over a page the 5.4.0 exporter had written, which had
no roster column. Nothing in the page or in a tool result said which release wrote it.

The maintainer's own session showed both on the day of this plan: its server read 5.4.0 after
5.5.0 was installed, and its trace line at a compaction named no version.

## The rulings (R36, R37, R44)

- The trace line carries the hook's version right after the timestamp. The tail stays
  `session=<id>`. A silent line carries it too. The resume block does not change.
- `export_html` stamps the version that exported the page. `package_verify` reports it as
  `review_exported_by`. `review_current` keeps its one meaning.
- The key is not called "rendered by": 5.5.0 gave that word to the note's roster.

## What changed

One field, one meta, one key. The store's shape does not change.

| Where | Before | After |
|---|---|---|
| The trace line | `<utc> source=… lines=N chars=N status=… session=<id>` | `<utc> version=<x> source=… lines=N chars=N status=… session=<id>` |
| The review page's head | `<meta name="tamheed-digest" …>` | the same, then `<meta name="tamheed-version" content="<x>">` |
| `package_verify` | `review_current` | the same, plus `review_exported_by` |

- **The hook reads the manifest itself** (`resume_hook.py`, `_version`), before it looks for a
  note. It imports the server only after a note is found, so a silent run would otherwise have no
  version to write. The read is guarded on its own: a missing or malformed manifest costs the line
  its version, never the line and never the block.
- **One rule for every value in the line.** The version passes `_token`, as the session id and the
  source do. Anything but a plain token is written `-`.
- **`_plugin_version()`** is lifted out of `server_info` and used by it and by the stamp. One
  source, the bundled manifest.
- **The stamp joins the digest's `replace`**, so `render` still imports nothing from the server.
  It is written only when the version is a plain token. It is a constant of the release: no clock,
  no counter, so two exports stay byte-identical.
- **`package_verify` reads both stamps from the same 4,096-byte head.** The version is read by an
  exact pattern over the token class, because the value is echoed into a tool result.
  `review_exported_by` is `None` with no page or no stamp, and the stamped version otherwise.

## The placement, and what it departs from

A common convention for `key=value` log lines is to append a new key at the end. This line's tail
is documented in two releases, pinned by four assertions, and taught to the field as its
instrument ("attribute a line by its `session=` tail"). The new key therefore goes after the
timestamp. The cost: a reader that takes `source=` by position breaks. The brief names the new
shape as a class and asks how the field's scripts read the line.

## Not changed, on purpose

- `review_current`: thirteen lab lines and the contract test read it as "the page's data is
  current". A page exported by another release keeps it true; a test pins that.
- The resume block: the version in its first line would move every session's character count.
- The two committed review pages. The lab page gains the stamp at beat 28 (plan 154).
  `minimal-brief/review.html` stays as it is and reads `None`.

## Tests (written first, each failing before its edit)

| Test | What it pins |
|---|---|
| `test_resume_hook.py::test_trace_line_names_the_version_that_wrote_it` | a silent and a printed line both open `<utc> version=<manifest> source=`; both keep the tail; seven bad manifests (missing, not JSON, no key, a value with a space, a value with a newline, a number, a list) each write exactly one line with `version=-`, and the block still prints |
| `test_mcp_contract.py::test_the_review_page_names_the_version_that_exported_it` | the stamp sits before `<title>`; two exports are byte-identical; the key equals `server_info`'s version; a page stamped `5.5.0` reads `5.5.0` and keeps `review_current` true; a page with no version stamp reads `None`; a stamp that is not a plain token reads `None`; a closed package verified by name reads the same |

The four tail assertions of plan 141 and the stale-page test of plan 081 were re-run, not
re-aimed.

## Validation

| Check | Result |
|---|---|
| The two new tests before the edit | one failure, one error: `'source=startup' != 'version=5.5.0'`; `KeyError: 'review_exported_by'` |
| `tests.test_resume_hook` whole, and the two page tests, after the edit | 17 tests, OK |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| The working tree after the gate | four files changed, no fixture among them |
