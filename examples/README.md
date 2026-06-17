# Keystone worked examples

Five end-to-end worked examples, one per project archetype. Each shows how Keystone takes a raw
project brief through clarification, artifact selection, a pruned package structure, representative
filled artifacts, the execution-agent handoff prompts, and a final execution-readiness verdict —
**without** building the whole package. They demonstrate the methodology and its safeguards on
deliberately different shapes of work, so a reader can see *why* the artifact set, research depth, and
gating differ from one project type to the next.

These examples are illustrative and self-contained. They invent plausible projects (a CLI, a billing
platform, an R&D study, a legacy modernization, an AI agent); each is a self-contained illustration, not a real product. Example
05 is expanded into a fuller, file-by-file package under
[`../generated-samples/support-triage-agent/`](../generated-samples/support-triage-agent/).

## What each example contains

Every scenario folder holds the same eight files, mirroring the stages of the workflow:

| File | Stage(s) | What it shows |
|---|---|---|
| `input.md` | 1 Intake | The raw brief as a user would paste it (unprocessed). |
| `clarifications.md` | 5–7 Clarify | The focused, **batched** questions Keystone asks + the `[given]`/assumed answers + the `ASM-` recorded when it proceeds without an answer. |
| `selected-artifacts.md` | 17 (rules) | Which **Always** artifacts and which **Conditional** triggers fired, with the reason — and what was deliberately omitted. |
| `structure.md` | generated-structure | The package directory tree **pruned to this project** (no empty dirs). |
| `representative-artifacts.md` | 3–16 | 1–3 short, *real* filled artifacts (a few `FR-`/`NFR-`, invariants, an ADR, risk rows, a phase or two, acceptance criteria) with correct identifiers. |
| `initial-prompt.md` | 20 Handoff | The execution-agent initial prompt: orient → **one** bounded task → stop gate; lists the `INV-`. |
| `follow-up-prompt.md` | 20 Handoff | One representative phase-gate follow-up prompt. |
| `readiness.md` | 22 Readiness | Per-critical-gate pass/fail + go/no-go + open items. |

## The five examples

### 01 · [small-software-cli](01-small-software-cli/) — `repostat`
A single-developer CLI that reports git contribution/activity statistics.
**Demonstrates the minimal path:** the *Always* set plus a single ADR and a test strategy; research,
experiments, technology-comparison, and heavy diagrams are **omitted with reasons** because there is no
genuine technical uncertainty. Shows that small projects collapse toward the minimal artifact set and
that a clean project produces an unqualified **GO**. Invariants stay tiny but real (read-only repo,
deterministic output).

### 02 · [enterprise-platform](02-enterprise-platform/) — `unify-billing`
A new multi-tenant subscription billing & invoicing platform (pricing models, invoicing, proration,
tax, dunning, three surfaces).
**Demonstrates the broad path:** nearly every conditional artifact fires — architecture + ADRs +
diagrams, a technology-comparison with stated weights, stakeholder register + WBS + milestones, NFR
thresholds + test strategy, compliance constraints, dependency register, progress cadence. Shows
**financial-correctness and tenant-isolation invariants**, a vendor-neutral payment-provider port, and
one decision (`ADR-0002`) correctly held **Proposed** pending finance review while the rest proceed.

### 03 · [rnd-initiative](03-rnd-initiative/) — `semantic-cache`
An R&D study into a semantic caching layer in front of an LLM API (cost/latency win vs wrong-answer
risk).
**Demonstrates the research-first path and three safeguards at once:** *no premature architecture*
(the technology-comparison verdict is explicitly "needs experiment `EXP-002`"), *decide-after-experiment*
(`DEC-001/002/003` are **Deferred** with triggers, never pretended Approved), and *surface the trade-off*
(false-positive rate vs hit-rate is characterized by `EXP-001`, not assumed). Phase 1 deliverable is
**knowledge + a go/no-go**, not a product; readiness is "GO to run the experiments," with
productionization intentionally undecided.

### 04 · [legacy-modernization](04-legacy-modernization/) — `claims-portal-modernization`
A strangler-fig modernization of a 12-year-old monolithic insurance claims app that must stay live.
**Demonstrates migration discipline under hard constraints:** data-preservation and audit-continuity
**invariants**, a dependency register for downstream systems, ADRs for the routing facade and the data
strategy, and a phased roadmap whose write-path phase (`PH-2`) is **gated on a spike** (`EXP-001`).
Shows a real tension (zero-downtime desire vs a bounded cutover window) resolved by an assumption, and a
**conditional readiness**: GO for `PH-1`, with `PH-2` entry contingent on the spike passing and
`ADR-0002` being approved.

### 05 · [ai-agentic-system](05-ai-agentic-system/) — `support-triage-agent`
A supervised AI agent that triages support email: classify → retrieve → draft → route/approve, with a
human-in-the-loop gate before any send.
**Demonstrates safety-first agentic planning:** five **safety invariants** (human approval before send,
grounding-or-defer, no PII egress, full audit, bounded loop/cost), risk rows for hallucination /
PII / prompt-injection / runaway cost, and an auto-send capability (`FR-008`) **gated** behind a
calibration experiment (`EXP-001`) and a decision (`ADR-0004`, **Proposed**). This is the example
expanded in full under [`../generated-samples/support-triage-agent/`](../generated-samples/support-triage-agent/).

## How to read these

- Start with `input.md`, then `clarifications.md`, to see what Keystone *had* versus what it *asked*.
- Read `selected-artifacts.md` to see the artifact-selection logic produce a different set per archetype.
- Skim `representative-artifacts.md` for the identifier discipline (every `FR-`/`NFR-` has a source;
  decisions carry an explicit status; `Proposed`/`Deferred` is never rendered as `Approved`).
- The two prompt files show the handoff contract: the initial prompt never authorizes building the whole
  system; it orients, gives one bounded task, and stops at an approval gate.
- `readiness.md` is the honesty check — note how 03 and 04 report *conditional* readiness rather than a
  blanket "ready," because that is what the evidence supports.

## Conventions (shared by all examples)

Identifiers follow `../skill/references/governance.md`:
`FR- NFR- CON- INV- ASM- DEP- OQ- DEC- ADR-NNNN RISK- HYP- EXP- POC- KPI- STK- PH- MS- WBS- AC- TEST-`.
Decision statuses are exactly **Proposed / Approved / Rejected / Superseded / Deferred**. Files and
directories are kebab-case. The plans stay vendor-, agent-, and stack-neutral unless an `ASM-` records a
specific choice.
