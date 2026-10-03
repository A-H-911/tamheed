---
name: plain-english
user-invocable: false
description: >-
  Use before writing English a reader cannot question. That is a tool description, a skill step, a
  row's statement, a requirement or an acceptance criterion. It is also a lesson, a handoff, a
  prompt file or a README. Use it before rewriting any of them, and when the readiness rule
  `prose-plain-english` names a text you own.
---

# Plain English

**A reader who cannot ask a question must parse every sentence one way. Write for that reader.**

Tamheed text is read by agents with no back-channel: a tool description, a refusal, a readiness
note, a handoff, a kickoff prompt. An executing agent reads the rows of the record the same way,
before it acts. ASD-STE100, the controlled English of aircraft maintenance manuals, exists for that
reader. This skill applies its structural rules to everything you write into a package or about
one. `tamheed:written-claims` keeps a sentence TRUE. This skill keeps it readable one way.

---

## Two modes

**Strict** is for text an agent acts on. That is a tool description, a skill step, a row's
statement, a prompt file, a handoff, the operating note or an acceptance criterion. Every rule
below applies, and the vocabulary binds.

**Flavored** is for text a human reads: a README, an architecture document, a charter, a changelog
paragraph. The structural rules apply in full. The vocabulary is a strong default, not a rule.

When no one named the mode, pick it by the reader. Then say nothing about the choice.

---

## The procedure

**1. One instruction per sentence. Twenty words for a step, twenty-five for a description.**
A step tells one actor to do one thing. A description states one fact. Count the words when a
sentence feels long. Split at "and", at "then", and at a comma that joins two clauses. A sentence
that lists names (identifiers, quoted trigger phrases) may run longer: the names are not prose.
- *Field evidence:* one skill step ran to 94 words and told the agent six things. The paragraph
  census found 445 skill sentences over twenty words, a third of them all.

**2. Active voice. Name the actor.**
"The server refuses the write" says who acts. "The write is refused" hides it. The passive is legal
when the actor is unknown or does not matter, and only then.

**3. No semicolon. Write two sentences.**
Rule 8.1 of the standard bans the mark. A semicolon joins two claims that each deserve a sentence.
The repository gate fails on one in a rostered file. The readiness rule reports one in a row.
- *Field evidence:* the bundle carried 2,503 semicolons in prose before the batch that wrote this
  skill. Every one joined two claims a reader had to separate.

**4. One word, one meaning. Use the vocabulary.**
`${CLAUDE_PLUGIN_ROOT}/references/vocabulary.md` fixes one verb per action and one meaning per
term. `check` means a gate, a rule or a script ran. `verify` means a verdict rests on evidence.
`confirm` means the operator gave their word. A rejected word is a hard finding under strict. A
project adds its own words as `glossary-term` rows (`GT-`). It never adds them by using a rejected
word in a row.
- *Field evidence:* the bundle used `check`, `verify`, `confirm` and `validate` for what read as one
  action. The census showed three actions and one word with no action of its own.

**5. Keep the hedge. A `may` never becomes an `is`.**
A hedge carries the author's confidence, and confidence is content. "The request may have failed"
and "the request failed" are two claims. A shorter sentence that promotes a hedge is a different
claim, not a simpler one. When a rewrite keeps a compound tense or a hedge on purpose, add one
line under it: `Kept as-is:`. The line names the phrase and the precision it keeps.
- *Field evidence:* the upstream project's own example once rewrote "an error may have occurred" as
  "the request failed" and added "the most common cause". Both read better. Both were wrong.

**6. No dropped words.**
Keep the article, the subject and the verb. "Files not backed up will be lost" has two readings.
"The files you did not back up will be lost" has one.

**7. No phrasal verb, no nominalization, no marketing word.**
`Start the job`, not `spin up the job`. `Analyze the log`, not `perform an analysis of the log`.
Remove `robust` and `seamless`, or replace them with the measurement that earns them.

**8. One topic per paragraph, at most six sentences. Three or more steps become a list.**
A sequence buried in prose is a sequence the reader must rebuild. Number it.

**9. Scan before you rewrite, then rewrite the sentence and nothing else.**
Six habits cover most of what makes machine-written English hard to parse: synonym rotation,
hedge stacking, nominalization, marketing adjectives, run-on sentences, soft phrasal verbs. Point
at the word or the mark that breaks a rule. Then fix that sentence. Never add a fact, a cause or a
frequency the source did not state. A rewrite that reads better because it supplies one is no
longer a rewrite.

**10. Run the linter when the text is a file.**
`python ${CLAUDE_PLUGIN_ROOT}/server/ste_lint.py --mode strict <file>` reports the structural
findings and the vocabulary. It cannot read meaning, it cannot see a dropped hedge, and it applies
the twenty-five-word cap only. The twenty-word cap for steps and the hedges are yours to keep.

**11. New text obeys this skill. Existing rows are the operator's call.**
The readiness rule `prose-plain-english` names the texts of the record that break the rules. Do not
rewrite those rows on your own. The operator runs `/tamheed:ste-rewrite`, which proposes a batch,
STOPs, and supersedes an immutable row instead of editing it.

---

## What this skill does NOT cover

- **Whether the sentence is true** - `tamheed:written-claims`.
- **Reading a row before you cite it** - `tamheed:reading-the-record`.
- **How a write reaches the store** - `tamheed:package-writes`.
- **The approved dictionary of ASD-STE100.** The standard is free to request and not free to
  redistribute, so its word list is not in this bundle. The vocabulary file is Tamheed's own.

---

*The rules follow ASD-STE100 Issue 9 as the public description of the standard states them. The
linter and this skill's rule set come from danyuchn/asd-ste100-skill (MIT, the notice in
`${CLAUDE_PLUGIN_ROOT}/THIRD-PARTY-NOTICES.md`).*
