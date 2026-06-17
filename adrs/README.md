# Architecture Decision Records (Keystone's own design)

These ADRs record the architecturally significant decisions behind **Keystone
itself** — the skill, its entry point, its artifact formats, its bootstrap, its
state model, and its structure. They are distinct from the ADRs that a
Keystone *run* produces for a target project (those live in a generated
package's own `adrs/`).

Format: each ADR follows a standard shape — Status, Date, Context, Decision,
Consequences, and Alternatives considered and rejected. IDs are `ADR-NNNN` per
`../skill/references/governance.md`. ADRs are immutable after approval: to
change a decision, add a new ADR that supersedes the old one rather than
editing it in place.

## Index

| ID | Title | Status | Summary |
|---|---|---|---|
| [ADR-0001](adr-0001-name-keystone.md) | Name the capability "Keystone" | Accepted | Chose "Keystone" over Project Forge / Groundwork / Charter / Blueprint / Launchpad / Scaffold; records the OpenStack-Keystone collision and the mitigation (consistent "Keystone (project inception)" framing + owner-scoped/fallback repo slug). |
| [ADR-0002](adr-0002-skill-owns-capability-thin-command.md) | Skill owns the capability; entry points are thin wrappers | Accepted | The skill is authoritative for all methodology; the slash command only normalizes input, selects a mode, invokes the skill, and routes output. Rejected: putting logic in the command (safeguard 12, gate G-CMD-THIN). |
| [ADR-0003](adr-0003-markdown-artifacts-with-json-schemas.md) | Human-readable Markdown artifacts + machine-readable JSON | Accepted | Markdown is the human surface; JSON (with schemas) is the machine surface; derived artifacts are regenerated. Rejected: single-format (Markdown-only or JSON-only) approaches. |
| [ADR-0004](adr-0004-provider-neutral-repo-bootstrap.md) | Provider-neutral repository bootstrap | Accepted | Local git always; remote (GitHub via `gh`) is an optional, swappable, approval-gated step. Rejected: hard GitHub coupling (safeguard 14). |
| [ADR-0005](adr-0005-derived-traceability-and-persisted-state.md) | Derived traceability; persisted state | Accepted | The traceability matrix is derived from the registers and re-derived each cycle; normalized state is persisted for resume/update. Rejected: hand-maintained matrices and no-state reconstruction. |
| [ADR-0006](adr-0006-progressive-disclosure-skill-structure.md) | Progressive-disclosure skill structure | Accepted | Lean `SKILL.md` plus `references/` loaded on demand. Rejected: one giant prompt, many tiny skills, external-only docs. |

## Conventions

- One ADR per file, named `adr-NNNN-short-title.md` (kebab-case).
- Status values follow `governance.md`; these are all **Accepted**.
- Each ADR carries front-matter (`id`, `title`, `status`, `date`, `version`)
  and repeats Status/Date in the body for readers viewing the raw file.
- Supersession: a replacing ADR sets `supersedes`/`superseded_by` on both ends;
  the superseded ADR stays (status Superseded) so history survives.
