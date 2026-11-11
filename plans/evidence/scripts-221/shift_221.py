"""Plans 221-229 (the 6.5.0 round): the guide hand maps cite server line numbers and the guide
test pins lines by number. An engine patch moves lines, so each citation is re-aimed by a line
map from HEAD's server text to the working copy (difflib equal blocks). The 212/214/217 tool,
remap only: a plan that adds a tool write adds its own entry by hand after this run.

    python plans/evidence/scripts-221/shift_221.py
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

D.write_text(d, encoding="utf-8", newline="\n")

T = R / "tests/test_user_guide.py"
tt = T.read_text(encoding="utf-8")
tt = re.sub(r"(lines\.append\()(\d{4})(\))", remap, tt)
tt = re.sub(r"(src\[)(\d{4})(\])", lambda m: (f"{m.group(1)}{line_map[int(m.group(2)) + 1] - 1}{m.group(3)}"
                                              if int(m.group(2)) + 1 in line_map else m.group(0)), tt)
T.write_text(tt, encoding="utf-8", newline="\n")
print("unmapped citations:", sorted(set(unmapped)))
print("shift applied")
