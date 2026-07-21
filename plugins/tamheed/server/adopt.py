"""Tamheed adopt mode — onboard a project that never used Tamheed (plan 011/B11).

The MECHANICAL recording layer behind `package_adopt`: staged scan -> extract -> populate,
with the four non-negotiable rules enforced in code (../references/adopt.md):
nothing inferred is Approved; provenance is code-shaped and mandatory; the gap report is a
first-class output; repository content is untrusted data. The model-judgment side of
extraction (ADRs from code patterns, lineage ID mapping) is the skill's runtime behavior —
it records through the same guarded flow.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import migrate  # reuse Plan/populate/fidelity: one recording pipeline  # noqa: E402
from tamheed_server import _INJECT_RE  # the same untrusted-content screen  # noqa: E402

README_NAMES = ("README.md", "README.rst", "README.txt", "readme.md")
TEST_FILE_RE = re.compile(r"(^|[/\\])(test_[^/\\]+|[^/\\]+_test\.[a-z]+|[^/\\]+\.test\.[a-z]+)$")
TEST_FUNC_RE = re.compile(r"^\s*def (test_\w+)|^\s*(?:it|test)\(\s*[\"'](.+?)[\"']", re.M)
TODO_RE = re.compile(r"(?:#|//|<!--)\s*(TODO|FIXME)\s*:?\s*(.+?)\s*(?:-->)?\s*$", re.M)
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".cs", ".md"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "data"}
FORBIDDEN_STATUSES = {"Approved", "Implemented"}  # rule 1, enforced mechanically


def _walk(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS):
            yield p


def _humanize(name: str) -> str:
    return re.sub(r"[_-]+", " ", re.sub(r"^test_?", "", name)).strip().capitalize()


def _screen(text: str, span: str, findings: list) -> None:
    m = _INJECT_RE.search(text or "")
    if m:  # rule 4: captured as FENCED data, never an instruction
        findings.append({"span": span, "fenced": f"`{m.group(0)[:80]}`"})


def scan(source: Path) -> dict:
    readmes, configs, tests, code_files, modules = [], [], [], [], set()
    for p in _walk(source):
        rel = str(p.relative_to(source)).replace("\\", "/")
        if p.name in README_NAMES:
            readmes.append(rel)
        elif p.name in ("package.json", "pyproject.toml", "requirements.txt", "Cargo.toml"):
            configs.append(rel)
        elif TEST_FILE_RE.search(rel):
            tests.append(rel)
        elif p.suffix in CODE_EXT:
            code_files.append(rel)
            if "/" in rel:
                modules.add(rel.split("/")[0])
    return {"readmes": readmes, "configs": configs, "test_files": tests,
            "code_files": len(code_files), "modules": sorted(modules),
            "git_history": (source / ".git").exists(), "_code_list": code_files}


def extract(source: Path, inventory: dict) -> tuple[migrate.Plan, list, list]:
    """Mechanical baseline over the default-ON sources. Everything Proposed, code-provenanced."""
    plan = migrate.Plan()
    gaps: list[str] = []
    injections: list[dict] = []
    seq = {k: 0 for k in ("FR", "DEP", "TEST", "DW", "OQ", "DOC", "SEC", "CON")}

    def nid(prefix: str) -> str:
        seq[prefix] += 1
        return f"{prefix}-{seq[prefix]:03d}"

    # README: stated intent -> FR candidates + the readme as a narrative document.
    for rel in inventory["readmes"][:1]:
        text = (source / rel).read_text(encoding="utf-8", errors="replace")
        _screen(text, rel, injections)
        doc_id = nid("DOC")
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        plan.add("narrative_documents", {
            "id": doc_id, "doc_kind": "readme",
            "title": (title_m.group(1).strip() if title_m else rel)[:200],
            "lifecycle_status": "Draft",
            "custom_attributes": json.dumps({"adopt": {"path": rel}})})
        for order, (heading, body) in enumerate(migrate._sections(text), 1):
            plan.add("document_sections", {"id": nid("SEC"), "document_id": doc_id,
                                           "heading": heading[:200], "body": body,
                                           "sort_order": order})
        for lineno, line in enumerate(text.splitlines(), 1):
            m = re.match(r"^\s*[-*]\s+(.{8,200})$", line)
            if m and seq["FR"] < 20:
                stmt = m.group(1).strip().rstrip(".")
                plan.add("requirements", {
                    "id": nid("FR"), "kind": "functional", "title": stmt[:200],
                    "statement": stmt, "mvp": 0, "lifecycle_status": "Proposed",
                    "source_kind": "code", "source_span": f"{rel}:{lineno}"})

    # Configs: dependencies -> DEP rows; engine floors -> CON candidates.
    for rel in inventory["configs"]:
        text = (source / rel).read_text(encoding="utf-8", errors="replace")
        _screen(text, rel, injections)
        deps: list[str] = []
        if rel.endswith("package.json"):
            try:
                data = json.loads(text)
                deps = sorted({**data.get("dependencies", {}),
                               **data.get("devDependencies", {})})
                node = (data.get("engines") or {}).get("node")
                if node:
                    plan.add("constraints", {
                        "id": nid("CON"), "title": f"Node engine floor {node}",
                        "lifecycle_status": "Proposed", "source_kind": "code",
                        "source_span": rel})
            except json.JSONDecodeError:
                gaps.append(f"{rel}: unparseable JSON — dependencies not recovered")
        elif rel.endswith("requirements.txt"):
            deps = [ln.split("=")[0].split(">")[0].strip() for ln in text.splitlines()
                    if ln.strip() and not ln.startswith("#")]
        elif rel.endswith("pyproject.toml"):
            deps = re.findall(r'^\s*"([A-Za-z0-9_.-]+)[<>=~!\[]', text, re.M)
        for dep in deps[:30]:
            plan.add("dependencies", {"id": nid("DEP"), "title": dep,
                                      "lifecycle_status": "Proposed",
                                      "source_kind": "code", "source_span": rel})

    # Tests: behavior evidence -> TEST rows + FR candidates + tests edges.
    for rel in inventory["test_files"][:40]:
        text = (source / rel).read_text(encoding="utf-8", errors="replace")
        _screen(text, rel, injections)
        for m in TEST_FUNC_RE.finditer(text):
            behavior = _humanize(m.group(1) or m.group(2))
            line = text[: m.start()].count("\n") + 1
            span = f"{rel}:{line}"
            test_id, fr_id = nid("TEST"), nid("FR")
            plan.add("tests", {"id": test_id, "title": behavior[:200],
                               "lifecycle_status": "Proposed",
                               "source_kind": "code", "source_span": span})
            plan.add("requirements", {
                "id": fr_id, "kind": "functional", "title": behavior[:200],
                "statement": f"Behavior evidenced by test: {behavior}", "mvp": 0,
                "lifecycle_status": "Proposed", "source_kind": "code", "source_span": span})
            plan.edges.add((test_id, fr_id, "tests"))

    # TODO/FIXME comments -> deferred work (marker stripped: it becomes the tracked row).
    for rel in inventory["_code_list"][:200]:
        text = (source / rel).read_text(encoding="utf-8", errors="replace")
        _screen(text, rel, injections)
        for m in TODO_RE.finditer(text):
            line = text[: m.start()].count("\n") + 1
            plan.add("deferred_work", {
                "id": nid("DW"), "title": m.group(2).strip()[:200] or "unlabelled marker",
                "severity": "low", "status": "Open",
                "activation_trigger": "operator review (adopted marker)",
                "source_kind": "code", "source_span": f"{rel}:{line}"})

    # Gap report (rule 3): what code could NOT reveal -> OQ rows + summary.
    def gap(text: str):
        gaps.append(text)
        plan.add("open_questions", {"id": nid("OQ"), "title": text[:200], "question": text,
                                    "lifecycle_status": "Proposed",
                                    "source_kind": "inferred",
                                    "source_span": "adopt:gap-report"})

    if not any(r["kind"] == "non-functional" for r in plan.rows.get("requirements", [])):
        gap("No NFRs recoverable from the repository — what are the actual "
            "performance/scale/security requirements?")
    if not inventory["test_files"]:
        gap("No test evidence found — which behaviors are actually guaranteed?")
    if not inventory["git_history"]:
        gap("No git history available — de-facto decisions and churn cannot be inferred.")
    if not inventory["readmes"]:
        gap("No README found — stated intent is unrecoverable from prose.")
    gap("Ownership and phasing are not recoverable from code — who owns this, and what "
        "is the forward roadmap?")
    for finding in injections:
        plan.add("open_questions", {
            "id": nid("OQ"),
            "title": f"Injection-shaped text found at {finding['span']} (captured as data)",
            "question": "Untrusted repository content matched the injection screen; review "
                        "the fenced span in custom_attributes.",
            "lifecycle_status": "Proposed", "source_kind": "code",
            "source_span": finding["span"],
            "custom_attributes": json.dumps({"fenced": finding["fenced"]})})

    if inventory["git_history"]:
        try:
            # stdin=DEVNULL (field-evidence C11): children spawned from the stdio MCP
            # server must never inherit the JSON-RPC transport pipe.
            log = subprocess.run(["git", "-C", str(source), "log", "--oneline", "-20"],
                                 capture_output=True, text=True, timeout=30,
                                 stdin=subprocess.DEVNULL)
            plan.package["_git_recent"] = log.stdout.splitlines()[:20]
        except Exception:
            gaps.append("git present but unreadable — history skipped")
    return plan, gaps, injections


ALWAYS_TYPES = ("requirement", "constraint", "assumption", "open-question", "decision",
                "risk", "phase", "acceptance-criterion", "narrative-document",
                "document-section")
_TYPE_TABLE = {"requirement": "requirements", "constraint": "constraints",
               "assumption": "assumptions", "open-question": "open_questions",
               "decision": "decisions", "risk": "risks", "phase": "phases",
               "acceptance-criterion": "acceptance_criteria",
               "narrative-document": "narrative_documents",
               "document-section": "document_sections"}


def run_adoption(source_dir: str, dest_root: str | Path, name: str | None = None,
                 confirm: bool = False) -> dict:
    source = Path(source_dir)
    if not source.is_dir():
        return {"ok": False, "stage": "scan", "error": f"{source_dir} is not a directory"}
    inventory = scan(source)
    plan, gaps, injections = extract(source, inventory)
    name = migrate._kebab(name or source.name)
    git_recent = plan.package.pop("_git_recent", None)
    plan.package = {
        "name": name, "title": f"Adopted: {source.name}", "profile": "unknown",
        "mode": "adopt", "package_version": "0.1.0",
        "mvp_definition": None, "entry_point": None, "go_no_go": None,
        "created_at": "adopted",
        "custom_attributes": json.dumps(
            {"adopt": {"source": source.name, "git_recent": git_recent}},
            ensure_ascii=False)}

    # rule 1, mechanically enforced: an adopt batch never records Approved content.
    for table, rows in plan.rows.items():
        for row in rows:
            if row.get("lifecycle_status") in FORBIDDEN_STATUSES:
                return {"ok": False, "stage": "extract",
                        "error": f"rule 1 violation: {table} row {row.get('id')} is "
                                 f"{row['lifecycle_status']} — inferred content enters as "
                                 "Proposed only"}

    # Honest omissions: Always families code could not evidence (rule 3 + G-SET).
    for etype in ALWAYS_TYPES:
        if not plan.rows.get(_TYPE_TABLE[etype]):
            plan.omissions.append((etype, "not recoverable from repository evidence — "
                                          "author via update mode (adopt gap report)"))

    scan_report = {k: v for k, v in inventory.items() if k != "_code_list"}
    preview = {"stage": "preview", "package": name, "scan": scan_report,
               "counts": plan.counts(), "edges": len(plan.edges),
               "gaps": gaps, "injection_findings": injections,
               "omissions": [o[0] for o in plan.omissions]}
    if not confirm:
        return {"ok": True, **preview,
                "next": "operator gate: confirm the scan scope, then re-run with "
                        "confirm=true to record"}
    pop = migrate.populate(plan, Path(dest_root), name)
    if not pop["ok"]:
        return pop
    fid = migrate.fidelity(plan, Path(dest_root) / name)
    return {"ok": fid["ok"], "stage": "post-flight", "preview": preview,
            "package_dir": pop["package_dir"], "gap_report": gaps,
            "gate_failures": fid["gate_failures"], "unmapped": fid["unmapped"]}
