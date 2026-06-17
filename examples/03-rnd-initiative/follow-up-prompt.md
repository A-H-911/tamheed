# Follow-up prompt — Phase gate: go/no-go after experiments (semantic-cache)

This is the **key R&D follow-up**. The Phase-1 experiments are complete. Your task here is **not another build task** — it is to **synthesize the results, resolve the deferred decisions, and produce the go/no-go**. Read this before doing anything.

## Resume context

Phase **PH-1 (de-risk via experiments) is complete**. State as of this prompt:
- **EXP-001 (hit-rate vs false-positive on workload Z) report**: a threshold was found at which **cost reduction ≈ 34% at a false-positive rate ≈ 0.8%**, holding on the holdout split — i.e. it lands inside the ASM-001 success region (≥ 30% cost reduction at ≤ 1% false positives).
- **EXP-002 (embedding-approach comparison) report**: the **lightweight embedding approach** came within ~1.5 points of the heavyweight approach on accuracy/separation while meeting the lookup-latency budget — within the HYP-002 tolerance.
- **EXP-003 (invalidation / staleness) report**: a **24-hour age-based TTL** held staleness-related wrong answers at ≈ 0.4% on time-sensitive prompts — under the HYP-003 0.5% bar.
- **POC-001 (cache-lookup latency)**: p95 lookup ≈ 38 ms — within the ASM-004 ≤ 50 ms budget (NFR-003).
- Hypotheses **HYP-001, HYP-002, HYP-003** are therefore all resolved (see PASS/FAIL below).

## Task — synthesis and decision resolution (no productionization yet)

Do the following, in order:

1. **Resolve each hypothesis** explicitly with its evidence:
   - HYP-001 → **confirmed** (EXP-001: 34% cost reduction at 0.8% false positives on holdout, inside the ASM-001 region).
   - HYP-002 → **confirmed** (EXP-002: lightweight approach within 2 pts at lower latency/cost).
   - HYP-003 → **confirmed** (EXP-003: 24h TTL holds staleness false positives at 0.4% ≤ 0.5%).
2. **Resolve each Deferred decision** from Deferred to Approved or Rejected, **with written rationale tied to the evidence**:
   - **DEC-001 (productionize?)** → its trigger (EXP-001 PASS + acceptable EXP-003 staleness) is satisfied → move to **Approved (go)**, rationale citing EXP-001 + EXP-003.
   - **DEC-002 (embedding approach)** → move from Deferred to **Approved** for the **lightweight approach**, rationale citing EXP-002 (and record the choice as the ASM- that now pins it; until now it was vendor-neutral).
   - **DEC-003 (invalidation strategy)** → move from Deferred to **Approved** for **24h age-based TTL** (with explicit-key invalidation per FR-003), rationale citing EXP-003.
3. **State the go/no-go** clearly: **GO** to productionize, gated decisions resolved.
4. **Because DEC-001 = go, produce the Phase-2 productionization plan** — the previously deferred productionization architecture and a bounded WBS — and define the **first bounded PH-2 task** with its own PASS/FAIL and a stop gate. (Generating this is now legitimate because the gate is passed; it would have been premature before.)

If, in any future run, the evidence had gone the other way (a hypothesis refuted, DEC-001 trigger not met), the task instead is: mark the relevant hypothesis **refuted** with evidence, move **DEC-001 to Rejected (no-go)**, produce the **documented recommendation explaining why semantic caching does not pay off on workload Z**, and **stop** — no PH-2 plan.

## PASS/FAIL for this synthesis

- **PASS** if: each hypothesis (HYP-001/002/003) is marked **confirmed or refuted with cited evidence**; each Deferred decision (DEC-001/002/003) is **resolved to Approved or Rejected with rationale** (none left Deferred, none rendered as Approved without its trigger met); the **go/no-go is stated explicitly**; and — if go — a **bounded PH-2 plan with a first task and a gate** is produced.
- **FAIL** if: any hypothesis is left unresolved or asserted without evidence; any decision is left Deferred or flipped to Approved without its trigger satisfied; the go/no-go is ambiguous; or (on a go) productionization work is started before the PH-2 plan is reviewed.

## Invariants still in force for any productionization

Any PH-2 work must continue to honor **INV-001** (never return a below-bar cached answer — the safety gate stays mandatory and non-bypassable per ADR-0001), **INV-002** (never serve cached answers across user/context boundaries), and **INV-003** (every served hit logged with similarity score and source key). The chosen lightweight approach and 24h TTL plug into the **same ADR-0001 contract** — the seam does not change.

## Gate

**Approval is required before any PH-2 build begins.** Produce the synthesis, the resolved decisions, the go/no-go, and (on a go) the PH-2 plan with its first bounded task — then **stop and wait for my approval**. Do not write production code in this step.
