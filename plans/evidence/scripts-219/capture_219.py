"""Plan 219: before/after pictures of the review page, on SCRATCH COPIES only (export_html writes
review.html and csv/ beside a package, so the committed fixtures are never the target). Copies the
lab-tracker fixture (13 handoffs: the Resume section has a handoff to show) and the demo sample to
the scratchpad, exports each in-process (`_WIRE_ROOT` off), serves the scratch folder, and
screenshots the progress-log fold and the Resume section at 1280px through the Python Playwright
runtime. `--acmp` adds a scratch copy of the operator's ACMP package, pictured into the scratchpad
only (never the repository: the field's words stay in the field).

    python plans/evidence/scripts-219/capture_219.py before
    python plans/evidence/scripts-219/capture_219.py after [--acmp]
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
WITH_ACMP = "--acmp" in sys.argv
SCRATCH = Path(os.environ["CLAUDE_SCRATCH"]) if os.environ.get("CLAUDE_SCRATCH") else Path(__file__).resolve().parents[0] / "scratch"
OUT = REPO / "plans" / "evidence" / "captures-219"
PRIVATE = SCRATCH / "captures-private"
PORT = 8768

SCRATCH.mkdir(parents=True, exist_ok=True)
OUT.mkdir(exist_ok=True)
PRIVATE.mkdir(exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8")


def export_copy(src: Path, root: Path, name: str) -> Path:
    dst = root / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    # a copied lock file names the live session that holds the ORIGINAL; on the copy it is a
    # stray byte string, not a holder, so it goes before the open (the server would refuse it)
    (dst / "data" / ".lock").unlink(missing_ok=True)
    srv.PACKAGE_ROOT = root
    out = srv.package_open(name)
    assert out.get("ok"), out
    ex = srv.export_html()
    assert ex.get("ok"), ex
    srv.package_close()
    return dst / "review.html"


pages = {
    "lab": export_copy(REPO / "evals" / "sample-results" / "lab-tracker" / "package", SCRATCH / "lab", "package"),
    "demo": export_copy(REPO / "generated-samples" / "support-triage-agent-v2", SCRATCH / "demo", "support-triage-agent-v2"),
}
if WITH_ACMP:
    pages["acmp"] = export_copy(Path(r"C:\Users\ahammo\Repos\acmp\tamheed-package"), SCRATCH / "acmp", "tamheed-package")
for k, p in pages.items():
    print(k, p, p.stat().st_size, "bytes")

server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                          cwd=SCRATCH, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
taken = []
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        for key, path in pages.items():
            rel = path.relative_to(SCRATCH).as_posix()
            url = f"http://127.0.0.1:{PORT}/{rel}"
            out_dir = PRIVATE if key == "acmp" else OUT
            page.goto(url, wait_until="load")
            # the progress-log fold: open it, picture the table wrapper
            fold = page.locator("details:has(summary:has-text('Progress log'))").first
            fold.wait_for(state="attached")
            fold.evaluate("el => el.open = true")
            # viewport pictures, not element pictures: a 1,700-row table is taller than a
            # screenshot can be, and the viewport is what the operator sees
            fold.evaluate("el => el.scrollIntoView({block: 'start'})")
            page.wait_for_timeout(300)
            p1 = out_dir / f"{MODE}-{key}-log.png"
            page.screenshot(path=str(p1))
            taken.append(p1)
            # the Resume section
            page.locator("section#resume").first.evaluate("el => el.scrollIntoView({block: 'start'})")
            page.wait_for_timeout(300)
            p2 = out_dir / f"{MODE}-{key}-resume.png"
            page.screenshot(path=str(p2))
            taken.append(p2)
            if MODE == "after" and key == "lab":
                # a fragment link to a row inside a scrolling fold must land below the sticky header
                page.locator("details#reg-requirements").first.evaluate("el => el.open = true")
                page.goto(url + "#FR-001", wait_until="load")
                page.locator("details#reg-requirements").first.evaluate("el => el.open = true")
                page.evaluate("location.hash = ''; location.hash = '#FR-001'")
                page.wait_for_timeout(400)
                p3 = out_dir / f"{MODE}-{key}-anchor.png"
                page.screenshot(path=str(p3))
                taken.append(p3)
        browser.close()
finally:
    server.terminate()
print(f"{MODE}: {len(taken)} pictures")
for p in taken:
    print(" ", p)
