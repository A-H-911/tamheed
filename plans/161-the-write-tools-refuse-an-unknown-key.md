# Plan 161: two write tools refuse an unknown key, and name their keys to the client

> Maintainer-executed, 2026-09-29. Batch map: [160-164-batch-findings-39.md](160-164-batch-findings-39.md).
> Source: the maintainer's census of the field's tool calls (the field did not report it),
> rulings R52 and R55.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the census showed

- **`progress_update` and `audit_record` read the keys they know and dropped the rest.** Each
  item was read with `.get()`. A key outside the list was ignored in silence.
- **One field write lost a key.** On 2026-09-07 a journal entry was sent with
  `custom_attributes`. The write returned `ok` and the attribute was never stored. It was one
  item of 453 written in the month.
- **Two calls got an opaque database error.** `NOT NULL constraint failed:
  progress_entries.entry`, on 2026-09-03 and on 2026-09-28. The second ran on 5.6.1 and had
  sent `summary` for `entry`.
- **No client could see the keys.** The schema a client receives for an item says "any
  object". The keys were written in the docstring, which no client receives, and in the skills.
- **The front door named a key loosely.** "event_type/subject/actor": the key is `subject_id`.
  A session that followed the sentence sent a key the engine dropped.

## The rulings (R52, R55)

- The two tools refuse an unknown key by name. The "unknown columns" refusal of `entity_query`
  and `entity_upsert` stays as it is.
- The two tools register a short contract that names their keys.

## What changed

| File | Before | After |
|---|---|---|
| `tamheed_server.py`, four constants | the keys stood in the docstrings and in the `INSERT` statements | `_PROGRESS_KEYS`, `_PROGRESS_REQUIRED`, `_VERDICT_KEYS`, `_VERDICT_REQUIRED` |
| `_item_error` | — | refuses an item that is no object, an item with a key outside the list, an item without a key the store requires |
| `progress_update` | a caller check that read a non-object item as an empty one | the item check first, then the caller check, both before any insert |
| `audit_record` | no check before the insert | the item check before any insert |
| `TOOLS["progress_update"]`, `TOOLS["audit_record"]` | one line each | the contract, built from the constants by `_keys_told` |
| both docstrings | the item's keys | the same, and one sentence: a key outside the list is refused, never dropped |

## What the refusal adds, and what it does not

- It refuses what the store refuses today, in words: a missing `entry`, a missing `ac_id` or
  `verdict`.
- It refuses what used to be dropped: any other key. `id` and `occurred_at` are among them. The
  server assigns both, and a caller's value was never honoured.
- **It adds no rule of its own.** An empty `entry` is written, as before. A value outside a
  vocabulary is still refused by the store's own check, with the text that quotes the
  vocabulary.
- **A null optional key means an absent one.** That was true of every optional key but
  `event_type`, whose default applied only when the key was absent. It applies to a null now.
- **`custom_attributes` is refused on `progress_update`.** The column exists, and
  `entity_upsert` writes it. The tool never took it.

## Not changed, on purpose

- `entity_upsert`. It has refused unknown columns since the server's first commit
  (`eb9f252`, 2026-07-17).
- The message of "unknown columns". It names the wrong columns and not the right ones; 44
  refusals of `entity_query` and 24 refused items of `entity_upsert` in the month, none since
  2026-09-21.
- The schema of an item. A typed item would put the keys in the schema and let the SDK refuse.
  The contract suite runs without the SDK, so that refusal would be tested by nothing in the
  gate.

## Tests (written first, each seen failing)

| Test | What it pins |
|---|---|
| `test_the_write_tools_refuse_a_key_they_do_not_take` | `summary`, `custom_attributes`, `note` and `id` are refused by name with the keys the tool takes; one bad item of two refuses the batch and names the item; a missing required key and an item that is no object are refused in words; nothing is written; every key the tools take still lands; an empty entry is written; the store's check still refuses a value outside the vocabulary |
| `test_the_write_tools_name_their_keys_to_the_client` | each registered description holds every key of its constant, marks the required ones, and fits the cap; each docstring holds its sentence |

## Validation

| Check | Result |
|---|---|
| The two tests before the engine moved | both failed: no constant in the server; the raw `NOT NULL` text came back |
| The same after it | pass |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
| The ten suites run with both tools wrapped (`suites_wrapped.py`) | 329 tests, none failing; 53 and 16 calls; the keys sent outside the lists are the seven cases of the new test and no other |
| The operator's trace file over the runs | 31 lines before and after |
| The three registered descriptions | 387, 311 and 300 characters |

**An error of the instrument, owned.** The first run of `suites_wrapped.py` reported 23 failing
tests and garbled keys while the gate was green. The script counted keys with
`Counter.update(item)`, which adds a dictionary's values. It raised inside the wrapper and
failed the tests it was watching. The disagreement with the gate showed it. The script counts
each key by name now.

## The two reviews

Two reviewer agents read the diff. Each finding was checked before it was acted on.

| Review | Finding | Checked | Disposition |
|---|---|---|---|
| python | MEDIUM: an explicit `event_type: null` still came back as the raw `NOT NULL` text, on the one optional key that has a default | reproduced in a scratch package. Every other optional key accepted null | a null `event_type` means an absent one and takes `note`. Test first, seen failing |
| python | LOW: a guard that tested each entry for being an object, after the item check had made it sure | true | removed |
| python | LOW: a test's docstring said the description and the refusal "cannot part"; its assertions prove the keys are named, not how the text is built | true | the docstring says what the test proves. The test also asserts the constant's own rendering stands in the description |
| python | the constants match the columns each insert writes; the validation runs to its end before the first insert; no call site in the bundle, the evals or the lab sends an unknown key | agrees with the wrapped suites | no change |
| security | LOW: the refusal echoes the caller's own key names | read: the message returns to the caller that sent them, and nothing stores or renders it. `entity_upsert` does the same | no change |
| security | the caller check is still reached for every item that passes the item check; `id` and `occurred_at` are refused, never honoured; the descriptions hold constants only | read at the lines it cites | no change |

One detail of a review was wrong and changed nothing: it named a test that does not exist.
