"""Plan 172: run one TURN of a multi-turn headless conversation from a turns file (run-a2.md,
run-b.md style): `## T<n> — ...` headings; a heading that names a slash command IS the prompt;
a words section is the prompt with `{PREAMBLE}` from run-words.md. The session id is kept in
<ws>/../runs/<run>.sid after the first turn; later turns `--resume` it. Before a slash turn a
dead lock is cleared in-process (the operator's word, journaled by the engine); a words turn
carries the preamble instead and the agent clears it on that word.

    python labrun_turns.py <turns.md> <ws> <run label> <turn label> <package> [--turns N] [--budget X] [--allow ...]
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
PREAMBLE = re.search(r"## Standing preamble[^\n]*\n\n((?:> .*\n)+)",
                     (HERE / "run-words.md").read_text(encoding="utf-8")).group(1)
PREAMBLE = " ".join(l[2:].strip() for l in PREAMBLE.splitlines())


def section(turns_md: Path, label: str):
    text = turns_md.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(label)}\s*[—-]\s*(.*?)$\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert m, f"no section {label}"
    head, body = m.group(1).strip(), m.group(2).strip()
    slash = re.fullmatch(r"`(/tamheed:[\w-]+ [^`]*)`", head)
    return (slash.group(1), True) if slash else (body.replace("{PREAMBLE}", PREAMBLE), False)


def main():
    turns_md, ws, run, label, package = (Path(sys.argv[1]), Path(sys.argv[2]).resolve(), *sys.argv[3:6])
    extra = sys.argv[6:]
    prompt, is_slash = section(turns_md, label)
    sid_file = ws.parent / "runs" / f"{run}.sid"
    cmd = [sys.executable, str(HERE / "labrun.py"), "run", "--ws", str(ws), "--label", f"{run}-{label}",
           "--prompt", prompt, *extra]
    if sid_file.exists():
        cmd += ["--resume", sid_file.read_text().strip()]
    if is_slash:
        subprocess.run([sys.executable, str(HERE / "labrun.py"), "lock", "--ws", str(ws), "--package", package, "--unlock"])
    print(f"TURN {label} {'slash' if is_slash else 'words'}: {prompt[:100]!r}")
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    m = re.search(r"SESSION (\S+)", out.stdout)
    if m and not sid_file.exists():
        sid_file.write_text(m.group(1))
    print(out.stdout); print(out.stderr[-2000:], file=sys.stderr)


if __name__ == "__main__":
    main()
