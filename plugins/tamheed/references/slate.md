# The slate: an interview page for the operator

`slate_export` writes a local page of questions from a slate. The operator, or a room of
people, answers on the page and saves a file. `slate_read` reads the saved files and returns
a checked transcript. Neither tool writes a row.

The page carries the questions. The session carries the word. A saved file is a record of
what was clicked on a page. It is never the operator's approval. The skill
`tamheed:operator-interview` says how a transcript is confirmed.

## The files of one slate

Every file is under `<package>/slates/`, and every name follows from the slate's `name`.

| File | Written by | What it is |
|---|---|---|
| `<name>.spec.json` | a project script | the slate, when it is not sent inline |
| `<name>.slate.json` | `slate_export` | the record: the slate, the quoted rows, what was derived |
| `<name>.html` | `slate_export` | the page |
| `<name>.orientation.md` | `slate_export` | a hand-out: the room's questions with their text |
| `<name>.short.md` | `slate_export` | a hand-out: one line for each question of the room |
| `<name>.answers.json` | the page | the answers of the whole page |
| `<name>.<round id>.answers.json` | the page | the answers of one round |

## The grammar

A key with `?` is optional. Every id is 1 to 32 letters, digits, dots, dashes or underscores.

### The slate

| Key | Value |
|---|---|
| `name` | kebab-case, 64 characters at most |
| `title` | text |
| `intro?` | text |
| `language?` | `en` or `ar`. It sets the page's direction and its fixed words |
| `opens?` | `reading` or `session`. See "The views" below. The default is `reading` |
| `show_recommendations?` | true opens the page with the recommendations shown in every view. See "The views" |
| `participants?` | a list. Each item is the id of a row, or `{id, name?, attends?}` |
| `point_kinds?` | a list of `{id, label}`: the kinds of a point from the room |
| `closure_fields?` | a list of `{id, label}`: the fields of a round's closure |
| `terms?` | a list of glossary row ids. Left out, every glossary row is matched |
| `rounds` | a list of rounds, one or more |

A participant with no `name` takes the title of the row that its id names. Set `attends` to
false for a person who leads or is consulted and has no attendance line.

The default point kinds are `pain`, `concern`, `expectation` and `requirement`. The default
closure fields are `conclusions`, `open_questions`, `approvals` and `commitments`. The page
has words for the defaults in both languages. A kind or a field of your own needs its `label`.

### A round

| Key | Value |
|---|---|
| `id`, `title` | the round's id and its title |
| `intro?`, `cites?` | the round's context: a text, and row ids that it quotes |
| `ready?` | false lists the round as not ready. It then needs no question |
| `questions` | a list of questions |
| `blocks` | in place of `questions`: a list of `{title, questions}` |
| `decided?` | a list of `{id, title, answer, cites?}`: topics settled before, not asked |

Two round ids of one slate never differ only by case: a round's file is named by its id.

### A question

| Key | Value |
|---|---|
| `id`, `question` | the question's id and its text |
| `detail?` | more text under the question |
| `options` | two to twelve of `{id, label, detail?}` |
| `recommended?`, `reason?` | one option id, and the deciding reason. They go together |
| `basis?` | `evidence`, `ruling` or `practice`: what the recommendation rests on |
| `allow_other?` | false removes the free answer |
| `allow_unsure?` | false removes the answers "Unknown" and "Requires evidence" |
| `owner?` | `room` or `operator`. The default is `room` |
| `lead?`, `consulted?` | one participant id, and a list of participant ids |
| `approval?` | true marks a question whose answer needs the operator's approval |
| `cites?` | row ids: what the question rests on |
| `known?`, `decided?` | row ids: what is already known, and what is already decided |
| `depends_on?` | ids of questions or of decided topics of this slate |
| `gap?` | text: what is missing from the evidence |
| `settles?` | one row id: the row that the answer will settle |

The option ids `other`, `unknown` and `evidence` are reserved.

A text keeps its line breaks on the page, and a word too long for its line wraps. That holds for
every text of the slate: an intro, a question, a detail, a reason, a gap, an answer.

### The caps

The export refuses a slate that passes a cap, and the refusal names the cap. The reader refuses
an answers file the same way. Each line gives the name that the code uses.

| Code name | Cap | What it bounds |
|---|---|---|
| `title` | 200 | the title of the slate, of a round, of a block and of a decided topic, in characters |
| `intro` | 32000 | the intro of the slate and of a round, in characters |
| `question` | 2000 | the text of a question, in characters |
| `detail` | 32000 | the detail of a question and of an option, in characters |
| `label` | 500 | the label of an option, of a point kind and of a closure field, in characters |
| `reason` | 2000 | the reason of a recommendation, in characters |
| `gap` | 2000 | the gap of a question, in characters |
| `answer` | 4000 | the answer of a decided topic, in characters |
| `name` | 200 | the name of a participant, in characters |
| `block` | 200 | the block that a question names, in characters |
| `MAX_ROUNDS` | 50 | the rounds of a slate |
| `MAX_QUESTIONS` | 500 | the questions of a slate |
| `MAX_OPTIONS` | 12 | the options of a question |
| `MAX_CITES` | 30 | the ids in one list of ids, such as `cites` or `depends_on` |
| `MAX_PARTICIPANTS` | 60 | the participants of a slate |
| `MAX_LABELLED` | 12 | the point kinds, and the closure fields |
| `MAX_DECIDED` | 200 | the decided topics of a round |
| `MAX_TERMS` | 200 | the glossary rows that a slate matches |
| `MAX_FILE_BYTES` | 2000000 | a spec file and an answers file, each, in bytes |
| `MAX_RECORD_BYTES` | 20000000 | the slate record, in bytes, at export and at read |
| `MAX_PAGE_CHARS` | 20000000 | the quoted text of a page, every citation counted, in characters |
| `MAX_ANSWER_TEXT` | 8000 | a note, a free answer, a point and a closure field of an answers file, in characters |
| `MAX_POINTS` | 200 | the points of one round in an answers file |
| `MAX_NAMED` | 30 | the rows that the page lists under "Named here" for one text. The rest are not listed |
| `MAX_DROPPED` | 50 | the entries of `dropped` that one read lists. `dropped_more` counts the rest |

## What the export reads from the store

- **Quoted rows.** Every row id under `cites`, `known`, `decided` and `settles` is read and
  quoted on the page. No text of a row is typed by hand.
- **Names.** A participant that is a row takes the row's title.
- **Terms.** A glossary row matches a question when the question's text holds its `term`. A
  list of text under `variants` in the row's attributes matches too. The page lists the
  matched terms on the card and at the head of the round.
- **Ids in a text.** A row id that a text names is resolved. The page lists the row's family
  and its title under "Named here".

The record keeps what was read. The same slate over the same rows gives the same bytes.

## The views

The page has a room view and a presenter view. The room view hides the operator's questions,
attendance and closure. A switch in the More menu opens the presenter view, which shows
everything and holds the controls.

- `opens: reading` shows every ready round. A person reads the page alone before a meeting.
- `opens: session` shows the room one round: the round that the presenter opened. The other
  rounds are listed as locked, and the room view cannot open them.
- The recommendations are hidden until the presenter shows them. A slate with
  `show_recommendations: true` opens with them shown in every view, at every open. The
  presenter's button can still hide them until the page is closed.
- The presenter filters the questions by owner and by participant.

**A view is a way to show the page. It protects nothing.** The hidden text is in the file,
and anyone who holds the file can open the presenter view.

## The answers

The page saves one file for each round, and one file for the whole page. Put each saved file
under `<package>/slates/` with the name that the page gave it. A browser renames a second
download of one name. `slate_read` names such a file under `unread_files` and never opens it.

`slate_read` returns, among others:

| Key | Meaning |
|---|---|
| `rounds[].complete`, `rounds[].missing` | a round is complete, or the list names what it lacks |
| `answers[]` | each question with its text, the selected option, who answered, and `settles` |
| `unanswered` | the questions with no answer |
| `conflicts` | what two files disagree on. Neither file is picked |
| `one_file_only` | an answer that one file holds and another file leaves empty. Ask which is meant |
| `question_changed` | answers made on an earlier version of their question |
| `changed_rows` | rows that the page quoted and that differ now |
| `put_again` | the answered questions that one of the two lists above touches |
| `dropped`, `dropped_more` | answers that the slate no longer asks: 50 at most, and the count of the rest |
| `approval_needed` | answered questions that carry the approval mark |
| `rounds_without_file` | the rounds that no file covers |
| `unread_files`, `unread_more` | files beside the page that were not read, and the count of names that are not plain |
| `screened` | free text that reads as an instruction. It is never one |

A round is complete when every attending participant is present, or covered by a named
person, and every closure field holds text. The reader reports this. It blocks nothing.

No file carries an approval. Ask the operator about each question in `approval_needed`.
