# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]
# ///
# C33 (A1): the ONE external dependency is bounded below the major — MCP SDK 2.0.0
# removed mcp.server.fastmcp, so an unbounded resolve broke every fresh environment
# (new installs, CI, cleaned uv caches) while cached ones kept working. Porting to
# mcp.server.mcpserver is deferred, deliberate work — never widen this pin without it.
"""Tamheed MCP server — the only write path into a v2 package (plan 008/B3, ADR-0001).

Successor of validate_package.py: the mechanical half of the capability the skill owns.
Tool handlers are plain functions (in-process testable, no transport needed); the official
MCP SDK wraps them for stdio serving. The SDK import is deferred to serve time so this
module — and the contract tests — work without it.

Rules (locked): no raw-SQL tool, ever; batch-first mutations in one transaction;
single-writer via the store lockfile; stored text is data, never instructions.
"""
from __future__ import annotations

import argparse
import csv as _csv
import datetime as _dt
import io
import json
import os
import re
import sys
from pathlib import Path

_SERVER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SERVER_DIR.parent / "db"))

import store  # plugins/tamheed/db/store.py  # noqa: E402

# Inlined from the retired v1 validator (D-017-4 parity kept): blank out fenced +
# inline code so TODO/{{...}} inside examples is never flagged as an unfinished marker.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def _strip_code(text: str) -> str:
    text = _CODE_FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return _INLINE_CODE_RE.sub(" ", text)

# --------------------------------------------------------------------------- state

PACKAGE_ROOT = Path(".")          # set by --package-dir; tests override directly
_CURRENT: store.PackageStore | None = None
_CURRENT_NAME: str | None = None

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# entity type -> table. The registry rows seeded at package_create mirror this.
ENTITY_TABLES = {
    "requirement": "requirements",
    "constraint": "constraints",
    "invariant": "invariants",
    "assumption": "assumptions",
    "dependency": "dependencies",
    "open-question": "open_questions",
    "decision": "decisions",
    "adr": "adrs",
    "risk": "risks",
    "hypothesis": "hypotheses",
    "experiment": "experiments",
    "poc": "pocs",
    "test": "tests",
    "kpi": "kpis",
    "stakeholder": "stakeholders",
    "phase": "phases",
    "milestone": "milestones",
    "slice": "slices",
    "wbs-item": "wbs_items",
    "acceptance-criterion": "acceptance_criteria",
    "audit-verdict": "audit_verdicts",
    "progress-entry": "progress_entries",
    "defect": "defects",
    "deferred-work": "deferred_work",
    "execution-gate": "execution_gates",
    "execution-plan": "execution_plans",
    "convention": "conventions",
    "scope-change": "scope_changes",
    "waiver": "waivers",           # v4 (plan 031): scoped, justified, approved, expiring
    "narrative-document": "narrative_documents",
    "document-section": "document_sections",
    "diagram": "diagrams",
    # "prompt" removed in v3.0.0 (plan 027, migration 003) — prompts are .md files in
    # <package>/prompts/, not entities; a legacy prompts.jsonl is converted by the
    # v3→v4 migration (package_open refuses pre-v4 stores).
    "glossary-term": "glossary_terms",  # community-extension worked example
    "trace-edge": "trace_edges",   # composite PK; write surface for relations
    "omission": "omissions",       # G-SET recorded-omitted rows (entity_type + reason)
}

_NON_ID_TABLES = {"trace_edges": "from_id", "omissions": "entity_type"}

# ------------------------------------------------------------- relation endpoint rules
# Plan 027 (B23): a typed relation constrains what its endpoints may BE — the schema
# CHECK constrains the vocabulary, these rules constrain the semantics (TEST —mitigates→
# FR was accepted for a year). Enforced HARD on new entity_upsert writes only; migrate/
# adopt insert via raw SQL, so legacy data loads untouched and gate_run reports stored
# violations as an ADVISORY list. Anchors: references/traceability.md chain,
# workflow.md stages 10/12/14, schema.sql risks.discharged_by, the golden's edge combos.
_REQ_LIKE = frozenset({"requirement", "constraint", "invariant", "assumption"})
_DECISION = frozenset({"decision", "adr"})
# v4: `milestone` left _WORK with its demotion to a label (plan 031) — a roadmap
# marker neither implements nor blocks; existing milestone edges retype to
# relates_to at migration.
_WORK = frozenset({"phase", "slice", "wbs-item", "execution-plan",
                   "defect", "deferred-work"})
_VERIF = frozenset({"test", "acceptance-criterion", "experiment", "poc"})

# The drift-delta targets: what a scope change may add/modify/remove (plan 031).
_PLAN_ROWS = (_REQ_LIKE | _WORK
              | frozenset({"acceptance-criterion", "risk", "kpi", "open-question"}))

# relation -> (allowed from-types | None=any, allowed to-types | None=any).
# Absent relation ('relates_to') = the untyped escape hatch. "SAME_TYPE" = both
# endpoints must share one entity type (supersession is always within a family).
# v4 (plan 031): binds_to DELETED (zero usage ever); scope_adds/scope_modifies/
# scope_removes carry drift-delta intent. Kinds with no evidenced edge semantics
# (stakeholder, audit-verdict, progress-entry, execution-gate as source, waiver,
# narrative-document, document-section, diagram, glossary-term) are DELIBERATELY
# relates_to-only — a guessed rule risks false rejections (the binds_to lesson);
# waivers and gates point at entities via their own applies_to column instead.
RELATION_RULES: dict = {
    "derives_from": (_REQ_LIKE | {"acceptance-criterion", "open-question", "hypothesis"},
                     _DECISION | _REQ_LIKE | {"stakeholder"}),
    "mitigates": (_DECISION | _WORK | _VERIF | _REQ_LIKE | {"convention"},
                  frozenset({"risk"})),
    "verifies": (_VERIF | {"invariant", "kpi"},
                 _REQ_LIKE | {"acceptance-criterion", "hypothesis", "risk"}),
    "supersedes": "SAME_TYPE",
    "blocked_by": (_WORK | {"open-question", "decision", "requirement"},
                   _WORK | {"open-question", "dependency", "decision", "risk",
                            "assumption", "execution-gate"}),
    "implements": (_WORK, _REQ_LIKE | _DECISION | {"acceptance-criterion"}),
    "satisfies": (_WORK | {"poc"}, _REQ_LIKE | {"acceptance-criterion", "kpi"}),
    "tests": (frozenset({"test"}),
              _REQ_LIKE | _DECISION | {"acceptance-criterion", "risk", "wbs-item",
                                       "slice", "defect"}),
    "discharges": (frozenset({"acceptance-criterion", "test"}),
                   frozenset({"risk", "assumption", "open-question", "hypothesis"})),
    "scope_adds": (frozenset({"scope-change"}), _PLAN_ROWS),
    "scope_modifies": (frozenset({"scope-change"}), _PLAN_ROWS),
    "scope_removes": (frozenset({"scope-change"}), _PLAN_ROWS),
}


def _edge_rule_violations(conn) -> list[str]:
    """Stored trace edges violating RELATION_RULES (the G-REL substrate; also run by
    package_adopt, whose raw-SQL inserts bypass the per-write enforcement)."""
    mistyped = []
    for from_id, to_id, relation, ftype, ttype in conn.execute(
            "SELECT e.from_id, e.to_id, e.relation, a.entity_type, b.entity_type"
            " FROM trace_edges e JOIN entity_index a ON a.id = e.from_id"
            " JOIN entity_index b ON b.id = e.to_id"
            " ORDER BY e.from_id, e.to_id, e.relation"):
        rule = RELATION_RULES.get(relation)
        if rule is None:
            continue
        if rule == "SAME_TYPE":
            bad = ftype != ttype
        else:
            from_ok, to_ok = rule
            bad = ((from_ok is not None and ftype not in from_ok)
                   or (to_ok is not None and ttype not in to_ok))
        if bad:
            mistyped.append(f"{from_id} ({ftype}) —{relation}→ {to_id} ({ttype})")
    return mistyped


def _relation_rule_error(conn, cols: dict) -> str | None:
    """The endpoint-type check for a trace-edge item; None = no objection.
    Missing endpoints and unknown relations fall through to the FK / SQL-CHECK paths
    (which already report them precisely)."""
    rule = RELATION_RULES.get(cols.get("relation"))
    if rule is None:
        return None
    types = {}
    for side in ("from_id", "to_id"):
        row = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?",
                           (cols.get(side),)).fetchone()
        if row is None:
            return None  # unknown endpoint: the IGNORE/rowcount path names it
        types[side] = row[0]
    relation = cols["relation"]
    if rule == "SAME_TYPE":
        if types["from_id"] != types["to_id"]:
            return (f"relation {relation!r} requires matching endpoint types; got "
                    f"{types['from_id']} ({cols['from_id']}) -> "
                    f"{types['to_id']} ({cols['to_id']})")
        return None
    from_ok, to_ok = rule
    if ((from_ok is None or types["from_id"] in from_ok)
            and (to_ok is None or types["to_id"] in to_ok)):
        return None
    return (f"relation {relation!r} does not allow {types['from_id']} -> "
            f"{types['to_id']} ({cols['from_id']} -> {cols['to_id']}); allowed from: "
            f"{', '.join(sorted(from_ok)) if from_ok else 'any'}; allowed to: "
            f"{', '.join(sorted(to_ok)) if to_ok else 'any'} — use 'relates_to' for "
            "an untyped association")

# (type_id, label, id_prefix, generation_class) — seeded into entity_types at create.
BASELINE_ENTITY_TYPES = [
    ("requirement", "Requirement (FR-/NFR-)", "FR-", "Always"),
    ("constraint", "Constraint", "CON-", "Always"),
    ("invariant", "Invariant", "INV-", "Conditional"),
    ("assumption", "Assumption", "ASM-", "Always"),
    ("dependency", "Dependency", "DEP-", "Conditional"),
    ("open-question", "Open question", "OQ-", "Always"),
    ("decision", "Decision", "DEC-", "Always"),
    ("adr", "Architecture Decision Record", "ADR-", "Conditional"),
    ("risk", "Risk", "RISK-", "Always"),
    ("hypothesis", "Hypothesis", "HYP-", "Conditional"),
    ("experiment", "Experiment", "EXP-", "Conditional"),
    ("poc", "Proof of concept", "POC-", "Conditional"),
    ("test", "Test", "TEST-", "Conditional"),
    ("kpi", "KPI", "KPI-", "Conditional"),
    ("stakeholder", "Stakeholder", "STK-", "Conditional"),
    ("phase", "Phase", "PH-", "Always"),
    ("milestone", "Milestone", "MS-", "Conditional"),
    ("slice", "Slice", "SL-", "Conditional"),
    ("wbs-item", "Work item", "WBS-", "Conditional"),
    ("acceptance-criterion", "Acceptance criterion", "AC-", "Always"),
    ("audit-verdict", "Audit verdict", "AV-", "Continuous"),
    ("progress-entry", "Progress entry", "PE-", "Continuous"),
    ("defect", "Defect", "DEF-", "Conditional"),
    ("deferred-work", "Deferred work", "DW-", "Conditional"),
    ("execution-gate", "Execution gate", "GATE-", "Conditional"),
    ("execution-plan", "Execution plan (per slice)", "EP-", "Conditional"),
    ("convention", "Durable convention", "CONV-", "Conditional"),
    ("scope-change", "Scope change", "SC-", "Continuous"),
    ("waiver", "Readiness waiver", "WVR-", "Conditional"),
    ("narrative-document", "Narrative document", "DOC-", "Always"),
    ("document-section", "Document section", "SEC-", "Always"),
    ("diagram", "Diagram", "DIA-", "Conditional"),
    # ("prompt", …) removed in v3.0.0 — see the ENTITY_TABLES note above.
    ("glossary-term", "Glossary term (extension example)", "GT-", "On-request"),
]

# G-COMPLETE-style placeholder screen (content tier — stays outside the schema).
_PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|\bTBD\b|\bFIXME\b|<placeholder>|\{\{[^}]*\}\}|lorem ipsum", re.IGNORECASE
)
# v4 (plan 031): the first-class ambiguity marker — spec-kit's forbidden-to-assume
# idea, tamheed-native: a marker is LEGAL only when it cites an existing, UNRESOLVED
# open question. Anything else (no id, dangling id, resolved OQ) fails G-COMPLETE.
_MARKER_RE = re.compile(r"\[NEEDS-CLARIFICATION(?::\s*([A-Za-z]+-\d+))?[^\]]*\]",
                        re.IGNORECASE)


def _scan_markers(conn) -> list[dict]:
    """Every [NEEDS-CLARIFICATION…] marker in prose columns; `invalid` is None for a
    legal marker (cites an existing unresolved OQ), else the operator-facing reason."""
    found = []
    for table in ENTITY_TABLES.values():
        text_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")
                     if (r[2] or "").upper() == "TEXT" and r[1] != "custom_attributes"]
        if not text_cols:
            continue
        pk = _NON_ID_TABLES.get(table, "id")
        for row in conn.execute(f"SELECT {pk}, {', '.join(text_cols)} FROM {table}"):
            for col, value in zip(text_cols, row[1:]):
                if not value:
                    continue
                for m in _MARKER_RE.finditer(str(value)):
                    cited = (m.group(1) or "").upper()
                    invalid = None
                    if not cited.startswith("OQ-"):
                        invalid = ("marker cites no OQ id — write"
                                   " [NEEDS-CLARIFICATION: OQ-NNN] and create the OQ")
                    else:
                        oq = conn.execute(
                            "SELECT resolution, resolved_by, lifecycle_status"
                            " FROM open_questions WHERE id = ?", (cited,)).fetchone()
                        if oq is None:
                            invalid = f"{cited} does not exist"
                        elif oq[0] is not None or oq[1] is not None:
                            invalid = f"{cited} is resolved — remove the marker"
                        elif oq[2] in ("Superseded", "Obsolete", "Rejected"):
                            invalid = f"{cited} is {oq[2]} — remove or re-cite"
                    found.append({"id": row[0], "column": col,
                                  "oq": cited or None, "invalid": invalid})
    return found
# G-INJECT-style screen on handoff emission. Stored text is data; these patterns catch
# text that tries to become instructions when a downstream agent reads it.
_INJECT_RE = re.compile(
    r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions"
    r"|disregard\s+(?:your|the|all)\s+[^.\n]{0,40}instructions"
    r"|you\s+are\s+now\s+(?:a|an|the)\b"
    r"|<\s*/?\s*system\s*>"
    r"|\bdo\s+not\s+(?:tell|inform)\s+the\s+user\b",
    re.IGNORECASE,
)

_UTC = _dt.timezone.utc


def _now() -> str:
    return _dt.datetime.now(_UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _err(message: str, **extra) -> dict:
    return {"ok": False, "error": message, **extra}


def _need_open():
    if _CURRENT is None:
        return _err("no package open — call package_create or package_open first")
    return None


def _commit() -> dict | None:
    """Write-back via the store; a tree that moved underneath the session is refused
    loudly (C31/C1) and the pending batch is rolled back so it cannot ride a LATER
    commit. Returns an error dict to surface, or None on success."""
    try:
        _CURRENT.commit()
    except store.StoreStaleError as exc:
        _CURRENT.conn.rollback()
        return _err(f"{exc} — the batch was NOT applied; close the package, reconcile "
                    "data/ via git, then reopen and retry")
    return None


def _columns(table: str) -> list[str]:
    return [r[1] for r in _CURRENT.conn.execute(f"PRAGMA table_info({table})")]


def _next_id(prefix: str, table: str, width: int = 3) -> str:
    # C31 (A1): MAX over the parsed NUMBER, never `ORDER BY id DESC` — text order agrees
    # with numeric order only below 1000 ("PE-999" > "PE-1000" as text), so the old form
    # permanently re-allocated PE-1000 once an executed package crossed 999 rows. CAST
    # absorbs a non-numeric suffix a caller-supplied id may have slipped in; MAX over an
    # empty set is NULL, which also covers the empty-table case.
    row = _CURRENT.conn.execute(
        f"SELECT MAX(CAST(SUBSTR(id, ?) AS INTEGER)) FROM {table} WHERE id GLOB ?",
        (len(prefix) + 1, prefix + "*"),
    ).fetchone()
    return f"{prefix}{(row[0] or 0) + 1:0{width}d}"


# --------------------------------------------------------------------------- package tools

def package_create(name: str, title: str, profile: str, mode: str = "full") -> dict:
    """Create a new package under the package root and open it (takes the lock)."""
    global _CURRENT, _CURRENT_NAME
    if _CURRENT is not None:
        return _err(f"package '{_CURRENT_NAME}' is already open — package_close it first")
    if not _NAME_RE.match(name):
        return _err(f"invalid package name {name!r} (kebab-case, [a-z0-9-])")
    pkg_dir = PACKAGE_ROOT / name
    if (pkg_dir / "data").exists():
        return _err(f"package '{name}' already exists — use package_open")
    try:
        s = store.PackageStore(pkg_dir).__enter__()
    except store.StoreLockedError as exc:
        return _err(str(exc))
    try:
        s.conn.executemany(
            "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
            " VALUES (?, ?, ?, ?)",
            BASELINE_ENTITY_TYPES,
        )
        s.conn.execute(
            "INSERT INTO packages (name, title, profile, mode, package_version, created_at)"
            " VALUES (?, ?, ?, ?, '4.0.0', ?)",
            (name, title, profile, mode, _now()),
        )
        s.commit()
    except Exception as exc:
        s.__exit__(None, None, None)
        return _err(f"create failed: {exc}")
    _CURRENT, _CURRENT_NAME = s, name
    # v3.0.0 (plan 027): <package>/prompts/ is the Stage-20 authoring surface — it
    # exists from birth, seeded with the stock scenario library.
    library = _emit_prompt_library(pkg_dir, name)
    return {"ok": True, "package": name, "dir": str(pkg_dir),
            "package_root": str(Path(PACKAGE_ROOT).resolve()),
            "prompt_library": library}


def _strip_identical_h1(title: str, body: str) -> str:
    # C27 (D1): the composition rule (`# {title}` prepended) is invisible to prompt
    # authors — strip an in-body H1 only when identical; a DIFFERENT H1 is preserved.
    head, _, rest = body.lstrip("\n").partition("\n")
    return rest.lstrip("\n") if head.strip() == f"# {title}" else body


def _filter_jsonl(path: Path, keep) -> list[str]:
    """Drop lines failing `keep(parsed_row)`; surviving lines stay byte-identical.
    Empty result deletes the file (CANONICAL: empty table = no file). Returns dropped
    lines (raw)."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    kept, dropped = [], []
    for line in lines:
        if line.strip() and not keep(json.loads(line)):
            dropped.append(line)
        else:
            kept.append(line)
    if not dropped:
        return []
    if any(line.strip() for line in kept):
        path.write_text("".join(kept), encoding="utf-8", newline="\n")
    else:
        path.unlink()
    return dropped


def _convert_legacy_prompts(pkg_dir: Path) -> dict | None:
    """v3.0.0 (plan 027, migration 003): turn a legacy data/prompts.jsonl into
    <package>/prompts/*.md files, ONCE, loudly — or abort the open on ANY anomaly
    (parse error, content collision) with the package untouched. The source is renamed
    to prompts.jsonl.converted (audit trail; escapes the *.jsonl fingerprint/dump
    globs), PRM- trace edges and the 'prompt' registry/omission rows are scrubbed
    (they would FK-fail against a schema without the table). Raises ValueError with
    the operator-facing message on refusal."""
    legacy = pkg_dir / "data" / "prompts.jsonl"
    if not legacy.exists():
        return None
    rows = []
    for lineno, line in enumerate(
            legacy.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            raise ValueError(
                f"data/prompts.jsonl:{lineno} unparseable — conversion aborted, "
                "package NOT opened; fix the line or move the file aside") from None
    out_dir = pkg_dir / "prompts"
    planned: list[tuple[Path, str, str, str]] = []
    collisions: list[str] = []
    for row in rows:
        pid, kind = row.get("id", "PRM-?"), row.get("prompt_kind", "prompt")
        title, body = row.get("title", ""), _strip_identical_h1(
            row.get("title", ""), row.get("body", ""))
        # No timestamp: deterministic content (idempotent re-open, stable goldens);
        # the conversion moment lives in the package_open report.
        provenance = (f"<!-- converted from data/prompts.jsonl {pid} (kind: {kind}, "
                      f"phase_id: {row.get('phase_id')}) by tamheed 3.0.0 -->")
        content = f"{provenance}\n# {title}\n\n{body}\n"
        dest = out_dir / f"{pid.lower()}-{kind}.md"
        if dest.exists() and dest.read_text(encoding="utf-8") != content:
            collisions.append(f"prompts/{dest.name}")
        planned.append((dest, content, pid, kind))
    if collisions:
        raise ValueError(
            "conversion collision: " + ", ".join(collisions) +
            " exist(s) with different content — resolve and re-open")
    converted, warnings, curation = [], [], []
    out_dir.mkdir(parents=True, exist_ok=True)
    for dest, content, pid, kind in planned:
        dest.write_text(content, encoding="utf-8", newline="\n")
        converted.append(f"prompts/{dest.name}")
        # Plan 028 (C34): the per-kind curation hint ships AT conversion too — the
        # standing converted_prompts report in handoff_emit repeats it thereafter.
        curation.append({"file": f"prompts/{dest.name}", "kind": kind,
                         "hint": _converted_hint(kind)})
        if m := _INJECT_RE.search(content):
            warnings.append({"file": f"prompts/{dest.name}",
                             "pattern": m.group(0)[:60]})
    edges_path = pkg_dir / "data" / "trace_edges.jsonl"
    removed_edges = []
    if edges_path.exists():
        removed_edges = [
            json.loads(line) for line in _filter_jsonl(
                edges_path,
                lambda r: not (str(r.get("from_id", "")).startswith("PRM-")
                               or str(r.get("to_id", "")).startswith("PRM-")))]
    for fname, key in (("entity_types.jsonl", "type_id"), ("omissions.jsonl",
                                                          "entity_type")):
        path = pkg_dir / "data" / fname
        if path.exists():
            _filter_jsonl(path, lambda r, k=key: r.get(k) != "prompt")
    legacy.rename(legacy.with_suffix(".jsonl.converted"))
    return {"prompts_converted": converted, "curation": curation,
            "source_renamed": "data/prompts.jsonl.converted",
            "trace_edges_removed": [
                [e.get("from_id"), e.get("to_id"), e.get("relation")]
                for e in removed_edges],
            "inject_warnings": warnings}


def _stored_package_version(pkg_dir: Path) -> str | None:
    """Read package_version straight from data/packages.jsonl (no store open)."""
    path = pkg_dir / "data" / "packages.jsonl"
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                return str(json.loads(line).get("package_version"))
            except ValueError:
                return None
    return None


def package_open(name: str) -> dict:
    """Open an existing package (takes the single-writer lock). v4 (plan 031): a
    pre-v4 package is REFUSED, never silently upgraded — migration is explicit."""
    global _CURRENT, _CURRENT_NAME
    if _CURRENT is not None:
        return _err(f"package '{_CURRENT_NAME}' is already open — package_close it first")
    pkg_dir = PACKAGE_ROOT / name
    if not (pkg_dir / "data").exists():
        return _err(f"package '{name}' not found under {PACKAGE_ROOT}")
    stored = _stored_package_version(pkg_dir)
    if stored is not None and not stored.startswith("4."):
        return _err(
            f"package '{name}' is a v{stored} store — this server is v4 and does not"
            " open it. Back the package up first (git commit, or copy data/), then run"
            " package_migrate(name=…) for a preview and"
            " package_migrate(name=…, confirm=true) to convert. The migration keeps a"
            " copy of the old files in data-v3-backup/.")
    try:
        s = store.PackageStore(pkg_dir).__enter__()
    except store.StoreLockedError as exc:
        return _err(str(exc))
    _CURRENT, _CURRENT_NAME = s, name
    return {"ok": True, "package": name,
            "package_root": str(Path(PACKAGE_ROOT).resolve())}


def package_close() -> dict:
    """Write back canonical text and release the lock."""
    global _CURRENT, _CURRENT_NAME
    if _CURRENT is None:
        return _err("no package open")
    # C31 (C1): a stale tree must not TRAP the session — the close still releases the
    # lock, but skips the final flush (every refused write was already reported "NOT
    # applied" at write time, so nothing unreported is discarded).
    err = _commit()
    _CURRENT.__exit__(None, None, None)
    name, _CURRENT, _CURRENT_NAME = _CURRENT_NAME, None, None
    if err:
        return {"ok": True, "package": name, "flushed": False,
                "warning": f"closed WITHOUT the final flush — {err['error']}"}
    return {"ok": True, "package": name}


# --------------------------------------------------------------------------- entity tools

def entity_upsert(entities: list[dict]) -> dict:
    """Batch upsert (one transaction, all-or-nothing). Each item: {'type': ..., <columns>}.

    Send FULL rows, even when updating an existing entity: the upsert's INSERT half
    evaluates NOT NULL on omitted columns BEFORE conflict resolution, so a partial
    {'id', 'statement'} update of an existing row fails on e.g. title NOT NULL.
    Returns per-item verdicts; a violated constraint is named in the item's error.
    JSON columns (custom_attributes) accept either a JSON string or a JSON
    object/array — objects are serialized at binding (C28: a raw dict used to fail
    the whole batch with sqlite's opaque "type 'dict' is not supported").
    """
    if guard := _need_open():
        return guard
    if not isinstance(entities, list) or not entities:
        return _err("entities must be a non-empty array")
    conn = _CURRENT.conn
    results, failed = [], False
    conn.execute("SAVEPOINT batch")
    for i, item in enumerate(entities):
        etype = item.get("type")
        table = ENTITY_TABLES.get(etype)
        if table is None:
            results.append({"index": i, "ok": False,
                            "error": f"unknown entity type {etype!r} — one of: "
                                     f"{', '.join(sorted(ENTITY_TABLES))}"})
            failed = True
            continue
        # "force" is the transition-guard override (plan 027), never a column.
        force = bool(item.get("force"))
        cols = {k: v for k, v in item.items() if k not in ("type", "force")}
        unknown = set(cols) - set(_columns(table))
        if unknown:
            results.append({"index": i, "ok": False,
                            "error": f"unknown columns for {etype}: {sorted(unknown)}"})
            failed = True
            continue
        forced_note = None
        if (etype in ("phase", "slice") and cols.get("id")
                and cols.get("lifecycle_status") == "Implemented"):
            # Plan 027 (maintainer decision): declaring a phase/slice DONE is guarded
            # by the blocking readiness rules. Transition-edge detection: a full-row
            # re-upsert of an ALREADY-Implemented row must not re-fire (entity_upsert
            # requires FULL rows even for updates). Rejected/Obsolete/… are never
            # guarded — only the success-terminal status is a claim of completion.
            current = conn.execute(f"SELECT lifecycle_status FROM {table} WHERE id = ?",
                                   (cols["id"],)).fetchone()
            if current is None or current[0] != "Implemented":
                rep = _readiness_report(conn, etype, cols["id"])
                blockers = [r for r in rep["rules"]
                            if r["severity"] == "blocking" and r["status"] == "fail"]
                if blockers and not force:
                    detail = "; ".join(
                        f"{r['rule']}: {', '.join(r['entities'][:5])}"
                        + (f" (+{len(r['entities']) - 5} more)"
                           if len(r["entities"]) > 5 else "")
                        for r in blockers)
                    results.append({
                        "index": i, "ok": False, "id": cols["id"],
                        "error": f"readiness: {cols['id']} cannot transition to"
                                 f" Implemented — {detail} — resolve the blockers, or"
                                 " re-run this item with \"force\": true after EXPLICIT"
                                 " operator confirmation"})
                    failed = True
                    continue
                if blockers:  # forced past blocking failures: the record is automatic
                    forced_note = "; ".join(
                        f"{r['rule']} ({len(r['entities'])})" for r in blockers)
        names = list(cols)
        if etype == "trace-edge":
            # Plan 027: endpoint-type rules, HARD on new writes. Same-batch endpoints
            # are visible (the entity_index triggers fire per statement).
            if msg := _relation_rule_error(conn, cols):
                results.append({"index": i, "ok": False, "id": None, "error": msg})
                failed = True
                continue
        if etype in ("trace-edge", "omission"):
            sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        elif etype in ("progress-entry", "audit-verdict"):
            # C31 (A4): the journal is APPEND-ONLY — no ON CONFLICT path, so writing an
            # existing id errors instead of silently rewriting recorded history.
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        else:
            updates = ", ".join(f"{c} = excluded.{c}" for c in names if c != "id")
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})"
                   + (f" ON CONFLICT(id) DO UPDATE SET {updates}" if updates else ""))
        conn.execute(f"SAVEPOINT item{i}")
        try:
            cur = conn.execute(sql, [json.dumps(v, ensure_ascii=False)
                                     if isinstance(v, (dict, list)) else v
                                     for v in (cols[c] for c in names)])
            conn.execute(f"RELEASE item{i}")
            if etype in ("trace-edge", "omission") and cur.rowcount == 0:
                # C31 (A3): IGNORE dropped the row — distinguish the idempotent
                # duplicate (fine, the reason IGNORE exists) from a constraint
                # rejection (an attempt is not a write and must not count as one).
                pk = (("from_id", "to_id", "relation") if etype == "trace-edge"
                      else ("entity_type",))
                exists = conn.execute(
                    f"SELECT 1 FROM {table} WHERE "
                    + " AND ".join(f"{c} = ?" for c in pk),
                    [cols.get(c) for c in pk]).fetchone()
                if exists:
                    results.append({"index": i, "ok": True, "unchanged": True,
                                    "id": cols.get("id")})
                else:
                    results.append({"index": i, "ok": False, "id": cols.get("id"),
                                    "error": "row rejected by a constraint "
                                             "(CHECK/NOT NULL) — not written"})
                    failed = True
            else:
                res = {"index": i, "ok": True, "id": cols.get("id")}
                if forced_note:
                    # The permanent record of a forced close does not depend on the
                    # agent remembering to write one — the server appends it, inside
                    # the same transaction as the transition itself.
                    pe_id = _next_id("PE-", "progress_entries")
                    conn.execute(
                        "INSERT INTO progress_entries (id, event_type, entry,"
                        " subject_id, actor, occurred_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (pe_id, "forced-override",
                         f"FORCED transition: {cols['id']} -> Implemented past"
                         f" blocking readiness failures ({forced_note}) —"
                         " operator-confirmed override",
                         cols.get("id"), "system:transition-guard", _now()))
                    res["forced"] = True
                    res["forced_audit"] = pe_id
                results.append(res)
        except Exception as exc:  # IntegrityError carries the constraint name
            conn.execute(f"ROLLBACK TO item{i}")
            msg = str(exc)
            if "NOT NULL constraint failed" in msg and cols.get("id") is not None:
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE id = ?",
                                      (cols["id"],)).fetchone()
                if exists:  # field-evidence C11 (D2): name the actual cause
                    msg += (" — the row exists; entity_upsert requires FULL rows even for"
                            " updates (INSERT evaluates NOT NULL before conflict resolution)")
            if (etype in ("progress-entry", "audit-verdict")
                    and "UNIQUE constraint failed" in msg):
                msg += (" — append-only journal: append a new entry via progress_update /"
                        " audit_record instead of editing history; corrections are"
                        " recorded as new entries")
            results.append({"index": i, "ok": False, "id": cols.get("id"), "error": msg})
            failed = True
    if failed:
        conn.execute("ROLLBACK TO batch")
        conn.execute("RELEASE batch")
        return {"ok": False, "applied": 0,
                "error": "batch rolled back — one or more items violated constraints",
                "items": results}
    conn.execute("RELEASE batch")
    if err := _commit():
        return err
    # C31 (A3): `applied` counts WRITES, not attempts — ignored duplicates are ok
    # per-item (`unchanged`) but never counted as applied.
    return {"ok": True,
            "applied": sum(1 for r in results if r["ok"] and not r.get("unchanged")),
            "items": results}


def entity_query(type: str, id: str | None = None, status: str | None = None,
                 columns: list[str] | None = None, limit: int = 100) -> dict:
    """Query one entity family with targeted columns — rows, not documents."""
    if guard := _need_open():
        return guard
    table = ENTITY_TABLES.get(type)
    if table is None:
        return _err(f"unknown entity type {type!r} — one of: "
                f"{', '.join(sorted(ENTITY_TABLES))}")
    if type in ("trace-edge", "omission"):
        # C31 (A2): write-only is not nonexistent — the old "unknown entity type"
        # message here sent a false statement into a package's permanent record.
        return _err(f"entity type {type!r} is write-only (composite key, no id column)"
                    " — writable via entity_upsert; query edges via trace_query")
    all_cols = _columns(table)
    cols = columns or all_cols
    if bad := set(cols) - set(all_cols):
        return _err(f"unknown columns: {sorted(bad)}")
    where, params = [], []
    if id is not None:
        where.append("id = ?"); params.append(id)
    if status is not None:
        status_col = ("lifecycle_status" if "lifecycle_status" in all_cols
                      else "status" if "status" in all_cols else None)
        if status_col is None:
            return _err(f"{type} has no status column")
        where.append(f"{status_col} = ?"); params.append(status)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    # `total` alongside the LIMIT'd rows (field-evidence C17: limit=100 silently
    # truncated a 218-row family and the caller had no way to know).
    total = _CURRENT.conn.execute(
        f"SELECT COUNT(*) FROM {table}{where_sql}", params).fetchone()[0]
    sql = f"SELECT {', '.join(cols)} FROM {table}{where_sql} ORDER BY id LIMIT {int(limit)}"
    rows = [dict(zip(cols, r)) for r in _CURRENT.conn.execute(sql, params)]
    return {"ok": True, "rows": rows, "count": len(rows), "total": total}


def trace_query(entity_id: str, direction: str = "both", relation: str | None = None) -> dict:
    """Traverse trace_edges: what does this entity link to / what depends on it?"""
    if guard := _need_open():
        return guard
    if direction not in ("out", "in", "both"):
        return _err("direction must be out | in | both")
    clauses, params = [], []
    if direction in ("out", "both"):
        clauses.append("from_id = ?"); params.append(entity_id)
    if direction in ("in", "both"):
        clauses.append("to_id = ?"); params.append(entity_id)
    sql = f"SELECT from_id, to_id, relation FROM trace_edges WHERE ({' OR '.join(clauses)})"
    if relation is not None:
        sql += " AND relation = ?"; params.append(relation)
    edges = [{"from": f, "to": t, "relation": r}
             for f, t, r in _CURRENT.conn.execute(sql, params)]
    return {"ok": True, "edges": edges, "count": len(edges)}


# --------------------------------------------------------------------------- gates

def gate_run() -> dict:
    """Run the mechanical gates. Plan 027: the referential gates VERIFY at gate time
    (the old hardcoded "enforced at write time" literals asserted integrity the gate
    never checked); coverage gates are the SQL views; the content tier is a
    placeholder scan here."""
    if guard := _need_open():
        return guard
    conn = _CURRENT.conn
    # G-IDS: run the FK check + entity_index<->tables consistency NOW, both directions.
    fk_failures = [f"{table} row {rowid} -> {parent}" for table, rowid, parent, _
                   in conn.execute("PRAGMA foreign_key_check")]
    index_failures = []
    checked_ids = 0
    for etype, table in ENTITY_TABLES.items():
        if table in _NON_ID_TABLES:
            continue  # write-only families have no id column
        for (missing,) in conn.execute(
                f"SELECT id FROM {table}"
                " WHERE id NOT IN (SELECT id FROM entity_index)"):
            index_failures.append(f"{missing} in {table} but not in entity_index")
        for (orphan,) in conn.execute(
                "SELECT id FROM entity_index WHERE entity_type = ?"
                f" AND id NOT IN (SELECT id FROM {table})", (etype,)):
            index_failures.append(f"{orphan} in entity_index but not in {table}")
        checked_ids += conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    ids_failures = fk_failures + index_failures
    # G-DEC-STATUS / G-REQ-SRC: cheap real SELECTs. The trim() catches whitespace-only
    # provenance the DDL CHECK (source_span <> '') structurally misses.
    dec_failures = [f"{row[0]}: {row[1]!r}" for row in conn.execute(
        "SELECT id, lifecycle_status FROM decisions WHERE lifecycle_status NOT IN"
        " ('Proposed','Approved','Rejected','Superseded','Deferred','Implemented')")]
    src_failures = [row[0] for row in conn.execute(
        "SELECT id FROM requirements WHERE source_kind IS NULL"
        " OR source_span IS NULL OR trim(source_span) = ''")]
    report = {
        "G-IDS": {"status": "fail" if ids_failures else "pass",
                  "failures": ids_failures,
                  "note": f"verified now: foreign_key_check clean, entity_index"
                          f" consistent ({checked_ids} ids)" if not ids_failures
                          else "verified now: referential integrity violated"},
        "G-DEC-STATUS": {"status": "fail" if dec_failures else "pass",
                         "failures": dec_failures,
                         "note": "verified now (also DDL CHECK-enforced at write time)"},
        "G-REQ-SRC": {"status": "fail" if src_failures else "pass",
                      "failures": src_failures,
                      "note": "verified now: NULL/whitespace-only provenance caught"
                              " (the DDL CHECK misses whitespace-only)"},
    }
    for gate, view in (("G-TRACE", "g_trace_failures"), ("G-SET", "g_set_failures"),
                       ("G-PROGRESS", "g_progress_failures")):
        failures = [r[0] for r in conn.execute(f"SELECT * FROM {view}")]
        report[gate] = {"status": "fail" if failures else "pass", "failures": failures}
    # Vacuous-pass tripwire (field-evidence C14, D-017-1): g_trace_failures filters on
    # mvp=1, so zero MVP rows makes G-TRACE pass over an empty set. Warning only —
    # adopt-mode packages are all-mvp=0 by design; `ready` semantics unchanged.
    mvp_rows = conn.execute("SELECT COUNT(*) FROM requirements WHERE mvp = 1").fetchone()[0]
    if mvp_rows == 0:
        report["G-TRACE"]["warning"] = (
            "0 MVP requirements — G-TRACE passed vacuously; set mvp=1 on the MVP set "
            "(expected only for adopt-mode or pre-scoping packages)")
    # v4 (plan 031): the SAME tripwire for G-PROGRESS — with zero verdicts anywhere the
    # view is globally gated off and passes over ACs nobody ever audited.
    verdict_rows = conn.execute("SELECT COUNT(*) FROM audit_verdicts").fetchone()[0]
    active_acs = conn.execute("SELECT COUNT(*) FROM acceptance_criteria"
                              " WHERE retired_in IS NULL").fetchone()[0]
    if verdict_rows == 0 and active_acs:
        report["G-PROGRESS"]["warning"] = (
            f"0 audit verdicts — G-PROGRESS passed vacuously over {active_acs} active"
            " AC(s); every one of them is unverified (expected only pre-execution)")
    findings = []
    for table in ENTITY_TABLES.values():
        text_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")
                     if (r[2] or "").upper() == "TEXT" and r[1] != "custom_attributes"]
        # custom_attributes is exempt (C14): it is provenance preserved verbatim, not
        # authored content — grading it fails the package for being faithful. The
        # G-INJECT screen still applies to it at handoff_emit.
        if not text_cols:
            continue
        pk = _NON_ID_TABLES.get(table, "id")
        for row in conn.execute(f"SELECT {pk}, {', '.join(text_cols)} FROM {table}"):
            for col, value in zip(text_cols, row[1:]):
                # strip_code first — parity with the retired v1 gate (D-017-4, C14):
                # `TODO`/{{...}} inside code spans is example text, not an unfinished marker.
                if value and _PLACEHOLDER_RE.search(_strip_code(str(value))):
                    findings.append({"id": row[0], "column": col})
    # v4 (plan 031): NEEDS-CLARIFICATION markers are legal ONLY when they cite an
    # existing unresolved OQ — a dangling/uncited/resolved-cite marker is an
    # unfinished marker like any other. Valid markers do NOT fail (they are the
    # honest record of a known ambiguity; the open-markers readiness advisory counts
    # them).
    for marker in _scan_markers(conn):
        if marker["invalid"]:
            findings.append({"id": marker["id"], "column": marker["column"],
                             "marker": marker["invalid"]})
    report["G-COMPLETE"] = {"status": "fail" if findings else "pass", "failures": findings}
    evidenced, narrated = conn.execute(
        "SELECT SUM(CASE WHEN evidence IS NOT NULL AND evidence <> '' THEN 1 ELSE 0 END),"
        " SUM(CASE WHEN evidence IS NULL OR evidence = '' THEN 1 ELSE 0 END)"
        " FROM audit_verdicts"
    ).fetchone()
    report["audit_evidence"] = {"evidenced": evidenced or 0, "narrated": narrated or 0,
                                "note": "narrated verdicts are the graded party grading itself (C7)"}
    # v4 (plan 031): the stored-edge sweep is a BLOCKING gate. Safe because every v4
    # package starts rule-clean — the migrate tool retypes violating edges to
    # relates_to at conversion, entity_upsert rejects them at write time, and adopt
    # reports them at adoption.
    mistyped = _edge_rule_violations(conn)
    report["G-REL"] = {
        "status": "pass" if not mistyped else "fail", "mistyped": mistyped,
        "note": "stored edges must satisfy RELATION_RULES; retype a wrong edge to"
                " relates_to (delete + re-add) if the link itself is real"}
    # Plan 028 (C34 §7, the FR-156..159 class): requirements created during execution
    # never get wired — work_bind stamps commits, it does not create trace edges, and
    # G-TRACE only sees mvp=1 matrix rows. Advisory on the habitual every-session
    # surface so a new unwired requirement surfaces within a session of being created.
    unwired = [r[0] for r in conn.execute(
        "SELECT id FROM requirements WHERE retired_in IS NULL"
        " AND id NOT IN (SELECT from_id FROM trace_edges)"
        " AND id NOT IN (SELECT to_id FROM trace_edges) ORDER BY id")]
    report["requirements_unwired"] = {
        "status": "advisory", "requirements": unwired,
        "note": "non-retired requirements with ZERO trace edges — wire derives_from/"
                "implements/tests in the session that creates them; never fails the"
                " gate"}
    ready = all(v.get("status") == "pass" for k, v in report.items() if k.startswith("G-"))
    return {"ok": True, "ready": ready, "gates": report}


# --------------------------------------------------------------------------- readiness

def _readiness_report(conn, scope: str, scope_id: str | None) -> dict:
    """The lifecycle-readiness rule engine (plan 027, maintainer note 8): "is this
    phase/slice/release actually DONE?" — the semantic layer above gate_run's
    mechanical floor. Blocking severities are maintainer-locked (interview
    2026-08-13, revised plan 031): pre-approval decisions/ADRs, ACs not latest-Met,
    open CRITICAL/HIGH defects (medium/low advise — every real gate regime
    severity-thresholds), undischarged risks; judgment-dependent items stay advisory.
    v4: a WVR- waiver row satisfies a named rule for a named entity (or the whole
    rule) — reported as `waived`, never silent; expired waivers are surfaced and
    ignored. `Review` (done-claimed) counts as OPEN everywhere — only verified
    Implemented closes work. Declared execution_gates rows surface as human_required —
    prose definitions are NEVER machine-evaluated."""
    rules: list[dict] = []
    today = _now()[:10]
    waivers, expired_waivers = {}, []
    for wid, wrule, applies, expires in conn.execute(
            "SELECT id, rule, applies_to, expires FROM waivers ORDER BY id"):
        if expires is not None and str(expires)[:10] < today:
            expired_waivers.append({"waiver": wid, "rule": wrule,
                                    "applies_to": applies, "expired": expires})
        else:
            waivers.setdefault(wrule, []).append((wid, applies))

    def rule(name: str, severity: str, entities: list, note: str,
             na: str | None = None, extra: str | None = None) -> None:
        entry = {"rule": name, "severity": severity,
                 "status": "fail" if entities else "pass",
                 "entities": entities, "note": note + (na or "") + (extra or "")}
        if entities and name in waivers:
            waived, remaining = [], []
            whole_rule = [wid for wid, applies in waivers[name] if applies is None]
            per_entity = {applies: wid for wid, applies in waivers[name]
                          if applies is not None}
            for ent in entities:
                if whole_rule:
                    waived.append({"entity": ent, "waiver": whole_rule[0]})
                elif ent in per_entity:
                    waived.append({"entity": ent, "waiver": per_entity[ent]})
                else:
                    remaining.append(ent)
            if waived:
                entry["waived"] = waived
                entry["entities"] = remaining
                if not remaining:
                    entry["status"] = "waived"
        if na:
            # C34 §4: a rule firing on ALL rows is indistinguishable from a rule
            # measuring nothing — say so. Severity is NOT downgraded (maintainer-locked:
            # an unpopulated column is itself a package deficiency). `extra` carries
            # blind-spot counts WITHOUT the flag (partial population still
            # discriminates).
            entry["discriminating"] = False
            if not entities:
                # C35/N3: a vacuous pass is not "verified clean" — the rule measured
                # nothing. `indeterminate` is a loud amber; `ready` and the transition
                # guard trip only on real "fail" (maintainer decision, non-blocking).
                entry["status"] = "indeterminate"
        rules.append(entry)

    def ids(sql: str, params: tuple = ()) -> list:
        return [r[0] for r in conn.execute(sql, params)]

    def na_note(table: str, column: str) -> str | None:
        total, populated = conn.execute(
            f"SELECT COUNT(*), COUNT({column}) FROM {table}").fetchone()
        if total and not populated:
            return (f" — 0 of {total} {table} rows have {column} set; this rule "
                    f"cannot discriminate (populate {column} to make it meaningful)")
        return None

    def unlocated_defects_note(scope_name: str) -> str | None:
        (n,) = conn.execute(
            "SELECT COUNT(*) FROM defects"
            " WHERE lifecycle_status IN ('Open','In-progress')"
            " AND found_in IS NULL").fetchone()
        if n:
            return (f" — {n} open defect(s) have no found_in and are INVISIBLE to "
                    f"{scope_name} scope")
        return None

    if scope == "package":
        rule("decisions-approved", "blocking",
             ids("SELECT id FROM decisions WHERE lifecycle_status = 'Proposed'"),
             "a closed package cannot rest on proposed decisions")
        rule("adrs-approved", "blocking",
             ids("SELECT id FROM adrs WHERE lifecycle_status IN ('Draft','Proposed')"),
             "ADRs left pre-approval — approve, reject, or supersede")
        rule("acs-met", "blocking",
             ids("SELECT ac.id FROM acceptance_criteria ac"
                 " LEFT JOIN v_latest_verdicts lv ON lv.ac_id = ac.id"
                 " WHERE ac.retired_in IS NULL"
                 " AND (lv.verdict IS NULL OR lv.verdict <> 'Met')"),
             "every active AC's LATEST verdict must be Met (verdicts append —"
             " an old Met does not survive a newer Not-met)")
        rule("defects-closed", "blocking",
             ids("SELECT id FROM defects WHERE lifecycle_status IN ('Open','In-progress')"
                 " AND severity IN ('critical','high')"),
             "open critical/high defects: fix, disposition, or convert to deferred-work"
             " (scope-change first if it changes scope)")
        rule("defects-minor", "advisory",
             ids("SELECT id FROM defects WHERE lifecycle_status IN ('Open','In-progress')"
                 " AND severity IN ('medium','low')"),
             "open medium/low defects — carrying them is legal, silence is not"
             " (plan 031: severity-thresholded blocking)")
        rule("risks-discharged", "blocking",
             ids("SELECT id FROM risks WHERE risk_state IN ('open','materialized')"
                 " AND discharged_by IS NULL"),
             "open/materialized risks with no discharging AC/test",
             na=na_note("risks", "discharged_by"))
        rule("deferred-work-reviewed", "advisory",
             ids("SELECT id FROM deferred_work"
                 " WHERE lifecycle_status IN ('Open','Activated','Scheduled')"),
             "activation triggers are prose — a human judges whether each fired")
        rule("open-questions-resolved", "advisory",
             ids("SELECT id FROM open_questions WHERE resolved_by IS NULL"),
             "unresolved open questions at close — resolve or carry deliberately",
             na=na_note("open_questions", "resolved_by"))
        rule("execution-plans-approved", "advisory",
             ids("SELECT id FROM execution_plans WHERE lifecycle_status NOT IN"
                 " ('Approved','Implemented','Superseded','Obsolete')"),
             "execution plans never approved")
        rule("requirements-wired", "advisory",
             ids("SELECT id FROM requirements WHERE retired_in IS NULL"
                 " AND id NOT IN (SELECT from_id FROM trace_edges)"
                 " AND id NOT IN (SELECT to_id FROM trace_edges)"),
             "requirements with zero trace edges — execution-created rows never wired"
             " (work_bind stamps commits, it does not wire traceability)")
        # ---- v4 liveness advisories (plan 031: registers stay alive because the
        # engine nags, not because columns exist) ----
        rule("decisions-look-architectural", "advisory",
             ids("SELECT DISTINCT d.id FROM decisions d"
                 " WHERE d.promoted_to IS NULL"
                 " AND d.lifecycle_status IN ('Approved','Implemented')"
                 " AND (EXISTS (SELECT 1 FROM trace_edges e WHERE e.to_id = d.id"
                 "              AND e.relation IN ('implements','satisfies'))"
                 "   OR EXISTS (SELECT 1 FROM trace_edges e"
                 "              JOIN entity_index x ON x.id = CASE WHEN e.from_id = d.id"
                 "                   THEN e.to_id ELSE e.from_id END"
                 "              WHERE (e.from_id = d.id OR e.to_id = d.id)"
                 "              AND x.entity_type IN ('invariant','constraint')))"
                 " ORDER BY d.id"),
             "DECs that work items implement or that touch invariants/constraints,"
             " never promoted — apply the one-way-door test (hard to reverse, broad"
             " blast radius => promote to an ADR)")
        rule("scope-changes-merged", "advisory",
             ids("SELECT id FROM scope_changes WHERE lifecycle_status = 'Approved'"),
             "approved scope changes whose deltas never merged into the plan rows —"
             " apply the scope_adds/scope_modifies/scope_removes edges' intent via"
             " entity_upsert, then set the SC- row to Merged")
        rule("open-questions-overdue", "advisory",
             ids("SELECT id FROM open_questions WHERE resolved_by IS NULL"
                 " AND resolution IS NULL AND due_by IS NOT NULL AND due_by < ?",
                 (today,)),
             "open questions past their due_by — answer, re-date, or escalate",
             na=na_note("open_questions", "due_by"))
        rule("risk-liveness", "advisory",
             ids("SELECT id FROM risks WHERE risk_state IN ('open','materialized')"
                 " AND (probability = 'high' OR impact = 'high')"
                 " AND (owner IS NULL OR response_strategy IS NULL)"),
             "open high-probability/high-impact risks missing an owner or response"
             " strategy — no owner means nobody monitors (the register-rot finding)",
             na=na_note("risks", "owner"))
        rule("assumptions-current", "advisory",
             ids("SELECT id FROM assumptions WHERE validation_date IS NOT NULL"
                 " AND validation_date < ? AND lifecycle_status NOT IN"
                 " ('Rejected','Superseded','Obsolete')", (today,)),
             "assumptions past their validation date — re-validate, or escalate the"
             " invalidated ones to risks (assumptions decay)",
             na=na_note("assumptions", "validation_date"))
        rule("hypotheses-measurable", "advisory",
             ids("SELECT id FROM hypotheses WHERE lifecycle_status NOT IN"
                 " ('Draft','Rejected','Superseded','Obsolete')"
                 " AND (metric IS NULL OR threshold IS NULL)"),
             "hypotheses past Draft without a metric + threshold — the number is"
             " decided BEFORE the experiment runs (anti-confirmation-bias)")
        rule("acs-slice-bound", "advisory",
             ids("SELECT id FROM acceptance_criteria WHERE retired_in IS NULL"
                 " AND slice_id IS NULL"),
             "active ACs bound to no slice — INVISIBLE to phase/slice exit views and"
             " scoped readiness; bind them or accept package-scope-only verification")
        markers = [f"{m['id']}.{m['column']} -> {m['oq']}"
                   for m in _scan_markers(conn) if not m["invalid"]]
        rule("clarifications-open", "advisory", markers,
             "open [NEEDS-CLARIFICATION: OQ-…] markers in prose fields — each cites a"
             " live OQ; resolve the OQ and remove the marker")
        gate_where, gate_params = "applies_to IS NULL", ()
    elif scope == "phase":
        rule("acs-met", "blocking",
             ids("SELECT ac.id FROM acceptance_criteria ac"
                 " JOIN slices s ON ac.slice_id = s.id"
                 " LEFT JOIN v_latest_verdicts lv ON lv.ac_id = ac.id"
                 " WHERE s.phase_id = ? AND ac.retired_in IS NULL"
                 " AND (lv.verdict IS NULL OR lv.verdict <> 'Met')", (scope_id,)),
             "ACs of this phase's slices whose latest verdict is not Met")
        rule("slices-closed", "blocking",
             ids("SELECT id FROM slices WHERE phase_id = ? AND retired_in IS NULL"
                 " AND lifecycle_status NOT IN"
                 " ('Implemented','Superseded','Obsolete','Rejected')", (scope_id,)),
             "slices of this phase not closed")
        rule("wbs-done", "blocking",
             ids("SELECT w.id FROM wbs_items w"
                 " LEFT JOIN slices s ON w.slice_id = s.id"
                 " WHERE (w.phase_id = ? OR s.phase_id = ?)"
                 " AND w.lifecycle_status NOT IN"
                 " ('Implemented','Superseded','Obsolete','Rejected')",
                 (scope_id, scope_id)),
             "open work items in this phase")
        found_na = na_note("defects", "found_in")
        rule("defects-closed", "blocking",
             ids("SELECT d.id FROM defects d"
                 " WHERE d.lifecycle_status IN ('Open','In-progress')"
                 " AND d.severity IN ('critical','high')"
                 " AND (d.found_in = ? OR d.found_in IN"
                 " (SELECT id FROM slices WHERE phase_id = ?))", (scope_id, scope_id)),
             "open critical/high defects found in this phase or its slices",
             na=found_na, extra=None if found_na else unlocated_defects_note("phase"))
        rule("defects-minor", "advisory",
             ids("SELECT d.id FROM defects d"
                 " WHERE d.lifecycle_status IN ('Open','In-progress')"
                 " AND d.severity IN ('medium','low')"
                 " AND (d.found_in = ? OR d.found_in IN"
                 " (SELECT id FROM slices WHERE phase_id = ?))", (scope_id, scope_id)),
             "open medium/low defects in this phase — carry deliberately or fix")
        # v4: no milestones rule — MS- is a roadmap label with no lifecycle (plan 031);
        # a milestone that gates is an execution_gate.
        gate_where, gate_params = "applies_to = ?", (scope_id,)
    else:  # slice
        rule("acs-met", "blocking",
             ids("SELECT ac.id FROM acceptance_criteria ac"
                 " LEFT JOIN v_latest_verdicts lv ON lv.ac_id = ac.id"
                 " WHERE ac.slice_id = ? AND ac.retired_in IS NULL"
                 " AND (lv.verdict IS NULL OR lv.verdict <> 'Met')", (scope_id,)),
             "ACs bound to this slice whose latest verdict is not Met")
        rule("wbs-done", "blocking",
             ids("SELECT id FROM wbs_items WHERE slice_id = ?"
                 " AND lifecycle_status NOT IN"
                 " ('Implemented','Superseded','Obsolete','Rejected')", (scope_id,)),
             "open work items in this slice")
        found_na = na_note("defects", "found_in")
        rule("defects-closed", "blocking",
             ids("SELECT id FROM defects WHERE found_in = ?"
                 " AND lifecycle_status IN ('Open','In-progress')"
                 " AND severity IN ('critical','high')", (scope_id,)),
             "open critical/high defects found in this slice", na=found_na,
             extra=None if found_na else unlocated_defects_note("slice"))
        rule("defects-minor", "advisory",
             ids("SELECT id FROM defects WHERE found_in = ?"
                 " AND lifecycle_status IN ('Open','In-progress')"
                 " AND severity IN ('medium','low')", (scope_id,)),
             "open medium/low defects in this slice — carry deliberately or fix")
        rule("execution-plan-approved", "advisory",
             ids("SELECT id FROM execution_plans WHERE slice_id = ?"
                 " AND lifecycle_status NOT IN"
                 " ('Approved','Implemented','Superseded','Obsolete')", (scope_id,)),
             "this slice's execution plan was never approved")
        gate_where, gate_params = "applies_to = ?", (scope_id,)
    # v4: all four gate kinds surface ('ready' was silently dropped through v3 — a
    # recorded DoR gate the operator never saw), plus the latest Go/Hold/Redirect/Kill
    # outcome when one was recorded (gate-decision PE- events carry the history).
    human_required = [
        {"gate": gid, "gate_kind": kind, "definition": definition, "outcome": outcome}
        for gid, kind, definition, outcome in conn.execute(
            "SELECT id, gate_kind, definition, outcome FROM execution_gates"
            f" WHERE {gate_where} ORDER BY id", gate_params)]
    ready = not any(r["severity"] == "blocking" and r["status"] == "fail"
                    for r in rules)
    out = {"scope": scope, "id": scope_id, "ready": ready, "rules": rules,
           "human_required": human_required}
    if expired_waivers:
        out["expired_waivers"] = expired_waivers
    return out


def readiness_check(scope: str = "package", id: str | None = None) -> dict:
    """Deep lifecycle-state validation at a close boundary: is this package/phase/slice
    actually DONE? Read-only reporting; the same blocking rules also guard the
    phase/slice -> 'Implemented' transition in entity_upsert (force + operator
    confirmation to override). human_required lists declared execution_gates whose
    prose definitions a human must confirm (recorded via progress_update)."""
    if guard := _need_open():
        return guard
    if scope not in ("package", "phase", "slice"):
        return _err(f"unknown scope {scope!r} — one of package, phase, slice")
    conn = _CURRENT.conn
    if scope == "package":
        scope_id = None
    else:
        if not id:
            return _err(f"scope {scope!r} requires an id (e.g. "
                        f"{'PH-1' if scope == 'phase' else 'SL-001'})")
        table = "phases" if scope == "phase" else "slices"
        if conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (id,)).fetchone() is None:
            return _err(f"unknown {scope} id {id!r}")
        scope_id = id
    return {"ok": True, **_readiness_report(conn, scope, scope_id)}


# --------------------------------------------------------------------------- execution loop

def progress_update(entries: list[dict]) -> dict:
    """Append progress entries (batch, one transaction). Item: {'entry', 'event_type'?,
    'subject_id'?, 'actor'?, 'corrects'?, 'phase_id'?, 'slice_id'?}.

    v4 (plan 031): events are TYPED — event_type from {work-done, verdict-recorded,
    transition, forced-override, gate-decision, escalation, correction, note}
    (default 'note', the deliberate escape hatch: the vocabulary never blocks a
    write). subject_id names the entity the event is about; actor follows the
    human:<name> | agent:<session> | system:<component> convention; `corrects`
    points at an earlier PE- — journals are corrected by compensating events, never
    edited."""
    if guard := _need_open():
        return guard
    if not isinstance(entries, list) or not entries:
        return _err("entries must be a non-empty array")
    conn = _CURRENT.conn
    ids = []
    try:
        for e in entries:
            pe_id = _next_id("PE-", "progress_entries")
            conn.execute(
                "INSERT INTO progress_entries (id, event_type, entry, subject_id,"
                " actor, corrects, phase_id, slice_id, occurred_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (pe_id, e.get("event_type", "note"), e.get("entry"),
                 e.get("subject_id"), e.get("actor"), e.get("corrects"),
                 e.get("phase_id"), e.get("slice_id"), _now()),
            )
            ids.append(pe_id)
    except Exception as exc:
        conn.rollback()
        return _err(str(exc))
    if err := _commit():
        return err
    return {"ok": True, "ids": ids}


def audit_record(verdicts: list[dict]) -> dict:
    """Record AC verdicts (batch). Item: {'ac_id', 'verdict', 'evidence'?,
    'verified_by'?, 'verification_method'?, 'against_commit'?}.

    Evidence refs (test file, CI run id) make the verdict evidenced rather than
    narrated (C7). v4 (plan 031): say WHO rendered it (human|agent|ci), HOW
    (auto-test|manual|inspection), and against WHAT commit — a Met the readiness
    engine can audit is worth more than a Met it must take on faith. The requirement
    auto-advance trigger cascades in the same transaction (C4), on LATEST-verdict
    semantics."""
    if guard := _need_open():
        return guard
    if not isinstance(verdicts, list) or not verdicts:
        return _err("verdicts must be a non-empty array")
    conn = _CURRENT.conn
    iteration = conn.execute("SELECT iteration FROM packages LIMIT 1").fetchone()
    ids = []
    try:
        for v in verdicts:
            av_id = _next_id("AV-", "audit_verdicts")
            conn.execute(
                "INSERT INTO audit_verdicts (id, ac_id, verdict, evidence,"
                " verified_by, verification_method, against_commit, iteration,"
                " recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (av_id, v.get("ac_id"), v.get("verdict"), v.get("evidence"),
                 v.get("verified_by"), v.get("verification_method"),
                 v.get("against_commit"),
                 iteration[0] if iteration else 1, _now()),
            )
            ids.append(av_id)
    except Exception as exc:
        conn.rollback()
        return _err(str(exc))
    if err := _commit():
        return err
    return {"ok": True, "ids": ids}


def work_bind(ref: str, entity_ids: list[str], note: str | None = None) -> dict:
    """Record that a commit/PR satisfies the named entities (C3) and stamp last_referenced —
    the cheap binding surface that keeps requirement IDs from staying planning ornaments."""
    if guard := _need_open():
        return guard
    if not entity_ids:
        return _err("entity_ids must be a non-empty array")
    conn = _CURRENT.conn
    stamped, now = [], _now()
    # C31 (C2): one transactional unit — any failure past the first UPDATE used to
    # leave pending last_referenced stamps that rode whatever the NEXT tool call did.
    try:
        for eid in entity_ids:
            row = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?",
                               (eid,)).fetchone()
            if row is None:
                conn.rollback()
                return _err(f"unknown entity id {eid!r}")
            table = ENTITY_TABLES.get(row[0])
            if table is None:
                conn.rollback()
                return _err(f"entity id {eid!r} has unmapped type {row[0]!r}")
            if "last_referenced" in _columns(table):
                conn.execute(f"UPDATE {table} SET last_referenced = ? WHERE id = ?",
                             (now, eid))
            stamped.append(eid)
        pe_id = _next_id("PE-", "progress_entries")
        conn.execute(
            "INSERT INTO progress_entries (id, entry, occurred_at, custom_attributes)"
            " VALUES (?, ?, ?, ?)",
            (pe_id, note or f"{ref} satisfies {', '.join(stamped)}", now,
             json.dumps({"ref": ref, "binds": stamped})),
        )
    except Exception as exc:
        conn.rollback()
        return _err(str(exc))
    if err := _commit():
        return err
    return {"ok": True, "bound": stamped, "progress_entry": pe_id}


# --------------------------------------------------------------------------- handoff

_PROMPTS_DIR = _SERVER_DIR.parent / "prompts"

# v1-flow patterns for the cutover stale-reference scan (C19). Precision matters: the bare
# word "Keystone" is NEVER matched alone — real projects use it as a product/domain term
# (ACMP's "Keystone optional" feature, ADR-0007 lesson).
_STALE_PATTERNS = [
    (re.compile(r"validate_package\.py"),
     "run gate_run via the tamheed MCP tools instead of the v1 validator"),
    (re.compile(r"keystone-state\.json"),
     "the package IS the state — query it with entity_query/trace_query"),
    (re.compile(r"docs/handoff/"),
     "prompts live in <package>/prompts/ (v3.0.0) — point there instead"),
    (re.compile(r"Keystone (?:v1|package|register|validator|tree)", re.IGNORECASE),
     "the v1 tree is a frozen archive; the Tamheed package is the record"),
    (re.compile(r"progress-log\.md|acceptance-audit\.md"),
     "v1 hand-edited artifacts — record via progress_update/audit_record instead"),
]


def _managed_emit(path: Path, content: str, force: bool = False) -> str:
    """Managed emission (field-evidence C20): every file Tamheed emits goes through this.
    Returns "emitted" | "unchanged" | "diverged". MEMORYLESS by design: "diverged" means
    the on-disk file differs from what would be emitted NOW — that covers operator hand
    edits AND legitimate source changes (superseded PRM row, plugin upgrade). Both refuse
    without force: safe-by-default, never a silent clobber."""
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return "unchanged"
        if not force:
            return "diverged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "emitted"


def _emit_prompt_library(pkg_dir: Path, name: str, force: bool = False) -> dict:
    """Copy the bundled scenario prompts into <package>/prompts/ (C19; the library lives
    with the package). Deterministic: static content, {package} substitution only."""
    out_dir = pkg_dir / "prompts"
    result: dict[str, list[str]] = {"emitted": [], "unchanged": [], "diverged": []}
    for src in sorted(_PROMPTS_DIR.glob("*.md")):
        text = src.read_text(encoding="utf-8").replace("{package}", name)
        status = _managed_emit(out_dir / src.name, text, force=force)
        result[status].append(f"prompts/{src.name}")
    return result


def _stale_reference_report(target: Path) -> list[dict]:
    findings = []
    for fname in ("CLAUDE.md", "AGENTS.md"):
        path = target / fname
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, suggestion in _STALE_PATTERNS:
                if pattern.search(line):
                    findings.append({"file": fname, "line": lineno,
                                     "text": line.strip()[:160],
                                     "suggestion": suggestion})
                    break
    return findings


# Restated-register signals (C22): the hazard is UNLABELED restatement of package content
# in agent-control files — it drifts silently. Labeled snapshots (blocks that already
# reference entity_query/review.html/gate_run) get "verify currency" guidance instead.
_ID_LED_LINE_RE = re.compile(r"^\s*(?:-\s*\*\*|\|\s*)([A-Z]{2,5})-\d")
_AUDIT_TALLY_RE = re.compile(r"\d+\s+Met\b.*\d+\s+(?:Partial|Not-met|Pending)")
_PKG_REF_RE = re.compile(r"entity_query\(|review\.html|gate_run")
_PREFIX_TYPE = {p.rstrip("-"): tid for tid, _label, p, _cls in BASELINE_ENTITY_TYPES}


def _restated_findings(label: str, lines: list[str]) -> list[dict]:
    """The C22 detectors over one file's lines (plan 028: also run over package prompt
    files — a hard-coded tally in a prompt drifts exactly like one in AGENTS.md).
    Anti-false-positive bounds unchanged: tally needs the word Met; blocks need >=3
    consecutive id-led lines."""
    findings = []

    def labeled(start: int, end: int) -> bool:
        lo = max(0, start - 3)
        return any(_PKG_REF_RE.search(lines[i]) for i in range(lo, end))

    run_start, run_prefixes = None, []
    for i, line in enumerate(lines + [""]):  # sentinel flushes a trailing run
        m = _ID_LED_LINE_RE.match(line)
        if m and m.group(1) in _PREFIX_TYPE:
            if run_start is None:
                run_start = i
            run_prefixes.append(m.group(1))
        else:
            if run_start is not None and len(run_prefixes) >= 3:
                prefix = max(set(run_prefixes), key=run_prefixes.count)
                tid = _PREFIX_TYPE[prefix]
                kind = ("labeled-snapshot" if labeled(run_start, i) else "unlabeled")
                suggestion = (
                    f'labeled snapshot of {tid} rows — verify it is still current '
                    f'(quoted register content drifts silently); the live form is '
                    f'`entity_query("{tid}")` / review.html#registers'
                    if kind == "labeled-snapshot" else
                    f'replace the restated {tid} rows with a reference: '
                    f'`entity_query("{tid}")` — full text in review.html#registers')
                findings.append({"file": label, "line": run_start + 1,
                                 "family": tid, "count": len(run_prefixes),
                                 "kind": kind, "suggestion": suggestion})
            run_start, run_prefixes = None, []
        if _AUDIT_TALLY_RE.search(line):
            kind = ("labeled-snapshot" if labeled(i, i + 1) else "unlabeled")
            findings.append({
                "file": label, "line": i + 1, "family": "audit-verdict", "count": 1,
                "kind": kind,
                "suggestion": "a hard-coded audit tally goes stale on the first new "
                              "verdict — the live form is gate_run()'s audit_evidence "
                              "split / review.html#execution"})
    return findings


def _restated_content_report(target: Path) -> list[dict]:
    findings = []
    for fname in ("CLAUDE.md", "AGENTS.md"):
        path = target / fname
        if path.exists():
            findings += _restated_findings(
                fname, path.read_text(encoding="utf-8").splitlines())
    return findings


# ------------------------------------------------------- converted-prompt lifecycle
# Plan 028 (C34): a converted legacy prompt is PROJECT content preserved verbatim —
# ~50-70% restated generic workflow the stock library now covers, interleaved with
# unique project knowledge. The tool never deletes or renames; it says which question
# to ask, per KIND (deterministic — no content-similarity heuristics), until the
# operator curates (removes the header line or the file).
_CONVERTED_RE = re.compile(
    r"^<!-- converted from data/prompts\.jsonl (PRM-\S+) \(kind: ([a-z-]+)")
_CONVERTED_HINTS = {
    "initial": "generic half now covered by package-onboarding.md/slice-kickoff.md; "
               "keep only project-specific content (and check any restated state for "
               "staleness)",
    "follow-up": "generic half now covered by orient-resume/replan-deferred/"
                 "slice-review; keep project-specific cautions",
    "review": "generic half now covered by integrity-check/slice-review; keep "
              "project-specific checklists",
}
_CONVERTED_CURATE = ("curate = extract the project-specific half into a purpose-named "
                     "prompt (or keep as-is) and remove this header line once "
                     "reviewed — this hint clears itself")


def _converted_hint(kind: str) -> str:
    return (f"{_CONVERTED_HINTS.get(kind, 'review against the stock library')}; "
            f"{_CONVERTED_CURATE}")


def _normalized_prompt(text: str) -> str:
    """Content identity across the conversion delta: drop the provenance header,
    normalize trailing whitespace (the v2 handoff copy and the converted package file
    share the same H1-strip composition, so this is the only legitimate difference)."""
    lines = [ln for ln in text.splitlines()
             if not ln.startswith("<!-- converted from data/prompts.jsonl")]
    return "\n".join(ln.rstrip() for ln in lines).strip()


_STALE_BLOCK_RE = re.compile(
    r"\n?<!-- tamheed:stale-warning -->.*?<!-- /tamheed:stale-warning -->\n?", re.S)

# Plan 027: the operating note's managed span (any version — v-bump = an update).
_NOTE_BLOCK_RE = re.compile(r"<!-- tamheed:note v\d+ -->.*?<!-- /tamheed:note -->", re.S)


def handoff_emit(target_dir: str, subdir: str = "handoff", force: bool = False) -> dict:
    """Wire the target project to the package: .mcp.json (standalone installs) + the
    CLAUDE.md operating note. v3.0.0 (plan 027): prompts are NOT copied into the
    target — <package>/prompts/ is the single source (stock scenario library +
    project-authored kickoff prompts, all plain .md the operator reads and picks).
    Emission is blocked if the injection screen finds instruction-shaped text in any
    package prompt file. Reports stale v1 references AND restated register content
    found in the target's CLAUDE.md/AGENTS.md."""
    if guard := _need_open():
        return guard
    target = Path(target_dir)
    if not target.is_dir():
        return _err(f"target_dir {target_dir!r} is not an existing directory")
    if subdir != "handoff":  # kept in the signature for MCP-schema stability only
        return _err("subdir removed in v3.0.0 — prompts live in <package>/prompts/ "
                    "and are no longer copied into the target")
    pkg_dir = PACKAGE_ROOT / _CURRENT_NAME
    library = _emit_prompt_library(pkg_dir, _CURRENT_NAME, force=force)
    stock = {p.name for p in _PROMPTS_DIR.glob("*.md")}
    prompts_dir = pkg_dir / "prompts"
    prompt_files = sorted(prompts_dir.glob("*.md")) if prompts_dir.exists() else []
    project = [p.name for p in prompt_files if p.name not in stock]
    if not project:
        return _err("no project-authored prompts in <package>/prompts/ — write the "
                    "kickoff prompt file(s) there first (Stage 20; adopted packages: "
                    "author at least a kickoff prompt)")
    # G-INJECT, relocated to the file substrate (v3.0.0): scan EVERY package prompt —
    # project-authored AND stock (stock scanning is free and catches tampering).
    findings = []
    for path in prompt_files:
        if m := _INJECT_RE.search(path.read_text(encoding="utf-8")):
            findings.append({"file": f"prompts/{path.name}",
                             "pattern": m.group(0)[:60]})
    if findings:
        return _err("G-INJECT: instruction-shaped text found — emission blocked",
                    gate="G-INJECT", findings=findings)
    emitted: list[str] = []
    unchanged: list[str] = []
    diverged: list[str] = []

    def emit(path: Path, content: str, rel: str) -> None:
        status = _managed_emit(path, content, force=force)
        {"emitted": emitted, "unchanged": unchanged, "diverged": diverged}[status].append(
            rel.replace("\\", "/"))

    # Portable executor config (field-evidence C19): on a plugin install the server path
    # points into the VERSIONED plugin cache — machine- and version-specific, and the
    # installed plugin already registers a server named `tamheed`, so emitting one would
    # double-register. Omit it and say so; standalone installs keep the absolute path.
    resolved = str((_SERVER_DIR / "tamheed_server.py").resolve()).replace("\\", "/")
    plugin_hosted = "/.claude/plugins/" in resolved
    mcp_cfg_path = target / ".mcp.json"
    if not plugin_hosted:
        cfg = (json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
               if mcp_cfg_path.exists() else {})
        cfg.setdefault("mcpServers", {})["tamheed"] = {
            "command": "uv",
            "args": ["run", resolved, "--package-dir", str(PACKAGE_ROOT.resolve())],
        }
        emit(mcp_cfg_path, json.dumps(cfg, indent=2) + "\n", ".mcp.json")

    warnings: list[str] = []
    # Plan 029 (C35/N2): the two kinds of stock divergence — operator customisation vs
    # a template that moved on — are indistinguishable without history; say so and name
    # the zero-machinery per-file acceptance path instead of leaving force blunt-only.
    if library["diverged"]:
        warnings.append(
            f"{len(library['diverged'])} stock prompt(s) differ from the current"
            " template — your customisation or a template update (indistinguishable"
            " without history); to accept the current template for ONE file, delete it"
            " and re-emit; force=True overwrites ALL diverged stock files")
    # v3.0.0: nothing is emitted into handoff/ anymore — leftover v2 copies actively
    # mislead. Plan 028 (C34 §2): the verdict is PER FILE, by content compare — a
    # blanket "delete" would have destroyed a live project prompt that existed nowhere
    # else (the operator had to do this compare by hand; now the tool does).
    leftover_dir = target / "handoff"
    leftovers = sorted(leftover_dir.glob("prm-*.md")) if leftover_dir.exists() else []
    for left in leftovers:
        pkg_copy = prompts_dir / left.name
        verdict = None
        if pkg_copy.exists():
            left_text = left.read_text(encoding="utf-8")
            pkg_text = pkg_copy.read_text(encoding="utf-8")
            if (left_text == pkg_text
                    or _normalized_prompt(left_text) == _normalized_prompt(pkg_text)):
                verdict = (f"handoff/{left.name}: copy of prompts/{left.name} — "
                           "safe to delete")
        if verdict is None:
            verdict = (f"handoff/{left.name}: NOT a copy of any package prompt — MOVE "
                       "it into <package>/prompts/ (deleting would destroy live "
                       "content)")
        warnings.append(verdict)
    # Plan 028: converted legacy prompts get a standing, self-clearing per-kind hint —
    # the conversion report was a one-shot moment already gone for converted packages.
    converted = []
    for path in prompt_files:
        first = path.read_text(encoding="utf-8").split("\n", 1)[0]
        if m := _CONVERTED_RE.match(first):
            converted.append({"file": f"prompts/{path.name}", "id": m.group(1),
                              "kind": m.group(2), "hint": _converted_hint(m.group(2))})
    stale = _stale_reference_report(target)
    # C24/D-8, carried into v3: v1-protocol instructions and dead relative links inside
    # package prompt files (migrated v1 prompts land there) misdirect the kickoff —
    # scan them like the target's agent-control files; never rewrite.
    for path in prompt_files:
        rel = f"prompts/{path.name}"
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            hit = next(((p, s) for p, s in _STALE_PATTERNS if p.search(line)), None)
            if hit:
                stale.append({"file": rel, "line": lineno,
                              "text": line.strip()[:160], "suggestion": hit[1]})
                continue
            for m in re.finditer(r"\]\(((?:\.\.?/)[^)#\s]+)\)", line):
                if not (path.parent / m.group(1)).resolve().exists():
                    stale.append({"file": rel, "line": lineno, "text": m.group(1),
                                  "suggestion": "dead relative link from "
                                                "<package>/prompts/ — fix the path"})
    restated = _restated_content_report(target)
    # Plan 028 (C34): the C22 detectors run over package prompt files too — a converted
    # prompt's hard-coded audit tally had drifted factually wrong with no signal.
    # Advisory only; never blocks emission (that strength stays G-INJECT's alone).
    for path in prompt_files:
        restated += _restated_findings(
            f"prompts/{path.name}", path.read_text(encoding="utf-8").splitlines())

    server_line = ("The `tamheed` MCP server is provided by the installed tamheed plugin "
                   "(no project-level .mcp.json entry needed)." if plugin_hosted else
                   "The `tamheed` MCP server is registered in this project's `.mcp.json`.")
    note_block = (
        "<!-- tamheed:note v3 -->\n\n"
        f"This project executes Tamheed package `{_CURRENT_NAME}` "
        f"(under `{PACKAGE_ROOT.resolve()}`). **The package is the record — when code and "
        "package disagree, fix the code or record a scope change; never let them drift.** "
        "**Package data lives in the git working tree** (C31): uncommitted package writes "
        "are destroyed by `git reset --hard` / `git checkout` / `git stash` exactly like "
        "uncommitted source — commit the package `data/` before branch operations. "
        f"{server_line} All package reads/writes go through the `tamheed` MCP tools; "
        f"ready-made task prompts live in `{_CURRENT_NAME}/prompts/` — start with "
        f"`{_CURRENT_NAME}/prompts/README.md`, the operator guide (which prompt for "
        f"which situation, semi-auto vs fully-auto); the human review surface is "
        f"`{_CURRENT_NAME}/review.html`.\n"
        "\n### Recording obligations (mandatory — unrecorded work is drift)\n\n"
        "| During execution, when… | Record BEFORE moving on |\n"
        "|---|---|\n"
        "| you find a defect | `entity_upsert` a `defect` row (`DEF-`, honest severity —"
        " open critical/high BLOCK readiness) — then fix it |\n"
        "| you find needed work that is out of scope | `entity_upsert` a `deferred-work`"
        " row (`DW-`) with an activation trigger |\n"
        "| you deviate from the approved plan in any way | a `scope-change` row (`SC-`)"
        " FIRST, `decision_ref` naming the deciding `DEC-`/`ADR-`, delta edges"
        " (`scope_adds`/`scope_modifies`/`scope_removes`) naming the affected rows —"
        " after approval, apply the row changes and set the `SC-` to Merged |\n"
        "| you hit genuine ambiguity | an `open-question` row (`OQ-`, with owner +"
        " due_by) and `[NEEDS-CLARIFICATION: OQ-NNN]` at the exact spot — NEVER"
        " assume |\n"
        "| you finish a unit of work | `progress_update(...)` — event_type `work-done`,"
        " `subject_id`, your `actor` string, phase/slice ids |\n"
        "| you believe a slice/wbs-item is complete | set its `lifecycle_status` to"
        " **Review** (done-claimed) — `Implemented` means VERIFIED and is"
        " readiness-guarded |\n"
        "| you verify an acceptance criterion | `audit_record(...)` with evidence +"
        " `verified_by` + `verification_method` + `against_commit` — never Met without"
        " proof |\n"
        "| you create a commit or PR | `work_bind(ref, entity_ids=[...])` |\n"
        "| you declare a slice/phase/release done | `readiness_check(scope)` first —"
        " resolve every blocking failure, or ask the OPERATOR for a `WVR-` waiver"
        " (their words; you never author your own) — `\"force\": true` only on the"
        " operator's explicit words |\n"
        "\nIf you cannot record (lock held, package missing), STOP and tell the"
        " operator — do not proceed unrecorded.\n"
        "\n### Tool cheat-sheet (execution loop)\n\n"
        "- `progress_update(entries=[{entry, event_type?, subject_id?, actor?,"
        " corrects?, phase_id?, slice_id?}])` — append TYPED progress (correct via a"
        " `correction` event, never edit)\n"
        "- `audit_record(verdicts=[{ac_id, verdict: Met|Partial|Not-met|Pending,"
        " evidence?, verified_by?, verification_method?, against_commit?}])` —"
        " evidence ref = evidenced, not narrated\n"
        "- `work_bind(ref, entity_ids=[...], note?)` — stamp a commit/PR onto entities\n"
        "- `entity_query(type, id?, status?, columns?, limit?)` — rows + total\n"
        "- `trace_query(entity_id, direction: out|in|both, relation?)` — typed links\n"
        "- `entity_upsert(entities=[{type, id, ...}])` — FULL rows, even for updates\n"
        "- `gate_run()` — mechanical gate verdict · `readiness_check(scope, id?)` —"
        " is it actually DONE (waivers honored, Review counts open)\n"
        "- `export_html()` — refresh review.html · `server_info()` — version + root\n"
        "<!-- /tamheed:note -->\n")
    note = "\n## Tamheed progress tracking\n" + note_block
    claude_md = target / "CLAUDE.md"
    existing = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    # Marker-managed warning block (C20/B2): rebuilt on EVERY emit — added while the scan
    # finds stale references, REMOVED once it is clean.
    content = _STALE_BLOCK_RE.sub("\n", existing)
    # Plan 027: the operating note is marker-managed too (v1 was append-once and could
    # never receive updates). A v1 note (heading, no markers) has no terminator to
    # bound a safe machine edit — warned, never touched; one manual deletion upgrades.
    note_m = _NOTE_BLOCK_RE.search(content)
    if "## Tamheed progress tracking" not in content:
        content = content + note
    elif note_m is None:
        warnings.append(
            "CLAUDE.md carries the v1 Tamheed operating note — delete the"
            " '## Tamheed progress tracking' section and re-run handoff_emit; the v2"
            " note is marker-managed and self-updates thereafter")
    elif note_m.group(0) != note_block.rstrip("\n"):
        # Plan 029 (C35/N1): the marker-delimited span is TOOL-OWNED and rebuilt on
        # EVERY emit — the stale-warning-block precedent. The v3.1.0 divergence
        # bookkeeping made the documented "self-updates" promise false, and applying
        # the note then required a force that clobbered operator-owned prompt files.
        # A hand edit inside the markers is overwritten — warned, never silent.
        content = content.replace(note_m.group(0), note_block.rstrip("\n"))
        warnings.append(
            "the tamheed:note span in CLAUDE.md was rebuilt — it is tool-owned and"
            " always reflects the current emission; keep operator content OUTSIDE the"
            " <!-- tamheed:note --> markers")
    if stale:
        content += ("\n<!-- tamheed:stale-warning -->\n"
                    "> **Stale v1 references detected** in this project's agent-control "
                    "files — see `stale_references` in the handoff_emit result for "
                    "file:line replacements. Apply them and freeze the v1 tree, then "
                    "re-run handoff_emit: this warning removes itself once the scan is "
                    "clean.\n<!-- /tamheed:stale-warning -->\n")
    if content != existing:
        claude_md.write_text(content, encoding="utf-8", newline="\n")
        emitted.append("CLAUDE.md")
    else:
        unchanged.append("CLAUDE.md")
    return {"ok": True, "written": emitted, "unchanged": unchanged, "diverged": diverged,
            "prompt_library": library, "project_prompts": project,
            "converted_prompts": converted, "stale_references": stale,
            "restated_content": restated, "warnings": warnings}


# --------------------------------------------------------------------------- staged flows & export

def _read_jsonl_tables(data_dir: Path) -> dict[str, list[dict]]:
    """Parse every data/<table>.jsonl into rows, keyed by table name (file stem)."""
    tables: dict[str, list[dict]] = {}
    for path in sorted(data_dir.glob("*.jsonl")):
        rows = []
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                raise ValueError(f"{path.name}:{lineno} unparseable JSON") from None
        tables[path.stem] = rows
    return tables


def package_migrate(name: str, confirm: bool = False) -> dict:
    """Migrate a v2/v3 package IN PLACE to the v4 store shape (staged, operator-gated).

    Default = preview: the full rewrite report (every value coercion, edge retype,
    column drop), nothing written. confirm=True = convert: the old data/ files are
    copied to data-v3-backup/ first, a legacy data/prompts.jsonl becomes
    prompts/*.md (the v3 converter, abort-on-anomaly), rows are transformed
    (migrate_v3to4.transform_tables), and the result is validated + canonicalized
    through a full store round-trip BEFORE it replaces the live files — a package
    that fails v4 integrity is left untouched. Migration is operator-initiated,
    always; package_open refuses pre-v4 stores and names this tool.
    v1 Keystone markdown packages are no longer ingested here — migrate them under
    tamheed 3.2.1 first (docs/migrate-from-keystone.md), then re-run this."""
    import shutil
    import tempfile

    import migrate_v3to4

    if _CURRENT is not None:
        return _err(f"package '{_CURRENT_NAME}' is open — package_close it first")
    pkg_dir = PACKAGE_ROOT / name
    data = pkg_dir / "data"
    if not data.exists():
        return _err(f"package '{name}' not found under {PACKAGE_ROOT}")
    lock = data / store.LOCK_NAME
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return _err(f"package '{name}' is locked ({store._describe_lock(lock)})")
    try:
        conversion = None
        if confirm:
            backup = pkg_dir / "data-v3-backup"
            if backup.exists():
                return _err("data-v3-backup/ already exists — a previous migration ran;"
                            " remove or rename it before migrating again")
            backup.mkdir()
            for f in data.iterdir():
                if f.name != store.LOCK_NAME:
                    shutil.copy2(f, backup / f.name)
            try:
                conversion = _convert_legacy_prompts(pkg_dir)
            except ValueError as exc:
                shutil.rmtree(backup)
                return _err(str(exc))
        try:
            tables = _read_jsonl_tables(data)
        except ValueError as exc:
            return _err(str(exc))
        legacy_note = None
        if not confirm and "prompts" in tables:
            # Preview parity with the confirm path's converter: PRM- rows/edges leave.
            tables.pop("prompts")
            tables["trace_edges"] = [
                e for e in tables.get("trace_edges", [])
                if not (str(e.get("from_id", "")).startswith("PRM-")
                        or str(e.get("to_id", "")).startswith("PRM-"))]
            legacy_note = ("data/prompts.jsonl will be converted to prompts/*.md on"
                           " confirm (the v3 prompt converter, abort-on-anomaly)")
        type_of_table = {tbl: kind for kind, tbl in ENTITY_TABLES.items()
                         if tbl not in _NON_ID_TABLES}
        try:
            tables, rep = migrate_v3to4.transform_tables(tables, RELATION_RULES,
                                                         type_of_table)
        except ValueError as exc:
            return _err(str(exc))
        have = {r.get("type_id") for r in tables.get("entity_types", [])}
        added = [tid for tid, _, _, _ in BASELINE_ENTITY_TYPES if tid not in have]
        for tid, label, prefix, gclass in BASELINE_ENTITY_TYPES:
            if tid in added:
                tables.setdefault("entity_types", []).append(
                    {"type_id": tid, "label": label, "id_prefix": prefix,
                     "generation_class": gclass, "custom_attributes": None})
        if added:
            rep["entity_types_added"] = added
        pe_rows = tables.setdefault("progress_entries", [])
        nxt = max((int(str(r.get("id"))[3:]) for r in pe_rows
                   if str(r.get("id", "")).startswith("PE-")), default=0) + 1
        rewrites = sorted(k for k in rep if k not in ("target_version", "version_from"))
        pe_rows.append({
            "id": f"PE-{nxt:03d}", "event_type": "note",
            "entry": (f"MIGRATED store v{rep.get('version_from')} -> v4.0.0"
                      f" ({', '.join(rewrites) if rewrites else 'no value rewrites'})"),
            "actor": "system:migrate"})
        if legacy_note:
            rep["legacy_prompts"] = legacy_note
        if not confirm:
            return {"ok": True, "stage": "preview", "package": name, "report": rep,
                    "note": "nothing written — back the package up (git commit or"
                            " copy data/), then re-run with confirm=true"}
        # Validate + canonicalize in a scratch store before touching the live files.
        with tempfile.TemporaryDirectory() as td:
            tmp_pkg = Path(td) / "pkg"
            (tmp_pkg / "data").mkdir(parents=True)
            for tname, rows in tables.items():
                if rows:
                    (tmp_pkg / "data" / f"{tname}.jsonl").write_bytes(
                        ("\n".join(json.dumps(r, ensure_ascii=False,
                                              separators=(",", ":")) for r in rows)
                         + "\n").encode("utf-8"))
            try:
                ts = store.PackageStore(tmp_pkg).__enter__()
            except Exception as exc:
                return _err(f"migration validation failed — package UNCHANGED"
                            f" (old files intact, backup at data-v3-backup/): {exc}")
            try:
                ts.commit()
            finally:
                ts.__exit__(None, None, None)
            stale = set(tables) | {p.stem for p in data.glob("*.jsonl")}
            for tname in stale:
                (data / f"{tname}.jsonl").unlink(missing_ok=True)
            for f in (tmp_pkg / "data").glob("*.jsonl"):
                shutil.copy2(f, data / f.name)
        out = {"ok": True, "stage": "migrated", "package": name, "report": rep,
               "backup": "data-v3-backup/",
               "package_root": str(Path(PACKAGE_ROOT).resolve()),
               "note": "review the report, commit the diff, then package_open"}
        if conversion:
            out["legacy_prompts"] = conversion
        out["prompt_library"] = _emit_prompt_library(pkg_dir, name)
        return out
    finally:
        os.close(fd)
        lock.unlink()


def package_adopt(source_dir: str, name: str | None = None, confirm: bool = False) -> dict:
    """Adopt a brownfield repository (staged: scan + dry report by default; confirm=True
    records — Proposed-only, code-provenanced, gap report first-class). See
    references/adopt.md; the four rules are enforced mechanically."""
    import adopt
    out = adopt.run_adoption(source_dir, PACKAGE_ROOT, name=name, confirm=confirm)
    out.setdefault("package_root", str(Path(PACKAGE_ROOT).resolve()))
    if out.get("stage") == "post-flight" and out.get("package_dir"):
        pkg = Path(out["package_dir"])
        out["prompt_library"] = _emit_prompt_library(pkg, pkg.name)
        # v4 (plan 031): adopt writes via raw SQL, bypassing per-write relation
        # enforcement — run the same edge sweep G-REL blocks on, HERE, so an adopted
        # package cannot fail readiness on day one without the operator being told.
        try:
            with store.PackageStore(pkg) as s:
                viol = _edge_rule_violations(s.conn)
            if viol:
                out["relation_rule_violations"] = {
                    "mistyped": viol,
                    "note": "these edges will FAIL the blocking G-REL gate — retype"
                            " to relates_to or fix the endpoints before handoff"}
        except store.StoreLockedError:
            pass  # the adoption report stands; the sweep re-runs at first gate_run
    return out


def export_html(output: str | None = None) -> dict:
    """Export the self-contained static HTML review surface (the human review view).

    Deterministic (same DB state => byte-identical file), so it is COMMITTED to the
    package's repo by default: writes <package>/review.html unless `output` overrides."""
    if guard := _need_open():
        return guard
    import export_html as viewer
    report = gate_run()
    text = viewer.render(_CURRENT.conn, report["gates"], report["ready"])
    path = Path(output) if output else PACKAGE_ROOT / _CURRENT_NAME / "review.html"
    path.write_text(text, encoding="utf-8", newline="\n")
    # C25 (maintainer req 3): per-table CSV beside the report — the viewer's summary
    # links point at csv/<table>.csv relative to review.html. Deterministic (same
    # ordered queries as the tables). C27 (D2): forced like review.html itself —
    # CSVs are DERIVED outputs regenerated from the DB, never operator files; without
    # force a diverged CSV was unrecoverable in-tool. Authored emissions (handoff_emit)
    # keep the refusal path.
    conn = _CURRENT.conn
    csv_dir = path.parent / "csv"
    csv_out: dict[str, list[str]] = {"emitted": [], "unchanged": [], "diverged": []}
    for table in sorted(set(ENTITY_TABLES.values())):
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        order = ("from_id, to_id, relation" if table == "trace_edges"
                 else "entity_type, reason" if table == "omissions"
                 else _NON_ID_TABLES.get(table, "id"))
        rows = conn.execute(
            f"SELECT {', '.join(cols)} FROM {table} ORDER BY {order}").fetchall()
        if not rows:
            continue
        buf = io.StringIO()
        writer = _csv.writer(buf, lineterminator="\n")
        writer.writerow(cols)
        writer.writerows(rows)
        status = _managed_emit(csv_dir / f"{table}.csv", buf.getvalue(), force=True)
        csv_out[status].append(f"csv/{table}.csv")
    return {"ok": True, "path": str(path), "bytes": len(text.encode("utf-8")),
            "csv": csv_out}


def server_info() -> dict:
    """Report server version, resolved package root, and store state.

    Makes startup diagnosable (field-evidence C11: a wedged call and a slow cold start
    were indistinguishable) and gives field reports a citable version anchor (C16)."""
    manifest = _SERVER_DIR.parent / ".claude-plugin" / "plugin.json"
    try:  # single version source: the bundled plugin manifest (D-017-3)
        version = json.loads(manifest.read_text(encoding="utf-8")).get("version", "unknown")
    except (OSError, ValueError):
        version = "unknown"  # standalone copy without the plugin manifest
    migrations = sorted(p.name for p in
                        (_SERVER_DIR.parent / "db" / "migrations").glob("[0-9]*.sql"))
    return {"ok": True, "version": version,
            "package_root": str(Path(PACKAGE_ROOT).resolve()),
            "open_package": _CURRENT_NAME,
            "migrations_head": migrations[-1] if migrations else None,
            # plan 027 (B23): the numeric schema head (PRAGMA user_version contract)
            "schema_version": store.schema_version()}


# --------------------------------------------------------------------------- server plumbing

TOOLS = {
    "server_info": (server_info, "Report server version, resolved package root, store state"),
    "package_create": (package_create, "Create a package under the package root (takes the lock)"),
    "package_open": (package_open, "Open an existing package (takes the single-writer lock)"),
    "package_close": (package_close, "Write back canonical text and release the lock"),
    "entity_upsert": (entity_upsert, "Batch upsert entities in one transaction; per-item verdicts"),
    "entity_query": (entity_query, "Query one entity family with targeted columns"),
    "trace_query": (trace_query, "Traverse typed trace edges from/to an entity"),
    "gate_run": (gate_run, "Run the mechanical quality gates; returns the gate report"),
    "readiness_check": (readiness_check,
                        "Lifecycle readiness at a close boundary (package/phase/slice)"),
    "progress_update": (progress_update, "Append progress entries (execution tracking)"),
    "audit_record": (audit_record, "Record AC verdicts, optionally evidence-bound"),
    "work_bind": (work_bind, "Bind a commit/PR to the entities it satisfies (stamps last_referenced)"),
    "handoff_emit": (handoff_emit, "Emit handoff prompts + executor MCP config (injection-screened)"),
    "package_migrate": (package_migrate, "Migrate a v2/v3 package in place to the v4 store (staged: preview, then confirm)"),
    "package_adopt": (package_adopt, "Adopt a brownfield repo (staged: scan/preview, then confirm)"),
    "export_html": (export_html, "Export the HTML review surface to <package>/review.html"),
}

_SDK_ERROR = ("tamheed MCP server requires the 'mcp' SDK (Python >=3.10): launch with"
              " 'uv run tamheed_server.py' (PEP 723 fetches it) or 'pip install mcp'.")


def _mcp_version() -> str:
    # The module's own __version__ wins (vendored copies describe themselves); the
    # shipped SDK exposes none, so distribution metadata is the usual answer.
    import mcp
    if v := getattr(mcp, "__version__", None):
        return str(v)
    try:
        from importlib.metadata import version
        return version("mcp")
    except Exception:
        return "unknown"


def selftest() -> int:
    print(f"tamheed MCP server — {len(TOOLS)} tools")
    for name, (_, desc) in TOOLS.items():
        print(f"  {name}: {desc}")
    # C33 (ask 4): the broken import was the ONE path no health check touched —
    # report SDK availability without failing (the contract tests run SDK-free by
    # design, and the tool surface itself needs no SDK).
    try:
        from mcp.server.fastmcp import FastMCP  # noqa: F401
        print(f"mcp sdk: ok ({_mcp_version()})")
    except ImportError as exc:
        print(f"mcp sdk: UNAVAILABLE for serving ({exc})")
    return 0


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        # C33 (A2): print the CAUGHT exception and distinguish absent from
        # incompatible — the old hint told the operator to install a package that
        # was already present and was the cause (an hour lost to three confident
        # wrong conclusions; the truth was one printed exception away).
        try:
            import mcp  # noqa: F401
            print(f"tamheed MCP server: mcp {_mcp_version()}"
                  f" is installed but does not provide mcp.server.fastmcp ({exc}) —"
                  " this build requires mcp<2; relaunch with a bounded resolve"
                  " (uv run reads the PEP 723 pin; or pip install 'mcp<2').",
                  file=sys.stderr)
        except ImportError:
            print(f"{_SDK_ERROR} (import failed: {exc})", file=sys.stderr)
        return 1
    app = FastMCP("tamheed")
    for name, (func, desc) in TOOLS.items():
        app.tool(name=name, description=desc)(func)
    app.run()  # stdio transport
    return 0


def main(argv: list[str] | None = None) -> int:
    global PACKAGE_ROOT
    for stream in (sys.stdout, sys.stderr):  # UTF-8 output on legacy Windows code pages
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Tamheed MCP server")
    parser.add_argument("--package-dir", default=None,
                        help="root directory packages live under (default:"
                             " $CLAUDE_PROJECT_DIR, else cwd)")
    parser.add_argument("--selftest", action="store_true", help="list tools and exit")
    args = parser.parse_args(argv)
    # Layered resolution (field-evidence C11): explicit flag > CLAUDE_PROJECT_DIR (the
    # documented stable project root — a stdio server's cwd is NOT guaranteed) > cwd.
    # A literal "${...}" means the host didn't expand the variable: treat as unset.
    package_dir = args.package_dir
    if not package_dir or package_dir.startswith("${"):
        package_dir = os.environ.get("CLAUDE_PROJECT_DIR") or "."
    PACKAGE_ROOT = Path(package_dir).resolve()
    if args.selftest:
        return selftest()
    return serve()


if __name__ == "__main__":
    sys.exit(main())
