# Vocabulary: one word, one meaning

Tamheed text is read by agents that cannot ask what a word meant. This file fixes one verb per
action and one meaning per term of art. The `tamheed:plain-english` skill cites it. The repository
gate reads the three tables below and fails on a rejected word in prose. A project extends the
terms with its own `glossary-term` rows (`GT-`), which the readiness rule reads.

The tables have fixed headers. The gate parses them, so keep the headers and the column order.
A rejected word stays legal inside a code span and inside a name listed in the third table.

## Actions

| action | approved verb | rejected synonyms |
|---|---|---|
| run a mechanical gate, rule or script | check | `validate` |
| rest a verdict on evidence | verify | — |
| give the operator's word on a row | confirm | — |
| take a row out of the record | retire | `delete`, `erase` |
| take a file, a marker or a line away | remove | `delete`, `erase` |
| make a process or a step begin | start | `launch`, `begin`, `initiate` |
| make a process or a loop end | stop | `halt`, `terminate` |
| make something visible to a reader | show | — |
| apply a tool, a rule or a value | use | `utilize`, `employ` |
| mend a defect in code | fix | `repair` |
| mend a wrong record or claim | correct | `repair` |
| move data to a reader or a system | send | `transmit` |
| take a row or a file through a tool | read | `get`, `fetch`, `retrieve`, `obtain` |
| make a row, a file or a plan different | change | `modify`, `alter` |
| put data into the store through a tool | write | — |
| put a fact into the record | record | — |
| the engine turns a write away | refuse | `decline` |
| the operator turns a row away | reject | `decline` |
| end an immutable row with a new row | supersede | — |
| put a file, a marker or a text in another's place | replace | — |
| take a trigger, a line or a row into a later state | carry | `propagate`, `forward` |
| write tool-owned files into a target project | emit | `produce` |
| derive a file from the record | generate | `produce` |
| say which row, run or file you mean | name | — |
| quote a row's own text with its id | cite | — |

## Terms

| term | one meaning | never means |
|---|---|---|
| record | the package: its rows are the source of truth | a log line, a recording |
| row | one entity in one table, with an id | a line of prose |
| note | the tool-owned operating note in the target's CLAUDE.md | a journal entry |
| journal | the `progress_entries` table | any file that logs |
| log | an external system's output (CI, a server) | the journal |
| display | a rendered view of data, never the store | the act of showing |
| reference | a document under `references/`, or a pointer to a row | the act of naming |
| bind | a lesson binds by its Approved status, from the write that approves it | the roster the note renders |
| carry | a deferred-work trigger, a handoff line or a row moves into a later state unchanged | copy |
| supersede | an immutable row ends and a new row takes its place | edit |
| retire | a row leaves the record and stays in history | delete a file |
| waive | the operator's `WVR-` row excuses one named readiness rule | a silent skip |
| force | the operator's explicit words override a guarded transition | a default |
| STOP | the ceremony: the agent halts for the operator's decision | a pause |
| operator's word | a decision the operator typed, quoted as typed | the agent's inference |
| check | a gate, a rule or a script ran and returned a result | a verdict with evidence |
| verify | a verdict rests on evidence with a method and a commit | a gate ran |
| confirm | the operator approves a row in their words | a gate ran |
| readiness | the semantic layer above the gates: blocking rules, advisory rules, waivers | the gates |
| gate | one mechanical check in `gate_run` | a readiness rule |
| drift | work that happened without a row | a stale sentence |
| handoff | the `handoff` journal entry a session writes last | stage 20 |
| planning half | stages 1-20: the brief becomes the package, through the handoff | a second agent |
| execution half | stages 21-22: the agent builds and records into the same package | a second agent |

## Names

| name | where it is a name |
|---|---|
| Quality validation | the title of stage 19 in `workflow.md` and the guide |
| Validated | a verdict value of experiments, hypotheses and POCs (with Invalidated, Inconclusive, Pending) |
| Invalidated | a verdict value of experiments, hypotheses and POCs |
| validated, traceable, execution-ready | the product line in the README and the plugin manifest |
| scope_modifies | a relation name |
| fast-forward | the git term |
| fix-forward | a ruling kind in the plans |
