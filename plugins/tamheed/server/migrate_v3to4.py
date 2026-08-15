"""Tamheed v3 -> v4 package migration — the JSONL-level transform (plan 031/B27).

Pure logic only: `transform_tables` takes parsed rows and returns rewritten rows plus
a full rewrite report. IO, locking, backup, legacy-prompt conversion, and the store
round-trip that validates + canonicalizes the result live in tamheed_server's
`package_migrate` handler. Every value rewrite is REPORTED — the preview lists them
all before the operator confirms (nothing is silently coerced).

v3 -> v4 changes applied here (see plans/031 and CHANGELOG [4.0.0]):
  packages          package_version -> 4.0.0; mode coerced to the CHECK vocabulary
  entity_types      template_ref dropped; 'prompt' row scrubbed; missing v4 baseline
                    rows (waiver) appended by the server from BASELINE_ENTITY_TYPES
  milestones        demoted to label: lifecycle_status/disposition columns dropped,
                    values stashed in custom_attributes.v3_* (findings_17 A5)
  stakeholders      name -> title
  defects           status -> lifecycle_status (vocabulary unchanged)
  deferred_work     status -> lifecycle_status (vocabulary unchanged)
  experiments/pocs  verdict PASS -> Validated, FAIL -> Invalidated
  scope_changes     lifecycle_status = 'Merged' (pre-v4 rows predate the drift-delta
                    lifecycle; they were reconciled under the old regime)
  progress_entries  event_type = 'note' (NOT NULL in v4; loader inserts explicit NULLs)
  diagrams          generation_class dropped (registry-level concept)
  risks             probability/impact normalized to the high/medium/low enum;
                    unmappable originals stashed in custom_attributes (v3_probability /
                    v3_impact), column set NULL
  ALL tables        provenance pairing: source_span with NULL source_kind gets
                    source_kind='inferred' (v4 CHECK: a span requires a kind)
  trace_edges       binds_to -> relates_to (relation deleted in v4); edges violating
                    RELATION_RULES retyped to relates_to (the link survives, the false
                    type claim does not); duplicates after retyping dropped
"""
from __future__ import annotations

import json
from typing import Any

LEGAL_MODES = {"full", "intake", "plan", "resume", "update", "migrate", "adopt"}
VERDICT_MAP = {"PASS": "Validated", "FAIL": "Invalidated"}
PI_ENUM = {"high", "medium", "low"}
# findings_17 C3 (plan 033): v2-era scales were single letters — a 1:1 mechanical
# mapping is recovery, not invention.
PI_LETTERS = {"h": "high", "m": "medium", "l": "low"}
# Tables that carry nullable provenance plus the v4 span-requires-kind CHECK.
PROV_TABLES = (
    "constraints", "invariants", "assumptions", "dependencies", "open_questions",
    "decisions", "adrs", "risks", "hypotheses", "experiments", "pocs", "tests",
    "kpis", "stakeholders", "phases", "wbs_items", "acceptance_criteria",
    "deferred_work", "glossary_terms",
)
TARGET_VERSION = "4.0.0"


def _pop_keys(rows: list[dict], keys: tuple[str, ...]) -> dict[str, list]:
    dropped: dict[str, list] = {}
    for row in rows:
        for key in keys:
            if key in row:
                dropped.setdefault(key, []).append((row.get("id") or row.get("type_id"),
                                                   row.pop(key)))
    return dropped


def _rename_key(rows: list[dict], old: str, new: str) -> int:
    n = 0
    for row in rows:
        if old in row:
            row[new] = row.pop(old)
            n += 1
    return n


def transform_tables(tables: dict[str, list[dict]],
                     relation_rules: dict[str, Any],
                     type_of_table: dict[str, str]) -> tuple[dict[str, list[dict]], dict]:
    """Rewrite v3 rows to v4 shape IN PLACE (on copies made by the caller) and return
    (tables, report). Raises ValueError on a package this transform cannot handle."""
    report: dict[str, Any] = {"target_version": TARGET_VERSION}

    # -- packages -------------------------------------------------------------
    pkg_rows = tables.get("packages") or []
    if not pkg_rows:
        raise ValueError("data/packages.jsonl missing or empty — not a tamheed package")
    pkg = pkg_rows[0]
    report["version_from"] = pkg.get("package_version")
    if str(pkg.get("package_version", "")).startswith("4."):
        raise ValueError(
            f"package is already v{pkg.get('package_version')} — nothing to migrate")
    pkg["package_version"] = TARGET_VERSION
    mode = str(pkg.get("mode") or "")
    if mode not in LEGAL_MODES and not mode.startswith("stage:"):
        report["mode_coerced"] = {"from": mode, "to": "full"}
        pkg["mode"] = "full"

    # -- registry -------------------------------------------------------------
    et_rows = tables.get("entity_types") or []
    _pop_keys(et_rows, ("template_ref",))
    scrubbed = [r for r in et_rows if r.get("type_id") == "prompt"]
    if scrubbed:
        tables["entity_types"] = [r for r in et_rows if r.get("type_id") != "prompt"]
        report["entity_types_scrubbed"] = ["prompt"]
    om_rows = tables.get("omissions") or []
    if any(r.get("entity_type") == "prompt" for r in om_rows):
        tables["omissions"] = [r for r in om_rows if r.get("entity_type") != "prompt"]
        report.setdefault("entity_types_scrubbed", []).append("prompt (omission row)")

    # -- structural renames / drops ------------------------------------------
    # findings_17 A5 (plan 033): dropped milestone lifecycle columns are STASHED
    # into custom_attributes (the risks v3_* pattern) — report + stash, never
    # report-only loss.
    ms_rows = {r.get("id"): r for r in tables.get("milestones") or []}
    ms_dropped = _pop_keys(tables.get("milestones") or [],
                           ("lifecycle_status", "disposition", "disposition_reason_ref"))
    for key, entries in ms_dropped.items():
        for mid, val in entries:
            if val is None or mid not in ms_rows:
                continue
            row = ms_rows[mid]
            extra = json.loads(row.get("custom_attributes") or "{}")
            extra[f"v3_{key}"] = val
            row["custom_attributes"] = json.dumps(
                extra, ensure_ascii=False, separators=(",", ":"))
    if ms_dropped.get("lifecycle_status"):
        report["milestone_status_dropped"] = [
            {"id": mid, "was": val, "stashed_as": "custom_attributes.v3_lifecycle_status"}
            for mid, val in ms_dropped["lifecycle_status"]]
    if _rename_key(tables.get("stakeholders") or [], "name", "title"):
        report["stakeholders_renamed"] = "name -> title"
    for table in ("defects", "deferred_work"):
        if _rename_key(tables.get(table) or [], "status", "lifecycle_status"):
            report.setdefault("status_column_renamed", []).append(table)
    _pop_keys(tables.get("diagrams") or [], ("generation_class",))

    # -- vocabulary maps ------------------------------------------------------
    for table in ("experiments", "pocs"):
        for row in tables.get(table) or []:
            old = row.get("verdict")
            if old in VERDICT_MAP:
                row["verdict"] = VERDICT_MAP[old]
                report.setdefault("verdicts_mapped", []).append(
                    {"id": row.get("id"), "from": old, "to": row["verdict"]})

    for row in tables.get("scope_changes") or []:
        if "lifecycle_status" not in row:
            row["lifecycle_status"] = "Merged"
            report.setdefault("scope_changes_marked_merged", []).append(row.get("id"))

    for row in tables.get("progress_entries") or []:
        if not row.get("event_type"):
            row["event_type"] = "note"

    # -- risks: probability/impact onto the enum ------------------------------
    for row in tables.get("risks") or []:
        for col in ("probability", "impact"):
            val = row.get(col)
            if val is None:
                continue
            low = str(val).strip().lower()
            low = PI_LETTERS.get(low, low)
            if low in PI_ENUM:
                if low != val:
                    report.setdefault("risk_scale_normalized", []).append(
                        {"id": row.get("id"), "column": col, "from": val, "to": low})
                row[col] = low
            else:
                extra = json.loads(row.get("custom_attributes") or "{}")
                extra[f"v3_{col}"] = val
                row["custom_attributes"] = json.dumps(
                    extra, ensure_ascii=False, separators=(",", ":"))
                row[col] = None
                report.setdefault("risk_scale_stashed", []).append(
                    {"id": row.get("id"), "column": col, "was": val,
                     "stashed_as": f"custom_attributes.v3_{col}"})

    # -- provenance pairing (span requires kind) ------------------------------
    for table in PROV_TABLES:
        for row in tables.get(table) or []:
            if row.get("source_span") and not row.get("source_kind"):
                row["source_kind"] = "inferred"
                report.setdefault("provenance_repaired", []).append(
                    {"table": table, "id": row.get("id")})

    # -- trace edges: retire binds_to, retype rule violations ------------------
    id_type: dict[str, str] = {}
    for table, etype in type_of_table.items():
        for row in tables.get(table) or []:
            rid = row.get("id")
            if rid:
                id_type[rid] = etype
    edges = tables.get("trace_edges") or []
    seen: set[tuple] = set()
    kept: list[dict] = []
    for edge in edges:
        rel = edge.get("relation") or ""
        reason = None
        if rel == "binds_to":
            reason = "binds_to deleted in v4"
        else:
            rule = relation_rules.get(rel)
            if rule is not None:
                ftype = id_type.get(edge.get("from_id") or "")
                ttype = id_type.get(edge.get("to_id") or "")
                if rule == "SAME_TYPE":
                    ok = ftype is not None and ftype == ttype
                else:
                    from_ok, to_ok = rule
                    ok = ((from_ok is None or ftype in from_ok)
                          and (to_ok is None or ttype in to_ok))
                if not ok:
                    reason = f"violates the v4 endpoint rule for '{rel}'"
        if reason:
            edge = dict(edge, relation="relates_to")
            report.setdefault("edges_retyped", []).append(
                {"from": edge.get("from_id"), "to": edge.get("to_id"),
                 "was": rel, "now": "relates_to", "reason": reason})
        key = (edge.get("from_id"), edge.get("to_id"), edge.get("relation"))
        if key in seen:
            report.setdefault("edges_deduplicated", []).append(list(key))
            continue
        seen.add(key)
        kept.append(edge)
    if edges:
        tables["trace_edges"] = kept

    return tables, report
