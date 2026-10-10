"""Plan 217: the guide's hand maps cite server line numbers and the guide test pins four lines by
number. The engine patch inserted lines, so each citation is re-aimed by a line map from HEAD's
server text to the working copy (difflib equal blocks), then package_close's new write (the
`.unflushed` sidecar) is added at its line. The 212/214 tool with one add_write.

    python plans/evidence/scripts-217/shift_217.py [--remap-only]
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[3]
SRV = "plugins/tamheed/server/tamheed_server.py"
old = subprocess.run(["git", "show", f"HEAD:{SRV}"], cwd=R, capture_output=True, text=True,
                     encoding="utf-8").stdout.splitlines()
new = (R / SRV).read_text(encoding="utf-8").splitlines()
line_map: dict[int, int] = {}
sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            line_map[i1 + k + 1] = j1 + k + 1

D = R / "docs/guide/diagrams.py"
d = D.read_text(encoding="utf-8")
start = d.index("TOOL_EFFECTS = {")
end = d.index("_SEVERITY_KEY = {")
region = d[start:end]
unmapped = []


def remap(m):
    n = int(m.group(2))
    if n not in line_map:
        unmapped.append(n)
        return m.group(0)
    return f"{m.group(1)}{line_map[n]}{m.group(3)}"


region = re.sub(r'(\(\s*"[^"]+",\s*)(\d{3,4})(\s*\))', remap, region)
region = re.sub(r'("G-[A-Z-]+":\s*)(\d{4})(\b)', remap, region)
region = re.sub(r"(\bL)(\d{4})(\b)", remap, region)
d = d[:start] + region + d[end:]

# the new write: the sidecar line in package_close
sidecar = [ln for ln, text in enumerate(new, 1) if '.unflushed").write_bytes(body)' in text]
assert len(sidecar) == 1, sidecar


def add_write(tool: str, ln: int):
    global d
    pat = re.compile(rf'("{tool}": \{{.*?"writes": \[)(.*?)(\]\}})', re.S)
    m = pat.search(d)
    assert m, tool
    assert "unflushed" not in m.group(2), tool
    d = d[:m.start()] + m.group(1) + m.group(2) + f', ("data/*.unflushed", {ln})' + m.group(3) + d[m.end():]


if "--remap-only" not in sys.argv:
    add_write("package_close", sidecar[0])
    print("sidecar write added at", sidecar[0])
D.write_text(d, encoding="utf-8", newline="\n")

T = R / "tests/test_user_guide.py"
tt = T.read_text(encoding="utf-8")
tt = re.sub(r"(lines\.append\()(\d{4})(\))", remap, tt)
tt = re.sub(r"(src\[)(\d{4})(\])", lambda m: (f"{m.group(1)}{line_map[int(m.group(2)) + 1] - 1}{m.group(3)}"
                                              if int(m.group(2)) + 1 in line_map else m.group(0)), tt)
T.write_text(tt, encoding="utf-8", newline="\n")
print("unmapped citations:", sorted(set(unmapped)))
print("shift applied")
