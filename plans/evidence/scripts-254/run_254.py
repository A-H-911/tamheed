"""Plan 254: run one command of the scratch Graphify in a fixed, recorded environment.

    python -I run_254.py <study> <step> <timeout s> [--net] [--out DIR] [--home DIR] -- <command> [args ...]

The environment: the scratch venv first on PATH; home, APPDATA, LOCALAPPDATA, TEMP and the Claude config
folder redirected into <study>/home (or --home DIR, a fresh one per build: X18); GRAPHIFY_BACKEND=none;
GRAPHIFY_NO_AUTO_REFRESH=1; the query log off; every AWS, model-provider, Claude-session and GRAPHIFY_
variable removed, then GRAPHIFY_OUT set from --out (X2); the audit hook on, blocking non-loopback network
unless --net. Writes out/<step>.json, the WHOLE stdout and stderr to out/<step>.stdout.txt and .stderr.txt
(X3), and out/audit-<step>.jsonl.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DROP = ("AWS_", "ANTHROPIC_", "OPENAI_", "GEMINI_", "GOOGLE_", "MOONSHOT_", "DEEPSEEK_", "AZURE_", "OLLAMA_",
        "CLAUDE_CODE_", "_CLAUDE_CODE_", "TAMHEED_", "GRAPHIFY_")


def env_for(study: Path, step: str, net: bool, out: str, home: str) -> dict:
    h = Path(home) if home else study / "home"
    for sub in ("AppData/Roaming", "AppData/Local", "tmp", ".claude"):
        (h / sub).mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(DROP)}
    env.update({
        "PATH": str(study / "venv" / "Scripts") + os.pathsep + env.get("PATH", ""),
        "USERPROFILE": str(h), "HOME": str(h), "APPDATA": str(h / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(h / "AppData" / "Local"), "TEMP": str(h / "tmp"), "TMP": str(h / "tmp"),
        "CLAUDE_CONFIG_DIR": str(h / ".claude"), "GRAPHIFY_BACKEND": "none", "GRAPHIFY_NO_AUTO_REFRESH": "1",
        "GRAPHIFY_QUERY_LOG_DISABLE": "1", "GRAPHIFY_NO_TIPS": "1", "PYTHONUTF8": "1",
        "G254_AUDIT_LOG": str(study / "out" / f"audit-{step}.jsonl"), "G254_BLOCK_NET": "0" if net else "1",
    })
    if out:
        env["GRAPHIFY_OUT"] = str(Path(out).resolve())
    return env


def main() -> None:
    study, step, timeout = Path(sys.argv[1]).resolve(), sys.argv[2], float(sys.argv[3])
    rest = sys.argv[4:]
    opts, cmd = rest[: rest.index("--")], rest[rest.index("--") + 1:]
    net = "--net" in opts
    out = opts[opts.index("--out") + 1] if "--out" in opts else ""
    home = opts[opts.index("--home") + 1] if "--home" in opts else ""
    (study / "out").mkdir(exist_ok=True)
    audit = study / "out" / f"audit-{step}.jsonl"
    audit.unlink(missing_ok=True)
    for stale in audit.parent.glob(audit.name + ".*"):
        stale.unlink()
    env = env_for(study, step, net, out, home)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=os.getcwd())
        code, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        so = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        code, se = "timeout", "TIMEOUT"
    secs = round(time.time() - t0, 2)
    (study / "out" / f"{step}.stdout.txt").write_text(so, encoding="utf-8")
    (study / "out" / f"{step}.stderr.txt").write_text(se, encoding="utf-8")
    events, garbled = [], 0
    for part in sorted(audit.parent.glob(audit.name + ".*")):  # one file per process (sitecustomize)
        for x in part.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                events.append(json.loads(x))
            except ValueError:
                garbled += 1
        part.unlink()
    audit.write_text("".join(json.dumps(e) + "\n" for e in sorted(events, key=lambda e: e["t"])), encoding="utf-8")
    summary: dict = {}
    for e in events:
        summary[e["event"]] = summary.get(e["event"], 0) + 1
    rec = {"step": step, "cwd": os.getcwd(), "cmd": cmd, "seconds": secs, "exit": code, "net_blocked": not net,
           "graphify_out": env.get("GRAPHIFY_OUT", ""), "home": env["USERPROFILE"], "audit": summary,
           "audit_garbled": garbled, "audit_processes": len({e["pid"] for e in events}),
           "blocked": [e for e in events if e.get("blocked")][:5],
           "processes": [e["args"][:2] for e in events if e["event"] == "subprocess.Popen"][:20],
           "writes_outside": sorted({e["args"][0] for e in events if e["event"] in ("open", "os.mkdir", "os.remove", "os.rename")
                                     and not any(str(x).lower().replace("\\\\", "\\") in e["args"][0].lower().replace("\\\\", "\\")
                                                 for x in (study,))})[:20]}
    (study / "out" / f"{step}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("step", "seconds", "exit", "audit", "blocked", "processes", "writes_outside")},
                     ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
