# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp"]
# ///
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
sys.path.insert(0, str(_SERVER_DIR.parent / "scripts"))

import store  # plugins/tamheed/db/store.py  # noqa: E402
import validate_package as _vp  # frozen v1 contract: strip_code reuse (D-017-4)  # noqa: E402

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
    "narrative-document": "narrative_documents",
    "document-section": "document_sections",
    "diagram": "diagrams",
    "prompt": "prompts",
    "glossary-term": "glossary_terms",  # community-extension worked example (migration 002)
    "trace-edge": "trace_edges",   # composite PK; write surface for relations
    "omission": "omissions",       # G-SET recorded-omitted rows (entity_type + reason)
}

_NON_ID_TABLES = {"trace_edges": "from_id", "omissions": "entity_type"}

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
    ("narrative-document", "Narrative document", "DOC-", "Always"),
    ("document-section", "Document section", "SEC-", "Always"),
    ("diagram", "Diagram", "DIA-", "Conditional"),
    ("prompt", "Handoff prompt", "PRM-", "Conditional"),
    ("glossary-term", "Glossary term (extension example)", "GT-", "On-request"),
]

# G-COMPLETE-style placeholder screen (content tier — stays outside the schema).
_PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|\bTBD\b|\bFIXME\b|<placeholder>|\{\{[^}]*\}\}|lorem ipsum", re.IGNORECASE
)
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


def _columns(table: str) -> list[str]:
    return [r[1] for r in _CURRENT.conn.execute(f"PRAGMA table_info({table})")]


def _next_id(prefix: str, table: str, width: int = 3) -> str:
    row = _CURRENT.conn.execute(
        f"SELECT id FROM {table} WHERE id GLOB ? ORDER BY id DESC LIMIT 1", (prefix + "*",)
    ).fetchone()
    n = int(row[0][len(prefix):]) + 1 if row else 1
    return f"{prefix}{n:0{width}d}"


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
            " VALUES (?, ?, ?, ?, '2.0.0', ?)",
            (name, title, profile, mode, _now()),
        )
        s.commit()
    except Exception as exc:
        s.__exit__(None, None, None)
        return _err(f"create failed: {exc}")
    _CURRENT, _CURRENT_NAME = s, name
    return {"ok": True, "package": name, "dir": str(pkg_dir),
            "package_root": str(Path(PACKAGE_ROOT).resolve())}


def package_open(name: str) -> dict:
    """Open an existing package (takes the single-writer lock)."""
    global _CURRENT, _CURRENT_NAME
    if _CURRENT is not None:
        return _err(f"package '{_CURRENT_NAME}' is already open — package_close it first")
    pkg_dir = PACKAGE_ROOT / name
    if not (pkg_dir / "data").exists():
        return _err(f"package '{name}' not found under {PACKAGE_ROOT}")
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
    _CURRENT.commit()
    _CURRENT.__exit__(None, None, None)
    name, _CURRENT, _CURRENT_NAME = _CURRENT_NAME, None, None
    return {"ok": True, "package": name}


# --------------------------------------------------------------------------- entity tools

def entity_upsert(entities: list[dict]) -> dict:
    """Batch upsert (one transaction, all-or-nothing). Each item: {'type': ..., <columns>}.

    Send FULL rows, even when updating an existing entity: the upsert's INSERT half
    evaluates NOT NULL on omitted columns BEFORE conflict resolution, so a partial
    {'id', 'statement'} update of an existing row fails on e.g. title NOT NULL.
    Returns per-item verdicts; a violated constraint is named in the item's error.
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
            results.append({"index": i, "ok": False, "error": f"unknown entity type {etype!r}"})
            failed = True
            continue
        cols = {k: v for k, v in item.items() if k != "type"}
        unknown = set(cols) - set(_columns(table))
        if unknown:
            results.append({"index": i, "ok": False,
                            "error": f"unknown columns for {etype}: {sorted(unknown)}"})
            failed = True
            continue
        names = list(cols)
        if etype in ("trace-edge", "omission"):
            sql = (f"INSERT OR IGNORE INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})")
        else:
            updates = ", ".join(f"{c} = excluded.{c}" for c in names if c != "id")
            sql = (f"INSERT INTO {table} ({', '.join(names)})"
                   f" VALUES ({', '.join('?' for _ in names)})"
                   + (f" ON CONFLICT(id) DO UPDATE SET {updates}" if updates else ""))
        conn.execute(f"SAVEPOINT item{i}")
        try:
            conn.execute(sql, [cols[c] for c in names])
            conn.execute(f"RELEASE item{i}")
            results.append({"index": i, "ok": True, "id": cols.get("id")})
        except Exception as exc:  # IntegrityError carries the constraint name
            conn.execute(f"ROLLBACK TO item{i}")
            msg = str(exc)
            if "NOT NULL constraint failed" in msg and cols.get("id") is not None:
                exists = conn.execute(f"SELECT 1 FROM {table} WHERE id = ?",
                                      (cols["id"],)).fetchone()
                if exists:  # field-evidence C11 (D2): name the actual cause
                    msg += (" — the row exists; entity_upsert requires FULL rows even for"
                            " updates (INSERT evaluates NOT NULL before conflict resolution)")
            results.append({"index": i, "ok": False, "id": cols.get("id"), "error": msg})
            failed = True
    if failed:
        conn.execute("ROLLBACK TO batch")
        conn.execute("RELEASE batch")
        return {"ok": False, "applied": 0,
                "error": "batch rolled back — one or more items violated constraints",
                "items": results}
    conn.execute("RELEASE batch")
    _CURRENT.commit()
    return {"ok": True, "applied": len(entities), "items": results}


def entity_query(type: str, id: str | None = None, status: str | None = None,
                 columns: list[str] | None = None, limit: int = 100) -> dict:
    """Query one entity family with targeted columns — rows, not documents."""
    if guard := _need_open():
        return guard
    table = ENTITY_TABLES.get(type)
    if table is None or type in ("trace-edge", "omission"):
        return _err(f"unknown entity type {type!r}")
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
    """Run the mechanical gates. Referential gates are enforced at write time (schema);
    coverage gates are the SQL views; the content tier is a placeholder scan here."""
    if guard := _need_open():
        return guard
    conn = _CURRENT.conn
    report = {
        "G-IDS": {"status": "pass", "note": "enforced at write time (FKs + entity_index)"},
        "G-DEC-STATUS": {"status": "pass", "note": "enforced at write time (CHECK)"},
        "G-REQ-SRC": {"status": "pass", "note": "enforced at write time (NOT NULL provenance)"},
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
                # strip_code first — parity with the frozen v1 gate (D-017-4, C14):
                # `TODO`/{{...}} inside code spans is example text, not an unfinished marker.
                if value and _PLACEHOLDER_RE.search(_vp.strip_code(str(value))):
                    findings.append({"id": row[0], "column": col})
    report["G-COMPLETE"] = {"status": "fail" if findings else "pass", "failures": findings}
    evidenced, narrated = conn.execute(
        "SELECT SUM(CASE WHEN evidence IS NOT NULL AND evidence <> '' THEN 1 ELSE 0 END),"
        " SUM(CASE WHEN evidence IS NULL OR evidence = '' THEN 1 ELSE 0 END)"
        " FROM audit_verdicts"
    ).fetchone()
    report["audit_evidence"] = {"evidenced": evidenced or 0, "narrated": narrated or 0,
                                "note": "narrated verdicts are the graded party grading itself (C7)"}
    ready = all(v.get("status") == "pass" for k, v in report.items() if k.startswith("G-"))
    return {"ok": True, "ready": ready, "gates": report}


# --------------------------------------------------------------------------- execution loop

def progress_update(entries: list[dict]) -> dict:
    """Append progress entries (batch, one transaction). Item: {'entry', 'phase_id'?, 'slice_id'?}."""
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
                "INSERT INTO progress_entries (id, entry, phase_id, slice_id, occurred_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (pe_id, e.get("entry"), e.get("phase_id"), e.get("slice_id"), _now()),
            )
            ids.append(pe_id)
    except Exception as exc:
        conn.rollback()
        return _err(str(exc))
    _CURRENT.commit()
    return {"ok": True, "ids": ids}


def audit_record(verdicts: list[dict]) -> dict:
    """Record AC verdicts (batch). Item: {'ac_id', 'verdict', 'evidence'?}. Evidence refs
    (test file, CI run id) make the verdict evidenced rather than narrated (C7). The
    requirement auto-advance trigger cascades in the same transaction (C4)."""
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
                "INSERT INTO audit_verdicts (id, ac_id, verdict, evidence, iteration, recorded_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (av_id, v.get("ac_id"), v.get("verdict"), v.get("evidence"),
                 iteration[0] if iteration else 1, _now()),
            )
            ids.append(av_id)
    except Exception as exc:
        conn.rollback()
        return _err(str(exc))
    _CURRENT.commit()
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
    for eid in entity_ids:
        row = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?", (eid,)).fetchone()
        if row is None:
            conn.rollback()
            return _err(f"unknown entity id {eid!r}")
        table = ENTITY_TABLES[row[0]]
        if "last_referenced" in _columns(table):
            conn.execute(f"UPDATE {table} SET last_referenced = ? WHERE id = ?", (now, eid))
        stamped.append(eid)
    pe_id = _next_id("PE-", "progress_entries")
    conn.execute(
        "INSERT INTO progress_entries (id, entry, occurred_at, custom_attributes)"
        " VALUES (?, ?, ?, ?)",
        (pe_id, note or f"{ref} satisfies {', '.join(stamped)}", now,
         json.dumps({"ref": ref, "binds": stamped})),
    )
    _CURRENT.commit()
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
     "use the emitted handoff/prm-*.md files and <package>/prompts/ instead"),
    (re.compile(r"Keystone (?:v1|package|register|validator|tree)", re.IGNORECASE),
     "the v1 tree is a frozen archive; the Tamheed package is the record"),
    (re.compile(r"progress-log\.md|acceptance-audit\.md"),
     "v1 hand-edited artifacts — record via progress_update/audit_record instead"),
]


def _emitted_prompt_report(target: Path, subdir: str) -> list[dict]:
    """C24/D-8: emitted prompt bodies (v1-migrated PRM rows) can carry v1-protocol
    instructions and dead relative links written for the old tree depth — the kickoff
    then actively misdirects. Scan them like the agent-control files; never rewrite."""
    findings = []
    base = target / subdir
    for path in (sorted(base.glob("*.md")) if base.exists() else []):
        rel = f"{subdir}/{path.name}".replace("\\", "/")
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            hit = next(((p, s) for p, s in _STALE_PATTERNS if p.search(line)), None)
            if hit:
                findings.append({"file": rel, "line": lineno,
                                 "text": line.strip()[:160], "suggestion": hit[1]})
                continue
            for m in re.finditer(r"\]\(((?:\.\.?/)[^)#\s]+)\)", line):
                if not (path.parent / m.group(1)).resolve().exists():
                    findings.append({
                        "file": rel, "line": lineno, "text": m.group(1),
                        "suggestion": "dead relative link from the emit location — "
                                      "refresh the PRM row to reference the package"})
    return findings


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


def _restated_content_report(target: Path) -> list[dict]:
    findings = []
    for fname in ("CLAUDE.md", "AGENTS.md"):
        path = target / fname
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()

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
                    findings.append({"file": fname, "line": run_start + 1,
                                     "family": tid, "count": len(run_prefixes),
                                     "kind": kind, "suggestion": suggestion})
                run_start, run_prefixes = None, []
            if _AUDIT_TALLY_RE.search(line):
                kind = ("labeled-snapshot" if labeled(i, i + 1) else "unlabeled")
                findings.append({
                    "file": fname, "line": i + 1, "family": "audit-verdict", "count": 1,
                    "kind": kind,
                    "suggestion": "a hard-coded audit tally goes stale on the first new "
                                  "verdict — the live form is gate_run()'s audit_evidence "
                                  "split / review.html#execution"})
    return findings


_STALE_BLOCK_RE = re.compile(
    r"\n?<!-- tamheed:stale-warning -->.*?<!-- /tamheed:stale-warning -->\n?", re.S)


def handoff_emit(target_dir: str, subdir: str = "handoff", force: bool = False) -> dict:
    """Assemble handoff prompts into the target project + write the executor-side MCP
    config (.mcp.json + CLAUDE.md operating note) so the executing agent can record
    progress. Every file is a MANAGED emission: hand-edited files are reported as
    `diverged` and never overwritten without force=true. Also emits the scenario prompt
    library into <package>/prompts/, reports stale v1 references AND restated register
    content found in the target's CLAUDE.md/AGENTS.md.
    Emission is blocked if the injection screen finds instruction-shaped text."""
    if guard := _need_open():
        return guard
    target = Path(target_dir)
    if not target.is_dir():
        return _err(f"target_dir {target_dir!r} is not an existing directory")
    sub = Path(subdir)
    if sub.is_absolute() or ".." in sub.parts:
        return _err(f"subdir {subdir!r} must be a relative path inside the target")
    conn = _CURRENT.conn
    prompts = conn.execute(
        "SELECT id, prompt_kind, title, body FROM prompts ORDER BY id"
    ).fetchall()
    if not prompts:
        return _err("no prompts in package — upsert prompt entities first")
    findings = [{"id": pid, "pattern": m.group(0)[:60]}
                for pid, _, title, body in prompts
                for m in [_INJECT_RE.search(f"{title}\n{body}")] if m]
    if findings:
        return _err("G-INJECT: instruction-shaped text found — emission blocked",
                    gate="G-INJECT", findings=findings)
    handoff = target / sub
    emitted: list[str] = []
    unchanged: list[str] = []
    diverged: list[str] = []

    def emit(path: Path, content: str, rel: str) -> None:
        status = _managed_emit(path, content, force=force)
        {"emitted": emitted, "unchanged": unchanged, "diverged": diverged}[status].append(
            rel.replace("\\", "/"))

    for pid, kind, title, body in prompts:
        emit(handoff / f"{pid.lower()}-{kind}.md", f"# {title}\n\n{body}\n",
             f"{subdir}/{pid.lower()}-{kind}.md")

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

    library = _emit_prompt_library(PACKAGE_ROOT / _CURRENT_NAME, _CURRENT_NAME,
                                   force=force)
    stale = _stale_reference_report(target) + _emitted_prompt_report(target, subdir)
    restated = _restated_content_report(target)

    server_line = ("The `tamheed` MCP server is provided by the installed tamheed plugin "
                   "(no project-level .mcp.json entry needed)." if plugin_hosted else
                   "The `tamheed` MCP server is registered in this project's `.mcp.json`.")
    note = (
        "\n## Tamheed progress tracking\n\n"
        f"This project executes Tamheed package `{_CURRENT_NAME}` "
        f"(under `{PACKAGE_ROOT.resolve()}`). **The package is the record — when code and "
        "package disagree, fix the code or record a scope change; never let them drift.** "
        f"{server_line} All package reads/writes go through the `tamheed` MCP tools; "
        f"ready-made task prompts live in `{_CURRENT_NAME}/prompts/` "
        "(orient-resume, progress-sync, integrity-check, generate-report, slice-review) "
        f"and the human review surface is `{_CURRENT_NAME}/review.html`.\n"
        "\n### Tool cheat-sheet (execution loop)\n\n"
        "- `progress_update(entries=[{entry, phase_id?, slice_id?}])` — append progress\n"
        "- `audit_record(verdicts=[{ac_id, verdict: Met|Partial|Not-met|Pending,"
        " evidence?}])` — evidence ref = evidenced, not narrated\n"
        "- `work_bind(ref, entity_ids=[...], note?)` — stamp a commit/PR onto entities\n"
        "- `entity_query(type, id?, status?, columns?, limit?)` — rows + total\n"
        "- `trace_query(entity_id, direction: out|in|both, relation?)` — typed links\n"
        "- `entity_upsert(entities=[{type, id, ...}])` — FULL rows, even for updates\n"
        "- `gate_run()` — mechanical gate verdict · `export_html()` — refresh review.html\n"
        "- `server_info()` — version + resolved package root (orientation)\n")
    claude_md = target / "CLAUDE.md"
    existing = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    # Marker-managed warning block (C20/B2): rebuilt on EVERY emit — added while the scan
    # finds stale references, REMOVED once it is clean. The operating note itself stays
    # append-once. "Re-run emit to verify the cutover" is thereby self-contained.
    content = _STALE_BLOCK_RE.sub("\n", existing)
    if "## Tamheed progress tracking" not in content:
        content = content + note
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
            "prompt_library": library, "stale_references": stale,
            "restated_content": restated}


# --------------------------------------------------------------------------- staged flows & export

def package_migrate(source_dir: str, name: str | None = None, confirm: bool = False,
                    allow_zero: list[str] | None = None,
                    patch: str | None = None,
                    status_map: dict[str, str] | None = None) -> dict:
    """Migrate a conformant v1 Keystone package into a v2 store (staged, operator-gated).

    Default = stages 1-2 (pre-flight + dry parse report). confirm=True = stages 4-5
    (populate in one transaction + post-flight fidelity). `allow_zero` acknowledges
    named families that legitimately parse to zero; `patch` is a JSON file of
    merge-by-id row overrides applied to the parsed plan before populate (the blessed
    repair path — echoed in the preview); `status_map` maps v1 status words to lifecycle
    values (present the preview's status_coerced proposals to the operator, then pass
    the confirmed map here). See references/migration-v1.md.
    Migration is operator-initiated, always (D-REPO-5)."""
    import migrate
    out = migrate.run_migration(source_dir, PACKAGE_ROOT, name=name, confirm=confirm,
                                allow_zero=allow_zero, patch=patch, status_map=status_map)
    out.setdefault("package_root", str(Path(PACKAGE_ROOT).resolve()))
    if out.get("stage") == "post-flight" and out.get("package_dir"):
        # C19 (user decision): the package carries its own prompt library from birth.
        pkg = Path(out["package_dir"])
        out["prompt_library"] = _emit_prompt_library(pkg, pkg.name)
        if _CURRENT is None:  # C24/B2: leave the package open so handoff_emit follows
            opened = package_open(pkg.name)
            if opened.get("ok"):
                out["package_opened"] = pkg.name
    return out


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
    # ordered queries as the tables), managed emissions (hand edits refused).
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
        status = _managed_emit(csv_dir / f"{table}.csv", buf.getvalue())
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
            "migrations_head": migrations[-1] if migrations else None}


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
    "progress_update": (progress_update, "Append progress entries (execution tracking)"),
    "audit_record": (audit_record, "Record AC verdicts, optionally evidence-bound"),
    "work_bind": (work_bind, "Bind a commit/PR to the entities it satisfies (stamps last_referenced)"),
    "handoff_emit": (handoff_emit, "Emit handoff prompts + executor MCP config (injection-screened)"),
    "package_migrate": (package_migrate, "Migrate a conformant v1 package (staged: preview, then confirm)"),
    "package_adopt": (package_adopt, "Adopt a brownfield repo (staged: scan/preview, then confirm)"),
    "export_html": (export_html, "Export the HTML review surface to <package>/review.html"),
}

_SDK_ERROR = ("tamheed MCP server requires the 'mcp' SDK (Python >=3.10): launch with"
              " 'uv run tamheed_server.py' (PEP 723 fetches it) or 'pip install mcp'.")


def selftest() -> int:
    print(f"tamheed MCP server — {len(TOOLS)} tools")
    for name, (_, desc) in TOOLS.items():
        print(f"  {name}: {desc}")
    return 0


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(_SDK_ERROR, file=sys.stderr)
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
