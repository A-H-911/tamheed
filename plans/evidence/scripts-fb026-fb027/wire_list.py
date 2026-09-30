"""The wire: start the bundle's MCP server over stdio with `uv run` (the PEP 723 route the
plugin uses), send `initialize` and `tools/list`, print `{tool name: description}` as JSON.
The instrument for the descriptions class: what a client that connects now receives.

Run:  python wire_list.py <bundle dir (.../plugins/tamheed)> <an empty package dir to create>
"""
import json
import subprocess
import sys
from pathlib import Path

bundle, empty = Path(sys.argv[1]), Path(sys.argv[2])
empty.mkdir()
p = subprocess.Popen(["uv", "run", str(bundle / "server" / "tamheed_server.py"),
                      "--package-dir", str(empty)],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def send(obj):
    p.stdin.write((json.dumps(obj) + "\n").encode())
    p.stdin.flush()


def recv():
    while True:
        line = p.stdout.readline()
        if not line:
            raise SystemExit("server closed")
        line = line.strip()
        if line:
            return json.loads(line)


send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                 "clientInfo": {"name": "wire_list", "version": "0"}}})
recv()
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
tools = recv()["result"]["tools"]
print(json.dumps({t["name"]: t.get("description", "") for t in tools}, ensure_ascii=False))
p.stdin.close()
p.terminate()
