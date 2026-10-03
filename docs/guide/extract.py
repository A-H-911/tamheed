"""Engine facts for the user guide — every structural statement index.html makes comes from here.

Nothing in this module is typed by hand except the labels of the shared column blocks and the
tool groups (both asserted against the engine). Every enumeration is sorted or follows a
registry's own order, so the build is byte-deterministic on every platform CI runs.
"""
from __future__ import annotations

import inspect
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path[:0] = [str(BUNDLE / "server"), str(BUNDLE / "db"), str(REPO)]

import check  # noqa: E402  (check.py: SUITES, GATES, the lint rosters)
import store  # noqa: E402
import tamheed_server as srv  # noqa: E402

SERVER_SRC = (BUNDLE / "server" / "tamheed_server.py").read_text(encoding="utf-8")
CHECK_SRC = (REPO / "check.py").read_text(encoding="utf-8")

# The shared column blocks the guide describes once (asserted to exist in the DDL).
BLOCKS = {
    "LIFE": ("lifecycle_status",),
    "DISP": ("disposition", "disposition_reason_ref"),
    "SRC": ("source_kind", "source_span"),
    "TAIL": ("custom_attributes", "last_referenced"),
}
# (table, column) pairs the SERVER writes — the caller never supplies them.
SERVER_FILLED = {
    ("progress_entries", "id"), ("progress_entries", "occurred_at"),
    ("audit_verdicts", "id"), ("audit_verdicts", "recorded_at"), ("audit_verdicts", "iteration"),
    ("feedback", "confirmed_at"),
    ("packages", "name"), ("packages", "profile"), ("packages", "package_version"),
    ("packages", "created_at"),
}
TAIL_SERVER = {"last_referenced"}  # stamped by work_bind on every table that carries it
STORE_TABLES = ("packages", "entity_types", "entity_index")  # the store's own furniture
GROUPS = {
    "read": ("server_info", "package_unlock", "entity_query", "trace_query", "gate_run",
             "readiness_check", "package_verify"),
    "mutate": ("package_create", "package_open", "package_close", "entity_upsert",
               "progress_update", "audit_record", "work_bind", "entity_export", "handoff_emit"),
    "staged": ("package_migrate", "package_adopt"),
    "export": ("export_html",),
}


def version() -> str:
    return json.loads((BUNDLE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


# ----------------------------------------------------------------------------- schema

def _strip_sql_comments(sql: str) -> str:
    return re.sub(r"--[^\n]*", "", sql)


def _check_sets(sql: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for col, body in re.findall(r"CHECK\s*\(\s*(\w+)\s+IN\s*\(([^)]*)\)", sql, re.S):
        out[col] = re.findall(r"'((?:[^']|'')*)'", body)
    return {k: [v.replace("''", "'") for v in vals] for k, vals in out.items()}


def _table_checks(sql: str) -> list[str]:
    """Table-level CHECK clauses (lines that start with CHECK), whitespace-collapsed. The
    clause is read to its balanced closing parenthesis, so a CHECK that spans lines (the
    requirements kind/prefix pairing) is carried whole."""
    found = []
    for m in re.finditer(r"^\s*CHECK\s*\(", sql, re.M):
        depth, i = 1, m.end()
        while i < len(sql) and depth:
            depth += {"(": 1, ")": -1}.get(sql[i], 0)
            i += 1
        found.append(re.sub(r"\s+", " ", sql[m.end():i - 1]).strip())
    return found


def _check_globs(sql: str) -> dict[str, list[str]]:
    """Column CHECKs of the form `col IN (...) OR col GLOB 'x'`: the GLOB alternatives a value
    may take besides the listed ones (packages.mode admits `stage:*`)."""
    out: dict[str, list[str]] = {}
    for col, body in re.findall(r"CHECK\s*\(\s*(\w+)\s+IN\s*\([^)]*\)((?:\s+OR\s+\w+\s+GLOB\s+'[^']*')+)", sql, re.S):
        out[col] = re.findall(r"GLOB\s+'([^']*)'", body)
    return out


def schema() -> dict:
    conn = store.connect()
    types = {tid: (label, prefix, cls) for tid, label, prefix, cls in srv.BASELINE_ENTITY_TYPES}
    table_type = {tbl: tid for tid, tbl in srv.ENTITY_TABLES.items()}
    family_order = [tbl for tbl in srv.ENTITY_TABLES.values()]  # registry order
    all_tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    ordered = family_order + [t for t in STORE_TABLES if t in all_tables]
    assert sorted(ordered) == all_tables, (sorted(ordered), all_tables)
    tables = []
    hue = 0
    for tbl in ordered:
        sql = _strip_sql_comments(conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,)).fetchone()[0])
        sets = _check_sets(sql)
        globs_by_col = _check_globs(sql)
        nonempty = set(re.findall(r"CHECK\s*\(\s*(\w+)\s*<>\s*''\s*\)", sql))
        globs = re.findall(r"id\s+GLOB\s+'([^']+)'", sql)
        fks = sorted(conn.execute(f"PRAGMA foreign_key_list({tbl})").fetchall(),
                     key=lambda r: (r[0], r[1]))
        fk_by_col = {r[3]: (r[2], r[4]) for r in fks}
        tid = table_type.get(tbl)
        kind = ("store" if tbl in STORE_TABLES else "relation" if tbl == "trace_edges"
                else "omission" if tbl == "omissions"
                else "journal" if tbl in ("progress_entries", "audit_verdicts") else "family")
        cols = []
        for cid, name, ctype, notnull, dflt, pk in conn.execute(f"PRAGMA table_info({tbl})"):
            block = next((b for b, names in BLOCKS.items() if name in names), None)
            server = (tbl, name) in SERVER_FILLED or name in TAIL_SERVER
            cols.append({
                "name": name, "type": ctype, "notnull": bool(notnull), "default": dflt,
                "pk": bool(pk), "required": bool(notnull) and dflt is None and not pk and not server,
                "fk": fk_by_col.get(name), "check_in": sets.get(name), "nonempty": name in nonempty,
                "check_glob": globs_by_col.get(name), "server": server, "block": block,
            })
        if kind == "family":
            hue += 1
        label, prefix, cls = types.get(tid, (None, None, None))
        tables.append({
            "table": tbl, "type": tid, "label": label, "prefix": prefix, "cls": cls, "kind": kind,
            "hue": ((hue - 1) % 12) + 1 if kind == "family" else None,
            "columns": cols, "id_globs": globs, "table_checks": _table_checks(sql),
            "pk": [c["name"] for c in cols if c["pk"]],
        })
    triggers = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")]
    views = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    named = [t for t in triggers if not re.search(r"_(ai|ad)$", t)]
    for b, names in BLOCKS.items():  # every block column exists somewhere
        for n in names:
            assert any(c["name"] == n for t in tables for c in t["columns"]), (b, n)
    for tbl, col in SERVER_FILLED:
        assert any(t["table"] == tbl and any(c["name"] == col for c in t["columns"])
                   for t in tables), (tbl, col)
    return {"tables": tables, "triggers": triggers, "named_triggers": named, "views": views,
            "schema_version": conn.execute("PRAGMA user_version").fetchone()[0]}


def lifecycle_sets(sch: dict) -> dict:
    """STD8 / STD9 / the domain lifecycles, discovered from the lifecycle_status CHECK sets."""
    std8 = ["Draft", "Proposed", "Approved", "Rejected", "Deferred", "Implemented", "Superseded",
            "Obsolete"]
    std9 = std8[:5] + ["Review"] + std8[5:]
    out = {"STD8": {"values": std8, "tables": []}, "STD9": {"values": std9, "tables": []},
           "domain": {}}
    for t in sch["tables"]:
        for c in t["columns"]:
            if c["name"] != "lifecycle_status" or not c["check_in"]:
                continue
            if c["check_in"] == std8:
                out["STD8"]["tables"].append(t["table"])
            elif c["check_in"] == std9:
                out["STD9"]["tables"].append(t["table"])
            else:
                out["domain"][t["table"]] = c["check_in"]
    assert out["STD8"]["tables"] and out["STD9"]["tables"] == ["slices", "wbs_items"], out
    return out


def families() -> list[dict]:
    return [{"type": tid, "label": label, "prefix": prefix, "cls": cls,
             "table": srv.ENTITY_TABLES[tid]} for tid, label, prefix, cls in srv.BASELINE_ENTITY_TYPES]


def relations() -> list[dict]:
    out = []
    for rel, rule in sorted(srv.RELATION_RULES.items()):
        if rule == "SAME_TYPE":
            out.append({"relation": rel, "same_type": True, "from": [], "to": []})
        else:
            out.append({"relation": rel, "same_type": False,
                        "from": sorted(rule[0]), "to": sorted(rule[1])})
    out.append({"relation": "relates_to", "same_type": False, "from": [], "to": [], "fallback": True})
    return out


# ------------------------------------------------------------------------------ tools

def tools() -> list[dict]:
    assert set().union(*GROUPS.values()) == set(srv.TOOLS), set(srv.TOOLS) ^ set().union(*GROUPS.values())
    group_of = {n: g for g, names in GROUPS.items() for n in names}
    out = []
    for name, (fn, desc) in srv.TOOLS.items():
        params = []
        for p in inspect.signature(fn).parameters.values():
            ann = p.annotation if isinstance(p.annotation, str) else getattr(p.annotation, "__name__", str(p.annotation))
            params.append({"name": p.name, "annotation": ann,
                           "required": p.default is inspect.Parameter.empty,
                           "default": None if p.default is inspect.Parameter.empty else repr(p.default)})
        out.append({"name": name, "desc": desc, "group": group_of[name], "params": params})
    return out


def upsert_meta_keys() -> list[str]:
    m = re.search(r'if k not in \(("type", "force"[^)]*)\)', SERVER_SRC, re.S)
    keys = re.findall(r'"([a-z_]+)"', m.group(1))
    assert keys == ["type", "force", "operator_confirm", "retire", "expect_unchanged", "substitute"], keys
    return keys


def header() -> dict:
    return {"writable": list(srv._HEADER_WRITABLE), "frozen": list(srv._HEADER_FROZEN),
            "row": list(srv._PACKAGE_ROW), "meta_keys": upsert_meta_keys()}


# ------------------------------------------------------------------------------ gates

def _set_literal(src: str, name: str) -> list[str]:
    m = re.search(name + r"\s*=\s*\{([^}]*)\}", src, re.S)
    return sorted(re.findall(r'"([A-Z][A-Z-]+)"', m.group(1)))


def gates() -> dict:
    return {"mechanical": sorted(srv.GATE_NAMES),
            "judgment": _set_literal(CHECK_SRC, "judgment_gates"),
            "warn": _set_literal(CHECK_SRC, "warn_gates")}


def readiness_rules() -> dict:
    start = SERVER_SRC.index("def _readiness_report(")
    body = SERVER_SRC[start:]
    body = body[:body.index("\ndef ", 10)]
    phase_at = body.index('elif scope == "phase":')
    slice_at = body.index("else:  # slice")
    out: dict[str, list[dict]] = {"package": [], "phase": [], "slice": []}
    base_indent: dict[str, int] = {}
    for m in re.finditer(r'rule\(\s*"([a-z-]+)",\s*"(blocking|advisory)"', body):
        pos = m.start()
        scope = "package" if pos < phase_at else "phase" if pos < slice_at else "slice"
        line_start = body.rfind("\n", 0, pos) + 1
        indent = pos - line_start
        base_indent.setdefault(scope, indent)
        out[scope].append({"rule": m.group(1), "severity": m.group(2),
                           "conditional": indent > base_indent[scope]})
    counts = {s: len(v) for s, v in out.items()}
    assert counts == {"package": 29, "phase": 5, "slice": 5}, counts
    return out


def events() -> dict:
    return {"all": sorted(srv.PE_EVENT_TYPES), "server_only": dict(sorted(srv._SERVER_ONLY_EVENTS.items()))}


def verdict_sets(sch: dict) -> dict:
    cols = {t['table']: {c['name']: c for c in t['columns']} for t in sch["tables"]}
    return {"audit_verdicts": cols['audit_verdicts']['verdict']['check_in'],
            "verified_by": cols["audit_verdicts"]["verified_by"]["check_in"],
            "verification_method": cols["audit_verdicts"]["verification_method"]["check_in"],
            "readiness_statuses": ["pass", "fail", "waived", "indeterminate"],
            "gate_outcome": cols["execution_gates"]["outcome"]["check_in"]}


# -------------------------------------------------------------------------- workflow

def stages() -> dict:
    wf = (BUNDLE / "references" / "workflow.md").read_text(encoding="utf-8")
    phases = re.findall(r"^## Phase ([ABC]) — (.+)$", wf, re.M)
    parts = re.split(r"^### (\d+)\. (.+)$", wf, flags=re.M)
    stage_rows = []
    for i in range(1, len(parts), 3):
        num, title, block = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
        stage_rows.append({"n": num, "title": title, "human": "✅" in block})
    loops_txt = wf[wf.index("## Loops"):]
    loops = sorted({int(n) for n in re.findall(r"\((\d+)\)", loops_txt.split("\n\n")[1])})
    assert len(stage_rows) == 22 and [s["n"] for s in stage_rows] == list(range(1, 23))
    phase_of = []
    for letter, title in phases:
        seg = wf[wf.index(f"## Phase {letter} — {title}"):]
        nxt = re.search(r"^## (?!Phase " + letter + ")", seg[5:], re.M)
        seg = seg[:nxt.start() + 5] if nxt else seg
        nums = [int(n) for n in re.findall(r"^### (\d+)\.", seg, re.M)]
        phase_of.append({"letter": letter, "title": title, "stages": nums})
    assert [p["stages"][0] for p in phase_of] == [1, 9, 16], phase_of
    return {"phases": phase_of, "stages": stage_rows, "loops": loops,
            "human": [s["n"] for s in stage_rows if s["human"]]}


def _frontmatter(text: str) -> dict:
    fm = text.split("---\n")[1]
    out: dict[str, str] = {}
    key = None
    for line in fm.splitlines():
        m = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = "" if val in (">-", ">", "|") else val.strip('"')
        elif key and line.startswith("  "):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def skills() -> list[dict]:
    out = []
    for p in sorted((BUNDLE / "skills").glob("*/SKILL.md")):
        fm = _frontmatter(p.read_text(encoding="utf-8"))
        name = fm["name"]
        assert name == p.parent.name, (name, p.parent.name)
        dmi = fm.get("disable-model-invocation") == "true"
        ui_false = fm.get("user-invocable") == "false"
        group = "front" if name == "tamheed" else "scenario" if dmi else "discipline"
        out.append({"name": name, "description": fm['description'], "group": group,
                    "slash": not ui_false, "model": not dmi,
                    "arg_hint": fm.get("argument-hint", ""),
                    "lines": len(p.read_text(encoding="utf-8").splitlines())})
    counts = {g: sum(1 for s in out if s['group'] == g) for g in ("front", "scenario", "discipline")}
    assert counts == {"front": 1, "scenario": 16, "discipline": 8}, counts
    return out


def modes(sch: dict) -> dict:
    pk = next(t for t in sch["tables"] if t["table"] == "packages")
    cols = {c['name']: c for c in pk['columns']}
    return {"modes": cols['mode']['check_in'], "stage_glob": "stage:<id>",
            "profiles": cols["profile"]["check_in"]}


def hook() -> dict:
    data = json.loads((BUNDLE / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    ev = data["hooks"]["SessionStart"][0]
    h = ev["hooks"][0]
    return {"event": "SessionStart", "matcher": ev['matcher'], "command": h['command'],
            "commandWindows": h.get("commandWindows", ""), "timeout": h["timeout"],
            "statusMessage": h.get("statusMessage", "")}


def mcp() -> dict:
    data = json.loads((BUNDLE / ".mcp.json").read_text(encoding="utf-8"))
    s = data["mcpServers"]["tamheed"]
    return {"command": " ".join([s['command'], *s['args']])}


def maintainer() -> dict:
    lints = [(int(n), text.strip()) for n, text in re.findall(r"^    # (\d+)\) (.+)$", CHECK_SRC, re.M)]
    assert [n for n, _ in lints] == list(range(1, len(lints) + 1)), lints
    return {"suites": [Path(s).name for s in check.SUITES],
            "gates": [n for n, _ in check.GATES], "lints": lints,
            "lint8_surfaces": re.findall(r'"([^"]+)"', re.search(r"surfaces = \(([^)]*)\)", CHECK_SRC, re.S).group(1))}


def review_sections() -> list[tuple[str, str]]:
    import export_html  # noqa: E402  (the review page's section roster)
    return [(sid, title) for sid, title, _fn in export_html.SECTIONS]


# ------------------------------------------------------------------------------ facts

def facts() -> dict:
    sch = schema()
    return {
        "version": version(), "schema": sch, "lifecycles": lifecycle_sets(sch),
        "families": families(), "relations": relations(), "tools": tools(), "header": header(),
        "gates": gates(), "rules": readiness_rules(), "events": events(),
        "verdicts": verdict_sets(sch), "stages": stages(), "skills": skills(),
        "modes": modes(sch), "hook": hook(), "mcp": mcp(), "maintainer": maintainer(),
        "review_sections": review_sections(),
    }


def derived_ids(f: dict) -> list[str]:
    """Every content id the page needs prose for (both languages)."""
    ids: list[str] = []
    for fam in f["families"]:
        ids.append(f"type.{fam['type']}")
    for t in f["schema"]["tables"]:
        ids.append(f"table.{t['table']}")
        for c in t["columns"]:
            if c["block"]:
                ids.append(f"block.{c['block']}.{c['name']}")
            else:
                ids.append(f"col.{t['table']}.{c['name']}")
    for tr in f["schema"]["named_triggers"]:
        ids.append(f"trigger.{tr}")
    for v in f["schema"]["views"]:
        ids.append(f"view.{v}")
    for r in f["relations"]:
        ids.append(f"rel.{r['relation']}")
    for t in f["tools"]:
        ids.append(f"tool.{t['name']}")
        for p in t["params"]:
            ids.append(f"param.{t['name']}.{p['name']}")
    for g in ("read", "mutate", "staged", "export"):
        ids.append(f"toolgroup.{g}")
    for k in f["header"]["meta_keys"]:
        ids.append(f"meta.{k}")
    for tier in ("mechanical", "judgment", "warn"):
        ids.append(f"gatetier.{tier}")
        for g in f["gates"][tier]:
            ids.append(f"gate.{g}")
    seen = set()
    for scope in ("package", "phase", "slice"):
        for r in f["rules"][scope]:
            if r["rule"] not in seen:
                seen.add(r["rule"])
                ids.append(f"rule.{r['rule']}")
    for e in f["events"]["all"]:
        ids.append(f"event.{e}")
    for s in ("STD8", "STD9"):
        ids.append(f"lifecycle.{s}")
    for v in ["Draft", "Proposed", "Approved", "Rejected", "Deferred", "Review", "Implemented",
              "Superseded", "Obsolete"]:
        ids.append(f"status.{v}")
    for v in f["verdicts"]["audit_verdicts"]:
        ids.append(f"verdict.{v}")
    for v in f["verdicts"]["readiness_statuses"]:
        ids.append(f"rstatus.{v}")
    for p in f["stages"]["phases"]:
        ids.append(f"phase.{p['letter']}")
    for s in f["stages"]["stages"]:
        ids.append(f"stage.{s['n']:02d}")
    for s in f["skills"]:
        ids.append(f"skill.{s['name']}")
    for g in ("front", "scenario", "discipline"):
        ids.append(f"skillgroup.{g}")
    for m in f["modes"]["modes"] + ["stage"]:
        ids.append(f"mode.{m}")
    for p in f["modes"]["profiles"]:
        ids.append(f"profile.{p}")
    for n, _ in f["maintainer"]["lints"]:
        ids.append(f"lint.{n:02d}")
    for s in f["maintainer"]["suites"]:
        ids.append(f"suite.{s}")
    for g in f["maintainer"]["gates"]:
        ids.append(f"checkgate.{g}")
    for sid, _ in f["review_sections"]:
        ids.append(f"review.{sid}")
    # de-duplicate, keep order
    out, seen2 = [], set()
    for i in ids:
        if i not in seen2:
            seen2.add(i)
            out.append(i)
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    f = facts()
    ids = derived_ids(f)
    print("version", f["version"], "| tables", len(f["schema"]["tables"]), "| families", len(f["families"]),
          "| tools", len(f["tools"]), "| params", sum(len(t["params"]) for t in f["tools"]),
          "| gates", {k: len(v) for k, v in f['gates'].items()},
          "| rules", {k: len(v) for k, v in f['rules'].items()},
          "| skills", len(f["skills"]), "| stages", len(f["stages"]["stages"]),
          "| lints", len(f["maintainer"]["lints"]), "| suites", len(f["maintainer"]["suites"]),
          "| derived ids", len(ids))
