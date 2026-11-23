"""Plan 254, step 5.5: the A/B sessions (G11, G14; freeze F6 version 3, tasks in ab_tasks.json).

    python -I ab_254.py <study> setup                 builds the 12 copies (6 tasks x arms A and B)
    python -I ab_254.py <study> run <task> <arm> <n>  one headless Opus session, saved as results/ab/<task>-<arm>-<n>
    python -I ab_254.py <study> all                   every task, arm and repeat (2), in a fixed interleaved order
    python -I ab_254.py <study> score                 scores every saved session -> results/ab.summary.json

Both arms: `git archive <build_at>` with plans/ removed and no .git; the copy's own .claude/settings.json without
the tamheed plugin; `--setting-sources project --strict-mcp-config --disable-slash-commands`, Opus, dontAsk, the
same tools, at most 0.60 USD a session. Arm B adds exactly what `graphify claude install --project` writes, a
map built by `graphify update` (no model), and the scratch venv first on PATH. Text read = the characters of
every tool result that entered the session (the G14 measure).
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import places_254 as P  # noqa: E402

TASKS = {t["id"]: t for t in json.loads((HERE / "ab_tasks.json").read_text(encoding="utf-8"))["tasks"]}
TOOLS = ["Read", "Grep", "Glob", "Bash(graphify:*)", "Bash(rg:*)"] + (["Skill"] if os.environ.get("G254_AB_SKILLS") == "1" else [])
DROP = ("TAMHEED_", "GRAPHIFY_", "AWS_")


def copy_for(study: Path, task: str, arm: str) -> Path:
    return study / "ab" / f"{task}-{arm}"


def setup(study: Path) -> None:
    repo = study / "hist"
    for tid, t in TASKS.items():
        rev = P.sha(str(repo), t["build_at"])
        for arm in ("A", "B"):
            d = copy_for(study, tid, arm)
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True)
            blob = subprocess.run([*P.GIT, "-C", str(repo), "archive", rev], capture_output=True, check=True).stdout
            tarfile.open(fileobj=io.BytesIO(blob)).extractall(d, filter="data")
            shutil.rmtree(d / "plans", ignore_errors=True)
            s = d / ".claude" / "settings.json"
            if s.exists():
                cfg = json.loads(s.read_text(encoding="utf-8"))
                cfg.pop("enabledPlugins", None)
                cfg.pop("extraKnownMarketplaces", None)
                s.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            assert not (d / ".git").exists()
            if arm == "B":
                (d / ".graphifyignore").write_text("CHANGELOG.md\nindex.html\ndocs/guide/figures/\ngenerated-samples/\n"
                                                   "evals/sample-results/\n", encoding="utf-8")
                for cmd in (["claude", "install", "--project"], ["update", "."]):
                    r = subprocess.run([sys.executable, "-I", str(HERE / "run_254.py"), str(study), f"ab-{tid}-{' '.join(cmd)[:6]}",
                                        "900", "--home", str(study / "ab" / "home"), "--",
                                        str(study / "venv" / "Scripts" / "graphify.exe"), *cmd],
                                       capture_output=True, text=True, encoding="utf-8", cwd=str(d))
                    assert '"exit": 0' in r.stdout, (tid, cmd, r.stdout[-400:])
                assert (d / "graphify-out" / "graph.json").exists()
            print(tid, arm, "ready", sum(1 for _ in d.rglob("*") if _.is_file()), "files")


def prompt(t: dict) -> str:
    return (t["question"] + "\n\nWork only from the files in the current directory. End your answer with one JSON "
            "block in a ```json fence, exactly in this shape: " + t["json"])


def run(study: Path, tid: str, arm: str, n: int) -> None:
    t, d = TASKS[tid], copy_for(study, tid, arm)
    out = Path(os.environ.get("G254_AB_DIR", str(HERE / "results" / "ab")))  # v4: transcripts kept privately
    out.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(DROP)}
    if arm == "B":
        env.update(PATH=str(study / "venv" / "Scripts") + os.pathsep + env["PATH"], GRAPHIFY_BACKEND="none",
                   GRAPHIFY_NO_AUTO_REFRESH="1", GRAPHIFY_QUERY_LOG_DISABLE="1")
    # v4 (post hoc, critic Y1): G254_AB_SKILLS=1 keeps skills on, so arm B gets Graphify's project skill and both arms
    # the same built-in skills (probe: arm A loads 19 and no graphify skill).
    skills_off = [] if os.environ.get("G254_AB_SKILLS") == "1" else ["--disable-slash-commands"]
    cmd = [shutil.which("claude") or "claude", "-p", prompt(t), "--model", "opus", "--setting-sources", "project",
           "--strict-mcp-config", *skills_off, "--permission-mode", "dontAsk", "--allowedTools", *TOOLS,
           "--max-budget-usd", "0.60", "--output-format", "stream-json", "--verbose", "--no-session-persistence"]
    p = subprocess.run(cmd, cwd=str(d), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200)
    (out / f"{tid}-{arm}-{n}.jsonl").write_text(p.stdout, encoding="utf-8")
    last = [json.loads(x) for x in p.stdout.splitlines() if x.startswith("{") and '"type":"result"' in x.replace(" ", "")]
    print(tid, arm, n, "exit", p.returncode, "cost", last[-1].get("total_cost_usd") if last else None, flush=True)


def score_one(path: Path) -> dict:
    tid, arm, n = path.stem.split("-")
    t = TASKS[tid]
    events = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.startswith("{")]
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    res = next((e for e in reversed(events) if e.get("type") == "result"), {})
    read_chars, calls = 0, {}
    for e in events:
        msg = e.get("message") if isinstance(e.get("message"), dict) else {}
        for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
            if c.get("type") == "tool_result":
                body = c.get("content")
                read_chars += len(body if isinstance(body, str) else json.dumps(body))
            elif c.get("type") == "tool_use":
                cmdline = (c.get("input") or {}).get("command", "") if c["name"] == "Bash" else ""
                real = re.search(r"(^|[;&|]\s*)graphify(\.exe)?\s+(query|affected|explain|path|section)", cmdline)
                skill = c["name"] == "Skill" and "graphify" in json.dumps(c.get("input"))
                name = c["name"] + (":graphify" if real or skill else "")  # v4: by command name (critic Y3)
                calls[name] = calls.get(name, 0) + 1
    text = res.get("result") or ""
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
    try:
        ans = json.loads(blocks[-1]) if blocks else {}
    except ValueError:
        ans = {}
    truth, neutral = t["truth"], set(t.get("neutral", []))
    right = total = false = 0
    for k, v in truth.items():
        got = ans.get(k)
        if k == "places":
            names = [str(x).replace("\\", "/") for x in (got or [])]
            for f, fn in v:
                total += 1
                right += any(f in x and (fn is None or re.search(r"\b" + re.escape(fn) + r"\b", x)) for x in names)
            false += sum(1 for x in names if not any(f in x for f, _ in v))
        elif isinstance(v, list):
            got = {str(x).strip("`() ").split(".")[-1] for x in (got or [])}
            total += len(v)
            right += len(set(v) & got)
            false += len(got - set(v) - neutral)
        else:
            total += 1
            right += str(got or "").strip("`() ").split(".")[-1] == v
    return {"task": tid, "arm": arm, "n": int(n), "right": right, "of": total, "false": false, "read_chars": read_chars,
            "cost": res.get("total_cost_usd"), "turns": res.get("num_turns"), "ms": res.get("duration_ms"),
            "subtype": res.get("subtype"), "calls": calls, "plugins": init.get("plugins"), "mcp": init.get("mcp_servers"),
            "skills": init.get("skills") or init.get("slash_commands"), "model": init.get("model")}


def score(study: Path) -> None:
    src = Path(os.environ.get("G254_AB_DIR", str(HERE / "results" / "ab")))
    rows = [score_one(p) for p in sorted(src.glob("*.jsonl"))]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], []).append(r)
    summ = {}
    for arm, rs in by.items():
        summ[arm] = {"sessions": len(rs), "right": sum(r["right"] for r in rs), "of": sum(r["of"] for r in rs),
                     "false": sum(r["false"] for r in rs), "read_chars": sum(r["read_chars"] for r in rs),
                     "cost": round(sum(r["cost"] or 0 for r in rs), 2), "turns": sum(r["turns"] or 0 for r in rs)}
    pairs = {}
    for r in rows:
        pairs.setdefault(r["task"], {}).setdefault(r["arm"], []).append(r["read_chars"])
    spread = {t: {a: (min(v), max(v)) for a, v in arms.items()} for t, arms in pairs.items()}
    out = {"rows": rows, "by_arm": summ, "read_spread_by_task": spread}
    if "A" in summ and "B" in summ:
        a, b = summ["A"], summ["B"]
        less = 1 - b["read_chars"] / max(1, a["read_chars"])
        noisy = [t for t, s in spread.items() if "A" in s and "B" in s and max(s["B"]) >= min(s["A"])]
        out["g14"] = {"less_text_read": round(less, 3), "right_A": a["right"], "right_B": b["right"],
                      "tasks_where_spreads_overlap": noisy,
                      "pass": less >= 0.25 and b["right"] >= a["right"] and not noisy}
    (HERE / "results" / os.environ.get("G254_AB_SUMMARY", "ab.summary.json")).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in out if k != "rows"}, indent=1))
    for r in rows:
        print(f"{r['task']:4s} {r['arm']} {r['n']} right {r['right']}/{r['of']} false {r['false']} read {r['read_chars']:7d} "
              f"cost {r['cost']} turns {r['turns']} {r['subtype']} calls {r['calls']}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    st, mode = Path(sys.argv[1]).resolve(), sys.argv[2]
    if mode == "setup":
        setup(st)
    elif mode == "run":
        run(st, sys.argv[3], sys.argv[4], int(sys.argv[5]))
    elif mode == "all":
        for n in (1, 2):
            for tid in TASKS:
                for arm in (("A", "B") if n == 1 else ("B", "A")):
                    done = Path(os.environ.get("G254_AB_DIR", str(HERE / "results" / "ab"))) / f"{tid}-{arm}-{n}.jsonl"
                    if not done.exists():
                        run(st, tid, arm, n)
    else:
        score(st)
