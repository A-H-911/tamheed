"""Plan 252: a headless `/tamheed:standup` on a seeded lab copy, under this bundle.

    env -u TAMHEED_HOOK_LOG python -I plans/evidence/scripts-252/rehearse_252.py <scratch folder>

1. Build a lab workspace (`scripts-248/setup_248.py`) and give it the open slice SL-004
   (`scripts-248/seed_248.py`, run A).
2. Record a FIRST report in-process, signed by the scripted operator `human:rehearsal-operator`
   (scratch only), so the next report is a daily one with a real window.
3. Move work in the window: WBS-5 claimed done with a work-done line, WBS-6 done, AC-007 met.
   Commit the package only, so the store is not behind.
4. Run `claude -p "/tamheed:standup package"` headless, with this bundle and no operator.
5. Check the transcript, the store and the page. Print counts only. Nothing is committed here.
"""
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
S248 = REPO / "plans" / "evidence" / "scripts-248"
sys.path[:0] = [str(BUNDLE / "server"), str(BUNDLE / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

OP = "human:rehearsal-operator"
# The skill reads `git log` and `git status` only; nothing wider is allowed (the automated
# security review of 2026-11-18 narrowed the 248 allowlist, which also allowed any python).
ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Skill", "ToolSearch",
         "Bash(git log:*)", "Bash(git status:*)", "PowerShell(git log *)",
         "PowerShell(git status *)"]
APPEND = ("Harness note (plan 252 rehearsal): no operator is present in this run. It allows"
          " only the shell commands git log and git status, plus the tamheed, Read, Glob,"
          " Grep, Skill and ToolSearch tools. Run one plain command per shell call, with no `&&`, `;`, pipes or"
          " `cd`. The working directory is already the project root.")
BUDGET, TURNS, TIMEOUT = 5.0, 70, 1500


def obs(key, value):
    print(f"OBS {key} {json.dumps(value, ensure_ascii=False, default=str)[:700]}")


def run(*cmd, cwd=None):
    env = {k: v for k, v in os.environ.items() if k != "TAMHEED_HOOK_LOG"}
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, env=env,
                          check=True).stdout


def ok(res, what):
    if not res.get("ok"):
        raise SystemExit(f"{what} refused: {json.dumps(res)[:800]}")
    return res


def seed_window(ws: Path) -> None:
    srv.PACKAGE_ROOT = ws
    ok(srv.package_open("package"), "open")
    try:
        first = ok(srv.standup_report(utc_offset="+03:00"), "first draft")
        now = first["plan_summary"]["suggest"]["now"]
        words = {"headline": "The command hardening slice starts.",
                 "did": "We planned the slice.", "challenges": "Nothing blocks the work.",
                 "next": "We start the slice.", "colour": "green", "slice_now": now,
                 "slice": "This slice hardens three commands. No task has started yet."}
        ok(srv.standup_report(narrative=words), "first words")
        ok(srv.standup_report(action="record", confirm={
            "operator_confirm": True, "by": OP, "words": "record it (rehearsal)",
            "colour": "green", "slice_now": now}), "first record")
        ok(srv.entity_upsert([{"type": "wbs-item", "id": "WBS-5", "substitute":
                               {"lifecycle_status": ["Approved", "Review"]}}]), "claim WBS-5")
        ok(srv.progress_update([{"entry": "Made add refuse a due date that is not YYYY-MM-DD.",
                                 "event_type": "work-done", "subject_id": "WBS-5",
                                 "actor": "agent:rehearsal-seed"}]), "work-done")
        srv._CURRENT.conn.execute("UPDATE wbs_items SET lifecycle_status = 'Implemented'"
                                  " WHERE id = 'WBS-6'")
        ok(srv.audit_record([{"ac_id": "AC-007", "verdict": "Met", "verified_by": "human",
                              "verification_method": "manual",
                              "evidence": "rehearsal seeding: ran the command by hand"}]),
           "verdict")
    finally:
        srv.package_close()
    run("git", "add", "-A", cwd=ws)
    run("git", "commit", "-qm", "plan: rehearsal window (package only)", cwd=ws)


def headless(ws: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cmd = [shutil.which("claude") or "claude", "-p", "/tamheed:standup package", "--debug-file",
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
    rows = [json.loads(x) for x in (out / "transcript.jsonl").read_text(encoding="utf-8")
            .splitlines() if x.strip()] if (out / "transcript.jsonl").exists() else []
    found = []
    for r in rows:
        for part in (r.get("message", {}).get("content") or []) if r.get("type") == "assistant" else []:
            if isinstance(part, dict) and part.get("type") == "tool_use":
                found.append((part["name"], part.get("input", {})))
    return found


def main(scratch: Path) -> None:
    scratch.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    run(py, "-I", str(S248 / "setup_248.py"), str(scratch), "run-A")
    run(py, "-I", str(S248 / "seed_248.py"), str(scratch), "A")
    ws = scratch / "run-A"
    seed_window(ws)
    out = scratch / "runs" / "standup"
    info = headless(ws, out)
    obs("session", info)
    made = calls(out)
    stand = [i for n, i in made if n.endswith("standup_report")]
    words = next((i.get("narrative") for i in stand if i.get("narrative")), None) or {}
    obs("standup calls", [{k: v for k, v in i.items() if k != "narrative"} for i in stand])
    obs("narrative keys", sorted(words))
    obs("slice keys", {k: words.get(k) for k in ("slice_now", "slice_next")})
    obs("words per key", {k: len(str(v).split()) for k, v in words.items()})
    obs("recorded by the agent", any(i.get("action") == "record" for i in stand))
    page = ws / "package" / "reports" / "draft.html"
    html = page.read_text(encoding="utf-8") if page.exists() else ""
    obs("draft page", {"exists": page.exists(), "sections": re.findall(
        r'<section class="card" id="([a-z]+)"', html), "one script": html.count("<script") == 1,
        "now mark": 's-now">now<' in html, "window states": sorted(set(re.findall(
            r'data-state="(done-window|claimed-window)"', html)))})
    debug = (out / "debug.log").read_text(encoding="utf-8", errors="replace") if (
        out / "debug.log").exists() else ""
    obs("ui-ux-pro-max loaded", "ui-ux-pro-max" in debug)
    srv.PACKAGE_ROOT = ws
    ok(srv.package_open("package"), "read")
    try:
        obs("reports", srv._CURRENT.conn.execute(
            "SELECT id, kind, lifecycle_status FROM standup_reports ORDER BY id").fetchall())
    finally:
        srv.package_close()
    obs("lock left", (ws / "package" / "data" / ".lock").exists())


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
