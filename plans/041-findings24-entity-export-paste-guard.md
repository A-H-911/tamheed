# Plan 041 (B37): findings_24 — the sanctioned read for committed scripts (`entity_export`) + the paste guard — v4.7.0

## Status

**DONE (2026-09-06)** — `python check.py` fully green, `--selftest` green (18 tools).
Version stamped **v4.7.0** (MINOR — a new tool and a new `entity_upsert` item key; no
schema migration). *Release only on the maintainer's explicit words.*

## What this was

findings_24 (evidence **C45**) reported one GAP and no defect. The tool-owned note says
all package reads and writes go through the MCP tools; the field's operator made that
unconditional (`DEC-135` d1); their four committed slate generators — the scripts that
discharge `LL-011`, every record the operator decides against quoted byte-exact from the
store — then had no sanctioned route to whole canonical rows. Both ways out were bad:
hand-transport (their measured `LL-063` loss: a 4,296-character field dropped a paragraph
mid-paste with `ok: true`) or a JSON-RPC client re-implemented per consumer, which their
operator declined as "a workaround shaped like compliance". The report deliberately named
no shape. It also verified `entity_query` truncates nothing, superseding a pinned lesson of
their own, and that `retire` caught a mis-typed `amends` within an hour.

Verified at source and on ACMP data before planning: the note sentence lives once in the
server; every mutation writes back at commit; `store.load()` is lock-free; the SDK imports
lazily; the disposition rows exist; only `lessons` carries the immutability trigger.

Maintainer-locked: the **`entity_export` tool** (the CLI and a lock-free open were
offered; the tool keeps the read rule literally true — the tool wrote the file), exposing
**all read-only tools**; the **`expect_unchanged`** guard; **v4.7.0**.

## What shipped

1. **`entity_export(path, tool?, args?)`** — 18 tools. Runs one read-only tool
   (`entity_query` default; `trace_query`, `gate_run`, `readiness_check`,
   `package_verify` with `record` refused, `server_info`) and writes its WHOLE result to
   `<package>/exports/<path>` (absolute allowed; refused under `data/`, resolved first;
   an existing file replaced only if it is itself an export). Envelope
   `{"tamheed_export": {version, package, tool, args, digest, memory_matches_disk},
   "result"}`; the digest is of the OPEN connection's canonical form; deterministic (no
   timestamp); the result carries metadata only with `count`/`total`/`partial` and a
   PARTIAL note; the docstring says the file has no payload cap.
2. **`expect_unchanged: [cols]`** on an upsert item: id-keyed rows only, never the
   journal; the row must exist; each named column compared to the stored value (JSON
   parsed; an omitted named column counts as changed); drift refused naming the columns.
3. **`package_verify`** shares `_canonical_digest` and `_dump_open_connection` with the
   new tool (refactor, no behaviour change).
4. **The note span**: the read rule draws the line (`data/` tool-owned; a committed
   script quotes an `exports/` file); two cheat-sheet lines.
5. **Teaching sweep**: server README (row + two rules), SKILL.md, both READMEs (+ the
   mermaid tool node, `exports/` in the package layout), docs/architecture (ASCII list,
   the three-actor sequence diagram, the read-side paragraph), CANONICAL.md,
   SECURITY.md, governance + template (lint-11 needle `expect_unchanged`), state.md;
   five stock prompts with roster appends (slice-review, progress-sync,
   register-liveness, package-onboarding, README — incl. LL-063's producer-source rule).
6. **Tests**: the export battery (whole rows byte-exact through the file, `exports/`
   resolution, determinism, `data/` + traversal + directory + non-export overwrite
   refusals, the allow-list, `record` refused, inner error propagated with nothing
   written, wrong kwargs, all six tools, `digest` == `package_verify`, partial/whole,
   closed-package refusal); the guard battery (one-space drift refused naming `title`
   with the batch rolled back, JSON spacing tolerated, byte-identical accepted, omitted
   column refused, missing row, unknown column, trace-edge, journal); the note needles.
7. **Evals**: four lab-tracker assertions (the export exists, carries the envelope,
   holds the criterion's own text, the beat's note names `expect_unchanged`).

## The DA round's catches (folded before execution)

`exported_at` dropped (determinism doctrine); overwrite restricted to existing exports;
`package_verify(record)` refused; the digest taken from the open connection with
`memory_matches_disk` beside it; `partial`/`count`/`total` + the no-cap sentence;
traversal resolved before the `data/` check; the guard refuses journal types and
compares JSON parsed; the beat exercises the guard on a `DEF-` row (the trigger-less
class the finding named). Stated, not changed: a session-less consumer (CI, a cron) has
no route — the read-only CLI is recorded as a future option.

## The lessons register, read again

63 rows (+`LL-063`, which supersedes `LL-045`). `LL-063`'s first half is the paste guard;
its second half — a producer's SOURCE is an instrument the output-vs-output frame hides —
became a line in the prompts README's standing rules.

## Verification

check.py green end-to-end (see the lab section for the beat-14 fixture); `--selftest`
lists 18 tools; the ACMP shape re-proven in-test (a 6,000-character field exported and
read back byte-exact; a one-space transport drift refused by the guard).

## The lab's beat 14 (real agent) — see `plans/evidence/lab-continuation-report-041-2026-09-06.md`

Every ✔ observed, none missed: the migrate refusal verbatim; the export exact (`count 2,
total 2, partial False, memory_matches_disk True`, digest == `package_verify()`, no rows
in the return; the file's envelope and both whole rows confirmed); the committed
generator (`workspace/scripts/gen-slate.py`, 86 lines, stdlib) rendering `slate.html`
from the export, its verifier PASSING on both rows and its calibration DETECTING the
planted corruption, byte-deterministic across runs, refusing a non-export; the
partial/whole pair (`1 of 5` with the PARTIAL note, then `5 == 5`); the `gate_run`
export; both refusals verbatim with nothing written under `data/`; the paste guard
refusing a one-word title drift naming `title` and accepting the exact title with only
the severity flipped, the row re-read byte-identical after the restore; the note's
export sentence and both cheat-sheet lines emitted; five stale-stock prompts refreshed;
`gate_run` ready; 26/26 lab assertions and `check.py` green under the agent's own run.

The agent's findings, triaged: (1) the recorded exports carry digest D1 while the
committed store verifies at D2 — by construction (the beat's closing journal row
followed the exports); the scenario now states it as the fixture note, and it is the
very reason a slate cites its digest; (2) the brief said "severity → medium" while the
fixture's DEF-001 was `high` — the flip was real because of that, nothing to change;
(3) the guard's refusal is two-layered (batch line + per-item text) — the existing
batch contract, kept.

## Left open

ACMP-side: upgrade → rebuild the four generators to read an `entity_export` file
(`WBS-31` unblocks; `DEC-138` d1's condition is met by a sanctioned route with the rule
untouched — their ruling); the export step becomes the first line of each slate prompt;
the digest goes into the slate header; `expect_unchanged` on every long-row status flip;
the `SL-038` verdicts can proceed against a compliant slate. Session-less consumers: the
CLI future option.
