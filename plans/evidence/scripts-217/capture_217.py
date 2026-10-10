"""Plan 217: element captures of every guide figure whose SVG changed in this beat (read from
`git status` under docs/guide/figures), EN/AR x light/dark, through the Python Playwright runtime.
The 214 capture script with the id list taken from the tree instead of typed.

    python plans/evidence/scripts-217/capture_217.py
"""
import re
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "plans" / "evidence" / "captures-217"
PORT = 8767

status = subprocess.run(["git", "status", "--porcelain", "docs/guide/figures"], cwd=REPO,
                        capture_output=True, text=True, encoding="utf-8").stdout
ids = sorted({re.sub(r"-(en|ar)(-dark)?\.svg$", "", Path(line[3:].strip()).name)
              for line in status.splitlines() if line.strip()})
print("changed figure ids:", ids)
OUT.mkdir(exist_ok=True)
server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                          cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="load")
        taken = []
        for lang in ("en", "ar"):
            page.click(f'[data-lang-btn="{lang}"]')
            for theme in ("light", "dark"):
                page.click(f'[data-theme-btn="{theme}"]')
                page.wait_for_timeout(300)
                for fid in ids:
                    fig = page.locator(f'figure.file:has(img[src*="/figures/{fid}-{lang}"])').first
                    fig.wait_for(state="attached")
                    fig.evaluate("el => { let d = el.closest('details'); while (d) { d.open = true;"
                                 " d = d.parentElement && d.parentElement.closest('details'); } }")
                    fig.scroll_into_view_if_needed()
                    img = fig.locator(f'img[src*="/figures/{fid}-{lang}"]').first
                    page.wait_for_function("el => el.complete", arg=img.element_handle())
                    page.wait_for_timeout(150)
                    src = img.evaluate("el => el.currentSrc || el.src") or ""
                    assert f"{fid}-{lang}" in src, (fid, lang, theme, src)
                    if theme == "dark":
                        assert "-dark.svg" in src, (fid, lang, theme, src)
                    path = OUT / f"{fid}-{lang}-{theme}.png"
                    fig.screenshot(path=str(path))
                    taken.append(path.name)
        browser.close()
    print(f"captured {len(taken)} files under {OUT}")
    for name in taken:
        print(" ", name)
finally:
    server.terminate()
