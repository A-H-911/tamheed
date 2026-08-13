<!-- ================= TAMHEED EVIDENCE ARCHIVE — C35 =================
Archived verbatim from c:\Users\ahammo\Repos\acmp\findings_14.md on 2026-08-14
(plan 029/B25). The v3.1.0 acceptance run — verdict: "the MINOR delivers what
findings_13 asked for, and one thing it claims does not happen." All §2/§4/§5
recommendations verified working (per-file leftover verdicts matched the
operator's hand triage exactly; the restated scan even caught prm-next.md,
unpredicted). Two real defects: N1 — the CLAUDE.md note did NOT self-update
while its own warning text promised it does (the operator quoted the code);
N2 — force was all-or-nothing, so applying the tool-owned note clobbered
operator-customised prompts. N3 (minor) — pass + discriminating:false read as
green. Also recorded: the OQ-flag expectation in OUR acceptance prompt was
wrong (5/76 populated — the tool discriminated correctly); the operator's
first hover probe nearly wrote a working feature up as broken (wrong element,
wrong property — reading the CSS caught it); the ⚠-first isolated-requirement
ordering was field-unverifiable (operator sequencing) but IS mechanically
verified in-repo (test_flow_lead_flags_isolated_requirements). Carried
forward: §2 prompt curation + README verdict, the §6 clean unprompted drift
session (now unblocked by N1's fix). Plan 029 (v3.2.0): note span becomes
tool-owned (rebuilt every emit + warning), stock-divergence guidance names the
delete+re-emit per-file path, vacuous non-discriminating passes read
indeterminate. Evidence is superseded, never edited.
================================================================== -->
# findings_14 â€” Tamheed v3.1.0 acceptance pass

**Verdict: the MINOR delivers what findings_13 asked for, and one thing it claims does not happen.**
Every Â§2/Â§4/Â§5 recommendation from findings_13 is implemented and verified. Two negatives below, plus
an honest list of what I did not complete.

`migrations_head` unchanged at `004`, `schema_version` 4 â€” "no schema migration" confirmed.

---

## âœ… What was verified working

**Per-file leftover verdicts match my hand triage exactly.** I had no leftovers left, so I recreated
one of each to test it:

```
handoff/prm-001-follow-up.md: copy of prompts/prm-001-follow-up.md â€” safe to delete
handoff/prm-unique-thing.md:  NOT a copy of any package prompt â€” MOVE it into <package>/prompts/
                              (deleting would destroy live content)
```

That is precisely the distinction I had to make by hand in findings_13 Â§2 â€” including the parenthetical
reasoning I used to *override* v3.0.0's blanket "delete" advice for `prm-next.md`. The copy was detected
even though my recreated copy carried the provenance header, so it is a real content compare.

**`converted_prompts`** lists all three with per-kind hints naming stock counterparts
(prm-001â†’orient-resume/replan-deferred/slice-review, prm-002â†’package-onboarding/slice-kickoff,
prm-003â†’integrity-check/slice-review), each ending "this hint clears itself".

**`restated_content`** flagged prm-002 line 24 (`labeled-snapshot`) â€” and *also* `prm-next.md` line 16
(`unlabeled`), which the brief did not predict. That second hit exists because I moved `prm-next.md`
into the package last pass, so it is now in scope. Good catch by the tool.

**Readiness discrimination â€” exactly the findings_13 Â§4 ask.**

- `risks-discharged`: `discriminating: false` + *"0 of 23 risks rows have discharged_by set; this rule
  cannot discriminate (populate discharged_by to make it meaningful)"*. It names the column to populate.
- slice `defects-closed`: `discriminating: false` + *"0 of 63 defects rows have found_in set"* â€” the
  silent under-report from findings_13 is now visible.
- `open-questions-resolved` correctly does **not** carry the flag: 5 of 76 OQs do have `resolved_by`,
  so it genuinely discriminates. **The brief expected the flag here; the tool is right and the
  expectation was wrong.**

**Hover-isolate works.** Hovering one node dimmed **all 1,052** edges (`stroke-opacity` â†’ `.04`) and
revealed **6** hidden `.hl` copies â€” that node's incident edges. `:has()` supported.
âš  My first probe reported *0 dimmed* â€” it targeted the wrong element (`#flow svg a`) and the wrong
property (`opacity`, not `stroke-opacity`). A working feature nearly written up as broken; reading the
CSS rule rather than trusting the probe is what caught it.

**Isolated fold is now a per-family breakdown** â€” `constraint 15, assumption 16, â€¦ audit-verdict 160,
progress-entry 311, document-section 633 (1694 rows)`. findings_13 Â§5's ask, implemented.

**`requirements_unwired`** (gate) and **`requirements-wired`** (readiness) both listed exactly
FR-156â€“159, and both carry my root cause in their note: *"work_bind stamps commits, it does not wire
traceability"*. After wiring: both empty. **DEF-063 closed** (details in the row).

---

## âš  Negative 1 â€” the note does **not** self-update, and the code says it does

`handoff_emit` returned `written: []`, `diverged: ["CLAUDE.md (tamheed:note)"]`. The v2 note in
CLAUDE.md was **not** updated to v3.1.0 content. The code:

```python
elif note_m.group(0) != note_block.rstrip("\n"):
    if force:  content = content.replace(...)   # updates
    else:      diverged.append("CLAUDE.md (tamheed:note)")
```

â€¦while the adjacent warning string promises the v2 note *"is marker-managed and **self-updates**
thereafter"*. It does not, without `force`.

This matters beyond documentation: **step 6 of this brief is premised on the note having self-updated.**
It hadn't, so the drift test could not run against v3.1.0 note content.

## âš  Negative 2 â€” `force` is all-or-nothing, so the fix for Negative 1 is destructive

`handoff_emit(force=True)` passes `force` into `_emit_prompt_library` â†’ `_managed_emit` for **every**
prompt. Applying the tool-owned note therefore also overwrites the five diverged prompts
(`drift-register`, `integrity-check`, `orient-resume`, `progress-sync`, `slice-review`) â€” three of which
carried project customisation since before v3.0.0.

There is no way to update the block the tool owns without clobbering files the operator owns. The two
kinds of divergence are also indistinguishable in the output: `integrity-check` (operator-customised)
and `drift-register` (template moved on in 3.1.0) are reported identically.

**Suggestion:** either scope `force` (`force="note"` / `force="prompts"`), or make the marker-delimited
note self-update as documented and reserve `force` for operator-owned files.

## âš  Negative 3 (minor) â€” `pass` + `discriminating: false` still reads as green

Slice `defects-closed` reports `status: "pass"` alongside `discriminating: false`. "Verified clean" and
"cannot measure" are different claims, and a reader skimming statuses sees green. A distinct status
(`indeterminate`) would carry the meaning without relying on the reader noticing the flag. The blocking
case (`risks-discharged`) is fine â€” it fails loudly.

---

## What I did NOT complete (and why)

- **Â§2 prompt curation â€” not done.** The hints are read and judged (above), but the three converted
  files are un-curated and their provenance headers remain. This is a substantial authoring task and I
  ran out of context budget before it. `prompts/README.md` was emitted but I have not read it, so I owe
  no verdict on it.
- **Â§4 "âš  4 requirement(s) first" ordering â€” unverifiable, my error.** I ran Â§5 (wiring) before Â§4
  (viewer), which removed the only isolated requirements. The per-family breakdown is confirmed; the
  âš -first ordering for requirements is not, because I destroyed its precondition. Sequencing mistake,
  not a tool defect.
- **Â§6 drift verdict â€” still not delivered.** Blocked twice over: it needs a genuinely fresh session
  (I cannot start one from inside this one), *and* the note it would test was never applied
  (Negative 1). Running it here would have measured v3.0.0 note content in a session already saturated
  with recording instructions â€” the same uncontrolled experiment I declined in findings_13 Â§6.

## Summary

| Step | Verdict |
|---|---|
| 1 handoff_emit surfaces | âœ… all three; per-file verdicts match hand triage exactly |
| 2 Curation + README | âŒ not done â€” out of context budget |
| 3 Readiness discrimination | âœ… notes name the column to populate Â· âš  `pass` + non-discriminating |
| 4 Viewer | âœ… hover-isolate + per-family fold Â· âš  âš -first ordering unverifiable (my sequencing) |
| 5 Wire FR-156..159 | âœ… list â†’ empty; DEF-063 closed, both halves |
| 6 Drift verdict | âŒ blocked â€” needs a fresh session AND the note was never applied |
| 7 This file | filed (three negatives) |
