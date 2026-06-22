# Workflow — 22 stages (authoritative)

Drive these in order; loops back are allowed and expected. Each stage lists **In · Do · Out · Enter · Exit
· Validate · Fail · Human · Artifacts**. "Human" marks where you pause for input/approval. Do not pass an
approval gate on the user's behalf. Gates referenced as `G-*` are defined in `quality-gates.md`.

Legend: Enter = entry criteria, Exit = exit criteria, Fail = failure conditions (stay/loop), Human =
human-intervention point.

## Phase A — Understand

### 1. Intake
- **In:** raw project description (prose and/or structured file), optional flags.
- **Do:** load input; detect format; attach to state; record provenance (source spans). Parse against
  `project-input.schema.json` where structured.
- **Out:** `keystone-state.json` seeded; raw input archived.
- **Enter:** any non-empty input. **Exit:** input captured with provenance.
- **Validate:** input is readable; encoding sane. **Fail:** empty/unreadable → ask for input.
- **Human:** confirm scope of the request (mode). **Artifacts:** state.

### 2. Initial classification
- **In:** captured input. **Do:** classify project type (e.g. small software / enterprise platform /
  R&D-heavy / legacy modernization / AI-agentic / data / infra), size, and risk profile; pick a profile
  that biases artifact selection and research depth.
- **Out:** `project_profile` in state. **Enter:** Stage 1 done. **Exit:** profile recorded + shown.
- **Validate:** profile justified by input. **Fail:** input too thin to classify → note and proceed with
  "unknown" profile, raise an `OQ-`. **Human:** confirm/adjust profile. **Artifacts:** state.

### 3. Requirement extraction
- **In:** input + provenance. **Do:** extract candidate requirements **verbatim** with source spans;
  do not paraphrase away meaning. Tag each as functional/non-functional/constraint/preference candidate.
- **Out:** raw requirement candidates. **Enter:** profile set. **Exit:** every requirement-bearing input
  span is either extracted or explicitly marked out-of-scope.
- **Validate:** each candidate has a source. **Fail:** ambiguous span → keep verbatim, flag for Stage 5.
- **Human:** none yet. **Artifacts:** draft requirements.

### 4. Requirement normalization
- **In:** candidates. **Do:** assign IDs (`FR-/NFR-/CON-`), deduplicate, split compound statements,
  classify preference vs requirement, set priority (MVP/Full), normalize into `requirement.schema.json`.
- **Out:** requirement registers (Draft). **Enter:** Stage 3 done. **Exit:** all candidates resolved to a
  register row or merged/withdrawn (with reason).
- **Validate:** G-REQ-SRC (every requirement has a source); IDs unique. **Fail:** unsourced requirement →
  demote to `ASM-` or raise `OQ-`. **Human:** none. **Artifacts:** requirements/, assumption-register.

### 5. Ambiguity detection
- **In:** normalized requirements. **Do:** find vague terms, undefined quantities, unclear actors,
  missing acceptance, unstated NFR thresholds. **Out:** ambiguity list → candidate `OQ-`.
- **Enter:** Stage 4. **Exit:** each ambiguity becomes an `OQ-` or is resolved by an `ASM-`.
- **Validate:** no requirement marked "clear" still contains a flagged vague term. **Fail:** loop.
- **Human:** none yet (batch into Stage 7). **Artifacts:** open-question-register.

### 6. Contradiction & dependency detection
- **In:** requirements + constraints. **Do:** detect conflicts (mutually exclusive requirements, NFR vs
  constraint clashes), hidden dependencies, and premature solution decisions embedded in the brief.
- **Out:** contradiction list, `DEP-` entries, flagged premature decisions. **Enter:** Stage 5.
- **Exit:** each contradiction has a resolution path (clarify / decide / defer). **Validate:** G-CONFLICT
  (no unresolved hard contradiction proceeds past Stage 8). **Fail:** loop / escalate to Stage 7.
- **Human:** none yet. **Artifacts:** dependency-register, open-question-register, open-decision-register.

### 7. Clarification
- **In:** `OQ-` + contradictions. **Do:** apply `clarification.md` — batch focused questions only where
  the answer changes the plan; elsewhere record `ASM-`. **Out:** answered `OQ-`, new `ASM-`, updated
  requirements. **Enter:** Stages 5–6 produced items. **Exit:** every blocking `OQ-` is answered or
  consciously deferred with an `ASM-`/risk. **Validate:** no blocking `OQ-` left open silently.
- **Fail:** user unavailable → proceed under explicit assumptions, mark package "provisional".
- **Human:** ✅ primary clarification point. **Artifacts:** registers updated.

### 8. Scope definition
- **In:** clarified requirements. **Do:** lock goals, non-goals, in-scope, out-of-scope, success metrics
  (`KPI-`); write the charter. **Out:** `00-charter.md` (Proposed). **Enter:** blocking questions handled.
- **Exit:** scope approved. **Validate:** every MVP requirement maps inside scope; non-goals explicit.
- **Fail:** scope rejected → revise. **Human:** ✅ approve scope. **Artifacts:** charter, executive-summary draft.

## Phase B — Explore

### 9. Research planning
- **In:** scope + uncertainties. **Do:** size research to genuine uncertainty (`research-depth.md`); build
  a research plan + R&D backlog targeting the riskiest unknowns. **Out:** research-plan, rnd-backlog.
- **Enter:** scope approved. **Exit:** each high-risk unknown has a planned investigation. **Validate:**
  research effort proportional to risk (not over/under). **Fail:** unbounded research → timebox. **Human:**
  confirm depth for large efforts. **Artifacts:** research/.

### 10. Architecture exploration
- **In:** requirements + research. **Do:** explore candidate architectures/components; identify decision
  points; draft context/component diagrams. **Out:** architecture draft + diagrams. **Enter:** Stage 9.
- **Exit:** at least one viable architecture per major decision point, with open points named. **Validate:**
  architecture covers all MVP requirements. **Fail:** a requirement no architecture satisfies → raise risk
  + `OQ-`. **Human:** none yet. **Artifacts:** architecture/, diagrams/.

### 11. Option comparison
- **In:** options per decision point. **Do:** compare against **explicit weighted criteria**; mark fit
  (strong/partial/weak/unknown/unsuitable); keep losers. **Out:** technology-comparison matrices.
- **Enter:** Stage 10. **Exit:** each decision point has a defensible front-runner or a clear "needs
  experiment". **Validate:** criteria stated before scoring; claims cited/`unverified`. **Fail:** tie with
  no tiebreak → define an experiment (Stage 13). **Human:** none yet. **Artifacts:** architecture/technology-comparison.

### 12. Hypothesis definition
- **In:** unknowns blocking decisions. **Do:** state falsifiable hypotheses (`HYP-`) with the signal that
  would confirm/refute. **Out:** hypothesis-register. **Enter:** Stage 11. **Exit:** each blocking unknown
  has a hypothesis or a decision. **Validate:** hypotheses are testable. **Fail:** untestable → reframe.
- **Human:** none. **Artifacts:** research/hypothesis-register.

### 13. POC & experiment planning
- **In:** `HYP-`. **Do:** plan minimal experiments/POCs with explicit PASS/FAIL criteria and a timebox.
- **Out:** `EXP-`/`POC-` plans. **Enter:** Stage 12. **Exit:** every decision-blocking hypothesis has a
  planned experiment. **Validate:** each experiment has PASS/FAIL + timebox. **Fail:** vague experiment →
  sharpen. **Human:** approve experiment budget for costly POCs. **Artifacts:** experiments/, pocs/.

### 14. Decision capture
- **In:** comparisons + (where available) experiment results. **Do:** record decisions (`DEC-`/`ADR-`) with
  status, rationale, alternatives, consequences; promote significant ones to ADRs. **Out:** decisions +
  ADRs. **Enter:** Stages 11–13. **Exit:** each decision point is Decided, Deferred (with trigger), or
  Experiment-pending. **Validate:** G-DEC-STATUS; rejected alternatives retained. **Fail:** decision with no
  rationale → block. **Human:** ✅ approve key decisions. **Artifacts:** decisions/, adrs/.

### 15. Risk analysis
- **In:** everything so far. **Do:** enumerate technical/dependency/platform/delivery/compliance risks;
  score impact·likelihood; write mitigations; tag MVP-or-Full. **Out:** risk-register. **Enter:** Stage 14.
- **Exit:** top risks have owners + mitigations + triggers. **Validate:** G-RISK (high-impact requirements
  and decisions have an associated risk view). **Fail:** unmitigated critical risk → flag for readiness.
- **Human:** confirm risk appetite. **Artifacts:** risks/.

## Phase C — Plan & hand off

### 16. Execution planning
- **In:** decisions + risks + scope. **Do:** phased roadmap (`PH-`) with goal/scope/deliverables/validation
  /risks/exit per phase; work-breakdown (`WBS-`); milestones (`MS-`); DoR/DoD; checkpoints. **Out:** planning/,
  execution/. **Enter:** Stages 14–15. **Exit:** MVP path is sequenced and each phase has exit criteria.
- **Validate:** G-EXEC (leaf items actionable+testable; phases gated). **Fail:** abstract phase → decompose.
- **Human:** approve roadmap. **Artifacts:** roadmap, work-breakdown, milestones, DoR/DoD, checkpoints.

### 17. Artifact generation
- **In:** all approved content. **Do:** generate the selected artifact set from `../templates/` per
  `artifact-rules.md`; build the traceability matrix (`traceability.md`); fill schemas. **Out:** the
  populated package. **Enter:** Stage 16. **Exit:** every selected artifact exists, is populated (no
  stubs), and is internally cross-linked. **Validate:** G-COMPLETE, G-TRACE, G-IDS. **Fail:** stub/empty
  artifact → fill or drop. **Human:** none. **Artifacts:** the full package.

### 18. Repository initialization
- **In:** populated package + flags. **Do:** run `../scripts/init_skill_repo.py` (or wrapper) for the
  target repo: folders, baseline files, README+logo, license, ADR/doc dirs, changelog, version, initial
  commit, optional remote+push. Default **dry-run**; require confirmation to write; never overwrite without
  `--force`. **Out:** initialized repo (or dry-run report). **Enter:** Stage 17; mode allows repo. **Exit:**
  repo created or dry-run reviewed. **Validate:** prerequisites present; target clean or `--force`. **Fail:**
  missing git/dirty tree → report and stop. **Human:** ✅ approve actual creation/push. **Artifacts:** repo, scripts/.

### 19. Quality validation
- **In:** package (+ repo). **Do:** run all quality gates (`quality-gates.md`) via `../scripts/` validators.
- **Out:** validation report. **Enter:** Stage 17 (repo optional). **Exit:** all **critical** gates pass.
- **Validate:** gate engine returns no critical failures. **Fail:** critical gate fails → loop to the owning
  stage. **Human:** review non-critical warnings. **Artifacts:** validation/.

### 20. Execution-agent handoff
- **In:** validated package. **Do:** assemble the handoff (`handoff.md`); write initial + follow-up + review
  prompts (`prompt-templates.md`); produce the handoff manifest. **Out:** handoff/. **Enter:** Stage 19 green.
- **Exit:** an external agent could start from the initial prompt with no missing context. **Validate:**
  G-HANDOFF (prompts reference real artifacts; no dangling instructions; agent-neutral). **Fail:** prompt
  references a missing artifact → fix. **Human:** approve handoff. **Artifacts:** handoff/.

### 21. Progress & decision update cycles
- **In:** execution feedback, new decisions, status. **Do:** record progress; update decision statuses
  (Proposed→Approved/…); update acceptance-criteria status + evidence and regenerate the **acceptance
  audit** (verdict × evidence per `AC-`; gate **G-PROGRESS** checks coverage) and the status report;
  re-derive dependent artifacts; bump versions. **Out:** progress/, validation/acceptance-audit.md,
  updated registers.
- **Enter:** package handed off; an update arrives. **Exit:** state and derived artifacts consistent.
- **Validate:** G-TRACE re-passes; superseded items linked. **Fail:** orphaned reference → repair.
- **Human:** approve material changes. **Artifacts:** progress/, affected registers (versioned).

### 22. Final readiness assessment
- **In:** the whole package. **Do:** run the readiness checklist; summarize gate results, open items,
  residual risks, and a go/no-go. **Out:** `execution-readiness-report.md`. **Enter:** Stages 19–20 done.
- **Exit:** report emitted; go/no-go stated. **Validate:** no critical gate failing; all `OQ-` either closed
  or listed as accepted-open. **Fail:** critical gap → not ready; list what's missing. **Human:** ✅ final
  go/no-go. **Artifacts:** handoff/execution-readiness-report.

## Loops

Clarification (7), decision capture (14), and validation (19) commonly send you back upstream. Returning to
an earlier stage is normal discipline, not failure — but record why (a note or `DEC-`) so the trail is intact.
