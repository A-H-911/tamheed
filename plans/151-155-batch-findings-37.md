# Tamheed v5.6.0 — the findings_37 batch: the release named on two surfaces, the export anchored on the commit

Status: **IN PROGRESS** — index section "Field cycle findings_37" in [README.md](README.md).
Commits: 151 `e151e3d`, 152 `6bae045`, 153 `9db4b7c`. Execution order: 151 → 152 → 153 → 154 → 155.

Read-only evidence this record rests on: ACMP `findings_37.md` (`27f63ae8` → `66ad54c4`), the rows
`DEC-235` (Approved), the journal `PE-1523`..`PE-1531`, the 25 feedback rows and 112 lessons
(unchanged), the field's `hook-trace.md`, `prm-next.md` and `tamheed-package-mechanics.md`; the
installed 5.5.0 tree and the field's review page, read by the script committed under
[`evidence/scripts-findings-37/`](evidence/scripts-findings-37/) with its output beside it;
Claude Code's settings page and plugin loading reference, the HTML Standard, the Reproducible
Builds page on version information and one author's page on `key=value` log lines, fetched
2026-09-28; the approved plan
(`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`, revision 2 after a
devil's-advocate review); the interview rulings R36–R44.

**Review.** The maintainer's first `advisor` call returned an error. A forked copy of the session
reviewed the first slate; it is the same model, so it is a second reading. After the operator
asked, a second `advisor` call answered and reviewed the export-order question, the key's name and
revision 1 of the plan. The five options of the first interview were checked by the fork only.

## 0. Measurements

Every count is from one machine and true at its run (`m37.py`, output in `m37.out.txt`).

| # | Measurement | Result |
|---|---|---|
| M1 | `server_info` in the maintainer's session, started 2026-09-27 19:37Z, before 5.5.0 was installed | `5.4.0` |
| M2 | That session's trace line at its compaction, 2026-09-28 04:53:14Z | `source=compact lines=0 chars=0 status=silent session=61baf644-…`; it names no version |
| M3 | The installed 5.5.0 tree, run-time folders left out | 86 files, all text; every line of each ends CRLF; the blobs are LF |
| M4 | The bundle, lines naming bind, binds, binding, bound | 146 by grep before plan 152, every one read; 152 at the script's run, after plan 152's sentences and with `.sql` in scope; none negated, none in the old sense |
| M5 | The field's review page | 14,525,561 bytes: registers 9.0 MB, execution 3.3 MB, graph 0.9 MB, flow 0.8 MB; its head carries the digest stamp and no version stamp |
| M6 | `review_current` named in | 13 lab lines; 0 eval assertions; 5 test lines before plan 151, 10 after |
| M7 | Lint 13's negated pattern over the bundle and `docs/*.md`, and seven controls | 76 files, 0 hits; 7 of 7 controls as wanted |
| M8 | `export_html` in the bundle's teaching text | 17 lines before plan 152, four step lists writing after the export; 18 after, none |
| M9 | `python check.py`, the trace variable unset, plans 151 to 154 | ALL CHECKS PASSED each time |
| M10 | The stock guide's body against the 5.5.0 body, at the stamp | one line in, one line out: the title |
| M11 | Lab beat 28 (plan 154), [the report](evidence/lab-continuation-report-154-2026-09-28.md) | held on its first run, the scratch phase first. Before the first export the keys read `review_current: true`, `review_exported_by: null`; after it `5.6.0`, the digest unchanged, a second export identical. A write after the export turned `review_current` false and the next export true. Both trace lines opened `version=5.6.0`; a bundle with no manifest wrote `version=-` |

## 1. What the field returned (no defect, no feedback row)

P0–P9 and P11 held. P10 was not exercised: no lesson was Proposed and none was manufactured. A
prediction of the field's own, that a version marker follows the install, was refuted by it.

- **E1.** The brief's sweep missed two live sentences in the old sense: the kickoff prompt, which
  the sweep never opened, and a memory line that negated the verb.
- **E2.** P9 promised the hook block "with its `Corrections` line". The brief's own close-out order
  writes a fresh handoff before the compaction.
- **The §3 question.** Whether a session started before the upgrade writes a line only after a
  reload. The hook did not change between the tags, and the line named no version.
- **Practices the skills did not state:** one reading rule for fourteen dated records; carried
  handoff lines marked as carried; the export after the binds.
- **About Claude Code:** a session started in a subfolder loaded no plugin; an update leaves the
  old version folder on disk with a marker.

## 2. Rulings (R36–R44, binding; R7–R35 stand)

| # | Ruling |
|---|---|
| R36 | The trace line carries the hook's version, right after the timestamp. The tail is unchanged. A silent line carries it too. The resume block does not change. |
| R37 | `export_html` stamps the version that exported the page. `package_verify` reports it in a new key, `None` on a page with no stamp. `review_current` keeps its meaning. |
| R38 | `written-claims` gains the rule for a ruling that changes a word. |
| R39 | `session-handoff` gains the carried-line sentence. Its order sentence is ruled by R43. |
| R40 | Not absorbed: the provenance clause, and the failed-prediction clause. |
| R41 | In scope: lint 13's negated shape; the docs corrections, cited; lab beat 28 and evals. |
| R42 | The review page's weight is not studied this release. |
| R43 | The commit is the anchor. The export precedes the commit that carries the page, and `package_verify` reads `review_current` true right before it. After a bind: bind, export, commit both; that commit stays unbound. Five step lists follow it. R43 widens R39's second sentence. |
| R44 | The key is `review_exported_by`. R44 replaces the name in R37's option text. |

MINOR is not a ruling: it is the repo's rule (additive = MINOR). The meta's name,
`tamheed-version`, is the maintainer's choice beside `tamheed-digest`.

## 3. Execution

| Plan | What | Status |
|---|---|---|
| 151 | [The version in the trace line and on the review page](151-the-version-in-the-trace-and-on-the-page.md) | DONE `e151e3d` |
| 152 | [The export before the commit, two sentences, lint 13's negated shape](152-the-export-before-the-commit-and-two-sentences.md) | DONE `6bae045` |
| 153 | [Docs + diagrams sweep for v5.6.0](153-docs-and-diagrams-sweep-findings-37.md) | DONE `9db4b7c` |
| 154 | [The version stamp, then lab beat 28 + evals](154-stamp-then-lab-beat-28.md) | DONE |
| 155 | [Tag v5.6.0, the brief file, close-out](155-release-v560.md) | PLANNED |

## 4. The 5.5.0 brief's errors, owned, and the maintainer's own

| # | Error | Class |
|---|---|---|
| W23 | The brief's sweep matched five phrasings. The 5.5.0 cycle's own lesson said to grep a word's every use and read each hit; it was applied to the bundle and not to the field copy. | a lesson not applied to its second subject |
| W24 | The sweep's families left out the kickoff prompt. | incomplete scope |
| W25 | P9 was written as unconditional and held only on the copy's state. | a class conditional on state |
| W26 | A question was asked before the instrument that could answer it was named. | unanswerable question |
| W27 | The first slate missed the order conflict between `session-handoff` and the lab. The fork found it. | gap in the maintainer's read |
| W28 | Two skill sentences were offered although the skills mostly carry them. | over-building |
| W29 | A line-ending pin was considered; a pull rewrites only changed files, so the installed tree would hold mixed endings. | a fix worse than the fault |
| W30 | Revision 1 said only `session-handoff` exports before a write. Four lists did. | true and too narrow |
| W31 | The first rule for it, "no write follows the export", cannot hold. The advisor caught it. | unsatisfiable rule |
| W32 | "62 text files": the installed tree holds 86. | wrong count |
| W33 | "Every hit read", with three long lines unread. | overclaim |
| W34 | "The advisor is unavailable in this session", after one failed call. | a boundary written untested |
| W35 | The key was first named with the word 5.5.0 gave to the note's roster. | one word, two senses |
| W36 | Lint 13's wider pattern was named and not specified; its "zero hits" was the fork's. | unverified |
| W37 | Research fetched after revision 1 did not reach it; one source argues against R36's placement. | research not recorded |
| W38 | "New eval assertions for the key": a key is a tool result, and the evals read files. | not executable as written |
| W39 | A key no text named. | missing teaching |
| W40 | The round's measurements were typed into the shell. | non-reproducible |
| W41 | A line on the field's open change request read as measured. | unlabelled source |
| W42 | The field's scripts were assumed to survive a new field in the line. | hidden assumption |
| W43 | The stamp's value and the hook's manifest read had no failure posture. | missing guard |

## 5. Execution notes (owned as they land)

1. Plan 152's table in the approved plan gave `release-close-out` a commit between its notes and
   its bind. The list binds the release's own tag or commit, which exists before the ceremony. The
   list changed in its order only.
2. Plan 153's first wording of D-LINT-NEGATED quoted the field's sentence, and lint 13 refused
   it. The entry was reworded. The lint's first catch was the maintainer's own prose.
3. Plan 153's first edit of the upgrade steps put its sentences between a claim and the
   parenthesis that belonged to it. Moved before the commit.
