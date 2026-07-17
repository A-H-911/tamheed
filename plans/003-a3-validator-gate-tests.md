# Plan 003 (A3): Test the validator's uncovered safety-critical gate paths

> **Executor instructions**: Follow this plan step by step. Run every verification command and
> confirm the expected result before moving on. On any STOP condition, stop and report. When done,
> update this plan's row in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat 0e055f6..HEAD -- plugins/keystone/scripts/validate_package.py tests/test_validate_package.py`
> Plans 001 and 002 are EXPECTED to have touched these files — that is not drift. Drift = the
> G-SET excerpts below no longer matching the live `gate_set`.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/001-*.md, plans/002-*.md (they add tests to the same file first)
- **Category**: tests
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Gate G-SET was added specifically to stop a hollow package from passing validation. Its two
sharpest rules have zero test coverage: **Rule B** (an artifact the manifest *declares present*
must exist on disk — the anti-paper-over rule) and the **empty-reason rejection** (an
`omitted_artifacts[]` entry with a placeholder reason like `-` must not count as a valid
omission). A regression deleting either rule would merge green today, silently reopening the hole
the gate exists to close. These tests also protect the v1→v2 migration, which trusts this gate.

Note: the prior version of this plan also covered `init_skill_repo.py` (`create_remote`,
`--force`, idempotency, wrapper smoke tests). Those were **deliberately dropped**: the repo
bootstrap is scheduled for deletion in plan 009 (B4). Do not add tests for `init_skill_repo.py`.

## Current state

- `plugins/keystone/scripts/validate_package.py` — `gate_set` at `:849-912`.
- `tests/test_validate_package.py` — has exactly one G-SET-adjacent negative test,
  `test_gate_set_rejects_unreadable_manifest` (`:409-413`), which covers only broken-JSON.
  The `tests/fixtures/incomplete-package/` fixture covers Rule A (artifact neither present nor
  omitted). Rules below are uncovered.

Verbatim excerpts at `0e055f6`:

```python
# validate_package.py:879-884  (omitted_artifacts parsing — the empty-reason filter)
        for entry in manifest.get("omitted_artifacts") or []:
            if isinstance(entry, dict):
                path = str(entry.get("path") or "").strip()
                reason = str(entry.get("reason") or "").strip()
                if path and reason and reason.lower() not in EMPTY_CELL_VALUES:
                    omitted_paths[path] = reason
```

```python
# validate_package.py:905-910  (Rule B)
    # Rule B (SKIP->FAIL hardening): anything the manifest declares present must
    # actually exist, so a manifest can't paper over a missing artifact.
    for path in sorted(set(declared_present)):
        if not (package_dir / path).is_file():
            result.findings.append(Finding("G-SET", "Critical",
                "manifest.json declares this artifact present, but it is missing on disk", path))
```

Also relevant: `gate_set` reads the Always registry via `_load_required_always()`
(`references/required-artifacts.json`); a package satisfies Rule A when each Always entry has one
of its `match` paths on disk or in `omitted_paths`.

## Commands you will need

Same as plan 001: `python tests/test_validate_package.py` (exit 0) and the four golden package
runs (0/0/1/1).

## Scope

**In scope**: `tests/test_validate_package.py` only.

**Out of scope**: `validate_package.py` (no production change in this plan — if a test exposes a
real bug in `gate_set`, STOP and report it; do not fix inline), all fixtures on disk (build temp
packages in the tests instead of adding fixture directories), `init_skill_repo.py` (see above).

## Git workflow

- Branch: `test/gate-set-rules`; single commit, e.g. `test: cover G-SET Rule B and empty-reason omissions`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Rule B test — declared-present-but-missing fails

Add a test that builds a minimal temp package which passes Rule A (copy the structure the
`tests/fixtures/valid-package/` uses, or synthesize every Always artifact), then adds to its
`manifest.json` an `artifacts[]` entry for a path that does NOT exist, e.g.
`{"path": "requirements/phantom.md"}`. Call `gate_set` (import it — the module exposes an
import-safe API) and assert a Critical finding whose message contains
`declares this artifact present`.

**Verify**: `python tests/test_validate_package.py` → exit 0 including the new test; commenting
out the Rule B loop makes it fail (check once, restore).

### Step 2: Empty-reason test — placeholder reason doesn't count as an omission

Add a test with a temp package missing one Always artifact (e.g. no `risks/risk-register.md`)
whose manifest records it as omitted with a placeholder reason:
`{"path": "risks/risk-register.md", "reason": "-"}`. Assert `gate_set` reports the
`neither present nor recorded` Critical finding — the `-` reason must be rejected by the
`EMPTY_CELL_VALUES` filter at `:883`.

**Verify**: suite green; changing the reason to a real sentence makes the finding disappear
(assert that too, in the same test, as the positive half).

### Step 3: Golden packages

**Verify**: the four golden runs still return 0/0/1/1.

## Test plan

Two tests as above, `unittest` style matching the file's existing G-SET test
(`test_gate_set_rejects_unreadable_manifest`), temp dirs cleaned up, no new fixture directories.

## Done criteria

- [ ] `python tests/test_validate_package.py` → exit 0, +2 tests
- [ ] Goldens 0/0/1/1
- [ ] `git status`: only `tests/test_validate_package.py` modified
- [ ] `plans/README.md` row updated

## STOP conditions

- The `gate_set` excerpts don't match the live code beyond plans 001/002's changes.
- A test exposes an actual defect in `gate_set` (e.g. Rule B not firing) — report; production
  changes are out of scope here.

## Maintenance notes

- When plan 010 (B5 migration) lands, these tests define the minimum integrity bar its v1 intake
  relies on; keep them passing against the frozen v1 validator.
- Deferred: `create_remote` / `--force` / wrapper coverage — intentionally dead scope (bootstrap
  deletion in plan 009).
