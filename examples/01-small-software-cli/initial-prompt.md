# Execution-agent initial prompt — repostat

This repo contains the **APPROVED** plan for **repostat**, a small, offline command-line tool that scans a
local git repository and reports contribution and activity statistics (commits per author, churn, file
hotspots, activity over time) to stdout and as exportable JSON/CSV/Markdown. You are starting
implementation. The complete plan — requirements, invariants, decisions, roadmap, and acceptance criteria
— lives in this package; the planning decisions in it are **final** and are not yours to relitigate. If you
believe a decision is wrong, surface it; do not silently deviate.

**Step 1 — Orientation (no code).** Read these documents (relative paths):
- `00-charter.md`
- `requirements/functional.md`
- `requirements/invariant-register.md`
- `planning/roadmap.md`

Then give me:
(a) a **≤1-page summary** of what you'll build and the invariants you must respect — explicitly
**INV-001** (never mutate the target repository; read-only) and **INV-002** (identical inputs produce
byte-identical reports; deterministic ordering and formatting);
(b) your **execution plan for Phase PH-1** (MVP: repository scanner + commits-per-author + JSON export +
stdout table) with the proposed file layout and a PASS/FAIL check for each task.
**STOP and wait for my approval** before writing any code.

**Step 2 — Repository scanner + commits-per-author (after approval).** Implement the offline `.git`
scanner and the commits-per-author report covering **FR-001** and **FR-002**, rendered to the stdout table
via the report model from **ADR-0001**. Provide, for this task:
- PASS: runs offline against a fixture repo and prints an author table; each author's count and percentage
  match the fixture's known values (AC-002); a checksum of the fixture's `.git` and working tree is
  unchanged after the run (AC-004 / INV-001).
- FAIL: any network access attempted, any miscount, or any write to the target repo.
**Pause for review** before moving on to the JSON formatter or any PH-1 remainder.

**Rules:** respect the invariants (INV-001, INV-002) from the first commit; pin all dependency and runtime
versions; record any deviation from the plan as a new ADR (do not change ADR-0001, which is immutable after
approval); do **not** expand scope beyond Phase PH-1 — churn, hotspots, activity-over-time, and CSV/Markdown
export are PH-2 and out of bounds for now.

**Prerequisites:** `git` available and readable on `PATH` (DEP-001); the project's pinned runtime installed
per **ASM-002** / DEP-002 (run `scripts/init_repo.sh` to bootstrap the repo and lock versions). No network
access is required or permitted at runtime (CON-001).
