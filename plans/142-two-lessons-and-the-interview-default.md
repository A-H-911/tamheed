# Plan 142: two absorbed lessons and the interview's default

> Maintainer-executed, 2026-09-27. Batch map: [141-145-batch-findings-35.md](141-145-batch-findings-35.md).
> Field source: ACMP `findings_35.md` (A3 item 2, B1, B4), `LL-112`, `DEC-233`; rulings R25, R26.

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

1. A trace line equal to a replay was read as the operator session's line. Another producer in the
   same folder wrote it (`LL-112`, Proposed in the field; its generic core absorbed on the
   maintainer's word, R26).
2. A blob compare of the installed tree read every file different. It had measured line endings.
3. The operator sent a bare option set back twice asking for a recommendation, then made
   recommendations standing (`DEC-233`). The rule it replaced had lived in memory and was cited to a
   decision whose text never stated it.

## What changed

| Skill | Place | Sentence |
|---|---|---|
| `measurement-evidence` | §3, last bullet | Every item differing is as suspect as none. The compare measured the transport. Normalise, prove a one-byte change is caught, then read. |
| `measurement-evidence` | §4, last bullet | A match on value is necessary and never sufficient when another producer can write the same value. Take identity from an instrument that carries one. "No other process ran" is a control only over processes you start. |
| `operator-interview` | step 3 | One option is marked as the agent's recommendation with its deciding reason, unless the operator turned recommendations off. A recommendation is never a verdict or an approval. |
| `operator-interview` | step 6, new bullet | A standing instruction about how to ask is a decision row in the operator's words, followed until replaced. It is not a banked answer. |
| `operator-interview` | "does NOT cover" | The bullet that left recommendations to each round is removed: the skill now covers it. |

Each sentence is written stack-neutral and anonymised: no field identifier, no product name.

## Not absorbed, on purpose

Citation chains (the "id resolves, sentence false" paragraph of `reading-the-record` covers the
error itself) and working-directory state (general shell hygiene). Both were offered in the
interview and not selected. An "advisor check" clause is harness-specific and was not ruled.

## Validation

`python check.py lint` green after the edits: 25 skills well-formed and stack-neutral. No
frontmatter changed, so the menu and model counts hold.
