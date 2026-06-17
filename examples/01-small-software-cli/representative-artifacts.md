# Representative artifacts — repostat

A handful of real, filled artifacts pulled from the generated package — enough to show the shape and the
cross-references, not the whole package. IDs are consistent across this file: ADR-0001 governs FR-005 and
INV-002; the acceptance criteria name the FR/NFR they verify.

## Functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| FR-001 | The system shall scan a local git repository, reading commit history from `.git` without requiring network access. | input.md ("point it at a local git repository"); CON-001 (offline) | MVP | Proposed |
| FR-002 | The system shall report commits per author, including absolute counts and percentage of total. | input.md ("commits per author") | MVP | Proposed |
| FR-003 | The system shall report code churn (lines added/removed) over time and per author. | input.md ("code churn") | Full | Proposed |
| FR-004 | The system shall report file hotspots, ranking files by change frequency, and activity over time bucketed by week and month. | input.md ("file hotspots", "activity over time") | Full | Proposed |
| FR-005 | The system shall render every report to stdout as a table and export it to JSON (MVP), and to CSV and Markdown (Full), from a single report model. | input.md ("export … JSON for sure … CSV and Markdown"); ASM-001 | MVP (JSON+stdout) / Full (CSV+MD) | Proposed |

## Non-functional requirements (excerpt)

| ID | Statement | Source | Priority | Status |
|---|---|---|---|---|
| NFR-001 | The system shall be deterministic: identical inputs (same repo state, same options) shall produce byte-identical reports across runs and platforms (stable ordering, fixed numeric formatting). | INV-002; input.md (scriptable/exportable output) | MVP | Proposed |
| NFR-002 | The system shall produce the default report for a repository of up to ~50,000 commits in ≤10 s on commodity hardware; larger repositories shall still complete. | ASM-003; input.md ("reasonably fast", "deep history") | MVP | Proposed |
| NFR-003 | The system shall operate strictly read-only against the target repository, making no writes, no index changes, and no ref updates. | INV-001; CON-002; input.md ("must not change anything") | MVP | Proposed |

## Invariants

| ID | Invariant | Rationale |
|---|---|---|
| INV-001 | The tool never mutates the target repository — no writes to the working tree, index, refs, config, or hooks; analysis is read-only. | The user must be able to run it on a repo with uncommitted work and trust nothing is touched (input.md hard requirement). Enforced by NFR-003 and audited each phase. |
| INV-002 | For identical inputs (repo state + options), output is byte-identical: deterministic ordering of authors/files, stable tie-breaks, and fixed numeric/locale formatting. | Output is meant to be diffed, scripted, and pasted into reports; nondeterminism would break those uses and make tests flaky. Realized by NFR-001 and ADR-0001. |

## One ADR

### ADR-0001 — Export rendering via a format-agnostic report model

**Status:** Approved

**Context.** repostat must emit the same statistics to several surfaces: a stdout table now, plus JSON
(MVP) and CSV and Markdown (Full) per FR-005 and ASM-001. If each output were computed independently,
the formats would drift, adding a fourth format later would touch every code path, and guaranteeing
byte-identical output (INV-002) would be hard because formatting logic would be scattered.

**Decision.** Compute statistics once into a single in-memory **report model** — a plain, fully-resolved
data structure (authors, churn series, hotspots, time buckets, with all ordering and rounding already
fixed). Rendering is done by **pluggable formatters** that consume that model and emit text:
`stdout-table`, `json`, `csv`, `markdown`. Formatters are pure functions of the model and never recompute
or re-sort. Adding a new export format is **additive**: write one formatter; nothing else changes. The
model is the single place where deterministic ordering and numeric formatting are enforced (satisfies
INV-002), and the same model backs every format (satisfies FR-005).

**Alternatives considered (rejected).**
- *Per-format computation* — each export builds its own numbers/strings. Rejected: formats drift, INV-002
  is hard to guarantee, and every new format is a cross-cutting change.
- *Template-only rendering with no explicit model* — pipe raw git output through per-format templates.
  Rejected: ordering/rounding would live in templates, making determinism and testing fragile.
- *Full plugin system with discovery/registration* — over-engineered for a solo tool with four built-in
  formats (contradicts the brief's "no plugin system"); deferred unless third-party formats are ever wanted.

**Consequences.**
- (+) New formats are one small additive change; the report model is the single source of truth.
- (+) Determinism (INV-002 / NFR-001) is enforced in one place and is straightforward to test with golden
  files.
- (+) Formatters are independently testable against a fixed model fixture.
- (−) A small upfront cost to define the model shape before any export exists; the MVP carries JSON +
  stdout only (ASM-001), so the model must be designed slightly ahead of its first second consumer.
- Links: realizes **FR-005**; enforces **INV-002**; verified by **AC-003** and the determinism tests in
  `validation/test-strategy.md`.

## Risk register (excerpt)

| ID | Risk | Impact | Likelihood | Mitigation | MVP/Full |
|---|---|---|---|---|---|
| RISK-001 | Very large repositories exceed the NFR-002 time budget (history far beyond ~50k commits, or pathological churn). | Med (slow runs, poor first impression) | Med | Stream commit history instead of loading it all; compute in a single pass; expose `--since`/branch scoping (Full) to bound work; document that beyond-target repos complete but may be slower. Track against ASM-003. | MVP (measure) / Full (scoping) |
| RISK-002 | One contributor appears as multiple authors because they commit under several emails (the user's two-machine case). | Med (misleading author stats) | High (common in solo + OSS repos) | MVP keys authors by raw committer email and documents the limitation; provide an optional `--mailmap`/identity-merge in a later phase (deferred decision DEC- in readiness.md). Surface the limitation in README so numbers aren't misread. | MVP (document) / Full (merge) |

## Roadmap (phases)

### PH-1 — MVP: usable daily
- **Goal:** a tool the user can run every day — scan a repo and see who committed how much, with
  scriptable JSON output.
- **Key deliverables:** repository scanner reading `.git` offline (FR-001); commits-per-author report
  (FR-002); the in-memory report model + `stdout-table` and `json` formatters (FR-005 MVP scope per
  ADR-0001, ASM-001); determinism and read-only behavior wired in (INV-001, INV-002, NFR-001, NFR-003);
  golden-output and read-only tests (`validation/test-strategy.md`).
- **Exit criteria:** AC-001, AC-002, AC-003 pass; the read-only invariant audit shows zero writes to a
  fixture repo; default report on the ~50k-commit fixture meets NFR-002; reaches milestone MS-001.

### PH-2 — Full: richer reports and exports
- **Goal:** the full reporting surface and all three export formats.
- **Key deliverables:** churn over time and per author (FR-003); file hotspots + activity-over-time
  buckets (FR-004); `csv` and `markdown` formatters added to the existing report model (FR-005 Full scope,
  additive per ADR-0001); date-range/branch filters (the brief's "nice to have"); RISK-001 scoping options.
- **Exit criteria:** acceptance criteria for FR-003/FR-004 and the CSV/Markdown exports pass; INV-001 and
  INV-002 still hold across all four formatters; reaches milestone MS-002.

## Acceptance criteria (excerpt)

| ID | Given/When/Then | Verifies |
|---|---|---|
| AC-001 | **Given** a local git repository with known history, **when** repostat is run with no network available, **then** it completes and prints an author table to stdout without any network access or error. | FR-001, CON-001 (offline) |
| AC-002 | **Given** a fixture repo whose commits-per-author counts are known, **when** the author report is generated, **then** each author's commit count and percentage match the expected values exactly. | FR-002 |
| AC-003 | **Given** the same fixture repo and identical options, **when** the JSON export is produced twice (and on a second platform), **then** the two outputs are byte-identical, and **when** any non-stdout format is added it renders from the same report model. | FR-005, NFR-001, INV-002 |
| AC-004 | **Given** a fixture repo with uncommitted changes and a recorded checksum of its `.git` and working tree, **when** repostat runs to completion, **then** the checksum is unchanged (no writes, no index/ref changes). | NFR-003, INV-001 |
