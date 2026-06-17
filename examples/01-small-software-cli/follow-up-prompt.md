# Follow-up prompt — Phase PH-2 gate (repostat)

**Resume context.** Phase **PH-1** is complete and approved. Its exit criteria were met: AC-001, AC-002,
and AC-003 pass; the read-only invariant audit showed zero writes to the fixture repo (AC-004 / INV-001);
the default report on the ~50k-commit fixture met the NFR-002 time budget; milestone MS-001 (MVP usable —
scan + commits-per-author + JSON export + stdout table) is reached. The in-memory report model and the
`stdout-table` and `json` formatters from ADR-0001 are in place.

**Phase PH-2 goal.** Extend repostat to the full reporting surface and all three export formats, building
**additively** on the existing report model (do not re-architect; ADR-0001 stands).

**Bounded tasks (each with PASS/FAIL — pause for review after each):**

1. **Churn over time and per author (FR-003).** Extend the report model with churn series (lines
   added/removed) by author and by time bucket.
   - PASS: churn totals on the fixture repo match known added/removed line counts; output is deterministic
     across two runs (INV-002).
   - FAIL: miscount, nondeterministic ordering, or any recompute that bypasses the report model.

2. **File hotspots + activity over time (FR-004).** Add file-change-frequency ranking and commit counts
   bucketed by week and month to the report model.
   - PASS: the top-N hotspots and the per-week/per-month buckets match the fixture's expected values;
     tie-breaks are stable (INV-002).
   - FAIL: unstable ranking on ties, off-by-one bucket boundaries, or wrong totals.

3. **CSV and Markdown export (FR-005, Full scope).** Add `csv` and `markdown` formatters that consume the
   same report model — no new computation in the formatters (per ADR-0001).
   - PASS: CSV and Markdown render the identical numbers the JSON export already produces for the same repo
     and options; re-running yields byte-identical output (INV-002); a fresh format required only a new
     formatter, no changes elsewhere.
   - FAIL: numbers diverge between formats, formatter recomputes/re-sorts, or output is nondeterministic.

**Invariants still in force (all tasks):** **INV-001** — read-only against the target repo, zero writes;
**INV-002** — byte-identical output for identical inputs. Re-run the read-only audit after PH-2 changes.

**PH-2 exit gate.** PH-2 is done when: the acceptance criteria for FR-003 and FR-004 and for the
CSV/Markdown exports all pass; all four formatters (stdout, json, csv, markdown) render from the one report
model and agree numerically; INV-001 and INV-002 still hold across every formatter; the traceability matrix
regenerates clean; milestone **MS-002** (full export set) is reached. Then STOP and request final review /
readiness recheck (`handoff/review-prompts.md`).
