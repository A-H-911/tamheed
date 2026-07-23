"""Tamheed v2 migration — walk a conformant v1 Keystone package into the database.

Plan 010 (B5). Mapping contract: ../references/migration-v1.md. Reuses the FROZEN v1
validator's parsers (never a second parser) and plan 007's store. Staged and
operator-gated: preview by default; populate only on confirm. Deterministic output
(no wall-clock timestamps) so migrated goldens are byte-comparable.
"""
from __future__ import annotations

import hashlib
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

try:  # when imported alongside the server (the normal case; no import cycle —
    # tamheed_server imports migrate lazily inside its handler)
    from tamheed_server import BASELINE_ENTITY_TYPES, ENTITY_TABLES  # noqa: E402
except ImportError:  # pragma: no cover
    BASELINE_ENTITY_TYPES = []
    ENTITY_TABLES = {}

LIFECYCLE = {"Draft", "Proposed", "Approved", "Rejected", "Deferred",
             "Implemented", "Superseded", "Obsolete"}
STATUS_MAP = {"Accepted": "Approved", "Planned": "Proposed"}
# Semantic defaults for common v1 register vocabularies (field-evidence C17). Unlike
# STATUS_MAP's canonical pairs these are judgment calls, so every application is recorded
# in the preview's status_coerced ledger and the operator can override via status_map.
STATUS_COERCE = {
    "Resolved": "Implemented",   # answered/done — the terminal-positive lifecycle state
    "Open": "Approved",          # live in the register, not awaiting ratification
    "Monitoring": "Approved",    # an activity on an in-force item, not a lifecycle stage
    "Active": "Approved",        # in force and operative
    "Living": "Approved",        # "living document" — same concept as active (C24/B3)
    "Complete": "Implemented",   # phase prose statuses (C24/D-9)
    "Closed": "Obsolete",        # terminal-neutral: no claim about HOW it closed
}

# v1 risk Status -> the purpose-built risk_state enum (C24/D-10). lifecycle_status gets
# the same cell through _status as before; this second mapping keeps the risk axis honest.
RISK_STATE_MAP = {"Open": "open", "Monitoring": "open", "Mitigated": "mitigated",
                  "Materialized": "materialized", "Closed": "retired",
                  "Accepted": "accepted"}

# v1 omitted_artifacts kind/path -> v2 entity type (G-SET's recorded-omitted half).
OMISSION_KEYWORDS = [
    ("risk", "risk"), ("constraint", "constraint"), ("assumption", "assumption"),
    ("invariant", "invariant"), ("dependency", "dependency"), ("stakeholder", "stakeholder"),
    ("milestone", "milestone"), ("hypothesis", "hypothesis"), ("experiment", "experiment"),
    ("poc", "poc"), ("test-strategy", "test"), ("work-breakdown", "wbs-item"),
    ("open-question", "open-question"), ("open-decision", "decision"),
    ("acceptance-audit", "audit-verdict"), ("acceptance", "acceptance-criterion"),
    ("progress", "progress-entry"), ("deferred", "deferred-work"),
    ("research", "narrative-document"),  # research-plan omissions (field-evidence C13)
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


def _norm_status_key(cell: str | None) -> str:
    s = (cell or "").strip().strip("*").strip()
    return s[:1].upper() + s[1:].lower() if s else s


def _status(cell: str | None, default: str = "Draft",
            plan: "Plan | None" = None, ident: str | None = None) -> str:
    raw = (cell or "").strip().strip("*").strip()
    s = STATUS_MAP.get(_norm_status_key(raw), _norm_status_key(raw))
    if s in LIFECYCLE:
        return s
    # Unknown vocabulary (C17): operator status_map > semantic defaults > default.
    # Every non-empty coercion is recorded — an empty cell -> default is absence, not
    # coercion. Compound cells never auto-map (exact match only). C28 (B2'): each entry
    # records WHICH branch fired — a supplied map no longer takes credit for
    # semantic-default coercions (findings_7 §B2).
    mapped, basis = None, "default"
    if plan is not None and plan.status_map:
        mapped = plan.status_map.get(s)
        if mapped is not None:
            basis = "status_map"
    if mapped is None:
        mapped = STATUS_COERCE.get(s)
        if mapped is not None:
            basis = "semantic-default"
    result = mapped or default
    if raw and plan is not None:
        plan.status_coerced.append({"id": ident, "original": raw, "coerced": result,
                                    "basis": basis})
    return result


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
    """Split a narrative body by its SHALLOWEST heading level below the H1 (C24/D-7:
    a `###`-only progress log once collapsed 23 dated entries into one 82k-char
    Preamble — the newest history became the least navigable)."""
    levels = [len(h) for h in re.findall(r"^(#{2,6})\s", text, re.M)]
    marker = "#" * (min(levels) if levels else 2) + " "
    parts: list[tuple[str, str]] = []
    heading, buf = "Preamble", []
    for line in text.splitlines():
        if line.startswith(marker):
            if "\n".join(buf).strip():
                parts.append((heading, "\n".join(buf).strip()))
            heading, buf = line[len(marker):].strip(), []
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        parts.append((heading, "\n".join(buf).strip()))
    return parts


_PIPE_SENTINEL = "\x00"

_TITLE_ALIASES = frozenset({
    "title", "statement", "given / when / then", "criterion", "requirement",
    "constraint", "assumption", "question", "decision", "risk", "invariant",
    "dependency", "hypothesis", "milestone", "metric", "test", "work item", "epic",
    "phase", "name", "stakeholder / role", "stakeholder"})

_LONGFORM_ALIASES = frozenset({"statement", "given / when / then", "criterion",
                               "description"})


def _tables(text: str):
    """C26/B3: escaped in-cell pipes (`\\|`) shear rows in the frozen table parser
    (`| a (X \\| Y) b |` split at the escape, corrupting two columns). Substitute a
    sentinel before parsing and restore the literal pipe in every header/cell after —
    the frozen parser itself is never touched (never-a-second-parser rule intact)."""
    tables = vp.parse_markdown_tables(text.replace("\\|", _PIPE_SENTINEL))
    for t in tables:
        t.headers = [h.replace(_PIPE_SENTINEL, "|") for h in t.headers]
        t.rows = [[c.replace(_PIPE_SENTINEL, "|") for c in r] for r in t.rows]
    return tables


def _clean_line(line: str) -> str:
    """Markdown-strip a defining line into a title. POSITIONAL stripping only — the old
    `[#*`>-]+` character class deleted every ASCII hyphen, mangling governed ids
    (`FR-001` -> `FR 001`) and severing cross-references (field-evidence C24/D-2). One
    consistent 200 cap (the old 120 was a second, hidden cap)."""
    s = line.strip()
    s = re.sub(r"^[#>\s]+", "", s)      # leading heading / blockquote markers
    s = re.sub(r"^[-*+]\s+", "", s)     # a single leading list bullet
    s = s.replace("**", "").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip()[:200] or "(untitled)"


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
        # File-level loss accounting (field-evidence C13): unmapped is id-granular, so
        # whole-file outcomes get their own ledgers, surfaced in the preview.
        self.partial_files: dict[str, int] = {}  # rows migrated per file; prose not (C17)
        self.skipped_files: list[str] = []   # skipped by design (derived views)
        # Preview-honesty ledgers (field-evidence C17): every judgment call reported.
        self.status_coerced: list[dict] = []   # [{id, original, coerced}]
        self.title_fallbacks: list[dict] = []  # [{id, family}] — title fell back to row[1]
        self.status_map: dict[str, str] = {}   # operator overrides, normalized keys
        # C21 (B1): registers with NO status column, per (file, family) -> row count.
        self.status_defaulted: dict[tuple[str, str], int] = {}
        self.dw_crosswalk: dict[str, str] = {}  # C24/D-4: legacy D-nn -> DW-NNN

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
                         "package_adopt, which reconstructs with provenance."}
    # In-process (field-evidence C11): a subprocess spawned from the stdio MCP server
    # inherits the JSON-RPC transport and can wedge on Windows. The frozen validator is
    # already imported as a library; calling it directly also removes the wedge-vs-slow
    # ambiguity. The try/except replaces the crash isolation the subprocess used to give.
    # Which contract judged this (field-evidence C17): the frozen validator carries no
    # version constant, so the content hash IS its identity — stale-copy incidents become
    # auditable from the result alone.
    src_bytes = Path(str(vp.__file__)).read_bytes()
    validator = {"sha256": hashlib.sha256(src_bytes).hexdigest(), "bytes": len(src_bytes)}
    try:
        report = vp.build_summary(source, vp.run_gates(source))
    except Exception as exc:
        return {"ok": False, "stage": "preflight", "validator": validator,
                "error": f"pre-flight crashed inside the frozen v1 validator: {exc!r}",
                "traceback": traceback.format_exc()[-2000:]}
    if not report["ok"]:
        return {"ok": False, "stage": "preflight", "validator": validator, "error":
                "v1 validator failed (critical: %s) — fix the package under v1 or use "
                "package_adopt if it is lineage-but-nonconformant"
                % ", ".join(report["critical_failed"]),
                "report": report}
    return {"ok": True, "stage": "preflight", "validator": validator}


# --------------------------------------------------------------------------- stage 2

def _map_register_row(plan: Plan, prefix: str, ident: str, t, row: list[str],
                      id_col: int = 0, src: str = ""):
    def col(*aliases):
        return _cell(row, t.col_index(aliases))

    def _scan_cols(names, skip):
        # Frozen-col_index matching (exact-equality, COLUMN order) minus excluded columns:
        # the id column never qualifies (C17), nor does the title's own column when
        # resolving the long-form text (C26 round-5 guard).
        for i, header in enumerate(t.headers):
            if i not in skip and header.strip().lower() in names:
                return _cell(row, i), i
        return None, None

    attrs = _row_attrs(t.headers, row)
    if t.col_index(["status"]) is None:
        # C21 (B1): a register with NO status column defaults to Approved — parity with
        # weak-definition synthesis (the richer source must not produce the poorer row).
        # DEC keeps Proposed (a proposed decision is never rendered approved) and — C24/
        # D-12, caught by the golden delta review — AC keeps Proposed too: an Approved AC
        # freezes slice_id via the immutability trigger, and v1 has no slices; the
        # Approved default would permanently kill v_phase_exit on migrated packages.
        status = "Proposed" if prefix in ("DEC", "AC") else "Approved"
        key = (src, prefix)
        plan.status_defaulted[key] = plan.status_defaulted.get(key, 0) + 1
    else:
        status = _status(col("status"), "Proposed" if prefix == "DEC" else "Draft",
                         plan=plan, ident=ident)
    # Two-pass title (C26/B1): an EXACT Title/Name column wins outright — column order
    # once let an `EPIC` crosswalk cell (matching the 'epic' alias) out-rank the real
    # Title column sitting one position later.
    title, title_ix = _scan_cols({"title", "name"}, {id_col})
    if title is None:
        title, title_ix = _scan_cols(_TITLE_ALIASES, {id_col})
    raw_fallback = None
    if title is None:
        # C24/D-0: the fallback CLEANS for the title but must never damage the long-form
        # text — the raw cell is carried separately and becomes the statement.
        raw_fallback = (row[1].strip() if len(row) > 1 else "") or "(untitled)"
        title = _clean_line(raw_fallback)
        plan.title_fallbacks.append({"id": ident, "family": prefix})
    if len(title) <= 3 or re.fullmatch(r"[A-Z]{2,10}-[\d.]+", title):
        # C24/D-5 + C26/B1: a 1-3 char OR id-shaped title is degenerate; rescue from a
        # real Title/Name column elsewhere in the row.
        better, better_ix = _scan_cols(
            {"title", "name"}, {id_col, -1 if title_ix is None else title_ix})
        if better and len(better) > 3 and not re.fullmatch(r"[A-Z]{2,10}-[\d.]+", better):
            plan.unmapped.append(f"{ident}: degenerate title {title!r} replaced from the "
                                 "Title column")
            title, title_ix = better, better_ix
    # Long-form text resolved INDEPENDENTLY of the title (C26 round-5 guard: a Title
    # column must never displace a Statement column). Named columns return raw cells;
    # the fallback path carries the uncleaned raw cell.
    stmt_cell, _six = _scan_cols(
        _LONGFORM_ALIASES, {id_col, -1 if title_ix is None else title_ix})
    long_text = raw_fallback if raw_fallback is not None else (stmt_cell or title)
    if prefix in ("FR", "NFR"):
        source = col("source") or ""
        kind = "clarification" if re.search(r"OQ-|clarif", source, re.I) else "brief"
        prio = (col("priority", "scope") or "")
        # MoSCoW tolerance (field-evidence C14): v1 packages using M/S/C/W priorities
        # must not migrate to an all-mvp=0 set that makes G-TRACE pass vacuously.
        prio_bare = prio.strip().strip("*").strip()
        is_mvp = ("mvp" in prio.lower() or prio_bare == "M"
                  or prio_bare.lower().startswith("must"))
        plan.add("requirements", {
            "id": ident, "kind": "functional" if prefix == "FR" else "non-functional",
            "title": title[:200], "statement": long_text,
            "priority": prio or None, "mvp": 1 if is_mvp else 0,
            "lifecycle_status": status if status != "Draft" else "Approved",
            "source_kind": kind, "source_span": source or "v1:register-row",
            "custom_attributes": attrs})
    elif prefix == "CON":
        plan.add("constraints", {"id": ident, "title": title[:200], "statement": long_text,
                                 "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "INV":
        plan.add("invariants", {"id": ident, "title": title[:200], "statement": long_text,
                                "enforcement": col("enforced by", "enforcement"),
                                "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "ASM":
        plan.add("assumptions", {"id": ident, "title": title[:200], "statement": long_text,
                                 "risk_if_wrong": col("risk if wrong"),
                                 "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "DEP":
        plan.add("dependencies", {"id": ident, "title": title[:200], "statement": long_text,
                                  "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "OQ":
        plan.add("open_questions", {"id": ident, "title": title[:200],
                                    "question": long_text,
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
        plan.add("decisions", {"id": ident, "title": title[:200], "decision": long_text,
                               "rationale": col("rationale", "rationale (short)"),
                               "lifecycle_status": status,
                               "promoted_to": promoted,
                               "custom_attributes": attrs})
    elif prefix == "RISK":
        risk_state = RISK_STATE_MAP.get(_norm_status_key(col("status")))
        plan.add("risks", {"id": ident, "title": title[:200], "description": long_text,
                           "probability": col("likelihood", "probability"),
                           "impact": col("impact"), "mitigation": col("mitigation"),
                           "lifecycle_status": status,
                           **({"risk_state": risk_state} if risk_state else {}),
                           "custom_attributes": attrs})
    elif prefix == "HYP":
        plan.add("hypotheses", {"id": ident, "title": title[:200], "statement": long_text,
                                "lifecycle_status": status, "custom_attributes": attrs})
    elif prefix == "KPI":
        plan.add("kpis", {"id": ident, "title": title[:200],
                          "measure": col("measurement method", "measure",
                                         "measurement", "cadence"),  # C24/D-3
                          "target": col("target"), "lifecycle_status": status,
                          "custom_attributes": attrs})
    elif prefix == "STK":
        plan.add("stakeholders", {"id": ident, "name": title[:200],
                                  "role": col("role"),  # C24/D-3
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
        phase_cell = _cell(row, t.col_index(["phase"])) or ""
        phase = next((i for i in _ids_in(phase_cell) if i.startswith("PH-")), None)
        if phase is None and re.fullmatch(r"\d+", phase_cell.strip()):
            cand = f"PH-{phase_cell.strip()}"
            if plan.has(cand):  # C24/D-3: bare phase numbers resolve when the phase exists
                phase = cand
        plan.add("wbs_items", {"id": ident, "title": title[:200], "phase_id": phase,
                               "lifecycle_status": status, "custom_attributes": attrs})
        for ref in _ids_in(_cell(row, t.col_index(["realises", "realizes"])) or ""):
            plan.edges.add((ident, ref, "implements"))
    elif prefix == "AC":
        verifies = _cell(row, t.col_index(["verifies"])) or ""
        req = next((i for i in _ids_in(verifies) if i.split("-")[0] in ("FR", "NFR")), None)
        # statement never inherits the title cap (field-evidence C12: every ACMP AC
        # exceeded 120 chars) — prefer the raw long-form cell, whatever it was headed.
        raw_stmt = _cell(row, t.col_index(
            ["given / when / then", "criterion", "statement"]))
        plan.add("acceptance_criteria", {
            "id": ident, "title": title[:120], "statement": raw_stmt or long_text,
            "requirement_id": req,
            # C24/D-12: imported ACs land Proposed, never Approved — the immutability
            # trigger freezes slice_id at Approved, and v1 has no slices; Proposed keeps
            # the structure completable (bind, then approve). The FR bump stays: the
            # Met-verdict cascade then advances finished requirements correctly.
            "lifecycle_status": status if status != "Draft" else "Proposed",
            "custom_attributes": attrs})
        for ref in _ids_in(verifies):
            plan.edges.add((ident, ref, "verifies"))
    elif prefix == "TEST":
        for ref in _ids_in(_cell(row, t.col_index(["verifies"])) or ""):
            plan.edges.add((ident, ref, "tests"))
        plan.add("tests", {"id": ident, "title": title[:200],
                           "kind": col("kind", "type"),  # C24/D-3 starvation alias
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


def _map_adr(plan: Plan, pf) -> bool:
    """Returns True when the file became an adrs row; False = caller falls through to the
    narrative catch-all (C17: an adrs/README.md index is prose worth keeping, not a loss)."""
    fm = pf.front_matter
    ident = (fm.get("id") or "").strip()
    status_src = fm.get("status")
    if not ident.startswith("ADR-"):
        # MADR fallback (field-evidence C12): Keystone v1 itself emitted
        # `# ADR-0031: title` + `- Status: Accepted` with no YAML front-matter —
        # requiring front-matter migrated real packages as ZERO ADRs, undetected.
        head = re.search(r"^#\s+(ADR-\d+)\b[:.]?\s*", pf.text, re.M)
        if not head:
            plan.unmapped.append(f"{pf.rel}: ADR file without front-matter or heading id")
            return False
        ident = head.group(1)
        bullet = re.search(r"^[-*]\s*\**Status\**\s*:\s*([A-Za-z-]+)", pf.text, re.M | re.I)
        status_src = bullet.group(1) if bullet else status_src
    title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
    sections = dict(_sections(pf.text))

    def section(*needles: str, exclude: str = "") -> str | None:
        for needle in needles:  # first needle that matches any heading wins
            hit = next((v for k, v in sections.items()
                        if needle in k.lower() and (not exclude or exclude not in k.lower())),
                       None)
            if hit is not None:
                return hit
        return None

    plan.add("adrs", {
        "id": ident, "title": _clean_line(title_m.group(1)) if title_m else ident,
        "context": section("context"),
        # MADR files head both "Decision Drivers" and "Decision Outcome": prefer the
        # outcome, never the drivers list (field-evidence C12/D4).
        "decision": section("decision outcome", "decision", exclude="driver"),
        "consequences": section("consequence"),
        "lifecycle_status": _status(status_src, "Proposed", plan=plan, ident=ident),
        "custom_attributes": json.dumps({"v1": {"front_matter": dict(fm)}},
                                        ensure_ascii=False)})
    return True


def _map_exp_poc(plan: Plan, pf) -> bool:
    fm = pf.front_matter
    ident = (fm.get("id") or "").strip()
    table = "experiments" if ident.startswith("EXP-") else "pocs"
    if not ident:
        plan.unmapped.append(f"{pf.rel}: experiment/POC file without front-matter id")
        return False
    title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
    plan.add(table, {
        "id": ident, "title": _clean_line(title_m.group(1)) if title_m else ident,
        "verdict": "Pending",
        "lifecycle_status": _status(fm.get("status"), "Proposed", plan=plan, ident=ident),
        "custom_attributes": json.dumps(
            {"v1": {"front_matter": dict(fm), "body": pf.text}}, ensure_ascii=False)})
    return True


def parse_v1(source: Path, status_map: dict[str, str] | None = None) -> Plan:
    plan = Plan()
    # Operator status overrides (C17): keys normalized exactly as _status normalizes
    # cells, so a supplied "resolved" matches a register's "Resolved".
    plan.status_map = {_norm_status_key(k): v for k, v in (status_map or {}).items()}
    files = vp.load_package(source)
    by_rel = {pf.rel: pf for pf in files}

    manifest = json.loads(by_rel["manifest.json"].text)
    raw_name = manifest.get("package") or manifest.get("project") or source.name
    plan.manifest_counts = manifest.get("identifier_counts") or {}
    state = {}
    if "keystone-state.json" in by_rel:
        state = json.loads(by_rel["keystone-state.json"].text)
    depth = ((state.get("project_profile") or {}).get("mode") or "").strip()
    # "profile" stays in extras deliberately (field-evidence C13): _norm_profile is lossy
    # ("software-platform (on-prem)" -> unknown) and the raw string must survive somewhere.
    extras = {k: v for k, v in manifest.items()
              if k not in ("package", "project", "mode", "mvp_definition",
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
        "created_at": manifest.get("generated_at") or manifest.get("generated")
        or "v1-migration",  # both spellings occur in real Keystone manifests (C12)
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
                for t in _tables(pf.text):
                    _map_matrix(plan, t)
            plan.skipped_files.append(pf.rel)  # derived views: regenerated in v2 (C13)
            continue
        if "acceptance-audit" in rel_l:
            audits_before = len(plan.audits)
            for t in _tables(pf.text):
                for row in t.rows:
                    ac = next((i for i in _ids_in(row[0]) if i.startswith("AC-")), None)
                    verdict = _cell(row, t.col_index(["verdict"]))
                    if ac and verdict in ("Met", "Partial", "Not-met", "Pending"):
                        # "Test ref" is Keystone's own evidence column head (C12); the
                        # remaining cells ride custom_attributes like every register row.
                        plan.audits.append({
                            "ac_id": ac, "verdict": verdict,
                            "evidence": _cell(row, t.col_index(["evidence", "test ref"])),
                            "custom_attributes": _row_attrs(t.headers, row)})
            plan.partial_files[pf.rel] = len(plan.audits) - audits_before
            continue
        if "deferred-work" in rel_l:
            # Ungoverned `D-nn` rows (Keystone's own convention) are invisible to the ID
            # regex — 23 live items vanished from ACMP with no trace (field-evidence C13).
            dw_before = len(plan.rows.get("deferred_work", []))
            for t in _tables(pf.text):
                for row in t.rows:
                    m = re.fullmatch(r"D-(\d+)", row[0].strip().strip("*"))
                    if not m:
                        continue
                    # C24/D-4: key on the PARSED number, never on row position — an
                    # unsorted register once silently shifted five ids, breaking every
                    # D-nn reference in logs, ADRs and commits.
                    legacy, num = m.group(0), int(m.group(1))
                    dw_id = f"DW-{num:03d}"
                    if plan.has(dw_id):  # duplicate source number: next free, noted
                        while plan.has(dw_id):
                            num += 1
                            dw_id = f"DW-{num:03d}"
                        plan.unmapped.append(f"{legacy}: duplicate number — assigned "
                                             f"{dw_id}")
                    plan.dw_crosswalk.setdefault(legacy, dw_id)  # first mapping wins
                    sev = (_cell(row, t.col_index(["severity"])) or "").lower()
                    # C26 (§A residual): carry the v1 Status onto the DW enum so a
                    # re-migration never needs the Done/Activated truth-up again.
                    raw_dw_status = _cell(row, t.col_index(["status"]))
                    dw_status = {"Open": "Open", "Activated": "Activated",
                                 "Scheduled": "Scheduled", "Done": "Done",
                                 "Won't-do": "Won't-do", "Won't do": "Won't-do",
                                 "Wont-do": "Won't-do"}.get(
                        _norm_status_key(raw_dw_status))
                    alias = (None if dw_status else
                             {"In progress": "Activated",
                              "In-progress": "Activated"}.get(
                                 _norm_status_key(raw_dw_status)))
                    if alias:
                        # C28 (B1'): a semantic alias is a judgment call too — findings_7
                        # caught the C27 honesty-symmetry comment being untrue while
                        # `In progress` sat in the silent exact map. Noted like the
                        # prose carries.
                        dw_status = alias
                        plan.unmapped.append(f"{legacy}: status {alias!r} carried from "
                                             f"semantic alias {raw_dw_status!r}")
                    elif raw_dw_status and dw_status is None:
                        # C27 (B1): real registers write prose in the Status cell —
                        # `**✅ Done 2026-07-12 (P9)** — narrative` is still a Done.
                        # Prefix-match the enum word after stripping leading
                        # punctuation/emoji; a prose carry is NOTED, never a
                        # silent judgment call in the mapping.
                        pm = re.match(r"\W*(Open|Activated|Scheduled|Done|Won'?t.?do)\b",
                                      raw_dw_status, re.IGNORECASE)
                        if pm:
                            dw_status = {"open": "Open", "activated": "Activated",
                                         "scheduled": "Scheduled",
                                         "done": "Done"}.get(pm.group(1).lower(),
                                                             "Won't-do")
                            plan.unmapped.append(
                                f"{legacy}: status {dw_status!r} carried from prose "
                                f"cell {raw_dw_status!r}")
                        else:
                            plan.unmapped.append(f"{legacy}: deferred-work status "
                                                 f"{raw_dw_status!r} outside the enum "
                                                 "— left Open")
                    plan.add("deferred_work", {
                        "id": dw_id,
                        **({"status": dw_status} if dw_status else {}),
                        "title": (_cell(row, t.col_index(
                            ["deferred item", "item", "description", "title", "work"]))
                            or _clean_line(" ".join(row[1:2]))),
                        "severity": sev if sev in ("critical", "high", "medium", "low")
                        else "medium",
                        "activation_trigger": _cell(row, t.col_index(
                            ["activation trigger", "trigger", "trigger to activate",
                             "activate when"])),  # C24/D-3 starvation alias
                        "source_kind": "brief", "source_span": f"v1:{pf.rel}",
                        "custom_attributes": _row_attrs(t.headers, row)})
            plan.partial_files[pf.rel] = (len(plan.rows.get("deferred_work", []))
                                          - dw_before)
            continue
        if rel_l.startswith("adrs/"):
            if _map_adr(plan, pf):
                continue  # success: rows-only; failure falls through to the catch-all (C17)
        elif rel_l.startswith(("experiments/", "pocs/")):
            if _map_exp_poc(plan, pf):
                continue
        elif "/diagrams/" in rel_l:
            stem = Path(rel_l).stem
            if stem in DIAGRAM_CLASS:
                dia_seq += 1
                plan.add("diagrams", {"id": f"DIA-{dia_seq:03d}", "kind": stem,
                                      "title": f"{stem} diagram", "body": pf.text,
                                      "generation_class": DIAGRAM_CLASS[stem]})
                continue
            # unknown diagram kind: fall through to the narrative catch-all (C17 —
            # listed-AND-preserved beats listed-only)

        prompt = next((k for s, k in PROMPT_KINDS if s in rel_l), None)
        if prompt:
            prm_seq += 1
            title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
            plan.add("prompts", {"id": f"PRM-{prm_seq:03d}", "prompt_kind": prompt,
                                 "title": _clean_line(title_m.group(1)) if title_m else prompt,
                                 "body": pf.text})

        # register tables anywhere (incl. KPI/STK tables inside the charter)
        rows_before = sum(len(v) for v in plan.rows.values())
        for t in _tables(pf.text):
            id_col = t.col_index(vp.ID_HEADERS)
            if id_col is None:
                id_col = vp._guess_id_column(t)
            if id_col is None:
                continue
            for row in t.rows:
                token = next(iter(_ids_in(row[id_col] if id_col < len(row) else "")), None)
                if token and not plan.has(token):
                    _map_register_row(plan, token.split("-")[0], token, t, row,
                                      id_col=id_col, src=pf.rel)
        rows_after = sum(len(v) for v in plan.rows.values())
        produced_rows = rows_after > rows_before

        kind = next((k for s, k in NARRATIVE_KINDS if s in pf.rel), None)
        if kind is None and not prompt:
            # C24/D-6 (reverses the 018 rows-only choice — field evidence won): rows and
            # prose are NOT alternatives. A register file's narrative (phase goals, exit
            # gates, legacy token maps) migrates alongside its rows as an 'other' doc.
            kind = "other"
        if produced_rows:
            plan.partial_files[pf.rel] = rows_after - rows_before
        if kind and not prompt:
            doc_seq += 1
            doc_id = f"DOC-{doc_seq:03d}"
            title_m = re.search(r"^#\s+(.+)$", pf.text, re.M)
            v1_attrs = {"path": pf.rel}
            if pf.front_matter:  # C17: the one place a v1 value was neither mapped nor kept
                v1_attrs["front_matter"] = dict(pf.front_matter)
            plan.add("narrative_documents", {
                "id": doc_id, "doc_kind": kind,
                "title": _clean_line(title_m.group(1)) if title_m else pf.rel,
                "lifecycle_status": _status(pf.front_matter.get("status"),
                                            plan=plan, ident=doc_id),
                "custom_attributes": json.dumps({"v1": v1_attrs}, ensure_ascii=False)})
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
        raw_line = text[occ.line - 1].strip() if 0 < occ.line <= len(text) else ""
        title = _clean_line(raw_line) if raw_line else occ.ident
        prefix = occ.prefix
        # C24/D-0 (review finding): weak-def rows were the ONLY rows with no
        # custom_attributes — the cleaned title was the sole surviving text (ACMP's 133
        # damaged WBS leaves). The raw defining line is now always preserved.
        weak_attrs = json.dumps(
            {"v1": {"raw_line": raw_line, "source": f"{occ.rel}:{occ.line}"}},
            ensure_ascii=False)
        if prefix == "PH":
            num = re.search(r"(\d+)", occ.ident)
            plan.add("phases", {"id": occ.ident, "title": title,
                                "sort_order": int(num.group(1)) if num else 0,
                                "lifecycle_status": "Approved",
                                "custom_attributes": weak_attrs})
        elif prefix == "WBS":
            plan.add("wbs_items", {"id": occ.ident, "title": title,
                                   "lifecycle_status": "Approved",
                                   "custom_attributes": weak_attrs})
        elif prefix in ("FR", "NFR"):
            plan.add("requirements", {
                "id": occ.ident, "kind": "functional" if prefix == "FR" else "non-functional",
                "title": title, "statement": raw_line or None,
                "mvp": 0, "lifecycle_status": "Approved",
                "source_kind": "inferred",
                "source_span": f"v1 weak definition {occ.rel}:{occ.line}",
                "custom_attributes": weak_attrs})
        elif prefix == "MS":
            plan.unmapped.append(f"{occ.ident}: weak milestone definition without a phase")
        elif prefix in ("KPI", "STK", "CON", "INV", "ASM", "DEP", "OQ", "DEC", "RISK",
                        "HYP", "AC", "TEST"):
            table = {"KPI": "kpis", "STK": "stakeholders", "CON": "constraints",
                     "INV": "invariants", "ASM": "assumptions", "DEP": "dependencies",
                     "OQ": "open_questions", "DEC": "decisions", "RISK": "risks",
                     "HYP": "hypotheses", "AC": "acceptance_criteria", "TEST": "tests"}[prefix]
            row = {"id": occ.ident, "lifecycle_status": "Approved",
                   "custom_attributes": weak_attrs}
            row["name" if table == "stakeholders" else "title"] = title
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

    # C24/D-9 (narrow): a phase table without a Status column often has the status in
    # prose — ONLY a section whose HEADING contains the exact PH- id, with a
    # `Status: <word>` line in its body, qualifies; everything else keeps the
    # status_defaulted note.
    for (src, fam) in [k for k in plan.status_defaulted if k[1] == "PH"]:
        pf = by_rel.get(src)
        if pf is None:
            continue
        resolved = 0
        for heading, body in _sections(pf.text):
            ph = next((r["id"] for r in plan.rows.get("phases", [])
                       if r["id"] in heading
                       # C26/B1-adjacent: headings often carry the phase TITLE, not the
                       # id ("## Phase 0 — Discovery & Validation") — meaningful now
                       # that titles are real (post-020). Id match stays first.
                       or (len(r.get("title") or "") >= 4
                           and (r.get("title") or "") in heading)), None)
            # C27 (B2): the 020 pattern fired ZERO times on the fixture that motivated
            # it — status sentences end `- **Exit gate.** …` bullets (never at line
            # start, so `^` never matched) and carry parenthetical qualifiers
            # (`complete (delivered …)`). Unanchored with a \b guard (ExitStatus: must
            # not match) and `(` joins the capture terminators.
            m = re.search(r"\**\bStatus\b\**\s*:\s*\**([A-Za-z][A-Za-z -]*?)\**\s*[.(\n]",
                          body + "\n") if ph else None
            if not m:
                continue
            for r in plan.rows["phases"]:
                if r["id"] == ph:
                    r["lifecycle_status"] = _status(m.group(1), "Approved",
                                                    plan=plan, ident=ph)
                    resolved += 1
        remaining = plan.status_defaulted[(src, fam)] - resolved
        if remaining > 0:
            plan.status_defaulted[(src, fam)] = remaining
        else:
            plan.status_defaulted.pop((src, fam), None)

    # A family that both migrated rows AND carries a recorded omission is a stale
    # manifest entry (field-evidence C13: ACMP's milestones were "omitted" beside 6 MS
    # rows) — the rows win, the omission is dropped.
    plan.omissions = [(etype, reason) for etype, reason in plan.omissions
                      if not plan.rows.get(ENTITY_TABLES.get(etype, etype), [])]
    return plan


# --------------------------------------------------------------------------- stages 4-5

INSERT_ORDER = ["requirements", "constraints", "invariants", "assumptions", "dependencies",
                "open_questions", "adrs", "decisions", "risks", "hypotheses", "experiments",
                "pocs", "kpis", "stakeholders", "phases", "milestones", "wbs_items",
                "acceptance_criteria", "tests", "deferred_work", "narrative_documents",
                "document_sections", "diagrams", "prompts"]



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
                        "INSERT INTO audit_verdicts (id, ac_id, verdict, evidence,"
                        " iteration, custom_attributes) VALUES (?, ?, ?, ?, 1, ?)",
                        (f"AV-{seq:03d}", audit["ac_id"], audit["verdict"],
                         audit["evidence"], audit.get("custom_attributes")))
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

    # ------------------------------------------------------------------ C23: FIDELITY
    # Column-level checks that row-level validation is structurally blind to (C24: the
    # report that found 12 degradation classes all row-level checks had certified).
    _TITLE_CAP_TABLES = ("requirements", "constraints", "invariants", "assumptions",
                         "dependencies", "open_questions", "decisions", "risks",
                         "hypotheses", "kpis", "phases", "milestones", "wbs_items",
                         "tests", "deferred_work")
    caps = [("acceptance_criteria", "title", 120), ("stakeholders", "name", 200)]
    caps += [(t, "title", 200) for t in _TITLE_CAP_TABLES]
    truncations = []
    for table, field, cap in caps:  # length histogram: mass at exactly the cap
        (n,) = conn.execute(f"SELECT COUNT(*) FROM {table}"
                            f" WHERE LENGTH({field}) = ?", (cap,)).fetchone()
        if n:
            truncations.append({"family": table, "field": field,
                                "count_at_cap": n, "cap": cap})
    _STARVE_SKIP = {"id", "lifecycle_status", "custom_attributes", "last_referenced",
                    "source_kind", "source_span", "introduced_in", "retired_in",
                    "disposition", "disposition_reason_ref", "superseded_by", "mvp",
                    "sort_order", "iteration", "parent_id", "slice_id", "risk_state",
                    "verdict", "status", "severity"}
    starvation, field_mapping = [], {}
    for table in sorted(set(ENTITY_TABLES.values())):
        cols_all = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        if "custom_attributes" not in cols_all:
            continue  # write-only surfaces (trace_edges, omissions) carry no attrs
        (total,) = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        if total < 5:
            continue
        attr_keys: set[str] = set()
        for (attrs,) in conn.execute(f"SELECT custom_attributes FROM {table}"
                                     " WHERE custom_attributes IS NOT NULL LIMIT 50"):
            try:
                attr_keys |= {k.lower() for k in (json.loads(attrs).get("v1") or {})
                              if isinstance(k, str)}
            except ValueError:
                pass
        cols = cols_all
        extra = sorted(k for k in attr_keys
                       if k not in {c.lower() for c in cols}
                       and k not in ("raw_line", "source", "path", "front_matter"))
        if extra:
            field_mapping[table] = extra[:8]  # v1 columns riding the attribute bag
        for col_name in cols:
            if col_name in _STARVE_SKIP:
                continue
            (nulls,) = conn.execute(f"SELECT COUNT(*) FROM {table}"
                                    f" WHERE {col_name} IS NULL").fetchone()
            if total and nulls / total >= 0.9:
                token = col_name.split("_")[0]
                hit = next((k for k in sorted(attr_keys) if token in k), None)
                if hit:  # the value exists in the bag while the typed column starves
                    starvation.append({"family": table, "column": col_name,
                                       "null_rate": round(nulls / total, 2),
                                       "v1_key": hit})
    (open_wbs,) = conn.execute("SELECT COUNT(*) FROM v_backlog").fetchone()
    conn.close()
    ok = not missing and all(not f for f in gates.values())
    return {"ok": ok, "identifier_gaps": missing, "count_deltas": deltas,
            "gate_failures": {g: f for g, f in gates.items() if f},
            "fidelity_ledgers": {"truncations": truncations,
                                 "column_starvation": starvation,
                                 "field_mapping": field_mapping},
            "execution_state_note": (
                f"{open_wbs} work item(s) land open in v_backlog — imported packages "
                "carry no execution state; sync verdicts/progress via update mode"
                if open_wbs else None),
            "unmapped": plan.unmapped}


# --------------------------------------------------------------------------- driver

def _group(entries: list[dict], key, labels: tuple) -> list[dict]:
    """C21 ledger ergonomics: group rows into operator decision units; ids expanded only
    for small groups (<=10) so a 77-row mechanical group stays one line."""
    groups: dict[tuple, list[str]] = {}
    for e in entries:
        groups.setdefault(key(e), []).append(e["id"])
    out = []
    for k, ids in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        g = dict(zip(labels, k))
        g["count"] = len(ids)
        if len(ids) <= 10:
            g["ids"] = ids
        out.append(g)
    return out


def _apply_patch(plan: Plan, patch_path: str) -> dict:
    """Merge-by-id row overrides applied to the parsed plan BEFORE populate (D1): the
    blessed repair path for migration gaps. Post-hoc mutation stays impossible —
    immutability triggers are never bypassed. Echoed in the preview."""
    data = json.loads(Path(patch_path).read_text(encoding="utf-8"))
    updated = added = 0
    for table, rows in data.items():
        if table == "audits":
            by_ac = {a["ac_id"]: a for a in plan.audits}
            for override in rows:
                if override.get("ac_id") in by_ac:
                    by_ac[override["ac_id"]].update(override)
                    updated += 1
            continue
        existing = {r.get("id"): r for r in plan.rows.get(table, [])}
        for override in rows:
            if override.get("id") in existing:
                existing[override["id"]].update(override)
                updated += 1
            else:
                plan.add(table, override)
                added += 1
    return {"path": patch_path, "updated": updated, "added": added}


_CUTOVER_NEXT = (
    "cutover (C15): open the package and run handoff_emit(<repo>) — it writes the "
    "executor .mcp.json and the CLAUDE.md tracking note. Then update stale v1 pointers "
    "in the repo's AGENTS.md/CLAUDE.md and freeze the v1 source tree; until then two "
    "sources of truth coexist.")


def run_migration(source_dir: str, dest_root: str | Path, name: str | None = None,
                  confirm: bool = False, allow_zero: list[str] | None = None,
                  patch: str | None = None,
                  status_map: dict[str, str] | None = None) -> dict:
    source = Path(source_dir)
    if not source.is_dir():
        return {"ok": False, "stage": "preflight", "error": f"{source_dir} is not a directory"}
    bad_values = sorted(set((status_map or {}).values()) - LIFECYCLE)
    if bad_values:
        return {"ok": False, "stage": "preflight",
                "error": f"status_map values outside the lifecycle vocabulary: {bad_values}"
                         f" (allowed: {', '.join(sorted(LIFECYCLE))})"}
    pre = preflight(source)
    if not pre["ok"]:
        return pre
    plan = parse_v1(source, status_map=status_map)
    patch_report = _apply_patch(plan, patch) if patch else None
    name = _kebab(name or plan.package["name"])

    # Stage-3 parity (field-evidence C13/RC3): the operator confirms on everything the
    # tool knows — parsed-vs-manifest deltas and file-level outcomes, not just id noise.
    parsed = {}
    for ident in plan.defined:
        prefix = ident.split("-")[0]
        parsed[prefix] = parsed.get(prefix, 0) + 1
    deltas = {p: {"manifest": n, "parsed": parsed.get(p, 0)}
              for p, n in plan.manifest_counts.items() if parsed.get(p, 0) != n}
    zero_families = sorted(p for p, n in plan.manifest_counts.items()
                           if n and not parsed.get(p))
    preview = {"stage": "preview", "package": name, "counts": plan.counts(),
               "edges": len(plan.edges), "audit_verdicts": len(plan.audits),
               "omissions": len(plan.omissions),
               "manifest_counts": plan.manifest_counts, "count_deltas": deltas,
               "zero_families": zero_families,
               "partial_files": {k: plan.partial_files[k]
                                 for k in sorted(plan.partial_files)},
               "skipped_files": sorted(plan.skipped_files),
               # C17 honesty ledgers: with no status_map, status_coerced shows the DEFAULT
               # proposals — the operator confirms/overrides them on the confirm call.
               # C21: the grouped views are the operator decision units (a 21-row ledger is
               # ~6 decisions); the row-granular list stays for audit.
               "status_coerced": plan.status_coerced,
               "status_coerced_groups": _group(plan.status_coerced,
                                               lambda e: (e["original"], e["coerced"]),
                                               ("original", "proposed")),
               # C28 (B2'): derived from the per-entry bases — "mixed" when a supplied
               # map covered only some of the coerced words (was: map-presence only,
               # which mislabeled semantic-default coercions as operator-confirmed).
               "status_coerced_basis": (
                   ("status_map" if bases == {"status_map"} else
                    "mixed" if "status_map" in bases else "defaults")
                   if (bases := {e["basis"] for e in plan.status_coerced})
                   else ("status_map" if status_map else "defaults")),
               "title_fallbacks": _group(plan.title_fallbacks,
                                         lambda e: (e["family"],), ("family",)),
               "status_defaulted": [
                   {"file": f, "family": fam, "count": n,
                    "defaulted_to": "Proposed" if fam in ("DEC", "AC") else "Approved"}
                   for (f, fam), n in sorted(plan.status_defaulted.items())],
               "dw_crosswalk": dict(sorted(plan.dw_crosswalk.items())),
               "validator": pre.get("validator"),
               "patch": patch_report, "unmapped": plan.unmapped}
    # C24/D-0 standing correction: title_fallbacks is a DATA-LOSS signal, not noise —
    # grouping it in 2.3.0 made the symptom quieter without anyone noticing. Say so.
    for g in preview["title_fallbacks"]:
        g["warning"] = ("data-loss signal: no recognizable title column — titles are "
                        "markdown-stripped and capped at 200; the full raw text is in "
                        "the long-form column or custom_attributes.v1")
    if not confirm:
        return {"ok": True, **preview,
                "next": "re-run with confirm=true to populate (operator gate, stage 3)"}
    unacknowledged = sorted(set(zero_families) - set(allow_zero or []))
    if unacknowledged:
        # Family-zero tripwire (C13): a whole family parsing to zero against a nonzero
        # manifest count is almost always silent loss, not reality (ACMP: 33 ADRs -> 0).
        return {**preview, "ok": False, "stage": "populate-refused",
                "error": "whole famil(y/ies) parsed to zero against a nonzero manifest "
                         "count: %s — fix the source (or the parser) or acknowledge "
                         "deliberately with allow_zero=[...]" % ", ".join(unacknowledged)}
    pop = populate(plan, Path(dest_root), name)
    if not pop["ok"]:
        return pop
    fid = fidelity(plan, Path(dest_root) / name)
    return {"ok": fid["ok"], "stage": "post-flight", "preview": preview,
            "package_dir": pop["package_dir"], "fidelity": fid,
            "next": _CUTOVER_NEXT if fid["ok"] else None,
            "note": None if fid["ok"] else
            "fidelity gaps are reported, never auto-resolved — review before use"}
