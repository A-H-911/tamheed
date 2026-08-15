# Tamheed tests

The deterministic test suites for the Tamheed store, MCP server, migration path, and tooling.
Everything here is **stdlib-only** (`unittest`, no pytest, no third-party packages, no
`coverage.py`); each suite is runnable directly:

```
python tests/test_<name>.py
```

## The eight suites

| Suite | What it pins |
|---|---|
| `test_db_roundtrip.py` | The store's integrity core: JSONL → SQLite → JSONL byte identity, FOREIGN KEY enforcement, CHECK enforcement, ADR supersession immutability (trigger-enforced), the requirement auto-advance trigger, and the single-writer lockfile. |
| `test_store_migrations.py` | Schema-migration chain mechanics: `PRAGMA user_version` tracks the applied head (stamped from Python, never inside the SQL files), re-application is a no-op, migrations apply before the JSONL load, and orphan JSONL for a dropped table loads without error. |
| `test_mcp_contract.py` | The ~100-test tool-surface contract, driven in-process (no live transport, no SDK needed): create → batch upsert (per-item verdicts naming violated constraints) → query → trace → `gate_run` → the execution loop (`progress_update` / `audit_record` / `work_bind`) → handoff emission + injection screen → lockfile conflict → `export_html` → the missing-SDK error path → `--selftest`. Includes the V4Engine behavior and the teaching-surface needles (prompts/templates may only teach tool and gate names that exist). |
| `test_migrate_v3to4.py` | The v3 → v4 transform contract: the `package_open` refusal on pre-v4 stores, the preview report (every documented transform), the confirmed conversion (backup kept, legacy-prompt conversion, store-validated write-back), per-transform row outcomes, double-migration refusal, the migrated package opening clean with G-REL passing, and **byte-determinism** (same input → byte-identical output). |
| `test_adopt_sample.py` | Adopt mode's four mechanical rules on a synthesized brownfield tree: code-shaped provenance everywhere, zero `Approved` rows, a non-empty gap report, and passing gates on the adopted package. |
| `test_export_html.py` | The HTML review surface: all sections render for a real package, hostile content (`<script>`, `onerror=`, `javascript:` links) never appears unescaped, and two exports of the same DB state are byte-identical. |
| `test_eval_runner.py` | The deterministic eval runner + `pkg_check.py` assertion primitives, driven as subprocesses (their real contract is exit codes + printed output): PASS on the shipped sample, FAIL on a broken copy, visible SKIP on unrecorded cases, non-zero when nothing was checked. |
| `test_scratch_diff.py` | The runbook-§8 scratch-diff tool: correct per-table keying (the historical mis-keyings are regression cases), union-of-columns comparison **including JSON blobs**, report-never-clobber duplicates, and the 0/1/2 exit-code contract (exit 1 is the normal mid-life outcome). |

## How check.py routes them

`check.py` at the repo root is THE deterministic gate — its `SUITES` list is the single
registry of these eight files, and CI job 1 runs exactly:

```
python check.py            # all suites + the lint battery + canonical form + eval fixtures
python check.py suites     # just the eight suites
```

A new suite registers itself in `check.py`'s `SUITES` list — nowhere else; CI picks it up
from there. The other subset gates are `lint`, `canonical`, and `evals`.

## The no-fixtures doctrine

There is no `tests/fixtures/` directory. Every suite **builds its own packages** in a
temp directory through the real tools (`package_create`, `entity_upsert`, …) — the setup
path is itself under test, and nothing on disk can rot out from under the assertions.

The committed goldens live elsewhere, as real artifacts rather than test fixtures:

- `generated-samples/support-triage-agent-v2/` — the demonstration package, migrated in
  place through every store generation (v1 → v4);
- `evals/sample-results/` — the eval runner's recorded sample, exercised by
  `python check.py` (gate `evals`).

## Coverage

Coverage is not tracked as a committed number (numbers rot). When you need it, measure with
the standard-library `trace` module:

```
python -m trace --count --summary --coverdir=.cov tests/test_db_roundtrip.py
```

`trace` measures line, not branch, coverage; for branch metrics run `coverage.py --branch`
separately (it is deliberately not a project dependency).
