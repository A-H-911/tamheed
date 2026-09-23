# Tamheed v4.13.0 — the findings_29 batch: the feedback channel's middle, the header read, three guard refinements

Status: **EXECUTED — v4.13.0 tagged on `91774b6`, 2026-09-23 (revision 2 approved after the devil's-advocate review).** Index: [README.md](README.md) § Field cycle findings_29.
Read-only work only: `findings_29.md` in full; the fifteen `FB-` rows through ACMP's tool-written
`exports/feedback.json` (UTF-8; never `data/`); ACMP's diff since findings_28 by file name; every
tamheed-side claim verified in source at the line; ACMP's prompt files classified with the plan-093
predicate (one ACMP claim false, §1.7); the lab fixture's `feedback` and `packages` rows read (it is the
lab's, not ACMP's); the two feedback diagrams and the sweep prompt read in full. Two advisor passes.
**No web research**: every question was settled by source or measurement; nothing here has an external
best practice to consult. Interview rulings (2026-09-23): **FB-014** readiness advisory + journaled middle
**+ a third `handoff_emit` warning**; **go_no_go** presence-checked; **substitute** refuses the re-run
shape + doc; **expect_unchanged** omitted = preserved = unchanged. No new tool (19 stays); no migration;
MINOR, v4.13.0. Changes land in **tamheed only**; ACMP gets a transcript-only brief after the tag.

---

## 1. Weaknesses — my 4.12.0 brief first, then revision 1 of this plan, then the engine

**The brief (owned in the next brief before it asks ACMP anything)**
1. **§4.2's refusal probe could not fail**: the guard is change-checked (`verdict_moves`,
   `tamheed_server.py:618`); re-sending the stored verdict unattended returns `ok: true`. The stop-list
   and the recipe disagreed.
2. **§5.1 named `DW-118` as `substitute`'s first use** — ACMP had done that repair on 2026-09-21.
3. **"A JSON column that would stop parsing"** — the check is `custom_attributes` only (`:737`).
4. **§6 "full rows, as stored" was the riskier instruction** on a bound row: the drift guard is
   presence-checked (`:1618-1620`), so a full re-send makes byte-exact transport of five long columns a
   precondition of a status flip. The `entity_upsert` docstring (`:1258`) says "Send FULL rows" outright,
   although the UPDATE assigns only sent names (`:1657`) and the retire path already documents "an
   omitted column is preserved" (`:1500`). ACMP found the partial recipe by reading the SQL.
5. **"Expect it AMBER on `prm-next.md`"** — wrong. **"None should remain"** measured nothing:
   `handoff_emit` never queries `Reported` (`:3252-3266`). That gap is `FB-014`.
6. **"Your four project prompts"** — ACMP has three. ACMP then wrote "`slice-review.md` is not scanned".
7. **`expect_unchanged` was recommended beside every write without saying what it means on a partial
   row** (§1.6 below).

**Revision 1 of this plan**
8. **It missed the stock sweep prompt.** `register-liveness.md` walks the advisories by name and
   `tests/test_mcp_contract.py:3800-3809` pins that list — and **`prompt-ids-resolve` (plan 093) was never
   added to either**. Plan 100 adds both rules there: a second stock body changes, a second `4.13.0`
   history key, and `refresh_stock` refreshes two fixture guides at release.
9. **It would have written a false journal row.** The `feedback_pe` writer (`:1799-1804`) stamps every
   row "on the operator's word — operator_confirm attested"; a bound-to-bound move has no word.
10. **The fold split had no predicates**, and the rule, the warning and the fold would have drifted.
11. **It assumed the lab fixture is migrated** for the `v1_manifest_derived` check; it is not
    (`packages.custom_attributes` null, `mvp_definition` null). The check needs a seeded package.
12. **"Dry-run on the fixture"** without saying *on a copy*: a slip dirties `evals/sample-results/`.
13. **"Update the docs" without having read the two diagrams** (`docs/entities.md:1019-1030`,
    `docs/architecture.md:100-108`) — now read; edits are named below.

**The engine (findings_29, each verified)**
14. `FB-014`: no liveness for `Reported` rows; the middle of the channel is unjournaled (`:1610`, `:1617`
    fire only for entering/leaving `_FEEDBACK_BOUND = {Confirmed, Reported, Resolved}`, `:323`).
15. `FB-015`: `_PACKAGE_ROW` (`:4112`) omits `mvp_definition`, `created_at`; only the page renders all
    ten, with an annotation (`export_html.py:121-127`) `server_info` lacks.
16. `substitute` not idempotent when `new` contains `old` (`:736`); same class as digit-glue, unguarded.
17. `expect_unchanged` refuses a correct partial write (`:1366-1367`, "an omitted column counts as
    changed") while the retire path (`:1500`) treats omission as preservation — two semantics in one
    function.
18. The page's middle fold (`export_html.py:566`) files an unanswered `Reported` row under a closing
    heading; the fold anchor `feedback-closed` is not pinned by any test (grepped).

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by source or measurement**
- Every findings_29 citation (§1 `:618`; §2 `:3252-3266`; §4 `:1366`; §5 `:4112`; §6 `:1618-1620`,
  `:1657`). No test re-sends the same verdict unattended (`grep go_no_go tests/ evals/`); no eval pins a
  readiness-rule count or a fold heading; `check.py` compares neither `review.html` nor `exports/`.
- `_scan_prompt_ids` selects by byte-equality against every stock body (`:460-475`). ACMP's six scanned
  files are `prm-next.md`, three `project-*.md`, `integrity-check.md`, **`slice-review.md`** (customised,
  3,259 bytes). ACMP's `register-liveness.md` and `README.md` are byte-equal stock → both refresh.
- ACMP's package diff since findings_28 is the predicted set plus `WBS-24.4` and `LL-098`; its
  `MEMORY.md`/`AGENTS.md`/note edits contradict nothing in tamheed's usage policy; four of their
  sentences are invalidated by this release (named in the brief).
- The disposition landed as instructed; `FB-014`/`FB-015` Confirmed on the word → Reported; export
  `count == total == 15`.
- The lab fixture: `FB-001` `Reported`/`resolved_in` null, `FB-002` `Confirmed` → the new rule reads
  amber with one entity and the third warning names `FB-001`; `test_mcp_contract.py:2810` checks header
  keys with `in`, so two more keys break nothing.
- Readiness counts: `quality-gates.md:61`, `docs/architecture.md:66` ("nineteen").

**Rejected**
- "`slice-review.md` is not scanned"; "a JSON column"; "four project prompts"; "the probe proves the
  guard"; "full rows are the safe shape on a bound row"; "the fixture is migrated".

**Unresolved — settled in execution, never by guessing**
- Whether the `register-liveness.md` renumbering (16 → 18 walk steps) trips the teaching-vocabulary lint;
  RED shows.
- Whether the export test's fixture package has a `Reported` row for the new fold; if not the test seeds
  one.

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A `system:feedback-guard` row that claims attestation for an unattended move | `feedback_pe` carries a third element (`attested: bool`); the entry reads "on the operator's word — operator_confirm attested" only when the word was given, else "bookkeeping move (Confirmed→Reported / Reported→Resolved) — no word required"; test pins both texts |
| Rule, warning and fold predicates drift | One module constant `_FEEDBACK_UNANSWERED_WHERE = "lifecycle_status = 'Reported' AND resolved_in IS NULL AND kind <> 'local-tool'"` used by all three (the page imports nothing from the server — it repeats the literal and a test asserts the two strings are equal) |
| `feedback-unanswered` amber forever on packages that never use feedback | Emitted only when `feedback` has rows (`waivers-open-ended`, plan 079); registers excluded |
| Presence-checking `go_no_go` writes `transition` rows for old == new | Two predicates: refuse on `"go_no_go" in cols` without the word; journal only on `verdict_moves` |
| An agent round-trips `server_info().package` into a header write and is refused | Teaching: name `go_no_go` only when changing it, on the word (server README `entity_upsert` row, governance) |
| The re-run refusal blocks a legitimate first run | Refuse only when `old in new` **and** `new` already occurs in the stored column; order: zero-occurrence → digit-glue → re-run → `custom_attributes` JSON; message: "`{new!r}` already occurs N time(s) in `{col}` and contains `{old!r}` — a re-run compounds; send old/new with the characters that bound them (ACMP: the backticks), or a full row" |
| `expect_unchanged` omitted = unchanged opens a hole | None: the UPDATE never assigns an omitted column (`:1657`; `:1500` is the precedent); a SENT column must still match; a new row still refused ("guards an UPDATE") |
| The third warning surfaces feedback text | ids only; the invariant at `:3246-3250` restated in the comment |
| Note row / template drift | Identity test; both move in one commit |
| Two stock bodies change | `4.13.0` keys for `README.md` and `register-liveness.md` in the same commit; `test_mcp_contract:3800` tuple gains both rule names; at release the F-1 route is `handoff_emit(refresh_stock=True)`, `refreshed` = both |
| The fixture is dirtied by a dry-run | Every dry-run runs on a **scratchpad copy** (`shutil.copytree`), never the tracked fixture |
| `v1_manifest_derived` unverifiable on the fixture | Acceptance seeds `custom_attributes = {"v1_manifest": {...}}` on a temp package; beat 20 verifies the two new columns on the fixture (`mvp_definition` written then read) and the annotation on a seeded copy |
| A new surface crashes on the recorded fixture (F-4/F-5) | Dry-run script over the copy is a done criterion of 100, 101 and 102, before beat 20 is dispatched |
| Docs edited without being read | Transactional edit script (the 097 pattern): `edit(old, new)` demands exactly one match; the diagrams' new lines are written against the text read today |

## 4. Changes made and why

1. `register-liveness.md` joins plan 100 (walk steps for `feedback-unanswered` and the missing
   `prompt-ids-resolve`; the test tuple; a second history key) — §1.8.
2. The journal row branches on the word — §1.9.
3. The three surfaces share one predicate — §1.10.
4. The `entity_upsert` docstring is corrected (full rows *or* the NOT NULL columns; omitted columns are
   preserved on an UPDATE) and the partial write is taught as the **feedback disposition recipe** only —
   NOT NULL sets differ per family (field report D2).
5. `resolved_in` doctrine for a `question`: the release *or the maintainer's response* that answered it;
   `upstream_ref` names where.
6. The brief's before/after becomes falsifiable: on ACMP's package the rule and the third warning name
   `FB-014`, `FB-015` before disposition and nothing after.
7. Six plans (100–105), the three guard refinements under one security review.

## 5. Refined execution plan

Constraints: stdlib only; no migration; no new tool; bundle never links out; CHANGELOG under
`[Unreleased]` until 105; stock edits carry `4.13.0` history keys; released blocks and shipped migrations
frozen; `system:` actors engine-only. Per plan: record → RED → GREEN → `python check.py` → reviewers where
listed → dry-run on a fixture copy (engine plans) → commit from a message file (explicit staging, nothing
under `.claude`) → push → CI. Status every three minutes.

| # | Plan | Validation → expected |
|---|---|---|
| 100 | **The feedback channel's middle (FB-014).** Engine: `feedback_pe` for a status move *within* the bound set, `attested=False`, journaled `transition` by `system:feedback-guard` with the bookkeeping text; `_FEEDBACK_UNANSWERED_WHERE`; advisory `feedback-unanswered` (only when `feedback` has rows; note: "reported upstream, not yet answered — when it ships set `lifecycle_status: Resolved`, `resolved_in` (the release, or the maintainer's response for a question) and `upstream_ref`, a partial row: id, kind, title and the three; `Rejected` on the word if upstream declined; registers never resolve"); third `handoff_emit` warning, ids only. Page: fold "Reported upstream, not yet answered" (`feedback-reported`) = the constant; "Resolved or rejected (kept as evidence)" (`feedback-closed`) = `kind <> 'local-tool' AND (lifecycle_status IN ('Resolved','Rejected') OR (lifecycle_status = 'Reported' AND resolved_in IS NOT NULL))`. Teaching: note row + `agent-control.template.md` ("…names every row until it has left the package, and every reported row until it is answered"); `prompts/README.md:148` + key; `register-liveness.md` gains walk steps for `prompt-ids-resolve` and `feedback-unanswered` (+ key), test tuple `:3800` extended; governance `:176`; counts nineteen → twenty ("two of them only when the package has waivers / feedback rows") in `quality-gates.md`, `architecture.md` | on a fixture copy: rule amber `["FB-001"]`, warning names `FB-001`; a `{id, kind, title, lifecycle_status: Resolved, resolved_in, upstream_ref}` write → `feedback_audit` row with the bookkeeping text, rule pass, warning gone; a fresh package with no feedback rows: rule absent; identity test; export test asserts both folds; `check.py` |
| 101 | **The header read is a superset of the write (FB-015).** `_PACKAGE_ROW` + `mvp_definition`, `created_at`; when `custom_attributes` contains `v1_manifest` (the page's predicate, `export_html.py:123`) `package.v1_manifest_derived = ["mode", "profile", "created_at"]`. Server README `server_info` row; `docs/entities.md` header paragraph | write `mvp_definition` on a copy, read it through `server_info`; seeded `v1_manifest` → list present, fresh → key absent; `:2810` extended to ten keys |
| 102 | **Three guard refinements** (security reviewer). (a) `go_no_go` presence-checked; audit only on `verdict_moves`. (b) `substitute` 15th refusal (order fixed above). (c) `expect_unchanged`: `c in cols and not _same_value(...)`; error "(a sent column must match the stored row; an omitted column is preserved by the UPDATE and never counts as drift)". Docstrings: `entity_upsert` "Send full rows, or at least the NOT NULL columns…"; the two `expect_unchanged` clauses; `custom_attributes` not "a JSON column" (`:683`, server README, SECURITY.md, CHANGELOG `[Unreleased]` only) | unattended same-verdict re-send refused; attested same-verdict `ok` with **no** `package_audit`; a prefix repair passes once, refused the second time naming the count and the remedy; glue fires before re-run; partial row + `expect_unchanged: ["detail"]` passes and `changed_columns` omits `detail`; a sent drifted column still refused; dry-run on a copy |
| 103 | **Teaching precision + docs & diagrams sweep** (transactional script). README/governance: the disposition recipe; the substitute idempotence sentence beside the digit-glue note (server README, SECURITY.md); "an id check is not a truth check" clause in the `prose-ids-resolve` and `prompt-ids-resolve` notes and `quality-gates.md`; header teaching (name `go_no_go` only when changing it). Diagrams: `docs/entities.md` state diagram — `Confirmed --> Reported` and `Reported --> Resolved` lines gain "engine journals the move (bookkeeping, no word)"; a note line for `feedback-unanswered`; `docs/architecture.md` flowchart — `P -->|feedback-unanswered + handoff_emit name it until resolved_in| M`; the write-side paragraph gains the presence-checked verdict and the re-run refusal; SECURITY.md; root/plugin/server READMEs; CHANGELOG | per-behaviour grep ≥ 2 docs; mermaid lint; `check.py` lints |
| — | **Full test**: `python check.py` (suites under `error::DeprecationWarning`, lints, canonical round-trip, evals); `accept_v4130.py` — one check per behaviour incl. the journal text, the fold split, the seeded annotation — N/N on the batch tree, 0/N on an extracted `v4.12.0` tree; `--selftest` 19/19; CI on every push | N/N vs 0/N |
| 104 | **Lab beat 20** (agent, opus, worktree; the dry-run scripts of 100–102 are re-run on a copy first and cited in the plan file; every new assertion fails on the pre-beat fixture): `FB-001` amber + warning → disposed by the recipe → journaled bookkeeping row, pass, warning gone; `go_no_go` same-verdict unattended refused, attested `ok` without audit; a one-token repair run twice → second refused; `expect_unchanged` on a partial row; `mvp_definition` written and read via `server_info`; the two refreshed stock prompts | new assertions; `plans/evidence/lab-continuation-report-104-…md`; `lab/scenario.md` beat 20 |
| 105 | **Release v4.13.0** (plan-058 recipe; F-1 via `refresh_stock`, `refreshed` = `README.md`, `register-liveness.md`; six stamps; stock-history re-set; annotated tag; CI on the tag) | lints; tag; CI |
| — | **The ACMP brief**, transcript-only, after the tag: upgrade 4.12.0→4.13.0 (no migration); the seven brief errors owned; **`slice-review.md` IS scanned** (six = `prm-next` + three `project-*` + `integrity-check` + `slice-review`); a **falsifiable pair**: before disposition `feedback-unanswered` names `FB-014`, `FB-015` and the third warning names both; `FB-014` → Resolved (plan 100), `FB-015` → Resolved (plan 101) by the recipe; after: pass, none; `refreshed` = two files; the memory lines invalidated (14 refusals → 15 and the order; "an omitted column counts as CHANGED"; "NO liveness surface"; "`go_no_go` is CHANGE-checked"); a probe that can fail this time (same verdict, unattended → refused); `findings_30.md` questions | ACMP's two rows leave `Reported`; `handoff_emit` names nothing |

**Considered and rejected:** exempting bookkeeping writes from the drift check (the recipe already cuts the
surface to two short columns); refusing every `old in new`; a `reported_at` column (the journal row
carries the date); teaching partial rows as the general shape; a `feedback-unanswered` age threshold
(there is no date column; the journal row is the date).

## 6. Approval checkpoint (approved 2026-09-23)

Approval authorized plans 100–105, commits, pushes and the `v4.13.0` tag on
`main` under the standing git delegation, and the ACMP brief. Behaviour and doctrine changes:

1. **`go_no_go` refused whenever named without the operator's word**, even unchanged.
2. **A 15th `substitute` refusal** (the re-run shape); the refusal order is part of the contract.
3. **`expect_unchanged` treats an omitted column as unchanged on an UPDATE.**
4. **Every status move inside the feedback bound set is journaled**, bookkeeping text, no word.
5. **Advisory `feedback-unanswered`** (packages with feedback rows only) + **a third `handoff_emit`
   warning**; the lab fixture reads amber until beat 20 disposes its row.
6. **`server_info().package` grows two columns** and `v1_manifest_derived` on migrated packages.
7. **The review page's feedback folds split** (unanswered vs closed).
8. **Two stock prompt bodies change** (`README.md`, `register-liveness.md` — the latter also repairs
   plan 093's omission).
9. **Doctrine wording**: the disposition recipe; "send full rows, or at least the NOT NULL columns";
   the two `expect_unchanged` clauses; "an id check is not a truth check"; `custom_attributes`.
10. **MINOR release v4.13.0** with lab beat 20.

Approve as written, or name which of the ten to change.

## Execution notes (2026-09-23)

- **Plan 102's security review** found the `expect_unchanged` check ran BEFORE the feedback block's own
  column writes (`lifecycle_status`, `confirmed_at` on a local-tool arrival) — an omitted-then-engine-set
  column slipped past the assertion. Closed: the check runs against the FINAL row; the PoC is a test.
- **Checking the feedback TABLE (the export and the journal's CSV mirror), not only findings_29**: every
  `system:` row in ACMP's 1,359-row journal is the engine's (six actors, no forgery); `PE-1357` had an
  empty actor — `work_bind`'s row, the one engine-written journal row with no author. Fixed under plan
  102's amendment (`system:work-bind`).
- **Beat 20's first dispatch STOPPED correctly at Step 9**: Step 2 resolves the fixture's only
  `Reported` row and beat 18's assertion (`lifecycle_status=Reported --min 1`) counted zero. The copy-based
  dry run (F-4/F-5's lesson) proves a NEW surface fires but never runs `run_evals`, so it cannot see an
  EXISTING assertion the beat falsifies. **Recipe lesson F-6: when a beat moves a lifecycle state, grep
  the case's assertions for predicates naming that state before dispatch.** Ruling: the beat-18
  assertion re-aimed at the engine's confirmation journal row (a fact that survives disposition).
