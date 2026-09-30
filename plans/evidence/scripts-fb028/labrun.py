"""Plan 172: drive one headless Claude Code session against the WORKING-TREE bundle, and handle
the package lock between sessions. Every session is a new client process (a `--resume` too):
the MCP server restarts with it, so a package a session left open is closed and its lock names
a dead process — measured on 2.1.286 by the probe (plans/evidence/lab-acceptance-report-*.md).

    python labrun.py run  --ws DIR --label NAME --prompt TEXT|@FILE [--resume SID] [--turns N]
                          [--budget USD] [--allow RULE ...]
    python labrun.py lock --ws DIR --package NAME [--unlock]     # observe; unlock on the operator's word

`run` writes <ws>/../runs/<label>/{result.json,stderr.txt,debug.log,transcript.jsonl} and prints
the session id, the turns, the cost, the denials and the agent's final report. Flags fixed by the
approved plan: Opus 5.5, `--plugin-dir` on the working tree, `--setting-sources ""` (no user
plugin, hook or setting loads), `--permission-mode dontAsk`, never bypassPermissions.
The hook's trace goes to <ws>/../runs/hook-trace.log (TAMHEED_HOOK_LOG set explicitly, because
the operator's settings.json sets it too and `env -u` alone is defeated when user settings load).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # the agents' reports carry arrows; cp1252 cannot print them
REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
MODEL = "opus"
BASE_ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Edit", "Write", "Skill",
              "ToolSearch"]


def run(a):
    ws = Path(a.ws).resolve()
    out = ws.parent / "runs" / a.label
    out.mkdir(parents=True, exist_ok=True)
    prompt = Path(a.prompt[1:]).read_text(encoding="utf-8") if a.prompt.startswith("@") else a.prompt
    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    cmd = [shutil.which("claude") or "claude", "-p"]  # a real .exe here: no shell, args as a list
    if a.resume:
        cmd += ["--resume", a.resume]
    cmd += [prompt, "--debug-file", str(out / "debug.log"), "--setting-sources", "",
            "--plugin-dir", str(BUNDLE), "--permission-mode", "dontAsk",
            "--allowedTools", *BASE_ALLOW, *(a.allow or []),
            "--model", MODEL, "--max-turns", str(a.turns), "--max-budget-usd", str(a.budget),
            "--output-format", "json"]
    trace = ws.parent / "runs" / "hook-trace.log"
    trace.touch()  # the hook traces only into an EXISTING file (plan 136's opt-in)
    env = dict(os.environ, TAMHEED_HOOK_LOG=str(trace))
    with (out / "stderr.txt").open("w", encoding="utf-8") as err:
        proc = subprocess.run(cmd, cwd=ws, env=env, stdout=subprocess.PIPE, stderr=err)
    (out / "result.json").write_bytes(proc.stdout)
    try:
        res = json.loads(proc.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        print("NO JSON RESULT; exit", proc.returncode); print(proc.stdout[:2000]); return 2
    sid = res.get("session_id")
    for t in glob.glob(str(Path.home() / f".claude/projects/*/{sid}.jsonl")):
        shutil.copy(t, out / "transcript.jsonl")
    print(f"SESSION {sid} subtype={res.get('subtype')} turns={res.get('num_turns')} "
          f"cost={res.get('total_cost_usd')} model={list((res.get('modelUsage') or {}).keys())}")
    print("DENIALS", json.dumps(res.get("permission_denials"))[:600])
    print("REPORT:\n" + (res.get("result") or "")[:6000])
    return 0


def lock(a):
    sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
    os.environ.pop("TAMHEED_HOOK_LOG", None)
    import tamheed_server as srv  # noqa: E402
    srv.PACKAGE_ROOT = Path(a.ws).resolve()
    lock_path = srv.PACKAGE_ROOT / a.package / "data" / ".lock"
    if not lock_path.exists():
        print("LOCK none"); return 0
    seen = srv._observe_lock(lock_path)
    print("LOCK", json.dumps(seen))
    if a.unlock:
        print("UNLOCK", json.dumps(srv.package_unlock(a.package, confirm=True))[:400])
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--ws", required=True); r.add_argument("--label", required=True)
    r.add_argument("--prompt", required=True); r.add_argument("--resume")
    r.add_argument("--turns", type=int, default=60); r.add_argument("--budget", type=float, default=8)
    r.add_argument("--allow", nargs="*")
    lk = sub.add_parser("lock")
    lk.add_argument("--ws", required=True); lk.add_argument("--package", required=True)
    lk.add_argument("--unlock", action="store_true")
    args = p.parse_args()
    sys.exit(run(args) if args.cmd == "run" else lock(args))
