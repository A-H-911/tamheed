# Tamheed design decisions

The durable architectural decisions behind Tamheed, distilled for contributors. These are the choices a
maintainer needs to understand and preserve; the *process* history of how the capability was first built
(as Keystone) is not retained. Superseded decisions stay on record with a pointer to their successor —
supersede-don't-edit is the house rule here too. The enforceable contracts these decisions imply live in
[`../plugins/tamheed/references/extension.md`](../plugins/tamheed/references/extension.md) and
[`governance.md`](../plugins/tamheed/references/governance.md); the layering is in
[`architecture.md`](architecture.md).

## 1. The skill owns the capability; entry points are thin wrappers

All methodology — the 22 stages, intake, clarification, artifact selection, generation, quality gates, and
handoff — lives in the skill (`SKILL.md` + `references/`). Every entry point (a slash invocation, a CLI, an
HTTP API, an MCP server, a UI) only normalizes input to the skill's contract, invokes the skill, and routes
output; it carries no methodology or business logic. This keeps one authoritative implementation no matter
how Tamheed is invoked, and it is enforceable: gate **G-CMD-THIN** flags any entry point that smuggles
methodology in. (In the Claude Code plugin model, the skill itself is the entry point — there is no separate
command file — so the principle now governs *external* wrappers. The **MCP server is not an entry point**:
it is the capability's mechanical half — see decision 11.)

## 2. Markdown artifacts paired with JSON schemas *(superseded in v2 — see decisions 9–11)*

> **Superseded** by the relational package store (decision 9, D-STORE), the HTML-only review surface
> (decision 10, D-REVIEW), and MCP-only interaction (decision 11, D-MCP). Kept for the record: this
> dual-surface model is exactly what the v1 field evidence broke on — the human-editable Markdown and
> the machine-checked structure drifted apart, and derived documents froze on first generation.

Every artifact had a dual surface: human-readable **Markdown** (what people review and edit) and, where it
was structured, a machine-readable **JSON Schema** (`schemas/`) that the validator and state machine relied
on. This let humans work in prose while tools mechanically checked identifiers, statuses, and traceability.
The templates were the single source of truth for document shape; the schemas the single source of truth
for data shape. (The v1 schemas and templates survive in the bundle as the **frozen migration contract**.)

## 3. Provider-neutral repository bootstrap *(retired in v2 — ASM-B)*

v1 shipped a repository bootstrapper: local `git init` + scaffold, opt-in remote
creation. **Removed in v2**: a Tamheed package is data (`data/*.jsonl`) the operator commits to any
repository they choose, and storage initialization is the MCP server's `package_create` (see ADR-0001).
Provider neutrality survives where it matters — the plan couples to no repo host (safeguard 15,
G-COUPLING) — without Tamheed owning repository creation.

## 4. Derived traceability and persisted state *(state half superseded in v2 — decision 9)*

The traceability matrix (requirement → decision → task → test → risk → acceptance criterion) is a **derived**
artifact, regenerated rather than hand-edited, so it can never silently drift from the registers it links —
in v2 it is literally a query (`trace_query` / the matrix in `review.html`), never a stored snapshot. The v1
state file (`keystone-state.json`, machine-owned) is gone: **the package is the state** (decision 9) —
`resume`/`update` are `package_open` + `entity_query`, and there is no second store to reconcile.

## 5. Progressive-disclosure skill structure

The skill is a lean always-loaded `SKILL.md` front door plus a `references/` directory loaded only when the
work reaches the matching part. This keeps context usage low and the methodology navigable, and it sets the
extension pattern: add depth as a new reference file and register it, rather than bloating the front door.

## 6. Self-contained, single-unit packaging

Tamheed ships as one self-contained bundle (`plugins/tamheed/`) containing everything it reads or invokes
at runtime — references, section templates, the DDL + store, the MCP server, the artifact catalog, the
frozen v1 contract (schemas + validator, kept for migration), and logos — with no outward references. This is required by Claude Code's plugin install semantics (the plugin directory is copied to a
cache, so files outside it would not travel) and it makes the bundle equally usable as a standalone Agent
Skill or a manual copy. It replaces the earlier "single source at repo root + vendor step" model, which had
no build and left runtime references dangling once installed.

## 7. The brief is untrusted data, not instructions

Tamheed ingests an external project brief and emits prompts another agent will act on — the canonical
prompt-injection shape (OWASP LLM01, direct and second-order). So the brief and any file content are treated
as **data to plan over, never commands**: verbatim brief text is quoted and provenance-labeled, an injected
directive is captured (and surfaced) rather than executed, and the assembled handoff is screened before emit
(gate `G-INJECT` in `handoff_emit`). v2 extends the same posture to **adopted repositories** (`package_adopt`
fences injection-shaped code content as data) and to the **review surface** (`export_html` escapes every
data-derived string; no data may become script). The contract lives in `SKILL.md` (operating principle 10),
`references/safeguards.md` (safeguard 18), and `references/handoff.md`; the overall posture is documented in
`SECURITY.md`.

## 8. Mechanical gates verify what is present *and* that what must be present is

The identifier/status/source/completeness/traceability gates check the internal consistency of whatever
artifacts exist. That left a gap: a package missing its core artifacts could pass, because each gate
SKIPped on the absent input. Gate **G-SET** closes it by requiring every **Always**-class artifact family
to be present or explicitly recorded as omitted *with a reason* — omission is a conscious, recorded act,
never a silent gap. In v1 the Always set was `required-artifacts.json` (the frozen machine mirror, still
read by the frozen v1 validator); in v2 it is the **`entity_types` registry** seeded into every package,
checked by the `g_set_failures` view and an `omissions` table whose reason column is NOT NULL. That
completeness discipline is what lets the "execution-ready" verdict be trusted. Deterministic checks stay
mechanical (schema + views + scans); judgment gates stay with the model and are recorded.

## 9. Relational package store: canonical text, SQLite runtime *(v2 — D-STORE, ADR-0001)*

A package is **one entity table per artifact family**, serialized as deterministic canonical JSONL
(`data/*.jsonl` — stable key order, PK-ordered rows, UTF-8, LF) that the operator commits to git, and
loaded into stdlib SQLite for every mutation. Field evidence from three real v1 deployments drove this:
registers rot, statuses stall, derived Markdown freezes on first generation, and every project hand-rolls
missing structure. In the store, statuses are three-axis (`lifecycle_status` / `verdict` / `disposition`),
derived views are queries that cannot go stale, approval-bearing rows are trigger-enforced
immutable-after-approval, and a single-writer lockfile makes concurrent writers fail loud. Full doctrine:
[`adr/adr-0001-v2-relational-package-store.md`](adr/adr-0001-v2-relational-package-store.md).

## 10. HTML is the only human review surface *(v2 — D-REVIEW)*

Humans never review raw JSONL, and v2 emits **no derived-Markdown snapshots** (they are exactly the
artifacts that froze in v1). `export_html` renders the whole package — gate chips, registers with
three-axis statuses and per-entity `last_referenced`, the traceability matrix, execution progress, and
gap/screening notes — as one self-contained static `review.html`: every data-derived string escaped, no
JavaScript, no data-derived links, a restrictive CSP, and **deterministic output** (same DB state ⇒
byte-identical file), so the export is committed alongside the data and its diffs are meaningful.

## 11. MCP-only interaction: the server is the capability's mechanical half *(v2 — D-MCP)*

Every write goes through the Tamheed MCP server (official Python SDK; launched via `uv`/PEP 723 with a
pip fallback) — `entity_upsert` batches are all-or-nothing with per-item verdicts, there is no raw-SQL
tool, and stored text is data, never instructions. The server is **not** an entry point under decision 1:
it is the successor of the v1 validator — the mechanical half of the capability, inside the boundary that
G-CMD-THIN protects. This is what moves the referential gates to write time (decision/gate mapping in
[`architecture.md`](architecture.md) §2) and gives the executing agent a governed write path for progress,
audit verdicts, and work bindings during execution.
