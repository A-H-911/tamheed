"""Shared package-recording pipeline (extracted from the retired v1 importer, plan 031).

`package_adopt` builds a Plan and runs populate() + fidelity() — one recording
pipeline, one fidelity report. The v1 markdown parsing that used to surround these
helpers was deleted with v1 ingestion; what remains is version-agnostic: raw-SQL
population of a fresh store from an in-memory Plan, then column-level fidelity checks.
Deterministic output (no wall-clock timestamps) so recorded goldens are byte-comparable.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "db"))

import store  # noqa: E402

try:  # no import cycle: tamheed_server imports this lazily inside handlers
    from tamheed_server import BASELINE_ENTITY_TYPES, ENTITY_TABLES  # noqa: E402
except ImportError:  # pragma: no cover
    BASELINE_ENTITY_TYPES = []
    ENTITY_TABLES = {}


def _kebab(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-") or "package"


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
        # v3.0.0 (plan 027): v1 prompt files become <package>/prompts/*.md files, never
        # rows — (v1_rel, out_name, text), written by populate after the store commit.
        self.prompt_files: list[tuple[str, str, str]] = []
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


INSERT_ORDER = ["requirements", "constraints", "invariants", "assumptions", "dependencies",
                "open_questions", "adrs", "decisions", "risks", "hypotheses", "experiments",
                "pocs", "kpis", "stakeholders", "phases", "milestones", "wbs_items",
                "acceptance_criteria", "tests", "deferred_work", "narrative_documents",
                "document_sections", "diagrams"]  # prompts: files since v3.0.0 (plan 027)


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
    # v3.0.0 (plan 027): v1 prompt files land as package files, after the store commit
    # (plain files, not part of the transaction; a failure here leaves a valid package).
    written_prompts = []
    if plan.prompt_files:
        out_dir = pkg_dir / "prompts"
        out_dir.mkdir(parents=True, exist_ok=True)
        # No timestamp: emissions stay byte-reproducible (golden regression); the
        # migration date lives in the run report, not the file.
        for rel, out_name, text in plan.prompt_files:
            header = f"<!-- migrated from v1 {rel} by tamheed 3.0.0 -->\n"
            (out_dir / out_name).write_text(header + text, encoding="utf-8",
                                            newline="\n")
            written_prompts.append(f"prompts/{out_name}")
    return {"ok": True, "stage": "populate", "package_dir": str(pkg_dir),
            "prompt_files": written_prompts}


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
    caps = [("acceptance_criteria", "title", 120), ("stakeholders", "title", 200)]
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
                    "verdict", "severity"}
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


_CUTOVER_NEXT = (
    "cutover (C15): open the package and run handoff_emit(<repo>) — it writes the "
    "executor .mcp.json and the CLAUDE.md tracking note. Then update stale v1 pointers "
    "in the repo's AGENTS.md/CLAUDE.md and freeze the v1 source tree; until then two "
    "sources of truth coexist.")
