"""Plan 212: element captures of the figures this beat changed, EN/AR x light/dark, through the
Python Playwright runtime (the MCP browser servers did not connect this session). Serves the
repository over http.server, toggles language and theme with the page's own buttons, and
screenshots each `figure.file` whose image names the figure id (a capture includes its caption).

    python plans/evidence/scripts-ste/labrun-212/capture_212.py
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "plans" / "evidence" / "captures-212"
IDS = ["fx-package_create", "fx-package_open", "fx-package_adopt",
       "gate-G-IDS", "gate-G-DEC-STATUS", "gate-G-REQ-SRC", "gate-G-COMPLETE", "gate-G-REL"]
PORT = 8765

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
                for fid in IDS:
                    # each language has its own figure element; the visible one is this language's
                    # the theme toggle rewrites the img src to the -dark file, so match the id+lang prefix only
                    fig = page.locator(f'figure.file:has(img[src*="/figures/{fid}-{lang}"])').first
                    fig.wait_for(state="attached")
                    # a gate figure sits inside a closed <details> fold: open every ancestor fold
                    fig.evaluate("el => { let d = el.closest('details'); while (d) { d.open = true;"
                                 " d = d.parentElement && d.parentElement.closest('details'); } }")
                    fig.scroll_into_view_if_needed()
                    # one figure holds both languages' pictures; take this language's image
                    img = fig.locator(f'img[src*="/figures/{fid}-{lang}"]').first
                    page.wait_for_function("el => el.complete", arg=img.element_handle())
                    page.wait_for_timeout(150)
                    src = img.evaluate("el => el.currentSrc || el.src") or ""
                    assert f"{fid}-{lang}" in src, (fid, lang, theme, src)   # the swap landed
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
