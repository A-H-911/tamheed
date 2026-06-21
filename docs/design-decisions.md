# Keystone design decisions

The durable architectural decisions behind Keystone, distilled for contributors. These are the choices a
maintainer needs to understand and preserve; the *process* history of how Keystone was first built is not
retained. The enforceable contracts these decisions imply live in
[`../plugins/keystone/references/extension.md`](../plugins/keystone/references/extension.md) and
[`governance.md`](../plugins/keystone/references/governance.md); the layering is in
[`architecture.md`](architecture.md).

## 1. The skill owns the capability; entry points are thin wrappers

All methodology — the 22 stages, intake, clarification, artifact selection, generation, quality gates, and
handoff — lives in the skill (`SKILL.md` + `references/`). Every entry point (a slash invocation, a CLI, an
HTTP API, an MCP server, a UI) only normalizes input to the skill's contract, invokes the skill, and routes
output; it carries no methodology or business logic. This keeps one authoritative implementation no matter
how Keystone is invoked, and it is enforceable: gate **G-CMD-THIN** flags any entry point that smuggles
methodology in. (In the Claude Code plugin model, the skill itself is the entry point — there is no separate
command file — so the principle now governs *external* wrappers.)

## 2. Markdown artifacts paired with JSON schemas

Every artifact has a dual surface: human-readable **Markdown** (what people review and edit) and, where it is
structured, a machine-readable **JSON Schema** (`schemas/`) that the validator and state machine rely on.
This lets humans work in prose while tools mechanically check identifiers, statuses, and traceability. The
templates (`templates/`) are the single source of truth for document shape; the schemas are the single
source of truth for data shape.

## 3. Provider-neutral repository bootstrap

The repo-init step (`scripts/init_skill_repo.py`) always works locally — `git init`, scaffold, initial commit
— with no network and no third-party tools. Remote creation/push (GitHub via `gh`) is an explicit, opt-in,
swappable step (`--create-remote`). The bootstrap defaults to safe behavior: dry-run-capable, idempotent, and
never overwriting without `--force`. Keystone is not tied to any one repo host.

## 4. Derived traceability and persisted state

The traceability matrix (requirement → decision → task → test → risk → acceptance criterion) is a **derived**
artifact, regenerated rather than hand-edited, so it can never silently drift from the registers it links.
Normalized run state is persisted to `keystone-state.json` (machine-owned), so `resume`/`update` reload prior
work instead of re-asking, and updating a decision re-derives the artifacts that depend on it.

## 5. Progressive-disclosure skill structure

The skill is a lean always-loaded `SKILL.md` front door plus a `references/` directory loaded only when the
work reaches the matching part. This keeps context usage low and the methodology navigable, and it sets the
extension pattern: add depth as a new reference file and register it, rather than bloating the front door.

## 6. Self-contained, single-unit packaging

Keystone ships as one self-contained bundle (`plugins/keystone/`) containing everything it reads or invokes
at runtime — references, templates, schemas, scripts, the artifact catalog, and logos — with no outward
references. This is required by Claude Code's plugin install semantics (the plugin directory is copied to a
cache, so files outside it would not travel) and it makes the bundle equally usable as a standalone Agent
Skill or a manual copy. It replaces the earlier "single source at repo root + vendor step" model, which had
no build and left runtime references dangling once installed.

## 7. The brief is untrusted data, not instructions

Keystone ingests an external project brief and emits prompts another agent will act on — the canonical
prompt-injection shape (OWASP LLM01, direct and second-order). So the brief and any file content are treated
as **data to plan over, never commands**: verbatim brief text is quoted and provenance-labeled, an injected
directive is captured (and surfaced) rather than executed, and the assembled handoff is screened before emit
(gate `G-INJECT`). The contract lives in `SKILL.md` (operating principle 10), `references/safeguards.md`
(safeguard 18), and `references/handoff.md`; the overall posture is documented in `SECURITY.md`.

## 8. Mechanical gates verify what is present *and* that what must be present is

The validator's identifier/status/source/completeness/traceability gates check the internal consistency of
whatever artifacts exist. That left a gap: a package missing its core artifacts could pass, because each
gate SKIPped on the absent input. Gate **G-SET** closes it by reading the **Always** set
(`plugins/keystone/references/required-artifacts.json`, the machine mirror of `artifact-rules.md`) and
requiring each always-on artifact to be present on disk or explicitly recorded in the manifest's
`omitted_artifacts[]` with a reason. Omission becomes a conscious, recorded act rather than a silent gap —
which is what lets the "execution-ready" verdict be trusted. Deterministic checks stay in the script;
judgment gates stay with the model (decision 2 is unchanged).
