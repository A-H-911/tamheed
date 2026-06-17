# Invocation modes

The thin entry point may pass a mode; if absent, infer from input completeness and **confirm with the user
before doing heavy work**. Modes change where the workflow starts/stops, not the methodology.

| Mode | Purpose | Starts | Stops | Writes a repo? |
|---|---|---|---|---|
| `full` | End-to-end inception → handoff | Stage 1 | Stage 22 | Yes (Stage 18), unless `--no-repo` |
| `intake` | Understand + surface gaps only | Stage 1 | Stage 7 (clarification plan) | No |
| `plan` (dry-run) | Full plan + artifacts, no repository | Stage 1 | Stage 17 + readiness preview | No |
| `resume` | Continue an interrupted package | last completed stage | as configured | Maybe |
| `stage:<id>` | Run/re-run one stage | that stage | that stage | Only if it is Stage 18 |
| `update` | Apply new decisions/progress | Stage 21 | Stage 22 | Refreshes derived artifacts only |

## Inference when no mode is given

- Sparse / idea-level input → propose `intake` (clarify first), then offer `full`.
- Rich, structured brief with explicit constraints → propose `full`.
- User points at an existing package directory → propose `resume` or `update`.
- User asks for "just the plan" / "don't create a repo" → `plan`.

Always state the chosen mode and what it will and will not do, then proceed.

## Mode contracts

- Every mode reads/writes `keystone-state.json`; `stage:<id>` requires existing state (or runs its own
  prerequisites in a lightweight way and records that it did).
- `plan` and `intake` must be side-effect-free outside the package directory.
- `full` and `update` honor approval gates: do not pass an approval gate on the user's behalf.
- `--no-repo`, `--force`, `--owner`, `--visibility`, `--license`, `--default-branch` flow through to repo
  initialization (Stage 18) only.
