"""Tamheed v2 migration — walk a conformant v1 Keystone package into the database.

Plan 010 (B5). Mapping contract: ../references/migration-v1.md. Reuses the FROZEN v1
validator's parsers (never a second parser) and plan 007's store. Staged and
operator-gated: preview by default; populate only on confirm. Deterministic output
(no wall-clock timestamps) so migrated goldens are byte-comparable.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "scripts"))
sys.path.insert(0, str(_HERE.parent / "db"))

import store  # noqa: E402
import validate_package as vp  # noqa: E402  (frozen v1 contract)

LIFECYCLE = {"Draft", "Proposed", "Approved", "Rejected", "Deferred",
             "Implemented", "Superseded", "Obsolete"}
STATUS_MAP = {"Accepted": "Approved", "Planned": "Proposed"}

# v1 omitted_artifacts kind/path -> v2 entity type (G-SET's recorded-omitted half).
OMISSION_KEYWORDS = [
    ("risk", "risk"), ("constraint", "constraint"), ("assumption", "assumption"),
    ("invariant", "invariant"), ("dependency", "dependency"), ("stakeholder", "stakeholder"),
    ("milestone", "milestone"), ("hypothesis", "hypothesis"), ("experiment", "experiment"),
    ("poc", "poc"), ("test-strategy", "test"), ("work-breakdown", "wbs-item"),
    ("open-question", "open-question"), ("open-decision", "decision"),
    ("acceptance-audit", "audit-verdict"), ("acceptance", "acceptance-criterion"),
    ("progress", "progress-entry"), ("deferred", "deferred-work"),
]

NARRATIVE_KINDS = [  # (rel-substring, doc_kind); first match wins
    ("00-charter", "charter"), ("executive-summary", "executive-summary"),
    ("architecture/architecture", "architecture"), ("research-plan", "research-plan"),
    ("technology-comparison", "technology-comparison"), ("AGENTS.md", "agent-control"),
    ("CLAUDE.md", "agent-control"), ("README.md", "readme"),
    ("governance/naming", "naming"), ("governance/contributing", "contributing"),
    ("governance/governance", "governance"),
]
PROMPT_KINDS = [("initial-prompt", "initial"), ("follow-up-prompts", "follow-up"),
                ("review-prompts", "review")]
DIAGRAM_CLASS = {"context": "Conditional", "component": "Conditional",
                 "integration": "Conditional", "data-flow": "On-request",
                 "deployment": "On-request"}
SKIP_FILES = ("traceability-matrix", "execution-readiness-report", "status-report",
              "execution/backlog", "handoff-manifest")

_ID_RE = vp.ID_TOKEN_RE


def _kebab(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-") or "package"


def _norm_profile(p: str | None) -> str:
    p = (p or "").lower()
    for known in ("enterprise", "rnd", "legacy", "ai-agentic"):
        if known in p:
            return known
    return "unknown"


def _status(cell: str | None, default: str = "Draft") -> str:
    s = (cell or "").strip().strip("*").strip()
    s = s[:1].upper() + s[1:].lower() if s else s
    s = STATUS_MAP.get(s, s)
    return s if s in LIFECYCLE else default


def _ids_in(text: str) -> list[str]:
    return [m.group(0) for m in _ID_RE.finditer(text or "")
            if m.group(1) in vp.GOVERNED_PREFIXES]


def _cell(row: list[str], idx: int | None) -> str | None:
    if idx is None or idx >= len(row):
        return None
    value = row[idx].strip()
    return value if value and value not in ("—", "-", "–") else None


def _row_attrs(headers: list[str], row: list[str]) -> str:
    return json.dumps({"v1": {h: c for h, c in zip(headers, row) if c.strip()}},
                      ensure_ascii=False)


def _sections(text: str) -> list[tuple[str, str]]:
    """Split a narrative body into (heading, body) by ## headings."""
    parts: list[tuple[str, str]] = []
    heading, buf = "Preamble", []
    for line in text.splitlines():
        if line.startswith("## "):
            if "\n".join(buf).strip():
                parts.append((heading, "\n".join(buf).strip()))
            heading, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        parts.append((heading, "\n".join(buf).strip()))
    return parts


def _clean_line(line: str) -> str:
    s = re.sub(r"[#*`>-]+", " ", line).strip()
    return re.sub(r"\s+", " ", s)[:120] or "(untitled)"


class Plan:
    """The stage-2 parse result: everything needed to populate, plus the dry report."""

    def __init__(self):
        self.rows: dict[str, list[dict]] = {}      # table -> row dicts
        self.edges: set[tuple[str, str, str]] = set()
        self.audits: list[dict] = []
        self.omissions: list[tuple[str, str]] = []
        self.unmapped: list[str] = []
        self.defined: set[str] = set()
        self.manifest_counts: dict[str, int] = {}
        self.package: dict = {}

    def add(self, table: str, row: dict):
        self.rows.setdefault(table, []).append(row)
        self.defined.add(row["id"])

    def has(self, ident: str) -> bool:
        return ident in self.defined

    def counts(self) -> dict[str, int]:
        return {t: len(r) for t, r in sorted(self.rows.items())}


# --------------------------------------------------------------------------- stage 1

def preflight(source: Path) -> dict:
    if not (source / "manifest.json").exists():
        return {"ok": False, "stage": "preflight",
                "error": "no manifest.json — not a conformant v1 package. If this is a "
                         "Keystone-lineage project without the mechanical layer, use "
                         "package_adopt (plan 011), which reconstructs with provenance."}
    # In-process (field-evidence C11): a subprocess spawned from the stdio MCP server
    # inherits the JSON-RPC transport and can wedge on Windows. The frozen validator is
    # already imported as a library; calling it directly also removes the wedge-vs-slow
    # ambiguity. The try/except replaces the crash isolation the subprocess used to give.
    try:
        report = vp.build_summary(source, vp.run_gates(source))
    except Exception as exc:
        return {"ok": False, "stage": "preflight",
                "error": f"pre-flight crashed inside the frozen v1 validator: {exc!r}",
                "traceback": traceback.format_exc()[-2000:]}
    if not report["ok"]:
        return {"ok": False, "stage": "preflight", "error":
                "v1 validator failed (critical: %s) — fix the package under v1 or use "
                "package_adopt if it is lineage-but-nonconformant"
                % ", ".join(report["critical_failed"]),
                "report": report}
    return {"ok": True, "stage": "preflight"}


# --------------------------------------------------------------------------- stage 2

def _map_register_row(plan: Plan, prefix: str, ident: str, t, row: list[str]):
    def col(*aliases):
        return _cell(row, t.col_index(aliases))

    attrs = _row_attrs(t.headers, row)
    status = _status(col("status"))
    title = col("statement", "requirement", "constraint", "assumption", "question",
                "decision", "risk", "invariant", "dependency", "hypothesis", "milestone",
                "metric", "test", "work item", "phase", "stakeholder / role",
                "stakeholder") or _clean_line(" ".join(row[1:2]))
    if prefix in ("FR", "NFR"):
        source = col("source") or ""
        kind = "clarification" if re.search(r"OQ-|clarif", source, re.I) else "brief"
        prio = (col("priority", "scope") or "")
        plan.add("requirements", {
            "id": ident, "kind": "functional" if prefix == "FR" else "non-functional",
            "title": title[:200], "statement": title,
            "priority": prio or None, "mvp": 1 if "mvp" in prio.lower() else 0,
            "lifecycle_status": status if status != "Draft" else "Approved",
            "source_kind": kind, "source_span": source or "v1:register-row",
            "custom_attributes": attrs})
    elif prefix == "CON":
        plan.add("constraints", {"id": ident, "title": title[:200], "statement": title,
                                 "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "INV":
        plan.add("invariants", {"id": ident, "title": title[:200], "statement": title,
                                "enforcement": col("enforced by", "enforcement"),
                                "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "ASM":
        plan.add("assumptions", {"id": ident, "title": title[:200], "statement": title,
                                 "risk_if_wrong": col("risk if wrong"),
                                 "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "DEP":
        plan.add("dependencies", {"id": ident, "title": title[:200], "statement": title,
                                  "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "OQ":
        plan.add("open_questions", {"id": ident, "title": title[:200], "question": title,
                                    "resolution": col("resolution"),
                                    "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "DEC":
        # promoted_to is an FK into adrs (field-evidence C12): only ADR- tokens qualify;
        # a cell citing other governed ids (amendments, cross-refs) must not crash populate.
        promoted_cell = col("promoted to") or ""
        promoted = next((i for i in _ids_in(promoted_cell) if i.startswith("ADR-")), None)
        if promoted is None and _ids_in(promoted_cell):
            plan.unmapped.append(f"{ident}: promoted-to cell has no ADR- token — "
                                 f"stored NULL ({promoted_cell[:60]!r})")
        plan.add("decisions", {"id": ident, "title": title[:200], "decision": title,
                               "rationale": col("rationale", "rationale (short)"),
                               "lifecycle_status": _status(col("status"), "Proposed"),
                               "promoted_to": promoted,
                               "custom_attributes": attrs})
    elif prefix == "RISK":
        plan.add("risks", {"id": ident, "title": title[:200], "description": title,
                           "probability": col("likelihood", "probability"),
                           "impact": col("impact"), "mitigation": col("mitigation"),
                           "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "HYP":
        plan.add("hypotheses", {"id": ident, "title": title[:200], "statement": title,
                                "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "KPI":
        plan.add("kpis", {"id": ident, "title": title[:200],
                          "measure": col("measurement method", "measure"),
                          "target": col("target"), "lifecycle_status": status,
                          "custom_attributes": attrs})
    elif prefix == "STK":
        plan.add("stakeholders", {"id": ident, "name": title[:200],
                                  "interest": col("interest in the project", "interest"),
                                  "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "PH":
        num = re.search(r"(\d+)", ident)
        plan.add("phases", {"id": ident, "title": title[:200],
                            "objective": col("goal", "objective"),
                            "exit_criteria": col("exit criteria", "gate"),
                            "sort_order": int(num.group(1)) if num else 0,
                            "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "MS":
        phase = next((i for i in _ids_in(" ".join(row)) if i.startswith("PH-")), None)
        if phase is None:
            plan.unmapped.append(f"{ident}: milestone row has no PH- reference")
            return
        plan.add("milestones", {"id": ident, "title": title[:200], "phase_id": phase,
                                "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "WBS":
        phase = next((i for i in _ids_in(_cell(row, t.col_index(["phase"])) or "")
                      if i.startswith("PH-")), None)
        plan.add("wbs_items", {"id": ident, "title": title[:200], "phase_id": phase,
                               "lifecycle_status": status, "custom_attributes": attrs})
        for ref in _ids_in(_cell(row, t.col_index(["realises", "realizes"])) or ""):
            plan.edges.add((ident, ref, "implements"))
    elif prefix == "AC":
        verifies = _cell(row, t.col_index(["verifies"])) or ""
        req = next((i for i in _ids_in(verifies) if i.split("-")[0] in ("FR", "NFR")), None)
        plan.add("acceptance_criteria", {
            "id": ident, "title": title[:120], "statement": title, "requirement_id": req,
            "lifecycle_status": status if status != "Draft" else "Approved",
            "custom_attributes": attrs})
        for ref in _ids_in(verifies):
            plan.edges.add((ident, ref, "verifies"))
    elif prefix == "TEST":
        for ref in _ids_in(_cell(row, t.col_index(["verifies"])) or ""):
            plan.edges.add((ident, ref, "tests"))
        plan.add("tests", {"id": ident, "title": title[:200], "kind": col("kind"),
                           "lifecycle_status": status, "custom_attributes": attrs})
    else:
        plan.unmapped.append(f"{ident}: no v2 mapping for prefix {prefix}")


_MATRIX_RELS = [("decision", "derives_from", "out"), ("work", "implements", "in"),
                ("test", "tests", "in"), ("risk", "relates_to", "in"),
                ("acceptance", "verifies", "in")]


def _map_matrix(plan: Plan, t) -> None:
    subject_col = 0
    for row in t.rows:
        subject = next(iter(_ids_in(row[subject_col])), None)
        if not subject:
            continue
        for ci, header in enumerate(t.headers):
            if ci == subject_col:
                continue
            for key, rel, direction in _MATRIX_RELS:
                if key in header.lower():
                    for ref in _ids_in(row[ci] if ci < len(row) else ""):
                        plan.edges.add((subject, ref, rel) if direction == "out"
                                       else (ref, subject, rel))
                    break


def _map_adr(plan: Plan, pf) -> None:
    fm = pf.front_matter
    ident = (fm.get("id") or "").strip()
    if not ident.startswith("ADR-"):
        plan.unmapped.append(f"{pf.rel}: ADR file without front-matter id")
        return
    title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
    sections = dict(_sections(pf.text))
    plan.add("adrs", {
        "id": ident, "title": _clean_line(title_m.group(1)) if title_m else ident,
        "context": next((v for k, v in sections.items() if "context" in k.lower()), None),
        "decision": next((v for k, v in sections.items() if "decision" in k.lower()), None),
        "consequences": next((v for k, v in sections.items()
                              if "consequence" in k.lower()), None),
        "lifecycle_status": _status(fm.get("status"), "Proposed"),
        "custom_attributes": json.dumps({"v1": {"front_matter": dict(fm)}},
                                        ensure_ascii=False)})


def _map_exp_poc(plan: Plan, pf) -> None:
    fm = pf.front_matter
    ident = (fm.get("id") or "").strip()
    table = "experiments" if ident.startswith("EXP-") else "pocs"
    if not ident:
        plan.unmapped.append(f"{pf.rel}: experiment/POC file without front-matter id")
        return
    title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
    plan.add(table, {
        "id": ident, "title": _clean_line(title_m.group(1)) if title_m else ident,
        "verdict": "Pending", "lifecycle_status": _status(fm.get("status"), "Proposed"),
        "custom_attributes": json.dumps(
            {"v1": {"front_matter": dict(fm), "body": pf.text}}, ensure_ascii=False)})


def parse_v1(source: Path) -> Plan:
    plan = Plan()
    files = vp.load_package(source)
    by_rel = {pf.rel: pf for pf in files}

    manifest = json.loads(by_rel["manifest.json"].text)
    raw_name = manifest.get("package") or manifest.get("project") or source.name
    plan.manifest_counts = manifest.get("identifier_counts") or {}
    state = {}
    if "keystone-state.json" in by_rel:
        state = json.loads(by_rel["keystone-state.json"].text)
    depth = ((state.get("project_profile") or {}).get("mode") or "").strip()
    extras = {k: v for k, v in manifest.items()
              if k not in ("package", "project", "profile", "mode", "mvp_definition",
                           "entry_point", "go_no_go", "generated_at", "package_version")}
    custom = {"v1_manifest": extras}
    if depth in ("quick", "standard", "deep", "research"):
        custom["research_depth"] = depth
    plan.package = {
        "name": _kebab(raw_name), "title": manifest.get("title") or raw_name,
        "profile": _norm_profile(manifest.get("profile")),
        "mode": manifest.get("mode") or "full",
        "package_version": manifest.get("package_version") or "1.0.0",
        "mvp_definition": manifest.get("mvp_definition"),
        "entry_point": manifest.get("entry_point"), "go_no_go": manifest.get("go_no_go"),
        "created_at": manifest.get("generated_at") or "v1-migration",
        "custom_attributes": json.dumps(custom, ensure_ascii=False)}

    for entry in manifest.get("omitted_artifacts") or []:
        kind = (entry.get("kind") or entry.get("path") or "").lower()
        reason = entry.get("reason") or "omitted in v1 (no reason recorded)"
        for kw, etype in OMISSION_KEYWORDS:
            if kw in kind:
                plan.omissions.append((etype, reason))
                break

    doc_seq = sec_seq = dia_seq = prm_seq = 0
    for pf in files:
        if pf.is_json or vp.is_template_path(pf.rel, Path(pf.rel).name):
            continue
        rel_l = pf.rel.replace("\\", "/").lower()
        if any(s in rel_l for s in SKIP_FILES):
            if "traceability-matrix" in rel_l:
                for t in vp.parse_markdown_tables(pf.text):
                    _map_matrix(plan, t)
            continue
        if "acceptance-audit" in rel_l:
            for t in vp.parse_markdown_tables(pf.text):
                for row in t.rows:
                    ac = next((i for i in _ids_in(row[0]) if i.startswith("AC-")), None)
                    verdict = _cell(row, t.col_index(["verdict"]))
                    if ac and verdict in ("Met", "Partial", "Not-met", "Pending"):
                        plan.audits.append({"ac_id": ac, "verdict": verdict,
                                            "evidence": _cell(row, t.col_index(["evidence"]))})
            continue
        if rel_l.startswith("adrs/"):
            _map_adr(plan, pf)
            continue
        if rel_l.startswith(("experiments/", "pocs/")):
            _map_exp_poc(plan, pf)
            continue
        if "/diagrams/" in rel_l:
            stem = Path(rel_l).stem
            if stem in DIAGRAM_CLASS:
                dia_seq += 1
                plan.add("diagrams", {"id": f"DIA-{dia_seq:03d}", "kind": stem,
                                      "title": f"{stem} diagram", "body": pf.text,
                                      "generation_class": DIAGRAM_CLASS[stem]})
            continue

        prompt = next((k for s, k in PROMPT_KINDS if s in rel_l), None)
        if prompt:
            prm_seq += 1
            title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
            plan.add("prompts", {"id": f"PRM-{prm_seq:03d}", "prompt_kind": prompt,
                                 "title": _clean_line(title_m.group(1)) if title_m else prompt,
                                 "body": pf.text})

        # register tables anywhere (incl. KPI/STK tables inside the charter)
        for t in vp.parse_markdown_tables(pf.text):
            id_col = t.col_index(vp.ID_HEADERS)
            if id_col is None:
                id_col = vp._guess_id_column(t)
            if id_col is None:
                continue
            for row in t.rows:
                token = next(iter(_ids_in(row[id_col] if id_col < len(row) else "")), None)
                if token and not plan.has(token):
                    _map_register_row(plan, token.split("-")[0], token, t, row)

        kind = next((k for s, k in NARRATIVE_KINDS if s in pf.rel), None)
        if kind and not prompt:
            doc_seq += 1
            doc_id = f"DOC-{doc_seq:03d}"
            title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
            plan.add("narrative_documents", {
                "id": doc_id, "doc_kind": kind,
                "title": _clean_line(title_m.group(1)) if title_m else pf.rel,
                "lifecycle_status": _status(pf.front_matter.get("status")),
                "custom_attributes": json.dumps({"v1": {"path": pf.rel}},
                                                ensure_ascii=False)})
            for order, (heading, body) in enumerate(_sections(pf.text), 1):
                sec_seq += 1
                plan.add("document_sections", {
                    "id": f"SEC-{sec_seq:03d}", "document_id": doc_id,
                    "heading": heading[:200], "body": body, "sort_order": order})

    # Weak/unmapped definitions (heading phases, bold-leader WBS items, …) -> minimal rows.
    occurrences, _ = vp.collect_identifiers(files)
    for occ in occurrences:
        if not occ.is_definition or plan.has(occ.ident):
            continue
        text = by_rel[occ.rel].text.splitlines()
        title = _clean_line(text[occ.line - 1]) if 0 < occ.line <= len(text) else occ.ident
        prefix = occ.prefix
        if prefix == "PH":
            num = re.search(r"(\d+)", occ.ident)
            plan.add("phases", {"id": occ.ident, "title": title,
                                "sort_order": int(num.group(1)) if num else 0,
                                "lifecycle_status": "Approved"})
        elif prefix == "WBS":
            plan.add("wbs_items", {"id": occ.ident, "title": title,
                                   "lifecycle_status": "Approved"})
        elif prefix in ("FR", "NFR"):
            plan.add("requirements", {
                "id": occ.ident, "kind": "functional" if prefix == "FR" else "non-functional",
                "title": title, "mvp": 0, "lifecycle_status": "Approved",
                "source_kind": "inferred",
                "source_span": f"v1 weak definition {occ.rel}:{occ.line}"})
        elif prefix == "MS":
            plan.unmapped.append(f"{occ.ident}: weak milestone definition without a phase")
        elif prefix in ("KPI", "STK", "CON", "INV", "ASM", "DEP", "OQ", "DEC", "RISK",
                        "HYP", "AC", "TEST"):
            table = {"KPI": "kpis", "STK": "stakeholders", "CON": "constraints",
                     "INV": "invariants", "ASM": "assumptions", "DEP": "dependencies",
                     "OQ": "open_questions", "DEC": "decisions", "RISK": "risks",
                     "HYP": "hypotheses", "AC": "acceptance_criteria", "TEST": "tests"}[prefix]
            row = {"id": occ.ident, "lifecycle_status": "Approved"}
            row["name" if table == "stakeholders" else "title"] = title
            if table == "decisions":
                row["lifecycle_status"] = "Approved"
            plan.add(table, row)

    # WBS parents implied by dotted ids (WBS-1.1 without an explicit WBS-1 row).
    wbs = {r["id"] for r in plan.rows.get("wbs_items", [])}
    for r in list(plan.rows.get("wbs_items", [])):
        parent = r["id"].rsplit(".", 1)[0]
        if "." in r["id"] and parent != r["id"]:
            if parent not in wbs and parent not in plan.defined:
                plan.add("wbs_items", {"id": parent, "title": f"{parent} (group)",
                                       "lifecycle_status": "Approved"})
                wbs.add(parent)
            r["parent_id"] = parent
    return plan


# --------------------------------------------------------------------------- stages 4-5

INSERT_ORDER = ["requirements", "constraints", "invariants", "assumptions", "dependencies",
                "open_questions", "adrs", "decisions", "risks", "hypotheses", "experiments",
                "pocs", "kpis", "stakeholders", "phases", "milestones", "wbs_items",
                "acceptance_criteria", "tests", "deferred_work", "narrative_documents",
                "document_sections", "diagrams", "prompts"]

try:
    from tamheed_server import BASELINE_ENTITY_TYPES  # when imported alongside the server
except ImportError:  # pragma: no cover
    BASELINE_ENTITY_TYPES = []


def populate(plan: Plan, dest_root: Path, name: str) -> dict:
    pkg_dir = dest_root / name
    if (pkg_dir / "data").exists():
        return {"ok": False, "stage": "populate",
                "error": f"destination package '{name}' already exists"}
    # `step` names the insert in flight so a constraint failure reports table/row context
    # (field-evidence C11/C13: a ~2,000-row populate dying with a bare IntegrityError is
    # very expensive to root-cause) — the batch stays one transaction, atomicity unchanged.
    step = "open store"
    try:
        with store.PackageStore(pkg_dir) as s:
            conn = s.conn
            try:
                step = "entity_types"
                conn.executemany(
                    "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
                    " VALUES (?, ?, ?, ?)", BASELINE_ENTITY_TYPES)
                step = "packages"
                pkg = dict(plan.package, name=name)
                conn.execute(
                    "INSERT INTO packages (name, title, profile, mode, package_version,"
                    " mvp_definition, entry_point, go_no_go, created_at, custom_attributes)"
                    " VALUES (:name, :title, :profile, :mode, :package_version,"
                    " :mvp_definition, :entry_point, :go_no_go, :created_at,"
                    " :custom_attributes)", pkg)
                for etype, reason in dict(plan.omissions).items():
                    step = f"omissions ({etype})"
                    conn.execute("INSERT OR IGNORE INTO omissions (entity_type, reason)"
                                 " VALUES (?, ?)", (etype, reason))
                for table in INSERT_ORDER:
                    rows = plan.rows.get(table, [])
                    if table == "wbs_items":  # parents before children
                        rows = sorted(rows, key=lambda r: r["id"].count("."))
                    for row in rows:
                        step = f"{table} row {row.get('id', '?')}"
                        cols = list(row)
                        conn.execute(
                            f"INSERT INTO {table} ({', '.join(cols)})"
                            f" VALUES ({', '.join(':' + c for c in cols)})", row)
                for seq, audit in enumerate(plan.audits, 1):
                    step = f"audit_verdicts row AV-{seq:03d} (ac {audit['ac_id']})"
                    conn.execute(
                        "INSERT INTO audit_verdicts (id, ac_id, verdict, evidence, iteration)"
                        " VALUES (?, ?, ?, ?, 1)",
                        (f"AV-{seq:03d}", audit["ac_id"], audit["verdict"], audit["evidence"]))
                known = {r[0] for r in conn.execute("SELECT id FROM entity_index")}
                for frm, to, rel in sorted(plan.edges):
                    if frm in known and to in known:
                        step = f"trace edge {frm} -> {to}"
                        conn.execute("INSERT OR IGNORE INTO trace_edges"
                                     " (from_id, to_id, relation) VALUES (?, ?, ?)",
                                     (frm, to, rel))
                    else:
                        plan.unmapped.append(
                            f"edge {frm} -> {to} ({rel}): endpoint not migrated")
                step = "commit"
                s.commit()
            except Exception:
                conn.rollback()  # one transaction: no partial package
                raise
    except store.StoreLockedError as exc:
        return {"ok": False, "stage": "populate", "error": str(exc)}
    except Exception as exc:
        # No poison directory (C11): the created data/ dir would make every retry refuse
        # with "already exists". The store lock was released by __exit__ above.
        shutil.rmtree(pkg_dir / "data", ignore_errors=True)
        return {"ok": False, "stage": "populate",
                "error": f"populate failed at {step}: {exc}"}
    return {"ok": True, "stage": "populate", "package_dir": str(pkg_dir)}


def fidelity(plan: Plan, pkg_dir: Path) -> dict:
    conn = store.load(pkg_dir / "data")
    ids = {r[0] for r in conn.execute("SELECT id FROM entity_index")}
    missing = sorted(plan.defined - ids)
    prefix_tables = {"FR": ("requirements", "kind='functional'"),
                     "NFR": ("requirements", "kind='non-functional'"),
                     "CON": ("constraints", None), "INV": ("invariants", None),
                     "ASM": ("assumptions", None), "DEP": ("dependencies", None),
                     "OQ": ("open_questions", None), "DEC": ("decisions", None),
                     "ADR": ("adrs", None), "RISK": ("risks", None),
                     "HYP": ("hypotheses", None), "EXP": ("experiments", None),
                     "POC": ("pocs", None), "KPI": ("kpis", None),
                     "STK": ("stakeholders", None), "PH": ("phases", None),
                     "MS": ("milestones", None), "WBS": ("wbs_items", None),
                     "AC": ("acceptance_criteria", None), "TEST": ("tests", None)}
    deltas = {}
    for prefix, expected in plan.manifest_counts.items():
        table, where = prefix_tables.get(prefix, (None, None))
        if table is None:
            continue
        sql = f"SELECT COUNT(*) FROM {table}" + (f" WHERE {where}" if where else "")
        actual = conn.execute(sql).fetchone()[0]
        if actual != expected:
            deltas[prefix] = {"manifest": expected, "migrated": actual}
    gates = {}
    for gate, view in (("G-TRACE", "g_trace_failures"), ("G-SET", "g_set_failures"),
                       ("G-PROGRESS", "g_progress_failures")):
        gates[gate] = [r[0] for r in conn.execute(f"SELECT * FROM {view}")]
    conn.close()
    ok = not missing and all(not f for f in gates.values())
    return {"ok": ok, "identifier_gaps": missing, "count_deltas": deltas,
            "gate_failures": {g: f for g, f in gates.items() if f},
            "unmapped": plan.unmapped}


# --------------------------------------------------------------------------- driver

def run_migration(source_dir: str, dest_root: str | Path, name: str | None = None,
                  confirm: bool = False) -> dict:
    source = Path(source_dir)
    if not source.is_dir():
        return {"ok": False, "stage": "preflight", "error": f"{source_dir} is not a directory"}
    pre = preflight(source)
    if not pre["ok"]:
        return pre
    plan = parse_v1(source)
    name = _kebab(name or plan.package["name"])
    preview = {"stage": "preview", "package": name, "counts": plan.counts(),
               "edges": len(plan.edges), "audit_verdicts": len(plan.audits),
               "omissions": len(plan.omissions),
               "manifest_counts": plan.manifest_counts, "unmapped": plan.unmapped}
    if not confirm:
        return {"ok": True, **preview,
                "next": "re-run with confirm=true to populate (operator gate, stage 3)"}
    pop = populate(plan, Path(dest_root), name)
    if not pop["ok"]:
        return pop
    fid = fidelity(plan, Path(dest_root) / name)
    return {"ok": fid["ok"], "stage": "post-flight", "preview": preview,
            "package_dir": pop["package_dir"], "fidelity": fid,
            "note": None if fid["ok"] else
            "fidelity gaps are reported, never auto-resolved — review before use"}
