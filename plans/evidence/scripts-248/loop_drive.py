"""Plan 248: drive /tamheed:loop-iteration as an external loop, one fresh session per pass.

    python -I loop_drive.py --ws <run folder> --run <label> --passes N --ledger <file>

Each pass is a new `claude -p "/tamheed:loop-iteration package"` process (the recipe of
scripts-fb028/labrun.py, with `--setting-sources project` so the project note loads as in a
field). Around each pass the driver reads the store IN-PROCESS (open, read, close in `finally`),
the scratch git log and the tamheed repository's own status. It stops on: a `stop=` other than
`none`, no ITERATION line, a lock left behind (never unlocked here), a VOID pass (timeout, a cap,
a denied test run), a change in the tamheed repository, or the ledger's caps (L3: 6 passes,
15 USD, 4 USD a pass).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path[:0] = [str(BUNDLE / "server"), str(BUNDLE / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

PROMPT = "/tamheed:loop-iteration package"
ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Edit", "Write", "Skill",
         "ToolSearch", "Bash(git:*)", "Bash(python:*)", "PowerShell(git *)",
         "PowerShell(python *)"]
APPEND = ("Harness note (plan 248 rehearsal): this run allows only git and python shell"
          " commands, plus the tamheed, Read, Edit, Write, Glob, Grep, Skill and ToolSearch"
          " tools. Run one plain command per shell call, with no `&&`, `;`, pipes or `cd`."
          " The working directory is already the project root.")
MAX_PASSES, MAX_COST, PASS_BUDGET, TURNS, TIMEOUT = 6, 15.0, 4.0, 80, 1200
LINE = re.compile(r"ITERATION:\s*wbs=(?P<wbs>\S+)\s+slice=(?P<slice>\S+)\s+acs_moved=(?P<acs>\S+)"
                  r"\s+gate=(?P<gate>\S+)\s+ready=(?P<ready>\S+)\s+stop=(?P<stop>.+?)"
                  r"\s+lessons_pending=(?P<lp>\S+)")
TEST_WORDS = ("unittest", "test_tracker", "pytest")


def git(cwd, *args) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          check=True).stdout.strip()


def store_read(ws: Path) -> dict:
    """One in-process read of the package. Never called while a lock is on disk."""
    srv.PACKAGE_ROOT = ws
    opened = srv.package_open("package")
    if not opened.get("ok"):
        return {"error": opened.get("error")}
    try:
        c, t = srv._CURRENT.conn, srv.ENTITY_TABLES
        q = lambda sql, *p: [list(r) for r in c.execute(sql, p).fetchall()]
        num = "CAST(SUBSTR(id, INSTR(id, '-') + 1) AS INTEGER)"
        g = srv.gate_run()
        return {
            "wbs": q(f"SELECT id, slice_id, lifecycle_status FROM {t['wbs-item']}"
                     f" WHERE lifecycle_status <> 'Implemented' OR {num} >= 5 ORDER BY {num}"),
            "slices": q(f"SELECT id, lifecycle_status FROM {t['slice']} WHERE {num} >= 4"),
            "verdicts": q("SELECT ac_id, verdict FROM v_latest_verdicts WHERE"
                          " CAST(SUBSTR(ac_id, 4) AS INTEGER) >= 7 ORDER BY ac_id"),
            "verdict_rows": q("SELECT COUNT(*) FROM audit_verdicts")[0][0],
            "journal": q(f"SELECT id, event_type, actor, subject_id, SUBSTR(entry, 1, 160)"
                         f" FROM progress_entries ORDER BY {num}"),
            "defects_open": q(f"SELECT id, severity, SUBSTR(title, 1, 80) FROM {t['defect']}"
                              " WHERE lifecycle_status IN ('Open', 'In-progress')"),
            "deferred": q(f"SELECT id, lifecycle_status, SUBSTR(title, 1, 80)"
                          f" FROM {t['deferred-work']}"),
            "questions": q(f"SELECT id, lifecycle_status FROM {t['open-question']}"),
            "scope": q(f"SELECT id, lifecycle_status FROM {t['scope-change']}"),
            "lessons_proposed": q(f"SELECT id FROM {t['lesson']}"
                                  " WHERE lifecycle_status = 'Proposed'"),
            "gate_ready": g["ready"],
            "gates_failing": sorted(k for k, v in g["gates"].items()
                                    if isinstance(v, dict) and v.get("status") == "fail"),
        }
    finally:
        srv.package_close()


def run_pass(ws: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cmd = [shutil.which("claude") or "claude", "-p", PROMPT, "--debug-file",
           str(out / "debug.log"), "--setting-sources", "project", "--plugin-dir", str(BUNDLE),
           "--permission-mode", "dontAsk", "--allowedTools", *ALLOW, "--append-system-prompt",
           APPEND, "--model", "opus", "--max-turns", str(TURNS), "--max-budget-usd",
           str(PASS_BUDGET), "--output-format", "json"]
    trace = ws.parent / "runs" / "hook-trace.log"
    trace.parent.mkdir(parents=True, exist_ok=True)
    trace.touch()
    env = dict(os.environ, TAMHEED_HOOK_LOG=str(trace))
    start = time.monotonic()
    try:
        with (out / "stderr.txt").open("w", encoding="utf-8") as err:
            proc = subprocess.run(cmd, cwd=ws, env=env, stdout=subprocess.PIPE, stderr=err,
                                  timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"void": "timeout", "seconds": round(time.monotonic() - start)}
    (out / "result.json").write_bytes(proc.stdout)
    try:
        res = json.loads(proc.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return {"void": f"no JSON result (exit {proc.returncode})"}
    sid = res.get("session_id")
    for tr in glob.glob(str(Path.home() / f".claude/projects/*/{sid}.jsonl")):
        shutil.copy(tr, out / "transcript.jsonl")
    text = (res.get("result") or "").replace("`", "")
    hits = list(LINE.finditer(text))
    denials = res.get("permission_denials") or []
    info = {"session": sid, "subtype": res.get("subtype"), "turns": res.get("num_turns"),
            "cost": res.get("total_cost_usd") or 0.0,
            "seconds": round(time.monotonic() - start), "denials": denials,
            "line": hits[-1].group(0) if hits else None,
            "fields": hits[-1].groupdict() if hits else None, "lines_found": len(hits)}
    if res.get("subtype") != "success":
        info["void"] = f"subtype {res.get('subtype')}"
    elif any(w in json.dumps(d) for d in denials for w in TEST_WORDS):
        info["void"] = "a test run was denied"
    (out / "report.md").write_text(res.get("result") or "", encoding="utf-8")
    return info


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ws", required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--passes", type=int, required=True)
    p.add_argument("--ledger", required=True)
    a = p.parse_args()
    ws, ledger_path = Path(a.ws).resolve(), Path(a.ledger)
    ledger = (json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists()
              else {"passes": 0, "cost": 0.0, "rows": []})
    lock = ws / "package" / "data" / ".lock"
    for k in range(1, a.passes + 1):
        if ledger["passes"] >= MAX_PASSES or ledger["cost"] + PASS_BUDGET > MAX_COST:
            print(f"STOP ledger cap: {ledger['passes']} passes, {ledger['cost']:.2f} USD")
            return 0
        if lock.exists():
            print("STOP a lock is on disk before the pass:", lock.read_text()[:300])
            return 1
        repo_before = git(REPO, "status", "--porcelain", "-uall")
        before, head_before = store_read(ws), git(ws, "rev-parse", "HEAD")
        out = ws.parent / "runs" / a.run / f"p{k}"
        info = run_pass(ws, out)
        info["lock_left"] = lock.exists()
        info["commits"] = git(ws, "log", "--format=%h %s", f"{head_before}..HEAD").splitlines()
        info["dirty"] = git(ws, "status", "--porcelain", "-uall").splitlines()
        after = {} if info["lock_left"] else store_read(ws)
        info["journal_new"] = [r for r in after.get("journal", [])
                               if r not in before.get("journal", [])]
        info["store"] = {key: v for key, v in after.items() if key != "journal"}
        info["repo_changed"] = git(REPO, "status", "--porcelain", "-uall") != repo_before
        ledger["passes"] += 1
        ledger["cost"] += info.get("cost") or 0.0
        ledger["rows"].append({"run": a.run, "pass": k, "line": info.get("line"),
                               "cost": info.get("cost"), "void": info.get("void")})
        ledger_path.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
        (out / "pass.json").write_text(json.dumps(info, indent=1, default=str),
                                       encoding="utf-8")
        print(f"PASS {a.run}/p{k}: {info.get('line')} | turns {info.get('turns')}"
              f" | {info.get('cost', 0):.2f} USD | {info.get('seconds')} s"
              f" | denials {len(info.get('denials') or [])} | void {info.get('void')}")
        print("  wbs", info["store"].get("wbs"), "| verdicts", info["store"].get("verdicts"))
        print("  commits", info["commits"], "| dirty", info["dirty"][:6],
              "| lock", info["lock_left"], "| repo changed", info["repo_changed"])
        print("  journal +", [r[:4] for r in info["journal_new"]])
        print("  gate_ready", info["store"].get("gate_ready"), info["store"].get("gates_failing"),
              "| open DEF", len(info["store"].get("defects_open") or []))
        stop = (info.get("fields") or {}).get("stop", "").strip()
        if (info.get("void") or not info.get("line") or info["lock_left"]
                or info["repo_changed"] or stop != "none"):
            print(f"STOP after p{k}: stop={stop or '-'} void={info.get('void')}"
                  f" line={'yes' if info.get('line') else 'no'}")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
