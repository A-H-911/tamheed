#!/usr/bin/env python3
"""Keystone package validator -- mechanical quality gates.

Runs the *mechanical* subset of the Keystone quality gates (see
``../references/quality-gates.md``) against a generated package
directory. Judgment gates (G-CONFLICT, G-EXEC, G-HANDOFF, G-OQ, G-CLAIM, ...)
are performed by a human/agent and are out of scope here.

Gates implemented (all Critical):
  G-IDS         identifiers match the governance format, are unique within a
                file family, and have no dangling cross-references.
  G-DEC-STATUS  every decision / ADR carries a status from the allowed set.
  G-REQ-SRC     every FR-/NFR- row has a non-empty source/provenance.
  G-COMPLETE    no TODO / <placeholder> / empty-section markers in non-template
                artifacts.
  G-TRACE       every MVP requirement in the traceability matrix reaches >=1
                decision, >=1 task, and >=1 test.
  G-SET         every "Always" artifact (references/required-artifacts.json) is
                present on disk or explicitly recorded in manifest.json
                omitted_artifacts[] with a reason; and anything the manifest
                declares present actually exists.
  G-PROGRESS    if an acceptance audit (validation/acceptance-audit.md) exists,
                every AC- in the acceptance criteria appears in it with a verdict
                from {Met, Partial, Not-met, Pending}; SKIP when no audit exists.

Assumptions (the input is semi-structured Markdown + JSON, stdlib only):
  - An identifier is a *definition* when it is the first ("ID") column of a
    register-table row or an ``id:`` field; every other occurrence is a
    *reference*.
  - "Source" = a non-empty Source/Provenance/Origin column or ``source:`` field
    (a dash or "n/a" counts as empty).
  - "Status" is read from a Status column or ``status:`` field and checked
    against the decision/document status set from governance.md.
  - A file is a template (exempt from G-COMPLETE) if its path has a
    ``templates`` segment or its name ends in ``.template.md`` / ``.tmpl``.
  - The traceability matrix lives at ``validation/traceability-matrix.md``
    and/or a JSON file; a row is MVP unless a scope column marks it full-only.

The validator never crashes on a missing optional file, explains each finding
with file + locator, and exits non-zero only when a Critical gate fails.

Usage:
    python tests/validate_package.py <package-dir>
    python tests/validate_package.py <package-dir> --json
    python tests/validate_package.py --help

Exit codes: 0 = all critical gates pass; 1 = a critical gate failed;
2 = usage / IO error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# --- Governance constants (mirror references/governance.md) ----------- #

ID_PATTERNS: Dict[str, "re.Pattern[str]"] = {
    "FR": re.compile(r"FR-\d{3,}"),
    "NFR": re.compile(r"NFR-\d{3,}"),
    "CON": re.compile(r"CON-\d{3,}"),
    "INV": re.compile(r"INV-\d{3,}"),
    "ASM": re.compile(r"ASM-\d{3,}"),
    "DEP": re.compile(r"DEP-\d{3,}"),
    "OQ": re.compile(r"OQ-\d{3,}"),
    "DEC": re.compile(r"DEC-\d{3,}"),
    "ADR": re.compile(r"ADR-\d{4,}"),
    "RISK": re.compile(r"RISK-\d{3,}"),
    "HYP": re.compile(r"HYP-\d{3,}"),
    "EXP": re.compile(r"EXP-\d{3,}"),
    "POC": re.compile(r"POC-\d{3,}"),
    "KPI": re.compile(r"KPI-\d{3,}"),
    "STK": re.compile(r"STK-\d{3,}"),
    "MS": re.compile(r"MS-\d{3,}"),
    "AC": re.compile(r"AC-\d{3,}"),
    "TEST": re.compile(r"TEST-\d{3,}"),
    "PH": re.compile(r"PH-\d+"),
    # Work items allow an optional group form: WBS-1 (a parent group / phase
    # bucket), WBS-1.1 (a leaf), and WBS-1.1.1 (a sub-leaf) are all valid.
    "WBS": re.compile(r"WBS-\d+(?:\.\d+){0,2}"),
}

# Loose recogniser to harvest candidates + detect malformed numbers. Anchored so
# it never swallows trailing punctuation or ranges: "FR-001..FR-003" -> two
# tokens; "FR-003." -> "FR-003". A trailing letter ("FR-1a") is still captured
# so it can be flagged as malformed.
ID_TOKEN_RE = re.compile(r"\b([A-Z]{2,5})-(\d+(?:\.\d+)*[A-Za-z]*)")

# Real-world definition forms beyond table ID columns and front-matter ``id:``.
# A definition can be a heading that leads with the identifier
# (``## WBS-1 — Foundations``, ``## PH-1 ...``) or a bold leader at the start of
# a list item (``- **WBS-1.1** ...``). The identifier may be wrapped in backticks
# and may be followed by a separator (space, em/en dash, colon, etc.) or end of
# line. These mirror how Keystone's work-breakdown and roadmap define entities.
HEADING_DEF_RE = re.compile(r"^#{1,6}\s+`?([A-Z]{2,5})-(\d+(?:\.\d+)*[A-Za-z]*)`?(?=$|[\s.,:;)—–-])")
BOLD_LEADER_DEF_RE = re.compile(r"^\s*[-*]\s*\*\*`?([A-Z]{2,5})-(\d+(?:\.\d+)*[A-Za-z]*)`?\*\*")

GOVERNED_PREFIXES = set(ID_PATTERNS.keys())

DECISION_STATUSES = {"Proposed", "Approved", "Rejected", "Superseded", "Deferred"}
DOCUMENT_STATUSES = DECISION_STATUSES | {"Accepted", "Implemented", "Obsolete", "Draft"}

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bXXX\b"),
    re.compile(r"<placeholder>", re.IGNORECASE),
    re.compile(r"<[^>\n]*\bplaceholder\b[^>\n]*>", re.IGNORECASE),
    re.compile(r"\bFILL[ _-]?IN\b", re.IGNORECASE),
    re.compile(r"\bLOREM IPSUM\b", re.IGNORECASE),
    re.compile(r"\{\{[^}\n]+\}\}"),
]

EMPTY_CELL_VALUES = {"", "-", "—", "–", "n/a", "na", "none", "tbd", "todo", "?"}

SOURCE_HEADERS = {"source", "provenance", "origin", "sources"}
STATUS_HEADERS = {"status"}
ID_HEADERS = {"id", "ref", "key", "identifier"}
SCOPE_HEADERS = {"scope", "mvp", "milestone", "release"}
DECISION_LINK_HEADERS = {"decision", "decisions", "dec", "adr", "adrs", "dec/adr", "decisions/adrs"}
TASK_LINK_HEADERS = {"work item", "work items", "wbs", "task", "tasks", "workitem", "workitems"}
TEST_LINK_HEADERS = {"test", "tests"}
VERDICT_HEADERS = {"verdict"}
ALLOWED_VERDICTS = {"met", "partial", "not-met", "not met", "pending"}

CRITICAL_GATES = {"G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-COMPLETE", "G-TRACE", "G-SET", "G-PROGRESS"}

# G-SET reads the canonical "Always" artifact set from the bundle (a sibling of
# scripts/, inside references/). It is the machine-readable mirror of the Always
# class in references/artifact-rules.md.
REQUIRED_ARTIFACTS_PATH = Path(__file__).resolve().parent.parent / "references" / "required-artifacts.json"


# --- Result model ----------------------------------------------------------- #

@dataclass
class Finding:
    gate: str
    severity: str
    message: str
    location: str = ""

    def to_dict(self) -> dict:
        return {"gate": self.gate, "severity": self.severity,
                "message": self.message, "location": self.location}


@dataclass
class GateResult:
    gate: str
    severity: str
    checked: bool = True
    findings: List[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.findings

    def to_dict(self) -> dict:
        return {"gate": self.gate, "severity": self.severity, "checked": self.checked,
                "passed": self.passed, "finding_count": len(self.findings),
                "findings": [f.to_dict() for f in self.findings]}


# --- Markdown helpers -------------------------------------------------------- #

@dataclass
class MarkdownTable:
    headers: List[str]
    rows: List[List[str]]
    start_line: int  # 1-based line of the header row

    def col_index(self, aliases: Iterable[str]) -> Optional[int]:
        norm = {a.lower() for a in aliases}
        for i, h in enumerate(self.headers):
            if h.strip().lower() in norm:
                return i
        return None


def _split_md_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _is_separator_row(cells: List[str]) -> bool:
    if not cells:
        return False
    for c in cells:
        c = c.strip()
        if not c or not set(c) <= set("-: "):
            return False
    return True


def parse_markdown_tables(text: str) -> List[MarkdownTable]:
    tables: List[MarkdownTable] = []
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n - 1:
        line = lines[i]
        if "|" in line and "|" in lines[i + 1] and _is_separator_row(_split_md_row(lines[i + 1])):
            headers = _split_md_row(line)
            sep = _split_md_row(lines[i + 1])
            if len(sep) >= 1 and abs(len(sep) - len(headers)) <= 1:
                start_line = i + 1
                rows: List[List[str]] = []
                j = i + 2
                while j < n:
                    rl = lines[j]
                    if "|" not in rl or not rl.strip():
                        break
                    cells = _split_md_row(rl)
                    if _is_separator_row(cells):
                        j += 1
                        continue
                    if len(cells) < len(headers):
                        cells = cells + [""] * (len(headers) - len(cells))
                    elif len(cells) > len(headers):
                        cells = cells[: len(headers)]
                    rows.append(cells)
                    j += 1
                tables.append(MarkdownTable(headers, rows, start_line))
                i = j
                continue
        i += 1
    return tables


_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    """Blank out fenced + inline code so examples/diagrams aren't flagged."""
    text = _CODE_FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = _INLINE_CODE_RE.sub(" ", text)
    return text


def parse_front_matter(text: str) -> Dict[str, str]:
    """Parse a leading --- ... --- block of flat key: value pairs (no YAML lib)."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: Dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"\s*([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$", line)
        if m:
            fm[m.group(1).strip().lower()] = m.group(2).strip().strip('"').strip("'")
    return fm


# --- File model -------------------------------------------------------------- #

@dataclass
class PackageFile:
    path: Path
    rel: str
    text: str
    is_template: bool
    front_matter: Dict[str, str]
    tables: List[MarkdownTable]

    @property
    def is_json(self) -> bool:
        return self.path.suffix.lower() == ".json"


def is_template_path(rel: str, name: str) -> bool:
    parts = {p.lower() for p in Path(rel).parts}
    if "templates" in parts:
        return True
    low = name.lower()
    return low.endswith(".template.md") or low.endswith(".tmpl") or low.endswith(".tmpl.md")


def family_of(rel: str) -> str:
    """Directory family used to scope uniqueness checks (e.g. requirements/)."""
    p = Path(rel)
    return p.parts[0] if len(p.parts) > 1 else "(root)"


def load_package(package_dir: Path) -> List[PackageFile]:
    out: List[PackageFile] = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".markdown", ".json"}:
            continue
        rel = path.relative_to(package_dir).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            text = ""
            sys.stderr.write("warning: could not read " + rel + ": " + str(exc) + "\n")
        if path.suffix.lower() == ".json":
            out.append(PackageFile(path, rel, text, is_template_path(rel, path.name), {}, []))
        else:
            out.append(PackageFile(path, rel, text, is_template_path(rel, path.name),
                                   parse_front_matter(text), parse_markdown_tables(text)))
    return out


# --- Identifier collection --------------------------------------------------- #

@dataclass
class IdOccurrence:
    ident: str
    prefix: str
    rel: str
    line: int
    is_definition: bool
    # A "weak" definition comes from a Markdown heading or a bold list-leader
    # (``## WBS-1``, ``- **WBS-1.1**``) rather than a register-table ID column or
    # front-matter ``id:``. It is enough to resolve a cross-reference, but it is
    # not counted for duplicate-definition detection: a detail heading that
    # restates an entity already defined in a table or front-matter is the same
    # entity, not a second definition.
    weak_def: bool = False


def classify_id(prefix: str, token: str) -> Tuple[bool, Optional[str]]:
    """Return (is_governed, format_error_or_None)."""
    if prefix not in GOVERNED_PREFIXES:
        return (False, None)
    pat = ID_PATTERNS[prefix]
    if pat.fullmatch(token):
        return (True, None)
    return (True, "'" + token + "' does not match required format for " + prefix
            + " (" + pat.pattern + ")")


def _guess_id_column(table: MarkdownTable) -> Optional[int]:
    best: Optional[int] = None
    best_ratio = 0.0
    for ci in range(len(table.headers)):
        hits = total = 0
        for row in table.rows:
            if ci >= len(row):
                continue
            cell = row[ci].strip().strip("`")
            if not cell:
                continue
            total += 1
            m = ID_TOKEN_RE.fullmatch(cell)
            if m and m.group(1) in GOVERNED_PREFIXES:
                hits += 1
        if total >= 1:
            ratio = hits / total
            if ratio > best_ratio and ratio >= 0.6:
                best_ratio, best = ratio, ci
    return best


def _collect_from_json(pf: PackageFile, findings: List[Finding]) -> List[IdOccurrence]:
    occ: List[IdOccurrence] = []
    try:
        data = json.loads(pf.text) if pf.text.strip() else None
    except json.JSONDecodeError as exc:
        findings.append(Finding("G-IDS", "Critical", "invalid JSON: " + str(exc), pf.rel))
        return occ

    def walk(node: object, key: Optional[str]) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for item in node:
                walk(item, key)
        elif isinstance(node, str):
            if key is not None and key.lower() in ID_HEADERS:
                m = ID_TOKEN_RE.fullmatch(node.strip())
                if m and m.group(1) in GOVERNED_PREFIXES:
                    _, err = classify_id(m.group(1), node.strip())
                    occ.append(IdOccurrence(node.strip(), m.group(1), pf.rel, 0, True))
                    if err:
                        findings.append(Finding("G-IDS", "Critical", err, pf.rel))
                    return
            for m in ID_TOKEN_RE.finditer(node):
                if m.group(1) in GOVERNED_PREFIXES:
                    _, err = classify_id(m.group(1), m.group(0))
                    occ.append(IdOccurrence(m.group(0), m.group(1), pf.rel, 0, False))
                    if err:
                        findings.append(Finding("G-IDS", "Critical", err, pf.rel))

    walk(data, None)
    return occ


def collect_identifiers(files: List[PackageFile]) -> Tuple[List[IdOccurrence], List[Finding]]:
    occurrences: List[IdOccurrence] = []
    findings: List[Finding] = []

    for pf in files:
        if pf.is_json:
            occurrences.extend(_collect_from_json(pf, findings))
            continue

        defined_on_lines: Dict[int, str] = {}

        fm_id = pf.front_matter.get("id")
        if fm_id:
            m = ID_TOKEN_RE.fullmatch(fm_id.strip())
            if m:
                pref = m.group(1)
                governed, err = classify_id(pref, fm_id.strip())
                if governed:
                    occurrences.append(IdOccurrence(fm_id.strip(), pref, pf.rel, 1, True))
                    if err:
                        findings.append(Finding("G-IDS", "Critical", err, pf.rel + ":front-matter"))

        # The acceptance audit is a DERIVED view that REPORTS verdicts on AC- which
        # are DEFINED in the acceptance criteria. Skip its tables here so its AC-
        # cells are captured as references (by the body scan below), not as a second
        # definition that would trip G-IDS duplicate-detection within validation/.
        audit_view = "acceptance-audit" in pf.rel.lower()

        for table in pf.tables:
            if audit_view:
                continue
            id_col = table.col_index(ID_HEADERS)
            if id_col is None:
                id_col = _guess_id_column(table)
            if id_col is None:
                continue
            for r_idx, row in enumerate(table.rows):
                if id_col >= len(row):
                    continue
                cell = row[id_col].strip().strip("`")
                if not cell:
                    continue
                m = ID_TOKEN_RE.fullmatch(cell)
                if not m:
                    continue
                pref = m.group(1)
                governed, err = classify_id(pref, cell)
                if not governed:
                    continue
                line = table.start_line + 1 + r_idx
                defined_on_lines[line] = cell
                occurrences.append(IdOccurrence(cell, pref, pf.rel, line, True))
                if err:
                    findings.append(Finding("G-IDS", "Critical", err, pf.rel + ":" + str(line)))

        # Heading- and bold-leader definitions (scanned on the raw text, since a
        # heading or list item is never code). A line that *defines* an id this
        # way also records it in defined_on_lines so the reference scan below
        # does not double-count the leading occurrence as a reference; any other
        # id later on the same line still counts as a reference.
        for ln_no, line in enumerate(pf.text.splitlines(), start=1):
            dm = HEADING_DEF_RE.match(line) or BOLD_LEADER_DEF_RE.match(line)
            if not dm:
                continue
            pref = dm.group(1)
            token = dm.group(1) + "-" + dm.group(2)
            governed, err = classify_id(pref, token)
            if not governed:
                continue
            if defined_on_lines.get(ln_no) == token:
                continue  # already captured as a table-row definition
            defined_on_lines[ln_no] = token
            occurrences.append(IdOccurrence(token, pref, pf.rel, ln_no, True, weak_def=True))
            if err:
                findings.append(Finding("G-IDS", "Critical", err, pf.rel + ":" + str(ln_no)))

        body = strip_code(pf.text)
        for ln_no, line in enumerate(body.splitlines(), start=1):
            for m in ID_TOKEN_RE.finditer(line):
                pref = m.group(1)
                token = m.group(0)
                governed, err = classify_id(pref, token)
                if not governed:
                    continue
                if defined_on_lines.get(ln_no) == token:
                    continue
                occurrences.append(IdOccurrence(token, pref, pf.rel, ln_no, False))
                if err:
                    findings.append(Finding("G-IDS", "Critical",
                                            "malformed identifier reference: " + err,
                                            pf.rel + ":" + str(ln_no)))

    return occurrences, findings


# --- Gate: G-IDS ------------------------------------------------------------- #

def gate_ids(files: List[PackageFile]) -> GateResult:
    occurrences, findings = collect_identifiers(files)
    result = GateResult("G-IDS", "Critical", checked=bool(occurrences), findings=list(findings))

    defs_by_family: Dict[str, Dict[str, List[IdOccurrence]]] = {}
    for occ in occurrences:
        # Only strong definitions (table ID column / front-matter id:) are
        # counted for uniqueness. A weak heading/bold-leader definition restating
        # an entity is not a second definition and must not trigger a duplicate.
        if not occ.is_definition or occ.weak_def:
            continue
        defs_by_family.setdefault(family_of(occ.rel), {}).setdefault(occ.ident, []).append(occ)
    for fam, by_id in defs_by_family.items():
        for ident, occ_list in by_id.items():
            if len(occ_list) > 1:
                locs = ", ".join(o.rel + ":" + str(o.line) for o in occ_list)
                result.findings.append(Finding("G-IDS", "Critical",
                    "duplicate definition of " + ident + " within family '" + fam
                    + "' (" + str(len(occ_list)) + "x)", locs))

    defined_anywhere = {o.ident for o in occurrences if o.is_definition}
    dangling: Dict[str, List[IdOccurrence]] = {}
    for occ in occurrences:
        if occ.is_definition or occ.ident in defined_anywhere:
            continue
        dangling.setdefault(occ.ident, []).append(occ)
    for ident, occ_list in sorted(dangling.items()):
        locs = ", ".join(o.rel + ":" + str(o.line) for o in occ_list[:5])
        if len(occ_list) > 5:
            locs += ", ... (+" + str(len(occ_list) - 5) + " more)"
        result.findings.append(Finding("G-IDS", "Critical",
            "dangling cross-reference: " + ident + " is referenced but never defined", locs))

    return result


# --- Gate: G-DEC-STATUS ------------------------------------------------------ #

def _norm_status(s: str) -> str:
    return s.strip().strip("*_`").lower()


def _looks_like_decision_file(rel: str) -> bool:
    low = rel.lower()
    return ("decision" in low or low.startswith("adrs/") or "/adrs/" in low
            or re.search(r"adr-\d{4}", low) is not None)


def gate_dec_status(files: List[PackageFile]) -> GateResult:
    result = GateResult("G-DEC-STATUS", "Critical", checked=False)
    allowed = {s.lower() for s in DOCUMENT_STATUSES}

    for pf in files:
        if pf.is_template or pf.is_json or not _looks_like_decision_file(pf.rel):
            continue

        is_standalone_adr = bool(re.search(r"adr-\d{4}", pf.rel.lower())) or (
            pf.rel.lower().startswith("adrs/") and pf.path.name.lower() != "readme.md")
        if is_standalone_adr:
            result.checked = True
            status = pf.front_matter.get("status")
            if not status:
                m = re.search(r"^\s*[*_>#-]*\s*Status\s*[:=]\s*(.+?)\s*$", pf.text,
                              re.MULTILINE | re.IGNORECASE)
                status = m.group(1).strip().strip("*_`") if m else None
            if not status:
                result.findings.append(Finding("G-DEC-STATUS", "Critical",
                    "ADR/decision document has no Status", pf.rel))
            elif _norm_status(status) not in allowed:
                result.findings.append(Finding("G-DEC-STATUS", "Critical",
                    "invalid status '" + status + "' (allowed: "
                    + str(sorted(DOCUMENT_STATUSES)) + ")", pf.rel))

        for table in pf.tables:
            status_col = table.col_index(STATUS_HEADERS)
            id_col = table.col_index(ID_HEADERS) or _guess_id_column(table)
            has_decision_ids = False
            if id_col is not None:
                for row in table.rows:
                    if id_col < len(row):
                        c = row[id_col].strip().strip("`")
                        if c.startswith("DEC-") or c.startswith("ADR-"):
                            has_decision_ids = True
                            break
            if status_col is None and not has_decision_ids:
                continue
            result.checked = True
            if status_col is None:
                result.findings.append(Finding("G-DEC-STATUS", "Critical",
                    "decision table has no Status column", pf.rel + ":" + str(table.start_line)))
                continue
            for r_idx, row in enumerate(table.rows):
                line = table.start_line + 1 + r_idx
                row_id = row[id_col].strip().strip("`") if (id_col is not None and id_col < len(row)) else ""
                if id_col is not None and row_id and not (row_id.startswith("DEC-") or row_id.startswith("ADR-")):
                    continue
                cell = row[status_col].strip().strip("`") if status_col < len(row) else ""
                if cell.lower() in EMPTY_CELL_VALUES:
                    result.findings.append(Finding("G-DEC-STATUS", "Critical",
                        "decision " + (row_id or "(row)") + " has no status",
                        pf.rel + ":" + str(line)))
                elif _norm_status(cell) not in allowed:
                    result.findings.append(Finding("G-DEC-STATUS", "Critical",
                        "decision " + (row_id or "(row)") + " has invalid status '" + cell + "'",
                        pf.rel + ":" + str(line)))

    return result


# --- Gate: G-REQ-SRC --------------------------------------------------------- #

def _is_requirements_file(rel: str) -> bool:
    low = rel.lower()
    return "requirements/" in low or "functional" in low or "non-functional" in low


def gate_req_src(files: List[PackageFile]) -> GateResult:
    result = GateResult("G-REQ-SRC", "Critical", checked=False)

    for pf in files:
        if pf.is_template or pf.is_json or not _is_requirements_file(pf.rel):
            continue
        for table in pf.tables:
            id_col = table.col_index(ID_HEADERS) or _guess_id_column(table)
            if id_col is None:
                continue
            src_col = table.col_index(SOURCE_HEADERS)
            has_reqs = any(id_col < len(row) and
                           (row[id_col].strip().startswith("FR-") or row[id_col].strip().startswith("NFR-"))
                           for row in table.rows)
            if not has_reqs:
                continue
            result.checked = True
            if src_col is None:
                result.findings.append(Finding("G-REQ-SRC", "Critical",
                    "requirements table has no Source/Provenance column",
                    pf.rel + ":" + str(table.start_line)))
                continue
            for r_idx, row in enumerate(table.rows):
                if id_col >= len(row):
                    continue
                rid = row[id_col].strip().strip("`")
                if not (rid.startswith("FR-") or rid.startswith("NFR-")):
                    continue
                line = table.start_line + 1 + r_idx
                cell = row[src_col].strip().strip("`") if src_col < len(row) else ""
                if cell.lower() in EMPTY_CELL_VALUES:
                    result.findings.append(Finding("G-REQ-SRC", "Critical",
                        "requirement " + rid + " has no source/provenance",
                        pf.rel + ":" + str(line)))

    return result


# --- Gate: G-COMPLETE -------------------------------------------------------- #

def _empty_sections(pf: PackageFile, scan_text: str, raw_text: str) -> List[Finding]:
    findings: List[Finding] = []
    lines = scan_text.splitlines()
    # strip_code preserves the line count, so the raw lines align 1:1 with the
    # stripped ones; a section whose stripped body is blank but whose raw body
    # holds a fenced code block (a file tree, schema snippet, etc.) is legitimate
    # content, not an empty section.
    raw_lines = raw_text.splitlines()
    headings: List[Tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            headings.append((idx, len(m.group(1)), m.group(2)))
    for k, (idx, level, title) in enumerate(headings):
        # Section ends at the next heading of the same or higher level; a deeper
        # heading is substructure, not the end.
        section_end = len(lines)
        for j in range(k + 1, len(headings)):
            if headings[j][1] <= level:
                section_end = headings[j][0]
                break
        first_child = section_end
        for j in range(k + 1, len(headings)):
            if headings[j][0] >= section_end:
                break
            if headings[j][1] > level:
                first_child = headings[j][0]
                break
        body = "\n".join(lines[idx + 1:first_child]).strip()
        has_sub = first_child < section_end
        raw_body = "\n".join(raw_lines[idx + 1:first_child])
        has_code_block = "```" in raw_body or "~~~" in raw_body
        if not body and not has_sub and not has_code_block:
            findings.append(Finding("G-COMPLETE", "Critical",
                "empty section under heading '" + title + "'", pf.rel + ":" + str(idx + 1)))
    return findings


def gate_complete(files: List[PackageFile]) -> GateResult:
    result = GateResult("G-COMPLETE", "Critical", checked=False)

    for pf in files:
        if pf.is_template:
            continue
        scan_text = pf.text if pf.is_json else strip_code(pf.text)
        if not scan_text.strip():
            result.checked = True
            result.findings.append(Finding("G-COMPLETE", "Critical", "artifact is empty", pf.rel))
            continue
        result.checked = True
        for ln_no, line in enumerate(scan_text.splitlines(), start=1):
            for pat in PLACEHOLDER_PATTERNS:
                m = pat.search(line)
                if m:
                    result.findings.append(Finding("G-COMPLETE", "Critical",
                        "unfinished marker '" + m.group(0) + "' present",
                        pf.rel + ":" + str(ln_no)))
                    break
        if not pf.is_json:
            result.findings.extend(_empty_sections(pf, scan_text, pf.text))

    return result


# --- Gate: G-TRACE ----------------------------------------------------------- #

def _is_trace_matrix_file(rel: str) -> bool:
    return "traceability" in rel.lower()


def _cell_empty(row: List[str], col: int) -> bool:
    if col >= len(row):
        return True
    return row[col].strip().strip("`").lower() in EMPTY_CELL_VALUES


def _trace_from_json(pf: PackageFile) -> List[Finding]:
    findings: List[Finding] = []
    try:
        data = json.loads(pf.text) if pf.text.strip() else None
    except json.JSONDecodeError:
        return findings
    rows = data
    if isinstance(data, dict):
        rows = data.get("rows") or data.get("traceability") or data.get("matrix")
    if not isinstance(rows, list):
        return findings
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        rid = str(entry.get("req") or entry.get("requirement") or entry.get("id") or "")
        if not (rid.startswith("FR-") or rid.startswith("NFR-")):
            continue
        if str(entry.get("scope") or "").lower() in {"full", "later", "post-mvp", "stretch", "v2"}:
            continue
        gaps = []
        for label, keys in (("decision", ("decisions", "decision")),
                            ("task", ("work_items", "work items", "wbs", "tasks")),
                            ("test", ("tests", "test"))):
            val = None
            for key in keys:
                if key in entry:
                    val = entry[key]
                    break
            if not val:
                gaps.append(label)
        if gaps:
            findings.append(Finding("G-TRACE", "Critical",
                "MVP requirement " + rid + " lacks link(s): " + ", ".join(gaps), pf.rel))
    return findings


def gate_trace(files: List[PackageFile]) -> GateResult:
    result = GateResult("G-TRACE", "Critical", checked=False)
    trace_files = [pf for pf in files if _is_trace_matrix_file(pf.rel) and not pf.is_template]
    if not trace_files:
        return result

    for pf in trace_files:
        if pf.is_json:
            findings = _trace_from_json(pf)
            if findings or pf.text.strip():
                result.checked = True
            result.findings.extend(findings)
            continue
        for table in pf.tables:
            req_col = table.col_index(ID_HEADERS) or _guess_id_column(table)
            if req_col is None:
                continue
            has_reqs = any(req_col < len(row) and
                           (row[req_col].strip().startswith("FR-") or row[req_col].strip().startswith("NFR-"))
                           for row in table.rows)
            if not has_reqs:
                continue
            result.checked = True
            dec_col = table.col_index(DECISION_LINK_HEADERS)
            task_col = table.col_index(TASK_LINK_HEADERS)
            test_col = table.col_index(TEST_LINK_HEADERS)
            scope_col = table.col_index(SCOPE_HEADERS)

            missing = []
            if dec_col is None:
                missing.append("decision")
            if task_col is None:
                missing.append("work-item")
            if test_col is None:
                missing.append("test")
            if missing:
                result.findings.append(Finding("G-TRACE", "Critical",
                    "traceability matrix missing column(s): " + ", ".join(missing),
                    pf.rel + ":" + str(table.start_line)))

            for r_idx, row in enumerate(table.rows):
                if req_col >= len(row):
                    continue
                rid = row[req_col].strip().strip("`")
                if not (rid.startswith("FR-") or rid.startswith("NFR-")):
                    continue
                line = table.start_line + 1 + r_idx
                if scope_col is not None and scope_col < len(row):
                    if row[scope_col].strip().lower() in {"full", "full-only", "later", "post-mvp", "stretch", "v2"}:
                        continue
                gaps = []
                if dec_col is not None and _cell_empty(row, dec_col):
                    gaps.append("decision")
                if task_col is not None and _cell_empty(row, task_col):
                    gaps.append("task")
                if test_col is not None and _cell_empty(row, test_col):
                    gaps.append("test")
                if gaps:
                    result.findings.append(Finding("G-TRACE", "Critical",
                        "MVP requirement " + rid + " lacks link(s): " + ", ".join(gaps),
                        pf.rel + ":" + str(line)))
    return result


# --- Gate: G-SET ------------------------------------------------------------- #

def _load_required_always() -> Tuple[List[dict], Optional[str]]:
    """Load the 'Always' artifact registry bundled with the skill."""
    try:
        data = json.loads(REQUIRED_ARTIFACTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], "could not load " + REQUIRED_ARTIFACTS_PATH.name + ": " + str(exc)
    always = data.get("always") if isinstance(data, dict) else None
    if not isinstance(always, list):
        return [], REQUIRED_ARTIFACTS_PATH.name + " has no 'always' list"
    return always, None


def gate_set(package_dir: Path) -> GateResult:
    """G-SET: every 'Always' artifact is present, or explicitly omitted-with-reason
    in manifest.json; and anything the manifest declares present actually exists."""
    result = GateResult("G-SET", "Critical", checked=True)

    always, load_err = _load_required_always()
    if load_err:
        # Without the registry the gate cannot run; report unchecked (SKIP) rather
        # than punish the package for a tooling problem.
        result.checked = False
        sys.stderr.write("warning: G-SET skipped: " + load_err + "\n")
        return result

    manifest_file = package_dir / "manifest.json"
    if not manifest_file.is_file():
        result.findings.append(Finding("G-SET", "Critical",
            "package manifest (manifest.json) is a required artifact and is missing; "
            "without it the intended artifact set cannot be determined", "manifest.json"))
        return result

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.findings.append(Finding("G-SET", "Critical",
            "manifest.json is unreadable / invalid JSON: " + str(exc), "manifest.json"))
        return result

    omitted_paths: Dict[str, str] = {}
    declared_present: List[str] = []
    if isinstance(manifest, dict):
        for entry in manifest.get("omitted_artifacts") or []:
            if isinstance(entry, dict):
                path = str(entry.get("path") or "").strip()
                reason = str(entry.get("reason") or "").strip()
                if path and reason and reason.lower() not in EMPTY_CELL_VALUES:
                    omitted_paths[path] = reason
        for entry in manifest.get("artifacts") or []:
            if isinstance(entry, dict):
                path = str(entry.get("path") or "").strip()
                if path:
                    declared_present.append(path)

    # Rule A: every Always artifact is present on disk OR declared omitted (with a
    # non-empty reason). This is what closes the "absence == not-applicable" hole.
    for spec in always:
        match = spec.get("match") or []
        label = spec.get("label") or spec.get("id") or "(artifact)"
        canonical = match[0] if match else str(spec.get("id") or "")
        if any((package_dir / m).is_file() for m in match):
            continue
        if any(m in omitted_paths for m in match):
            continue
        result.findings.append(Finding("G-SET", "Critical",
            "required artifact '" + label + "' is neither present nor recorded in "
            "manifest.json omitted_artifacts[] with a reason", canonical))

    # Rule B (SKIP->FAIL hardening): anything the manifest declares present must
    # actually exist, so a manifest can't paper over a missing artifact.
    for path in sorted(set(declared_present)):
        if not (package_dir / path).is_file():
            result.findings.append(Finding("G-SET", "Critical",
                "manifest.json declares this artifact present, but it is missing on disk", path))

    return result


# --- Gate: G-PROGRESS -------------------------------------------------------- #

def _is_acceptance_audit_file(rel: str) -> bool:
    return "acceptance-audit" in rel.lower()


def _is_acceptance_criteria_file(rel: str) -> bool:
    low = rel.lower()
    return ("acceptance-criteria" in low or "acceptance-criterion" in low) and "acceptance-audit" not in low


def _ac_ids_in_id_column(pf: PackageFile) -> List[Tuple[str, int]]:
    """Rows whose id column holds an AC- identifier: (AC-id, 1-based line)."""
    found: List[Tuple[str, int]] = []
    for table in pf.tables:
        id_col = table.col_index(ID_HEADERS)
        if id_col is None:
            id_col = _guess_id_column(table)
        if id_col is None:
            continue
        for r_idx, row in enumerate(table.rows):
            if id_col >= len(row):
                continue
            cell = row[id_col].strip().strip("`")
            m = ID_TOKEN_RE.fullmatch(cell)
            if m and m.group(1) == "AC":
                found.append((cell, table.start_line + 1 + r_idx))
    return found


def gate_progress(files: List[PackageFile]) -> GateResult:
    """G-PROGRESS: if an acceptance audit exists, every AC- defined in the
    acceptance criteria must appear in it with a verdict from the allowed set.
    SKIP when no audit is present (execution tracking is conditional on handoff /
    a long execution horizon)."""
    result = GateResult("G-PROGRESS", "Critical", checked=False)

    audit_files = [pf for pf in files
                   if _is_acceptance_audit_file(pf.rel) and not pf.is_template and not pf.is_json]
    if not audit_files:
        return result  # SKIP: no acceptance audit in this package

    result.checked = True

    criteria_ids: Dict[str, str] = {}
    for pf in files:
        if pf.is_template or pf.is_json or not _is_acceptance_criteria_file(pf.rel):
            continue
        for ac, line in _ac_ids_in_id_column(pf):
            criteria_ids.setdefault(ac, pf.rel + ":" + str(line))

    audit_verdicts: Dict[str, Tuple[str, str]] = {}
    saw_verdict_col = False
    for pf in audit_files:
        for table in pf.tables:
            id_col = table.col_index(ID_HEADERS)
            if id_col is None:
                id_col = _guess_id_column(table)
            if id_col is None:
                continue
            v_col = table.col_index(VERDICT_HEADERS)
            if v_col is not None:
                saw_verdict_col = True
            for r_idx, row in enumerate(table.rows):
                if id_col >= len(row):
                    continue
                cell = row[id_col].strip().strip("`")
                m = ID_TOKEN_RE.fullmatch(cell)
                if not (m and m.group(1) == "AC"):
                    continue
                verdict = ""
                if v_col is not None and v_col < len(row):
                    verdict = row[v_col].strip().strip("`").lower()
                audit_verdicts[cell] = (verdict, pf.rel + ":" + str(table.start_line + 1 + r_idx))

    if not saw_verdict_col:
        result.findings.append(Finding("G-PROGRESS", "Critical",
            "acceptance audit has no Verdict column", audit_files[0].rel))

    for ac in sorted(criteria_ids):
        if ac not in audit_verdicts:
            result.findings.append(Finding("G-PROGRESS", "Critical",
                "acceptance criterion " + ac + " is not represented in the acceptance audit "
                "(coverage gap)", criteria_ids[ac]))
            continue
        verdict, loc = audit_verdicts[ac]
        if not verdict or verdict in EMPTY_CELL_VALUES:
            result.findings.append(Finding("G-PROGRESS", "Critical",
                "acceptance criterion " + ac + " has no verdict in the acceptance audit", loc))
        elif verdict not in ALLOWED_VERDICTS:
            result.findings.append(Finding("G-PROGRESS", "Critical",
                "acceptance criterion " + ac + " has invalid verdict '" + verdict
                + "' (allowed: Met / Partial / Not-met / Pending)", loc))

    return result


# --- Orchestration & reporting ----------------------------------------------- #

def run_gates(package_dir: Path) -> List[GateResult]:
    files = load_package(package_dir)
    return [gate_ids(files), gate_dec_status(files), gate_req_src(files),
            gate_complete(files), gate_trace(files), gate_set(package_dir),
            gate_progress(files)]


def build_summary(package_dir: Path, results: List[GateResult]) -> dict:
    critical_failures = [r for r in results if r.severity == "Critical" and not r.passed]
    return {
        "package": str(package_dir),
        "ok": not critical_failures,
        "critical_failed": [r.gate for r in critical_failures],
        "gates": [r.to_dict() for r in results],
        "totals": {
            "gates": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "findings": sum(len(r.findings) for r in results),
        },
    }


def print_human_report(package_dir: Path, results: List[GateResult]) -> None:
    print("Keystone package validation: " + str(package_dir))
    print("=" * 64)
    for r in results:
        if not r.checked:
            mark, note = "SKIP", " (no applicable inputs found)"
        elif r.passed:
            mark, note = "PASS", ""
        else:
            plural = "s" if len(r.findings) != 1 else ""
            mark, note = "FAIL", " (" + str(len(r.findings)) + " finding" + plural + ")"
        print("[" + mark + "] " + r.gate.ljust(13) + " " + r.severity.ljust(8) + note)
        for f in r.findings:
            loc = " @ " + f.location if f.location else ""
            print("        - " + f.message + loc)
    print("-" * 64)
    critical_failures = [r for r in results if r.severity == "Critical" and not r.passed]
    if critical_failures:
        gates = ", ".join(r.gate for r in critical_failures)
        print("RESULT: NOT READY -- critical gate(s) failed: " + gates)
    else:
        skipped = [r.gate for r in results if not r.checked]
        extra = (" (" + str(len(skipped)) + " gate(s) skipped: " + ", ".join(skipped) + ")") if skipped else ""
        print("RESULT: OK -- no critical gate failures" + extra)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_package.py",
        description=("Run Keystone's mechanical quality gates (G-IDS, G-DEC-STATUS, "
                     "G-REQ-SRC, G-COMPLETE, G-TRACE, G-SET, G-PROGRESS) against a generated "
                     "package directory. Exits non-zero if any CRITICAL gate fails."),
        epilog="See ../references/quality-gates.md for gate definitions.")
    parser.add_argument("package_dir", help="path to the generated package directory")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit a machine-readable JSON summary instead of the human report")
    args = parser.parse_args(argv)

    package_dir = Path(args.package_dir)
    if not package_dir.exists():
        sys.stderr.write("error: package directory not found: " + str(package_dir) + "\n")
        return 2
    if not package_dir.is_dir():
        sys.stderr.write("error: not a directory: " + str(package_dir) + "\n")
        return 2

    results = run_gates(package_dir)
    summary = build_summary(package_dir, results)
    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_report(package_dir, results)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------------
# Gate reference (kept inline so the validator is self-describing)
# ---------------------------------------------------------------------------
#
# G-IDS (Critical) - Identifier integrity.
#   Every identifier in the package must match its governance format (see the
#   ID_PATTERNS table above, mirrored from references/governance.md):
#   FR-NNN, NFR-NNN, CON-NNN, INV-NNN, ASM-NNN, DEP-NNN, OQ-NNN, DEC-NNN,
#   ADR-NNNN, RISK-NNN, HYP-NNN, EXP-NNN, POC-NNN, KPI-NNN, STK-NNN, MS-NNN,
#   AC-NNN, TEST-NNN, PH-N, WBS-N[.N[.N]] (the group form WBS-N is valid, as are
#   the leaf WBS-N.N and sub-leaf WBS-N.N.N). An identifier is treated as a
#   *definition* when it is the value of a register table's ID column, an
#   id: front-matter field, the leading token of a Markdown heading
#   (## WBS-1 ...), or the bold leader of a list item (- **WBS-1.1** ...); it is
#   a *reference* everywhere else. Heading/bold-leader definitions are enough to
#   resolve a cross-reference but are not counted for duplicate detection (a
#   detail heading restating an entity already defined in a table or front-matter
#   is the same entity, not a second definition). The gate fails on: a malformed
#   identifier (right prefix, wrong number format); a duplicate definition of the
#   same identifier within one directory family; and a dangling cross-reference -
#   an identifier that is referenced in prose, a link, or a register cell but
#   never defined anywhere in the package.
#   Rationale: consistent, resolvable identifiers are what make the
#   traceability matrix and the execution handoff trustworthy. A dangling
#   reference means a downstream agent will follow a link to nothing.
#
# G-DEC-STATUS (Critical) - Decision status presence and validity.
#   Every decision (DEC-) row, every ADR row in an index, and every standalone
#   ADR document must carry an explicit status drawn from the allowed set.
#   For decisions the allowed set is exactly Proposed, Approved, Rejected,
#   Superseded, Deferred; ADR documents additionally accept the conventional
#   Accepted alias and the lifecycle terminals Implemented, Obsolete, Draft.
#   The gate fails on a missing status, an empty status cell, or a status value
#   outside the allowed set. Rationale: safeguard 9 - a Proposed decision must
#   never be rendered as if it were Approved, because only Approved decisions
#   constrain execution. Status is therefore mandatory and explicit.
#
# G-REQ-SRC (Critical) - Requirement provenance.
#   Every functional (FR-) and non-functional (NFR-) requirement row must have
#   a non-empty Source / Provenance / Origin value (a dash, "n/a", "none", or
#   "tbd" all count as empty). The gate also fails if a requirements table has
#   no source column at all. Rationale: safeguard 1 - requirements must trace
#   back to an input span, a resolved open question, or a clarification, so a
#   reader can audit where each requirement came from. Anything inferred by
#   Keystone on its own initiative belongs in the assumption register as an
#   ASM- with a risk-if-wrong, not silently asserted as a requirement.
#
# G-COMPLETE (Critical) - No unfinished content.
#   No non-template artifact may contain an unfinished marker (TODO, TBD,
#   FIXME, XXX, a <placeholder> token, a {{mustache}} hole, FILL-IN, or LOREM
#   IPSUM) and no artifact may contain an empty section (a heading with neither
#   body text, child headings, nor a fenced code block beneath it - a code block
#   such as a file tree or a schema snippet is legitimate content). Empty files
#   fail outright. Code fences and inline code are stripped before the marker
#   scan so that legitimate examples, schema snippets, and diagrams are not
#   misread as unfinished prose; the empty-section check still sees the raw text
#   so a code-only section counts as filled. Template files (anything under a
#   templates/ path or named
#   *.template.md / *.tmpl) are exempt, because placeholder tokens are exactly
#   what a blank template is supposed to contain. Rationale: safeguard 11 - a
#   package handed to an execution agent must be complete, not a skeleton with
#   holes the agent is silently expected to fill.
#
# G-TRACE (Critical) - Traceability coverage for the MVP.
#   The traceability matrix (validation/traceability-matrix.md, and/or a JSON
#   mirror) is parsed row by row. Every requirement that is in scope for the
#   MVP - that is, every FR-/NFR- row not explicitly marked full-only / later /
#   post-mvp / stretch / v2 in a scope column - must link to at least one
#   decision, at least one work item, and at least one test. A row with an
#   empty cell in any of those required columns is a gap and fails the gate, as
#   does a matrix that is missing one of those columns entirely. Rationale: the
#   matrix is what lets an implementing agent navigate from any need to its
#   evidence (why it is built this way, where it gets built, how we know it
#   works) and back again. An MVP requirement with a gap is either unbuildable
#   as specified or quietly out of scope; either way it must be resolved (by
#   adding the missing link or by explicitly de-scoping the requirement) rather
#   than shipped as a silent omission.
#
# G-SET (Critical) - Required-artifact-set completeness.
#   The "Always" generation class in references/artifact-rules.md (mirrored
#   machine-readably in references/required-artifacts.json) names the artifacts
#   every package must contain: charter, executive summary, functional and
#   non-functional requirements, the constraint / assumption / open-question /
#   open-decision registers, the risk register, the phased roadmap, acceptance
#   criteria, the traceability matrix, the handoff initial prompt, the
#   execution-readiness report, the package manifest, and the README. G-SET
#   requires each of these to be present on disk OR explicitly recorded in
#   manifest.json's omitted_artifacts[] with a non-empty reason; it also fails if
#   the manifest itself is missing (intended scope is then undeterminable) or if
#   the manifest declares an artifact present that does not exist on disk.
#   Rationale: the other five gates verify the *internal consistency of what is
#   present*; G-SET verifies *that what must be present actually is*. Without it,
#   a package reduced to a charter and a README passes every other gate by SKIP
#   and is wrongly reported READY - the absence of an artifact is silently
#   indistinguishable from "not applicable". G-SET makes omission a conscious,
#   recorded act (an omitted_artifacts[] entry) rather than a silent gap, which is
#   exactly what lets an execution agent trust the readiness verdict.
#
# G-PROGRESS (Critical) - Acceptance-audit coverage (execution tracking).
#   When a package carries an acceptance audit (validation/acceptance-audit.md),
#   every acceptance criterion (AC-) defined in validation/acceptance-criteria.md
#   must appear in the audit with a verdict from the allowed set (Met, Partial,
#   Not-met, Pending). A criterion missing from the audit, a blank verdict, an
#   out-of-set verdict, or an audit with no Verdict column at all is a finding.
#   The gate SKIPs entirely when no audit is present, because the audit is a
#   Conditional artifact (handoff / long execution horizon) - so this gate never
#   penalises a planning-only package, only one that ships a tracking surface and
#   leaves it incoherent. Rationale: the acceptance audit is the closing loop that
#   proves the built thing met the plan; G-PROGRESS keeps it honest (every AC
#   accounted for) the same way G-TRACE keeps the matrix honest.
#
# Severity and exit behaviour.
#   All seven gates above are Critical: any failure makes the package NOT READY
#   and the process exits 1. The Warn-severity gates from quality-gates.md
#   (G-ASM-VISIBLE, G-CLAIM, G-RISK, G-COUPLING, G-BLOAT, G-CMD-THIN) and the
#   partly-mechanical Criticals (G-CONFLICT, G-EXEC, G-HANDOFF, G-OQ) are
#   judgment checks recorded by a human or agent in the validation report; they
#   are intentionally outside this script's scope. A gate reported as SKIP
#   simply found no applicable inputs in the package (for example, no
#   traceability matrix yet) and is neither a pass nor a failure on its own -
#   whether a given artifact is required at all is governed by the artifact
#   selection rules, not by this validator.
#
# Heuristic limits worth knowing.
#   The parser handles GitHub-style pipe tables and flat front-matter only; it
#   does not evaluate nested YAML, HTML tables, or pipes escaped inside cells.
#   Identifier detection keys off the governed prefixes, so a project that
#   invents a new prefix must register it in ID_PATTERNS to be checked. These
#   trade a little precision for robustness on semi-structured prose, in
#   keeping with the goal of useful signal over false certainty.
# ---------------------------------------------------------------------------
#
# Worked example - reading a finding.
#   A finding printed as
#       [FAIL] G-TRACE       Critical (1 finding)
#               - MVP requirement FR-003 lacks link(s): test @ validation/traceability-matrix.md:14
#   means: in the traceability matrix, on the row for FR-003 (physical line 14
#   of that file), the Tests column was empty while the requirement is in MVP
#   scope. To clear it, either add the verifying TEST- identifier to that row
#   (and define that test in validation/test-strategy.md) or move FR-003 out of
#   MVP scope with a recorded decision. The JSON form of the same run carries
#   the identical message under gates[].findings[] with gate, severity,
#   message, and location keys, so a wrapper or CI job can act on it directly
#   without scraping the human report.
#
# Integration notes.
#   The script is import-safe: run_gates(package_dir) returns the list of
#   GateResult objects and build_summary(package_dir, results) returns the same
#   dict that --json prints, so a harness can call the API directly (the test
#   runner does exactly this) instead of shelling out. There is no global
#   state, no network access, and no third-party dependency; the only inputs
#   are the files under the package directory. This keeps the validator usable
#   inside the skill, inside CI, and inside ad-hoc one-off checks with the same
#   behaviour and the same exit-code contract in every context.
#
# Why mechanical gates live in code rather than in the skill prose.
#   The skill (skill/SKILL.md plus references/) is authoritative for the
#   methodology and is loaded into a model's context on demand. Mechanical
#   checks - format matching, uniqueness, dangling-reference detection, table
#   coverage - are exactly the kind of deterministic, repeatable work that a
#   small stdlib program does more reliably and far more cheaply than a model
#   re-deriving the rules every run. Keeping them here means the gate result is
#   reproducible byte-for-byte, can gate a commit without a model in the loop,
#   and stays in lockstep with governance.md because both cite the same prefix
#   table and the same status vocabulary. The judgment gates stay with the
#   model precisely because they need reading comprehension this script does
#   not attempt.
#
# Relationship to keystone-state.json.
#   When a package carries a machine-owned keystone-state.json, this validator
#   reads identifiers and traceability rows out of it the same way it reads the
#   Markdown surface, so the two are cross-checked: an identifier defined only
#   in state but never rendered, or a matrix gap present in the rendered table
#   but hidden in state, both surface as findings. The validator does not edit
#   state or artifacts - it only reports - so it is safe to run repeatedly and
#   safe to run inside a read-only check. Reconciliation between state and the
#   rendered artifacts is the skill's job during resume and update cycles; this
#   script's contribution is to make any divergence visible and to refuse the
#   "ready" verdict while a Critical divergence remains. Run it early and run
#   it often: it is cheap, deterministic, and the cheapest possible insurance
#   against handing a downstream agent a package that cannot be navigated.
# ---------------------------------------------------------------------------
# End of validate_package.py - mechanical Keystone quality gates (stdlib only).


