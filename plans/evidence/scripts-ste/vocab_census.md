# Vocabulary census (plan 179, read-only)

Counts are inflected uses in prose outside code spans, fenced code and blockquotes. `in code` counts the word inside backticks (a name, never rewritten). `names` lists engine identifiers that contain the word (a name cannot change in a MINOR).

## check/verify/confirm/validate

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| check | 67 | 39 | 9 | 0 | 89 | 10 | 214 | 19 | 6 |
| verify | 27 | 17 | 8 | 2 | 33 | 27 | 114 | 31 | 6 |
| confirm | 35 | 30 | 6 | 2 | 42 | 41 | 156 | 47 | 0 |
| validate | 6 | 33 | 1 | 0 | 20 | 1 | 61 | 2 | 0 |
- names containing **check**: tool: readiness_check, skill: integrity-check
- names containing **verify**: column: verified_by, tool: package_verify, relation: verifies
- names containing **confirm**: readiness rule: lessons-confirmed
- samples **check**: ...ing anything that depends on it; a pull request's checks show... / ...On a direct push, a path filter is checked against that push, so a package-only commit may r... / ...nothing. On a pull-request event it is checked against the whole PR diff, so a package-only comm...
- samples **verify**: ...- **Verify candidate changes one at a time against the curre... / ...commit +   for any criterion actually verified (evidence plus... / ...8. **Verify any recent repair**: if rows were repaired since...
- samples **confirm**: ...*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,... / ...edge to the   — the operator confirms later.... / .../ ) — the operator confirms later; only Approved lessons bind;...
- samples **validate**: ...working.** Re-validate the row and write the new date from that act; cle... / ...4. **Assumptions** ( ): past   — re-validate... / ...Transform a project description into a complete, validated, traceable, execution-ready planning and...

## delete/remove/erase (+retire)

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| delete | 11 | 9 | 2 | 3 | 14 | 18 | 57 | 0 | 0 |
| remove | 9 | 5 | 1 | 1 | 32 | 44 | 92 | 0 | 0 |
| erase | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| retire | 17 | 26 | 3 | 5 | 51 | 29 | 131 | 21 | 2 |
- names containing **remove**: relation: scope_removes
- names containing **retire**: column: retired_in
- samples **delete**: ...layer runs first, and keep passing if any one is deleted.... / ...rd. State the weakest premise the argument needs; delete the ones it... / ...and the file had already been deleted....
- samples **remove**: ...removes the **condition** over one that changes the **odd... / ...a deliberate fault, confirm the gate FAILS, then remove it.** Prefer the command CI runs... / ...- **A substring proxy removes rows that NAME a thing without covering it**, and...
- samples **retire**: ...arrying BOTH a typed relation and   as residue to retire.... / ...package (entity_upsert - full-row, substitute or retire items -... / ...- **Trace edges are keyed**  . A wrong edge is retired ( , journaled)...

## start/launch/begin/initiate

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| start | 16 | 14 | 7 | 5 | 52 | 20 | 114 | 0 | 1 |
| launch | 1 | 1 | 0 | 0 | 7 | 1 | 10 | 0 | 0 |
| begin | 0 | 0 | 1 | 0 | 1 | 0 | 2 | 0 | 0 |
| initiate | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
- samples **start**: ...recording a CI result on the PR that produced it starts a new run and supersedes that result.... / ...Stop conditions (evaluate at the start of every iteration and before closing a slice):... / ...it: a background process started in the same place writes the identical line. Take...
- samples **launch**: ...|   | Server install/launch; the full MCP tool reference |... / ...CP server requires the 'mcp' SDK (Python >=3.10): launch with 'uv run tamheed_server.py' (PEP 723 fetches...

## stop/halt/terminate

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| stop | 38 | 13 | 11 | 4 | 22 | 4 | 92 | 5 | 2 |
| halt | 1 | 0 | 0 | 1 | 0 | 0 | 2 | 0 | 0 |
| terminate | 2 | 0 | 0 | 0 | 1 | 0 | 3 | 0 | 0 |
- samples **stop**: ...full-row upsert;   by supersession); STOP for approval, and only... / ...e to read the brake for fully-auto execution: the stop conditions an unattended loop evaluates every ite... / ...( ) beside   when running   unattended. The loop stops...
- samples **halt**: ...waiver for a single named rule), so the loop halts and surfaces the failing rules...
- samples **terminate**: ...anges nothing and the enumeration of roots cannot terminate, the retention is structural — and... / ...that inability to terminate is itself the tell....

## show/display

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| show | 12 | 2 | 0 | 1 | 22 | 9 | 46 | 6 | 0 |
| display | 3 | 1 | 0 | 2 | 0 | 2 | 8 | 0 | 0 |
- samples **show**: ...thing that depends on it; a pull request's checks show... / ...cause; a batch merge shows a later red as an unrelated-looking flake and a r... / ...anged column, so a re-transmission that lost text shows as a length drop...
- samples **display**: ...ken FOR that send. Text that has passed through a display — a... / ...— never  , never a pasted display; export immediately before... / ...never  , never a pasted display (v4.7). A full-row update that only means to...

## use/utilize/employ

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| use | 20 | 6 | 10 | 0 | 20 | 7 | 63 | 0 | 3 |
| utilize | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| employ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
- samples **use**: ...Use before stating that CI or a deploy is green, red... / ...Run a coverage gate in the build configuration CI uses; a coverage number... / ...2. Open it and use the sticky nav — the page has eleven sections:...

## fix/repair/correct

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| fix | 42 | 8 | 11 | 2 | 13 | 12 | 88 | 9 | 1 |
| repair | 9 | 6 | 0 | 4 | 5 | 3 | 27 | 0 | 1 |
| correct | 28 | 8 | 1 | 1 | 19 | 21 | 78 | 14 | 0 |
- names containing **fix**: column: fixed_by
- names containing **correct**: column: corrects
- samples **fix**: ...ion: the defect row is registered FIRST, then the fix, the evidence, the binding and the status flip.... / ...BEFORE the fix, so the record survives even if the session dies... / ...roduce the symptom as a minimal failing test — no fix yet....
- samples **repair**: ...the record survives even if the session dies mid-repair:... / ...8. **Verify any recent repair**: if rows were repaired since the last check (a... / ...8. **Verify any recent repair**: if rows were repaired since the last check (a...
- samples **correct**: ...o "path filters do not work". Both behaviours are correct; they are different... / ...batch —   on the wrong triple + the correct relation,... / ...command the number prints, is correct, and changes nothing — you read it after the push...

## send/transmit

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| send | 9 | 3 | 0 | 0 | 5 | 10 | 27 | 0 | 1 |
| transmit | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
- samples **send**: ...d none compares a field to the value you meant to send. A bad write reports  , every... / ...but the row you send must still satisfy the table's NOT NULL constrain... / ...- **  names only columns you SEND.** A sent column that differs from the...

## get/retrieve/fetch/obtain (+read)

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| get | 14 | 10 | 1 | 0 | 20 | 0 | 45 | 0 | 0 |
| retrieve | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fetch | 6 | 1 | 0 | 1 | 6 | 3 | 17 | 0 | 0 |
| obtain | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| read | 175 | 50 | 19 | 16 | 151 | 48 | 459 | 21 | 9 |
- names containing **read**: skill: reading-the-record
- samples **get**: ...- A red that matches an OPEN intermittent row gets its occurrence appended there; the row's... / ...unfalsifiable: every recurrence gets attributed to the residual it disclosed. Prefer a... / ...artefact small enough to adjudicate by hand, get per-item output rather than a percentage, and rea...
- samples **fetch**: ...the reader may not have open. Id alone makes them fetch it;... / ...schemas this session lists for the tools were fetched when the client process started;... / ...readiness counts Review as open) — re-fetch the row through...
- samples **read**: ...the PR-head run and can read all-green while the branch is red.... / ...n" is a claim about EVERY workflow on that sha.** Read each one's conclusion, not the one... / ...you happened to read first — and   is a third conclusion, neither pass...

## change/modify/alter

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| change | 83 | 42 | 26 | 8 | 77 | 19 | 255 | 29 | 4 |
| modify | 1 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 0 |
| alter | 1 | 0 | 0 | 0 | 2 | 2 | 5 | 1 | 0 |
- names containing **change**: table: scope_changes, readiness rule: scope-changes-merged
- names containing **modify**: relation: scope_modifies
- samples **change**: ...as not run. And a checkout changes the source, not the installed environment: reinst... / ...- **Verify candidate changes one at a time against the current trunk**, so eve... / ...on from the approved plan (scope grew, shrank, or changed shape) →...
- samples **modify**: ...an installed tree, images included, once read as modified; each file's size gap equalled...
- samples **alter**: ...altered any of them.... / ...UPDATE and never counts as drift): the transport altered the value; re-fetch the row through entity_query... / ...UPDATE and never counts as drift): the transport altered the value; re-fetch the row through entity_query...

## write/record/journal/log

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| write | 101 | 70 | 12 | 6 | 124 | 74 | 387 | 35 | 3 |
| record | 120 | 53 | 31 | 11 | 138 | 70 | 423 | 41 | 8 |
| journal | 43 | 31 | 5 | 7 | 73 | 26 | 185 | 0 | 1 |
| log | 5 | 1 | 3 | 0 | 5 | 5 | 19 | 7 | 1 |
- names containing **write**: skill: package-writes
- names containing **record**: column: recorded_at, tool: audit_record, event_type: verdict-recorded, skill: reading-the-record
- samples **write**: ...Write  , not "the merge was green". After a merge, poll... / ...find a control run where the needed jobs passed. Write... / ...ll-row upsert — and re-read its prose in the same write: a closed status over...
- samples **record**: ...that CI or a deploy is green, red or done; before recording an audit verdict,... / ...branch's run to completion before recording anything that depends on it; a pull request's che... / ...- *Why:* recording a CI result on the PR that produced it starts a n...
- samples **journal**: ...a gate-decision journal entry or a done-claim that rests on a CI run; bef... / ...journal "CI green" without a run id; the next reader cann... / ...with   — journals are never edited) +   per orphan...
- samples **log**: ...lded below it),   (AC × latest verdict + progress log),... / ...value.** A log line equal to your replay to the character proves... / ...response body on the wire, the rendered page, the log line as written —...

## refuse/reject/decline

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| refuse | 31 | 22 | 1 | 7 | 49 | 10 | 120 | 0 | 1 |
| reject | 9 | 20 | 16 | 0 | 32 | 19 | 96 | 9 | 1 |
| decline | 7 | 1 | 0 | 0 | 3 | 1 | 12 | 0 | 0 |
- samples **refuse**: ...7. Any store error (locked, stale tree, refused batch) — never retry around the... / ...g them is the operator's interview, and the store refuses the... / ...s as protection improves.** When an earlier layer refuses the whole population a later...
- samples **reject**: ...terview is not re-run from scratch"; the operator rejected the entry — *always you must... / ...typed audit event itself); **Reject** (kept as evidence); or **refine** (upsert a... / ...enters) — and retiring or rejecting an UNPINNED lesson removes NOTHING, the fill...
- samples **decline**: ...was open (a trade-off accepted, a fix declined, a behaviour kept on purpose), that... / ...- **An absent reason is not a reason.** A decline recorded without one reads like a signal because... / ...decline usually carries one — and that is exactly what ma...

## supersede/replace/override

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| supersede | 16 | 23 | 18 | 0 | 28 | 35 | 120 | 16 | 2 |
| replace | 8 | 6 | 5 | 1 | 13 | 3 | 36 | 1 | 2 |
| override | 3 | 2 | 0 | 0 | 6 | 2 | 13 | 9 | 0 |
- names containing **supersede**: column: superseded_by, relation: supersedes, readiness rule: lessons-superseded-binding
- names containing **override**: event_type: forced-override
- samples **supersede**: ...t on the PR that produced it starts a new run and supersedes that result.... / ...(superseded verdicts are history):   names the graded verdict... / ...resting on a superseded measurement ( )....
- samples **replace**: ...n row in their own words and follow it until they replace it. It governs the... / ...e written in the same batch; a new relation never replaces an old one by itself.... / ...or a term with a search-and-replace over the rows you know about leaves the quotation...
- samples **override**: ...conditions override everything here.... / ...item ask the operator for a   waiver.   overrides the whole... / ...overrides the whole transition and exists only on the opera...

## carry/forward/propagate

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| carry | 76 | 42 | 11 | 8 | 93 | 24 | 254 | 24 | 0 |
| forward | 6 | 3 | 1 | 0 | 1 | 3 | 14 | 0 | 0 |
| propagate | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
- names containing **carry**: relation: carries, readiness rule: deferred-work-carried
- samples **carry**: ...- *Field evidence:* twenty-nine commits carried a gates line without coverage; run at last, cover... / ...hand edit or a damaged row),   true (a false one carries... / ...pair carrying BOTH a typed relation and   as residue to retire....
- samples **forward**: ...true then, never consent for now. Do not carry it forward as a default, a starting position or a... / ...- After a squash-merge, a   that will not fast-forward is the tell: verify the package tree is... / ...- **A fix-forward ruling deliberately freezes a historical figure**...
- samples **propagate**: ...findings propagates a wrong number into every artefact that quotes it...

## emit/generate/produce

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| emit | 6 | 12 | 1 | 0 | 30 | 5 | 54 | 0 | 0 |
| generate | 8 | 5 | 7 | 1 | 15 | 0 | 36 | 12 | 2 |
| produce | 14 | 4 | 4 | 1 | 12 | 0 | 35 | 0 | 1 |
- names containing **emit**: tool: handoff_emit
- names containing **generate**: skill: generate-report
- samples **emit**: ...is the one write that is always allowed),  , and emit the... / ...record the reason as a final  ,  , and emit the... / ...emit rebuilds it. So an Approved lesson is rendered by...
- samples **generate**: ...name: generate-report... / ...Generate the review surface for the   Tamheed package:... / ...Quote it verbatim and generate it (an   file, a slate built from it); never para...
- samples **produce**: ...- *Why:* recording a CI result on the PR that produced it starts a new run and supersedes that result.... / ...cate once in the foreground and read the value it produces. Bound every loop by an... / ...Invoke this ( ) to produce and read the   HTML review surface....

## name/cite/reference

| word | skills | references | templates | stock README | docs+root | server literals | total | in code | headings |
|---|---|---|---|---|---|---|---|---|---|
| name | 121 | 59 | 32 | 28 | 139 | 73 | 452 | 66 | 12 |
| cite | 12 | 7 | 2 | 1 | 11 | 2 | 35 | 0 | 0 |
| reference | 11 | 20 | 26 | 0 | 65 | 3 | 125 | 90 | 5 |
- names containing **name**: column: name
- names containing **reference**: column: last_referenced
- samples **name**: ...name: ci-evidence... / ...is true only for one run, one event and one tree. Name them, or you have not said... / ...commit a verdict names is the sha the run tested, on the remote (  §6),...
- samples **cite**: ...**1. Cite the run id and the event, never a colour.**... / ...Every entity you cite carries its own text where you cite it: title, th... / ...ry entity you cite carries its own text where you cite it: title, the operative field (a deferred...
- samples **reference**: ...grading itself — list them); and  , the references that resolve to... / ...An id is a pointer, not a reference:   checks foreign keys, not ids in prose. A green... / ...16. **Dangling references** ( ): identifiers written in PROSE that...

