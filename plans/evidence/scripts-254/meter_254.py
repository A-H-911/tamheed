"""Plan 254: coverage, quotes and cost of a reader, from its own transcript, never from its word.

    python -I meter_254.py <study folder> <reader> <agent id> [<agent id> ...]

Coverage: every bundle of bundles/<reader>/ must have been returned whole by a Read call (the result's
last line number equals the bundle's line count). Quotes: each FACTS/PURPOSE quote must occur, with
whitespace collapsed, in the source file it names (or anywhere in the clone, reported apart).
Cost: list price of the transcript's own token counts, one count per message id.
"""
import json
import re
import sys
from pathlib import Path

PRICE = {  # USD per million tokens: input, 5-minute cache write, cache hit, output (pricing page, 2026-11-23)
    "claude-opus-5-5": (4.0, 5.0, 0.20, 20.0),
    "claude-sonnet-5-5": (2.0, 2.5, 0.10, 10.0),
    "claude-haiku-5-5": (0.10, 0.125, 0.01, 0.50),
    "claude-haiku-5-5>100k": (0.50, 0.625, 0.05, 2.50),
    "claude-fable-5-2": (8.0, 10.0, 0.20, 40.0),
}
REPO = Path(__file__).resolve().parents[3]
PROJECTS = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(REPO))  # Claude's folder name for this repo


def transcript(agent: str) -> Path:
    hits = list(PROJECTS.glob(f"*/subagents/agent-{agent}.jsonl"))
    if not hits:
        sys.exit(f"no transcript for {agent}")
    return hits[0]


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace(" ↵", "")).strip()


def main(study: Path, reader: str, agents: list[str], report: str = "") -> None:
    bundles = {f.name: f for f in sorted((study / "bundles" / reader).glob("*.txt"))}
    seen: dict[str, int] = {}
    usage: dict[str, tuple[str, dict]] = {}
    final = ""
    calls = 0
    for agent in agents:
        uses = {}
        for line in transcript(agent).open(encoding="utf-8"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message") or {}
            if not isinstance(m, dict):
                continue
            if m.get("usage") and m.get("id"):
                usage[m["id"]] = (m.get("model", ""), m["usage"])
            content = m.get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if c.get("type") == "tool_use":
                    calls += 1
                    uses[c["id"]] = c.get("input", {})
                elif c.get("type") == "tool_result":
                    inp = uses.get(c.get("tool_use_id"), {})
                    name = Path(str(inp.get("file_path", ""))).name
                    if name in bundles and Path(inp["file_path"]).parent.name == reader:
                        body = c.get("content")
                        body = body if isinstance(body, str) else "".join(x.get("text", "") for x in body or [] if isinstance(x, dict))
                        nums = [int(x) for x in re.findall(r"^\s*(\d+)[\t→]", body, re.M)]
                        if nums and not inp.get("offset") and not inp.get("limit"):
                            seen[name] = max(seen.get(name, 0), max(nums))
                elif c.get("type") == "text" and m.get("role") == "assistant":
                    final = c.get("text", "") or final
    if report:  # a report handed back outside the transcript (SubagentHandback)
        final = Path(report).read_text(encoding="utf-8", errors="replace")
    cover = []
    for name, f in bundles.items():
        need = f.read_text(encoding="utf-8").count("\n")
        cover.append((name, seen.get(name, 0), need, seen.get(name, 0) >= need))
    cost = 0.0
    tot = {"in": 0, "write": 0, "hit": 0, "out": 0}
    for model, u in usage.values():
        ctx = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        key = model + (">100k" if model.startswith("claude-haiku") and ctx > 100_000 else "")
        p = PRICE.get(key, PRICE["claude-opus-5-5"])
        vals = (u.get("input_tokens") or 0, u.get("cache_creation_input_tokens") or 0, u.get("cache_read_input_tokens") or 0, u.get("output_tokens") or 0)
        for k, v in zip(tot, vals):
            tot[k] += v
        cost += sum(v * q for v, q in zip(vals, p)) / 1e6
    models = sorted({m for m, _ in usage.values()})
    facts, bad, elsewhere, kinds = [], [], 0, {}
    src_text: dict[str, str] = {}
    for line in final.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            fact = json.loads(line)
        except ValueError:
            bad.append(("unparsed", line[:120]))
            continue
        q, path = squash(fact.get("quote", "")), fact.get("path", "")
        if not q:
            bad.append(("no quote", line[:120]))
            continue
        if path not in src_text and (study / "src" / path).is_file():
            src_text[path] = squash((study / "src" / path).read_text(encoding="utf-8", errors="replace"))
        if q in src_text.get(path, ""):
            facts.append(fact)
            kinds[fact.get("kind", "purpose")] = kinds.get(fact.get("kind", "purpose"), 0) + 1
        elif any(q in squash(p.read_text(encoding="utf-8", errors="replace")) for p in (study / "src").rglob("*") if p.is_file() and p.suffix in (".py", ".md", ".toml", ".json", ".ts", ".yml")):
            elsewhere += 1
            bad.append(("quote in another file", path, q[:80]))
        else:
            bad.append(("quote not found", path, q[:80]))
    out = {"reader": reader, "models": models, "calls": calls, "messages": len(usage), "tokens": tot,
           "usd": round(cost, 2), "bundles_whole": sum(c[3] for c in cover), "bundles": len(cover),
           "gaps": [c for c in cover if not c[3]], "facts_kept": len(facts), "by_kind": kinds,
           "rejected": len(bad), "rejected_sample": bad[:12]}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    keep = Path(__file__).resolve().parent / "readers"
    keep.mkdir(exist_ok=True)
    (keep / f"{reader}.facts.jsonl").write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in facts), encoding="utf-8", newline="\n")
    (keep / f"{reader}.meter.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[3:]
    rep = args.pop(args.index("--report") + 1) if "--report" in args else ""
    args = [a for a in args if a != "--report"]
    main(Path(sys.argv[1]).resolve(), sys.argv[2], args, rep)
