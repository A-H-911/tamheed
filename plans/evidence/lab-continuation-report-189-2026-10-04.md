# Lab continuation report — beat 33, v5.9.0 (plan 189, 2026-10-04)

> `lab/scenario.md` beat 33: the plain-English release against the recorded `lab-tracker`
> fixture. Two phases. The scratch phase ran FIRST, by a real agent through the headless harness
> (`plans/evidence/scripts-fb028/labrun.py`, Opus 5.5, `--plugin-dir` on the working tree,
> `--setting-sources ""`, `--permission-mode dontAsk`, the base allow list, never
> bypassPermissions) on a copy of the fixture outside the repository. The fixture phase then ran
> in-process through the working-tree server (`plans/evidence/scripts-ste/labrun-189/beat33.py`,
> actor `agent:lab-beat-33`). The session's writes replaced the fixture's `data/`, `prompts/README.md`,
> `CLAUDE.md`, `csv/` and `review.html`. No eval or test file was edited by the beat. The scratch
> copy was never committed. The run's outputs are beside this report under
> `scripts-ste/labrun-189/` (the turns file, the two result files, the two reports, the hook trace).

## 1. The scratch phase: `/tamheed:ste-rewrite package` by a real agent

**Setup** (`beat33_setup.py`, in-process): the fixture copied, the note emitted with
`refresh_stock=true`. The guide refreshed to the 5.9.0 body. The note's marker read `tamheed:note v6`
and its first sentence "The Tamheed package for this project is `package` (...)". The standalone
`.mcp.json` was removed (the session's server is the `--plugin-dir` bundle). The rule read before
the session:

```
prose-plain-english: fail, counts {"long-sentence": 7, "semicolon": 14}, 36 texts
AC-002.statement, AC-005.statement, ADR-0001.confirmation/consequences/decision, ASM-001.statement,
DEC-001.decision/rationale, FR-002.rationale/statement, FR-003.rationale, LL-001.statement,
LL-004.statement, NFR-001.statement, PE-063.entry
```

**T1, the slash command as the whole prompt.** Session `c3d04d2d-2e6f-4204-9808-d63220cbfb7a`,
23 turns, $0.77, no permission denial. The hook ran at start (`version=5.9.0 source=startup
lines=6 chars=840 status=printed`). The agent opened the package, read the rule, read every named
row whole, and wrote a batch-1 table of ten texts with before, after and consequence. It STOPPED
with nothing written. Its report (`r33-T1.report.md`) sorted the 15 texts into three cases:

- Immutable rows (`governance.md`): ADR-0001, AC-002, AC-005, LL-001, LL-004. A successor row.
- **Approved rows of a family with no supersession column** (FR-002, FR-003, NFR-001, ASM-001,
  DEC-001): "The skill does not say." The agent put this as Q0 and recommended rewriting them in
  place, Approved, with `expect_unchanged`, because every change is punctuation or a split.
- The journal entry PE-063 (the latest handoff): append-only, "I will not write anything for it".

Skipped by default and said so: AC-002 (Met verdict), LL-004 (Approved; a supersession would take
it off the roster). LL-001 is Promoted (pinned, in SKL-001): "The skill's default-skip list does not
name Promoted lessons. I skip it anyway ... That is my own call."

**T2, the operator's words** (`run-33.md`, a `--resume`, a new client process). 21 turns, $1.51, no
denial. The hook ran at resume (`source=resume lines=6 chars=987 status=printed`). The words: Q0 (a)
approved as a rule for this run; one in-place rewrite (ASM-001.statement); one supersession
(ADR-0001 → ADR-0002), then ADR-0002 approved on the words "The operator confirms ADR-0002 as
written, 2026-10-04, lab beat 33"; every other row skipped. The agent's report (`r33-T2.report.md`):

```
PE-064  the lock removal on the operator's word (pid 81772 not running), written by the server
ASM-001 rewritten in place, still Approved; only `statement` changed, the rest in expect_unchanged
ADR-0002 inserted Proposed: decision, consequences, confirmation rewritten, every other column carried
ADR-0001 Superseded, superseded_by ADR-0002
ADR-0002 Approved on the operator's words
PE-065  the batch note: both rulings quoted, rows written / superseded / skipped listed
PE-066  the handoff, written LAST, actor agent:lab-beat-33
counts before {"long-sentence": 7, "semicolon": 14}  after {"long-sentence": 6, "semicolon": 10}
adrs-approved pass over 1 row before, pass over 2 rows after
refusals: none
```

Two things the agent said that the maintainer took: the "after" count was read before its own
handoff, so PE-063's semicolon still counted ("I have not run that check"), and "Your Q0 (a) ruling
exists only as a quote in PE-065. No decision row records it."

## 2. The fixture phase (`beat33.py`, in-process, the committed package)

```
OBS A.before: {"review_current": true, "review_exported_by": "5.8.1"}
OBS A.schema: {"schema_version": 7, "migrations_head": "007_handoff.sql", "version": "5.9.0"}
OBS A.open.resume: {"handoff": "PE-063", "behind": 0}
OBS A.rule.before: {"status": "fail", "counts": {"long-sentence": 7, "semicolon": 14}, "texts": 36}
OBS A.guide: {"refreshed": ["prompts/README.md"], "title": "tamheed v5.9.0"}
OBS A.note: {"marker": "tamheed:note v6", "first_sentence": "The Tamheed package for this project is `package` (under ..."}
OBS A.handoff: "PE-065"
OBS A.handoffs: 12
OBS A.rule.after: {"status": "fail", "counts": {"long-sentence": 7, "semicolon": 13}, "texts": 36}
OBS A.page: {"date_before": "2026-09-30", "date_after": "2026-10-03", "lines_before": 1094, "lines_after": 1101}
OBS A.gate_run.ready: true
OBS A.verify: {"verified": true, "dirty": [], "foreign": [], "review_current": true, "review_exported_by": "5.9.0"}
OBS A.lock_gone: true
```

The fixture's register rows keep their semicolons and long sentences: rewriting a package is the
operator's choice (the brief's STOP), and the eval asserts Tamheed-owned files only. The rule's count
moved from 14 to 13 semicolons because the beat's own handoff (plain English) replaced PE-063, whose
one semicolon had counted, in the rule's population. The first run of this phase wrote a note and a
handoff that carried five semicolons and sentences over 25 words, against the rule the release ships.
The advisor's read caught it. The fixture was restored from HEAD and the phase re-run with the texts
above, as the batch's recipe says (a beat that fails after phase A re-runs from a restored fixture).

The emit target carried an `@package/CLAUDE.md` pointer, so the v6 note landed in the fixture
package's own `CLAUDE.md` (that is where `A.note` was read). Its first sentence names the package
with this machine's absolute path, so the file was removed before the commit; the fixture carries
no note, as before beat 33. The eval's resume assertion moved from `PE-063` to `PE-065`, the
beat's handoff.
`python evals/pkg_check.py ste-clean evals/sample-results/lab-tracker/package` reads 0 hard
findings over the refreshed guide and skips `project-kickoff.md` by name.

## 3. What the beat found, and what changed because of it

1. **The rewrite skill named no path for an Approved row of a family with no supersession
   column.** A requirement, a constraint, an assumption, a dependency or a decision is Approved but
   not trigger-immutable, and has no `superseded_by`. The real agent stopped on it (Q0). The skill
   now says: rewritten in place, still Approved, only while the change is punctuation or a sentence
   split; a change of meaning is a new row through the `update` flow. The operator's word in T2 was
   the first ruling under that sentence.
2. **The default-skip list did not name a Promoted lesson.** The agent skipped LL-001 on its own
   call. The skill's DEFAULT now lists a Promoted lesson beside an Approved one.
3. **The latest handoff entry.** The agent reasoned its way to "append-only, leaves the rule when
   this session writes its own handoff". The skill now says that in one bullet.
4. The agent read the "after" count before its own handoff and said so. Step 8's order ("re-run,
   show the counts, then the next batch") is kept: the next batch would read the current count.
5. No engine defect. No permission denial. The hook ran on both turns under the 5.9.0 bundle.

Cost: $2.29 (T1 $0.77, T2 $1.51). Transcripts stay in the maintainer's `~/.claude/projects/`.
