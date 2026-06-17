---
id: ADR-0004
title: Provider-neutral repository bootstrap
status: Accepted
date: 2026-06-17
version: 1.0.0
---

# ADR-0004: Provider-neutral repository bootstrap

Status: Accepted
Date: 2026-06-17

## Context

Keystone can turn a finished package into a real initial repository (Stage 18,
via `scripts/init_skill_repo.py`). Creating a repository touches two distinct
things: a **local** git repository (always wanted) and a **remote** hosted
repository (sometimes wanted, on a host the user chooses). GitHub is the common
default, but binding the bootstrap to GitHub would make Keystone unusable for
GitLab, Gitea/Forgejo, Codeberg, or air-gapped/local-only users, and would
entangle the always-safe local path with credentials and network calls that the
local path does not need.

## Decision

Make the bootstrap **provider-neutral** (safeguard 14):

- **Local git always works.** `git init`, the folder structure, baseline files,
  and the initial commit happen with no network and no provider assumptions.
- **Remote creation is an optional, swappable step.** GitHub via the `gh` CLI
  is the default remote implementation, gated behind `--create-remote`; the
  remote step is isolated so another provider can be slotted in without
  touching the local path.
- **Prerequisites are validated per path.** `git` is required; `gh` is checked
  only when `--create-remote` is requested, and missing tools fail with a clear
  message listing what is needed.
- **Side-effectful actions require explicit approval.** Creating a remote or
  pushing never happens without explicit approval in the conversation.

## Consequences

- Keystone is usable by anyone with git, regardless of host, including
  local-only and air-gapped users.
- The risky, networked, credentialed part (remote creation/push) is opt-in and
  cleanly separated from the safe local part, which reduces blast radius and
  makes the tool predictable.
- Adding a new remote provider is a localized change behind the same flag,
  not a rewrite.
- **Cost:** GitHub users do not get a zero-config "just push it" default; they
  must pass `--create-remote` and have `gh` available. Accepted as the price of
  neutrality and safety, and consistent with the bootstrap's broader safety
  contract (dry-run first, no overwrite without `--force`, refuse a dirty
  target).

## Alternatives considered and rejected

- **Hard GitHub coupling** (always create+push to GitHub). Rejected: excludes
  every non-GitHub and local-only user, bakes a provider choice into the skill
  (which should be a per-use decision), and forces network/credentials into the
  always-on local path. Directly violates safeguard 14.
- **Abstract every provider behind a plugin layer now.** Rejected as premature:
  a full provider-plugin framework is overhead with one real implementation
  today. Isolating the remote step behind a flag captures the swappability
  benefit and leaves the door open to a plugin layer if a second provider
  actually lands.
- **Print instructions instead of creating anything.** Rejected: the value of
  Stage 18 is producing a real, initialized repo, not a checklist. Safety is
  achieved through dry-run, approval, and no-overwrite defaults rather than by
  refusing to act. (When the user prefers to bootstrap themselves, Keystone
  delivers the script plus the suggested invocation and does not execute it —
  but that is a per-use choice, not the architecture.)
