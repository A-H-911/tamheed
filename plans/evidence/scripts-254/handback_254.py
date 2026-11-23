"""Plan 254: save an agent's final report verbatim from its own transcript (hand-back call or last text).

    python -I handback_254.py <agent id> <out file>
"""
import json, re, sys
from pathlib import Path
hit = next((Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path(__file__).resolve().parents[3]))).glob(f"*/subagents/agent-{sys.argv[1]}.jsonl"))
text = ""
for line in hit.open(encoding="utf-8"):
    try:
        m = json.loads(line).get("message") or {}
    except ValueError:
        continue
    for c in m.get("content") or [] if isinstance(m.get("content"), list) else []:
        if c.get("type") == "tool_use" and c.get("name") == "SubagentHandback":
            inp = c.get("input", {})
            text = next((v for v in inp.values() if isinstance(v, str) and len(v) > 200), text)
        elif c.get("type") == "text" and m.get("role") == "assistant" and len(c.get("text", "")) > 200:
            text = c["text"] if not text else text
Path(sys.argv[2]).write_text(text, encoding="utf-8", newline="\n")
print(len(text), "characters saved;", text.count('{"fix"'), "fix rows")
