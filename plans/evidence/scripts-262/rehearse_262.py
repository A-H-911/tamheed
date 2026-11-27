"""Plan 262: three headless runs on seeded lab copies, under this bundle (R161, R168, D14).

    env -u TAMHEED_HOOK_LOG python -I plans/evidence/scripts-262/rehearse_262.py <scratch folder>

1. run-A (the lab's SL-004): three work-done entries carry `slice_id` SL-004, and the latest
   handoff names SL-004. Both signals of orient-resume step 7 hold.
   `/tamheed:orient-resume package` should resume SL-004 at the handoff and offer no kickoff.
2. run-A2: SL-004 is Implemented, and a new SL-005 (PH-1, Approved) has ONE work-done entry. The
   latest handoff still names SL-004. Only one signal holds for SL-005: the agent should state
   both facts and ask.
3. run-A again, a cold agent with a plain request: record a new defect and a new scope change.
   Recorded: whether each new row's item carries `create: true`, with no word about it in the
   prompt. A measurement, never a pass or a fail.

Each run is capped (--max-budget-usd). Counts and short quotes only are printed. Nothing is
committed to this repository.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
S248 = REPO / "plans" / "evidence" / "scripts-248"
sys.path[:0] = [str(BUNDLE / "server"), str(BUNDLE / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Skill", "ToolSearch",
         "Bash(git log:*)", "Bash(git status:*)", "Bash(git show:*)", "PowerShell(git log *)",
         "PowerShell(git status *)", "PowerShell(git show *)"]
APPEND = ("Harness note (plan 262 rehearsal): no operator is present in this run. It allows"
          " only the shell commands git log, git status and git show, plus the tamheed, Read,"
          " Glob, Grep, Skill and ToolSearch tools. Run one plain command per shell call, with"
          " no `&&`, `;`, pipes or `cd`. The working directory is already the project root.")
BUDGET, TURNS, TIMEOUT = 1.5, 50, 1200


def obs(key, value):
    print(f"OBS {key} {json.dumps(value, ensure_ascii=False, default=str)[:900]}")


def run(*cmd, cwd=None):
    env = {k: v for k, v in os.environ.items() if k != "TAMHEED_HOOK_LOG"}
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, env=env,
                          check=True).stdout


def ok(res, what):
    if not res.get("ok"):
        raise SystemExit(f"{what} refused: {json.dumps(res)[:800]}")
    return res


def journal(entries):
    ok(srv.progress_update(entries), "journal")


def seed_a(ws: Path) -> None:
    srv.PACKAGE_ROOT = ws
    ok(srv.package_open("package"), "open")
    try:
        for n, (wbs, line) in enumerate((("WBS-5", "Planned the bad-date check of add."),
                                         ("WBS-5", "Wrote the failing test for add."),
                                         ("WBS-6", "Started list --overdue.")), 1):
            journal([{"entry": line, "event_type": "work-done", "subject_id": wbs,
                      "slice_id": "SL-004", "actor": "agent:rehearsal-seed"}])
        journal([{"entry": "HANDOFF. Resume point: SL-004, WBS-6 (list --overdue) is half"
                           " done. The kickoff plan of SL-004 was approved last session.",
                  "event_type": "handoff", "slice_id": "SL-004",
                  "actor": "agent:rehearsal-seed"}])
    finally:
        srv.package_close()
    run("git", "add", "-A", cwd=ws)
    run("git", "commit", "-qm", "plan: rehearsal journal (package only)", cwd=ws)


def seed_b(ws: Path) -> None:
    srv.PACKAGE_ROOT = ws
    ok(srv.package_open("package"), "open")
    try:
        journal([{"entry": "HANDOFF. Resume point: SL-004 is closed.",
                  "event_type": "handoff", "slice_id": "SL-004",
                  "actor": "agent:rehearsal-seed"}])
        conn = srv._CURRENT.conn
        conn.execute("UPDATE slices SET lifecycle_status = 'Implemented' WHERE id = 'SL-004'")
        ok(srv.entity_upsert([{"type": "slice", "id": "SL-005", "title": "Export to CSV",
                               "phase_id": "PH-1", "sort_order": 9,
                               "lifecycle_status": "Approved"}]), "SL-005")
        journal([{"entry": "Looked at the CSV module for SL-005.", "event_type": "work-done",
                  "slice_id": "SL-005", "actor": "agent:rehearsal-seed"}])
    finally:
        srv.package_close()
    run("git", "add", "-A", cwd=ws)
    run("git", "commit", "-qm", "plan: rehearsal journal (package only)", cwd=ws)


def headless(ws: Path, out: Path, prompt: str) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cmd = [shutil.which("claude") or "claude", "-p", prompt, "--debug-file",
           str(out / "debug.log"), "--setting-sources", "project", "--plugin-dir", str(BUNDLE),
           "--permission-mode", "dontAsk", "--allowedTools", *ALLOW, "--append-system-prompt",
           APPEND, "--model", "opus", "--max-turns", str(TURNS), "--max-budget-usd",
           str(BUDGET), "--output-format", "json"]
    start = time.monotonic()
    env = {k: v for k, v in os.environ.items() if k != "TAMHEED_HOOK_LOG"}
    with (out / "stderr.txt").open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, cwd=ws, env=env, stdout=subprocess.PIPE, stderr=err,
                              timeout=TIMEOUT)
    (out / "result.json").write_bytes(proc.stdout)
    res = json.loads(proc.stdout.decode("utf-8", "replace"))
    for tr in glob.glob(str(Path.home() / f".claude/projects/*/{res.get('session_id')}.jsonl")):
        shutil.copy(tr, out / "transcript.jsonl")
    (out / "report.md").write_text(res.get("result") or "", encoding="utf-8")
    return {"subtype": res.get("subtype"), "turns": res.get("num_turns"),
            "cost": round(res.get("total_cost_usd") or 0.0, 2),
            "seconds": round(time.monotonic() - start),
            "denials": [d.get("tool_name") for d in res.get("permission_denials") or []]}


def calls(out: Path) -> list:
    path = out / "transcript.jsonl"
    rows = ([json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
            if path.exists() else [])
    found = []
    for r in rows:
        content = r.get("message", {}).get("content") if r.get("type") == "assistant" else None
        for part in content or []:
            if isinstance(part, dict) and part.get("type") == "tool_use":
                found.append((part["name"], part.get("input", {})))
    return found


def report(out: Path) -> str:
    return (out / "report.md").read_text(encoding="utf-8") if (out / "report.md").exists() else ""


def main(scratch: Path) -> None:
    scratch.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    for run_id in ("A", "A2"):            # seed_248 seeds run-<id> with the A rows unless "B"
        run(py, "-I", str(S248 / "setup_248.py"), str(scratch), f"run-{run_id}")
        run(py, "-I", str(S248 / "seed_248.py"), str(scratch), run_id)
    seed_a(scratch / "run-A")
    seed_b(scratch / "run-A2")
    total = 0.0
    for tag, ws in (("both", scratch / "run-A"), ("one", scratch / "run-A2")):
        out = scratch / "runs" / tag
        info = headless(ws, out, "/tamheed:orient-resume package")
        total += info["cost"]
        text = report(out)
        obs(f"{tag} session", info)
        obs(f"{tag} report", text[-1500:])
        obs(f"{tag} offers the kickoff", "slice-kickoff" in text)
        obs(f"{tag} names a handoff", "handoff" in text.lower())
        obs(f"{tag} searched the journal", [i for n, i in calls(out)
                                            if n.endswith("entity_query") and i.get("search")])
    # a headless session ends without package_close, so its lock stays on disk. The harness
    # stands in for the operator here, in scratch only (the first pass of this run met it)
    srv.PACKAGE_ROOT = scratch / "run-A"
    if (scratch / "run-A" / "package" / "data" / ".lock").exists():
        ok(srv.package_unlock("package", confirm=True), "unlock")
    out = scratch / "runs" / "create"
    info = headless(scratch / "run-A", out,
                    "Record two new rows in this project's Tamheed package, and change no code."
                    " First, a defect: the add command crashes on an empty title. Severity"
                    " high, found in SL-004. Second, a scope change: list gets a --json flag,"
                    " decided by DEC-003. Then stop.")
    total += info["cost"]
    obs("create session", info)
    items = [it for n, i in calls(out) if n.endswith("entity_upsert")
             for it in i.get("entities", []) if isinstance(it, dict)]
    obs("create items", [{"type": it.get("type"), "id": it.get("id"),
                          "create": it.get("create")} for it in items])
    obs("total cost", round(total, 2))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
