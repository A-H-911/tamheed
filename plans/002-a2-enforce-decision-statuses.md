# Plan 002 (A2): Enforce the decision-status set on DEC- rows (and reconcile governance.md)

> **Executor instructions**: Follow this plan step by step. Run every verification command and
> confirm the expected result before moving to the next step. If anything in the "STOP conditions"
> section occurs, stop and report — do not improvise. When done, update the status row for this
> plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat 0e055f6..HEAD -- plugins/keystone/scripts/validate_package.py plugins/keystone/references/governance.md tests/test_validate_package.py`
> On any drift, compare "Current state" excerpts to the live code first; mismatch = STOP.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/001-a1-fix-falsy-or-id-column.md (same file/test suite; land 001 first)
- **Category**: bug / contract
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Gate G-DEC-STATUS exists to enforce a core safeguard: a decision is never rendered with a status
it hasn't earned. The validator defines the strict decision-status set (`DECISION_STATUSES`,
`validate_package.py:105`) but **never applies it** — the only use is building the looser
`DOCUMENT_STATUSES` on the next line. Both standalone ADR documents and `DEC-` register rows are
checked against `DOCUMENT_STATUSES`, so a `DEC-` row with `Draft`, `Accepted`, or `Obsolete`
passes even though `references/governance.md:59` says the decision set is "exactly" five values.
Additionally, governance.md contradicts itself: its own lifecycle (`:46`, `:56`) flows items to
`Implemented` during execution. **The maintainer decided (recorded decision D-U1, 2026-07-11):**
DEC- rows allow `{Proposed, Approved, Rejected, Superseded, Deferred, Implemented}` — the five
plus `Implemented` — and `governance.md:59` is amended to say so explicitly. Doc and code move in
the same commit.

## Current state

Files:

- `plugins/keystone/scripts/validate_package.py` — validator; `gate_dec_status` at `:551-609`.
- `plugins/keystone/references/governance.md` — the identifier/status contract (authoritative doc).
- `tests/test_validate_package.py` — stdlib-only self-test (no pytest).

Verbatim excerpts at `0e055f6`:

```python
# validate_package.py:105-106
DECISION_STATUSES = {"Proposed", "Approved", "Rejected", "Superseded", "Deferred"}
DOCUMENT_STATUSES = DECISION_STATUSES | {"Accepted", "Implemented", "Obsolete", "Draft"}
```

```python
# validate_package.py:553  (top of gate_dec_status)
    allowed = {s.lower() for s in DOCUMENT_STATUSES}
```

```python
# validate_package.py:594-607  (the DEC/ADR table-row loop, abridged)
            for r_idx, row in enumerate(table.rows):
                line = table.start_line + 1 + r_idx
                row_id = row[id_col].strip().strip("`") if (id_col is not None and id_col < len(row)) else ""
                if id_col is not None and row_id and not (row_id.startswith("DEC-") or row_id.startswith("ADR-")):
                    continue
                cell = row[status_col].strip().strip("`") if status_col < len(row) else ""
                if cell.lower() in EMPTY_CELL_VALUES:
                    ...  # "has no status" finding
                elif _norm_status(cell) not in allowed:
                    ...  # "invalid status" finding, message prints sorted(DOCUMENT_STATUSES)
```

Standalone ADR documents are checked at `:561-574` against the same `allowed` — that behavior is
CORRECT and must not change (ADR docs legitimately use Draft/Accepted/Implemented/Obsolete).

```text
# governance.md:59-60
**Decision statuses** are exactly: Proposed, Approved, Rejected, Superseded, Deferred. Never render a
Proposed decision as if Approved — this is a core safeguard.
```

The governance lifecycle at `:46` includes `Approved/Implemented → Superseded` and `:56` defines
`Implemented` — the internal tension D-U1 resolves.

The validator also carries a self-documenting inline gate reference near `:1125-1131` that
restates the allowed sets — it must be updated to match, or the file contradicts itself.

Verified safety fact: no golden package is affected. Every `DEC-` row in
`tests/fixtures/*/decisions/open-decision-register.md` and
`generated-samples/support-triage-agent/decisions/open-decision-register.md` uses
Approved/Proposed/Deferred (plus one deliberately empty status in `invalid-package`, which is a
different finding path).

## Commands you will need

Same five commands as plan 001 ("Commands you will need" table there): the test suite plus the
four golden package runs with expected exit codes 0/0/1/1.

## Scope

**In scope**: `plugins/keystone/scripts/validate_package.py`,
`plugins/keystone/references/governance.md` (one sentence), `tests/test_validate_package.py`.

**Out of scope**: the standalone-ADR branch (`:561-574`) behavior; `adr-metadata.schema.json` and
`decision.schema.json` (their enums are consistent with governance and are NOT part of D-U1 —
if you believe they need changing, STOP and report); all fixtures and the demo package.

## Git workflow

- Branch: `fix/enforce-dec-row-statuses`; single commit, e.g.
  `fix: enforce decision-status set on DEC- rows per governance (D-U1)`.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Update the status-set constants

In `validate_package.py:105-106`, make `DECISION_STATUSES` the D-U1 six-value set and keep
`DOCUMENT_STATUSES` exactly as it computes today:

```python
DECISION_STATUSES = {"Proposed", "Approved", "Rejected", "Superseded", "Deferred", "Implemented"}
DOCUMENT_STATUSES = DECISION_STATUSES | {"Accepted", "Obsolete", "Draft"}
```

(`DOCUMENT_STATUSES` membership is unchanged by this refactor — verify by listing it mentally:
the same nine values.)

**Verify**: `python tests/test_validate_package.py` → exit 0.

### Step 2: Apply the per-prefix set in the row loop

In `gate_dec_status`, keep `allowed` (document set) for the standalone-ADR branch and ADR- rows,
and check `DEC-` rows against the decision set. In the row loop (`:594-607`), after `row_id` is
computed, select the set:

```python
                is_dec_row = row_id.startswith("DEC-")
                row_allowed = ({s.lower() for s in DECISION_STATUSES}
                               if is_dec_row else allowed)
```

(Hoist the lowered decision set out of the loop as a local computed once next to `allowed` —
match the file's existing style at `:553`.) Use `row_allowed` in the `elif` check, and make the
invalid-status message print the set that was actually applied
(`sorted(DECISION_STATUSES)` for DEC- rows, `sorted(DOCUMENT_STATUSES)` otherwise).
Rows with an empty `row_id` (no ID column) keep the document set — do not tighten them.

**Verify**: `python tests/test_validate_package.py` → exit 0 (existing tests still green).

### Step 3: Amend governance.md:59

Replace the first sentence of the `:59-60` block with:

```text
**Decision statuses** are exactly: Proposed, Approved, Rejected, Superseded, Deferred — plus
Implemented once a decision is realized during execution/update cycles. Never render a
Proposed decision as if Approved — this is a core safeguard.
```

**Verify**: `grep -n "plus" plugins/keystone/references/governance.md` shows the amended line;
no other line of the file changed (`git diff --stat` shows 1 file, minimal lines).

### Step 4: Update the validator's inline gate reference

Near `:1125-1131`, adjust the G-DEC-STATUS description to state: DEC- rows accept exactly the
six decision statuses; ADR documents and ADR index rows additionally accept
Accepted/Obsolete/Draft.

**Verify**: `python plugins/keystone/scripts/validate_package.py --help` (or however the inline
reference is surfaced — it is a comment block; verify by reading the diff) → text matches Step 2's
behavior.

### Step 5: Add two regression tests

In `tests/test_validate_package.py` (same conventions as plan 001's tests):

1. A decision register with `| DEC-001 | ... | Draft |` → assert a G-DEC-STATUS finding whose
   message contains `invalid status`.
2. A decision register with `| DEC-002 | ... | Implemented |` and an ADR index row
   `| ADR-0001 | ... | Draft |` in the same table → assert **no** G-DEC-STATUS finding (both are
   legal under D-U1: Implemented for DEC-, Draft for ADR-).

**Verify**: `python tests/test_validate_package.py` → exit 0, test count +2; reverting Step 2
makes test 1 fail (fail-before/pass-after — check once, re-apply).

### Step 6: Golden packages

**Verify**: the four golden runs return 0/0/1/1 as in plan 001.

## Test plan

Two tests as in Step 5; no existing test modified. The `invalid-package` fixture's empty-status
row continues to exercise the empty-cell path — untouched.

## Done criteria

- [ ] `python tests/test_validate_package.py` → exit 0, +2 tests
- [ ] Goldens: 0/0/1/1
- [ ] `grep -c "Implemented" plugins/keystone/scripts/validate_package.py` includes the new
      DECISION_STATUSES membership; `DOCUMENT_STATUSES` still has 9 members
- [ ] governance.md:59 names Implemented explicitly
- [ ] Only the three in-scope files modified
- [ ] `plans/README.md` status row updated

## STOP conditions

- Excerpts don't match live code (drift).
- Any golden package fails after Step 2 — a fixture uses a status this plan didn't anticipate;
  report which file/row rather than loosening the set.
- You find a consumer that imports `DECISION_STATUSES` from outside this file.

## Maintenance notes

- `decision.schema.json` / `adr-metadata.schema.json` enums were deliberately left alone; if a
  future change adds `Implemented` to machine-surface decisions, update schema + governance + this
  gate together.
- Reviewer scrutiny: the row-loop selection logic — ADR- rows in a mixed DEC/ADR table must keep
  the document set.
