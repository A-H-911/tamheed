"""Plan 172: the census of one or more headless transcripts, as M68 did — per session: the
client build, the model, the tool calls by name, every tamheed result with `"ok": false` (the
engine's refusals, quoted), the denied tools, the hook rows, the slash commands typed, and the
agent's final report verbatim. Reads the transcripts `labrun.py` copied beside each result.

    python labrun_census.py <runs dir> [<runs dir> ...]     # every */transcript.jsonl under each
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def census(path: Path, denials=None):
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    calls, refusals, hooks, commands, builds, models = Counter(), [], [], [], set(), set()
    results = {}
    for r in rows:
        if r.get("version"):
            builds.add(r["version"])
        a = r.get("attachment") or {}
        if a.get("type") == "model":
            models.add((a.get("identity") or {}).get("modelId"))
        if str(a.get("type", "")).startswith("hook"):
            hooks.append((a.get("hookName"), (a.get("content") or "")[:60].replace("\n", " ")))
        m = r.get("message")
        c = m.get("content") if isinstance(m, dict) else None
        if isinstance(c, str) and c.startswith("<command-message>"):
            commands.append(c.split("<command-name>")[1].split("</command-name>")[0])
        if isinstance(c, list):
            for x in c:
                if not isinstance(x, dict):
                    continue
                if x.get("type") == "tool_use":
                    calls[x["name"]] += 1
                    results[x["id"]] = x["name"]
                if x.get("type") == "tool_result":
                    name = results.get(x.get("tool_use_id"), "?")
                    body = x.get("content")
                    text = body if isinstance(body, str) else " ".join(
                        y.get("text", "") for y in body if isinstance(y, dict)) if isinstance(body, list) else ""
                    if name.startswith("mcp__plugin_tamheed") and '"ok": false' in text:
                        try:
                            j = json.loads(text)
                            err = [j.get("error") or j.get("errors")] + [
                                f"{it.get('id')}: {it.get('error')}" for it in j.get("items", []) if it.get("error")]
                        except Exception:  # noqa: BLE001
                            err = text[:300]
                        refusals.append((name.rsplit("__", 1)[1], json.dumps(err, ensure_ascii=False)[:400]))
                    if x.get("is_error"):
                        refusals.append((name, "TOOL ERROR " + text[:200].replace("\n", " ")))
    res = json.loads((path.parent / "result.json").read_text(encoding="utf-8")) if (path.parent / "result.json").exists() else {}
    print(f"=== {path.parent.name}: session {res.get('session_id')} build {sorted(builds)} model {sorted(m for m in models if m)}"
          f" turns {res.get('num_turns')} cost {res.get('total_cost_usd')} rows {len(rows)}")
    print("  commands typed:", commands)
    print("  calls:", dict(calls.most_common()))
    dn = denials if denials is not None else res.get("permission_denials") or []
    print("  denials (every turn):", [(d.get("tool_name"), (d.get("tool_input") or {}).get("command", "")[:70]) for d in dn])
    print("  hooks:", hooks)
    print("  refusals/errors:")
    for name, err in refusals:
        print(f"    - {name}: {err}")
    print("  final report:\n    " + (res.get("result") or "").replace("\n", "\n    "))
    print()


if __name__ == "__main__":
    # a resumed turn's transcript is the whole conversation so far: one census per session, on
    # its last turn's copy; the per-turn line lists each turn's label, turns and the cumulative cost
    for d in sys.argv[1:]:
        by_sid = {}
        for res_path in sorted(Path(d).glob("*/result.json"), key=lambda q: q.stat().st_mtime):
            res = json.loads(res_path.read_text(encoding="utf-8"))
            by_sid.setdefault(res.get("session_id"), []).append(
                (res_path.parent.name, res.get("num_turns"), res.get("total_cost_usd"), res.get("permission_denials") or []))
        for sid, turns in by_sid.items():
            print(f"### session {sid}: turns " + "; ".join(f"{lab} ({n} turns, cumulative ${c:.2f})" for lab, n, c, _ in turns))
            census(Path(d) / turns[-1][0] / "transcript.jsonl", [x for *_, dd in turns for x in dd])
