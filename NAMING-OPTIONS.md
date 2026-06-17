# Naming Options & Recommendation

Status: Decided · 2026-06-17 · **Selected: `Keystone`** (chosen by the project owner)

The capability: a reusable **project-inception → R&D-planning → architecture-governance → execution-handoff
→ repository-initialization** engine, intended to grow into broader project-management and engineering
workflows. Naming criteria (from the brief): short, memorable, vendor-neutral, technology-neutral, easy to
type as a slash command, valid as a GitHub repo name, and **broad enough to support future capabilities
without becoming misleading**.

Scoring is 1–5 (5 = best). "Ambiguity" is scored so that 5 = least ambiguous / lowest collision risk.

## Candidates

### 1. Keystone — **SELECTED**
- Skill: `Keystone` · Command: `/keystone` · Repo: `keystone`
- **Rationale:** the keystone is the wedge-shaped stone at the apex of an arch that locks all other stones
  in place — nothing stands without it. It maps cleanly onto "the planning foundation that makes execution
  hold together," and onto the architecture-governance theme. Single word, strong imagery, easy to type.
- Clarity 4 · Memorability 5 · Extensibility 5 (not tied to "the beginning"; works across plan→execute→
  govern) · Ambiguity 2 (**collision:** OpenStack **Keystone** is a well-known identity service; "keystone"
  also appears in other tools/brands). 
- **Trade-off accepted:** the OpenStack collision is real for a technical audience. Mitigations: always
  present as "Keystone (project inception)" in docs/README; the GitHub repo `keystone` may already be taken
  for the bare name, so plan for an owner/scope (`<owner>/keystone`) or a fallback repo slug
  (`keystone-inception`, `keystone-kit`) while keeping the command `/keystone`.

### 2. Project Forge
- Skill: `Project Forge` · Command: `/project-forge` · Repo: `project-forge`
- **Rationale:** a forge crafts many things from raw material — apt for "forge a project from a brief," and
  scales as scope grows. The original working name.
- Clarity 5 · Memorability 4 · Extensibility 5 · Ambiguity 3 (overlaps code-forge tooling: SourceForge,
  Forgejo, "forge" in many dev contexts; two-word, hyphenated command is longer to type).

### 3. Groundwork
- Skill: `Groundwork` · Command: `/groundwork` · Repo: `groundwork`
- **Rationale:** "lay the groundwork" — foundation/inception. Clean single word, vendor-neutral, very low
  collision in dev tooling.
- Clarity 5 · Memorability 4 · Extensibility 3 (leans toward "the beginning"; risks feeling narrow once the
  capability drives execution/progress) · Ambiguity 5.

### 4. Charter
- Skill: `Charter` · Command: `/charter` · Repo: `charter`
- **Rationale:** the project charter is a core inception artifact; connotes authorizing/initiating +
  governance. Short, professional, very typeable.
- Clarity 5 · Memorability 4 · Extensibility 3 (reads as "the charter doc"; narrower than the full
  inception→handoff scope) · Ambiguity 4 (Charter Communications brand; common English word).

### 5. Blueprint
- Skill: `Blueprint` · Command: `/blueprint` · Repo: `blueprint`
- **Rationale:** plans/specs/architecture — instantly communicates "the plan."
- Clarity 5 · Memorability 5 · Extensibility 4 · Ambiguity 2 (**very** common project/product name — many
  "Blueprint" repos, frameworks, and products; high collision).

### 6. Launchpad
- Skill: `Launchpad` · Command: `/launchpad` · Repo: `launchpad`
- **Rationale:** readiness-to-launch / execution handoff.
- Clarity 4 · Memorability 4 · Extensibility 4 · Ambiguity 2 (Canonical **Launchpad** is a major existing
  platform; high collision).

### 7. Scaffold
- Skill: `Scaffold` · Command: `/scaffold` · Repo: `scaffold`
- **Rationale:** scaffolding a project.
- Clarity 4 · Memorability 4 · Extensibility 2 (strongly implies **code** scaffolding/generators — would
  mislead about Keystone's planning/governance focus) · Ambiguity 2 (heavily used term).

## Comparison

| Name | Clarity | Memorability | Extensibility | Ambiguity (5=low risk) | Total |
|---|---|---|---|---|---|
| **Keystone** | 4 | 5 | 5 | 2 | 16 |
| Project Forge | 5 | 4 | 5 | 3 | 17 |
| Groundwork | 5 | 4 | 3 | 5 | 17 |
| Charter | 5 | 4 | 3 | 4 | 16 |
| Blueprint | 5 | 5 | 4 | 2 | 16 |
| Launchpad | 4 | 4 | 4 | 2 | 14 |
| Scaffold | 4 | 4 | 2 | 2 | 12 |

## Recommendation vs decision

On raw score, **Project Forge** and **Groundwork** edge ahead, primarily because Keystone, Blueprint, and
Launchpad carry real collision risk. A purely analysis-driven recommendation would short-list Project Forge
(most extensible, brandable) or Groundwork (cleanest, lowest collision).

**The project owner selected `Keystone`.** It scores top on memorability and extensibility and fits the
architecture-governance metaphor exceptionally well; the only material weakness is the OpenStack-Keystone
collision, which is mitigated by consistent "Keystone (project inception)" framing and an owner-scoped or
fallback repo slug if `keystone` is unavailable. This decision is recorded as `ADR-0001` in `adrs/`.

## Identity (as built)

- **Skill name:** `keystone`
- **Slash command:** `/keystone`
- **GitHub repo:** `keystone` (fallbacks if taken: `keystone-inception`, `keystone-kit`)
- **One-line:** *Keystone turns a project description into an execution-ready plan and handoff package.*
